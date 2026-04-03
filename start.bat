@echo off
echo ========================================
echo AI智能体平台 - 一键启动脚本
echo ========================================
echo.

echo [1/3] 检查Docker状态...
docker --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未检测到Docker，请先安装Docker Desktop
    pause
    exit /b 1
)

echo [2/3] 启动服务...
docker-compose up -d --build

echo [3/3] 等待服务就绪...
timeout /t 30 /nobreak >nul

echo.
echo ========================================
echo 服务启动完成！
echo ========================================
echo.
echo 前端地址: http://localhost
echo 后端API: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo.
echo 默认管理员账号:
echo   用户名: admin
echo   密码: admin123
echo.
echo 查看服务状态: docker-compose ps
echo 查看日志: docker-compose logs -f
echo 停止服务: docker-compose down
echo.
pause
