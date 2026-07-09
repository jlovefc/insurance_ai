from pdfminer.high_level import extract_text

files = [
    'G:\\人身保險業務員 證照考試\\題庫總整理\\PDF檔（文字型 — 可以複製文字）\\答案在題目表格最後一欄的 \u201cAns\u201d 欄位\\JY電子檔筆記-【專業科目：人身保險-實務&法規】-V12.1.0.pdf',
    'G:\\人身保險業務員 證照考試\\題庫總整理\\PDF檔（文字型 — 可以複製文字）\\答案在題目表格最後一欄的 \u201c答案\u201d 欄位\\JY電子檔筆記-金融道德-V1.4.0.pdf',
]

for path in files:
    text = extract_text(path)
    out = path.replace(".pdf", ".txt")
    open(out, "w", encoding="utf-8").write(text)
    print(f"完成：{out}")
