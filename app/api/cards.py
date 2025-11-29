"""
卡片 CRUD API 端点
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import crud, schemas, models
from ..database import get_db
from ..utils.activation import auto_activate_if_needed, extract_card_info, query_card_from_api, get_card_transactions

router = APIRouter(prefix="/cards", tags=["cards"])


@router.post("/", response_model=schemas.CardResponse, status_code=201)
async def create_card(
    card: schemas.CardCreate,
    db: Session = Depends(get_db)
):
    """创建新卡片"""
    # 检查卡密是否已存在
    existing_card = crud.get_card_by_id(db, card.card_id)
    if existing_card:
        raise HTTPException(status_code=400, detail="卡密已存在")

    db_card = crud.create_card(db, card)
    return db_card


@router.get("/", response_model=List[schemas.CardResponse])
async def list_cards(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """获取卡片列表（支持分页、筛选、搜索）"""
    cards = crud.get_cards(db, skip=skip, limit=limit, status=status, search=search)
    return cards


@router.get("/{card_id}", response_model=schemas.CardResponse)
async def get_card(
    card_id: str,
    db: Session = Depends(get_db)
):
    """获取单个卡片信息"""
    db_card = crud.get_card_by_id(db, card_id)
    if not db_card:
        raise HTTPException(status_code=404, detail="卡片不存在")
    return db_card


@router.put("/{card_id}", response_model=schemas.CardResponse)
async def update_card(
    card_id: str,
    card_update: schemas.CardUpdate,
    db: Session = Depends(get_db)
):
    """更新卡片信息"""
    db_card = crud.update_card(db, card_id, card_update)
    if not db_card:
        raise HTTPException(status_code=404, detail="卡片不存在")
    return db_card


@router.delete("/{card_id}", response_model=schemas.APIResponse)
async def delete_card(
    card_id: str,
    db: Session = Depends(get_db)
):
    """删除卡片（软删除）"""
    success = crud.delete_card(db, card_id)
    if not success:
        raise HTTPException(status_code=404, detail="卡片不存在")
    return {"success": True, "message": "卡片已删除"}


@router.post("/{card_id}/activate", response_model=schemas.ActivationResponse)
async def activate_card(
    card_id: str,
    db: Session = Depends(get_db)
):
    """
    激活卡片（保留原有自动激活逻辑）
    1. 调用 MisaCard API 查询和激活
    2. 更新本地数据库
    3. 记录激活日志
    """
    # 检查卡片是否存在
    db_card = crud.get_card_by_id(db, card_id)
    if not db_card:
        raise HTTPException(status_code=404, detail="卡片不存在于本地数据库")

    # 自动激活流程
    success, card_data, message = await auto_activate_if_needed(card_id)

    if not success:
        # 记录失败日志
        crud.create_activation_log(db, card_id, "failed", error_message=message)
        raise HTTPException(status_code=400, detail=message)

    # 提取卡片信息
    card_info = extract_card_info(card_data)

    # 更新数据库中的卡片信息
    if card_info.get("card_number"):
        # 解析过期时间（API返回的delete_date字段）
        from datetime import datetime
        exp_date = None
        if card_info.get("exp_date"):
            try:
                exp_date = datetime.fromisoformat(card_info["exp_date"].replace('Z', '+00:00'))
            except:
                pass

        crud.activate_card_in_db(
            db,
            card_id,
            card_info["card_number"],
            card_info["card_cvc"],
            card_info["card_exp_date"],
            card_info.get("billing_address"),
            validity_hours=card_info.get("validity_hours"),
            exp_date=exp_date
        )

        # 记录成功日志
        crud.create_activation_log(db, card_id, "success")

        # 重新获取更新后的卡片
        db_card = crud.get_card_by_id(db, card_id)
        return {
            "success": True,
            "message": message,
            "card_data": db_card
        }
    else:
        # 卡片未激活，但查询成功
        return {
            "success": True,
            "message": message,
            "card_data": db_card
        }


@router.post("/{card_id}/query", response_model=schemas.ActivationResponse)
async def query_card(
    card_id: str,
    db: Session = Depends(get_db)
):
    """
    从API查询卡片信息并更新数据库
    用于获取最新的卡片状态、过期时间等信息
    """
    # 检查卡片是否存在
    db_card = crud.get_card_by_id(db, card_id)
    if not db_card:
        raise HTTPException(status_code=404, detail="卡片不存在于本地数据库")

    # 从API查询卡片信息
    success, card_data, error = await query_card_from_api(card_id)

    if not success:
        raise HTTPException(status_code=400, detail=error or "查询失败")

    # 提取卡片信息
    card_info = extract_card_info(card_data)

    # 解析过期时间（API返回的delete_date字段，是UTC+8时间）
    from datetime import datetime, timezone, timedelta
    exp_date = None
    if card_info.get("exp_date"):
        try:
            # 解析时间字符串
            dt = datetime.fromisoformat(card_info["exp_date"].replace('Z', '+00:00'))

            # 如果是 naive datetime（没有时区信息），说明是 UTC+8 时间
            if dt.tzinfo is None:
                # 先标记为 UTC+8
                utc8 = timezone(timedelta(hours=8))
                dt = dt.replace(tzinfo=utc8)
                # 转换为 UTC 时间
                exp_date = dt.astimezone(timezone.utc)
            else:
                # 如果已经有时区信息，转换为 UTC
                exp_date = dt.astimezone(timezone.utc)
        except:
            pass

    # 更新数据库中的卡片信息
    update_data = schemas.CardUpdate(
        card_limit=card_info.get("card_limit"),
        status=card_info.get("status")
    )

    # 如果有卡号信息，说明已激活，更新完整信息
    if card_info.get("card_number"):
        crud.activate_card_in_db(
            db,
            card_id,
            str(card_info["card_number"]),
            str(card_info["card_cvc"]),
            card_info["card_exp_date"],
            card_info.get("billing_address"),
            validity_hours=card_info.get("validity_hours"),
            exp_date=exp_date
        )
    else:
        # 未激活，只更新基本信息和过期时间
        db_card.validity_hours = card_info.get("validity_hours")
        db_card.exp_date = exp_date
        crud.update_card(db, card_id, update_data)

    # 重新获取更新后的卡片
    db_card = crud.get_card_by_id(db, card_id)
    return {
        "success": True,
        "message": "查询成功",
        "card_data": db_card
    }


@router.get("/{card_id}/logs", response_model=List[dict])
async def get_activation_logs(
    card_id: str,
    db: Session = Depends(get_db)
):
    """获取卡片的激活历史记录"""
    logs = crud.get_activation_logs(db, card_id)
    return [
        {
            "id": log.id,
            "status": log.status,
            "error_message": log.error_message,
            "activation_time": log.activation_time,
        }
        for log in logs
    ]


@router.post("/{card_id}/refund", response_model=schemas.APIResponse)
async def toggle_refund_status(
    card_id: str,
    db: Session = Depends(get_db)
):
    """
    切换卡片的退款状态（标记/取消标记退款）
    """
    from datetime import datetime

    db_card = crud.get_card_by_id(db, card_id)
    if not db_card:
        raise HTTPException(status_code=404, detail="卡片不存在")

    # 切换退款状态
    db_card.refund_requested = not db_card.refund_requested

    if db_card.refund_requested:
        from datetime import timezone
        db_card.refund_requested_time = datetime.now(timezone.utc)
        message = "已标记为申请退款"
    else:
        db_card.refund_requested_time = None
        message = "已取消退款标记"

    db.commit()
    db.refresh(db_card)

    return {
        "success": True,
        "message": message,
        "data": {"refund_requested": db_card.refund_requested}
    }


@router.get("/batch/unreturned-card-numbers", response_model=schemas.APIResponse)
async def get_unreturned_card_numbers(
    db: Session = Depends(get_db)
):
    """
    获取所有已过期、未退款且已激活的卡号列表
    用于批量复制和申请退款
    """
    # 先更新所有过期卡片的状态
    crud.update_expired_cards(db)

    # 筛选条件：已过期 + 已激活 + 未退款 + 有卡号
    cards = db.query(models.Card).filter(
        models.Card.status == 'expired',  # 只获取已过期的卡片
        models.Card.is_activated == True,
        models.Card.refund_requested == False,
        models.Card.card_number.isnot(None)
    ).all()

    card_numbers = [str(card.card_number) for card in cards]

    return {
        "success": True,
        "message": f"找到 {len(card_numbers)} 张已过期未退款的卡片",
        "data": {
            "count": len(card_numbers),
            "card_numbers": card_numbers
        }
    }


@router.get("/{card_id}/transactions", response_model=schemas.APIResponse)
async def get_card_transaction_history(
    card_id: str,
    db: Session = Depends(get_db)
):
    """
    获取卡片的消费记录
    需要卡片已激活（有卡号）才能查询
    """
    # 检查卡片是否存在
    db_card = crud.get_card_by_id(db, card_id)
    if not db_card:
        raise HTTPException(status_code=404, detail="卡片不存在")

    # 检查卡片是否已激活
    if not db_card.card_number:
        raise HTTPException(status_code=400, detail="卡片未激活，无法查询消费记录")

    # 从API查询消费记录
    success, card_info, error = await get_card_transactions(str(db_card.card_number))

    if not success:
        raise HTTPException(status_code=400, detail=error or "查询消费记录失败")

    return {
        "success": True,
        "message": "查询成功",
        "data": card_info
    }
