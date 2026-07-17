"""
测试 AI 对话功能
运行方式: py test_ai_chat.py
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_models():
    """测试模型列表"""
    print("=" * 60)
    print("测试模型列表 API")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/agents/models")
    data = response.json()
    
    print(f"状态码: {response.status_code}")
    print(f"当前模型: {data.get('current_model')}")
    print(f"可用模型数量: {len(data.get('models', []))}")
    
    for model in data.get('models', []):
        status = "✓" if model.get('available') else "✗"
        print(f"  {status} {model['name']} ({model['id']})")
    
    return response.status_code == 200

def test_chat():
    """测试 AI 对话"""
    print("\n" + "=" * 60)
    print("测试 AI 对话 API")
    print("=" * 60)
    
    payload = {
        "user_input": "你好，请简单介绍一下你自己",
        "user_id": "test_user_001"
    }
    
    print(f"发送消息: {payload['user_input']}")
    
    response = requests.post(
        f"{BASE_URL}/agents/query",
        json=payload,
        timeout=60
    )
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"会话ID: {data.get('session_id')}")
        print(f"识别意图: {data.get('intent')}")
        print(f"执行任务数: {data.get('tasks_executed')}")
        print(f"\nAI 回复:\n{data.get('result', {}).get('answer', '无回复')}")
    else:
        print(f"错误: {response.text}")
    
    return response.status_code == 200

def test_health():
    """测试健康检查"""
    print("\n" + "=" * 60)
    print("测试健康检查 API")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/agents/health")
    data = response.json()
    
    print(f"状态码: {response.status_code}")
    print(f"系统状态: {data.get('status')}")
    print(f"智能体数量: {data.get('agents_count')}")
    print(f"会话数量: {data.get('sessions_count')}")
    
    return response.status_code == 200

if __name__ == "__main__":
    print("智能助手 AI 对话功能测试")
    print("=" * 60)
    
    # 检查后端是否运行
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"后端服务: 运行中 (状态码: {response.status_code})")
    except:
        print("后端服务: 未运行")
        print("\n请先启动后端服务:")
        print("  cd c:\\Users\\heale\\Desktop\\智能学习系统-new\\backend")
        print("  py -m uvicorn main:app --host 0.0.0.0 --port 8000")
        exit(1)
    
    # 运行测试
    results = []
    results.append(("健康检查", test_health()))
    results.append(("模型列表", test_models()))
    results.append(("AI对话", test_chat()))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"  {name}: {status}")
    
    all_passed = all(r[1] for r in results)
    print("\n" + ("所有测试通过!" if all_passed else "部分测试失败!"))