# -*- coding: utf-8 -*-
"""
debug_p1_header.py - 看 p.1 表頭第 2 欄到底是什麼
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import pdfplumber

with pdfplumber.open("input/實務精選題.pdf") as pdf:
    for page_num in [1, 2, 8, 9, 10]:
        page = pdf.pages[page_num - 1]
        tables = page.extract_tables()
        print(f"\n=== p.{page_num} ===")
        for ti, tbl in enumerate(tables):
            if tbl and len(tbl) > 0:
                header = tbl[0]
                print(f"  表 {ti} 表頭:")
                for ci, cell in enumerate(header):
                    raw = repr(cell)
                    print(f"    欄 {ci}: {raw}")
