"""
成就系统接口
"""
import uuid
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct

from app.models.database import (
    Achievement, UserAchievement, ExerciseRecord, ExerciseSession,
    StudyActivity, Favorite, get_db
)
from app.core.security import get_current_user_id

router = APIRouter()


# ========== 请求/响应模型 ==========

class AchievementResponse(BaseModel):
    """成就响应"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str
    icon: Optional[str] = None
    condition_type: str
    condition_value: int
    created_at: datetime


class UserAchievementResponse(BaseModel):
    """用户成就响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str
    achievement_id: str
    unlocked_at: datetime


class MyAchievementItem(BaseModel):
    """我的成就项"""
    achievement: AchievementResponse
    unlocked_at: datetime


class MyAchievementListResponse(BaseModel):
    """我的成就列表响应"""
    total: int
    items: List[MyAchievementItem]


class AchievementCheckResponse(BaseModel):
    """成就检查响应"""
    newly_unlocked: List[AchievementResponse]


class LeaderboardItem(BaseModel):
    """排行榜项"""
    user_id: str
    unlocked_count: int


class LeaderboardResponse(BaseModel):
    """排行榜响应"""
    items: List[LeaderboardItem]


# ========== 辅助函数 ==========

def _get_exercise_count(db: Session, user_id: str) -> int:
    """获取用户练习次数"""
    return db.query(ExerciseRecord).filter(ExerciseRecord.user_id == user_id).count()


def _get_streak_days(db: Session, user_id: str) -> int:
    """获取用户连续学习天数（简化计算：有学习活动记录的不同日期数）"""
    activities = db.query(StudyActivity).filter(
        StudyActivity.user_id == user_id
    ).order_by(StudyActivity.created_at.desc()).all()

    if not activities:
        return 0

    # 获取有活动的日期集合
    activity_dates = set()
    for a in activities:
        activity_dates.add(a.created_at.date())

    if not activity_dates:
        return 0

    # 计算连续天数（从今天往前数）
    sorted_dates = sorted(activity_dates, reverse=True)
    streak = 1
    today = datetime.utcnow().date()

    # 如果今天没有活动，从最后一天开始算
    check_date = sorted_dates[0]
    if check_date != today and (today - check_date).days > 1:
        # 已经连续中断
        return 0

    for i in range(1, len(sorted_dates)):
        if (sorted_dates[i - 1] - sorted_dates[i]).days == 1:
            streak += 1
        else:
            break

    return streak


def _get_accuracy(db: Session, user_id: str) -> int:
    """获取用户正确率（百分比）"""
    total = db.query(ExerciseRecord).filter(ExerciseRecord.user_id == user_id).count()
    if total == 0:
        return 0
    correct = db.query(ExerciseRecord).filter(
        ExerciseRecord.user_id == user_id,
        ExerciseRecord.is_correct == True
    ).count()
    return int((correct / total) * 100)


def _get_material_count(db: Session, user_id: str) -> int:
    """获取用户收藏资料数"""
    return db.query(Favorite).filter(
        Favorite.user_id == user_id,
        Favorite.target_type == "study_material"
    ).count()


def _check_condition(db: Session, user_id: str, condition_type: str, condition_value: int) -> bool:
    """检查用户是否满足成就条件"""
    if condition_type == "exercise_count":
        return _get_exercise_count(db, user_id) >= condition_value
    elif condition_type == "streak_days":
        return _get_streak_days(db, user_id) >= condition_value
    elif condition_type == "accuracy":
        return _get_accuracy(db, user_id) >= condition_value
    elif condition_type == "material_count":
        return _get_material_count(db, user_id) >= condition_value
    return False


# ========== 接口实现 ==========

@router.get("", response_model=List[AchievementResponse])
async def list_achievements(
    db: Session = Depends(get_db)
):
    """
    获取所有成就列表
    """
    items = db.query(Achievement).order_by(Achievement.created_at.desc()).all()
    return items


@router.get("/my", response_model=MyAchievementListResponse)
async def get_my_achievements(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取当前用户已解锁的成就
    """
    results = db.query(UserAchievement, Achievement).join(
        Achievement, UserAchievement.achievement_id == Achievement.id
    ).filter(UserAchievement.user_id == user_id).order_by(
        UserAchievement.unlocked_at.desc()
    ).all()

    items = []
    for ua, ach in results:
        items.append({
            "achievement": ach,
            "unlocked_at": ua.unlocked_at
        })

    return {"total": len(items), "items": items}


@router.post("/check", response_model=AchievementCheckResponse)
async def check_achievements(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    检查并解锁成就（根据用户的练习数、连续学习天数等条件自动检查）
    """
    # 获取所有成就
    achievements = db.query(Achievement).all()

    # 获取用户已解锁的成就ID
    unlocked_ids = {
        ua.achievement_id for ua in db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id
        ).all()
    }

    newly_unlocked = []

    for achievement in achievements:
        if achievement.id in unlocked_ids:
            continue

        if _check_condition(db, user_id, achievement.condition_type, achievement.condition_value):
            # 解锁成就
            user_achievement = UserAchievement(
                user_id=user_id,
                achievement_id=achievement.id
            )
            db.add(user_achievement)
            newly_unlocked.append(achievement)

    if newly_unlocked:
        db.commit()

    return {"newly_unlocked": newly_unlocked}


@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_achievement_leaderboard(
    limit: int = Query(20, ge=1, le=100, description="排行榜数量"),
    db: Session = Depends(get_db)
):
    """
    获取排行榜（按解锁成就数量排序）
    """
    results = db.query(
        UserAchievement.user_id,
        func.count(UserAchievement.id).label("unlocked_count")
    ).group_by(UserAchievement.user_id).order_by(
        func.count(UserAchievement.id).desc()
    ).limit(limit).all()

    items = [
        {"user_id": r.user_id, "unlocked_count": r.unlocked_count}
        for r in results
    ]

    return {"items": items}
