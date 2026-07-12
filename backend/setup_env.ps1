# 基于大模型的个性化资源生成与学习多智能体系统 - 环境安装脚本
# 运行方式: 右键 -> 使用 PowerShell 运行

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SmartLearning-MAS 环境安装脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Python
Write-Host "🔍 检查 Python 版本..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python 未安装或未添加到 PATH" -ForegroundColor Red
    Write-Host "   请从 https://www.python.org/downloads/ 下载安装 Python 3.11+" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "  ✅ $pythonVersion" -ForegroundColor Green

# 检查 pip
Write-Host "🔍 检查 pip..." -ForegroundColor Yellow
$pipVersion = pip --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ pip 未安装" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "  ✅ pip 已安装" -ForegroundColor Green

# 创建虚拟环境
Write-Host ""
Write-Host "📦 创建虚拟环境..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "  ⚠️ 虚拟环境已存在，跳过创建" -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "  ✅ 虚拟环境创建完成" -ForegroundColor Green
}

# 激活虚拟环境
Write-Host ""
Write-Host "🚀 激活虚拟环境..." -ForegroundColor Yellow
$venvPython = ".\venv\Scripts\python.exe"
$venvPip = ".\venv\Scripts\pip.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "❌ 虚拟环境创建失败" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "  ✅ 虚拟环境已激活" -ForegroundColor Green

# 升级 pip
Write-Host ""
Write-Host "⬆️  升级 pip..." -ForegroundColor Yellow
& $venvPip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
Write-Host "  ✅ pip 升级完成" -ForegroundColor Green

# 安装核心依赖
Write-Host ""
Write-Host "📥 安装核心依赖..." -ForegroundColor Yellow
& $venvPip install fastapi uvicorn pydantic pydantic-settings httpx sqlalchemy python-dotenv -i https://pypi.tuna.tsinghua.edu.cn/simple
Write-Host "  ✅ 核心依赖安装完成" -ForegroundColor Green

# 安装向量数据库依赖
Write-Host ""
Write-Host "📥 安装向量数据库依赖 (Chroma + FAISS)..." -ForegroundColor Yellow
& $venvPip install chromadb faiss-cpu sentence-transformers -i https://pypi.tuna.tsinghua.edu.cn/simple
Write-Host "  ✅ 向量数据库依赖安装完成" -ForegroundColor Green

# 安装 LangChain 生态
Write-Host ""
Write-Host "📥 安装 LangChain 生态..." -ForegroundColor Yellow
& $venvPip install langchain langchain-community langchain-chroma langchain-huggingface langchain-text-splitters -i https://pypi.tuna.tsinghua.edu.cn/simple
Write-Host "  ✅ LangChain 生态安装完成" -ForegroundColor Green

# 安装其他工具库
Write-Host ""
Write-Host "📥 安装其他工具库..." -ForegroundColor Yellow
& $venvPip install numpy pandas pyyaml requests -i https://pypi.tuna.tsinghua.edu.cn/simple
Write-Host "  ✅ 工具库安装完成" -ForegroundColor Green

# 验证安装
Write-Host ""
Write-Host "🔍 验证安装..." -ForegroundColor Yellow
& $venvPython check_env.py

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  安装完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步操作:" -ForegroundColor Yellow
Write-Host "  1. 测试大模型 API: .\venv\Scripts\python.exe test_llm.py" -ForegroundColor White
Write-Host "  2. 启动后端服务: .\venv\Scripts\python.exe main.py" -ForegroundColor White
Write-Host ""

pause
