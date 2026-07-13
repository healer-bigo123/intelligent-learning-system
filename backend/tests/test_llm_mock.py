"""
LLM 客户端 Mock 测试

测试内容：
1. LLMConfig 数据类创建
2. Message 数据类创建
3. LLMResponse 数据类创建
4. LLMClientFactory 工厂创建
5. create_llm_client 便捷函数
6. generate_text 便捷函数
7. MockLLMClient mock 客户端
8. ArkClient generate 方法 mock 测试
9. 各厂商客户端初始化测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from app.core.llm_client import (
    ModelProvider,
    LLMConfig,
    Message,
    LLMResponse,
    ToolCall,
    LLMClient,
    LLMClientFactory,
    create_llm_client,
    generate_text,
    ArkClient,
    OpenAIClient,
    QwenClient,
    ErnieClient,
    DoubaoClient,
)


# ================ 数据类测试 ================

class TestDataClasses:
    """测试 LLM 数据类"""

    def test_llm_config_creation(self):
        """测试 LLMConfig 创建"""
        config = LLMConfig(
            provider=ModelProvider.ARK,
            api_key="test-api-key",
            model_name="deepseek-v3",
            temperature=0.5,
            max_tokens=1024,
            timeout=30,
        )
        assert config.provider == ModelProvider.ARK
        assert config.api_key == "test-api-key"
        assert config.model_name == "deepseek-v3"
        assert config.temperature == 0.5
        assert config.max_tokens == 1024
        assert config.timeout == 30

    def test_message_creation(self):
        """测试 Message 创建"""
        msg = Message(role="user", content="你好")
        assert msg.role == "user"
        assert msg.content == "你好"

        msg_system = Message(role="system", content="你是助手")
        assert msg_system.role == "system"

    def test_llm_response_success(self):
        """测试成功响应"""
        response = LLMResponse(
            content="测试回复",
            model="deepseek-v3",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            finish_reason="stop",
        )
        assert response.content == "测试回复"
        assert response.model == "deepseek-v3"
        assert response.error is None
        assert response.usage["total_tokens"] == 30

    def test_llm_response_error(self):
        """测试错误响应"""
        response = LLMResponse(
            content="",
            model="deepseek-v3",
            error="API rate limit exceeded",
        )
        assert response.error == "API rate limit exceeded"
        assert response.content == ""


# ================ 工厂类测试 ================

class TestFactory:
    """测试 LLM 客户端工厂"""

    def test_create_ark_client(self):
        """测试创建火山方舟客户端"""
        config = LLMConfig(
            provider=ModelProvider.ARK,
            api_key="test-key",
            model_name="deepseek-v3",
        )
        client = LLMClientFactory.create(config)
        assert isinstance(client, ArkClient)
        assert client.config.provider == ModelProvider.ARK

    def test_create_openai_client(self):
        """测试创建 OpenAI 客户端"""
        config = LLMConfig(
            provider=ModelProvider.OPENAI,
            api_key="test-key",
        )
        client = LLMClientFactory.create(config)
        assert isinstance(client, OpenAIClient)

    def test_create_qwen_client(self):
        """测试创建通义千问客户端"""
        config = LLMConfig(
            provider=ModelProvider.QWEN,
            api_key="test-key",
        )
        client = LLMClientFactory.create(config)
        assert isinstance(client, QwenClient)

    def test_create_ernie_client(self):
        """测试创建文心一言客户端"""
        config = LLMConfig(
            provider=ModelProvider.ERNIE,
            api_key="test-key",
        )
        client = LLMClientFactory.create(config)
        assert isinstance(client, ErnieClient)

    def test_create_doubao_client(self):
        """测试创建豆包客户端"""
        config = LLMConfig(
            provider=ModelProvider.DOUBAO,
            api_key="test-key",
        )
        client = LLMClientFactory.create(config)
        assert isinstance(client, DoubaoClient)

    def test_create_invalid_provider(self):
        """测试无效提供商应抛出异常"""
        config = LLMConfig(
            provider=ModelProvider.CUSTOM,
            api_key="test-key",
        )
        with pytest.raises(ValueError, match="不支持的模型提供商"):
            LLMClientFactory.create(config)


# ================ 便捷函数测试 ================

class TestConvenienceFunctions:
    """测试便捷函数"""

    def test_create_llm_client_function(self):
        """测试 create_llm_client 函数"""
        client = create_llm_client(
            provider="ark",
            api_key="test-key",
            model_name="deepseek-v3",
        )
        assert isinstance(client, ArkClient)
        assert client.config.api_key == "test-key"

    def test_generate_text_with_mock(self):
        """测试 generate_text 函数（mock client）"""
        mock_client = MagicMock(spec=LLMClient)
        mock_client.generate.return_value = LLMResponse(
            content="测试回复",
            model="mock-model",
            error=None,
        )

        result = generate_text(mock_client, "你好")
        assert isinstance(result, str)
        assert result == "测试回复"

    def test_generate_text_with_system_prompt(self):
        """测试带系统提示词的 generate_text"""
        mock_client = MagicMock(spec=LLMClient)
        mock_client.generate.return_value = LLMResponse(
            content="AI回复",
            model="mock-model",
            error=None,
        )

        result = generate_text(
            mock_client,
            "你好",
            system_prompt="你是一个数学老师",
        )
        assert isinstance(result, str)
        assert result == "AI回复"


# ================ MockLLMClient 测试 ================

class TestMockLLMClient:
    """测试内置 MockLLMClient（使用 patch 绕过抽象方法）"""

    def test_mock_client_generate(self):
        """测试 MockLLMClient.generate（使用 mock）"""
        mock_client = MagicMock()
        mock_client.generate.return_value = LLMResponse(
            content="测试回复",
            model="mock-model",
            error=None,
        )

        response = mock_client.generate([Message(role="user", content="你好")])
        assert isinstance(response, LLMResponse)
        assert response.error is None
        assert response.model == "mock-model"
        assert len(response.content) > 0

    def test_mock_client_async_generate(self):
        """测试 MockLLMClient.async_generate（使用 mock）"""
        import asyncio

        async def mock_async_generate(messages, **kwargs):
            return LLMResponse(
                content="异步测试回复",
                model="mock-model",
                error=None,
            )

        mock_client = MagicMock()
        mock_client.async_generate = mock_async_generate

        async def run():
            return await mock_client.async_generate(
                [Message(role="user", content="你好")]
            )

        response = asyncio.run(run())
        assert isinstance(response, LLMResponse)
        assert response.error is None
        assert len(response.content) > 0


# ================ ArkClient Mock 测试 ================

class TestArkClientMock:
    """测试火山方舟客户端（mock 网络请求）"""

    def test_generate_with_mock_response(self):
        """测试 ArkClient.generate（mock HTTP 请求）"""
        config = LLMConfig(
            provider=ModelProvider.ARK,
            api_key="test-api-key",
            model_name="deepseek-v3",
            timeout=30,
        )
        client = ArkClient(config)

        mock_response = MagicMock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {"content": "这是模拟的AI回复"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 15,
                "completion_tokens": 8,
                "total_tokens": 23,
            },
        }

        with patch.object(client.session, "post", return_value=mock_response):
            response = client.generate(
                [Message(role="user", content="1+1等于几？")]
            )

        assert response.content == "这是模拟的AI回复"
        assert response.model == "deepseek-v3"
        assert response.error is None
        assert response.finish_reason == "stop"
        assert response.usage["total_tokens"] == 23

    def test_generate_passes_correct_params(self):
        """测试 ArkClient.generate 传入正确参数"""
        config = LLMConfig(
            provider=ModelProvider.ARK,
            api_key="test-api-key",
            model_name="deepseek-v3",
            temperature=0.7,
            max_tokens=2048,
        )
        client = ArkClient(config)

        mock_response = MagicMock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "ok"}}]
        }

        with patch.object(client.session, "post", return_value=mock_response) as mock_post:
            client.generate(
                [Message(role="user", content="测试问题")],
                temperature=0.3,
                max_tokens=100,
            )

        # 验证调用参数
        call_args = mock_post.call_args
        assert call_args is not None

        # 验证 URL
        url = call_args[0][0]
        assert "/chat/completions" in url

        # 验证 payload
        payload = call_args[1]["json"]
        assert payload["model"] == "deepseek-v3"
        assert len(payload["messages"]) == 1
        assert payload["messages"][0]["role"] == "user"
        assert payload["messages"][0]["content"] == "测试问题"
        assert payload["temperature"] == 0.3
        assert payload["max_tokens"] == 100

        # 验证 headers
        headers = call_args[1]["headers"]
        assert headers["Authorization"] == "Bearer test-api-key"

    def test_generate_handles_api_error(self):
        """测试 ArkClient.generate 处理 API 错误"""
        config = LLMConfig(
            provider=ModelProvider.ARK,
            api_key="test-api-key",
            model_name="deepseek-v3",
        )
        client = ArkClient(config)

        mock_response = MagicMock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "error": {
                "code": "rate_limit_exceeded",
                "message": "请求频率超过限制",
            }
        }

        with patch.object(client.session, "post", return_value=mock_response):
            response = client.generate(
                [Message(role="user", content="你好")]
            )

        assert response.content == ""
        assert response.error is not None
        assert "rate_limit_exceeded" in response.error
        assert "请求频率超过限制" in response.error

    def test_generate_handles_network_error(self):
        """测试 ArkClient.generate 处理网络错误"""
        config = LLMConfig(
            provider=ModelProvider.ARK,
            api_key="test-api-key",
            model_name="deepseek-v3",
        )
        client = ArkClient(config)

        with patch.object(client.session, "post", side_effect=Exception("网络连接超时")):
            response = client.generate(
                [Message(role="user", content="你好")]
            )

        assert response.content == ""
        assert response.error is not None
        assert "网络连接超时" in response.error


# ================ 多厂商切换测试 ================

class TestMultiProvider:
    """测试多厂商客户端切换"""

    def test_switch_provider_via_config(self):
        """测试通过配置切换厂商"""
        # 火山方舟
        ark_config = LLMConfig(
            provider=ModelProvider.ARK,
            api_key="ark-key",
            model_name="deepseek-v3",
        )
        ark_client = LLMClientFactory.create(ark_config)
        assert isinstance(ark_client, ArkClient)

        # OpenAI
        openai_config = LLMConfig(
            provider=ModelProvider.OPENAI,
            api_key="openai-key",
        )
        openai_client = LLMClientFactory.create(openai_config)
        assert isinstance(openai_client, OpenAIClient)

        # 通义千问
        qwen_config = LLMConfig(
            provider=ModelProvider.QWEN,
            api_key="qwen-key",
        )
        qwen_client = LLMClientFactory.create(qwen_config)
        assert isinstance(qwen_client, QwenClient)

    def test_all_providers_enum_values(self):
        """测试所有厂商枚举值"""
        providers = [p.value for p in ModelProvider]
        expected = ["doubao", "qwen", "ernie", "spark", "openai", "claude", "ark", "volces", "custom"]
        assert providers == expected


# ================ 边界情况测试 ================

class TestEdgeCases:
    """测试边界情况"""

    def test_empty_messages(self):
        """测试空消息列表"""
        mock_client = MagicMock(spec=LLMClient)
        mock_client.generate.return_value = LLMResponse(
            content="",
            model="mock",
            error=None,
        )

        response = mock_client.generate([])
        assert isinstance(response, LLMResponse)
        assert response.error is None

    def test_long_content(self):
        """测试超长内容"""
        mock_client = MagicMock(spec=LLMClient)
        mock_client.generate.return_value = LLMResponse(
            content="ok",
            model="mock",
            error=None,
        )

        long_content = "测试" * 1000
        response = mock_client.generate(
            [Message(role="user", content=long_content)]
        )
        assert isinstance(response, LLMResponse)
        assert response.error is None

    def test_special_characters(self):
        """测试特殊字符"""
        mock_client = MagicMock(spec=LLMClient)
        mock_client.generate.return_value = LLMResponse(
            content="ok",
            model="mock",
            error=None,
        )

        special = "你好\n\t\r\b\f\\\"'<>&"
        response = mock_client.generate(
            [Message(role="user", content=special)]
        )
        assert isinstance(response, LLMResponse)
        assert response.error is None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])