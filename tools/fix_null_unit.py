# -*- coding: utf-8 -*-
"""
fix_null_unit.py - 把指定 subject 中 unit 為 NULL 的題目補上 unit
================================================================
作用:讓主 app 的科目下拉選單能顯示沒有章節的科目。

用法:
    python tools\\fix_null_unit.py --subject 職業道德
    python tools\\fix_null_unit.py --subject 金融市場常識 --unit "全部題目"
"""
import argparse
import sqlite3
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DEFAULT_DB = r'platform\instance\insurance_exam.db'
DEFAULT_UNIT = '全部題目'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--subject', required=True, help='目標科目名稱')
    ap.add_argument('--unit', default=DEFAULT_UNIT, help='要填的 unit 值')
    ap.add_argument('--db', default=DEFAULT_DB)
    args = ap.parse_args()

    c = sqlite3.connect(args.db)
    cur = c.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM questions WHERE subject = ? AND unit IS NULL",
        (args.subject,)
    )
    before = cur.fetchone()[0]
    print(f"準備更新: subject='{args.subject}' AND unit IS NULL → {before} 題")

    if before == 0:
        print("沒有需要更新的題目,結束")
        c.close()
        return

    cur.execute(
        "UPDATE questions SET unit = ? WHERE subject = ? AND unit IS NULL",
        (args.unit, args.subject)
    )
    c.commit()
    print(f"已更新: {cur.rowcount} 題 → unit='{args.unit}'")

    cur.execute(
        "SELECT subject, unit, COUNT(*) FROM questions WHERE subject = ? GROUP BY subject, unit",
        (args.subject,)
    )
    print(f"\n'{args.subject}' 的分佈:")
    for row in cur.fetchall():
        print(f"  {row}")

    c.close()
    print("\n完成。請 Ctrl+F5 重新整理主 app。")


if __name__ == "__main__":
    main()
