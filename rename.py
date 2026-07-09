import re
from pathlib import Path

input_path = Path(r'C:\insurance_ai\input')
renamed = 0
skipped = 0
errors = 0

for file_path in input_path.rglob('*'):
    if file_path.suffix.lower() not in ['.jpg','.jpeg','.png','.pdf']:
        continue
    match = re.match(r'P(\d+)', file_path.stem, re.IGNORECASE)
    if match:
        new_name = f'P{int(match.group(1)):03d}{file_path.suffix}'
        new_path = file_path.parent / new_name
        if new_path == file_path:
            skipped += 1
            continue
        try:
            file_path.rename(new_path)
            print(f'OK {file_path.name} -> {new_name}')
            renamed += 1
        except Exception as e:
            print(f'ERR {file_path.name}: {e}')
            errors += 1
    else:
        skipped += 1

print(f'\n完成! 改名:{renamed} 跳過:{skipped} 失敗:{errors}')