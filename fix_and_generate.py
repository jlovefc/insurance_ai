import json, sys, re
sys.path.insert(0, r'C:\insurance_ai\tools')
from output_tool import create_word_document

def get_page_num(item):
    numbers = re.findall(r'\d+', item['file_name'])
    return int(numbers[0]) if numbers else 0

# 讀取原始 JSON
with open(r'C:\insurance_ai\output\structured_data.json', encoding='utf-8') as f:
    data = json.load(f)

# 正確排序
data_sorted = sorted(data, key=get_page_num)

# 確認排序結果
print("排序後完整順序：")
for i, d in enumerate(data_sorted):
    print(f"  [{i+1}] {d['file_name']}")

# 存回已排序的 JSON
with open(r'C:\insurance_ai\output\structured_data_sorted.json', 'w', encoding='utf-8') as f:
    json.dump(data_sorted, f, ensure_ascii=False, indent=2)
print("\n已儲存排序後的 JSON")

# 生成 Word
print("\n生成 Word...")
result = create_word_document(
    data_sorted,
    r'C:\insurance_ai\output\保險員證照考試教材整理_排序版.docx'
)
print(f"✅ 完成：{result}")