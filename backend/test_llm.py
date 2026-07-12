"""
大模型 API 连通性测试脚本
运行: python test_llm.py
"""
import asyncio
import os
import sys

# 将 backend 目录加入路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.core.config import settings
    from app.core.llm_client import llm_client
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("   请确保已安装依赖: pip install httpx pydantic pydantic-settings python-dotenv")
    sys.exit(1)


async def test_env():
    """检查环境变量配置"""
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
    """测试基础对话接口"""
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
        print(f"  用量: {response.get('usage', {})}")
        return True

    except Exception as e:
        print(f"  ❌ 失败: {e}")
        return False


async def test_stream():
    """测试流式对话接口"""
    print("\n" + "=" * 50)
    print("🧪 测试流式对话 (stream)")
    print("=" * 50)

    try:
        messages = llm_client.build_messages(
            system_prompt="你是一位专业的AI学习助手，用中文回答。",
            user_prompt="请列举3个提高学习效率的方法。",
        )

        print("  请求中... ", end="", flush=True)
        full_text = ""
        async for chunk in llm_client.chat_stream(messages):
            full_text += chunk
            print(".", end="", flush=True)

        print(f"\n  ✅ 成功!")
        print(f"  完整回复: {full_text[:150]}...")
        return True

    except Exception as e:
        print(f"\n  ❌ 失败: {e}")
        return False


async def test_web_search():
    """测试联网搜索接口"""
    print("\n" + "=" * 50)
    print("🧪 测试联网搜索 (responses + web_search)")
    print("=" * 50)

    try:
        print("  请求中...")
        response = await llm_client.generate_with_web_search(
            query="今天有什么热点新闻",
            max_keyword=3,
        )

        print(f"  ✅ 成功!")
        # 尝试提取文本输出
        output_text = ""
        if "output" in response:
            for item in response["output"]:
                if item.get("type") == "message":
                    for content in item.get("content", []):
                        if content.get("type") == "output_text":
                            output_text += content.get("text", "")

        if output_text:
            print(f"  回复: {output_text[:200]}...")
        else:
            print(f"  原始响应: {str(response)[:300]}...")
        return True

    except Exception as e:
        print(f"  ❌ 失败: {e}")
        return False


async def main():
    print("🚀 火山方舟 DeepSeek API 连通性测试")
    print(f"   模型: {settings.VOLCES_MODEL}")
    print(f"   接口: {settings.VOLCES_BASE_URL}")

    # 1. 环境检查
    env_ok = await test_env()
    if not env_ok:
        print("\n⚠️ 环境变量未配置完整，请检查 .env 文件")
        return

    # 2. 基础对话测试
    chat_ok = await test_chat()

    # 3. 流式对话测试
    stream_ok = await test_stream()

    # 4. 联网搜索测试
    web_ok = await test_web_search()

    # 汇总
    print("\n" + "=" * 50)
    print("📊 测试结果汇总")
    print("=" * 50)
    print(f"  环境配置: {'✅ 通过' if env_ok else '❌ 失败'}")
    print(f"  基础对话: {'✅ 通过' if chat_ok else '❌ 失败'}")
    print(f"  流式对话: {'✅ 通过' if stream_ok else '❌ 失败'}")
    print(f"  联网搜索: {'✅ 通过' if web_ok else '❌ 失败'}")

    if all([chat_ok, stream_ok, web_ok]):
        print("\n🎉 所有测试通过！大模型 API 连接正常。")
    else:
        print("\n⚠️ 部分测试失败，请检查 API 密钥和网络连接。")


if __name__ == "__main__":
    asyncio.run(main())
