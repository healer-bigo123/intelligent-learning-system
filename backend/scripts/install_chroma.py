#!/usr/bin/env python3
"""
Chroma 向量数据库安装脚本
一键安装所有向量数据库相关依赖
"""
import subprocess
import sys
import importlib


def check_module(module_name, package_name=None):
    """检查模块是否已安装"""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False


def install_package(package):
    """安装单个包"""
    print(f"📦 正在安装 {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"  ✅ {package} 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ {package} 安装失败: {e}")
        return False


def main():
    print("=" * 60)
    print("🔧 Chroma 向量数据库安装工具")
    print("=" * 60)

    # 定义需要安装的包
    packages = [
        ("chromadb", "chromadb"),
        ("langchain_chroma", "langchain-chroma"),
        ("langchain_huggingface", "langchain-huggingface"),
        ("sentence_transformers", "sentence-transformers"),
        ("langchain_community", "langchain-community"),
        ("langchain_text_splitters", "langchain-text-splitters"),
        ("websockets", "websockets"),  # 讯飞星火流式需要
    ]

    print("\n📋 需要安装的包：")
    for module, package in packages:
        status = "✅ 已安装" if check_module(module) else "❌ 未安装"
        print(f"  {status} {package}")

    print("\n" + "=" * 60)
    print("🚀 开始安装...")
    print("=" * 60)

    # 使用清华镜像加速
    mirror = "-i https://pypi.tuna.tsinghua.edu.cn/simple"

    success_count = 0
    fail_count = 0

    for module, package in packages:
        if check_module(module):
            print(f"\n⏭️  {package} 已安装，跳过")
            success_count += 1
            continue

        # 尝试安装
        print(f"\n📦 正在安装 {package}...")
        try:
            cmd = [sys.executable, "-m", "pip", "install", package]
            # 添加镜像
            cmd.extend(["-i", "https://pypi.tuna.tsinghua.edu.cn/simple"])

            subprocess.check_call(cmd)
            print(f"  ✅ {package} 安装成功")
            success_count += 1
        except subprocess.CalledProcessError:
            print(f"  ❌ {package} 安装失败")
            fail_count += 1

    print("\n" + "=" * 60)
    print("📊 安装结果汇总")
    print("=" * 60)
    print(f"  成功: {success_count}/{len(packages)}")
    print(f"  失败: {fail_count}/{len(packages)}")

    if fail_count == 0:
        print("\n🎉 所有依赖安装完成！")
        print("\n请重启后端服务以启用向量数据库：")
        print("  python main.py")
    else:
        print("\n⚠️ 部分依赖安装失败，请检查网络连接或手动安装")

    input("\n按回车键退出...")


if __name__ == "__main__":
    main()
