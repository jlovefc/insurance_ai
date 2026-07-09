import json
with open(r'C:\insurance_ai\output\structured_data.json', encoding='utf-8') as f:
    data = json.load(f)
print(f'總檔案數：{len(data)}')
for d in data:
    print(d['file_name'], '→', len(d.get('structured_pages',[])), '頁')