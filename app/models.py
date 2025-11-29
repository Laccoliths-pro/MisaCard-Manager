"""
数据库模型定义
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.sql import func
from .database import Base


class Card(Base):
    """卡片信息表"""
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    # 卡密（唯一标识）
    card_id = Column(String, unique=True, index=True, nullable=False)
    # 卡片昵称
    card_nickname = Column(String, nullable=True)
    # 卡号（激活后才有）
    card_number = Column(String, nullable=True)
    # CVC（激活后才有）
    card_cvc = Column(String, nullable=True)
    # 信用卡有效期（激活后才有，格式：MM/YY，如"11/31"）
    card_exp_date = Column(String, nullable=True)
    # 账单地址
    billing_address = Column(String, nullable=True)
    # 额度
    card_limit = Column(Float, default=0.0)
    # 有效期小时数（对应API的exp_date字段，是整数如1表示1小时）
    validity_hours = Column(Integer, nullable=True)
    # 状态：active, inactive, expired, deleted
    status = Column(String, default="inactive")
    # 是否已激活
    is_activated = Column(Boolean, default=False)
    # 创建时间
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    # 激活时间
    card_activation_time = Column(DateTime(timezone=True), nullable=True)
    # 卡片系统过期时间（对应API的delete_date字段，这才是判断卡片是否过期的时间戳）
    exp_date = Column(DateTime(timezone=True), nullable=True)
    # 软删除时间（用户删除卡片的时间，不是卡片过期时间）
    delete_date = Column(DateTime(timezone=True), nullable=True)
    # 是否已申请退款
    refund_requested = Column(Boolean, default=False)
    # 退款申请时间
    refund_requested_time = Column(DateTime(timezone=True), nullable=True)


class ActivationLog(Base):
    """激活记录表"""
    __tablename__ = "activation_logs"

    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(String, index=True, nullable=False)
    # 激活状态：success, failed
    status = Column(String, nullable=False)
    # 错误信息（如果失败）
    error_message = Column(String, nullable=True)
    # 激活时间
    activation_time = Column(DateTime(timezone=True), server_default=func.now())
    # 响应数据（JSON格式）
    response_data = Column(String, nullable=True)
