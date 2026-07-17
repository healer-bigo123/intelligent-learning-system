"""
成就系统模块测试 - 覆盖 achievements 模块核心接口

接口列表：
1. GET  /api/v1/achievements            - 获取所有成就列表
2. GET  /api/v1/achievements/my         - 获取我的成就
3. POST /api/v1/achievements/check      - 检查并解锁成就
4. GET  /api/v1/achievements/leaderboard - 获取排行榜
"""
import uuid
import pytest

from app.models.database import SessionLocal, Achievement, UserAchievement, Exercise, ExerciseRecord
from sqlalchemy import text


# 用于成就测试的唯一学科标识，便于清理
_ACHIEVEMENT_TEST_SUBJECT = "AchievementTestSubject"


# ============================================================
# Fixtures
# ============================================================

def _create_test_achievement() -> str:
    """创建一个用于测试的成就定义（练习1次即可解锁）"""
    db = SessionLocal()
    try:
        db.execute(text("PRAGMA foreign_keys = ON"))
        achievement = Achievement(
            id=str(uuid.uuid4()),
            name="初次练习",
            description="完成1次练习即可解锁",
            icon="🏅",
            condition_type="exercise_count",
            condition_value=1,
        )
        db.add(achievement)
        db.commit()
        return achievement.id
    finally:
        db.close()


@pytest.fixture
async def achievement_setup(current_user_id):
    """创建测试成就定义，测试结束后清理相关数据"""
    achievement_id = _create_test_achievement()
    yield achievement_id

    db = SessionLocal()
    try:
        db.execute(text("PRAGMA foreign_keys = ON"))
        # 删除用户已解锁的该成就记录
        db.query(UserAchievement).filter(
            UserAchievement.user_id == current_user_id,
            UserAchievement.achievement_id == achievement_id
        ).delete(synchronize_session=False)

        # 删除成就测试过程中创建的练习记录与练习题
        test_exercises = db.query(Exercise).filter(
            Exercise.user_id == current_user_id,
            Exercise.subject == _ACHIEVEMENT_TEST_SUBJECT
        ).all()
        test_exercise_ids = [e.id for e in test_exercises]
        if test_exercise_ids:
            db.query(ExerciseRecord).filter(
                ExerciseRecord.exercise_id.in_(test_exercise_ids)
            ).delete(synchronize_session=False)
            for exercise in test_exercises:
                db.delete(exercise)

        # 删除成就定义
        achievement = db.query(Achievement).filter(Achievement.id == achievement_id).first()
        if achievement:
            db.delete(achievement)

        db.commit()
    finally:
        db.close()


@pytest.fixture
async def unlocked_achievement(async_client, auth_token, achievement_setup):
    """完成一次练习并触发成就解锁，返回成就 ID"""
    # 创建一道练习题
    create_response = await async_client.post(
        "/api/v1/exercises",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "subject": _ACHIEVEMENT_TEST_SUBJECT,
            "type": "choice",
            "question": "成就测试题：2 + 2 = ?",
            "options": ["3", "4", "5"],
            "correct_answer": "4",
            "difficulty": 1,
            "knowledge_point": "加法",
        },
    )
    assert create_response.status_code == 201
    exercise_id = create_response.json()["id"]

    # 提交答案，产生答题记录
    submit_response = await async_client.post(
        f"/api/v1/exercises/{exercise_id}/submit",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"user_answer": "4", "time_spent": 10},
    )
    assert submit_response.status_code == 200

    # 触发成就检查
    check_response = await async_client.post(
        "/api/v1/achievements/check",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert check_response.status_code == 200
    assert any(item["id"] == achievement_setup for item in check_response.json()["newly_unlocked"])

    yield achievement_setup


# ============================================================
# 1. 获取所有成就列表
# ============================================================

@pytest.mark.asyncio
async def test_list_achievements(async_client, achievement_setup):
    """正常获取成就列表"""
    response = await async_client.get("/api/v1/achievements")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(item["id"] == achievement_setup for item in data)


# ============================================================
# 2. 获取我的成就
# ============================================================

@pytest.mark.asyncio
async def test_get_my_achievements(async_client, auth_token, unlocked_achievement):
    """获取已解锁的成就列表"""
    response = await async_client.get(
        "/api/v1/achievements/my",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert any(item["achievement"]["id"] == unlocked_achievement for item in data["items"])


@pytest.mark.asyncio
async def test_get_my_achievements_unauthorized(async_client):
    """未授权获取我的成就"""
    response = await async_client.get("/api/v1/achievements/my")
    assert response.status_code == 401


# ============================================================
# 3. 检查并解锁成就
# ============================================================

@pytest.mark.asyncio
async def test_check_achievements_unlock(async_client, auth_token, achievement_setup):
    """满足条件后调用 check 接口解锁成就"""
    # 创建并提交练习，产生答题记录
    create_response = await async_client.post(
        "/api/v1/exercises",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "subject": _ACHIEVEMENT_TEST_SUBJECT,
            "type": "choice",
            "question": "成就测试题：1 + 1 = ?",
            "options": ["1", "2", "3"],
            "correct_answer": "2",
            "difficulty": 1,
            "knowledge_point": "加法",
        },
    )
    assert create_response.status_code == 201
    exercise_id = create_response.json()["id"]

    await async_client.post(
        f"/api/v1/exercises/{exercise_id}/submit",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"user_answer": "2", "time_spent": 5},
    )

    # 检查成就
    response = await async_client.post(
        "/api/v1/achievements/check",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert any(item["id"] == achievement_setup for item in data["newly_unlocked"])


@pytest.mark.asyncio
async def test_check_achievements_already_unlocked(async_client, auth_token, unlocked_achievement):
    """已解锁的成就再次检查不应重复返回"""
    response = await async_client.post(
        "/api/v1/achievements/check",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    assert unlocked_achievement not in [item["id"] for item in response.json()["newly_unlocked"]]


@pytest.mark.asyncio
async def test_check_achievements_unauthorized(async_client):
    """未授权检查成就"""
    response = await async_client.post("/api/v1/achievements/check")
    assert response.status_code == 401


# ============================================================
# 4. 获取排行榜
# ============================================================

@pytest.mark.asyncio
async def test_get_achievement_leaderboard(async_client, auth_token, unlocked_achievement):
    """排行榜中应包含当前用户"""
    response = await async_client.get("/api/v1/achievements/leaderboard")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert any(item["unlocked_count"] >= 1 for item in data["items"])
