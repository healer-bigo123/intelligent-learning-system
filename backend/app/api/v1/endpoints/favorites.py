"""
收藏功能接口
"""
import uuid
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session

from app.models.database import Favorite, get_db
from app.core.security import get_current_user_id

router = APIRouter()


# ========== 请求/响应模型 ==========

class FavoriteCreateRequest(BaseModel):
    """添加收藏请求"""
    target_type: str = Field(..., description="收藏目标类型: study_material / mistake / exercise")
    target_id: str = Field(..., description="收藏目标ID")


class FavoriteResponse(BaseModel):
    """收藏响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str
    target_type: str
    target_id: str
    created_at: datetime


class FavoriteListResponse(BaseModel):
    """收藏列表响应"""
    total: int
    items: List[FavoriteResponse]


class FavoriteCheckResponse(BaseModel):
    """收藏检查响应"""
    is_favorited: bool


# ========== 接口实现 ==========

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_favorite(
    request: FavoriteCreateRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    添加收藏
    """
    # 检查是否已收藏
    existing = db.query(Favorite).filter(
        Favorite.user_id == user_id,
        Favorite.target_type == request.target_type,
        Favorite.target_id == request.target_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="已收藏该内容")

    favorite = Favorite(
        user_id=user_id,
        target_type=request.target_type,
        target_id=request.target_id
    )

    db.add(favorite)
    db.commit()
    db.refresh(favorite)

    return favorite


@router.get("", response_model=FavoriteListResponse)
async def list_favorites(
    target_type: Optional[str] = Query(None, description="按目标类型筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取收藏列表（支持按 target_type 筛选）
    """
    query = db.query(Favorite).filter(Favorite.user_id == user_id)

    if target_type:
        query = query.filter(Favorite.target_type == target_type)

    total = query.count()
    items = query.order_by(Favorite.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {"total": total, "items": items}


@router.delete("/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_favorite(
    favorite_id: int,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    取消收藏
    """
    favorite = db.query(Favorite).filter(
        Favorite.id == favorite_id,
        Favorite.user_id == user_id
    ).first()

    if not favorite:
        raise HTTPException(status_code=404, detail="收藏不存在")

    db.delete(favorite)
    db.commit()

    return None


@router.get("/check", response_model=FavoriteCheckResponse)
async def check_favorite(
    target_type: str = Query(..., description="目标类型"),
    target_id: str = Query(..., description="目标ID"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    检查是否已收藏
    """
    favorite = db.query(Favorite).filter(
        Favorite.user_id == user_id,
        Favorite.target_type == target_type,
        Favorite.target_id == target_id
    ).first()

    return {"is_favorited": favorite is not None}
