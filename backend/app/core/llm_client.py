"""
大语言模型统一调用接口

支持的模型提供商：
- 豆包 Doubao
- Qwen 通义千问
- ERNIE 文心一言
- Spark 讯飞星火
- OpenAI GPT
- Claude
- 自定义模型
"""
import os
import json
import time
import hashlib
from typing import Dict, List, Any, Optional, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

import requests
import jwt

# ================ 配置类 ================

class ModelProvider(str, Enum):
    """模型提供商枚举"""
    DOUBAO = "doubao"
    QWEN = "qwen"
    ERNIE = "ernie"
    SPARK = "spark"
    OPENAI = "openai"
    CLAUDE = "claude"
    ARK = "ark"          # 火山方舟
    VOLCES = "volces"    # 火山方舟(volces)
    CUSTOM = "custom"

@dataclass
class LLMConfig:
    """LLM配置"""
    provider: ModelProvider
    api_key: str
    secret_key: Optional[str] = None
    model_name: str = ""
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout: int = 30

@dataclass
class Message:
    """对话消息"""
    role: str  # user, assistant, system
    content: str

@dataclass
class LLMResponse:
    """LLM响应"""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None
    error: Optional[str] = None

@dataclass
class ToolCall:
    """工具调用"""
    tool_name: str
    parameters: Dict[str, Any]

# ================ 基类 ================

class LLMClient(ABC):
    """LLM客户端基类"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.session = requests.Session()
        self.session.timeout = config.timeout
    
    @abstractmethod
    def generate(self, messages: List[Message], **kwargs) -> LLMResponse:
        """生成响应"""
        pass
    
    @abstractmethod
    def generate_with_tools(self, messages: List[Message], tools: List[Dict[str, Any]], **kwargs) -> Union[LLMResponse, ToolCall]:
        """带工具调用的生成"""
        pass
    
    def _build_system_prompt(self, instructions: str = "") -> str:
        """构建系统提示词"""
        if instructions:
            return instructions
        return """
你是一个智能学习助手，擅长回答学科问题、制定学习计划、批改作业等。
请用友好、专业的语言回答用户问题，必要时使用提供的工具获取信息。
        """.strip()

# ================ 豆包客户端 ================

class DoubaoClient(LLMClient):
    """豆包API客户端"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat"
        self.model_name = config.model_name or "completions_pro"
    
    def generate(self, messages: List[Message], **kwargs) -> LLMResponse:
        """调用豆包API"""
        try:
            url = f"{self.base_url}/{self.model_name}?access_token={self._get_access_token()}"
            
            payload = {
                "messages": [{"role": m.role, "content": m.content} for m in messages],
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens)
            }
            
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            if data.get("error_code"):
                return LLMResponse(
                    content="",
                    model=self.model_name,
                    error=f"Error {data['error_code']}: {data.get('error_msg', 'Unknown error')}"
                )
            
            return LLMResponse(
                content=data["result"],
                model=self.model_name,
                usage=data.get("usage")
            )
        
        except Exception as e:
            return LLMResponse(
                content="",
                model=self.model_name,
                error=str(e)
            )
    
    def generate_with_tools(self, messages: List[Message], tools: List[Dict[str, Any]], **kwargs) -> Union[LLMResponse, ToolCall]:
        """带工具调用"""
        try:
            url = f"{self.base_url}/{self.model_name}?access_token={self._get_access_token()}"
            
            tool_descriptions = []
            for tool in tools:
                tool_descriptions.append({
                    "tool_name": tool["name"],
                    "parameter": tool.get("parameters", {}),
                    "description": tool.get("description", "")
                })
            
            payload = {
                "messages": [{"role": m.role, "content": m.content} for m in messages],
                "tools": tool_descriptions,
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens)
            }
            
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            if data.get("error_code"):
                return LLMResponse(
                    content="",
                    model=self.model_name,
                    error=f"Error {data['error_code']}: {data.get('error_msg', 'Unknown error')}"
                )
            
            # 检查是否有工具调用
            if data.get("is_truncated") and data.get("tool_list"):
                tool_call = data["tool_list"][0]
                return ToolCall(
                    tool_name=tool_call["tool_name"],
                    parameters=tool_call.get("parameter", {})
                )
            
            return LLMResponse(
                content=data["result"],
                model=self.model_name,
                usage=data.get("usage")
            )
        
        except Exception as e:
            return LLMResponse(
                content="",
                model=self.model_name,
                error=str(e)
            )
    
    def _get_access_token(self) -> str:
        """获取访问令牌"""
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.config.api_key,
            "client_secret": self.config.secret_key
        }
        
        response = self.session.post(url, params=params)
        response.raise_for_status()
        return response.json()["access_token"]

# ================ Qwen 客户端 ================

class QwenClient(LLMClient):
    """通义千问API客户端"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://dashscope.aliyuncs.com/api/text/generation"
        self.model_name = config.model_name or "qwen-turbo"
    
    def generate(self, messages: List[Message], **kwargs) -> LLMResponse:
        """调用Qwen API"""
        try:
            url = f"{self.base_url}/v1"
            
            payload = {
                "model": self.model_name,
                "input": {
                    "messages": [{"role": m.role, "content": m.content} for m in messages]
                },
                "parameters": {
                    "temperature": kwargs.get("temperature", self.config.temperature),
                    "max_tokens": kwargs.get("max_tokens", self.config.max_tokens)
                }
            }
            
            headers = {"Authorization": f"Bearer {self.config.api_key}"}
            response = self.session.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "success":
                return LLMResponse(
                    content="",
                    model=self.model_name,
                    error=data.get("message", "Unknown error")
                )
            
            return LLMResponse(
                content=data["output"]["text"],
                model=self.model_name,
                usage=data.get("usage")
            )
        
        except Exception as e:
            return LLMResponse(
                content="",
                model=self.model_name,
                error=str(e)
            )
    
    def generate_with_tools(self, messages: List[Message], tools: List[Dict[str, Any]], **kwargs) -> Union[LLMResponse, ToolCall]:
        """带工具调用"""
        # Qwen的工具调用需要特定格式
        try:
            url = f"{self.base_url}/v1"
            
            tool_list = []
            for tool in tools:
                tool_list.append({
                    "tool_name": tool["name"],
                    "parameters": tool.get("parameters", {}),
                    "description": tool.get("description", "")
                })
            
            payload = {
                "model": self.model_name,
                "input": {
                    "messages": [{"role": m.role, "content": m.content} for m in messages],
                    "tool_list": tool_list
                },
                "parameters": {
                    "temperature": kwargs.get("temperature", self.config.temperature),
                    "max_tokens": kwargs.get("max_tokens", self.config.max_tokens)
                }
            }
            
            headers = {"Authorization": f"Bearer {self.config.api_key}"}
            response = self.session.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "success":
                return LLMResponse(
                    content="",
                    model=self.model_name,
                    error=data.get("message", "Unknown error")
                )
            
            output = data.get("output", {})
            if output.get("tool_calls"):
                tool_call = output["tool_calls"][0]
                return ToolCall(
                    tool_name=tool_call["tool_name"],
                    parameters=tool_call.get("parameters", {})
                )
            
            return LLMResponse(
                content=output.get("text", ""),
                model=self.model_name,
                usage=data.get("usage")
            )
        
        except Exception as e:
            return LLMResponse(
                content="",
                model=self.model_name,
                error=str(e)
            )

# ================ ERNIE 客户端 ================

class ErnieClient(LLMClient):
    """文心一言API客户端"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat"
        self.model_name = config.model_name or "ernie-4.0"
    
    def generate(self, messages: List[Message], **kwargs) -> LLMResponse:
        try:
            url = f"{self.base_url}/{self.model_name}?access_token={self._get_access_token()}"
            
            payload = {
                "messages": [{"role": m.role, "content": m.content} for m in messages],
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens)
            }
            
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            if data.get("error_code"):
                return LLMResponse(
                    content="",
                    model=self.model_name,
                    error=f"Error {data['error_code']}: {data.get('error_msg', 'Unknown error')}"
                )
            
            return LLMResponse(
                content=data["result"],
                model=self.model_name,
                usage=data.get("usage")
            )
        
        except Exception as e:
            return LLMResponse(
                content="",
                model=self.model_name,
                error=str(e)
            )
    
    def generate_with_tools(self, messages: List[Message], tools: List[Dict[str, Any]], **kwargs) -> Union[LLMResponse, ToolCall]:
        return self.generate(messages, **kwargs)
    
    def _get_access_token(self) -> str:
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.config.api_key,
            "client_secret": self.config.secret_key
        }
        
        response = self.session.post(url, params=params)
        response.raise_for_status()
        return response.json()["access_token"]

# ================ 火山方舟客户端 ================

class ArkClient(LLMClient):
    """火山方舟 API 客户端 (Volces)"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://ark.cn-beijing.volces.com/api/v3"
        self.model_name = config.model_name or "deepseek-v3-2-251201"
    
    def generate(self, messages: List[Message], **kwargs) -> LLMResponse:
        """调用火山方舟API"""
        try:
            url = f"{self.base_url}/chat/completions"
            
            payload = {
                "model": self.model_name,
                "messages": [{"role": m.role, "content": m.content} for m in messages],
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens)
            }
            
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            response = self.session.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get("error"):
                return LLMResponse(
                    content="",
                    model=self.model_name,
                    error=f"{data['error'].get('code', '')}: {data['error'].get('message', 'Unknown error')}"
                )
            
            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                model=self.model_name,
                usage=data.get("usage"),
                finish_reason=data["choices"][0].get("finish_reason")
            )
        
        except Exception as e:
            return LLMResponse(
                content="",
                model=self.model_name,
                error=str(e)
            )
    
    def generate_with_tools(self, messages: List[Message], tools: List[Dict[str, Any]], **kwargs) -> Union[LLMResponse, ToolCall]:
        """带工具调用"""
        return self.generate(messages, **kwargs)

# ================ OpenAI 客户端 ================

class OpenAIClient(LLMClient):
    """OpenAI API客户端"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://api.openai.com/v1"
        self.model_name = config.model_name or "gpt-3.5-turbo"
    
    def generate(self, messages: List[Message], **kwargs) -> LLMResponse:
        try:
            url = f"{self.base_url}/chat/completions"
            
            payload = {
                "model": self.model_name,
                "messages": [{"role": m.role, "content": m.content} for m in messages],
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens)
            }
            
            headers = {"Authorization": f"Bearer {self.config.api_key}"}
            response = self.session.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                model=self.model_name,
                usage=data.get("usage"),
                finish_reason=data["choices"][0].get("finish_reason")
            )
        
        except Exception as e:
            return LLMResponse(
                content="",
                model=self.model_name,
                error=str(e)
            )
    
    def generate_with_tools(self, messages: List[Message], tools: List[Dict[str, Any]], **kwargs) -> Union[LLMResponse, ToolCall]:
        try:
            url = f"{self.base_url}/chat/completions"
            
            formatted_tools = []
            for tool in tools:
                formatted_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool.get("description", ""),
                        "parameters": tool.get("parameters", {})
                    }
                })
            
            payload = {
                "model": self.model_name,
                "messages": [{"role": m.role, "content": m.content} for m in messages],
                "tools": formatted_tools,
                "tool_choice": "auto",
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens)
            }
            
            headers = {"Authorization": f"Bearer {self.config.api_key}"}
            response = self.session.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            choice = data["choices"][0]
            if choice["message"].get("tool_calls"):
                tool_call = choice["message"]["tool_calls"][0]
                return ToolCall(
                    tool_name=tool_call["function"]["name"],
                    parameters=json.loads(tool_call["function"]["arguments"])
                )
            
            return LLMResponse(
                content=choice["message"]["content"],
                model=self.model_name,
                usage=data.get("usage"),
                finish_reason=choice.get("finish_reason")
            )
        
        except Exception as e:
            return LLMResponse(
                content="",
                model=self.model_name,
                error=str(e)
            )

# ================ 工厂类 ================

class LLMClientFactory:
    """LLM客户端工厂"""
    
    @staticmethod
    def create(config: LLMConfig) -> LLMClient:
        """创建LLM客户端"""
        client_map = {
            ModelProvider.DOUBAO: DoubaoClient,
            ModelProvider.QWEN: QwenClient,
            ModelProvider.ERNIE: ErnieClient,
            ModelProvider.OPENAI: OpenAIClient,
            ModelProvider.CLAUDE: OpenAIClient,  # Claude也用类似OpenAI的格式
            ModelProvider.SPARK: ErnieClient,     # Spark用类似ERNIE的格式
            ModelProvider.ARK: ArkClient,        # 火山方舟
            ModelProvider.VOLCES: ArkClient,     # 火山方舟(volces)
        }
        
        client_class = client_map.get(config.provider)
        if not client_class:
            raise ValueError(f"不支持的模型提供商: {config.provider}")
        
        return client_class(config)

# ================ 便捷函数 ================

def create_llm_client(
    provider: str,
    api_key: str,
    secret_key: Optional[str] = None,
    model_name: str = "",
    **kwargs
) -> LLMClient:
    """便捷函数：创建LLM客户端"""
    config = LLMConfig(
        provider=ModelProvider(provider.lower()),
        api_key=api_key,
        secret_key=secret_key,
        model_name=model_name,
        **kwargs
    )
    return LLMClientFactory.create(config)

def generate_text(
    client: LLMClient,
    prompt: str,
    system_prompt: Optional[str] = None,
    **kwargs
) -> str:
    """便捷函数：生成文本"""
    messages = []
    if system_prompt:
        messages.append(Message(role="system", content=system_prompt))
    messages.append(Message(role="user", content=prompt))
    
    response = client.generate(messages, **kwargs)
    return response.content if not response.error else f"Error: {response.error}"

# ================ Mock LLM 客户端 ================

class MockLLMClient(LLMClient):
    """Mock LLM客户端 - 用于测试和演示"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
    
    async def async_generate(self, messages: List[Message], **kwargs) -> LLMResponse:
        content = "\u6211\u662f\u667a\u80fd\u5b66\u4e60\u52a9\u624b\uff01\u8bf7\u95ee\u4f60\u6709\u4ec0\u4e48\u5b66\u4e60\u65b9\u9762\u7684\u95ee\u9898\u9700\u8981\u5e2e\u52a9\uff1f\n\n\u6211\u53ef\u4ee5\u5e2e\u52a9\u60a8\uff1a\n- \u89e3\u7b54\u5b66\u4e60\u95ee\u9898\n- \u5236\u5b9a\u5b66\u4e60\u8ba1\u5212\n- \u6279\u6539\u4f5c\u4e1a\n- \u966a\u4f34\u5b66\u4e60\n- \u63a8\u8350\u5b66\u4e60\u8d44\u6e90\n- \u5206\u6790\u5b66\u4e60\u60c5\u51b5"
        return LLMResponse(
            content=content,
            error=None,
            model="mock-model",
            usage=LLMUsage(prompt_tokens=10, completion_tokens=50, total_tokens=60)
        )
    
    def generate(self, messages: List[Message], **kwargs) -> LLMResponse:
        content = "\u6211\u662f\u667a\u80fd\u5b66\u4e60\u52a9\u624b\uff01\u8bf7\u95ee\u4f60\u6709\u4ec0\u4e48\u5b66\u4e60\u65b9\u9762\u7684\u95ee\u9898\u9700\u8981\u5e2e\u52a9\uff1f\n\n\u6211\u53ef\u4ee5\u5e2e\u52a9\u60a8\uff1a\n- \u89e3\u7b54\u5b66\u4e60\u95ee\u9898\n- \u5236\u5b9a\u5b66\u4e60\u8ba1\u5212\n- \u6279\u6539\u4f5c\u4e1a\n- \u966a\u4f34\u5b66\u4e60\n- \u63a8\u8350\u5b66\u4e60\u8d44\u6e90\n- \u5206\u6790\u5b66\u4e60\u60c5\u51b5"
        return LLMResponse(
            content=content,
            error=None,
            model="mock-model",
            usage=LLMUsage(prompt_tokens=10, completion_tokens=50, total_tokens=60)
        )

    def generate_with_tools(self, messages: List[Message], tools: List[Dict[str, Any]], **kwargs) -> Union[LLMResponse, ToolCall]:
        return self.generate(messages, **kwargs)


# ================ 全局实例 ================
llm_client = None
LLM_AVAILABLE = False
"""
全局LLM客户端实例

根据配置自动初始化对应的LLM客户端：
- 如果配置了VOLCES_API_KEY，则使用火山方舟
- 如果配置了OPENAI_API_KEY，则使用OpenAI
- 否则创建一个Mock客户端
"""
try:
    from app.core.config import settings
    
    if settings.VOLCES_API_KEY:
        config = LLMConfig(
            provider=ModelProvider.VOLCES,
            api_key=settings.VOLCES_API_KEY,
            base_url=settings.VOLCES_BASE_URL,
            model_name=settings.VOLCES_MODEL,
            temperature=0.7,
            max_tokens=2048
        )
        llm_client = ArkClient(config)
        LLM_AVAILABLE = True
    elif settings.OPENAI_API_KEY:
        config = LLMConfig(
            provider=ModelProvider.OPENAI,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            model_name=settings.OPENAI_MODEL,
            temperature=0.7,
            max_tokens=2048
        )
        llm_client = OpenAIClient(config)
        LLM_AVAILABLE = True
    else:
        print("[WARN] 未配置LLM API密钥，将使用Mock客户端")
        llm_client = MockLLMClient(LLMConfig(provider=ModelProvider.CUSTOM, api_key="mock"))
        LLM_AVAILABLE = False
    
    print(f"[INFO] LLM客户端初始化完成: {llm_client.__class__.__name__}, 可用: {LLM_AVAILABLE}")
except Exception as e:
    print(f"[ERROR] LLM客户端初始化失败: {e}")
    llm_client = MockLLMClient(LLMConfig(provider=ModelProvider.CUSTOM, api_key="mock"))
    LLM_AVAILABLE = False


# ================ 示例 ================

if __name__ == "__main__":
    # 示例：创建豆包客户端并测试
    # 注意：请替换为你自己的API密钥
    # config = LLMConfig(
    #     provider=ModelProvider.DOUBAO,
    #     api_key="YOUR_API_KEY",
    #     secret_key="YOUR_SECRET_KEY",
    #     temperature=0.7
    # )
    
    # client = DoubaoClient(config)
    # response = client.generate([Message(role="user", content="你好")])
    # print(response.content)
    
    print("LLM客户端模块已加载")
    print("支持的模型提供商:", [p.value for p in ModelProvider])