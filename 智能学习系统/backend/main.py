"""
基于大模型的个性化资源生成与学习多智能体系统 - FastAPI 主入口
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    print(f"[START] {settings.APP_NAME} v{settings.APP_VERSION} 启动中...")

    # 初始化数据目录
    os.makedirs("./data", exist_ok=True)
    os.makedirs("./logs", exist_ok=True)
    os.makedirs(settings.KNOWLEDGE_BASE_DIR, exist_ok=True)

    # 初始化 SQLite 数据库
    try:
        from app.models.database import init_db
        init_db()
    except Exception as e:
        print(f"[WARN] 数据库初始化跳过: {e}")

    # 初始化向量数据库（可选，缺少依赖时跳过）
    try:
        from app.core.vector_store import init_vector_store
        await init_vector_store()
    except ImportError as e:
        print(f"[WARN] 向量数据库依赖未安装，跳过初始化: {e}")
        print("   如需使用向量数据库，请运行: pip install chromadb langchain-chroma langchain-huggingface sentence-transformers")
    except Exception as e:
        print(f"[WARN] 向量数据库初始化跳过: {e}")

    # 初始化知识库（可选，缺少依赖时跳过）
    try:
        from app.core.knowledge_base import init_knowledge_base
        await init_knowledge_base()
    except ImportError as e:
        print(f"[WARN] 知识库依赖未安装，跳过初始化: {e}")
        print("   如需使用知识库，请运行: pip install langchain-community langchain-text-splitters")
    except Exception as e:
        print(f"[WARN] 知识库初始化跳过: {e}")

    print("[OK] 系统初始化完成")
    yield

    # 关闭时清理
    print("[STOP] 系统关闭中...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="基于大模型的个性化资源生成与学习多智能体系统",
    lifespan=lifespan,
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
