"""
通知功能接口
"""
import uuid
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session

from app.models.database import Notification, get_db
from app.core.security import get_current_user_id

router = APIRouter()


# ========== 请求/响应模型 ==========

class NotificationResponse(BaseModel):
    """通知响应"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
    content: str
    type: str
    is_read: bool
    created_at: datetime


class NotificationListResponse(BaseModel):
    """通知列表响应"""
    total: int
    items: List[NotificationResponse]


class UnreadCountResponse(BaseModel):
    """未读数量响应"""
    count: int


# ========== 接口实现 ==========

@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    is_read: Optional[bool] = Query(None, description="按已读状态筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取通知列表（支持按 is_read 筛选）
    """
    query = db.query(Notification).filter(Notification.user_id == user_id)

    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)

    total = query.count()
    items = query.order_by(Notification.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {"total": total, "items": items}


@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    标记通知为已读
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="通知不存在")

    notification.is_read = True
    db.commit()
    db.refresh(notification)

    return notification


@router.put("/read-all")
async def mark_all_notifications_read(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    标记所有通知为已读
    """
    db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).update({"is_read": True})

    db.commit()

    return {"message": "所有通知已标记为已读"}


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    删除通知
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="通知不存在")

    db.delete(notification)
    db.commit()

    return None


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取未读通知数量
    """
    count = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).count()

    return {"count": count}
