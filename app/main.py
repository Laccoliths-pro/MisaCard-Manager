"""
FastAPI 主应用程序
MisaCard 管理系统 - Python 重构版
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os

from .database import engine
from . import models
from .api import cards, imports

# 创建数据库表
models.Base.metadata.create_all(bind=engine)

# 创建 FastAPI 应用
app = FastAPI(
    title="MisaCard 管理系统",
    description="卡片管理系统 - 支持卡片查询、激活、批量导入",
    version="2.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由
app.include_router(cards.router, prefix="/api")
app.include_router(imports.router, prefix="/api")

# 静态文件和模板配置
templates_path = os.path.join(os.path.dirname(__file__), "templates")
static_path = os.path.join(os.path.dirname(__file__), "static")

# 确保目录存在
os.makedirs(static_path, exist_ok=True)

templates = Jinja2Templates(directory=templates_path)
app.mount("/static", StaticFiles(directory=static_path), name="static")


@app.get("/")
async def root(request: Request):
    """首页 - 渲染前端界面"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "MisaCard Backend",
        "version": "2.0.0"
    }


@app.get("/api/info")
async def api_info():
    """API 信息"""
    return {
        "name": "MisaCard API",
        "version": "2.0.0",
        "endpoints": {
            "cards": "/api/cards",
            "import": "/api/import",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
