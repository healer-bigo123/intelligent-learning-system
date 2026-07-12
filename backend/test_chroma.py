#!/usr/bin/env python3
"""
Chroma 向量数据库测试脚本
安装完成后运行此脚本验证向量数据库是否正常工作
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings


def test_imports():
    """测试所有依赖是否能正常导入"""
    print("=" * 60)
    print("🔍 测试依赖导入")
    print("=" * 60)

    modules = [
        ("chromadb", "ChromaDB"),
        ("langchain_chroma", "LangChain-Chroma"),
        ("langchain_huggingface", "LangChain-HuggingFace"),
        ("sentence_transformers", "Sentence-Transformers"),
        ("langchain_community", "LangChain-Community"),
        ("langchain_text_splitters", "LangChain-Text-Splitters"),
    ]

    all_ok = True
    for module, name in modules:
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError as e:
            print(f"  ❌ {name}: {e}")
            all_ok = False

    return all_ok


async def test_vector_store():
    """测试向量数据库核心功能"""
    print("\n" + "=" * 60)
    print("🧪 测试向量数据库功能")
    print("=" * 60)

    try:
        from app.core.vector_store import vector_store_manager

        # 测试初始化
        print("\n1️⃣ 测试 Chroma 初始化...")
        chroma = vector_store_manager.init_chroma()
        print("  ✅ Chroma 初始化成功")

        # 测试 Embedding 模型
        print("\n2️⃣ 测试 Embedding 模型...")
        embedding_model = vector_store_manager.init_embedding_model()
        test_text = "这是一个测试句子"
        embedding = embedding_model.embed_query(test_text)
        print(f"  ✅ Embedding 生成成功，维度: {len(embedding)}")

        # 测试添加文档
        print("\n3️⃣ 测试添加文档...")
        from langchain_core.documents import Document
        docs = [
            Document(page_content="Python 是一种流行的编程语言", metadata={"source": "test1"}),
            Document(page_content="机器学习是人工智能的一个分支", metadata={"source": "test2"}),
            Document(page_content="深度学习使用神经网络进行学习", metadata={"source": "test3"}),
        ]
        vector_store_manager.add_documents_to_chroma(docs)
        print("  ✅ 文档添加成功")

        # 测试搜索
        print("\n4️⃣ 测试语义搜索...")
        results = vector_store_manager.search_chroma("什么是人工智能？", k=2)
        print(f"  ✅ 搜索完成，找到 {len(results)} 条结果")
        for i, result in enumerate(results, 1):
            print(f"     结果 {i}: {result['content'][:50]}...")

        # 测试统计
        print("\n5️⃣ 测试统计信息...")
        stats = vector_store_manager.get_collection_stats()
        print(f"  ✅ 集合文档数: {stats.get('count', 'N/A')}")

        print("\n" + "=" * 60)
        print("🎉 向量数据库测试全部通过！")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "=" * 60)
    print("🚀 Chroma 向量数据库测试工具")
    print("=" * 60)

    # 第一步：测试导入
    if not test_imports():
        print("\n⚠️ 部分依赖未安装，请先运行: python install_chroma.py")
        input("\n按回车键退出...")
        return

    # 第二步：测试功能
    success = asyncio.run(test_vector_store())

    if success:
        print("\n✨ 向量数据库已就绪，可以重启后端服务：")
        print("  python main.py")
    else:
        print("\n⚠️ 测试未通过，请检查错误信息")

    input("\n按回车键退出...")


if __name__ == "__main__":
    main()
