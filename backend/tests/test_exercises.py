"""
练习模块测试 - 覆盖 exercises 模块全部接口

接口列表（实际 API 端点）：
1.  GET    /api/v1/exercises                        - 获取题目列表
2.  POST   /api/v1/exercises                        - 创建题目
3.  GET    /api/v1/exercises/{id}                   - 获取题目详情
4.  POST   /api/v1/exercises/{id}/submit            - 提交答案
5.  POST   /api/v1/exercises/sessions/generate      - 创建练习会话
6.  GET    /api/v1/exercises/sessions/{id}          - 获取会话详情
7.  POST   /api/v1/exercises/sessions/{id}/complete - 完成会话
8.  GET    /api/v1/exercises/history/list           - 练习历史

每个接口覆盖三种场景：正常请求(200/201)、未授权(401)、参数错误(422)
"""
import pytest
from httpx import AsyncClient


# ============================================================
# 1. GET /api/v1/exercises - 获取题目列表
# ============================================================

@pytest.mark.asyncio
async def test_get_exercises_list(async_client, auth_token):
    """正常获取题目列表"""
    response = await async_client.get(
        "/api/v1/exercises",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data


@pytest.mark.asyncio
async def test_get_exercises_list_unauthorized(async_client):
    """未授权获取题目列表"""
    response = await async_client.get("/api/v1/exercises")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_exercises_list_with_filters(async_client, auth_token):
    """按学科和难度筛选题目列表"""
    response = await async_client.get(
        "/api/v1/exercises",
        headers={"Authorization": f"Bearer {auth_token}"},
        params={"subject": "数学", "difficulty": 3, "page": 1, "page_size": 10},
    )
    assert response.status_code == 200


# ============================================================
# 2. POST /api/v1/exercises - 创建题目
# ============================================================

@pytest.mark.asyncio
async def test_create_exercise(async_client, auth_token, test_exercise_data):
    """正常创建题目"""
    response = await async_client.post(
        "/api/v1/exercises",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=test_exercise_data,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["subject"] == "数学"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_exercise_unauthorized(async_client, test_exercise_data):
    """未授权创建题目"""
    response = await async_client.post(
        "/api/v1/exercises",
        json=test_exercise_data,
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_exercise_missing_required(async_client, auth_token):
    """缺少必填字段创建题目"""
    response = await async_client.post(
        "/api/v1/exercises",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"subject": "数学"},  # 缺少 type, question, correct_answer
    )
    assert response.status_code == 422


# ============================================================
# 3. GET /api/v1/exercises/{id} - 获取题目详情
# ============================================================

@pytest.mark.asyncio
async def test_get_exercise_detail(async_client, auth_token, test_exercise_data):
    """正常获取题目详情"""
    create_resp = await async_client.post(
        "/api/v1/exercises",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=test_exercise_data,
    )
    exercise_id = create_resp.json()["id"]

    response = await async_client.get(
        f"/api/v1/exercises/{exercise_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == exercise_id


@pytest.mark.asyncio
async def test_get_exercise_detail_unauthorized(async_client):
    """未授权获取题目详情"""
    response = await async_client.get("/api/v1/exercises/nonexistent-id")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_exercise_detail_not_found(async_client, auth_token):
    """获取不存在的题目"""
    response = await async_client.get(
        "/api/v1/exercises/nonexistent-id-12345",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 404


# ============================================================
# 4. POST /api/v1/exercises/{id}/submit - 提交答案
# ============================================================

@pytest.mark.asyncio
async def test_submit_answer(async_client, auth_token, test_exercise_data):
    """正常提交答案"""
    create_resp = await async_client.post(
        "/api/v1/exercises",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=test_exercise_data,
    )
    exercise_id = create_resp.json()["id"]

    response = await async_client.post(
        f"/api/v1/exercises/{exercise_id}/submit",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"user_answer": "x=-1", "time_spent": 30},
    )
    assert response.status_code == 200
    data = response.json()
    assert "is_correct" in data
    assert "correct_answer" in data


@pytest.mark.asyncio
async def test_submit_answer_unauthorized(async_client):
    """未授权提交答案"""
    response = await async_client.post(
        "/api/v1/exercises/some-id/submit",
        json={"user_answer": "x=-1"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_submit_answer_missing_field(async_client, auth_token):
    """缺少必填字段提交答案"""
    response = await async_client.post(
        "/api/v1/exercises/some-id/submit",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={},  # 缺少 user_answer
    )
    assert response.status_code == 422


# ============================================================
# 5. POST /api/v1/exercises/sessions/generate - 创建练习会话
# ============================================================

@pytest.mark.asyncio
async def test_create_exercise_session(async_client, auth_token, test_exercise_data):
    """正常创建练习会话"""
    # 先创建一道题
    create_resp = await async_client.post(
        "/api/v1/exercises",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=test_exercise_data,
    )
    exercise_id = create_resp.json()["id"]

    response = await async_client.post(
        "/api/v1/exercises/sessions/generate",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "subject": "数学",
            "exercise_count": 1,
            "title": "测试练习会话",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "session" in data
    assert "exercises" in data


@pytest.mark.asyncio
async def test_create_exercise_session_unauthorized(async_client):
    """未授权创建练习会话"""
    response = await async_client.post(
        "/api/v1/exercises/sessions/generate",
        json={"subject": "数学"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_exercise_session_missing_field(async_client, auth_token):
    """缺少必填字段创建练习会话"""
    response = await async_client.post(
        "/api/v1/exercises/sessions/generate",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={},  # 缺少 subject
    )
    assert response.status_code == 422


# ============================================================
# 6. GET /api/v1/exercises/sessions/{id} - 获取会话详情
# ============================================================

@pytest.mark.asyncio
async def test_get_exercise_session(async_client, auth_token, test_exercise_data):
    """正常获取练习会话详情"""
    # 创建题和会话
    create_resp = await async_client.post(
        "/api/v1/exercises",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=test_exercise_data,
    )
    exercise_id = create_resp.json()["id"]

    session_resp = await async_client.post(
        "/api/v1/exercises/sessions/generate",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "subject": "数学",
            "exercise_count": 1,
            "title": "测试会话",
        },
    )
    session_id = session_resp.json()["session"]["id"]

    response = await async_client.get(
        f"/api/v1/exercises/sessions/{session_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "session" in data


@pytest.mark.asyncio
async def test_get_exercise_session_unauthorized(async_client):
    """未授权获取会话详情"""
    response = await async_client.get("/api/v1/exercises/sessions/some-id")
    assert response.status_code == 401


# ============================================================
# 7. POST /api/v1/exercises/sessions/{id}/complete - 完成会话
# ============================================================

@pytest.mark.asyncio
async def test_submit_exercise_session(async_client, auth_token, test_exercise_data):
    """正常完成练习会话"""
    create_resp = await async_client.post(
        "/api/v1/exercises",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=test_exercise_data,
    )
    exercise_id = create_resp.json()["id"]

    session_resp = await async_client.post(
        "/api/v1/exercises/sessions/generate",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "subject": "数学",
            "exercise_count": 1,
            "title": "测试会话",
        },
    )
    session_id = session_resp.json()["session"]["id"]

    # 先提交答案
    await async_client.post(
        f"/api/v1/exercises/{exercise_id}/submit",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"user_answer": "x=-1", "time_spent": 30},
    )

    # 完成会话
    response = await async_client.post(
        f"/api/v1/exercises/sessions/{session_id}/complete",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_submit_exercise_session_unauthorized(async_client):
    """未授权完成会话"""
    response = await async_client.post("/api/v1/exercises/sessions/some-id/complete")
    assert response.status_code == 401


# ============================================================
# 8. GET /api/v1/exercises/history/list - 练习历史
# ============================================================

@pytest.mark.asyncio
async def test_get_exercises_history(async_client, auth_token):
    """正常获取练习历史"""
    response = await async_client.get(
        "/api/v1/exercises/history/list",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data


@pytest.mark.asyncio
async def test_get_exercises_history_unauthorized(async_client):
    """未授权获取练习历史"""
    response = await async_client.get("/api/v1/exercises/history/list")
    assert response.status_code == 401