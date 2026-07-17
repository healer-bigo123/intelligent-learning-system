"""
对话接口 - 支持流式输出，已接入大模型 API
"""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List

from app.core.knowledge_base import knowledge_base_manager
from app.core.llm_client import llm_client, Message, LLM_AVAILABLE

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    use_rag: bool = True
    history: Optional[List[dict]] = []


async def generate_response(message: str, use_rag: bool = True, history: Optional[List[dict]] = None):
    """生成对话响应 - 接入真实大模型 API"""

    # 如果启用 RAG，先检索相关知识
    context = ""
    if use_rag:
        try:
            context = knowledge_base_manager.get_context_for_rag(message)
        except Exception:
            context = ""

    # 构建系统提示词
    system_prompt = "你是一位专业的AI学习助手，擅长帮助学生理解知识点、解答问题。请用中文回答，保持简洁清晰。"
    if context:
        system_prompt += f"\n\n以下是与问题相关的参考资料，请基于这些资料回答：\n{context}"

    # 构建消息列表
    messages = []
    if history:
        for msg in history:
            messages.append(Message(role=msg.get("role", "user"), content=msg.get("content", "")))
    messages.append(Message(role="user", content=message))

    # 调用真实大模型 API
    try:
        if not LLM_AVAILABLE:
            yield "data: [ERROR] LLM 服务未配置，请检查 API Key 设置\n\n"
            yield "data: [DONE]\n\n"
            return
        
        response = llm_client.generate(messages)
        
        if response.error:
            yield f"data: [ERROR] 模型调用失败: {response.error}\n\n"
        else:
            # 将响应按字符逐步输出模拟流式效果
            content = response.content
            for char in content:
                yield f"data: {char}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        yield f"data: [ERROR] 模型调用失败: {str(e)}\n\n"
        yield "data: [DONE]\n\n"


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """流式对话接口"""
    return StreamingResponse(
        generate_response(request.message, request.use_rag, request.history),
        media_type="text/event-stream"
    )


@router.post("/")
async def chat(request: ChatRequest):
    """非流式对话接口"""
    # 如果启用 RAG，先检索相关知识
    context = ""
    if request.use_rag:
        try:
            context = knowledge_base_manager.get_context_for_rag(request.message)
        except Exception:
            context = ""

    # 构建系统提示词
    system_prompt = "你是一位专业的AI学习助手，擅长帮助学生理解知识点、解答问题。请用中文回答，保持简洁清晰。"
    if context:
        system_prompt += f"\n\n以下是与问题相关的参考资料，请基于这些资料回答：\n{context}"

    # 构建消息列表
    messages = []
    if request.history:
        for msg in request.history:
            messages.append(Message(role=msg.get("role", "user"), content=msg.get("content", "")))
    messages.append(Message(role="user", content=request.message))

    try:
        if not LLM_AVAILABLE:
            return {
                "response": "LLM 服务未配置，请检查 API Key 设置",
                "session_id": request.session_id,
                "use_rag": request.use_rag,
                "error": True,
            }
        
        response = llm_client.generate(messages)
        
        if response.error:
            return {
                "response": f"模型调用失败: {response.error}",
                "session_id": request.session_id,
                "use_rag": request.use_rag,
                "error": True,
            }
        
        return {
            "response": response.content,
            "session_id": request.session_id,
            "use_rag": request.use_rag,
            "context_used": bool(context),
        }
    except Exception as e:
        return {
            "response": f"模型调用失败: {str(e)}",
            "session_id": request.session_id,
            "use_rag": request.use_rag,
            "error": True,
        }
