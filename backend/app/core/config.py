"""
全局配置管理 - 使用 Pydantic Settings 加载环境变量
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    APP_NAME: str = Field(default="SmartLearning-MAS", description="应用名称")
    APP_VERSION: str = Field(default="0.1.0", description="应用版本")
    DEBUG: bool = Field(default=True, description="调试模式")
    HOST: str = Field(default="0.0.0.0", description="服务绑定地址")
    PORT: int = Field(default=8000, description="服务端口")
    
    # ===================== LLM 大模型配置 =====================
    # 切换方式：修改 LLM_PROVIDER 即可切换厂商，无需改动业务代码
    # 可选值：volces(火山方舟)、xinghuo(讯飞星火)、openai
    LLM_PROVIDER: str = Field(default="volces", description="LLM 厂商选择")

    # 火山方舟 DeepSeek API (当前主用)
    VOLCES_API_KEY: str = Field(default="", description="火山方舟 API Key")
    VOLCES_BASE_URL: str = Field(default="https://ark.cn-beijing.volces.com/api/v3", description="火山方舟 Base URL")
    VOLCES_MODEL: str = Field(default="deepseek-v3-2-251201", description="火山方舟模型ID")

    # 科大讯飞星火大模型 API
    XINGHUO_APP_ID: str = Field(default="", description="讯飞星火 APP ID")
    XINGHUO_API_KEY: str = Field(default="", description="讯飞星火 API Key")
    XINGHUO_API_SECRET: str = Field(default="", description="讯飞星火 API Secret")
    XINGHUO_BASE_URL: str = Field(default="https://spark-api-open.xf-yun.com/v1", description="讯飞星火 OpenAPI Base URL")
    XINGHUO_DOMAIN: str = Field(default="generalv3.5", description="讯飞星火模型 domain")
    XINGHUO_MODEL: str = Field(default="generalv3.5", description="讯飞星火模型ID")

    # OpenAI API (备选方案)
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API Key")
    OPENAI_BASE_URL: str = Field(default="https://api.openai.com/v1", description="OpenAI Base URL")
    OPENAI_MODEL: str = Field(default="gpt-4o-mini", description="OpenAI 模型ID")
    
    # 数据库配置（默认 SQLite，无需额外安装）
    DATABASE_URL: str = Field(
        default="sqlite:///./data/smart_learning.db",
        description="数据库连接URL"
    )
    REDIS_URL: str = Field(default="", description="Redis连接URL（可选）")
    
    # 向量数据库配置
    CHROMA_PERSIST_DIRECTORY: str = Field(default="./data/chroma_db", description="Chroma持久化目录")
    CHROMA_COLLECTION_NAME: str = Field(default="knowledge_base", description="Chroma集合名称")
    FAISS_INDEX_PATH: str = Field(default="./data/faiss_index", description="FAISS索引路径")
    
    # Embedding 模型配置
    EMBEDDING_MODEL_NAME: str = Field(
        default="BAAI/bge-large-zh-v1.5",
        description="Embedding模型名称"
    )
    EMBEDDING_DEVICE: str = Field(default="cpu", description="Embedding运行设备")
    
    # 知识库配置
    KNOWLEDGE_BASE_DIR: str = Field(default="./knowledge_base", description="知识库目录")
    CHUNK_SIZE: int = Field(default=512, description="文档分块大小")
    CHUNK_OVERLAP: int = Field(default=50, description="文档分块重叠大小")
    
    # 多智能体配置
    AGENT_MAX_ITERATIONS: int = Field(default=10, description="智能体最大迭代次数")
    AGENT_TIMEOUT_SECONDS: int = Field(default=60, description="智能体超时时间")
    
    # JWT 认证配置
    JWT_SECRET_KEY: str = Field(default="smartlearning-secret-key-change-in-production", description="JWT密钥")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT算法")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24 * 7, description="Token过期时间(分钟)")
    
    # 向量存储配置
    USE_SIMPLE_VECTOR: bool = Field(default=True, description="使用简化版向量存储")

    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")
    LOG_FILE: str = Field(default="./logs/app.log", description="日志文件路径")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # 忽略未定义的环境变量


# 全局配置实例
settings = Settings()
