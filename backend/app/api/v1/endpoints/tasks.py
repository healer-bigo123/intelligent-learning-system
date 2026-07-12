"""
任务管理接口
"""
import uuid
from datetime import datetime, date, timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.database import Task, get_db
from app.core.security import get_current_user_id

router = APIRouter()


# ========== 请求/响应模型 ==========

class TaskCreateRequest(BaseModel):
    """创建任务请求"""
    title: str = Field(..., min_length=1, max_length=200, description="任务标题")
    description: Optional[str] = Field(None, description="任务描述")
    subject: Optional[str] = Field("其他", description="学科")
    priority: Optional[str] = Field("medium", description="优先级: low / medium / high")
    due_date: Optional[datetime] = Field(None, description="截止时间")


class TaskUpdateRequest(BaseModel):
    """更新任务请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="任务标题")
    description: Optional[str] = Field(None, description="任务描述")
    subject: Optional[str] = Field(None, description="学科")
    priority: Optional[str] = Field(None, description="优先级: low / medium / high")
    status: Optional[str] = Field(None, description="状态: pending / completed")
    due_date: Optional[datetime] = Field(None, description="截止时间")


class TaskResponse(BaseModel):
    """任务响应"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    subject: str
    priority: str
    status: str
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class TaskListResponse(BaseModel):
    """任务列表响应"""
    total: int
    items: List[TaskResponse]


class TaskStatsResponse(BaseModel):
    """任务统计响应"""
    total: int
    completed: int
    pending: int
    completion_rate: int


# ========== 接口实现 ==========

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    request: TaskCreateRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    创建新任务
    """
    task_id = f"task-{uuid.uuid4().hex[:8]}"

    task = Task(
        id=task_id,
        user_id=user_id,
        title=request.title,
        description=request.description,
        subject=request.subject,
        priority=request.priority,
        due_date=request.due_date,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    status: Optional[str] = Query(None, description="按状态筛选: pending / completed"),
    subject: Optional[str] = Query(None, description="按学科筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取任务列表（支持按状态和学科筛选）
    """
    query = db.query(Task).filter(Task.user_id == user_id)

    if status:
        query = query.filter(Task.status == status)
    if subject:
        query = query.filter(Task.subject == subject)

    total = query.count()
    items = query.order_by(Task.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {"total": total, "items": items}


@router.get("/today", response_model=TaskListResponse)
async def list_today_tasks(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取今日任务列表
    """
    today = date.today()
    tomorrow = today + timedelta(days=1)

    items = db.query(Task).filter(
        Task.user_id == user_id,
        func.date(Task.created_at) >= today,
        func.date(Task.created_at) < tomorrow
    ).order_by(Task.created_at.desc()).all()

    return {"total": len(items), "items": items}


@router.get("/stats", response_model=TaskStatsResponse)
async def get_task_stats(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取任务统计
    """
    total = db.query(Task).filter(Task.user_id == user_id).count()
    completed = db.query(Task).filter(Task.user_id == user_id, Task.status == "completed").count()
    pending = total - completed
    completion_rate = int((completed / total) * 100) if total > 0 else 0

    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "completion_rate": completion_rate
    }


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取单个任务详情
    """
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")

    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    request: TaskUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    更新任务
    """
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")

    update_data = request.model_dump(exclude_unset=True)

    # 如果状态变为 completed，设置 completed_at
    if "status" in update_data:
        if update_data["status"] == "completed" and task.status != "completed":
            update_data["completed_at"] = datetime.utcnow()
        elif update_data["status"] == "pending":
            update_data["completed_at"] = None

    for field, value in update_data.items():
        setattr(task, field, value)

    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    删除任务
    """
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")

    db.delete(task)
    db.commit()

    return None
