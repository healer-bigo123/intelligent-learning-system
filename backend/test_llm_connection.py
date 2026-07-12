"""测试LLM连接"""
import sys
sys.path.insert(0, 'app')
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from core.llm_client import ArkClient, LLMConfig, ModelProvider, Message

config = LLMConfig(
    provider=ModelProvider.VOLCES,
    api_key="ark-8ecadcf3-5a8e-4b9d-80a0-3ebdda1d2c59-888c0",
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    model_name="deepseek-v3-2-251201",
    temperature=0.7,
    max_tokens=2048
)

client = ArkClient(config)

print("Testing LLM connection...")
print(f"Model: {config.model_name}")
print(f"API Key: {config.api_key[:10]}...")

try:
    messages = [Message(role="user", content="Hello, who are you?")]
    response = client.generate(messages)
    
    if response.error:
        print(f"FAILED: {response.error}")
    else:
        print("SUCCESS!")
        print(f"Model: {response.model}")
        print(f"Response: {response.content[:200]}")
        
except Exception as e:
    print(f"ERROR: {e}")
