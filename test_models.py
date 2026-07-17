"""测试三个模型的智能助手功能"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def register_and_login():
    """注册并登录测试用户"""
    # 注册
    register_data = {
        "username": "test_user_001",
        "password": "123456",
        "role": "student"
    }
    r = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print(f"注册状态: {r.status_code}")
    
    # 登录
    login_data = {
        "username": "test_user_001",
        "password": "123456"
    }
    r = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"登录状态: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        token = data.get("access_token")
        # 尝试从响应中获取 user_id，如果没有则通过 /me 接口获取
        user_id = data.get("user_id")
        if not user_id:
            me_r = requests.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {token}"})
            if me_r.status_code == 200:
                user_id = me_r.json().get("id")
        print(f"用户ID: {user_id}")
        return token, user_id
    else:
        print(f"登录失败: {r.text}")
        return None, None

def test_model(model_id, model_name, token, user_id):
    """测试指定模型的智能助手功能"""
    print(f"\n{'='*60}")
    print(f"测试模型: {model_name} ({model_id})")
    print(f"{'='*60}")
    
    # 切换模型
    headers = {"Authorization": f"Bearer {token}"}
    switch_data = {"model_id": model_id}
    r = requests.post(f"{BASE_URL}/agents/model/select", json=switch_data, headers=headers)
    print(f"切换模型状态: {r.status_code}")
    if r.status_code != 200:
        print(f"切换失败: {r.text}")
        return False
    else:
        print(f"切换成功: {r.json()}")
    
    # 发送测试问题
    query_data = {
        "user_id": user_id,
        "user_input": "请帮我解释一下什么是勾股定理？",
        "session_id": None
    }
    
    print(f"发送问题: {query_data['user_input']}")
    r = requests.post(f"{BASE_URL}/agents/query", json=query_data, headers=headers)
    print(f"查询状态: {r.status_code}")
    
    if r.status_code == 200:
        result = r.json()
        print(f"会话ID: {result.get('session_id')}")
        print(f"意图: {result.get('intent')}")
        print(f"任务数: {result.get('tasks_executed')}")
        
        # 提取回答内容
        if 'result' in result and 'content' in result['result']:
            content = result['result']['content']
            if isinstance(content, dict) and 'answer' in content:
                answer = content['answer']
                print(f"\n回答内容 (前500字):")
                print(answer[:500] if len(answer) > 500 else answer)
                return True
            else:
                print(f"回答格式异常: {json.dumps(content, ensure_ascii=False)[:200]}")
        else:
            print(f"响应格式: {json.dumps(result, ensure_ascii=False)[:300]}")
        return False
    else:
        print(f"查询失败: {r.text}")
        return False

def main():
    print("开始测试三个模型的智能助手功能...")
    
    # 登录
    token, user_id = register_and_login()
    if not token:
        print("登录失败，退出测试")
        return
    
    # 测试三个模型: (model_id, model_name)
    models = [
        ("spark-3.5", "讯飞星火"),
        ("doubao-pro", "豆包"),
        ("deepseek-v3-2-251201", "DeepSeek")
    ]
    results = {}
    
    for model_id, model_name in models:
        success = test_model(model_id, model_name, token, user_id)
        results[model_name] = success
    
    # 汇总结果
    print(f"\n{'='*60}")
    print("测试结果汇总")
    print(f"{'='*60}")
    for model_name, success in results.items():
        status = "成功" if success else "失败"
        print(f"{model_name}: {status}")

if __name__ == "__main__":
    main()
