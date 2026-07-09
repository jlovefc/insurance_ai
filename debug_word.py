import json, sys, os
sys.path.insert(0, r'C:\insurance_ai\tools')

# 確認載入的是新版
import output_tool
print(f"output_tool 路徑：{output_tool.__file__}")

with open(r'C:\insurance_ai\output\structured_data.json', encoding='utf-8') as f:
    data = json.load(f)

print(f"JSON 總筆數：{len(data)}")
print(f"前3筆：{[d['file_name'] for d in data[:3]]}")
print(f"後3筆：{[d['file_name'] for d in data[-3:]]}")

# 確認 P123 的資料內容
for d in data:
    if d['file_name'] == 'P123.jpg':
        print(f"\nP123 資料：")
        print(f"  structured_pages 數量：{len(d.get('structured_pages', []))}")
        if d.get('structured_pages'):
            print(f"  第一頁主題：{d['structured_pages'][0].get('main_topic', '無')}")