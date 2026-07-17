"""
学习资料库接口 - 类似作业帮资料库
支持：资料录入、分类、标签、关键词搜索、筛选查询
"""
import uuid
from datetime import datetime
from typing import Optional, List

import httpx
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.models.database import StudyMaterial, get_db
from app.core.security import get_current_user_id
from app.core.video_search import video_match_service

router = APIRouter()


# ========== 请求/响应模型 ==========

class StudyMaterialCreateRequest(BaseModel):
    """创建学习资料请求"""
    title: str = Field(..., description="资料标题")
    content: str = Field(..., description="资料内容")
    subject: str = Field(..., description="学科")
    grade: Optional[str] = Field(None, description="年级")
    material_type: str = Field("知识点", description="资料类型: 知识点/公式/例题/文章/笔记")
    knowledge_point: Optional[str] = Field(None, description="所属知识点")
    tags: Optional[str] = Field(None, description="标签，逗号分隔")
    source: Optional[str] = Field(None, description="来源")
    difficulty: int = Field(3, ge=1, le=5, description="难度 1-5")


class StudyMaterialUpdateRequest(BaseModel):
    """更新学习资料请求"""
    title: Optional[str] = Field(None, description="资料标题")
    content: Optional[str] = Field(None, description="资料内容")
    subject: Optional[str] = Field(None, description="学科")
    grade: Optional[str] = Field(None, description="年级")
    material_type: Optional[str] = Field(None, description="资料类型")
    knowledge_point: Optional[str] = Field(None, description="所属知识点")
    tags: Optional[str] = Field(None, description="标签")
    source: Optional[str] = Field(None, description="来源")
    difficulty: Optional[int] = Field(None, ge=1, le=5, description="难度")
    status: Optional[str] = Field(None, description="active / archived")


class StudyMaterialResponse(BaseModel):
    """学习资料响应"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
    content: str
    subject: str
    grade: Optional[str]
    material_type: str
    knowledge_point: Optional[str]
    tags: str
    source: Optional[str]
    difficulty: int
    views: int
    status: str
    created_at: datetime
    updated_at: datetime


class StudyMaterialListResponse(BaseModel):
    """学习资料列表响应"""
    total: int
    items: List[StudyMaterialResponse]


class StudyMaterialStatsResponse(BaseModel):
    """学习资料统计响应"""
    total: int
    by_subject: dict
    by_type: dict
    by_grade: dict


# ========== 接口实现 ==========

# ========== 图片代理接口（必须在 /{material_id} 之前） ==========

@router.get("/image-proxy")
async def image_proxy(url: str = Query(..., description="图片URL")):
    """
    图片代理接口 - 解决B站图片防盗链问题
    前端通过此接口加载B站封面图，后端添加正确的Referer头
    无需认证（img标签无法设置Authorization头）
    """
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="无效的URL")

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.bilibili.com",
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "image/jpeg")

            return StreamingResponse(
                response.content,
                media_type=content_type,
                headers={
                    "Cache-Control": "public, max-age=86400",
                }
            )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"图片加载失败: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"代理错误: {str(e)}")


@router.post("", status_code=status.HTTP_201_CREATED, response_model=StudyMaterialResponse)
async def create_study_material(
    request: StudyMaterialCreateRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    添加学习资料
    """
    material_id = str(uuid.uuid4())
    new_material = StudyMaterial(
        id=material_id,
        user_id=user_id,
        title=request.title,
        content=request.content,
        subject=request.subject,
        grade=request.grade,
        material_type=request.material_type,
        knowledge_point=request.knowledge_point,
        tags=request.tags or "",
        source=request.source,
        difficulty=request.difficulty,
        views=0,
        status="active",
    )

    db.add(new_material)
    db.commit()
    db.refresh(new_material)

    return new_material


@router.get("", response_model=StudyMaterialListResponse)
async def list_study_materials(
    subject: Optional[str] = Query(None, description="按学科筛选"),
    grade: Optional[str] = Query(None, description="按年级筛选"),
    material_type: Optional[str] = Query(None, description="按类型筛选"),
    knowledge_point: Optional[str] = Query(None, description="按知识点筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索（标题+内容）"),
    tag: Optional[str] = Query(None, description="按标签筛选"),
    difficulty: Optional[int] = Query(None, description="按难度筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取学习资料列表（支持多维度筛选和搜索）
    """
    query = db.query(StudyMaterial).filter(StudyMaterial.status == "active")

    if subject:
        query = query.filter(StudyMaterial.subject == subject)
    if grade:
        query = query.filter(StudyMaterial.grade == grade)
    if material_type:
        query = query.filter(StudyMaterial.material_type == material_type)
    if knowledge_point:
        query = query.filter(StudyMaterial.knowledge_point.contains(knowledge_point))
    if tag:
        query = query.filter(StudyMaterial.tags.contains(tag))
    if difficulty:
        query = query.filter(StudyMaterial.difficulty == difficulty)
    if keyword:
        query = query.filter(
            or_(
                StudyMaterial.title.contains(keyword),
                StudyMaterial.content.contains(keyword),
                StudyMaterial.knowledge_point.contains(keyword),
            )
        )

    total = query.count()
    items = query.order_by(StudyMaterial.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {"total": total, "items": items}


@router.get("/{material_id}", response_model=StudyMaterialResponse)
async def get_study_material(
    material_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取学习资料详情（同时增加浏览次数）
    """
    material = db.query(StudyMaterial).filter(
        StudyMaterial.id == material_id,
        StudyMaterial.status == "active"
    ).first()

    if not material:
        raise HTTPException(status_code=404, detail="资料不存在")

    # 增加浏览次数
    material.views += 1
    db.commit()

    return material


@router.put("/{material_id}", response_model=StudyMaterialResponse)
async def update_study_material(
    material_id: str,
    request: StudyMaterialUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    更新学习资料
    """
    material = db.query(StudyMaterial).filter(
        StudyMaterial.id == material_id,
        StudyMaterial.user_id == user_id
    ).first()

    if not material:
        raise HTTPException(status_code=404, detail="资料不存在或无权限")

    update_data = request.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(material, field, value)

    db.commit()
    db.refresh(material)

    return material


@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_study_material(
    material_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    删除学习资料（软删除，将状态改为 archived）
    """
    material = db.query(StudyMaterial).filter(
        StudyMaterial.id == material_id,
        StudyMaterial.user_id == user_id
    ).first()

    if not material:
        raise HTTPException(status_code=404, detail="资料不存在或无权限")

    material.status = "archived"
    db.commit()

    return None


@router.get("/stats/overview", response_model=StudyMaterialStatsResponse)
async def get_study_material_stats(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    学习资料统计（按学科、类型、年级分组）
    """
    # 总数
    total = db.query(StudyMaterial).filter(
        StudyMaterial.status == "active"
    ).count()

    # 按学科统计
    subject_results = db.query(
        StudyMaterial.subject,
        func.count(StudyMaterial.id).label("count")
    ).filter(StudyMaterial.status == "active").group_by(StudyMaterial.subject).all()

    # 按类型统计
    type_results = db.query(
        StudyMaterial.material_type,
        func.count(StudyMaterial.id).label("count")
    ).filter(StudyMaterial.status == "active").group_by(StudyMaterial.material_type).all()

    # 按年级统计
    grade_results = db.query(
        StudyMaterial.grade,
        func.count(StudyMaterial.id).label("count")
    ).filter(
        StudyMaterial.status == "active",
        StudyMaterial.grade.isnot(None)
    ).group_by(StudyMaterial.grade).all()

    return {
        "total": total,
        "by_subject": {r.subject: r.count for r in subject_results},
        "by_type": {r.material_type: r.count for r in type_results},
        "by_grade": {r.grade: r.count for r in grade_results if r.grade},
    }


@router.get("/filter/options")
async def get_filter_options(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取筛选选项（学科列表、年级列表、类型列表）
    """
    subjects = [r[0] for r in db.query(StudyMaterial.subject).filter(
        StudyMaterial.status == "active"
    ).distinct().all() if r[0]]

    grades = [r[0] for r in db.query(StudyMaterial.grade).filter(
        StudyMaterial.status == "active",
        StudyMaterial.grade.isnot(None)
    ).distinct().all() if r[0]]

    types = [r[0] for r in db.query(StudyMaterial.material_type).filter(
        StudyMaterial.status == "active"
    ).distinct().all() if r[0]]

    # 获取所有标签
    all_tags = set()
    tag_results = db.query(StudyMaterial.tags).filter(
        StudyMaterial.status == "active"
    ).all()
    for tags_str in tag_results:
        if tags_str[0]:
            all_tags.update([t.strip() for t in tags_str[0].split(",") if t.strip()])

    return {
        "subjects": sorted(subjects),
        "grades": sorted(grades),
        "material_types": sorted(types),
        "tags": sorted(list(all_tags)),
    }


@router.get("/{material_id}/match-videos")
async def match_videos_for_material(
    material_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    根据学习资料智能匹配相关视频
    
    根据资料的标题、学科、知识点、标签等信息，
    自动从 B 站搜索并匹配相关的教学视频
    """
    material = db.query(StudyMaterial).filter(
        StudyMaterial.id == material_id,
        StudyMaterial.status == "active"
    ).first()
    
    if not material:
        raise HTTPException(status_code=404, detail="资料不存在")
    
    # 构建资料信息字典
    material_dict = {
        "title": material.title,
        "content": material.content,
        "subject": material.subject,
        "knowledge_point": material.knowledge_point,
        "tags": material.tags,
    }
    
    # 调用视频匹配服务
    try:
        videos = await video_match_service.match_videos(material_dict, max_results=10)
        return {
            "videos": videos,
            "total": len(videos),
            "material_id": material_id,
            "material_title": material.title
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"视频匹配失败: {str(e)}"
        )
