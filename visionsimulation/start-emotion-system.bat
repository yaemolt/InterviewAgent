@echo off
chcp 65001 >nul
title 智能情绪识别系统 - 一键启动
color 0A

echo.
echo =========================================
echo     🧠 智能情绪识别系统 - 一键启动
echo =========================================
echo.
echo 🚀 正在启动前端和后端服务...
echo.

:: 进入项目根目录
cd /d "%~dp0"

:: 检查必要的环境
echo 🔍 检查运行环境...

:: 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装，请先安装Python 3.8-3.11
    goto :error
)
echo ✅ Python环境检查通过

:: 检查Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js未安装，请先安装Node.js 16+
    goto :error
)
echo ✅ Node.js环境检查通过

echo.
echo 📦 准备启动服务...

:: 检查并安装后端依赖
echo 🔧 检查后端依赖...
cd emotion_recognition_api
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ 后端依赖安装可能有问题，但继续尝试启动...
) else (
    echo ✅ 后端依赖安装成功
)

:: 启动后端（在新窗口中）
echo 🔧 启动后端API服务器...
start "🔧 后端API服务器 - localhost:5000" cmd /k "python start_api.py"
cd ..

:: 等待8秒让后端先启动并加载模型
echo ⏳ 等待后端启动（8秒）...
timeout /t 8 /nobreak >nul

:: 检查后端是否启动成功
echo 🔍 检查后端连接...
curl -s http://localhost:5000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 后端服务启动成功
) else (
    echo ⚠️ 后端可能尚未完全启动，继续启动前端...
)

:: 启动前端（在新窗口中）
echo 🎨 启动前端Vue应用...
cd Frontend
start "🎨 前端Vue应用 - localhost:5175" cmd /k "npm install && npm run dev"
cd ..

:: 等待5秒
echo ⏳ 等待前端启动（5秒）...
timeout /t 5 /nobreak >nul

echo.
echo ✅ 系统启动完成！
echo.
echo 📌 服务信息:
echo    🎨 前端地址: http://localhost:5175
echo    🔧 后端地址: http://localhost:5000
echo    🔗 API代理:  /api -^> http://localhost:5000
echo.
echo 💡 使用说明:
echo    1. 等待两个服务器完全启动（约30-60秒）
echo    2. 在浏览器中访问: http://localhost:5175
echo    3. 允许摄像头权限
echo    4. 点击"开始识别"按钮
echo    5. 每秒自动发送8帧视频进行DAiSEE情绪分析
echo.
echo 🎯 支持的情绪维度:
echo    • 无聊 (Boredom)
echo    • 参与度 (Engagement) 
echo    • 困惑 (Confusion)
echo    • 挫折感 (Frustration)
echo.
echo 🔍 故障排除:
echo    • 如果前端无法连接API，检查后端窗口是否显示启动成功
echo    • 如果摄像头无法访问，检查浏览器权限设置
echo    • 推荐使用Chrome、Firefox等现代浏览器
echo    • 后端依赖PyTorch，首次启动可能较慢（1-3分钟）
echo    • 已修复WebM格式兼容性问题，支持应急帧提取
echo.
echo 🛑 停止服务:
echo    • 关闭对应的命令窗口
echo    • 或在各窗口中按 Ctrl+C
echo.

:: 询问是否打开浏览器
set /p OPEN_BROWSER="🌐 是否自动打开浏览器？(y/n): "
if /i "%OPEN_BROWSER%"=="y" (
    echo ⏳ 等待服务完全启动...
    timeout /t 15 /nobreak >nul
    echo 🌐 正在打开浏览器...
    start http://localhost:5175
)

echo.
echo 📋 系统已启动，按任意键关闭此窗口...
echo 💡 提示: 保持后端和前端窗口开启以维持服务运行
pause >nul
goto :end

:error
echo.
echo ❌ 启动失败，请安装必要的环境：
echo    1. Python 3.8-3.11: https://www.python.org/downloads/
echo    2. Node.js 16+: https://nodejs.org/
echo.
pause
goto :end

:end
echo 👋 再见！ 