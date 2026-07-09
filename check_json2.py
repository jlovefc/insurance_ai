import json

with open(r'C:\insurance_ai\output\structured_data.json', encoding='utf-8') as f:
    data = json.load(f)

print(f'JSON 總筆數：{len(data)}')
print(f'所有檔名：')
for d in data:
    print(f"  {d['file_name']}")