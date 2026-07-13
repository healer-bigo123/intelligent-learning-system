"""
Mock 数据测试脚本 - 学习路径 + 排行榜/成就接口
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

# 先注册一个测试用户获取 token
def get_token():
    # 使用新的测试用户名避免冲突
    test_username = "mocktester"
    test_password = "123456"

    # 先尝试注册新用户
    register_data = {
        "username": test_username,
        "password": test_password,
        "email": "mock@example.com",
        "nickname": "Mock测试用户"
    }
    try:
        r = requests.post(f"{BASE_URL}/auth/register", json=register_data, timeout=5)
        if r.status_code == 201:
            print(f"[OK] 注册用户成功: {test_username}")
            return r.json()["access_token"]
        elif r.status_code == 400 and "已被注册" in r.text:
            print(f"[INFO] 用户已存在，尝试登录: {test_username}")
    except Exception as e:
        print(f"[WARN] 注册失败: {e}")

    # 如果注册失败（用户已存在），尝试登录
    login_data = {
        "username": test_username,
        "password": test_password
    }
    try:
        r = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=5)
        if r.status_code == 200:
            print(f"[OK] 登录成功: {test_username}")
            return r.json()["access_token"]
        else:
            print(f"[WARN] 登录失败: {r.status_code} {r.text}")
    except Exception as e:
        print(f"[WARN] 登录请求失败: {e}")

    return None


def test_learning_paths(token):
    """测试学习路径接口"""
    print("\n========== 学习路径接口测试 ==========")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. 创建学习路径
    print("\n[1] 创建学习路径...")
    path_data = {
        "title": "高一数学期末冲刺计划",
        "description": "为期一个月的数学复习计划，覆盖函数、三角函数、数列等重点章节",
        "steps": [
            {"title": "函数基础复习", "description": "复习一次函数、二次函数、反比例函数", "duration": 120, "status": "pending"},
            {"title": "三角函数专题", "description": "掌握正弦、余弦、正切函数及其图像", "duration": 180, "status": "pending"},
            {"title": "数列与数学归纳法", "description": "等差数列、等比数列、递推数列", "duration": 150, "status": "pending"},
            {"title": "立体几何", "description": "空间向量、线面关系、空间角", "duration": 200, "status": "pending"},
            {"title": "综合模拟测试", "description": "完成3套模拟试卷", "duration": 180, "status": "pending"}
        ]
    }
    r = requests.post(f"{BASE_URL}/learning-paths", json=path_data, headers=headers)
    print(f"  状态码: {r.status_code}")
    if r.status_code == 201:
        path_id = r.json()["id"]
        print(f"  创建成功，ID: {path_id}")
    else:
        print(f"  响应: {r.text}")
        return

    # 2. 获取学习路径列表
    print("\n[2] 获取学习路径列表...")
    r = requests.get(f"{BASE_URL}/learning-paths", headers=headers)
    print(f"  状态码: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"  总数: {data.get('total', 0)}")
        for item in data.get("items", []):
            print(f"    - {item['title']} ({item['status']})")

    # 3. 获取学习路径详情
    print(f"\n[3] 获取学习路径详情 (ID: {path_id})...")
    r = requests.get(f"{BASE_URL}/learning-paths/{path_id}", headers=headers)
    print(f"  状态码: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"  标题: {data['title']}")
        print(f"  步骤数: {len(data.get('steps', []))}")

    # 4. 完成第一个步骤
    print(f"\n[4] 完成第一个步骤...")
    r = requests.post(f"{BASE_URL}/learning-paths/{path_id}/steps/0/complete", headers=headers)
    print(f"  状态码: {r.status_code}")
    if r.status_code == 200:
        print(f"  响应: {r.json()}")

    # 5. 获取进度统计
    print(f"\n[5] 获取学习进度统计...")
    r = requests.get(f"{BASE_URL}/learning-paths/stats/progress", headers=headers)
    print(f"  状态码: {r.status_code}")
    if r.status_code == 200:
        print(f"  统计: {json.dumps(r.json(), ensure_ascii=False, indent=2)}")

    # 6. 再创建一个已完成的路径
    print(f"\n[6] 创建第二个学习路径...")
    path_data2 = {
        "title": "英语词汇积累计划",
        "description": "每天背诵50个单词，一个月掌握1500个高频词汇",
        "steps": [
            {"title": "第一周：基础词汇", "description": "掌握常用动词和形容词", "duration": 300, "status": "completed"},
            {"title": "第二周：进阶词汇", "description": "学术词汇和短语搭配", "duration": 300, "status": "completed"},
            {"title": "第三周：高频考点", "description": "高考高频词汇", "duration": 300, "status": "completed"}
        ]
    }
    r = requests.post(f"{BASE_URL}/learning-paths", json=path_data2, headers=headers)
    if r.status_code == 201:
        path_id2 = r.json()["id"]
        # 标记为已完成
        requests.put(f"{BASE_URL}/learning-paths/{path_id2}", json={"status": "completed"}, headers=headers)
        print(f"  创建成功并标记为已完成")

    print("\n[OK] 学习路径接口测试完成")


def test_achievements(token):
    """测试成就系统接口"""
    print("\n========== 成就系统接口测试 ==========")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. 获取成就列表（首次会自动初始化默认成就）
    print("\n[1] 获取所有成就列表...")
    r = requests.get(f"{BASE_URL}/achievements", headers=headers)
    print(f"  状态码: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        # 可能是列表或对象格式
        if isinstance(data, list):
            print(f"  成就总数: {len(data)}")
            for item in data[:5]:
                print(f"    - {item['name']}: {item['description']} (条件: {item['condition_type']} >= {item['condition_value']})")
        else:
            print(f"  成就总数: {data.get('total', 0)}")
            for item in data.get("items", [])[:5]:
                print(f"    - {item['name']}: {item['description']} (条件: {item['condition_type']} >= {item['condition_value']})")

    # 2. 获取我的成就
    print(f"\n[2] 获取我的已解锁成就...")
    r = requests.get(f"{BASE_URL}/achievements/my", headers=headers)
    print(f"  状态码: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        if isinstance(data, list):
            print(f"  已解锁: {len(data)} 个")
        else:
            print(f"  已解锁: {len(data.get('items', []))} 个")

    # 3. 检查成就解锁
    print(f"\n[3] 检查并解锁成就...")
    r = requests.post(f"{BASE_URL}/achievements/check", headers=headers)
    print(f"  状态码: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        unlocked = data.get("unlocked", [])
        print(f"  本次解锁: {len(unlocked)} 个")
        for a in unlocked:
            print(f"    + 解锁成就: {a['name']}")

    # 4. 获取排行榜
    print(f"\n[4] 获取排行榜...")
    r = requests.get(f"{BASE_URL}/achievements/leaderboard", headers=headers)
    print(f"  状态码: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        if isinstance(data, list):
            items = data
        else:
            items = data.get('items', [])
        print(f"  排行榜人数: {len(items)}")
        for i, item in enumerate(items[:5]):
            print(f"    {i+1}. {item.get('username', '未知用户')} - {item.get('achievement_count', 0)} 个成就")

    print("\n[OK] 成就系统接口测试完成")


def test_timeline(token):
    """测试学习记录时间线接口"""
    print("\n========== 学习记录时间线接口测试 ==========")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. 记录几个学习活动
    print("\n[1] 记录学习活动...")
    activities = [
        {"activity_type": "exercise", "title": "完成数学练习10题", "duration": 600, "score": 80},
        {"activity_type": "mistake_review", "title": "复习错题：三角函数", "duration": 300},
        {"activity_type": "material_read", "title": "阅读：导数知识点", "duration": 900},
        {"activity_type": "session_complete", "title": "完成模拟测试", "duration": 3600, "score": 75},
    ]
    for act in activities:
        r = requests.post(f"{BASE_URL}/timeline/record", json=act, headers=headers)
        if r.status_code == 201:
            print(f"  + {act['title']} ({act['duration']}秒)")

    # 2. 获取学习总览
    print(f"\n[2] 获取学习总览...")
    r = requests.get(f"{BASE_URL}/timeline/stats/overview", headers=headers)
    print(f"  状态码: {r.status_code}")
    if r.status_code == 200:
        print(f"  统计: {json.dumps(r.json(), ensure_ascii=False, indent=2)}")

    # 3. 获取连续学习天数
    print(f"\n[3] 获取连续学习天数...")
    r = requests.get(f"{BASE_URL}/timeline/streak", headers=headers)
    print(f"  状态码: {r.status_code}")
    if r.status_code == 200:
        print(f"  结果: {json.dumps(r.json(), ensure_ascii=False, indent=2)}")

    # 4. 获取时间线列表
    print(f"\n[4] 获取学习记录时间线...")
    r = requests.get(f"{BASE_URL}/timeline", headers=headers)
    print(f"  状态码: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"  记录数: {data.get('total', 0)}")
        for item in data.get("items", [])[:3]:
            print(f"    - [{item['activity_type']}] {item['title']} ({item['duration']}秒)")

    print("\n[OK] 学习记录时间线接口测试完成")


def test_favorites_and_notifications(token):
    """测试收藏和通知接口"""
    print("\n========== 收藏和通知接口测试 ==========")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. 添加收藏
    print("\n[1] 添加收藏...")
    fav_data = {
        "target_type": "study_material",
        "target_id": "mock-material-001"
    }
    r = requests.post(f"{BASE_URL}/favorites", json=fav_data, headers=headers)
    print(f"  状态码: {r.status_code}")
    if r.status_code == 201:
        print(f"  收藏成功")

    # 2. 获取收藏列表
    print(f"\n[2] 获取收藏列表...")
    r = requests.get(f"{BASE_URL}/favorites", headers=headers)
    print(f"  状态码: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"  收藏数: {data.get('total', 0)}")

    # 3. 获取未读通知数
    print(f"\n[3] 获取未读通知数...")
    r = requests.get(f"{BASE_URL}/notifications/unread-count", headers=headers)
    print(f"  状态码: {r.status_code}")
    if r.status_code == 200:
        print(f"  结果: {json.dumps(r.json(), ensure_ascii=False)}")

    print("\n[OK] 收藏和通知接口测试完成")


if __name__ == "__main__":
    print("=" * 50)
    print("SmartLearning Mock 数据测试")
    print("=" * 50)

    token = get_token()
    if not token:
        print("[ERROR] 无法获取 Token，请确保后端服务已启动")
        exit(1)

    print(f"\n[OK] 获取 Token 成功")

    try:
        test_learning_paths(token)
    except Exception as e:
        print(f"[ERROR] 学习路径测试失败: {e}")

    try:
        test_achievements(token)
    except Exception as e:
        print(f"[ERROR] 成就系统测试失败: {e}")

    try:
        test_timeline(token)
    except Exception as e:
        print(f"[ERROR] 学习记录测试失败: {e}")

    try:
        test_favorites_and_notifications(token)
    except Exception as e:
        print(f"[ERROR] 收藏通知测试失败: {e}")

    print("\n" + "=" * 50)
    print("所有测试执行完毕")
    print("=" * 50)
