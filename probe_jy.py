import pypdf
reader = pypdf.PdfReader(r'C:\insurance_ai\jy_jinde.pdf')
for i in range(len(reader.pages)):
    text = reader.pages[i].extract_text()
    if '職業道德' in text and '練習題' in text:
        print(f'=== 第{i+1}頁 ===')
        print(repr(text[:600]))
        print()
