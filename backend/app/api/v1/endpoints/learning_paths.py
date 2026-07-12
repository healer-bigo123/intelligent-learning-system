"""
学习路径/计划接口
"""
import uuid
import json
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session

from app.models.database import LearningPath, get_db
from app.core.security import get_current_user_id

router = APIRouter()


# ========== 请求/响应模型 ==========

class LearningPathStep(BaseModel):
    """学习路径步骤"""
    title: str = Field(..., description="步骤标题")
    description: Optional[str] = Field(None, description="步骤描述")
    duration: Optional[int] = Field(None, ge=0, description="预计时长（分钟）")
    status: str = Field(default="pending", description="pending / in_progress / completed")


class LearningPathCreateRequest(BaseModel):
    """创建学习路径请求"""
    title: str = Field(..., description="路径标题")
    description: Optional[str] = Field(None, description="路径描述")
    steps: List[LearningPathStep] = Field(default_factory=list, description="步骤列表")


class LearningPathUpdateRequest(BaseModel):
    """更新学习路径请求"""
    title: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[List[LearningPathStep]] = None
    status: Optional[str] = Field(None, description="active / completed / paused")


class LearningPathResponse(BaseModel):
    """学习路径响应"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    steps: str
    status: str
    created_at: datetime
    updated_at: datetime


class LearningPathListResponse(BaseModel):
    """学习路径列表响应"""
    total: int
    items: List[LearningPathResponse]


class LearningPathProgressStats(BaseModel):
    """学习进度统计响应"""
    total_paths: int
    active_paths: int
    completed_paths: int
    total_steps: int
    completed_steps: int
    overall_progress: float


# ========== 接口实现 ==========

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_learning_path(
    request: LearningPathCreateRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    创建学习路径
    """
    path_id = str(uuid.uuid4())
    steps_json = json.dumps([step.model_dump() for step in request.steps], ensure_ascii=False)

    new_path = LearningPath(
        id=path_id,
        user_id=user_id,
        title=request.title,
        description=request.description,
        steps=steps_json,
        status="active"
    )

    db.add(new_path)
    db.commit()
    db.refresh(new_path)

    return new_path


@router.get("", response_model=LearningPathListResponse)
async def list_learning_paths(
    status: Optional[str] = Query(None, description="按状态筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的学习路径列表
    """
    query = db.query(LearningPath).filter(LearningPath.user_id == user_id)

    if status:
        query = query.filter(LearningPath.status == status)

    total = query.count()
    items = query.order_by(LearningPath.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {"total": total, "items": items}


@router.get("/{path_id}", response_model=LearningPathResponse)
async def get_learning_path(
    path_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取学习路径详情
    """
    path = db.query(LearningPath).filter(
        LearningPath.id == path_id,
        LearningPath.user_id == user_id
    ).first()

    if not path:
        raise HTTPException(status_code=404, detail="学习路径不存在")

    return path


@router.put("/{path_id}")
async def update_learning_path(
    path_id: str,
    request: LearningPathUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    更新学习路径（标题、描述、步骤、状态）
    """
    path = db.query(LearningPath).filter(
        LearningPath.id == path_id,
        LearningPath.user_id == user_id
    ).first()

    if not path:
        raise HTTPException(status_code=404, detail="学习路径不存在")

    update_data = request.model_dump(exclude_unset=True)

    if "steps" in update_data and update_data["steps"] is not None:
        update_data["steps"] = json.dumps(
            [step.model_dump() for step in update_data["steps"]],
            ensure_ascii=False
        )

    for field, value in update_data.items():
        setattr(path, field, value)

    db.commit()
    db.refresh(path)

    return path


@router.delete("/{path_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_learning_path(
    path_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    删除学习路径
    """
    path = db.query(LearningPath).filter(
        LearningPath.id == path_id,
        LearningPath.user_id == user_id
    ).first()

    if not path:
        raise HTTPException(status_code=404, detail="学习路径不存在")

    db.delete(path)
    db.commit()

    return None


@router.post("/{path_id}/steps/{step_index}/complete")
async def complete_step(
    path_id: str,
    step_index: int,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    完成某个步骤
    """
    path = db.query(LearningPath).filter(
        LearningPath.id == path_id,
        LearningPath.user_id == user_id
    ).first()

    if not path:
        raise HTTPException(status_code=404, detail="学习路径不存在")

    try:
        steps = json.loads(path.steps) if path.steps else []
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="步骤数据格式错误")

    if step_index < 0 or step_index >= len(steps):
        raise HTTPException(status_code=400, detail="步骤索引超出范围")

    steps[step_index]["status"] = "completed"
    path.steps = json.dumps(steps, ensure_ascii=False)

    # 如果所有步骤都已完成，自动标记路径为 completed
    if all(step.get("status") == "completed" for step in steps):
        path.status = "completed"

    db.commit()
    db.refresh(path)

    return {
        "message": "步骤已完成",
        "step_index": step_index,
        "path_status": path.status
    }


@router.get("/stats/progress", response_model=LearningPathProgressStats)
async def get_learning_progress(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取学习进度统计
    """
    paths = db.query(LearningPath).filter(LearningPath.user_id == user_id).all()

    total_paths = len(paths)
    active_paths = sum(1 for p in paths if p.status == "active")
    completed_paths = sum(1 for p in paths if p.status == "completed")

    total_steps = 0
    completed_steps = 0

    for path in paths:
        try:
            steps = json.loads(path.steps) if path.steps else []
        except json.JSONDecodeError:
            continue
        total_steps += len(steps)
        completed_steps += sum(1 for s in steps if s.get("status") == "completed")

    overall_progress = (
        (completed_steps / total_steps) * 100 if total_steps > 0 else 0.0
    )

    return {
        "total_paths": total_paths,
        "active_paths": active_paths,
        "completed_paths": completed_paths,
        "total_steps": total_steps,
        "completed_steps": completed_steps,
        "overall_progress": round(overall_progress, 2)
    }
