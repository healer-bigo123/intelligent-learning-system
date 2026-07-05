"""
知识库管理接口
"""
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel

from app.core.knowledge_base import knowledge_base_manager

# 向量存储管理器 - 延迟导入避免启动失败
try:
    from app.core.vector_store import vector_store_manager
except ImportError:
    from app.core.simple_vector_store import simple_vector_store as vector_store_manager

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    k: int = 5
    store_type: str = "chroma"


class SearchResponse(BaseModel):
    results: List[dict]
    total: int


@router.post("/search", response_model=SearchResponse)
async def search_knowledge(request: SearchRequest):
    """搜索知识库"""
    try:
        results = knowledge_base_manager.search_knowledge_base(
            query=request.query,
            k=request.k,
            store_type=request.store_type
        )
        return SearchResponse(results=results, total=len(results))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    store_type: str = Form("chroma")
):
    """上传文档到知识库"""
    import tempfile
    import os
    
    # 验证文件类型
    allowed_extensions = [".txt", ".md", ".pdf"]
    ext = os.path.splitext(file.filename)[1].lower()
    
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {ext}，仅支持: {', '.join(allowed_extensions)}"
        )
    
    try:
        # 保存临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # 加载文档
        documents = knowledge_base_manager.load_document(tmp_path)
        
        # 添加到知识库
        knowledge_base_manager.add_to_knowledge_base(documents, store_type)
        
        # 清理临时文件
        os.unlink(tmp_path)
        
        return {
            "message": "文档上传成功",
            "filename": file.filename,
            "document_count": len(documents),
            "store_type": store_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.get("/stats")
async def get_knowledge_stats():
    """获取知识库统计信息"""
    try:
        stats = vector_store_manager.get_collection_stats()
        return {
            "vector_stats": stats,
            "supported_formats": [".txt", ".md", ".pdf"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")
