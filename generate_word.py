import json, sys, re, traceback
sys.path.insert(0, r'C:\insurance_ai\tools')
from output_tool import create_word_document

def natural_sort_key(item):
    name = item['file_name']
    numbers = re.findall(r'\d+', name)
    return int(numbers[0]) if numbers else 0

with open(r'C:\insurance_ai\output\structured_data.json', encoding='utf-8') as f:
    data = json.load(f)

# 按頁碼數字正確排序
data_sorted = sorted(data, key=natural_sort_key)

print(f"總筆數：{len(data_sorted)}")
print(f"前5筆：{[d['file_name'] for d in data_sorted[:5]]}")
print(f"後5筆：{[d['file_name'] for d in data_sorted[-5:]]}")
print(f"確認順序正確後，開始生成 Word...")

try:
    result = create_word_document(
        data_sorted,
        r'C:\insurance_ai\output\保險員證照考試教材整理.docx'
    )
    print(f"✅ 完成：{result}")
except Exception as e:
    print(f"❌ 失敗：{e}")
    traceback.print_exc()