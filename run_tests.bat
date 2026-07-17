@echo off
chcp 65001 >nul
echo ==========================================
echo   智能学习系统 - 测试验证脚本
echo ==========================================
echo.

REM 检查虚拟环境
if not exist "backend\venv\Scripts\activate.bat" (
    echo [错误] 未找到虚拟环境，请先运行 backend\setup_env.ps1 创建环境
    pause
    exit /b 1
)

echo [1/4] 激活虚拟环境...
call backend\venv\Scripts\activate.bat
if errorlevel 1 (
    echo [错误] 激活虚拟环境失败
    pause
    exit /b 1
)

echo [2/4] 检查数据库...
if not exist "backend\data\smart_learning.db" (
    echo [提示] 数据库不存在，正在初始化...
    cd backend
    python init_data.py
    cd ..
    if errorlevel 1 (
        echo [错误] 数据库初始化失败
        pause
        exit /b 1
    )
)

echo [3/4] 运行成就系统测试...
cd backend
python -m pytest tests\test_achievements.py -v --tb=short
if errorlevel 1 (
    echo.
    echo [警告] 成就系统测试未通过，请检查上方错误信息
) else (
    echo.
    echo [成功] 成就系统测试全部通过
)

echo.
echo [4/4] 运行课堂系统测试...
python -m pytest tests\test_classroom.py -v --tb=short
if errorlevel 1 (
    echo.
    echo [警告] 课堂系统测试未通过，请检查上方错误信息
) else (
    echo.
    echo [成功] 课堂系统测试全部通过
)

cd ..
echo.
echo ==========================================
echo   测试完成
echo ==========================================
pause
