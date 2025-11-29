"""
txt 文件解析器
支持解析格式：
卡密: mio-f3dc27e4-e853-429a-9e4b-3294af7c25ca 额度: 1 有效期: 1小时
"""
import re
from typing import List, Dict, Optional


def parse_card_line(line: str) -> Optional[Dict]:
    """
    解析单行卡片数据

    支持多种格式：
    1. 完整格式：卡密: mio-xxx 额度: 1 有效期: 1小时
    2. 仅卡密：mio-xxx (使用默认额度1和有效期1小时)

    Args:
        line: 包含卡片信息的文本行

    Returns:
        解析后的字典，包含 card_id, card_limit, validity_hours
        如果解析失败返回 None
    """
    line = line.strip()
    if not line:
        return None

    # 方式1: 尝试匹配完整格式：卡密: xxx 额度: xxx 有效期: xxx小时
    full_pattern = r'卡密:\s*([^\s]+)\s+额度:\s*(\d+(?:\.\d+)?)\s+有效期:\s*(\d+)\s*小时'
    match = re.search(full_pattern, line)

    if match:
        card_id = match.group(1).strip()
        card_limit = float(match.group(2))
        validity_hours = int(match.group(3))

        # 验证卡密格式
        if validate_card_id(card_id):
            return {
                "card_id": card_id,
                "card_limit": card_limit,
                "validity_hours": validity_hours
            }

    # 方式2: 尝试从文本中提取卡密（可能有"卡密:"前缀）
    card_id_pattern = r'(?:卡密:\s*)?(mio-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'
    match = re.search(card_id_pattern, line, re.IGNORECASE)

    if match:
        card_id = match.group(1).strip()

        # 验证卡密格式
        if validate_card_id(card_id):
            # 只有卡密时，使用默认值
            return {
                "card_id": card_id,
                "card_limit": 0.0,  # 默认额度0（激活后从API获取实际额度）
                "validity_hours": 1  # 默认有效期1小时
            }

    return None


def parse_txt_file(content: str) -> tuple[List[Dict], List[str]]:
    """
    解析整个 txt 文件内容

    Args:
        content: txt 文件的完整内容

    Returns:
        (成功解析的卡片列表, 失败的行列表)
    """
    lines = content.split('\n')
    parsed_cards = []
    failed_lines = []

    for line_num, line in enumerate(lines, 1):
        if not line.strip():
            continue

        parsed = parse_card_line(line)
        if parsed:
            parsed_cards.append(parsed)
        else:
            failed_lines.append(f"第{line_num}行: {line.strip()}")

    return parsed_cards, failed_lines


def validate_card_id(card_id: str) -> bool:
    """
    验证卡密格式是否正确

    Args:
        card_id: 卡密字符串

    Returns:
        True 如果格式正确，否则 False
    """
    # 检查是否以 mio- 开头
    if not card_id.startswith('mio-'):
        return False

    # 检查后面是否是 UUID 格式（带连字符）
    uuid_pattern = r'^mio-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(uuid_pattern, card_id.lower()))


def format_card_info(card_data: Dict) -> str:
    """
    格式化卡片信息为可读文本

    Args:
        card_data: 卡片数据字典

    Returns:
        格式化后的文本
    """
    return f"卡密: {card_data['card_id']} 额度: {card_data['card_limit']} 有效期: {card_data['validity_hours']}小时"
