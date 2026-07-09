import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

from ocr_tool import process_file
from gemini_tool import analyze_page, generate_questions
from output_tool import create_word_document

def get_all_files(input_folder: str) -> list:
    supported_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.pdf']
    files = []
    input_path = Path(input_folder)
    if not input_path.exists():
        print(f"❌ 找不到輸入資料夾：{input_folder}")
        return files
    for file_path in input_path.rglob('*'):
        if file_path.suffix.lower() in supported_extensions:
            files.append(str(file_path))
    return sorted(files)

def process_with_retry(func, *args, max_retries=3, delay=5):
    """自動重試機制（任務7）"""
    for attempt in range(max_retries):
        try:
            return func(*args)
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"  ⚠️  錯誤，{delay} 秒後重試（{attempt + 1}/{max_retries}）: {str(e)}")
                time.sleep(delay)
            else:
                print(f"  ❌ 重試 {max_retries} 次後仍失敗: {str(e)}")
                return None

def main():
    print("=" * 60)
    print("🤖 保險員證照考試教材 AI 處理系統（強化版）")
    print("   ✅ 支援流程圖視覺分析")
    print("   ✅ 支援跨頁內容自動合併")
    print("   ✅ 支援複雜表格結構提取")
    print("=" * 60)

    input_folder = os.getenv('INPUT_FOLDER', r'C:\insurance_ai\input')
    output_folder = os.getenv('OUTPUT_FOLDER', r'C:\insurance_ai\output')
    Path(output_folder).mkdir(parents=True, exist_ok=True)

    print(f"\n📁 掃描資料夾：{input_folder}")
    files = get_all_files(input_folder)

    if not files:
        print("❌ 找不到任何支援的檔案（jpg/png/pdf）")
        print(f"請將檔案放入：{input_folder}")
        return

    print(f"✅ 找到 {len(files)} 個檔案")
    for f in files:
        print(f"   📄 {Path(f).name}")

    all_results = []
    all_questions = []

    print("\n" + "=" * 60)
    print("🔍 開始處理...")
    print("=" * 60)

    for file_idx, file_path in enumerate(files, 1):
        file_name = Path(file_path).name
        print(f"\n[{file_idx}/{len(files)}] 處理：{file_name}")

        # STEP 1: OCR 提取
        print("  📖 OCR 提取中...")
        ocr_result = process_with_retry(process_file, file_path)
        if not ocr_result:
            print(f"  ❌ 跳過此檔案")
            continue

        total_pages = len(ocr_result['pages'])
        print(f"  ✅ 提取完成，共 {total_pages} 頁")

        # STEP 2: 逐頁 Gemini AI 分析
        print("  🧠 AI 逐頁分析中...")
        structured_pages = []

        for page_data in ocr_result['pages']:
            page_num = page_data['page_num']
            text = page_data['text']
            has_flowchart = page_data.get('has_flowchart', False)
            flowchart_image = page_data.get('flowchart_image', None)
            is_merged = page_data.get('is_merged', False)
            merged_pages = page_data.get('merged_pages', [])

            if not text.strip():
                print(f"    第 {page_num} 頁：空白，跳過")
                continue

            status = f"第 {page_num}/{total_pages} 頁"
            if is_merged:
                status += f" [跨頁合併: {merged_pages}]"
            if has_flowchart:
                status += " [含流程圖]"
            print(f"    分析{status}...")

            # 結構化分析
            structured = process_with_retry(
                analyze_page, text, page_num, file_name,
                has_flowchart, flowchart_image, is_merged, merged_pages
            )

            if structured:
                structured_pages.append(structured)
                # 生成題目
                questions = process_with_retry(generate_questions, structured)
                if questions:
                    for q in questions:
                        q['source_file'] = file_name
                        q['source_page'] = page_num
                    all_questions.extend(questions)
                    print(f"      ✅ 生成 {len(questions)} 道題目")

            time.sleep(3)  # 避免 API 速率限制

        file_result = {
            'file_name': file_name,
            'file_path': file_path,
            'total_pages': total_pages,
            'structured_pages': structured_pages
        }
        all_results.append(file_result)
        print(f"  ✅ {file_name} 完成！")

    # STEP 3: 儲存所有輸出
    print("\n" + "=" * 60)
    print("💾 儲存結果...")
    print("=" * 60)

    # 儲存結構化 JSON
    json_path = os.path.join(output_folder, 'structured_data.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        # 移除無法序列化的 PIL Image 物件
        results_for_json = []
        for r in all_results:
            r_copy = r.copy()
            pages_copy = []
            for p in r_copy.get('structured_pages', []):
                p_copy = {k: v for k, v in p.items() if k != 'flowchart_image'}
                pages_copy.append(p_copy)
            r_copy['structured_pages'] = pages_copy
            results_for_json.append(r_copy)
        json.dump(results_for_json, f, ensure_ascii=False, indent=2)
    print(f"✅ 結構化資料：{json_path}")

    # 儲存題庫
    questions_path = os.path.join(output_folder, 'question_bank.json')
    with open(questions_path, 'w', encoding='utf-8') as f:
        json.dump(all_questions, f, ensure_ascii=False, indent=2)
    print(f"✅ 題庫：{questions_path}（共 {len(all_questions)} 題）")

    # 生成 Word 文件
    print("\n📝 生成 Word 文件...")
    word_path = os.path.join(output_folder, '保險員證照考試教材整理.docx')
    result_path = process_with_retry(create_word_document, all_results, word_path)
    if result_path:
        print(f"✅ Word 文件：{result_path}")

    # 完成報告
    print("\n" + "=" * 60)
    print("🎉 所有任務完成！")
    print("=" * 60)
    print(f"📊 處理統計：")
    print(f"   檔案數量：{len(all_results)} 個")
    total_p = sum(len(r.get('structured_pages', [])) for r in all_results)
    cross_p = sum(1 for r in all_results for p in r.get('structured_pages', []) if p.get('is_cross_page'))
    flow_p = sum(1 for r in all_results for p in r.get('structured_pages', []) if p.get('has_flowchart'))
    print(f"   處理頁數：{total_p} 頁")
    print(f"   跨頁合併：{cross_p} 處")
    print(f"   流程圖頁：{flow_p} 頁")
    print(f"   生成題目：{len(all_questions)} 題")
    print(f"\n📁 輸出位置：{output_folder}")
    print(f"   📄 保險員證照考試教材整理.docx")
    print(f"   📊 structured_data.json")
    print(f"   📝 question_bank.json")

if __name__ == "__main__":
    main()
