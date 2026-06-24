@echo off
chcp 65001 >nul 2>&1
title CyAnalyst Dev Server

cd /d "%~dp0"

if not exist "node_modules" (
    echo [INFO] 首次运行，正在安装依赖...
    call npm install
    if errorlevel 1 (
        echo [ERROR] 依赖安装失败，请检查 Node.js 环境
        pause
        exit /b 1
    )
    echo [INFO] 依赖安装完成
    echo.
)

echo [INFO] 启动开发服务器...
echo [INFO] 访问地址: http://localhost:5173/cyanalyst/
echo [INFO] 按 Ctrl+C 停止
echo.

call npx astro dev --port 5173

pause
