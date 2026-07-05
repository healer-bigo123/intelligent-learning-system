"""
外部数据源管理接口
"""
import uuid
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.core.security import get_current_user_id
from app.core.external_data import (
    data_source_manager,
    DataSourceConfig,
    DataSourceType,
    AuthType,
    SyncStrategy,
    SyncRecord,
    DataSyncStatus,
    ExternalDataError,
    register_education_api,
    register_exercise_bank
)

router = APIRouter()

# ================ 请求/响应模型 ================

class DataSourceConfigRequest(BaseModel):
    """创建/更新数据源配置请求"""
    name: str = Field(..., description="数据源名称")
    type: str = Field(..., description="数据源类型")
    base_url: str = Field(..., description="基础URL")
    auth_type: str = Field(default="none", description="认证类型")
    auth_config: Optional[Dict[str, Any]] = Field(default={}, description="认证配置")
    sync_strategy: str = Field(default="manual", description="同步策略")
    sync_interval: int = Field(default=3600, ge=60, description="同步间隔（秒）")
    description: str = Field(default="", description="描述")

class DataSourceConfigResponse(BaseModel):
    """数据源配置响应"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    name: str
    type: str
    base_url: str
    auth_type: str
    sync_strategy: str
    sync_interval: int
    enabled: bool
    description: str
    created_at: datetime
    updated_at: datetime

class SyncRecordResponse(BaseModel):
    """同步记录响应"""
    id: str
    source_id: str
    sync_type: str
    status: str
    total_records: int
    success_count: int
    failed_count: int
    error_message: str
    started_at: datetime
    completed_at: Optional[datetime]

class SearchRequest(BaseModel):
    """搜索请求"""
    query: str = Field(..., description="搜索关键词")
    filters: Optional[Dict[str, Any]] = Field(default={}, description="筛选条件")
    source_ids: Optional[List[str]] = Field(default=None, description="指定数据源ID列表")

class SearchResultItem(BaseModel):
    """搜索结果项"""
    id: Optional[str]
    title: Optional[str]
    content: Optional[str]
    type: Optional[str]
    subject: Optional[str]
    source_id: str
    source_name: str
    extra: Optional[Dict[str, Any]]

class SyncStatusResponse(BaseModel):
    """同步状态响应"""
    source_id: str
    source_name: str
    status: str
    last_sync_time: Optional[datetime]
    sync_interval: int

class DataSourceStatsResponse(BaseModel):
    """数据源统计响应"""
    total_sources: int
    active_sources: int
    total_sync_count: int
    success_sync_count: int
    failed_sync_count: int

# ================ 辅助函数 ================

def parse_enum_value(enum_class, value: str, default=None):
    """解析枚举值"""
    try:
        return enum_class(value)
    except ValueError:
        if default is not None:
            return default
        raise HTTPException(status_code=400, detail=f"无效的{enum_class.__name__}值: {value}")

# ================ 接口实现 ================

@router.post("", status_code=status.HTTP_201_CREATED, response_model=DataSourceConfigResponse)
async def create_data_source(
    request: DataSourceConfigRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    创建外部数据源配置
    
    支持的数据源类型:
    - education_api: 教育数据API
    - knowledge_base: 知识库
    - exercise_bank: 外部题库
    - learning_platform: 学习平台
    - custom_api: 自定义API
    
    支持的认证类型:
    - none: 无需认证
    - api_key: API密钥
    - oauth2: OAuth2.0
    - basic: 基础认证
    - bearer_token: Bearer Token
    - custom: 自定义认证
    
    支持的同步策略:
    - manual: 手动同步
    - scheduled: 定时同步
    - realtime: 实时同步
    - on_demand: 按需同步
    """
    try:
        # 解析枚举值
        source_type = parse_enum_value(DataSourceType, request.type)
        auth_type = parse_enum_value(AuthType, request.auth_type)
        sync_strategy = parse_enum_value(SyncStrategy, request.sync_strategy)
        
        # 创建配置
        config = DataSourceConfig(
            id=str(uuid.uuid4()),
            name=request.name,
            type=source_type,
            base_url=request.base_url,
            auth_type=auth_type,
            auth_config=request.auth_config or {},
            sync_strategy=sync_strategy,
            sync_interval=request.sync_interval,
            enabled=True,
            description=request.description
        )
        
        # 注册数据源
        data_source_manager.register_source(config)
        
        return {
            "id": config.id,
            "name": config.name,
            "type": config.type.value,
            "base_url": config.base_url,
            "auth_type": config.auth_type.value,
            "sync_strategy": config.sync_strategy.value,
            "sync_interval": config.sync_interval,
            "enabled": config.enabled,
            "description": config.description,
            "created_at": config.created_at,
            "updated_at": config.updated_at
        }
    
    except ExternalDataError as e:
        raise HTTPException(status_code=500, detail=f"数据源注册失败: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=List[DataSourceConfigResponse])
async def list_data_sources(
    source_type: Optional[str] = Query(None, description="按类型筛选"),
    enabled: Optional[bool] = Query(None, description="按启用状态筛选"),
    user_id: str = Depends(get_current_user_id)
):
    """
    获取所有数据源配置列表
    """
    sources = data_source_manager.list_sources()
    
    # 按类型筛选
    if source_type:
        try:
            type_enum = DataSourceType(source_type)
            sources = [s for s in sources if s.type == type_enum]
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的数据源类型: {source_type}")
    
    # 按启用状态筛选
    if enabled is not None:
        sources = [s for s in sources if s.enabled == enabled]
    
    return [
        {
            "id": s.id,
            "name": s.name,
            "type": s.type.value,
            "base_url": s.base_url,
            "auth_type": s.auth_type.value,
            "sync_strategy": s.sync_strategy.value,
            "sync_interval": s.sync_interval,
            "enabled": s.enabled,
            "description": s.description,
            "created_at": s.created_at,
            "updated_at": s.updated_at
        }
        for s in sources
    ]

@router.get("/{source_id}", response_model=DataSourceConfigResponse)
async def get_data_source(
    source_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    获取指定数据源配置详情
    """
    source = data_source_manager.get_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="数据源不存在")
    
    config = source.config
    return {
        "id": config.id,
        "name": config.name,
        "type": config.type.value,
        "base_url": config.base_url,
        "auth_type": config.auth_type.value,
        "sync_strategy": config.sync_strategy.value,
        "sync_interval": config.sync_interval,
        "enabled": config.enabled,
        "description": config.description,
        "created_at": config.created_at,
        "updated_at": config.updated_at
    }

@router.put("/{source_id}", response_model=DataSourceConfigResponse)
async def update_data_source(
    source_id: str,
    request: DataSourceConfigRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    更新数据源配置
    """
    # 检查数据源是否存在
    existing_source = data_source_manager.get_source(source_id)
    if not existing_source:
        raise HTTPException(status_code=404, detail="数据源不存在")
    
    try:
        # 解析枚举值
        source_type = parse_enum_value(DataSourceType, request.type)
        auth_type = parse_enum_value(AuthType, request.auth_type)
        sync_strategy = parse_enum_value(SyncStrategy, request.sync_strategy)
        
        # 创建新配置（保持原有ID）
        config = DataSourceConfig(
            id=source_id,
            name=request.name,
            type=source_type,
            base_url=request.base_url,
            auth_type=auth_type,
            auth_config=request.auth_config or {},
            sync_strategy=sync_strategy,
            sync_interval=request.sync_interval,
            enabled=existing_source.config.enabled,
            description=request.description,
            created_at=existing_source.config.created_at,
            updated_at=datetime.utcnow()
        )
        
        # 先注销旧的，再注册新的
        data_source_manager.unregister_source(source_id)
        data_source_manager.register_source(config)
        
        return {
            "id": config.id,
            "name": config.name,
            "type": config.type.value,
            "base_url": config.base_url,
            "auth_type": config.auth_type.value,
            "sync_strategy": config.sync_strategy.value,
            "sync_interval": config.sync_interval,
            "enabled": config.enabled,
            "description": config.description,
            "created_at": config.created_at,
            "updated_at": config.updated_at
        }
    
    except ExternalDataError as e:
        raise HTTPException(status_code=500, detail=f"数据源更新失败: {str(e)}")

@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_data_source(
    source_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    删除数据源配置
    """
    if not data_source_manager.get_source(source_id):
        raise HTTPException(status_code=404, detail="数据源不存在")
    
    data_source_manager.unregister_source(source_id)
    return None

@router.post("/{source_id}/enable")
async def enable_data_source(
    source_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    启用数据源
    """
    source = data_source_manager.get_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="数据源不存在")
    
    source.config.enabled = True
    return {"message": "数据源已启用", "source_id": source_id}

@router.post("/{source_id}/disable")
async def disable_data_source(
    source_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    禁用数据源
    """
    source = data_source_manager.get_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="数据源不存在")
    
    source.config.enabled = False
    return {"message": "数据源已禁用", "source_id": source_id}

@router.post("/{source_id}/sync")
async def sync_data_source(
    source_id: str,
    force: bool = Query(False, description="是否强制同步"),
    user_id: str = Depends(get_current_user_id)
):
    """
    手动同步指定数据源
    """
    source = data_source_manager.get_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="数据源不存在")
    
    if not source.config.enabled:
        raise HTTPException(status_code=400, detail="数据源未启用")
    
    try:
        record = source.sync_data(force)
        
        return {
            "record_id": record.id,
            "source_id": record.source_id,
            "sync_type": record.sync_type,
            "status": record.status.value,
            "total_records": record.total_records,
            "success_count": record.success_count,
            "failed_count": record.failed_count,
            "error_message": record.error_message,
            "started_at": record.started_at,
            "completed_at": record.completed_at
        }
    
    except ExternalDataError as e:
        raise HTTPException(status_code=500, detail=f"同步失败: {str(e)}")

@router.post("/sync-all")
async def sync_all_data_sources(
    force: bool = Query(False, description="是否强制同步"),
    user_id: str = Depends(get_current_user_id)
):
    """
    同步所有已启用的数据源
    """
    try:
        records = data_source_manager.sync_all(force)
        
        return {
            "total_sources": len(records),
            "success_count": sum(1 for r in records if r.status == DataSyncStatus.SUCCESS),
            "failed_count": sum(1 for r in records if r.status == DataSyncStatus.FAILED),
            "sync_records": [
                {
                    "record_id": r.id,
                    "source_id": r.source_id,
                    "status": r.status.value,
                    "success_count": r.success_count,
                    "failed_count": r.failed_count,
                    "error_message": r.error_message
                }
                for r in records
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量同步失败: {str(e)}")

@router.get("/{source_id}/sync-history", response_model=List[SyncRecordResponse])
async def get_sync_history(
    source_id: str,
    limit: int = Query(20, ge=1, le=100, description="获取数量限制"),
    user_id: str = Depends(get_current_user_id)
):
    """
    获取指定数据源的同步历史记录
    """
    source = data_source_manager.get_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="数据源不存在")
    
    history = data_source_manager.get_sync_history(source_id, limit)
    
    return [
        {
            "id": h.id,
            "source_id": h.source_id,
            "sync_type": h.sync_type,
            "status": h.status.value,
            "total_records": h.total_records,
            "success_count": h.success_count,
            "failed_count": h.failed_count,
            "error_message": h.error_message,
            "started_at": h.started_at,
            "completed_at": h.completed_at
        }
        for h in history
    ]

@router.post("/search", response_model=List[SearchResultItem])
async def search_external_data(
    request: SearchRequest,
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
    user_id: str = Depends(get_current_user_id)
):
    """
    在外部数据源中搜索数据
    
    搜索结果会标记数据来源，便于区分本地数据和外部数据
    """
    try:
        # 如果指定了数据源，则逐个搜索
        if request.source_ids:
            results = []
            for source_id in request.source_ids:
                source = data_source_manager.get_source(source_id)
                if not source or not source.config.enabled:
                    continue
                
                try:
                    data = source.search_data(request.query, request.filters)
                    for item in data[:limit//len(request.source_ids)]:
                        results.append({
                            "id": item.get('id'),
                            "title": item.get('title', item.get('name', item.get('question', '')[:50] + '...')),
                            "content": item.get('content', item.get('description', '')[:100] + '...'),
                            "type": item.get('type', item.get('category', 'unknown')),
                            "subject": item.get('subject', item.get('category', '')),
                            "source_id": source_id,
                            "source_name": source.config.name,
                            "extra": item
                        })
                except Exception as e:
                    # 单个数据源搜索失败不影响其他数据源
                    continue
        else:
            # 在所有数据源中搜索
            all_results = data_source_manager.search_all(request.query, request.filters)
            
            # 转换结果格式
            results = []
            for item in all_results[:limit]:
                source_name = item.pop('source_name', '未知')
                source_id = item.pop('source_id', '')
                
                results.append({
                    "id": item.get('id'),
                    "title": item.get('title', item.get('name', str(item.get('question', ''))[:50] + '...')),
                    "content": item.get('content', item.get('description', str(item.get('explanation', ''))[:100] + '...')),
                    "type": item.get('type', item.get('category', 'unknown')),
                    "subject": item.get('subject', item.get('category', '')),
                    "source_id": source_id,
                    "source_name": source_name,
                    "extra": item
                })
        
        return results
    
    except ExternalDataError as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")

@router.get("/{source_id}/fetch")
async def fetch_from_source(
    source_id: str,
    endpoint: str = Query(..., description="API端点路径"),
    params: Optional[str] = Query(None, description="查询参数（JSON字符串）"),
    user_id: str = Depends(get_current_user_id)
):
    """
    从指定数据源获取原始数据
    """
    source = data_source_manager.get_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="数据源不存在")
    
    if not source.config.enabled:
        raise HTTPException(status_code=400, detail="数据源未启用")
    
    try:
        # 解析参数
        parsed_params = json.loads(params) if params else None
        
        # 获取数据
        data = source.fetch_data(endpoint, parsed_params)
        
        return {
            "source_id": source_id,
            "source_name": source.config.name,
            "endpoint": endpoint,
            "data": data,
            "timestamp": datetime.utcnow()
        }
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="无效的参数JSON格式")
    except ExternalDataError as e:
        raise HTTPException(status_code=500, detail=f"数据获取失败: {str(e)}")

@router.get("/status", response_model=Dict[str, Any])
async def get_data_source_status(
    user_id: str = Depends(get_current_user_id)
):
    """
    获取所有数据源的状态概览
    """
    status = data_source_manager.get_status()
    sources = data_source_manager.list_sources()
    
    return {
        "manager_status": status,
        "sources": [
            {
                "source_id": s.id,
                "source_name": s.name,
                "type": s.type.value,
                "enabled": s.enabled,
                "sync_interval": s.sync_interval,
                "sync_strategy": s.sync_strategy.value
            }
            for s in sources
        ]
    }

@router.get("/stats", response_model=DataSourceStatsResponse)
async def get_data_source_stats(
    user_id: str = Depends(get_current_user_id)
):
    """
    获取数据源统计信息
    """
    sources = data_source_manager.list_sources()
    history = data_source_manager.get_sync_history(limit=1000)
    
    return {
        "total_sources": len(sources),
        "active_sources": len([s for s in sources if s.enabled]),
        "total_sync_count": len(history),
        "success_sync_count": sum(1 for h in history if h.status == DataSyncStatus.SUCCESS),
        "failed_sync_count": sum(1 for h in history if h.status == DataSyncStatus.FAILED)
    }