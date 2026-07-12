"""
简化版向量存储 - 不依赖外部模型下载，用于快速启动
使用 SQLite + 简单文本匹配作为备选方案
"""
import os
import json
import sqlite3
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.config import settings


class SimpleVectorStore:
    """简化版向量存储（基于 SQLite + 关键词匹配）"""

    def __init__(self, db_path: str = "./data/simple_vector.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建文档表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                source TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 尝试创建全文搜索虚拟表（某些 SQLite 编译版本不支持 FTS5）
        try:
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
                    content, source, metadata,
                    content='documents',
                    content_rowid='id'
                )
            """)

            # 创建触发器保持同步
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS documents_ai AFTER INSERT ON documents BEGIN
                    INSERT INTO documents_fts(rowid, content, source, metadata)
                    VALUES (new.id, new.content, new.source, new.metadata);
                END
            """)

            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS documents_ad AFTER DELETE ON documents BEGIN
                    INSERT INTO documents_fts(documents_fts, rowid, content, source, metadata)
                    VALUES ('delete', old.id, old.content, old.source, old.metadata);
                END
            """)
        except sqlite3.OperationalError:
            # FTS5 不可用，跳过
            pass

        conn.commit()
        conn.close()

    def _extract_keywords(self, text: str) -> List[str]:
        """提取中文关键词（简单分词）"""
        # 去除标点，保留中文字符和英文单词
        words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', text.lower())

        # 停用词列表
        stopwords = {'的', '了', '是', '在', '我', '有', '和', '就', '不', '人',
                     '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去',
                     '你', '会', '着', '没有', '看', '好', '自己', '这', '什么',
                     '怎么', '哪些', '吗', '呢', '吧', '啊', '哦', '嗯'}

        result = []
        for w in words:
            # 英文单词直接保留（长度>1）
            if re.match(r'^[a-zA-Z]+$', w):
                if len(w) > 1:
                    result.append(w)
                continue

            # 中文处理
            if len(w) == 1:
                # 单字如果是停用词则跳过
                if w not in stopwords:
                    result.append(w)
            elif len(w) == 2:
                # 双字词：检查是否全是停用词组合
                if w not in stopwords:
                    result.append(w)
            else:
                # 三字及以上：保留完整词，同时提取子词
                result.append(w)
                # 也提取其中的二字词（滑动窗口）
                for i in range(len(w) - 1):
                    bigram = w[i:i+2]
                    if bigram not in stopwords:
                        result.append(bigram)

        return result

    def _calculate_similarity(self, query: str, content: str) -> float:
        """计算查询与内容的相关性分数"""
        query_keywords = self._extract_keywords(query)
        content_keywords = self._extract_keywords(content)

        if not query_keywords:
            return 0.0

        query_set = set(query_keywords)
        content_set = set(content_keywords)

        # 计算 Jaccard 相似度
        intersection = query_set & content_set
        union = query_set | content_set

        if not union:
            return 0.0

        jaccard = len(intersection) / len(union)

        # 额外加分：查询中的长词（>=3字）被完整匹配
        bonus = 0.0
        for qw in query_keywords:
            if len(qw) >= 3 and qw in content:
                bonus += 0.1  # 每个长词匹配加 0.1

        # 额外加分：关键词出现频率
        freq_score = 0.0
        for qk in query_keywords:
            freq = content_keywords.count(qk)
            if freq > 0:
                freq_score += min(freq * 0.05, 0.15)  # 每个关键词最多加 0.15

        return min(jaccard + bonus + freq_score, 1.0)

    def add_document(self, content: str, source: str = "", metadata: Dict = None):
        """添加文档"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO documents (content, source, metadata) VALUES (?, ?, ?)",
            (content, source, json.dumps(metadata or {}))
        )
        conn.commit()
        doc_id = cursor.lastrowid
        conn.close()
        return doc_id

    # 兼容 vector_store_manager 的接口
    def add_documents_to_chroma(self, documents):
        """兼容接口：添加文档"""
        for doc in documents:
            content = getattr(doc, 'page_content', str(doc))
            metadata = getattr(doc, 'metadata', {})
            source = metadata.get('source', '')
            self.add_document(content, source, metadata)
        print(f" 已向简化版向量库添加 {len(documents)} 个文档片段")

    def search_chroma(self, query: str, k: int = 5):
        """兼容接口：搜索文档"""
        return self.search(query, k)

    def search_faiss(self, query: str, k: int = 5):
        """兼容接口：搜索文档"""
        return self.search(query, k)

    def get_collection_stats(self):
        """兼容接口：获取统计"""
        return self.get_stats()

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """搜索文档（关键词匹配 + 相关性排序）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 先尝试 FTS5 全文搜索
        try:
            cursor.execute("""
                SELECT d.id, d.content, d.source, d.metadata
                FROM documents_fts fts
                JOIN documents d ON fts.rowid = d.id
                WHERE documents_fts MATCH ?
                LIMIT ?
            """, (query, k * 3))  # 多取一些用于重排序

            rows = cursor.fetchall()
            if rows:
                results = []
                for row in rows:
                    content = row[1]
                    score = self._calculate_similarity(query, content)
                    results.append({
                        "id": row[0],
                        "content": content,
                        "source": row[2],
                        "metadata": json.loads(row[3] or "{}"),
                        "score": score
                    })
                # 按相关性排序
                results.sort(key=lambda x: x["score"], reverse=True)
                conn.close()
                return results[:k]
        except sqlite3.OperationalError:
            pass

        # FTS5 不可用或没有结果，回退到全表扫描 + 关键词匹配
        cursor.execute("SELECT id, content, source, metadata FROM documents")
        all_docs = cursor.fetchall()
        conn.close()

        # 计算每篇文档的相关性
        scored_results = []
        for row in all_docs:
            content = row[1]
            score = self._calculate_similarity(query, content)
            if score > 0:  # 只返回相关的文档
                scored_results.append({
                    "id": row[0],
                    "content": content,
                    "source": row[2],
                    "metadata": json.loads(row[3] or "{}"),
                    "score": score
                })

        # 按相关性排序，取前 k 个
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        return scored_results[:k]

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM documents")
        count = cursor.fetchone()[0]
        conn.close()
        return {"document_count": count}


# 全局实例
simple_vector_store = SimpleVectorStore()
