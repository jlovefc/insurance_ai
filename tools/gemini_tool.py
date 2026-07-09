"""
gemini_tool.py - Gemini AI 分析工具（修正版）
修正：
1. 使用 safe_json_loads() 清理 AI 回傳的 JSON
2. 使用 force_to_text() / force_list_of_str() 防呆所有欄位
"""

import google.generativeai as genai
import os
import json
import base64
from io import BytesIO
from PIL import Image

from utils import force_to_text, force_list_of_str, safe_json_loads


def setup_gemini():
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("找不到 GEMINI_API_KEY，請確認 .env 檔案設定正確")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash-lite')


def image_to_base64(pil_image: Image.Image) -> str:
    buffer = BytesIO()
    pil_image.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode()


def analyze_flowchart(pil_image: Image.Image, page_num: int, file_name: str) -> str:
    """用 Gemini Vision 分析流程圖"""
    model = setup_gemini()
    try:
        prompt = f"""請分析這個保險考試教材第 {page_num} 頁的流程圖或圖表。
請詳細描述：
1. 流程圖的主要主題
2. 流程的起點和終點
3. 每個步驟/方塊的內容（用 → 表示流向）
4. 如果有判斷節點，說明「是」和「否」各走哪條路
5. 整個流程的邏輯摘要

請用以下格式輸出：
【流程圖主題】：
【流程步驟】：步驟1 → 步驟2 → 步驟3
【判斷節點】：
【流程摘要】："""

        response = model.generate_content([
            prompt,
            {"mime_type": "image/png", "data": image_to_base64(pil_image)}
        ])
        return response.text
    except Exception as e:
        return f"[流程圖分析失敗]: {str(e)}"


def normalize_page_result(raw: dict, page_num: int, file_name: str) -> dict:
    """
    強制標準化 AI 回傳的結果，確保所有欄位都是正確型態
    這是解決 'expected str instance, dict found' 的核心函式
    """
    return {
        "page_num": page_num,
        "file_name": file_name,
        "is_cross_page": bool(raw.get("is_cross_page", False)),
        "merged_pages": force_list_of_str(raw.get("merged_pages", [])),
        "has_flowchart": bool(raw.get("has_flowchart", False)),
        "main_topic": force_to_text(raw.get("main_topic", "未知主題")),
        "sub_topics": force_list_of_str(raw.get("sub_topics", [])),
        "key_points": force_list_of_str(raw.get("key_points", [])),
        # definitions 可能是 list of dict，特別處理
        "definitions": [
            {
                "term": force_to_text(d.get("term", "") if isinstance(d, dict) else d),
                "definition": force_to_text(d.get("definition", "") if isinstance(d, dict) else "")
            }
            for d in (raw.get("definitions", []) or [])
            if d is not None
        ],
        "flowchart_steps": force_list_of_str(raw.get("flowchart_steps", [])),
        # tables 可能是 list of dict，特別處理
        "tables": [
            {
                "title": force_to_text(t.get("title", "") if isinstance(t, dict) else t),
                "content": force_to_text(t.get("content", "") if isinstance(t, dict) else "")
            }
            for t in (raw.get("tables", []) or [])
            if t is not None
        ],
        "exam_hints": force_list_of_str(raw.get("exam_hints", [])),
        "structured_content": force_to_text(raw.get("structured_content", "")),
    }


def analyze_page(text: str, page_num: int, file_name: str,
                 has_flowchart: bool = False, flowchart_image=None,
                 is_merged: bool = False, merged_pages: list = None) -> dict:
    """用 Gemini AI 對一頁進行結構化處理"""
    model = setup_gemini()

    # 流程圖視覺分析
    flowchart_description = ""
    if has_flowchart and flowchart_image is not None:
        print(f"      🔍 視覺分析流程圖...")
        flowchart_description = analyze_flowchart(flowchart_image, page_num, file_name)

    cross_page_note = f"（跨頁合併，涵蓋第 {merged_pages} 頁）" if is_merged and merged_pages else ""
    flowchart_note = f"\n\n【流程圖分析結果】\n{flowchart_description}" if flowchart_description else ""

    prompt = f"""你是保險員證照考試的專業教材整理助手。
請將以下從保險考試教材第 {page_num} 頁{cross_page_note}提取的內容進行結構化整理。

【原始文字內容】
{text}
{flowchart_note}

重要：請輸出合法的 JSON 格式，不要包含任何控制字元、反斜線或特殊跳脫字元。
只輸出 JSON，不要其他文字：
{{
    "page_num": {page_num},
    "file_name": "{file_name}",
    "is_cross_page": {str(is_merged).lower()},
    "merged_pages": {json.dumps(merged_pages or [])},
    "has_flowchart": {str(has_flowchart).lower()},
    "main_topic": "本頁的主要主題",
    "sub_topics": ["子主題1", "子主題2"],
    "key_points": ["重點1", "重點2", "重點3"],
    "definitions": [{{"term": "術語", "definition": "定義"}}],
    "flowchart_steps": ["步驟1", "步驟2"],
    "tables": [{{"title": "表格標題", "content": "表格內容"}}],
    "exam_hints": ["考試重點1", "考試重點2"],
    "structured_content": "完整結構化內容"
}}"""

    try:
        response = model.generate_content(prompt)
        raw = safe_json_loads(response.text, fallback=None)

        if raw is None:
            # JSON 解析失敗，回傳安全的預設結果
            return normalize_page_result({
                "main_topic": "JSON解析失敗，保留原始內容",
                "structured_content": text + ("\n\n" + flowchart_description if flowchart_description else ""),
                "flowchart_steps": [flowchart_description] if flowchart_description else [],
            }, page_num, file_name)

        # 標準化所有欄位
        result = normalize_page_result(raw, page_num, file_name)
        return result

    except Exception as e:
        return normalize_page_result({
            "main_topic": f"分析錯誤: {str(e)}",
            "structured_content": text,
        }, page_num, file_name)


def generate_questions(structured_content: dict) -> list:
    """根據結構化內容自動生成考試題目"""
    model = setup_gemini()

    # 安全取得所有欄位（全部用 force_to_text 防呆）
    main_topic = force_to_text(structured_content.get('main_topic', ''))
    key_points = force_list_of_str(structured_content.get('key_points', []))
    flowchart_steps = force_list_of_str(structured_content.get('flowchart_steps', []))
    exam_hints = force_list_of_str(structured_content.get('exam_hints', []))
    content_text = force_to_text(structured_content.get('structured_content', ''))[:2000]

    flowchart_info = f"\n流程步驟：{' → '.join(flowchart_steps)}" if flowchart_steps else ""

    prompt = f"""你是保險員證照考試出題專家。
根據以下保險考試教材內容，生成5道高品質選擇題。

主題：{main_topic}
重點：{', '.join(key_points)}
{flowchart_info}
考試提示：{', '.join(exam_hints)}
完整內容：{content_text}

重要：請輸出合法 JSON，不要包含控制字元或非法跳脫字元。
只輸出 JSON 陣列：
[
  {{
    "question": "題目內容",
    "options": {{"A": "選項A", "B": "選項B", "C": "選項C", "D": "選項D"}},
    "answer": "A",
    "explanation": "解析說明",
    "topic": "所屬主題",
    "difficulty": "easy",
    "question_type": "知識型"
  }}
]"""

    try:
        response = model.generate_content(prompt)
        result = safe_json_loads(response.text, fallback=None)

        if result is None or not isinstance(result, list):
            return []

        # 標準化每道題目
        normalized = []
        for q in result:
            if not isinstance(q, dict):
                continue
            normalized.append({
                "question": force_to_text(q.get("question", "")),
                "options": {
                    k: force_to_text(v)
                    for k, v in (q.get("options", {}) or {}).items()
                },
                "answer": force_to_text(q.get("answer", "")),
                "explanation": force_to_text(q.get("explanation", "")),
                "topic": force_to_text(q.get("topic", "")),
                "difficulty": force_to_text(q.get("difficulty", "medium")),
                "question_type": force_to_text(q.get("question_type", "知識型")),
            })
        return normalized

    except Exception as e:
        print(f"      ⚠️  題目生成失敗: {str(e)}")
        return []
