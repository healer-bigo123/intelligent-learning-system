"""
图片分析接口 - 支持图片上传、识别和批改
"""
from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import base64
import io
from PIL import Image

from app.core.llm_client import llm_client, LLM_AVAILABLE
from app.core.agent_system import GradingAgent, Task, Intent, IntentType

router = APIRouter()


class ImageAnalysisRequest(BaseModel):
    """图片分析请求"""
    image_base64: Optional[str] = None  # Base64编码的图片
    prompt: Optional[str] = None  # 用户问题/提示
    analysis_type: str = "grading"  # grading: 批改, recognition: 识别