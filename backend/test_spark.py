import sys
sys.path.insert(0, '.')

from app.core.llm_client import SparkClient, LLMConfig, ModelProvider, Message
from app.core.config import settings

print("Testing Spark client...")
print(f"APP_ID: {settings.XINGHUO_APP_ID}")
print(f"API_SECRET: {settings.XINGHUO_API_SECRET[:10]}...")
print(f"BASE_URL: {settings.XINGHUO_BASE_URL}")

config = LLMConfig(
    provider=ModelProvider.SPARK,
    api_key=settings.XINGHUO_APP_ID or settings.XINGHUO_API_KEY,
    secret_key=settings.XINGHUO_API_SECRET,
    model_name="spark-3.5",
    base_url=settings.XINGHUO_BASE_URL,
    temperature=0.7,
    max_tokens=2048
)

client = SparkClient(config)
print(f"Client base_url: {client.base_url}")
print(f"Client domain: {client.domain}")

response = client.generate([
    Message(role="system", content="你是一个智能学习助手"),
    Message(role="user", content="你好")
])

print(f"\nResponse content: '{response.content}'")
print(f"Response error: {response.error}")
print(f"Response model: {response.model}")
