@echo off
chcp 65001 >nul
title 后端API服务器 - localhost:5000
color 0E

echo.
echo =========================================
echo     🔧 启动后端API服务器
echo =========================================
echo.

:: 进入后端目录
cd /d "%~dp0emotion_recognition_api"

:: 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装，请先安装Python 3.8-3.11
    pause
    exit /b 1
)

echo ✅ Python环境检查通过
echo.

:: 安装依赖
echo 📦 安装Python依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

echo ✅ 依赖安装成功
echo.

:: 启动API服务
echo 🚀 启动API服务器...
echo 📍 服务地址: http://localhost:5000
echo 🔍 健康检查: http://localhost:5000/api/health
echo.
echo 按 Ctrl+C 停止服务
echo.

python start_api.py

echo.
echo 👋 服务已停止
pause 