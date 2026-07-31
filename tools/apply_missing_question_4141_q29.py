"""Controlled inclusion of the approved versioned JY unit03 Q29 as ID4141.

Default execution is a read-only dry-run. Only an explicit --apply may write,
and apply mode requires byte-identical JSON and SQLite backups.

References:
- docs/answer_audit/jy_unit03_q29_official_law_support_20260716.md
- docs/answer_audit/jy_unit03_q29_versioned_question_draft_20260716.md
- docs/answer_audit/jy_unit03_q29_inclusion_plan_20260716.md
- docs/corrections/p90_q29_jy_missing_candidate_20260716.md
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "all_questions.json"
DEFAULT_DATABASE = ROOT / "platform" / "instance" / "insurance_exam.db"
DEFAULT_JSON_BACKUP = (
    ROOT / "backups" / "all_questions_before_q29_4141_inclusion_20260716.json"
)
DEFAULT_DATABASE_BACKUP = (
    ROOT / "backups" / "insurance_exam_before_q29_4141_inclusion_20260716.db"
)

EXPECTED_JSON_COUNT = 4_127
EXPECTED_SQLITE_COUNT = 4_140
EXPECTED_MAX_ID = 4_140
TARGET_ID = 4_141

QUESTION: dict[str, Any] = {
    "id": TARGET_ID,
    "case_id": "MISS-20260716-0008",
    "subject": "B 保險實務-分類",
    "unit": "03 保險費架構、解約金、準備金、保單紅利",
    "content": (
        "依金融監督管理委員會民國113年7月16日發布、同年11月1日生效之"
        "金管保壽字第11304922511號令，人身保險業辦理不分紅人壽保險商品"
        "業務時，下列有關銷售文件之敘述何者正確？"
    ),
    "options": [
        "不得單獨強調保費預定利率",
        "得以保單報酬率與銀行存款報酬率比較作為主要招攬訴求",
        "無須說明本保險不參加紅利分配及無紅利給付項目",
        "得將保費預定利率作為唯一銷售重點",
    ],
    "correct_answer": "1",
    "explanation": (
        "依金融監督管理委員會民國113年7月16日金管保壽字第11304922511號令，"
        "人身保險業辦理不分紅人壽保險商品業務，其銷售文件不得單獨強調保費"
        "預定利率，亦不得以保單報酬率與其他金融商品比較等方式誤導保戶；銷售"
        "文件、保險單面頁及保險單條款並應明確說明本保險為不分紅保險單、不參加"
        "紅利分配且無紅利給付項目。該令自民國113年11月1日生效，因此答案為第1項。"
    ),
    "evidence_file": "docs/corrections/p90_q29_jy_missing_candidate_20260716.md",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dry-run or apply the approved inclusion of Q29 as ID4141."
    )
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--json-backup", type=Path, default=DEFAULT_JSON_BACKUP)
    parser.add_argument(
        "--database-backup", type=Path, default=DEFAULT_DATABASE_BACKUP
    )
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_hash(value: Any) -> str:
    data = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def load_json_bank(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig") as stream:
        data = json.load(stream)
    if not isinstance(data, list) or not all(isinstance(row, dict) for row in data):
        raise RuntimeError("all_questions.json must contain a list of objects")
    return data


def json_record() -> dict[str, Any]:
    return {
        "id": QUESTION["id"],
        "subject": QUESTION["subject"],
        "unit": QUESTION["unit"],
        "content": QUESTION["content"],
        "options": list(QUESTION["options"]),
        "correct_answer": QUESTION["correct_answer"],
        "explanation": QUESTION["explanation"],
    }


def open_database(path: Path, *, read_only: bool) -> sqlite3.Connection:
    if read_only:
        connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    else:
        connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def validate_json_before(rows: list[dict[str, Any]]) -> None:
    ids = [int(row["id"]) for row in rows]
    if len(rows) != EXPECTED_JSON_COUNT:
        raise RuntimeError(
            f"JSON count is {len(rows)}; expected {EXPECTED_JSON_COUNT}"
        )
    if max(ids) != EXPECTED_MAX_ID:
        raise RuntimeError(
            f"JSON max(id) is {max(ids)}; expected {EXPECTED_MAX_ID}"
        )
    if TARGET_ID in ids:
        raise RuntimeError(f"Target ID {TARGET_ID} already exists in JSON")
    exact = [
        row["id"]
        for row in rows
        if str(row.get("content", "")).strip() == QUESTION["content"]
        and row.get("options") == QUESTION["options"]
    ]
    if exact:
        raise RuntimeError(
            f"Exact Q29 content and options already exist in JSON as IDs {exact}"
        )


def validate_sqlite_before(connection: sqlite3.Connection) -> None:
    count, maximum = connection.execute(
        "SELECT COUNT(*), MAX(id) FROM questions"
    ).fetchone()
    if count != EXPECTED_SQLITE_COUNT:
        raise RuntimeError(
            f"SQLite count is {count}; expected {EXPECTED_SQLITE_COUNT}"
        )
    if maximum != EXPECTED_MAX_ID:
        raise RuntimeError(
            f"SQLite max(id) is {maximum}; expected {EXPECTED_MAX_ID}"
        )
    if connection.execute(
        "SELECT 1 FROM questions WHERE id = ?", (TARGET_ID,)
    ).fetchone():
        raise RuntimeError(f"Target ID {TARGET_ID} already exists in SQLite")

    candidates = connection.execute(
        "SELECT id, options FROM questions WHERE TRIM(content) = ?",
        (QUESTION["content"],),
    ).fetchall()
    exact_ids: list[int] = []
    for row in candidates:
        try:
            options = json.loads(row["options"])
        except (TypeError, json.JSONDecodeError):
            options = row["options"]
        if options == QUESTION["options"]:
            exact_ids.append(row["id"])
    if exact_ids:
        raise RuntimeError(
            f"Exact Q29 content and options already exist in SQLite as IDs {exact_ids}"
        )

    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    if integrity != "ok":
        raise RuntimeError(f"SQLite integrity_check failed before apply: {integrity}")


def validate_backup(live: Path, backup: Path, label: str) -> None:
    if not backup.is_file():
        raise RuntimeError(f"{label} backup is required but missing: {backup}")
    live_hash = sha256(live)
    backup_hash = sha256(backup)
    if live_hash != backup_hash:
        raise RuntimeError(
            f"{label} backup is not byte-identical to live file: "
            f"live={live_hash}, backup={backup_hash}"
        )


def sqlite_non_target_hash(connection: sqlite3.Connection) -> str:
    rows = connection.execute(
        """
        SELECT id, content, options, correct_answer, unit, explanation,
               difficulty, created_at, subject, is_important
        FROM questions WHERE id != ? ORDER BY id
        """,
        (TARGET_ID,),
    ).fetchall()
    return stable_hash([list(row) for row in rows])


def insert_sqlite_question(connection: sqlite3.Connection) -> None:
    cursor = connection.execute(
        """
        INSERT INTO questions
            (id, content, options, correct_answer, unit, explanation, subject)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            TARGET_ID,
            QUESTION["content"],
            json.dumps(QUESTION["options"], ensure_ascii=False),
            QUESTION["correct_answer"],
            QUESTION["unit"],
            QUESTION["explanation"],
            QUESTION["subject"],
        ),
    )
    if cursor.rowcount != 1:
        raise RuntimeError(f"SQLite insert affected {cursor.rowcount} rows")


def write_json_bank(path: Path, rows: list[dict[str, Any]]) -> None:
    temporary = path.with_name(path.name + ".4141_q29.tmp")
    if temporary.exists():
        raise RuntimeError(f"Refusing to overwrite stale temporary file: {temporary}")
    try:
        with temporary.open("w", encoding="utf-8", newline="") as stream:
            json.dump(rows, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def validate_after(
    rows: list[dict[str, Any]],
    connection: sqlite3.Connection,
    *,
    json_other_hash_before: str,
    sqlite_other_hash_before: str,
) -> None:
    if len(rows) != EXPECTED_JSON_COUNT + 1:
        raise RuntimeError("Unexpected JSON count after apply")
    matches = [row for row in rows if int(row.get("id", -1)) == TARGET_ID]
    if matches != [json_record()]:
        raise RuntimeError("JSON ID4141 does not match the approved record")
    if stable_hash([row for row in rows if int(row.get("id", -1)) != TARGET_ID]) != json_other_hash_before:
        raise RuntimeError("A non-target JSON question changed")

    count, maximum = connection.execute(
        "SELECT COUNT(*), MAX(id) FROM questions"
    ).fetchone()
    if (count, maximum) != (EXPECTED_SQLITE_COUNT + 1, TARGET_ID):
        raise RuntimeError(f"Unexpected SQLite count/max: {(count, maximum)}")
    row = connection.execute(
        """
        SELECT id, subject, unit, content, options, correct_answer, explanation
        FROM questions WHERE id = ?
        """,
        (TARGET_ID,),
    ).fetchone()
    if row is None:
        raise RuntimeError("SQLite ID4141 was not inserted")
    actual = dict(row)
    actual["options"] = json.loads(actual["options"])
    expected = json_record()
    if actual != expected:
        raise RuntimeError(f"SQLite ID4141 mismatch: {actual!r}")
    if sqlite_non_target_hash(connection) != sqlite_other_hash_before:
        raise RuntimeError("A non-target SQLite question changed")
    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    if integrity != "ok":
        raise RuntimeError(f"SQLite integrity_check failed after apply: {integrity}")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    args = parse_args()

    json_path = args.json.expanduser().resolve()
    database_path = args.database.expanduser().resolve()
    for path, label in ((json_path, "JSON"), (database_path, "SQLite")):
        if not path.is_file():
            raise FileNotFoundError(f"{label} file not found: {path}")

    apply_mode = bool(args.apply)
    json_hash_before = sha256(json_path)
    database_hash_before = sha256(database_path)
    rows = load_json_bank(json_path)
    connection = open_database(database_path, read_only=not apply_mode)
    original_json_bytes: bytes | None = None

    print(f"mode: {'apply' if apply_mode else 'dry-run'}")
    print(f"JSON sha256 before: {json_hash_before}")
    print(f"SQLite sha256 before: {database_hash_before}")

    try:
        validate_json_before(rows)
        validate_sqlite_before(connection)
        print("planned addition:")
        print(json.dumps(QUESTION, ensure_ascii=False, indent=2))

        if not apply_mode:
            connection.close()
            connection = None
            json_hash_after = sha256(json_path)
            database_hash_after = sha256(database_path)
            print(f"JSON sha256 after: {json_hash_after}")
            print(f"SQLite sha256 after: {database_hash_after}")
            if json_hash_after != json_hash_before:
                raise RuntimeError("Dry-run changed all_questions.json")
            if database_hash_after != database_hash_before:
                raise RuntimeError("Dry-run changed SQLite")
            print("dry-run successful: ID4141 was not written")
            return 0

        validate_backup(
            json_path, args.json_backup.expanduser().resolve(), "JSON"
        )
        validate_backup(
            database_path,
            args.database_backup.expanduser().resolve(),
            "SQLite",
        )
        json_other_hash_before = stable_hash(rows)
        sqlite_other_hash_before = sqlite_non_target_hash(connection)
        original_json_bytes = json_path.read_bytes()

        connection.execute("BEGIN IMMEDIATE")
        new_rows = [*rows, json_record()]
        insert_sqlite_question(connection)
        validate_after(
            new_rows,
            connection,
            json_other_hash_before=json_other_hash_before,
            sqlite_other_hash_before=sqlite_other_hash_before,
        )
        write_json_bank(json_path, new_rows)
        connection.commit()
        original_json_bytes = None
        print("apply successful: ID4141 added to JSON and SQLite")
        return 0
    except Exception:
        if connection is not None and apply_mode:
            connection.rollback()
        if original_json_bytes is not None:
            json_path.write_bytes(original_json_bytes)
        raise
    finally:
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
