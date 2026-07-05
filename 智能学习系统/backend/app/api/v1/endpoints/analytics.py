"""
成绩分析与评估报告接口
"""
import uuid
import json
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.database import (
    ExerciseRecord, Exercise, ExerciseSession,
    Mistake, AssessmentReport, get_db
)
from app.core.security import get_current_user_id
from app.core.llm_client import llm_client

router = APIRouter()


# ========== 请求/响应模型 ==========

class OverviewResponse(BaseModel):
    """学习概览响应"""
    total_exercises: int
    correct_count: int
    accuracy_rate: float
    total_mistakes: int
    unsolved_mistakes: int
    streak_days: int


class SubjectTrendItem(BaseModel):
    """学科趋势单项"""
    subject: str
    total_exercises: int
    correct_count: int
    accuracy_rate: float


class SubjectTrendResponse(BaseModel):
    """学科成绩趋势响应"""
    items: List[SubjectTrendItem]


class WeakPointItem(BaseModel):
    """薄弱知识点单项"""
    knowledge_point: str
    total_attempts: int
    wrong_count: int
    error_rate: float


class WeakPointsResponse(BaseModel):
    """薄弱知识点分析响应"""
    items: List[WeakPointItem]


class ReportGenerateResponse(BaseModel):
    """生成评估报告响应"""
    id: str
    content: str
    created_at: datetime


class ReportLatestResponse(BaseModel):
    """最新评估报告响应"""
    id: str
    content: str
    created_at: datetime


# ========== 接口实现 ==========

@router.get("/overview", response_model=OverviewResponse)
async def get_learning_overview(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    学习概览（统计总练习数、正确率、错题数、连续学习天数等）
    """
    # 总练习数（答题记录数）
    total_exercises = db.query(ExerciseRecord).filter(
        ExerciseRecord.user_id == user_id
    ).count()

    # 正确数
    correct_count = db.query(ExerciseRecord).filter(
        ExerciseRecord.user_id == user_id,
        ExerciseRecord.is_correct == True
    ).count()

    # 正确率
    accuracy_rate = (correct_count / total_exercises * 100) if total_exercises > 0 else 0.0

    # 错题总数
    total_mistakes = db.query(Mistake).filter(
        Mistake.user_id == user_id
    ).count()

    # 未解决错题数
    unsolved_mistakes = db.query(Mistake).filter(
        Mistake.user_id == user_id,
        Mistake.status == "unsolved"
    ).count()

    # 连续学习天数（基于 ExerciseRecord 的 created_at）
    streak_days = _calculate_streak_days(db, user_id)

    return {
        "total_exercises": total_exercises,
        "correct_count": correct_count,
        "accuracy_rate": round(accuracy_rate, 2),
        "total_mistakes": total_mistakes,
        "unsolved_mistakes": unsolved_mistakes,
        "streak_days": streak_days
    }


@router.get("/subjects", response_model=SubjectTrendResponse)
async def get_subject_trends(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    各科成绩趋势（按学科分组统计正确率、练习数）
    """
    results = db.query(
        Exercise.subject,
        func.count(ExerciseRecord.id).label("total"),
        func.sum(func.case([(ExerciseRecord.is_correct == True, 1)], else_=0)).label("correct")
    ).join(
        ExerciseRecord, Exercise.id == ExerciseRecord.exercise_id
    ).filter(
        ExerciseRecord.user_id == user_id
    ).group_by(Exercise.subject).all()

    items = []
    for subject, total, correct in results:
        total = total or 0
        correct = correct or 0
        accuracy_rate = (correct / total * 100) if total > 0 else 0.0
        items.append({
            "subject": subject,
            "total_exercises": total,
            "correct_count": correct,
            "accuracy_rate": round(accuracy_rate, 2)
        })

    return {"items": items}


@router.get("/weak-points", response_model=WeakPointsResponse)
async def get_weak_points(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    薄弱知识点分析（基于错题和练习记录，找出错误率最高的知识点）
    """
    # 从 ExerciseRecord 统计各知识点的答题情况
    exercise_stats = db.query(
        Exercise.knowledge_point,
        func.count(ExerciseRecord.id).label("total"),
        func.sum(func.case([(ExerciseRecord.is_correct == False, 1)], else_=0)).label("wrong")
    ).join(
        Exercise, Exercise.id == ExerciseRecord.exercise_id
    ).filter(
        ExerciseRecord.user_id == user_id,
        Exercise.knowledge_point.isnot(None),
        Exercise.knowledge_point != ""
    ).group_by(Exercise.knowledge_point).all()

    # 从 Mistake 统计各知识点的错题情况
    mistake_stats = db.query(
        Mistake.knowledge_point,
        func.count(Mistake.id).label("wrong")
    ).filter(
        Mistake.user_id == user_id,
        Mistake.knowledge_point.isnot(None),
        Mistake.knowledge_point != ""
    ).group_by(Mistake.knowledge_point).all()

    # 合并统计
    stats_map = {}
    for kp, total, wrong in exercise_stats:
        if not kp:
            continue
        stats_map[kp] = {
            "total_attempts": total or 0,
            "wrong_count": wrong or 0
        }

    for kp, wrong in mistake_stats:
        if not kp:
            continue
        if kp in stats_map:
            stats_map[kp]["wrong_count"] += wrong or 0
        else:
            stats_map[kp] = {
                "total_attempts": wrong or 0,
                "wrong_count": wrong or 0
            }

    items = []
    for kp, data in stats_map.items():
        total = data["total_attempts"]
        wrong = data["wrong_count"]
        error_rate = (wrong / total * 100) if total > 0 else 0.0
        items.append({
            "knowledge_point": kp,
            "total_attempts": total,
            "wrong_count": wrong,
            "error_rate": round(error_rate, 2)
        })

    # 按错误率降序排列
    items.sort(key=lambda x: x["error_rate"], reverse=True)

    return {"items": items}


@router.post("/report/generate", response_model=ReportGenerateResponse)
async def generate_assessment_report(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    生成评估报告（调用 llm_client.chat，让大模型基于用户数据生成文字报告）
    """
    # 收集用户数据
    overview = await get_learning_overview(user_id, db)
    subjects = await get_subject_trends(user_id, db)
    weak_points = await get_weak_points(user_id, db)

    # 构建 prompt
    system_prompt = (
        "你是一位专业的学习评估分析师。请根据提供的学生学习数据，"
        "生成一份简洁、专业、有建设性的学习评估报告。"
        "报告应包含：整体表现评价、各科分析、薄弱知识点建议、后续学习建议。"
        "请用中文输出，控制在 800 字以内。"
    )

    user_prompt = f"""
学生学习数据如下：

【学习概览】
- 总练习数：{overview['total_exercises']}
- 正确数：{overview['correct_count']}
- 正确率：{overview['accuracy_rate']}%
- 错题总数：{overview['total_mistakes']}
- 未解决错题：{overview['unsolved_mistakes']}
- 连续学习天数：{overview['streak_days']}

【各科成绩趋势】
{json.dumps([item.model_dump() for item in subjects['items']], ensure_ascii=False, indent=2)}

【薄弱知识点】（按错误率降序）
{json.dumps([item.model_dump() for item in weak_points['items'][:10]], ensure_ascii=False, indent=2)}

请生成评估报告。
"""

    messages = llm_client.build_messages(
        system_prompt=system_prompt,
        user_prompt=user_prompt
    )

    try:
        response = await llm_client.chat(messages, temperature=0.7)
        content = response["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"大模型生成报告失败: {str(e)}"
        )

    # 保存报告
    report_id = str(uuid.uuid4())
    report = AssessmentReport(
        id=report_id,
        user_id=user_id,
        content=content
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return {
        "id": report.id,
        "content": report.content,
        "created_at": report.created_at
    }


@router.get("/report/latest", response_model=ReportLatestResponse)
async def get_latest_report(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取最新评估报告
    """
    report = db.query(AssessmentReport).filter(
        AssessmentReport.user_id == user_id
    ).order_by(AssessmentReport.created_at.desc()).first()

    if not report:
        raise HTTPException(status_code=404, detail="暂无评估报告")

    return {
        "id": report.id,
        "content": report.content,
        "created_at": report.created_at
    }


# ========== 辅助函数 ==========

def _calculate_streak_days(db: Session, user_id: str) -> int:
    """
    计算连续学习天数（基于 ExerciseRecord 的 created_at）
    """
    records = db.query(ExerciseRecord).filter(
        ExerciseRecord.user_id == user_id
    ).order_by(ExerciseRecord.created_at.desc()).all()

    if not records:
        return 0

    # 提取有记录的日期集合
    record_dates = set()
    for r in records:
        record_dates.add(r.created_at.date())

    # 从今天往前数连续天数
    today = datetime.utcnow().date()
    streak = 0

    # 如果今天没有记录，从昨天开始算
    check_date = today
    if check_date not in record_dates:
        check_date = today - timedelta(days=1)

    while check_date in record_dates:
        streak += 1
        check_date -= timedelta(days=1)

    return streak
