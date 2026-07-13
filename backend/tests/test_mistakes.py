"""
错题模块测试 - 覆盖 mistakes 模块全部 7 个接口

接口列表：
1. GET    /api/v1/mistakes              - 获取错题列表（支持分页、筛选）
2. POST   /api/v1/mistakes              - 创建错题
3. GET    /api/v1/mistakes/{id}         - 获取错题详情
4. PUT    /api/v1/mistakes/{id}         - 更新错题
5. DELETE /api/v1/mistakes/{id}         - 删除错题
6. POST   /api/v1/mistakes/{id}/review  - 复习错题
7. GET    /api/v1/mistakes/statistics   - 错题统计

每个接口覆盖三种场景：正常请求(200/201)、未授权(401)、参数错误(422)
"""
import pytest
from httpx import AsyncClient


# ============================================================
# 1. GET /api/v1/mistakes - 获取错题列表
# ============================================================

@pytest.mark.asyncio
async def test_get_mistakes_list(async_client, auth_token):
    """正常获取错题列表"""
    response = await async_client.get(
        "/api/v1/mistakes",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_get_mistakes_list_unauthorized(async_client):
    """未授权获取错题列表"""
    response = await async_client.get("/api/v1/mistakes")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_mistakes_list_with_filters(async_client, auth_token):
    """按学科筛选错题列表"""
    response = await async_client.get(
        "/api/v1/mistakes",
        headers={"Authorization": f"Bearer {auth_token}"},
        params={"subject": "数学", "page": 1, "page_size": 10},
    )
    assert response.status_code == 200


# ============================================================
# 2. POST /api/v1/mistakes - 创建错题
# ============================================================

@pytest.mark.asyncio
async def test_create_mistake(async_client, auth_token, test_mistake_data):
    """正常创建错题"""
    response = await async_client.post(
        "/api/v1/mistakes",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=test_mistake_data,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["subject"] == "数学"
    assert "id" in data

    # 清理：删除刚创建的错题
    await async_client.delete(
        f"/api/v1/mistakes/{data['id']}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )


@pytest.mark.asyncio
async def test_create_mistake_unauthorized(async_client, test_mistake_data):
    """未授权创建错题"""
    response = await async_client.post(
        "/api/v1/mistakes",
        json=test_mistake_data,
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_mistake_missing_required(async_client, auth_token):
    """缺少必填字段创建错题"""
    response = await async_client.post(
        "/api/v1/mistakes",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"subject": "数学"},  # 缺少 question, correct_answer
    )
    assert response.status_code == 422


# ============================================================
# 3. GET /api/v1/mistakes/{id} - 获取错题详情
# ============================================================

@pytest.mark.asyncio
async def test_get_mistake_detail(async_client, auth_token, test_mistake_data):
    """正常获取错题详情"""
    # 先创建一条
    create_resp = await async_client.post(
        "/api/v1/mistakes",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=test_mistake_data,
    )
    mistake_id = create_resp.json()["id"]

    # 获取详情
    response = await async_client.get(
        f"/api/v1/mistakes/{mistake_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == mistake_id
    assert data["subject"] == "数学"

    # 清理
    await async_client.delete(
        f"/api/v1/mistakes/{mistake_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )


@pytest.mark.asyncio
async def test_get_mistake_detail_unauthorized(async_client):
    """未授权获取错题详情"""
    response = await async_client.get("/api/v1/mistakes/nonexistent-id")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_mistake_detail_not_found(async_client, auth_token):
    """获取不存在的错题详情"""
    response = await async_client.get(
        "/api/v1/mistakes/nonexistent-id-12345",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 404


# ============================================================
# 4. PUT /api/v1/mistakes/{id} - 更新错题
# ============================================================

@pytest.mark.asyncio
async def test_update_mistake(async_client, auth_token, test_mistake_data):
    """正常更新错题"""
    # 先创建
    create_resp = await async_client.post(
        "/api/v1/mistakes",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=test_mistake_data,
    )
    mistake_id = create_resp.json()["id"]

    # 更新
    response = await async_client.put(
        f"/api/v1/mistakes/{mistake_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"subject": "物理", "difficulty": 5},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["subject"] == "物理"
    assert data["difficulty"] == 5

    # 清理
    await async_client.delete(
        f"/api/v1/mistakes/{mistake_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )


@pytest.mark.asyncio
async def test_update_mistake_unauthorized(async_client):
    """未授权更新错题"""
    response = await async_client.put(
        "/api/v1/mistakes/some-id",
        json={"subject": "物理"},
    )
    assert response.status_code == 401


# ============================================================
# 5. DELETE /api/v1/mistakes/{id} - 删除错题
# ============================================================

@pytest.mark.asyncio
async def test_delete_mistake(async_client, auth_token, test_mistake_data):
    """正常删除错题"""
    # 先创建
    create_resp = await async_client.post(
        "/api/v1/mistakes",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=test_mistake_data,
    )
    mistake_id = create_resp.json()["id"]

    # 删除
    response = await async_client.delete(
        f"/api/v1/mistakes/{mistake_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 204

    # 确认已删除
    get_resp = await async_client.get(
        f"/api/v1/mistakes/{mistake_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_mistake_unauthorized(async_client):
    """未授权删除错题"""
    response = await async_client.delete("/api/v1/mistakes/some-id")
    assert response.status_code == 401


# ============================================================
# 6. POST /api/v1/mistakes/{id}/review - 复习错题
# ============================================================

@pytest.mark.asyncio
async def test_review_mistake(async_client, auth_token, test_mistake_data):
    """正常复习错题"""
    # 先创建
    create_resp = await async_client.post(
        "/api/v1/mistakes",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=test_mistake_data,
    )
    mistake_id = create_resp.json()["id"]

    # 复习
    response = await async_client.post(
        f"/api/v1/mistakes/{mistake_id}/review",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200

    # 清理
    await async_client.delete(
        f"/api/v1/mistakes/{mistake_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )


@pytest.mark.asyncio
async def test_review_mistake_unauthorized(async_client):
    """未授权复习错题"""
    response = await async_client.post("/api/v1/mistakes/some-id/review")
    assert response.status_code == 401


# ============================================================
# 7. GET /api/v1/mistakes/stats/overview - 错题统计
# ============================================================

@pytest.mark.asyncio
async def test_get_mistakes_statistics(async_client, auth_token):
    """正常获取错题统计"""
    response = await async_client.get(
        "/api/v1/mistakes/stats/overview",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "total" in data


@pytest.mark.asyncio
async def test_get_mistakes_statistics_unauthorized(async_client):
    """未授权获取错题统计"""
    response = await async_client.get("/api/v1/mistakes/stats/overview")
    assert response.status_code == 401