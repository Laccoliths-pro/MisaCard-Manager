"""
卡片自动激活功能
保留原有 Next.js 项目的激活逻辑
"""
import httpx
from typing import Optional, Dict, Tuple
import json

from ..config import MISACARD_API_BASE_URL, MISACARD_API_HEADERS


# API 配置（从配置文件导入）
API_BASE_URL = MISACARD_API_BASE_URL
API_HEADERS = MISACARD_API_HEADERS

# 消费记录查询API基础URL
CARD_INFO_API_BASE_URL = "https://api.misacard.com/api/m/get_card_info"


async def query_card_from_api(card_id: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
    """
    从 MisaCard API 查询卡片信息

    Args:
        card_id: 卡密

    Returns:
        (成功标志, 卡片数据, 错误信息)
    """
    try:
        timeout = httpx.Timeout(30.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, verify=False) as client:
            response = await client.get(
                f"{API_BASE_URL}/{card_id}",
                headers=API_HEADERS
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("result"):
                    return True, data["result"], None
                else:
                    return False, None, data.get("msg") or "卡片不存在"
            else:
                return False, None, f"API 请求失败: {response.status_code}"

    except httpx.TimeoutException as e:
        return False, None, f"请求超时: {str(e)}"
    except httpx.HTTPError as e:
        return False, None, f"HTTP错误: {str(e)}"
    except Exception as e:
        return False, None, f"查询失败: {str(e)}"


async def activate_card_via_api(card_id: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
    """
    通过 MisaCard API 激活卡片

    Args:
        card_id: 卡密

    Returns:
        (成功标志, 激活后的卡片数据, 错误信息)
    """
    try:
        timeout = httpx.Timeout(30.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, verify=False) as client:
            response = await client.post(
                f"{API_BASE_URL}/activate/{card_id}",
                headers=API_HEADERS
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("result"):
                    return True, data["result"], None
                else:
                    return False, None, data.get("msg") or "激活失败"
            else:
                return False, None, f"激活请求失败: {response.status_code}"

    except httpx.TimeoutException as e:
        return False, None, f"激活超时: {str(e)}"
    except httpx.HTTPError as e:
        return False, None, f"HTTP错误: {str(e)}"
    except Exception as e:
        return False, None, f"激活失败: {str(e)}"


def is_card_unactivated(card_data: Dict) -> bool:
    """
    检查卡片是否未激活（保留原有逻辑）

    Args:
        card_data: 卡片数据字典

    Returns:
        True 如果未激活，否则 False
    """
    return (
        card_data.get("card_number") is None
        and card_data.get("card_cvc") is None
        and card_data.get("card_exp_date") is None
    )


async def auto_activate_if_needed(card_id: str) -> Tuple[bool, Optional[Dict], str]:
    """
    自动激活流程（保留原有逻辑）
    1. 查询卡片信息
    2. 如果未激活，自动调用激活 API
    3. 返回最终的卡片数据

    Args:
        card_id: 卡密

    Returns:
        (成功标志, 卡片数据, 消息)
    """
    # 步骤1: 查询卡片
    success, card_data, error = await query_card_from_api(card_id)
    if not success:
        return False, None, error or "查询失败"

    # 步骤2: 检查是否需要激活
    if is_card_unactivated(card_data):
        # 自动激活
        success, activated_data, error = await activate_card_via_api(card_id)
        if success:
            return True, activated_data, "卡片已自动激活"
        else:
            # 激活失败，但返回原始数据
            return True, card_data, f"激活失败: {error}，返回未激活数据"

    # 步骤3: 已激活，直接返回
    return True, card_data, "卡片已激活"


def extract_card_info(api_response: Dict) -> Dict:
    """
    从 API 响应中提取卡片信息

    Args:
        api_response: API 返回的卡片数据

    Returns:
        格式化的卡片信息字典
    """
    return {
        "card_number": api_response.get("card_number"),
        "card_cvc": api_response.get("card_cvc"),
        "card_exp_date": api_response.get("card_exp_date"),  # 信用卡有效期格式（MM/YY）
        "billing_address": api_response.get("billing_address"),
        "card_nickname": api_response.get("card_nickname"),
        "card_limit": api_response.get("card_limit", 0),
        "status": api_response.get("status", "unknown"),
        "create_time": api_response.get("create_time"),
        "card_activation_time": api_response.get("card_activation_time"),
        "validity_hours": api_response.get("exp_date"),  # API的exp_date是有效期小时数
        "exp_date": api_response.get("delete_date"),  # API的delete_date才是系统过期时间
    }


async def get_card_transactions(card_number: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
    """
    从 MisaCard API 查询卡片消费记录

    Args:
        card_number: 卡号

    Returns:
        (成功标志, 卡片信息和交易数据, 错误信息)
    """
    try:
        # 增加超时时间到30秒，禁用SSL验证
        timeout = httpx.Timeout(30.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, verify=False) as client:
            response = await client.get(
                f"{CARD_INFO_API_BASE_URL}/{card_number}",
                headers=API_HEADERS
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("result"):
                    return True, data["result"], None
                else:
                    return False, None, data.get("msg") or "无法获取卡片信息"
            else:
                return False, None, f"API 请求失败: {response.status_code}"

    except httpx.TimeoutException as e:
        return False, None, f"请求超时: {str(e)}"
    except httpx.HTTPError as e:
        return False, None, f"HTTP错误: {str(e)}"
    except Exception as e:
        return False, None, f"查询失败: {str(e)}"
