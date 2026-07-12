"""
环境检查、安装、测试一体化脚本
运行: python check_and_setup.py
"""
import subprocess
import sys
import os

def run_cmd(cmd, cwd=None):
    """运行命令并返回输出"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, cwd=cwd, timeout=60
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def check_python():
    """检查 Python 是否可用"""
    print("=" * 50)
    print("🔍 检查 Python 环境")
    print("=" * 50)
    
    # 尝试找 python
    for py_cmd in ["python", "python3", "py"]:
        code, out, err = run_cmd(f"{py_cmd} --version")
        if code == 0:
            print(f"  ✅ 找到 Python: {out.strip()}")
            return py_cmd
    
    # 尝试常见路径
    common_paths = [
        r"C:\Users\admin\AppData\Local\Programs\Python\Python311\python.exe",
        r"C:\Users\admin\AppData\Local\Programs\Python\Python310\python.exe",
        r"C:\Program Files\Python311\python.exe",
        r"C:\Program Files\Python310\python.exe",
        r"D:\Python311\python.exe",
        r"D:\Python\python.exe",
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            code, out, err = run_cmd(f'"{path}" --version')
            if code == 0:
                print(f"  ✅ 找到 Python: {out.strip()} ({path})")
                return path
    
    print("  ❌ 未找到 Python，请先安装 Python 3.10+")
    print("     下载地址: https://www.python.org/downloads/")
    return None

def check_pip(python_cmd):
    """检查 pip 是否可用"""
    print("\n🔍 检查 pip")
    code, out, err = run_cmd(f'"{python_cmd}" -m pip --version')
    if code == 0:
        print(f"  ✅ pip: {out.strip()}")
        return True
    print("  ❌ pip 不可用")
    return False

def install_deps(python_cmd):
    """安装依赖"""
    print("\n" + "=" * 50)
    print("📥 安装核心依赖")
    print("=" * 50)
    
    deps = [
        "fastapi", "uvicorn", "pydantic", "pydantic-settings",
        "httpx", "sqlalchemy", "python-dotenv"
    ]
    
    for dep in deps:
        print(f"\n  安装 {dep}...")
        code, out, err = run_cmd(
            f'"{python_cmd}" -m pip install {dep} -i https://pypi.tuna.tsinghua.edu.cn/simple',
            cwd=r"C:\Users\admin\Desktop\plan\backend"
        )
        if code == 0:
            print(f"    ✅ {dep} 安装成功")
        else:
            print(f"    ❌ {dep} 安装失败: {err[:100]}")

def verify_deps(python_cmd):
    """验证依赖安装"""
    print("\n" + "=" * 50)
    print("🔍 验证依赖安装")
    print("=" * 50)
    
    deps = {
        "fastapi": "fastapi",
        "uvicorn": "uvicorn",
        "pydantic": "pydantic",
        "httpx": "httpx",
        "sqlalchemy": "sqlalchemy",
        "dotenv": "dotenv",
    }
    
    all_ok = True
    for name, module in deps.items():
        code, out, err = run_cmd(f'"{python_cmd}" -c "import {module}; print(\'OK\')"')
        if code == 0 and "OK" in out:
            print(f"  ✅ {name}")
        else:
            print(f"  ❌ {name}")
            all_ok = False
    
    return all_ok

def test_llm_api(python_cmd):
    """测试大模型 API"""
    print("\n" + "=" * 50)
    print("🧪 测试大模型 API 连通性")
    print("=" * 50)
    
    backend_dir = r"C:\Users\admin\Desktop\plan\backend"
    test_script = os.path.join(backend_dir, "test_llm.py")
    
    if not os.path.exists(test_script):
        print(f"  ❌ 测试脚本不存在: {test_script}")
        return False
    
    print("  运行测试脚本...")
    code, out, err = run_cmd(f'"{python_cmd}" "{test_script}"', cwd=backend_dir)
    
    print(out)
    if err:
        print(f"  错误输出: {err}")
    
    return code == 0

def main():
    print("🚀 SmartLearning-MAS 环境检查与配置")
    
    # 1. 找 Python
    python_cmd = check_python()
    if not python_cmd:
        print("\n❌ 请先安装 Python 3.10+")
        input("按回车键退出...")
        return
    
    # 2. 检查 pip
    if not check_pip(python_cmd):
        print("\n❌ pip 不可用")
        input("按回车键退出...")
        return
    
    # 3. 安装依赖
    install_deps(python_cmd)
    
    # 4. 验证依赖
    deps_ok = verify_deps(python_cmd)
    if not deps_ok:
        print("\n⚠️ 部分依赖安装失败，请检查网络连接")
        input("按回车键退出...")
        return
    
    # 5. 测试大模型 API
    print("\n✅ 核心依赖安装完成！")
    print("\n是否要测试大模型 API？(y/n)")
    choice = input().strip().lower()
    if choice == 'y':
        test_llm_api(python_cmd)
    
    print("\n🎉 配置完成！")
    print(f"\n启动后端服务:")
    print(f'  cd C:\\Users\\admin\\Desktop\\plan\\backend')
    print(f'  "{python_cmd}" main.py')
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
