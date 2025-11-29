"""
数据库配置和连接
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import DATABASE_URL

# SQLite 数据库文件路径
SQLALCHEMY_DATABASE_URL = DATABASE_URL

# 创建数据库引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite 特定配置
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


# 依赖项：获取数据库会话
def get_db():
    """
    获取数据库会话的依赖项
    使用yield确保请求结束后关闭会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
