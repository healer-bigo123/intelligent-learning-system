#!/usr/bin/env python3
"""
简化版向量存储测试脚本
无需下载 HuggingFace 模型，纯本地运行
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.simple_vector_store import simple_vector_store


def test_add_documents():
    """测试添加文档"""
    print("=" * 60)
    print("📝 测试添加文档")
    print("=" * 60)

    # 模拟文档数据
    class MockDoc:
        def __init__(self, content, metadata):
            self.page_content = content
            self.metadata = metadata

    docs = [
        MockDoc("Python 是一种流行的编程语言，广泛应用于数据分析、人工智能和 Web 开发", {"source": "python_intro.md"}),
        MockDoc("机器学习是人工智能的一个分支，通过数据训练模型来实现预测和分类", {"source": "ml_basics.md"}),
        MockDoc("深度学习使用神经网络进行学习，在图像识别和自然语言处理领域表现出色", {"source": "deep_learning.md"}),
        MockDoc("FastAPI 是一个现代、快速的 Python Web 框架，基于 Starlette 和 Pydantic", {"source": "fastapi_doc.md"}),
        MockDoc("SQLite 是一个轻量级的关系型数据库，无需服务器即可运行", {"source": "sqlite_guide.md"}),
    ]

    simple_vector_store.add_documents_to_chroma(docs)

    stats = simple_vector_store.get_stats()
    print(f"\n📊 当前文档总数: {stats['document_count']}")
    return True


def test_search():
    """测试搜索功能"""
    print("\n" + "=" * 60)
    print("🔍 测试语义搜索")
    print("=" * 60)

    queries = [
        "什么是人工智能",
        "Python 能做什么",
        "数据库有哪些",
        "神经网络",
    ]

    for query in queries:
        print(f"\n🎯 查询: '{query}'")
        results = simple_vector_store.search(query, k=2)

        if results:
            for i, result in enumerate(results, 1):
                print(f"   结果 {i} (相关度: {result['score']:.2f}):")
                print(f"   {result['content'][:60]}...")
        else:
            print("   ⚠️ 未找到相关结果")

    return True


def test_stats():
    """测试统计信息"""
    print("\n" + "=" * 60)
    print("📈 测试统计信息")
    print("=" * 60)

    stats = simple_vector_store.get_collection_stats()
    print(f"  文档总数: {stats.get('document_count', 0)}")
    return True


def main():
    print("\n" + "=" * 60)
    print("🚀 简化版向量存储测试")
    print("=" * 60)
    print("\n✅ 此测试无需下载 HuggingFace 模型，纯本地运行")

    try:
        # 清空旧数据（可选）
        # simple_vector_store.clear()

        test_add_documents()
        test_search()
        test_stats()

        print("\n" + "=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60)
        print("\n简化版向量存储已就绪，可以：")
        print("  1. 上传文档到知识库")
        print("  2. 进行关键词检索")
        print("  3. 重启后端服务: python main.py")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

    input("\n按回车键退出...")


if __name__ == "__main__":
    main()
