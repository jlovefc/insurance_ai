import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import pdfplumber
import os
from pathlib import Path

def setup_tesseract():
    tesseract_path = os.getenv('TESSERACT_PATH', r'C:\Program Files\Tesseract-OCR\tesseract.exe')
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

def enhance_image(image: Image.Image) -> Image.Image:
    """強化圖片品質以提升 OCR 準確度"""
    image = image.convert('L')
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    image = image.filter(ImageFilter.SHARPEN)
    return image

def ocr_image(image_path: str) -> str:
    """對圖片檔案進行 OCR"""
    setup_tesseract()
    try:
        image = Image.open(image_path)
        image = enhance_image(image)
        text = pytesseract.image_to_string(image, lang='chi_tra+chi_sim+eng', config='--psm 6 --oem 3')
        return text.strip()
    except Exception as e:
        return f"[OCR錯誤] {image_path}: {str(e)}"

def ocr_pil_image(pil_image: Image.Image) -> str:
    """對 PIL Image 物件直接 OCR"""
    setup_tesseract()
    try:
        enhanced = enhance_image(pil_image)
        text = pytesseract.image_to_string(enhanced, lang='chi_tra+chi_sim+eng', config='--psm 6 --oem 3')
        return text.strip()
    except Exception as e:
        return f"[OCR錯誤]: {str(e)}"

def extract_complex_table(page) -> str:
    """強化版表格提取：保留欄位標題和對齊格式"""
    table_texts = []
    tables = page.extract_tables()
    if not tables:
        return ""
    for table_idx, table in enumerate(tables):
        if not table:
            continue
        table_text = f"\n[表格 {table_idx + 1}]\n"
        for row_idx, row in enumerate(table):
            if not row:
                continue
            cleaned_cells = [str(cell).strip().replace('\n', ' ') if cell else "" for cell in row]
            table_text += " | ".join(cleaned_cells) + "\n"
            if row_idx == 0:
                table_text += "-" * 60 + "\n"
        table_texts.append(table_text)
    return "\n".join(table_texts)

def is_incomplete_sentence(text: str) -> bool:
    """判斷文字是否為不完整句子（跨頁偵測）"""
    if not text:
        return False
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if not lines:
        return False
    last_line = lines[-1]
    complete_endings = ['。', '！', '？', '…', '.', '!', '?', ':', '：', '】', '）', ')', '"', '」']
    for ending in complete_endings:
        if last_line.endswith(ending):
            return False
    if len(last_line) < 5:
        return False
    return True

def merge_cross_pages(pages: list) -> list:
    """合併跨頁內容：自動偵測並合併不完整句子"""
    if len(pages) <= 1:
        return pages
    merged_pages = []
    i = 0
    while i < len(pages):
        current_page = pages[i].copy()
        while i + 1 < len(pages) and is_incomplete_sentence(current_page['text']):
            next_page = pages[i + 1]
            current_page['text'] = current_page['text'].rstrip() + '\n[↓ 跨頁連續內容 ↓]\n' + next_page['text']
            current_page['is_merged'] = True
            current_page['merged_pages'] = current_page.get('merged_pages', [current_page['page_num']]) + [next_page['page_num']]
            i += 1
        merged_pages.append(current_page)
        i += 1
    return merged_pages

def detect_flowchart(page) -> dict:
    """偵測流程圖：提取頁面圖片供 AI 視覺分析"""
    result = {'has_flowchart': False, 'flowchart_image': None, 'text_content': ''}
    try:
        text = page.extract_text() or ""
        result['text_content'] = text
        flowchart_indicators = ['→', '↓', '↑', '←', '⇒', '流程', '步驟', '開始', '結束', '判斷']
        has_indicators = any(indicator in text for indicator in flowchart_indicators)
        if has_indicators and len(text.strip()) < 500:
            result['has_flowchart'] = True
            img = page.to_image(resolution=200)
            result['flowchart_image'] = img.original
    except Exception as e:
        result['text_content'] = f"[流程圖偵測錯誤]: {str(e)}"
    return result

def extract_pdf(pdf_path: str) -> list:
    """強化版 PDF 提取：自動處理流程圖、複雜表格、跨頁內容"""
    pages = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            for page_num, page in enumerate(pdf.pages, 1):
                print(f"    提取第 {page_num}/{total_pages} 頁...")
                page_data = {
                    'page_num': page_num, 'text': '',
                    'has_tables': False, 'has_flowchart': False,
                    'flowchart_image': None, 'is_merged': False, 'merged_pages': []
                }
                # 偵測流程圖
                flowchart_info = detect_flowchart(page)
                page_data['has_flowchart'] = flowchart_info['has_flowchart']
                page_data['flowchart_image'] = flowchart_info['flowchart_image']
                # 提取文字
                text = page.extract_text() or ""
                # 提取複雜表格
                table_text = extract_complex_table(page)
                if table_text:
                    page_data['has_tables'] = True
                # 文字太少時用 OCR
                if len(text.strip()) < 50:
                    print(f"    第 {page_num} 頁文字太少，改用 OCR 掃描...")
                    img = page.to_image(resolution=300)
                    text = ocr_pil_image(img.original)
                page_data['text'] = (text + "\n" + table_text).strip()
                pages.append(page_data)
        # 處理跨頁內容
        print(f"    偵測跨頁內容...")
        pages = merge_cross_pages(pages)
        merged_count = sum(1 for p in pages if p.get('is_merged'))
        flowchart_count = sum(1 for p in pages if p.get('has_flowchart'))
        table_count = sum(1 for p in pages if p.get('has_tables'))
        if merged_count > 0:
            print(f"    ✅ 偵測到 {merged_count} 個跨頁內容，已自動合併")
        if flowchart_count > 0:
            print(f"    ✅ 偵測到 {flowchart_count} 頁含流程圖，已標記供 AI 視覺分析")
        if table_count > 0:
            print(f"    ✅ 偵測到 {table_count} 頁含表格，已結構化提取")
    except Exception as e:
        pages.append({
            'page_num': 0, 'text': f"[PDF提取錯誤] {pdf_path}: {str(e)}",
            'has_tables': False, 'has_flowchart': False,
            'flowchart_image': None, 'is_merged': False, 'merged_pages': []
        })
    return pages

def process_file(file_path: str) -> dict:
    """統一處理任何檔案（圖片或PDF）"""
    file_path = Path(file_path)
    extension = file_path.suffix.lower()
    result = {'file_name': file_path.name, 'file_path': str(file_path), 'file_type': extension, 'pages': []}
    if extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
        image = Image.open(str(file_path))
        text = ocr_pil_image(image)
        result['pages'] = [{'page_num': 1, 'text': text, 'has_tables': False,
                             'has_flowchart': True, 'flowchart_image': image,
                             'is_merged': False, 'merged_pages': []}]
    elif extension == '.pdf':
        result['pages'] = extract_pdf(str(file_path))
    else:
        result['pages'] = [{'page_num': 1, 'text': f'不支援的檔案格式: {extension}',
                             'has_tables': False, 'has_flowchart': False,
                             'flowchart_image': None, 'is_merged': False, 'merged_pages': []}]
    return result
