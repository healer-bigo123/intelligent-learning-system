"""
向量数据库管理模块 - 支持 Chroma 和 FAISS
"""
import os
from typing import List, Dict, Any, Optional

# 延迟导入 langchain 相关库，避免启动时导入失败
try:
    from langchain_chroma import Chroma
except ImportError:
    Chroma = None

try:
    from langchain_community.vectorstores import FAISS
except ImportError:
    FAISS = None

# 尝试导入 langchain-huggingface，如果不存在则使用备选方案
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
    except ImportError:
        HuggingFaceEmbeddings = None

from app.core.config import settings


class VectorStoreManager:
    """向量数据库管理器"""
    
    def __init__(self):
        self.embedding_model = None
        self.chroma_store = None
        self.faiss_store = None
        
    def init_embedding_model(self):
        """初始化 Embedding 模型"""
        if self.embedding_model is None:
            if HuggingFaceEmbeddings is None:
                raise ImportError(
                    "HuggingFaceEmbeddings 不可用。请运行: "
                    "pip install langchain-huggingface sentence-transformers"
                )
            print(f" 正在加载 Embedding 模型: {settings.EMBEDDING_MODEL_NAME}")
            print(f"   首次加载会从 HuggingFace 下载模型，请耐心等待...")
            self.embedding_model = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDING_MODEL_NAME,
                model_kwargs={"device": settings.EMBEDDING_DEVICE},
                encode_kwargs={"normalize_embeddings": True}
            )
            print(" Embedding 模型加载完成")
        return self.embedding_model
    
    def init_chroma(self):
        """初始化 Chroma 向量数据库"""
        if Chroma is None:
            raise ImportError("langchain-chroma 未安装")
        if self.chroma_store is None:
            os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
            
            print(f" 正在初始化 Chroma 向量数据库: {settings.CHROMA_PERSIST_DIRECTORY}")
            self.chroma_store = Chroma(
                collection_name=settings.CHROMA_COLLECTION_NAME,
                embedding_function=self.init_embedding_model(),
                persist_directory=settings.CHROMA_PERSIST_DIRECTORY,
            )
            print(" Chroma 向量数据库初始化完成")
        return self.chroma_store
    
    def init_faiss(self):
        """初始化 FAISS 向量数据库（作为备选）"""
        if FAISS is None:
            raise ImportError("langchain-community 未安装")
        if self.faiss_store is None:
            faiss_path = settings.FAISS_INDEX_PATH
            
            if os.path.exists(faiss_path):
                print(f" 正在加载 FAISS 索引: {faiss_path}")
                self.faiss_store = FAISS.load_local(
                    faiss_path,
                    self.init_embedding_model(),
                    allow_dangerous_deserialization=True
                )
                print(" FAISS 索引加载完成")
            else:
                print(f"️ FAISS 索引不存在，将在首次添加文档时创建: {faiss_path}")
        return self.faiss_store
    
    def add_documents_to_chroma(self, documents: List[Any], metadatas: List[Dict] = None):
        """向 Chroma 添加文档"""
        store = self.init_chroma()
        
        if metadatas:
            for i, doc in enumerate(documents):
                if isinstance(doc, str):
                    doc.metadata = metadatas[i]
        
        store.add_documents(documents)
        print(f" 已向 Chroma 添加 {len(documents)} 个文档片段")
        
    def add_documents_to_faiss(self, texts: List[str], metadatas: List[Dict] = None):
        """向 FAISS 添加文档"""
        if self.faiss_store is None:
            self.faiss_store = FAISS.from_texts(
                texts,
                self.init_embedding_model(),
                metadatas=metadatas
            )
            os.makedirs(settings.FAISS_INDEX_PATH, exist_ok=True)
            self.faiss_store.save_local(settings.FAISS_INDEX_PATH)
        else:
            self.faiss_store.add_texts(texts, metadatas=metadatas)
            self.faiss_store.save_local(settings.FAISS_INDEX_PATH)
        
        print(f" 已向 FAISS 添加 {len(texts)} 个文档片段")
    
    def search_chroma(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """在 Chroma 中搜索相似文档"""
        store = self.init_chroma()
        results = store.similarity_search_with_score(query, k=k)
        
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score)
            })
        return formatted_results
    
    def search_faiss(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """在 FAISS 中搜索相似文档"""
        if self.faiss_store is None:
            return []
        
        results = self.faiss_store.similarity_search_with_score(query, k=k)
        
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score)
            })
        return formatted_results
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """获取向量库统计信息"""
        stats = {
            "chroma": {"document_count": 0},
            "faiss": {"document_count": 0}
        }
        
        if self.chroma_store:
            stats["chroma"]["document_count"] = self.chroma_store._collection.count()
        
        if self.faiss_store:
            stats["faiss"]["document_count"] = self.faiss_store.index.ntotal
            
        return stats


# 全局向量数据库管理器实例
vector_store_manager = VectorStoreManager()


async def init_vector_store():
    """初始化向量数据库（在应用启动时调用）"""
    # 检查是否使用简化版向量存储（避免下载 HuggingFace 模型）
    from app.core.config import settings
    if settings.USE_SIMPLE_VECTOR:
        print("ℹ️ 使用简化版向量存储（跳过 HuggingFace 模型下载）")
        print("   如需使用完整版向量数据库，请设置 USE_SIMPLE_VECTOR=false")
        return

    try:
        vector_store_manager.init_embedding_model()
        vector_store_manager.init_chroma()
        vector_store_manager.init_faiss()
        print(" 向量数据库初始化完成")
    except Exception as e:
        print(f" 向量数据库初始化失败: {e}")
        raise
