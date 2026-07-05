#!/usr/bin/env python3
"""
设置 HuggingFace 国内镜像
解决模型下载网络问题
"""
import os


def setup_mirror():
    """设置 HuggingFace 镜像源"""
    print("=" * 60)
    print("🔧 设置 HuggingFace 国内镜像")
    print("=" * 60)

    # 方法1：环境变量（当前终端有效）
    os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
    print("\n✅ 已设置环境变量 HF_ENDPOINT=https://hf-mirror.com")

    # 方法2：写入 .env 文件（持久化）
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            content = f.read()

        if "HF_ENDPOINT" not in content:
            with open(env_path, "a", encoding="utf-8") as f:
                f.write("\n# HuggingFace 国内镜像\nHF_ENDPOINT=https://hf-mirror.com\n")
            print("✅ 已写入 .env 文件")
        else:
            print("⏭️ .env 中已存在 HF_ENDPOINT 配置")
    else:
        print("⚠️ 未找到 .env 文件")

    # 方法3：创建 huggingface 缓存目录
    cache_dir = os.path.expanduser("~/.cache/huggingface")
    os.makedirs(cache_dir, exist_ok=True)
    print(f"✅ 缓存目录: {cache_dir}")

    print("\n" + "=" * 60)
    print("🎉 镜像设置完成！")
    print("=" * 60)
    print("\n现在可以重新运行测试脚本：")
    print("  python test_chroma.py")
    print("\n或者手动下载模型后放到缓存目录：")
    print("  https://hf-mirror.com/BAAI/bge-large-zh-v1.5")


if __name__ == "__main__":
    setup_mirror()
    input("\n按回车键退出...")
