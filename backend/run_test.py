"""
直接测试大模型 API
运行: python run_test.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.core.config import settings
    from app.core.llm_client import llm_client
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

async def test_env():
    print("=" * 50)
    print("🔍 环境变量检查")
    print("=" * 50)
    
    checks = {
        "VOLCES_API_KEY": settings.VOLCES_API_KEY,
        "VOLCES_BASE_URL": settings.VOLCES_BASE_URL,
        "VOLCES_MODEL": settings.VOLCES_MODEL,
    }
    
    all_ok = True
    for key, value in checks.items():
        status = "✅ 已配置" if value and value != "your_api_key_here" else "❌ 未配置"
        if not value or value == "your_api_key_here":
            all_ok = False
        print(f"  {key}: {status}")
        if value and "key" not in key.lower():
            print(f"    值: {value}")
        elif value and "key" in key.lower():
            print(f"    值: {value[:20]}...")
    
    return all_ok

async def test_chat():
    print("\n" + "=" * 50)
    print("🧪 测试基础对话 (chat/completions)")
    print("=" * 50)
    
    try:
        messages = llm_client.build_messages(
            system_prompt="你是一位专业的AI学习助手，用中文回答。",
            user_prompt="请用一句话介绍你自己。",
        )
        
        print("  请求中...")
        response = await llm_client.chat(messages, stream=False)
        
        content = response["choices"][0]["message"]["content"]
        print(f"  ✅ 成功!")
        print(f"  回复: {content[:100]}...")
        return True
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        return False

async def main():
    print("🚀 火山方舟 DeepSeek API 连通性测试")
    print(f"   模型: {settings.VOLCES_MODEL}")
    print(f"   接口: {settings.VOLCES_BASE_URL}")
    
    env_ok = await test_env()
    if not env_ok:
        print("\n⚠️ 环境变量未配置完整，请检查 .env 文件")
        return
    
    chat_ok = await test_chat()
    
    print("\n" + "=" * 50)
    print("📊 测试结果汇总")
    print("=" * 50)
    print(f"  环境配置: {'✅ 通过' if env_ok else '❌ 失败'}")
    print(f"  基础对话: {'✅ 通过' if chat_ok else '❌ 失败'}")
    
    if chat_ok:
        print("\n🎉 大模型 API 连接正常！")
        print("\n现在可以启动后端服务:")
        print("  python main.py")

if __name__ == "__main__":
    asyncio.run(main())
    input("\n按回车键退出...")
