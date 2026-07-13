"""
测试配置文件 - pytest fixtures
提供共享的测试客户端、认证token、测试数据
"""
import sys
import os

# 确保 backend 目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.fixture
async def async_client():
    """创建异步测试客户端（不依赖真实服务端口）"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def test_user():
    """测试用户信息（来自 init_data.py）"""
    return {
        "username": "student1",
        "password": "123456",
    }


@pytest.fixture
async def auth_token(async_client, test_user):
    """获取认证 token"""
    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "username": test_user["username"],
            "password": test_user["password"],
        },
    )
    assert response.status_code == 200, f"登录失败: {response.json()}"
    data = response.json()
    return data["access_token"]


@pytest.fixture
def test_mistake_data():
    """创建错题的标准请求体"""
    return {
        "subject": "数学",
        "question": "测试错题：求解方程 x^2 + 2x + 1 = 0",
        "correct_answer": "x = -1",
        "user_answer": "x = 1",
        "analysis": "完全平方公式，(x+1)^2 = 0",
        "tags": ["代数", "一元二次方程"],
        "difficulty": 3,
    }


@pytest.fixture
def test_exercise_data():
    """创建练习题的标准请求体"""
    return {
        "subject": "数学",
        "type": "choice",
        "question": "方程 x^2 + 2x + 1 = 0 的解是？",
        "options": ["x=1", "x=-1", "x=0", "无解"],
        "correct_answer": "x=-1",
        "difficulty": 2,
        "knowledge_point": "一元二次方程",
    }