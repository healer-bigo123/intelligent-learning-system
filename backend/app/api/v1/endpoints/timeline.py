"""
学习记录时间线接口
"""
import uuid
from datetime import datetime, date, timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct

from app.models.database import StudyActivity, Achievement, UserAchievement, get_db
from app.core.security import get_current_user_id

router = APIRouter()


# ========== 请求/响应模型 ==========

class TimelineRecordRequest(BaseModel):
    """记录学习活动请求"""
    activity_type: str = Field(..., description="活动类型: exercise / mistake_review / material_read / session_complete")
    target_id: Optional[str] = Field(None, description="关联目标 ID")
    title: Optional[str] = Field(None, description="活动标题")
    duration: int = Field(default=0, ge=0, description="学习时长（秒）")
    score: Optional[int] = Field(None, ge=0, le=100, description="得分（百分比）")


class TimelineActivityResponse(BaseModel):
    """学习活动响应"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    activity_type: str
    target_id: Optional[str] = None
    title: Optional[str] = None
    duration: int
    score: Optional[int] = None
    created_at: datetime


class TimelineListResponse(BaseModel):
    """学习记录列表响应"""
    total: int
    items: List[TimelineActivityResponse]


class DailyStatsItem(BaseModel):
    """每日统计单项"""
    date: str
    total_duration: int
    activity_count: int


class DailyStatsResponse(BaseModel):
    """每日学习统计响应"""
    items: List[DailyStatsItem]


class OverviewStatsResponse(BaseModel):
    """学习总览统计响应"""
    total_duration: int
    total_activities: int
    streak_days: int


class StreakResponse(BaseModel):
    """连续学习天数响应"""
    streak_days: int
    last_study_date: Optional[str] = None


class AchievementUnlockResponse(BaseModel):
    """成就解锁响应"""
    achievement_id: str
    name: str
    description: str
    icon: Optional[str] = None


class TimelineRecordResponse(BaseModel):
    """记录学习活动响应"""
    activity: TimelineActivityResponse
    unlocked_achievements: List[AchievementUnlockResponse]


# ========== 成就检查辅助函数 ==========

def _check_achievements(db: Session, user_id: str, activity: StudyActivity) -> List[AchievementUnlockResponse]:
    """
    检查并解锁成就
    """
    unlocked = []

    # 获取用户已解锁的成就 ID 列表
    unlocked_ids = {
        ua.achievement_id for ua in
        db.query(UserAchievement).filter(UserAchievement.user_id == user_id).all()
    }

    # 获取所有成就定义
    achievements = db.query(Achievement).all()

    for ach in achievements:
        if ach.id in unlocked_ids:
            continue

        condition_met = False

        if ach.condition_type == "exercise_count":
            count = db.query(StudyActivity).filter(
                StudyActivity.user_id == user_id,
                StudyActivity.activity_type == "exercise"
            ).count()
            condition_met = count >= ach.condition_value

        elif ach.condition_type == "streak_days":
            streak = _calculate_streak_days(db, user_id)
            condition_met = streak >= ach.condition_value

        elif ach.condition_type == "material_count":
            count = db.query(StudyActivity).filter(
                StudyActivity.user_id == user_id,
                StudyActivity.activity_type == "material_read"
            ).count()
            condition_met = count >= ach.condition_value

        elif ach.condition_type == "accuracy":
            # 计算练习正确率（基于有分数的活动）
            total = db.query(StudyActivity).filter(
                StudyActivity.user_id == user_id,
                StudyActivity.activity_type == "exercise",
                StudyActivity.score.isnot(None)
            ).count()
            if total > 0:
                correct = db.query(StudyActivity).filter(
                    StudyActivity.user_id == user_id,
                    StudyActivity.activity_type == "exercise",
                    StudyActivity.score == 100
                ).count()
                accuracy = int((correct / total) * 100)
                condition_met = accuracy >= ach.condition_value

        if condition_met:
            user_ach = UserAchievement(
                user_id=user_id,
                achievement_id=ach.id
            )
            db.add(user_ach)
            unlocked.append(AchievementUnlockResponse(
                achievement_id=ach.id,
                name=ach.name,
                description=ach.description,
                icon=ach.icon
            ))

    if unlocked:
        db.commit()

    return unlocked


def _calculate_streak_days(db: Session, user_id: str) -> int:
    """
    计算连续学习天数
    """
    # 获取用户所有有学习活动的日期（去重，按日期倒序）
    dates_result = db.query(
        func.date(StudyActivity.created_at).label("study_date")
    ).filter(
        StudyActivity.user_id == user_id
    ).group_by(
        func.date(StudyActivity.created_at)
    ).order_by(
        func.date(StudyActivity.created_at).desc()
    ).all()

    if not dates_result:
        return 0

    study_dates = [row.study_date for row in dates_result]

    streak = 1
    today = date.today()

    # 如果今天没有学习，从昨天开始算
    if study_dates[0] == today:
        check_date = today
    else:
        check_date = today - timedelta(days=1)

    if study_dates[0] != check_date and study_dates[0] != today:
        return 0

    for i in range(1, len(study_dates)):
        expected = check_date - timedelta(days=i)
        if study_dates[i] == expected:
            streak += 1
        else:
            break

    return streak


# ========== 接口实现 ==========

@router.post("/record", response_model=TimelineRecordResponse, status_code=status.HTTP_201_CREATED)
async def record_activity(
    request: TimelineRecordRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    记录学习活动，并检查成就解锁
    """
    activity_id = str(uuid.uuid4())

    activity = StudyActivity(
        id=activity_id,
        user_id=user_id,
        activity_type=request.activity_type,
        target_id=request.target_id,
        title=request.title,
        duration=request.duration,
        score=request.score
    )

    db.add(activity)
    db.commit()
    db.refresh(activity)

    # 检查成就解锁
    unlocked = _check_achievements(db, user_id, activity)

    return {
        "activity": activity,
        "unlocked_achievements": unlocked
    }


@router.get("", response_model=TimelineListResponse)
async def list_timeline(
    activity_type: Optional[str] = Query(None, description="按活动类型筛选"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取学习记录时间线（支持按日期范围筛选和分页）
    """
    query = db.query(StudyActivity).filter(StudyActivity.user_id == user_id)

    if activity_type:
        query = query.filter(StudyActivity.activity_type == activity_type)
    if start_date:
        query = query.filter(func.date(StudyActivity.created_at) >= start_date)
    if end_date:
        query = query.filter(func.date(StudyActivity.created_at) <= end_date)

    total = query.count()
    items = query.order_by(StudyActivity.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {"total": total, "items": items}


@router.get("/stats/daily", response_model=DailyStatsResponse)
async def get_daily_stats(
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取每日学习统计（学习时长、活动次数）
    """
    query = db.query(
        func.date(StudyActivity.created_at).label("study_date"),
        func.sum(StudyActivity.duration).label("total_duration"),
        func.count(StudyActivity.id).label("activity_count")
    ).filter(StudyActivity.user_id == user_id)

    if start_date:
        query = query.filter(func.date(StudyActivity.created_at) >= start_date)
    if end_date:
        query = query.filter(func.date(StudyActivity.created_at) <= end_date)

    results = query.group_by(
        func.date(StudyActivity.created_at)
    ).order_by(
        func.date(StudyActivity.created_at).desc()
    ).all()

    items = [
        DailyStatsItem(
            date=str(row.study_date),
            total_duration=row.total_duration or 0,
            activity_count=row.activity_count or 0
        )
        for row in results
    ]

    return {"items": items}


@router.get("/stats/overview", response_model=OverviewStatsResponse)
async def get_overview_stats(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取学习总览（总学习时长、总活动数、连续学习天数）
    """
    total_duration_result = db.query(
        func.sum(StudyActivity.duration)
    ).filter(StudyActivity.user_id == user_id).scalar()

    total_activities = db.query(StudyActivity).filter(StudyActivity.user_id == user_id).count()
    streak_days = _calculate_streak_days(db, user_id)

    return {
        "total_duration": total_duration_result or 0,
        "total_activities": total_activities,
        "streak_days": streak_days
    }


@router.get("/streak", response_model=StreakResponse)
async def get_streak(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取连续学习天数
    """
    streak_days = _calculate_streak_days(db, user_id)

    last_activity = db.query(StudyActivity).filter(
        StudyActivity.user_id == user_id
    ).order_by(StudyActivity.created_at.desc()).first()

    last_study_date = None
    if last_activity:
        last_study_date = last_activity.created_at.date().isoformat()

    return {
        "streak_days": streak_days,
        "last_study_date": last_study_date
    }
