"""
练习测试接口 - P0 核心功能
"""
import uuid
import json
import random
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session

from app.models.database import Exercise, ExerciseRecord, ExerciseSession, get_db
from app.core.security import get_current_user_id

router = APIRouter()


# ========== 请求/响应模型 ==========

class ExerciseCreateRequest(BaseModel):
    """创建练习题请求"""
    subject: str = Field(..., description="学科")
    type: str = Field(..., description="题型: choice / fill_blank / short_answer / programming")
    question: str = Field(..., description="题目内容")
    options: Optional[List[str]] = Field(None, description="选择题选项")
    correct_answer: str = Field(..., description="正确答案")
    explanation: Optional[str] = Field(None, description="答案解析")
    knowledge_point: Optional[str] = Field(None, description="知识点")
    difficulty: int = Field(default=3, ge=1, le=5, description="难度 1-5")


class ExerciseResponse(BaseModel):
    """练习题响应"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    subject: str
    type: str
    question: str
    options: Optional[str] = None
    correct_answer: str
    explanation: Optional[str] = None
    knowledge_point: Optional[str] = None
    difficulty: int
    source: str
    status: str
    created_at: datetime


class ExerciseSubmitRequest(BaseModel):
    """提交答案请求"""
    user_answer: str = Field(..., description="用户答案")
    time_spent: int = Field(default=0, ge=0, description="耗时（秒）")


class ExerciseSubmitResponse(BaseModel):
    """提交答案响应"""
    is_correct: bool
    correct_answer: str
    explanation: Optional[str] = None
    score: int


class ExerciseRecordResponse(BaseModel):
    """练习记录响应"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    exercise_id: str
    user_answer: Optional[str] = None
    is_correct: bool
    score: int
    time_spent: int
    created_at: datetime


class ExerciseSessionCreateRequest(BaseModel):
    """创建练习会话请求"""
    title: Optional[str] = Field(None, description="练习标题")
    subject: str = Field(..., description="学科")
    exercise_count: int = Field(default=5, ge=1, le=20, description="题目数量")
    difficulty: Optional[int] = Field(None, ge=1, le=5, description="难度筛选")


class ExerciseSessionResponse(BaseModel):
    """练习会话响应"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: Optional[str] = None
    subject: str
    exercise_ids: str
    total_count: int
    correct_count: int
    score: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None


class ExerciseHistoryItem(BaseModel):
    """练习历史单项"""
    exercise_id: str
    question: str
    subject: str
    type: str
    user_answer: Optional[str] = None
    correct_answer: str
    is_correct: bool
    score: int
    created_at: datetime


# ========== 接口实现 ==========

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_exercise(
    request: ExerciseCreateRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    手动创建练习题
    """
    exercise_id = str(uuid.uuid4())
    options_str = json.dumps(request.options, ensure_ascii=False) if request.options else None

    exercise = Exercise(
        id=exercise_id,
        user_id=user_id,
        subject=request.subject,
        type=request.type,
        question=request.question,
        options=options_str,
        correct_answer=request.correct_answer,
        explanation=request.explanation,
        knowledge_point=request.knowledge_point,
        difficulty=request.difficulty,
        source="manual",
        status="active"
    )

    db.add(exercise)
    db.commit()
    db.refresh(exercise)

    return exercise


@router.get("")
async def list_exercises(
    subject: Optional[str] = Query(None, description="按学科筛选"),
    type: Optional[str] = Query(None, description="按题型筛选"),
    difficulty: Optional[int] = Query(None, description="按难度筛选"),
    knowledge_point: Optional[str] = Query(None, description="按知识点筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    查询练习题列表
    """
    query = db.query(Exercise).filter(Exercise.user_id == user_id, Exercise.status == "active")

    if subject:
        query = query.filter(Exercise.subject == subject)
    if type:
        query = query.filter(Exercise.type == type)
    if difficulty:
        query = query.filter(Exercise.difficulty == difficulty)
    if knowledge_point:
        query = query.filter(Exercise.knowledge_point.contains(knowledge_point))

    total = query.count()
    items = query.order_by(Exercise.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {"total": total, "items": items}


@router.get("/history/list")
async def get_exercise_history(
    subject: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取练习历史
    """
    query = db.query(ExerciseRecord, Exercise).join(
        Exercise, ExerciseRecord.exercise_id == Exercise.id
    ).filter(ExerciseRecord.user_id == user_id)

    if subject:
        query = query.filter(Exercise.subject == subject)

    total = query.count()
    results = query.order_by(ExerciseRecord.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for record, exercise in results:
        items.append({
            "record_id": record.id,
            "exercise_id": exercise.id,
            "question": exercise.question,
            "subject": exercise.subject,
            "type": exercise.type,
            "user_answer": record.user_answer,
            "correct_answer": exercise.correct_answer,
            "is_correct": record.is_correct,
            "score": record.score,
            "time_spent": record.time_spent,
            "created_at": record.created_at.isoformat()
        })

    return {"total": total, "items": items}


# ========== 练习会话（一组题的测试）==========

@router.post("/sessions/generate", status_code=status.HTTP_201_CREATED)
async def generate_exercise_session(
    request: ExerciseSessionCreateRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    生成练习会话（从题库中随机抽取题目）
    """
    query = db.query(Exercise).filter(
        Exercise.user_id == user_id,
        Exercise.status == "active",
        Exercise.subject == request.subject
    )

    if request.difficulty:
        query = query.filter(Exercise.difficulty == request.difficulty)

    exercises = query.all()

    if len(exercises) < request.exercise_count:
        raise HTTPException(
            status_code=400,
            detail=f"题库中该条件的题目不足，仅有 {len(exercises)} 道"
        )

    # 随机抽取
    selected = random.sample(exercises, request.exercise_count)
    exercise_ids = ",".join([e.id for e in selected])

    session_id = str(uuid.uuid4())
    session = ExerciseSession(
        id=session_id,
        user_id=user_id,
        title=request.title or f"{request.subject} 练习",
        subject=request.subject,
        exercise_ids=exercise_ids,
        total_count=request.exercise_count,
        correct_count=0,
        score=0,
        status="in_progress"
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "session": session,
        "exercises": [
            {
                "id": e.id,
                "type": e.type,
                "question": e.question,
                "options": json.loads(e.options) if e.options else None,
                "difficulty": e.difficulty,
                "knowledge_point": e.knowledge_point
            }
            for e in selected
        ]
    }


@router.get("/sessions/history/list")
async def get_session_history(
    subject: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取练习会话历史
    """
    query = db.query(ExerciseSession).filter(ExerciseSession.user_id == user_id)

    if subject:
        query = query.filter(ExerciseSession.subject == subject)

    total = query.count()
    items = query.order_by(ExerciseSession.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {"total": total, "items": items}


@router.get("/sessions/{session_id}")
async def get_exercise_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取练习会话详情
    """
    session = db.query(ExerciseSession).filter(
        ExerciseSession.id == session_id,
        ExerciseSession.user_id == user_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="练习会话不存在")

    # 获取题目详情
    exercise_ids = session.exercise_ids.split(",") if session.exercise_ids else []
    exercises = db.query(Exercise).filter(Exercise.id.in_(exercise_ids)).all()

    return {
        "session": session,
        "exercises": [
            {
                "id": e.id,
                "type": e.type,
                "question": e.question,
                "options": json.loads(e.options) if e.options else None,
                "difficulty": e.difficulty,
                "knowledge_point": e.knowledge_point
            }
            for e in exercises
        ]
    }


@router.post("/sessions/{session_id}/complete")
async def complete_exercise_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    完成练习会话，计算总分
    """
    session = db.query(ExerciseSession).filter(
        ExerciseSession.id == session_id,
        ExerciseSession.user_id == user_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="练习会话不存在")

    exercise_ids = session.exercise_ids.split(",") if session.exercise_ids else []

    # 查询该会话所有题目的答题记录
    records = db.query(ExerciseRecord).filter(
        ExerciseRecord.user_id == user_id,
        ExerciseRecord.exercise_id.in_(exercise_ids)
    ).all()

    correct_count = sum(1 for r in records if r.is_correct)
    total = len(exercise_ids)
    score = int((correct_count / total) * 100) if total > 0 else 0

    session.correct_count = correct_count
    session.score = score
    session.status = "completed"
    session.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(session)

    return {
        "session": session,
        "summary": {
            "total": total,
            "correct": correct_count,
            "wrong": total - correct_count,
            "score": score
        }
    }


@router.get("/{exercise_id}")
async def get_exercise(
    exercise_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取练习题详情（不返回正确答案，用于答题）
    """
    exercise = db.query(Exercise).filter(
        Exercise.id == exercise_id,
        Exercise.user_id == user_id
    ).first()

    if not exercise:
        raise HTTPException(status_code=404, detail="练习题不存在")

    # 返回时隐藏正确答案
    result = {
        "id": exercise.id,
        "user_id": exercise.user_id,
        "subject": exercise.subject,
        "type": exercise.type,
        "question": exercise.question,
        "options": json.loads(exercise.options) if exercise.options else None,
        "knowledge_point": exercise.knowledge_point,
        "difficulty": exercise.difficulty,
        "created_at": exercise.created_at.isoformat()
    }
    return result


@router.get("/{exercise_id}/full")
async def get_exercise_full(
    exercise_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取练习题完整信息（包含答案和解析，用于查看）
    """
    exercise = db.query(Exercise).filter(
        Exercise.id == exercise_id,
        Exercise.user_id == user_id
    ).first()

    if not exercise:
        raise HTTPException(status_code=404, detail="练习题不存在")

    return exercise


@router.post("/{exercise_id}/submit")
async def submit_answer(
    exercise_id: str,
    request: ExerciseSubmitRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    提交答案
    """
    exercise = db.query(Exercise).filter(
        Exercise.id == exercise_id,
        Exercise.user_id == user_id
    ).first()

    if not exercise:
        raise HTTPException(status_code=404, detail="练习题不存在")

    # 判断答案是否正确（简单字符串匹配，可扩展为更智能的匹配）
    is_correct = request.user_answer.strip().lower() == exercise.correct_answer.strip().lower()
    score = 100 if is_correct else 0

    # 记录答题
    record_id = str(uuid.uuid4())
    record = ExerciseRecord(
        id=record_id,
        user_id=user_id,
        exercise_id=exercise_id,
        user_answer=request.user_answer,
        is_correct=is_correct,
        score=score,
        time_spent=request.time_spent
    )
    db.add(record)
    db.commit()

    return {
        "is_correct": is_correct,
        "correct_answer": exercise.correct_answer,
        "explanation": exercise.explanation,
        "score": score
    }
