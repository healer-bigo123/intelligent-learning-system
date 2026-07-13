"""
知识库管理模块 - 负责文档加载、分块、向量化和检索增强生成(RAG)
"""
import os
from typing import List, Dict, Any, Optional

# 文档加载器 - 带容错处理
try:
    from langchain_community.document_loaders import TextLoader, PyPDFLoader, UnstructuredMarkdownLoader
except ImportError:
    TextLoader = None
    PyPDFLoader = None
    UnstructuredMarkdownLoader = None

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    RecursiveCharacterTextSplitter = None

try:
    from langchain_core.documents import Document
except ImportError:
    Document = None

from app.core.config import settings

# 向量存储管理器 - 延迟初始化
vector_store_manager = None
VECTOR_STORE_AVAILABLE = False

def _get_vector_store():
    """获取向量存储管理器（延迟加载）"""
    global vector_store_manager, VECTOR_STORE_AVAILABLE
    if vector_store_manager is None:
        try:
            from app.core.vector_store import vector_store_manager as vsm
            vector_store_manager = vsm
            VECTOR_STORE_AVAILABLE = True
        except ImportError:
            from app.core.simple_vector_store import simple_vector_store as vsm
            vector_store_manager = vsm
            VECTOR_STORE_AVAILABLE = False
    return vector_store_manager


class KnowledgeBaseManager:
    """知识库管理器"""

    def __init__(self):
        if RecursiveCharacterTextSplitter is None:
            print("[WARN] langchain_text_splitters 未安装，知识库功能将不可用")
            self.text_splitter = None
        else:
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                length_function=len,
                separators=["\n\n", "\n", "。", "；", " ", ""]
            )

        self.supported_extensions = {}
        if TextLoader:
            self.supported_extensions[".txt"] = TextLoader
        if UnstructuredMarkdownLoader:
            self.supported_extensions[".md"] = UnstructuredMarkdownLoader
        if PyPDFLoader:
            self.supported_extensions[".pdf"] = PyPDFLoader
    
    def load_document(self, file_path: str) -> List[Any]:
        """加载单个文档"""
        if Document is None:
            raise ImportError("langchain_core 未安装，无法加载文档")

        ext = os.path.splitext(file_path)[1].lower()

        if ext not in self.supported_extensions:
            raise ValueError(f"不支持的文件格式: {ext}，支持的格式: {list(self.supported_extensions.keys())}")

        # .txt 文件直接读取，避免 LangChain TextLoader 在 Windows 中文路径下的兼容性问题
        if ext == ".txt":
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                documents = [Document(
                    page_content=content,
                    metadata={
                        "source": file_path,
                        "file_type": ext,
                        "file_name": os.path.basename(file_path),
                    }
                )]
                return documents
            except Exception as e:
                raise RuntimeError(f"读取文件失败 ({file_path}): {str(e)}")

        loader_class = self.supported_extensions[ext]
        loader = loader_class(file_path)
        documents = loader.load()

        # 添加文件元数据
        for doc in documents:
            doc.metadata.update({
                "source": file_path,
                "file_type": ext,
                "file_name": os.path.basename(file_path),
            })

        return documents
    
    def load_directory(self, directory_path: str) -> List[Document]:
        """加载目录中的所有支持文档"""
        all_documents = []
        
        for root, _, files in os.walk(directory_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in self.supported_extensions:
                    file_path = os.path.join(root, file)
                    try:
                        docs = self.load_document(file_path)
                        all_documents.extend(docs)
                        print(f" 已加载文档: {file_path}")
                    except Exception as e:
                        print(f" 加载文档失败 {file_path}: {e}")
        
        return all_documents
    
    def split_documents(self, documents: List[Any]) -> List[Any]:
        """将文档分块"""
        if self.text_splitter is None:
            raise ImportError("文本分割器未初始化")
        chunks = self.text_splitter.split_documents(documents)
        print(f" 文档分块完成: {len(documents)} 个文档 → {len(chunks)} 个片段")
        return chunks
    
    def add_to_knowledge_base(self, documents: List[Any], store_type: str = "chroma"):
        """将文档添加到知识库"""
        chunks = self.split_documents(documents)
        vsm = _get_vector_store()

        if store_type == "chroma":
            vsm.add_documents_to_chroma(chunks)
        elif store_type == "faiss":
            texts = [chunk.page_content for chunk in chunks]
            metadatas = [chunk.metadata for chunk in chunks]
            vsm.add_documents_to_faiss(texts, metadatas)
        else:
            raise ValueError(f"不支持的存储类型: {store_type}")
    
    def search_knowledge_base(self, query: str, k: int = 5, store_type: str = "chroma") -> List[Dict[str, Any]]:
        """在知识库中搜索"""
        vsm = _get_vector_store()
        if store_type == "chroma":
            return vsm.search_chroma(query, k)
        elif store_type == "faiss":
            return vsm.search_faiss(query, k)
        else:
            raise ValueError(f"不支持的存储类型: {store_type}")
    
    def get_context_for_rag(self, query: str, k: int = 5) -> str:
        """获取 RAG 所需的上下文文本"""
        results = self.search_knowledge_base(query, k)
        
        if not results:
            return ""
        
        context_parts = []
        for i, result in enumerate(results, 1):
            source = result["metadata"].get("source", "未知来源")
            content = result["content"]
            context_parts.append(f"[参考{i}] 来源: {source}\n{content}\n")
        
        return "\n".join(context_parts)


# 全局知识库管理器实例
knowledge_base_manager = KnowledgeBaseManager()


async def init_knowledge_base():
    """初始化知识库（在应用启动时调用）"""
    from app.core.config import settings
    # 如果使用简化版向量存储，跳过复杂的知识库初始化
    use_simple = settings.USE_SIMPLE_VECTOR

    try:
        kb_dir = settings.KNOWLEDGE_BASE_DIR

        if not os.path.exists(kb_dir):
            os.makedirs(kb_dir, exist_ok=True)
            print(f" 创建知识库目录: {kb_dir}")
            print(" 请将课程文档（.txt, .md, .pdf）放入该目录，系统将自动加载")
            return

        # 检查 langchain 依赖是否可用
        if not knowledge_base_manager.supported_extensions:
            print("️ 文档加载器未安装，跳过知识库初始化")
            print("   如需使用知识库，请运行: pip install langchain-community langchain-text-splitters")
            return

        # 检查目录中是否有文档
        has_docs = any(
            f.endswith(tuple(knowledge_base_manager.supported_extensions.keys()))
            for _, _, files in os.walk(kb_dir)
            for f in files
        )

        if not has_docs:
            print(f" 知识库目录为空: {kb_dir}")
            print(" 请将课程文档（.txt, .md, .pdf）放入该目录")
            return

        # 如果使用简化版，只加载文档到 SQLite，不进行向量化
        if use_simple:
            print(f" 正在加载知识库文档到简化版存储...")
            documents = knowledge_base_manager.load_directory(kb_dir)
            if documents:
                # 直接添加到简化版向量存储（不进行分块）
                vsm = _get_vector_store()
                vsm.add_documents_to_chroma(documents)
                print(f" 知识库初始化完成（简化版），共索引 {len(documents)} 个文档")
            return

        # 完整版：加载并索引文档
        print(f" 正在加载知识库文档...")
        documents = knowledge_base_manager.load_directory(kb_dir)

        if documents:
            knowledge_base_manager.add_to_knowledge_base(documents)
            print(f" 知识库初始化完成，共索引 {len(documents)} 个文档")
        else:
            print("️ 未能加载任何文档")

    except Exception as e:
        print(f" 知识库初始化失败: {e}")
        raise
