# -*- coding: utf-8 -*-
"""
probe_pdf.py - PDF 內部結構探測
================================
看 PDF 有幾頁、每頁文字長什麼樣、有沒有表格,
讓我決定怎麼寫 parser。

用法:
    python tools\\probe_pdf.py input\\JY-人身保險.pdf

需要的套件: pdfplumber (比 pypdf 更會處理表格)
若沒裝會自動提示。
"""
import argparse
import sys
import os

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", help="PDF 路徑")
    ap.add_argument("--pages", type=int, default=3, help="探測前幾頁")
    args = ap.parse_args()

    if not os.path.exists(args.pdf):
        print(f"X 找不到 {args.pdf}")
        sys.exit(1)

    # 嘗試 import pdfplumber
    try:
        import pdfplumber
    except ImportError:
        print("X 沒裝 pdfplumber,請執行:")
        print("    pip install pdfplumber")
        sys.exit(1)

    print(f"探測中: {args.pdf}")
    print(f"檔案大小: {os.path.getsize(args.pdf):,} bytes\n")

    with pdfplumber.open(args.pdf) as pdf:
        total = len(pdf.pages)
        print(f"總頁數: {total}\n")
        print("=" * 70)

        for i in range(min(args.pages, total)):
            page = pdf.pages[i]
            print(f"\n【第 {i+1} 頁】")
            print("─" * 70)

            # 1. 純文字
            text = page.extract_text() or "(無文字)"
            # 截斷顯示
            if len(text) > 1500:
                print(text[:1500])
                print(f"... (此頁文字共 {len(text)} 字,只顯示前 1500)")
            else:
                print(text)

            # 2. 表格偵測
            tables = page.extract_tables()
            print(f"\n[表格偵測] 此頁找到 {len(tables)} 個表格")
            for ti, tbl in enumerate(tables):
                print(f"  表格 {ti+1}: {len(tbl)} 列 × "
                      f"{len(tbl[0]) if tbl else 0} 欄")
                # 顯示前 3 列
                for ri, row in enumerate(tbl[:3]):
                    cells = [str(c)[:30] if c else "" for c in row]
                    print(f"    [列{ri+1}] {cells}")
                if len(tbl) > 3:
                    print(f"    ... (共 {len(tbl)} 列)")

            print("=" * 70)

        # 抽樣中間頁面,看正文題目長相
        if total > 5:
            mid = total // 2
            print(f"\n\n【抽樣中間頁:第 {mid+1} 頁】")
            print("─" * 70)
            page = pdf.pages[mid]
            text = page.extract_text() or ""
            if len(text) > 1500:
                print(text[:1500])
                print(f"... ({len(text)} 字)")
            else:
                print(text)
            tables = page.extract_tables()
            print(f"\n表格: {len(tables)}")
            if tables and tables[0]:
                first_tbl = tables[0]
                print(f"  第一個表格: {len(first_tbl)} 列 × {len(first_tbl[0])} 欄")
                # 顯示前 3 列
                for ri, row in enumerate(first_tbl[:3]):
                    cells = [str(c)[:40] if c else "" for c in row]
                    print(f"    [列{ri+1}] {cells}")

    print("\n探測完成。請把上面整段輸出貼給我。")


if __name__ == "__main__":
    main()
