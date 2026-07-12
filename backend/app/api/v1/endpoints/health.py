"""
健康检查接口
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def health_check():
    """基础健康检查"""
    return {"status": "healthy", "service": "backend"}


@router.get("/ready")
async def readiness_check():
    """就绪检查 - 验证依赖服务状态"""
    checks = {
        "vector_store": False,
        "llm_client": False,
    }

    # 检查向量存储
    try:
        from app.core.vector_store import vector_store_manager
        stats = vector_store_manager.get_collection_stats()
        checks["vector_store"] = True
        checks["vector_stats"] = stats
    except ImportError:
        try:
            from app.core.simple_vector_store import simple_vector_store
            stats = simple_vector_store.get_stats()
            checks["vector_store"] = True
            checks["vector_mode"] = "simple"
            checks["vector_stats"] = stats
        except Exception as e:
            checks["vector_store_error"] = str(e)
    except Exception as e:
        checks["vector_store_error"] = str(e)

    # 检查 LLM 客户端
    try:
        from app.core.llm_client import llm_client
        checks["llm_client"] = True
        checks["llm_model"] = llm_client.model
    except Exception as e:
        checks["llm_client_error"] = str(e)

    all_ready = checks["llm_client"]

    return {
        "ready": all_ready,
        "checks": checks
    }
