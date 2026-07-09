# -*- coding: utf-8 -*-
app_path = r'C:\insurance_ai\platform\app.py'

with open(app_path, encoding='utf-8') as f:
    lines = f.readlines()

# 清理所有之前失敗插入的行，重新來過
clean_lines = []
for line in lines:
    stripped = line.lstrip()
    if stripped.startswith('_letter_to_num') or stripped.startswith('_norm_answer'):
        continue
    if '_norm_answer == str(question.correct_answer)' in line:
        indent = '        '
        clean_lines.append(indent + "is_correct = user_answer_str == str(question.correct_answer).strip()\n")
        continue
    clean_lines.append(line)

# 重新插入正確的修改
final_lines = []
for line in clean_lines:
    final_lines.append(line)
    if "user_answer_str = str(ans.get('answer', '')).strip()" in line:
        indent = '        '
        final_lines.append(indent + "_letter_to_num = {'A':'1','B':'2','C':'3','D':'4','E':'5'}\n")
        final_lines.append(indent + "_norm_answer = _letter_to_num.get(user_answer_str.upper(), user_answer_str)\n")

# 把 is_correct 改用 _norm_answer
result = []
for line in final_lines:
    if "is_correct = user_answer_str == str(question.correct_answer).strip()" in line:
        indent = '        '
        result.append(indent + "is_correct = _norm_answer == str(question.correct_answer).strip()\n")
    else:
        result.append(line)

with open(app_path, 'w', encoding='utf-8') as f:
    f.writelines(result)

import py_compile
try:
    py_compile.compile(app_path, doraise=True)
    print('語法檢查通過，可以啟動伺服器')
except py_compile.PyCompileError as e:
    print(f'語法錯誤: {e}')

with open(app_path, encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines[309:320], start=310):
    print(f'{i}: {repr(line.rstrip())}')
