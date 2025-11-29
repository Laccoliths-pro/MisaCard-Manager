#!/bin/bash
# 启动 MisaCard 管理系统

echo "启动 MisaCard 管理系统..."
echo "================================"
echo ""
echo "Web 界面: http://localhost:8000"
echo "API 文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "================================"
echo ""

# 启动服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
