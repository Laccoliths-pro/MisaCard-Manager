"""
Pydantic 数据验证模型
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CardBase(BaseModel):
    """卡片基础模型"""
    card_id: str = Field(..., description="卡密")
    card_nickname: Optional[str] = Field(None, description="卡片昵称")
    card_limit: float = Field(default=0.0, description="额度")
    validity_hours: Optional[int] = Field(None, description="有效期（小时）")


class CardCreate(CardBase):
    """创建卡片请求模型"""
    pass


class CardUpdate(BaseModel):
    """更新卡片请求模型"""
    card_nickname: Optional[str] = None
    card_limit: Optional[float] = None
    validity_hours: Optional[int] = None
    status: Optional[str] = None


class CardResponse(CardBase):
    """卡片响应模型"""
    id: int
    card_number: Optional[str] = None
    card_cvc: Optional[str] = None
    card_exp_date: Optional[str] = None
    billing_address: Optional[str] = None
    status: str
    is_activated: bool
    create_time: datetime
    card_activation_time: Optional[datetime] = None
    exp_date: Optional[datetime] = None
    delete_date: Optional[datetime] = None
    refund_requested: bool = False
    refund_requested_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class CardImportItem(BaseModel):
    """txt导入单条数据模型"""
    card_id: str
    card_limit: float
    validity_hours: int


class CardImportRequest(BaseModel):
    """批量导入请求模型"""
    cards: list[CardImportItem]


class CardImportResponse(BaseModel):
    """批量导入响应模型"""
    success_count: int
    failed_count: int
    failed_items: list[dict]
    message: str


class ActivationRequest(BaseModel):
    """激活请求模型"""
    card_id: str


class ActivationResponse(BaseModel):
    """激活响应模型"""
    success: bool
    message: str
    card_data: Optional[CardResponse] = None


class APIResponse(BaseModel):
    """通用API响应模型"""
    success: bool
    message: str
    data: Optional[dict] = None
