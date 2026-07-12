"""
对话接口 - 支持流式输出，已接入火山方舟 DeepSeek API
"""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List

from app.core.knowledge_base import knowledge_base_manager
from app.core.llm_client import llm_client

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
        context = knowledge_base_manager.get_context_for_rag(message)

    # 构建系统提示词
    system_prompt = "你是一位专业的AI学习助手，擅长帮助学生理解知识点、解答问题。请用中文回答，保持简洁清晰。"
    if context:
        system_prompt += f"\n\n以下是与问题相关的参考资料，请基于这些资料回答：\n{context}"

    # 构建消息列表
    messages = llm_client.build_messages(
        system_prompt=system_prompt,
        user_prompt=message,
        history=history,
    )

    # 调用真实大模型 API 流式输出
    try:
        async for chunk in llm_client.chat_stream(messages):
            yield f"data: {chunk}\n\n"
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
        context = knowledge_base_manager.get_context_for_rag(request.message)

    # 构建系统提示词
    system_prompt = "你是一位专业的AI学习助手，擅长帮助学生理解知识点、解答问题。请用中文回答，保持简洁清晰。"
    if context:
        system_prompt += f"\n\n以下是与问题相关的参考资料，请基于这些资料回答：\n{context}"

    # 构建消息列表
    messages = llm_client.build_messages(
        system_prompt=system_prompt,
        user_prompt=request.message,
        history=request.history,
    )

    try:
        response = await llm_client.chat(messages, stream=False)
        content = response["choices"][0]["message"]["content"]
        return {
            "response": content,
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
