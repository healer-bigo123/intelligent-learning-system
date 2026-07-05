"""
错题题库接口 - P0 核心功能
"""
import uuid
import json
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.database import Mistake, get_db
from app.core.security import get_current_user_id

router = APIRouter()


# ========== 请求/响应模型 ==========

class MistakeCreateRequest(BaseModel):
    """添加错题请求"""
    subject: str = Field(..., description="学科")
    question: str = Field(..., description="题目内容")
    correct_answer: str = Field(..., description="正确答案")
    user_answer: Optional[str] = Field(None, description="用户当时的答案")
    analysis: Optional[str] = Field(None, description="解析/反思")
    knowledge_point: Optional[str] = Field(None, description="知识点")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    source: Optional[str] = Field(None, description="来源")
    difficulty: int = Field(default=3, ge=1, le=5, description="难度 1-5")


class MistakeUpdateRequest(BaseModel):
    """更新错题请求"""
    subject: Optional[str] = None
    question: Optional[str] = None
    correct_answer: Optional[str] = None
    user_answer: Optional[str] = None
    analysis: Optional[str] = None
    knowledge_point: Optional[str] = None
    tags: Optional[List[str]] = None
    source: Optional[str] = None
    difficulty: Optional[int] = Field(None, ge=1, le=5)
    status: Optional[str] = Field(None, description="unsolved / reviewing / mastered")


class MistakeResponse(BaseModel):
    """错题响应"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    subject: str
    question: str
    correct_answer: str
    user_answer: Optional[str] = None
    analysis: Optional[str] = None
    knowledge_point: Optional[str] = None
    tags: str
    source: Optional[str] = None
    difficulty: int
    status: str
    review_count: int
    last_review_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class MistakeListResponse(BaseModel):
    """错题列表响应"""
    total: int
    items: List[MistakeResponse]


class MistakeStatsResponse(BaseModel):
    """错题统计响应"""
    total: int
    unsolved: int
    reviewing: int
    mastered: int
    by_subject: dict


# ========== 接口实现 ==========

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_mistake(
    request: MistakeCreateRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    添加错题
    """
    mistake_id = str(uuid.uuid4())
    tags_str = ",".join(request.tags) if request.tags else ""

    new_mistake = Mistake(
        id=mistake_id,
        user_id=user_id,
        subject=request.subject,
        question=request.question,
        correct_answer=request.correct_answer,
        user_answer=request.user_answer,
        analysis=request.analysis,
        knowledge_point=request.knowledge_point,
        tags=tags_str,
        source=request.source,
        difficulty=request.difficulty,
        status="unsolved",
        review_count=0
    )

    db.add(new_mistake)
    db.commit()
    db.refresh(new_mistake)

    return new_mistake


@router.get("", response_model=MistakeListResponse)
async def list_mistakes(
    subject: Optional[str] = Query(None, description="按学科筛选"),
    status: Optional[str] = Query(None, description="按状态筛选"),
    knowledge_point: Optional[str] = Query(None, description="按知识点筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    查询错题列表（支持筛选和分页）
    """
    query = db.query(Mistake).filter(Mistake.user_id == user_id)

    if subject:
        query = query.filter(Mistake.subject == subject)
    if status:
        query = query.filter(Mistake.status == status)
    if knowledge_point:
        query = query.filter(Mistake.knowledge_point.contains(knowledge_point))
    if keyword:
        query = query.filter(
            Mistake.question.contains(keyword) |
            Mistake.analysis.contains(keyword) |
            Mistake.tags.contains(keyword)
        )

    total = query.count()
    items = query.order_by(Mistake.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {"total": total, "items": items}


@router.get("/{mistake_id}", response_model=MistakeResponse)
async def get_mistake(
    mistake_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取错题详情
    """
    mistake = db.query(Mistake).filter(
        Mistake.id == mistake_id,
        Mistake.user_id == user_id
    ).first()

    if not mistake:
        raise HTTPException(status_code=404, detail="错题不存在")

    return mistake


@router.put("/{mistake_id}")
async def update_mistake(
    mistake_id: str,
    request: MistakeUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    更新错题（添加笔记、修改标签、更新状态等）
    """
    mistake = db.query(Mistake).filter(
        Mistake.id == mistake_id,
        Mistake.user_id == user_id
    ).first()

    if not mistake:
        raise HTTPException(status_code=404, detail="错题不存在")

    update_data = request.model_dump(exclude_unset=True)

    if "tags" in update_data and update_data["tags"] is not None:
        update_data["tags"] = ",".join(update_data["tags"])

    for field, value in update_data.items():
        setattr(mistake, field, value)

    db.commit()
    db.refresh(mistake)

    return mistake


@router.delete("/{mistake_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mistake(
    mistake_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    删除错题
    """
    mistake = db.query(Mistake).filter(
        Mistake.id == mistake_id,
        Mistake.user_id == user_id
    ).first()

    if not mistake:
        raise HTTPException(status_code=404, detail="错题不存在")

    db.delete(mistake)
    db.commit()

    return None


@router.post("/{mistake_id}/review")
async def review_mistake(
    mistake_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    复习错题（增加复习次数，更新最后复习时间）
    """
    mistake = db.query(Mistake).filter(
        Mistake.id == mistake_id,
        Mistake.user_id == user_id
    ).first()

    if not mistake:
        raise HTTPException(status_code=404, detail="错题不存在")

    mistake.review_count += 1
    mistake.last_review_at = datetime.utcnow()

    # 如果复习次数达到 3 次，自动标记为 mastered
    if mistake.review_count >= 3 and mistake.status != "mastered":
        mistake.status = "mastered"

    db.commit()
    db.refresh(mistake)

    return {
        "message": "复习记录已更新",
        "review_count": mistake.review_count,
        "status": mistake.status
    }


@router.get("/stats/overview", response_model=MistakeStatsResponse)
async def get_mistake_stats(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    错题统计分析
    """
    total = db.query(Mistake).filter(Mistake.user_id == user_id).count()
    unsolved = db.query(Mistake).filter(Mistake.user_id == user_id, Mistake.status == "unsolved").count()
    reviewing = db.query(Mistake).filter(Mistake.user_id == user_id, Mistake.status == "reviewing").count()
    mastered = db.query(Mistake).filter(Mistake.user_id == user_id, Mistake.status == "mastered").count()

    # 按学科统计
    subject_stats = db.query(
        Mistake.subject,
        func.count(Mistake.id).label("count")
    ).filter(Mistake.user_id == user_id).group_by(Mistake.subject).all()

    by_subject = {s.subject: s.count for s in subject_stats}

    return {
        "total": total,
        "unsolved": unsolved,
        "reviewing": reviewing,
        "mastered": mastered,
        "by_subject": by_subject
    }
