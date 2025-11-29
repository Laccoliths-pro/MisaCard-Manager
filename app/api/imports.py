"""
批量导入 API 端点
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from .. import crud, schemas
from ..database import get_db
from ..utils.parser import parse_txt_file, validate_card_id

router = APIRouter(prefix="/import", tags=["import"])


class TextImportRequest(BaseModel):
    """文本导入请求模型"""
    content: str


@router.post("/text", response_model=schemas.CardImportResponse)
async def import_from_text(
    request: TextImportRequest,
    db: Session = Depends(get_db)
):
    """
    从文本内容批量导入卡片（支持剪贴板粘贴）
    支持格式：卡密: mio-xxx 额度: x 有效期: x小时
    """
    text_content = request.content.strip()

    if not text_content:
        raise HTTPException(status_code=400, detail="文本内容不能为空")

    # 解析文本
    parsed_cards, failed_lines = parse_txt_file(text_content)

    if not parsed_cards:
        raise HTTPException(
            status_code=400,
            detail=f"没有成功解析任何卡片数据。失败的行: {failed_lines}"
        )

    # 批量导入
    success_count = 0
    failed_count = 0
    failed_items = []

    for card_data in parsed_cards:
        try:
            # 验证卡密格式
            if not validate_card_id(card_data["card_id"]):
                failed_count += 1
                failed_items.append({
                    "card_id": card_data["card_id"],
                    "reason": "卡密格式不正确"
                })
                continue

            # 检查是否已存在
            existing_card = crud.get_card_by_id(db, card_data["card_id"])
            if existing_card:
                failed_count += 1
                failed_items.append({
                    "card_id": card_data["card_id"],
                    "reason": "卡密已存在"
                })
                continue

            # 创建卡片
            card_create = schemas.CardCreate(**card_data)
            crud.create_card(db, card_create)
            success_count += 1

        except Exception as e:
            failed_count += 1
            failed_items.append({
                "card_id": card_data.get("card_id", "未知"),
                "reason": str(e)
            })

    return {
        "success_count": success_count,
        "failed_count": failed_count,
        "failed_items": failed_items,
        "message": f"成功导入 {success_count} 张卡片，失败 {failed_count} 张"
    }


@router.post("/json", response_model=schemas.CardImportResponse)
async def import_from_json(
    import_data: schemas.CardImportRequest,
    db: Session = Depends(get_db)
):
    """
    从 JSON 数据批量导入卡片
    """
    success_count = 0
    failed_count = 0
    failed_items = []

    for card_item in import_data.cards:
        try:
            # 验证卡密格式
            if not validate_card_id(card_item.card_id):
                failed_count += 1
                failed_items.append({
                    "card_id": card_item.card_id,
                    "reason": "卡密格式不正确"
                })
                continue

            # 检查是否已存在
            existing_card = crud.get_card_by_id(db, card_item.card_id)
            if existing_card:
                failed_count += 1
                failed_items.append({
                    "card_id": card_item.card_id,
                    "reason": "卡密已存在"
                })
                continue

            # 创建卡片
            card_create = schemas.CardCreate(
                card_id=card_item.card_id,
                card_limit=card_item.card_limit,
                validity_hours=card_item.validity_hours
            )
            crud.create_card(db, card_create)
            success_count += 1

        except Exception as e:
            failed_count += 1
            failed_items.append({
                "card_id": card_item.card_id,
                "reason": str(e)
            })

    return {
        "success_count": success_count,
        "failed_count": failed_count,
        "failed_items": failed_items,
        "message": f"成功导入 {success_count} 张卡片，失败 {failed_count} 张"
    }
