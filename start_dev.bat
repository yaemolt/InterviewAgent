@echo off
echo 正在启动智能面试系统...

echo.
echo 1. 启动后端服务...
cd simulation\back
start "后端服务" cmd /k "python app.py"

echo.
echo 2. 等待3秒让后端服务启动...
timeout /t 3 /nobreak > nul

echo.
echo 3. 启动前端服务...
cd ..\FrontEnd
start "前端服务" cmd /k "npm run dev -- --host"

echo.
echo 启动完成！
echo 前端服务: http://localhost:5174
echo 后端服务: http://localhost:5000
echo 健康检查: http://localhost:5000/api/health
echo.
echo 注意：前端服务已配置为在所有网络接口上运行
echo 您也可以通过局域网IP访问前端服务
echo.
pause 