"""
环境检查脚本 - 检查 Python 依赖是否齐全
运行: python check_env.py
"""
import sys


def check_module(name, import_name=None):
    """检查模块是否可导入"""
    import_name = import_name or name
    try:
        __import__(import_name)
        print(f"  ✅ {name}")
        return True
    except ImportError as e:
        print(f"  ❌ {name}")
        return False


print("=" * 50)
print("🔍 Python 环境依赖检查")
print("=" * 50)

# 核心依赖（必须）
required_deps = [
    ("fastapi", "fastapi"),
    ("uvicorn", "uvicorn"),
    ("pydantic", "pydantic"),
    ("pydantic-settings", "pydantic_settings"),
    ("httpx", "httpx"),
    ("sqlalchemy", "sqlalchemy"),
    ("python-dotenv", "dotenv"),
]

# 可选依赖
optional_deps = [
    ("chromadb", "chromadb"),
    ("faiss-cpu", "faiss"),
    ("sentence-transformers", "sentence_transformers"),
    ("langchain", "langchain"),
    ("langchain-community", "langchain_community"),
    ("langchain-chroma", "langchain_chroma"),
    ("langchain-huggingface", "langchain_huggingface"),
    ("langchain-text-splitters", "langchain_text_splitters"),
    ("alembic", "alembic"),
    ("numpy", "numpy"),
    ("pandas", "pandas"),
]

print("\n📦 核心依赖（必须）")
total_ok = 0
total_fail = 0
for name, import_name in required_deps:
    if check_module(name, import_name):
        total_ok += 1
    else:
        total_fail += 1

print("\n📦 可选依赖（向量数据库/RAG）")
optional_ok = 0
optional_fail = 0
for name, import_name in optional_deps:
    if check_module(name, import_name):
        optional_ok += 1
    else:
        optional_fail += 1

print("\n" + "=" * 50)
print("📊 检查结果汇总")
print("=" * 50)
print(f"  核心依赖: {total_ok}/{len(required_deps)} 通过")
if optional_fail > 0:
    print(f"  可选依赖: {optional_ok}/{len(optional_deps)} 通过 ({optional_fail} 个缺失)")
else:
    print(f"  可选依赖: {optional_ok}/{len(optional_deps)} 通过")

if total_fail > 0:
    print("\n❌ 核心依赖缺失，请运行:")
    print("  pip install fastapi uvicorn pydantic pydantic-settings httpx sqlalchemy python-dotenv")
    sys.exit(1)
else:
    print("\n🎉 核心依赖全部通过！")
    if optional_fail > 0:
        print("\n💡 可选依赖缺失，如需完整功能请运行:")
        print("  pip install -r requirements.txt")
    sys.exit(0)
