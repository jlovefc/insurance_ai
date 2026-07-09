"""
utils.py - 資料格式防呆工具
解決 AI 回傳格式不穩定的問題：
1. force_to_text(): 任何型態安全轉成字串
2. safe_json_loads(): 清理並安全解析 JSON
"""

import json
import re


def force_to_text(value) -> str:
    """
    將任何型態安全轉成文字：
    - str：直接回傳
    - int/float/bool：轉字串
    - list：逐項轉文字後合併
    - dict：優先取常見文字欄位，否則轉成 JSON 字串
    - None：回傳空字串
    """
    if value is None:
        return ""

    if isinstance(value, str):
        return value

    if isinstance(value, (int, float, bool)):
        return str(value)

    if isinstance(value, list):
        return "\n".join(force_to_text(item) for item in value)

    if isinstance(value, dict):
        # 優先取常見文字欄位
        for key in ["text", "content", "description", "summary", "title", "answer", "question", "definition"]:
            if key in value:
                return force_to_text(value[key])
        # 找不到就整個轉 JSON 字串
        return json.dumps(value, ensure_ascii=False)

    return str(value)


def force_list_of_str(value) -> list:
    """確保回傳的一定是 list of str"""
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, list):
        return [force_to_text(item) for item in value if item is not None]
    if isinstance(value, dict):
        return [force_to_text(value)]
    return [str(value)]


def clean_json_text(text: str) -> str:
    """清理 AI 回傳的 JSON 文字，移除不合法字元"""
    text = text.strip()

    # 移除 Markdown code block
    text = re.sub(r"^```json", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"^```", "", text).strip()
    text = re.sub(r"```$", "", text).strip()

    # 移除不可見控制字元，但保留正常換行(\n)與 tab(\t)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)

    return text


def safe_json_loads(response_text: str, fallback=None):
    """
    安全解析 JSON：
    1. 先清理文字
    2. 嘗試直接解析
    3. 失敗則回傳 fallback
    """
    if not response_text:
        return fallback

    cleaned = clean_json_text(response_text)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"      ⚠️  JSON 解析失敗：{e}")
        return fallback
