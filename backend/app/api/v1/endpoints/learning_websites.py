"""
学习网站链接接口
支持：网站链接的增删改查、分类筛选、推荐列表
"""
import uuid
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.database import LearningWebsite, get_db
from app.core.security import get_current_user_id

router = APIRouter()


# ========== 请求/响应模型 ==========

class LearningWebsiteCreateRequest(BaseModel):
    """创建学习网站请求"""
    name: str = Field(..., description="网站名称")
    url: str = Field(..., description="网站链接")
    description: Optional[str] = Field(None, description="网站描述")
    category: str = Field("general", description="分类: programming/math/language/video/course/general")
    icon: Optional[str] = Field(None, description="图标URL")
    is_recommended: bool = Field(False, description="是否推荐")
    sort_order: int = Field(0, description="排序顺序")


class LearningWebsiteUpdateRequest(BaseModel):
    """更新学习网站请求"""
    name: Optional[str] = Field(None, description="网站名称")
    url: Optional[str] = Field(None, description="网站链接")
    description: Optional[str] = Field(None, description="网站描述")
    category: Optional[str] = Field(None, description="分类")
    icon: Optional[str] = Field(None, description="图标URL")
    is_recommended: Optional[bool] = Field(None, description="是否推荐")
    sort_order: Optional[int] = Field(None, description="排序顺序")
    status: Optional[str] = Field(None, description="active / inactive")


class LearningWebsiteResponse(BaseModel):
    """学习网站响应"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    url: str
    description: Optional[str]
    category: str
    icon: Optional[str]
    is_recommended: bool
    sort_order: int
    status: str
    created_at: datetime
    updated_at: datetime


class LearningWebsiteListResponse(BaseModel):
    """学习网站列表响应"""
    total: int
    items: List[LearningWebsiteResponse]


# ========== 接口实现 ==========

@router.post("", status_code=status.HTTP_201_CREATED, response_model=LearningWebsiteResponse)
async def create_learning_website(
    request: LearningWebsiteCreateRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    添加学习网站链接
    """
    website_id = str(uuid.uuid4())
    new_website = LearningWebsite(
        id=website_id,
        name=request.name,
        url=request.url,
        description=request.description,
        category=request.category,
        icon=request.icon,
        is_recommended=request.is_recommended,
        sort_order=request.sort_order,
        status="active",
    )

    db.add(new_website)
    db.commit()
    db.refresh(new_website)

    return new_website


@router.get("", response_model=LearningWebsiteListResponse)
async def list_learning_websites(
    category: Optional[str] = Query(None, description="按分类筛选"),
    is_recommended: Optional[bool] = Query(None, description="是否只显示推荐"),
    keyword: Optional[str] = Query(None, description="关键词搜索（名称+描述）"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取学习网站链接列表（支持分类筛选和搜索）
    """
    query = db.query(LearningWebsite).filter(LearningWebsite.status == "active")

    if category:
        query = query.filter(LearningWebsite.category == category)
    if is_recommended is not None:
        query = query.filter(LearningWebsite.is_recommended == is_recommended)
    if keyword:
        query = query.filter(
            or_(
                LearningWebsite.name.contains(keyword),
                LearningWebsite.description.contains(keyword),
            )
        )

    total = query.count()
    items = query.order_by(LearningWebsite.sort_order.asc(), LearningWebsite.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {"total": total, "items": items}


@router.get("/recommended", response_model=LearningWebsiteListResponse)
async def get_recommended_websites(
    category: Optional[str] = Query(None, description="按分类筛选"),
    limit: int = Query(10, ge=1, le=50, description="数量限制"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取推荐的学习网站链接
    """
    query = db.query(LearningWebsite).filter(
        LearningWebsite.status == "active",
        LearningWebsite.is_recommended == True
    )

    if category:
        query = query.filter(LearningWebsite.category == category)

    items = query.order_by(LearningWebsite.sort_order.asc()).limit(limit).all()

    return {"total": len(items), "items": items}


@router.get("/categories")
async def get_categories(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取所有分类列表
    """
    categories = [r[0] for r in db.query(LearningWebsite.category).filter(
        LearningWebsite.status == "active"
    ).distinct().all() if r[0]]

    return {"categories": sorted(categories)}


@router.get("/{website_id}", response_model=LearningWebsiteResponse)
async def get_learning_website(
    website_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取学习网站详情
    """
    website = db.query(LearningWebsite).filter(
        LearningWebsite.id == website_id,
        LearningWebsite.status == "active"
    ).first()

    if not website:
        raise HTTPException(status_code=404, detail="网站链接不存在")

    return website


@router.put("/{website_id}", response_model=LearningWebsiteResponse)
async def update_learning_website(
    website_id: str,
    request: LearningWebsiteUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    更新学习网站链接
    """
    website = db.query(LearningWebsite).filter(
        LearningWebsite.id == website_id
    ).first()

    if not website:
        raise HTTPException(status_code=404, detail="网站链接不存在")

    update_data = request.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(website, field, value)

    db.commit()
    db.refresh(website)

    return website


@router.delete("/{website_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_learning_website(
    website_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    删除学习网站链接（软删除）
    """
    website = db.query(LearningWebsite).filter(
        LearningWebsite.id == website_id
    ).first()

    if not website:
        raise HTTPException(status_code=404, detail="网站链接不存在")

    website.status = "inactive"
    db.commit()

    return None
