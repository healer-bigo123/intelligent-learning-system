"""
课堂互动模块测试 - 覆盖 classroom 模块核心接口

接口列表：
1. POST /api/v1/classrooms                     - 创建课堂
2. GET  /api/v1/classrooms                     - 获取课堂列表
3. GET  /api/v1/classrooms/{id}                - 获取课堂详情
4. POST /api/v1/classrooms/{id}/join           - 加入课堂
5. POST /api/v1/classrooms/{id}/votes          - 发起投票
6. GET  /api/v1/classrooms/{id}/votes/{vid}/result - 查看投票结果
7. POST /api/v1/classrooms/{id}/votes/{vid}/cast   - 投票
8. POST /api/v1/classrooms/{id}/lottery        - 随机抽签
9. POST /api/v1/classrooms/{id}/quizzes        - 发起随堂测验
10. POST /api/v1/classrooms/{id}/quizzes/{qid}/submit - 提交测验答案
11. GET  /api/v1/classrooms/{id}/quizzes/{qid}/result - 查看测验结果
12. POST /api/v1/classrooms/{id}/ppt           - 生成课堂 PPT
"""
import pytest

from app.models.database import SessionLocal, Classroom, LearningResource
from app.api.v1.endpoints import classroom as classroom_module
from sqlalchemy import text


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
async def created_classroom(async_client, auth_token):
    """创建一个测试课堂，测试结束后清理"""
    response = await async_client.post(
        "/api/v1/classrooms",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"name": "测试课堂", "description": "用于接口测试的课堂"},
    )
    assert response.status_code == 201
    classroom = response.json()

    yield classroom

    # 清理课堂（级联删除成员、投票、抽签、测验）
    db = SessionLocal()
    try:
        db.execute(text("PRAGMA foreign_keys = ON"))
        c = db.query(Classroom).filter(Classroom.id == classroom["id"]).first()
        if c:
            db.delete(c)
            db.commit()
    finally:
        db.close()


# ============================================================
# 1. 创建课堂
# ============================================================

@pytest.mark.asyncio
async def test_create_classroom(async_client, auth_token):
    """正常创建课堂"""
    response = await async_client.post(
        "/api/v1/classrooms",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"name": "初中数学课堂", "description": "测试描述"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "初中数学课堂"
    assert data["code"]
    assert len(data["code"]) == 6
    assert "id" in data

    # 清理
    db = SessionLocal()
    try:
        db.execute(text("PRAGMA foreign_keys = ON"))
        c = db.query(Classroom).filter(Classroom.id == data["id"]).first()
        if c:
            db.delete(c)
            db.commit()
    finally:
        db.close()


@pytest.mark.asyncio
async def test_create_classroom_unauthorized(async_client):
    """未授权创建课堂"""
    response = await async_client.post(
        "/api/v1/classrooms",
        json={"name": "未授权课堂"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_classroom_missing_name(async_client, auth_token):
    """缺少课堂名称应返回 422"""
    response = await async_client.post(
        "/api/v1/classrooms",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"description": "只有描述"},
    )
    assert response.status_code == 422


# ============================================================
# 2. 获取课堂列表
# ============================================================

@pytest.mark.asyncio
async def test_list_classrooms(async_client, auth_token, created_classroom):
    """正常获取课堂列表"""
    response = await async_client.get(
        "/api/v1/classrooms",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert any(item["id"] == created_classroom["id"] for item in data["items"])


@pytest.mark.asyncio
async def test_list_classrooms_unauthorized(async_client):
    """未授权获取课堂列表"""
    response = await async_client.get("/api/v1/classrooms")
    assert response.status_code == 401


# ============================================================
# 3. 获取课堂详情
# ============================================================

@pytest.mark.asyncio
async def test_get_classroom_detail(async_client, auth_token, created_classroom):
    """老师获取课堂详情"""
    response = await async_client.get(
        f"/api/v1/classrooms/{created_classroom['id']}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_classroom["id"]
    assert data["code"] == created_classroom["code"]
    assert "members" in data
    assert len(data["members"]) >= 1


@pytest.mark.asyncio
async def test_get_classroom_detail_unauthorized(async_client, created_classroom):
    """未授权获取课堂详情"""
    response = await async_client.get(f"/api/v1/classrooms/{created_classroom['id']}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_classroom_detail_non_member(async_client, created_classroom, second_auth_token):
    """非成员获取课堂详情应返回 403"""
    response = await async_client.get(
        f"/api/v1/classrooms/{created_classroom['id']}",
        headers={"Authorization": f"Bearer {second_auth_token}"},
    )
    assert response.status_code == 403


# ============================================================
# 4. 加入课堂
# ============================================================

@pytest.mark.asyncio
async def test_join_classroom(async_client, created_classroom, second_auth_token):
    """学生通过邀请码加入课堂"""
    response = await async_client.post(
        f"/api/v1/classrooms/{created_classroom['id']}/join",
        headers={"Authorization": f"Bearer {second_auth_token}"},
        json={"code": created_classroom["code"]},
    )
    assert response.status_code == 200
    assert "加入课堂成功" in response.json()["message"]

    # 学生列表中应包含该课堂
    list_response = await async_client.get(
        "/api/v1/classrooms",
        headers={"Authorization": f"Bearer {second_auth_token}"},
    )
    assert any(item["id"] == created_classroom["id"] for item in list_response.json()["items"])


@pytest.mark.asyncio
async def test_join_classroom_wrong_code(async_client, created_classroom, second_auth_token):
    """邀请码错误应返回 400"""
    response = await async_client.post(
        f"/api/v1/classrooms/{created_classroom['id']}/join",
        headers={"Authorization": f"Bearer {second_auth_token}"},
        json={"code": "000000"},
    )
    assert response.status_code == 400
    assert "邀请码错误" in response.json()["detail"]


@pytest.mark.asyncio
async def test_join_classroom_already_joined(async_client, created_classroom, second_auth_token):
    """重复加入课堂应返回 400"""
    await async_client.post(
        f"/api/v1/classrooms/{created_classroom['id']}/join",
        headers={"Authorization": f"Bearer {second_auth_token}"},
        json={"code": created_classroom["code"]},
    )

    response = await async_client.post(
        f"/api/v1/classrooms/{created_classroom['id']}/join",
        headers={"Authorization": f"Bearer {second_auth_token}"},
        json={"code": created_classroom["code"]},
    )
    assert response.status_code == 400
    assert "已在课堂中" in response.json()["detail"]


# ============================================================
# 5. 投票
# ============================================================

@pytest.mark.asyncio
async def test_create_and_cast_vote(async_client, auth_token, created_classroom, second_auth_token):
    """老师发起投票，学生投票后结果正确"""
    # 学生先加入课堂
    await async_client.post(
        f"/api/v1/classrooms/{created_classroom['id']}/join",
        headers={"Authorization": f"Bearer {second_auth_token}"},
        json={"code": created_classroom["code"]},
    )

    # 老师发起投票
    create_response = await async_client.post(
        f"/api/v1/classrooms/{created_classroom['id']}/votes",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"title": "最喜欢的学科", "options": ["数学", "英语", "物理"]},
    )
    assert create_response.status_code == 201
    vote_id = create_response.json()["id"]

    # 学生投票
    cast_response = await async_client.post(
        f"/api/v1/classrooms/{created_classroom['id']}/votes/{vote_id}/cast",
        headers={"Authorization": f"Bearer {second_auth_token}"},
        json={"option_index": 1},
    )
    assert cast_response.status_code == 200
    assert cast_response.json()["results"]["1"] == 1

    # 查看结果
    result_response = await async_client.get(
        f"/api/v1/classrooms/{created_classroom['id']}/votes/{vote_id}/result",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert result_response.status_code == 200
    assert result_response.json()["results"]["1"] == 1


@pytest.mark.asyncio
async def test_create_vote_not_teacher(async_client, created_classroom, second_auth_token):
    """非老师发起投票应返回 403"""
    response = await async_client.post(
        f"/api/v1/classrooms/{created_classroom['id']}/votes",
        headers={"Authorization": f"Bearer {second_auth_token}"},
        json={"title": "非法投票", "options": ["A", "B"]},
    )
    assert response.status_code == 403


# ============================================================
# 6. 随机抽签
# ============================================================

@pytest.mark.asyncio
async def test_create_lottery(async_client, auth_token, created_classroom):
    """老师发起抽签，获胜者在候选人中"""
    response = await async_client.post(
        f"/api/v1/classrooms/{created_classroom['id']}/lottery",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"title": "抽人回答", "candidates": ["张三", "李四", "王五"]},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["winner"] in ["张三", "李四", "王五"]


@pytest.mark.asyncio
async def test_create_lottery_empty_candidates(async_client, auth_token, created_classroom):
    """空候选人列表应返回 400"""
    response = await async_client.post(
        f"/api/v1/classrooms/{created_classroom['id']}/lottery",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"title": "空抽签", "candidates": []},
    )
    assert response.status_code == 400


# ============================================================
# 7. 随堂测验
# ============================================================

@pytest.mark.asyncio
async def test_create_and_submit_quiz(async_client, auth_token, created_classroom, second_auth_token):
    """老师发起测验，学生提交答案后可查看结果"""
    # 学生加入课堂
    await async_client.post(
        f"/api/v1/classrooms/{created_classroom['id']}/join",
        headers={"Authorization": f"Bearer {second_auth_token}"},
        json={"code": created_classroom["code"]},
    )

    # 老师发起测验
    create_response = await async_client.post(
        f"/api/v1/classrooms/{created_classroom['id']}/quizzes",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "title": "小测验",
            "questions": [
                {"question": "1+1=？", "options": ["1", "2", "3"], "answer": "2"},
                {"question": "2+2=？", "options": ["3", "4", "5"], "answer": "4"},
            ],
        },
    )
    assert create_response.status_code == 201
    quiz_id = create_response.json()["id"]

    # 学生提交答案
    submit_response = await async_client.post(
        f"/api/v1/classrooms/{created_classroom['id']}/quizzes/{quiz_id}/submit",
        headers={"Authorization": f"Bearer {second_auth_token}"},
        json={"answers": {"0": "2", "1": "4"}},
    )
    assert submit_response.status_code == 200
    assert "提交成功" in submit_response.json()["message"]

    # 查看结果
    result_response = await async_client.get(
        f"/api/v1/classrooms/{created_classroom['id']}/quizzes/{quiz_id}/result",
        headers={"Authorization": f"Bearer {second_auth_token}"},
    )
    assert result_response.status_code == 200
    data = result_response.json()
    assert data["id"] == quiz_id


# ============================================================
# 8. 生成课堂 PPT
# ============================================================

@pytest.mark.asyncio
async def test_generate_ppt(async_client, auth_token, created_classroom, monkeypatch):
    """老师生成课堂 PPT，结果保存为学习资源"""
    # classroom.py 调用 llm_client.build_messages() 和 llm_client.chat()
    # 需要 mock 这两个方法
    def mock_build_messages(system_prompt, user_prompt):
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    async def mock_chat(messages, stream=False):
        return {
            "choices": [
                {
                    "message": {
                        "content": '{"title": "测试PPT", "slides": [{"title": "第一页", "content": "要点"}]}'
                    }
                }
            ]
        }

    original_build_messages = getattr(classroom_module.llm_client, "build_messages", None)
    original_chat = getattr(classroom_module.llm_client, "chat", None)
    classroom_module.llm_client.build_messages = mock_build_messages
    classroom_module.llm_client.chat = mock_chat

    try:
        response = await async_client.post(
            f"/api/v1/classrooms/{created_classroom['id']}/ppt",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"topic": "一元二次方程"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "ppt"
        resource_id = data["id"]

        # 清理生成的学习资源
        db = SessionLocal()
        try:
            db.execute(text("PRAGMA foreign_keys = ON"))
            r = db.query(LearningResource).filter(LearningResource.id == resource_id).first()
            if r:
                db.delete(r)
                db.commit()
        finally:
            db.close()
    finally:
        # 恢复原始方法
        if original_build_messages is not None:
            classroom_module.llm_client.build_messages = original_build_messages
        else:
            delattr(classroom_module.llm_client, "build_messages")
        if original_chat is not None:
            classroom_module.llm_client.chat = original_chat
        else:
            delattr(classroom_module.llm_client, "chat")
