"""
快速检查核心依赖是否安装
"""
import sys

deps = ["fastapi", "uvicorn", "pydantic", "httpx"]
all_ok = True

for dep in deps:
    try:
        mod = __import__(dep)
        ver = getattr(mod, "__version__", "unknown")
        print(f"OK: {dep}=={ver}")
    except ImportError:
        print(f"MISSING: {dep}")
        all_ok = False

sys.exit(0 if all_ok else 1)
