"""
思维导图接口
"""
import uuid
import json
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session

from app.models.database import MindMap, get_db
from app.core.security import get_current_user_id
from app.core.llm_client import llm_client

router = APIRouter()


# ========== 请求/响应模型 ==========

class MindMapGenerateRequest(BaseModel):
    """生成思维导图请求"""
    subject: str = Field(..., description="学科")
    knowledge_point: str = Field(..., description="知识点")


class MindMapUpdateRequest(BaseModel):
    """更新思维导图请求"""
    title: Optional[str] = Field(None, description="标题")
    content: Optional[dict] = Field(None, description="思维导图内容")
    status: Optional[str] = Field(None, description="active / archived")


class MindMapResponse(BaseModel):
    """思维导图响应"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
    subject: str
    content: str
    status: str
    created_at: datetime
    updated_at: datetime


class MindMapListResponse(BaseModel):
    """思维导图列表响应"""
    total: int
    items: List[MindMapResponse]


# ========== 接口实现 ==========

@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_mindmap(
    request: MindMapGenerateRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    根据知识点生成思维导图
    """
    system_prompt = (
        "你是一位专业的教育内容生成助手，擅长根据知识点生成结构清晰的思维导图。"
        "请严格按照以下 JSON 格式返回思维导图数据，不要返回任何其他内容：\n"
        "{\n"
        '  "title": "思维导图标题",\n'
        '  "nodes": [\n'
        '    {"id": "1", "label": "中心主题", "level": 0},\n'
        '    {"id": "2", "label": "分支1", "level": 1, "parentId": "1"},\n'
        '    {"id": "3", "label": "分支2", "level": 1, "parentId": "1"}\n'
        "  ],\n"
        '  "edges": [\n'
        '    {"source": "1", "target": "2"},\n'
        '    {"source": "1", "target": "3"}\n'
        "  ]\n"
        "}\n"
        "要求：\n"
        "1. id 使用字符串，从 '1' 开始递增\n"
        "2. level 表示层级，0 为根节点，1 为一级分支，以此类推\n"
        "3. parentId 表示父节点 id，根节点不需要 parentId\n"
        "4. edges 中的 source 和 target 对应节点的 id\n"
        "5. 内容要丰富、有教育意义，覆盖该知识点的核心概念"
    )

    user_prompt = f"请为 {request.subject} 学科的「{request.knowledge_point}」知识点生成一份思维导图。"

    messages = llm_client.build_messages(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )

    try:
        response = await llm_client.chat(messages, stream=False)
        content = response["choices"][0]["message"]["content"]

        # 尝试从响应中提取 JSON
        try:
            mindmap_data = json.loads(content)
        except json.JSONDecodeError:
            # 如果直接解析失败，尝试提取 markdown 代码块中的 JSON
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()
            mindmap_data = json.loads(json_str)

        title = mindmap_data.get("title", f"{request.knowledge_point} 思维导图")
        mindmap_id = str(uuid.uuid4())

        new_mindmap = MindMap(
            id=mindmap_id,
            user_id=user_id,
            title=title,
            subject=request.subject,
            content=json.dumps(mindmap_data, ensure_ascii=False),
            status="active",
        )

        db.add(new_mindmap)
        db.commit()
        db.refresh(new_mindmap)

        return new_mindmap
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"思维导图生成失败: {str(e)}"
        )


@router.get("", response_model=MindMapListResponse)
async def list_mindmaps(
    subject: Optional[str] = Query(None, description="按学科筛选"),
    status: Optional[str] = Query(None, description="按状态筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的思维导图列表
    """
    query = db.query(MindMap).filter(MindMap.user_id == user_id)

    if subject:
        query = query.filter(MindMap.subject == subject)
    if status:
        query = query.filter(MindMap.status == status)

    total = query.count()
    items = query.order_by(MindMap.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {"total": total, "items": items}


@router.get("/{mindmap_id}", response_model=MindMapResponse)
async def get_mindmap(
    mindmap_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取单个思维导图详情
    """
    mindmap = db.query(MindMap).filter(
        MindMap.id == mindmap_id,
        MindMap.user_id == user_id
    ).first()

    if not mindmap:
        raise HTTPException(status_code=404, detail="思维导图不存在")

    return mindmap


@router.put("/{mindmap_id}")
async def update_mindmap(
    mindmap_id: str,
    request: MindMapUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    更新思维导图（标题、内容）
    """
    mindmap = db.query(MindMap).filter(
        MindMap.id == mindmap_id,
        MindMap.user_id == user_id
    ).first()

    if not mindmap:
        raise HTTPException(status_code=404, detail="思维导图不存在")

    update_data = request.model_dump(exclude_unset=True)

    if "content" in update_data and update_data["content"] is not None:
        update_data["content"] = json.dumps(update_data["content"], ensure_ascii=False)

    for field, value in update_data.items():
        setattr(mindmap, field, value)

    db.commit()
    db.refresh(mindmap)

    return mindmap


@router.delete("/{mindmap_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mindmap(
    mindmap_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    删除思维导图
    """
    mindmap = db.query(MindMap).filter(
        MindMap.id == mindmap_id,
        MindMap.user_id == user_id
    ).first()

    if not mindmap:
        raise HTTPException(status_code=404, detail="思维导图不存在")

    db.delete(mindmap)
    db.commit()

    return None
