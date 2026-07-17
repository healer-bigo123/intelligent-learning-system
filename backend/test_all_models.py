import sys, requests, json
sys.path.insert(0, '.')

BASE = "http://localhost:8000/api/v1"

def test_model(model_id, model_name):
    print(f"\n{'='*50}")
    print(f"测试模型: {model_name} ({model_id})")
    print(f"{'='*50}")
    
    # 切换模型
    r = requests.post(f"{BASE}/agents/model/select", json={"model_id": model_id})
    print(f"切换结果: {r.status_code} - {r.json()}")
    if r.status_code != 200:
        print(f"  切换失败，跳过")
        return
    
    # 发送查询
    r = requests.post(f"{BASE}/agents/query", json={"user_input": "你好，请简单介绍一下你自己", "user_id": "test"})
    data = r.json()
    answer = data.get("result", {}).get("answer", "")
    error = data.get("result", {}).get("error", "")
    
    if answer and len(answer) > 10:
        print(f"  回答内容: {answer[:120]}...")
        print(f"  状态: OK")
    elif error:
        print(f"  错误: {error}")
        print(f"  状态: FAIL")
    else:
        print(f"  回答为空")
        print(f"  完整result: {json.dumps(data.get('result', {}), ensure_ascii=False)[:200]}")
        print(f"  状态: FAIL")

# 测试三个模型
test_model("spark-3.5", "讯飞星火 3.5")
test_model("doubao-pro", "豆包 Pro")
test_model("deepseek-v3-2-251201", "DeepSeek V3")

print(f"\n{'='*50}")
print("测试完成")
