"""Plan and apply the approved inclusion of questions 4136 and 4137.

Evidence and approval:
- docs/answer_audit/missing_question_inclusion_plan_20260716.md
- docs/corrections/p90_q19_jy_missing_candidate_20260716.md
- docs/corrections/p89_q12_jy_premium_calculation_missing_candidate_20260716.md

The default mode is a read-only dry-run. Only an explicit --apply may write.
An apply additionally requires current, byte-identical JSON and SQLite backups.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sqlite3
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "all_questions.json"
DEFAULT_DATABASE = ROOT / "platform" / "instance" / "insurance_exam.db"
DEFAULT_JSON_BACKUP = (
    ROOT / "backups" / "all_questions_before_missing_questions_4136_4137.json"
)
DEFAULT_DATABASE_BACKUP = (
    ROOT / "backups" / "insurance_exam_before_missing_questions_4136_4137.db"
)

EXPECTED_JSON_COUNT = 4_122
EXPECTED_SQLITE_COUNT = 4_135
EXPECTED_MAX_ID = 4_135
TARGET_IDS = (4_136, 4_137)

QUESTIONS: tuple[dict[str, Any], ...] = (
    {
        "id": 4_136,
        "case_id": "MISS-20260716-0004",
        "subject": "B 保險實務-分類",
        "unit": "03 保險費架構、解約金、準備金、保單紅利",
        "content": "若預定死亡率降低，定期保險的保險費就會？",
        "options": ["一樣", "不一定", "便宜", "貴"],
        "correct_answer": "3",
        "explanation": (
            "其他條件不變時，預定死亡率降低代表預期死亡給付成本下降，"
            "定期保險保費因而降低。"
        ),
        "evidence_file": (
            "docs/corrections/p90_q19_jy_missing_candidate_20260716.md"
        ),
    },
    {
        "id": 4_137,
        "case_id": "MISS-20260716-0001",
        "subject": "B 保險實務-分類",
        "unit": "03 保險費架構、解約金、準備金、保單紅利",
        "content": (
            "一萬名30歲的男性各投保100萬的死亡保險（保險期間1年），"
            "若生命表顯示30歲男性死亡率為千分之二，"
            "請問每人該付多少純保費？"
        ),
        "options": ["1仟元", "2仟元", "3仟元", "4仟元"],
        "correct_answer": "2",
        "explanation": (
            "10000 × 2/1000 = 20人\n"
            "20 × 1000000 / 10000 = 2000"
        ),
        "evidence_file": (
            "docs/corrections/"
            "p89_q12_jy_premium_calculation_missing_candidate_20260716.md"
        ),
    },
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dry-run or apply the approved inclusion of IDs 4136 and 4137."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write both approved questions after all backup and safety checks.",
    )
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


def load_json_bank(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not all(isinstance(row, dict) for row in data):
        raise RuntimeError("all_questions.json must contain a list of objects")
    return data


def json_record(question: dict[str, Any]) -> dict[str, Any]:
    """Return only the existing formal JSON schema fields."""
    return {
        "id": question["id"],
        "subject": question["subject"],
        "unit": question["unit"],
        "content": question["content"],
        "options": question["options"],
        "correct_answer": question["correct_answer"],
    }


def printable_record(question: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": question["id"],
        "case_id": question["case_id"],
        "subject": question["subject"],
        "unit": question["unit"],
        "content": question["content"],
        "options": question["options"],
        "correct_answer": question["correct_answer"],
        "explanation": question["explanation"],
        "evidence_file": question["evidence_file"],
    }


def open_database(path: Path, *, read_only: bool) -> sqlite3.Connection:
    if read_only:
        connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    else:
        connection = sqlite3.connect(path)
    return connection


def validate_json_before(rows: list[dict[str, Any]]) -> None:
    ids = [row.get("id") for row in rows]
    if len(rows) != EXPECTED_JSON_COUNT:
        raise RuntimeError(
            f"JSON count is {len(rows)}; expected {EXPECTED_JSON_COUNT}"
        )
    if max(ids) != EXPECTED_MAX_ID:
        raise RuntimeError(f"JSON max(id) is {max(ids)}; expected {EXPECTED_MAX_ID}")
    occupied = sorted(set(ids).intersection(TARGET_IDS))
    if occupied:
        raise RuntimeError(f"Target IDs already exist in JSON: {occupied}")
    existing_contents = {row.get("content") for row in rows}
    duplicates = [q["id"] for q in QUESTIONS if q["content"] in existing_contents]
    if duplicates:
        raise RuntimeError(
            f"Exact target content already exists in JSON for proposed IDs: {duplicates}"
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
    placeholders = ",".join("?" for _ in TARGET_IDS)
    occupied = connection.execute(
        f"SELECT id FROM questions WHERE id IN ({placeholders}) ORDER BY id",
        TARGET_IDS,
    ).fetchall()
    if occupied:
        raise RuntimeError(f"Target IDs already exist in SQLite: {occupied}")
    for question in QUESTIONS:
        duplicate = connection.execute(
            "SELECT id FROM questions WHERE content = ? LIMIT 1",
            (question["content"],),
        ).fetchone()
        if duplicate is not None:
            raise RuntimeError(
                f"Exact target content already exists in SQLite as ID {duplicate[0]}"
            )
    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    if integrity != "ok":
        raise RuntimeError(f"SQLite integrity_check failed before apply: {integrity}")


def validate_backup(live: Path, backup: Path, label: str) -> None:
    if not backup.is_file():
        raise RuntimeError(f"{label} backup is required but missing: {backup}")
    live_hash = sha256(live)
    backup_hash = sha256(backup)
    if backup_hash != live_hash:
        raise RuntimeError(
            f"{label} backup is not byte-identical to the current live file: "
            f"live={live_hash}, backup={backup_hash}"
        )
    print(f"{label} backup verified: {backup}")
    print(f"{label} backup sha256: {backup_hash}")


def write_json_bank(path: Path, rows: list[dict[str, Any]]) -> None:
    temporary = path.with_name(path.name + ".4136_4137.tmp")
    if temporary.exists():
        raise RuntimeError(f"Refusing to overwrite stale temporary file: {temporary}")
    try:
        text = json.dumps(rows, ensure_ascii=False, indent=2).replace("\n", "\r\n")
        temporary.write_text(text, encoding="utf-8", newline="")
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def insert_sqlite_questions(connection: sqlite3.Connection) -> None:
    for question in QUESTIONS:
        cursor = connection.execute(
            """
            INSERT INTO questions
                (id, content, options, correct_answer, unit, explanation, subject)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                question["id"],
                question["content"],
                json.dumps(question["options"], ensure_ascii=False),
                question["correct_answer"],
                question["unit"],
                question["explanation"],
                question["subject"],
            ),
        )
        if cursor.rowcount != 1:
            raise RuntimeError(
                f"SQLite insert for ID {question['id']} affected {cursor.rowcount} rows"
            )


def validate_after(
    rows: list[dict[str, Any]], connection: sqlite3.Connection
) -> None:
    if len(rows) != EXPECTED_JSON_COUNT + 2:
        raise RuntimeError(f"JSON post-apply count is {len(rows)}; expected 4124")
    by_id = {row.get("id"): row for row in rows}
    for question in QUESTIONS:
        if by_id.get(question["id"]) != json_record(question):
            raise RuntimeError(f"JSON ID {question['id']} does not match approved data")

    count, maximum = connection.execute(
        "SELECT COUNT(*), MAX(id) FROM questions"
    ).fetchone()
    if count != EXPECTED_SQLITE_COUNT + 2 or maximum != TARGET_IDS[-1]:
        raise RuntimeError(
            f"Unexpected SQLite post-apply state: count={count}, max(id)={maximum}"
        )
    for question in QUESTIONS:
        row = connection.execute(
            """
            SELECT subject, unit, content, options, correct_answer, explanation
            FROM questions WHERE id = ?
            """,
            (question["id"],),
        ).fetchone()
        expected = (
            question["subject"],
            question["unit"],
            question["content"],
            json.dumps(question["options"], ensure_ascii=False),
            question["correct_answer"],
            question["explanation"],
        )
        if row != expected:
            raise RuntimeError(f"SQLite ID {question['id']} does not match approved data")
    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    if integrity != "ok":
        raise RuntimeError(f"SQLite integrity_check failed after apply: {integrity}")
    print(f"post-apply JSON count: {len(rows)}")
    print(f"post-apply SQLite count: {count}")
    print(f"post-apply SQLite max(id): {maximum}")
    print(f"post-apply integrity_check: {integrity}")


def main() -> int:
    args = parse_args()
    json_path = args.json.expanduser().resolve()
    database_path = args.database.expanduser().resolve()
    json_backup = args.json_backup.expanduser().resolve()
    database_backup = args.database_backup.expanduser().resolve()

    if not json_path.is_file():
        raise FileNotFoundError(f"JSON question bank not found: {json_path}")
    if not database_path.is_file():
        raise FileNotFoundError(f"SQLite question bank not found: {database_path}")
    if tuple(question["id"] for question in QUESTIONS) != TARGET_IDS:
        raise RuntimeError("Script targets are not exactly IDs 4136 and 4137")

    before_hashes = {
        "all_questions.json": sha256(json_path),
        "insurance_exam.db": sha256(database_path),
    }
    mode = "apply" if args.apply else "dry-run"
    print(f"mode: {mode}")
    print(f"json: {json_path}")
    print(f"database: {database_path}")
    print(f"JSON sha256 before: {before_hashes['all_questions.json']}")
    print(f"SQLite sha256 before: {before_hashes['insurance_exam.db']}")

    rows = load_json_bank(json_path)
    validate_json_before(rows)
    read_connection = open_database(database_path, read_only=True)
    try:
        validate_sqlite_before(read_connection)
    finally:
        read_connection.close()

    print(f"JSON count before: {len(rows)}")
    print(f"JSON max(id) before: {max(row['id'] for row in rows)}")
    print(f"SQLite count before: {EXPECTED_SQLITE_COUNT}")
    print(f"SQLite max(id) before: {EXPECTED_MAX_ID}")
    print("approved questions:")
    for question in QUESTIONS:
        print(json.dumps(printable_record(question), ensure_ascii=False, indent=2))

    if not args.apply:
        after_hashes = {
            "all_questions.json": sha256(json_path),
            "insurance_exam.db": sha256(database_path),
        }
        if after_hashes != before_hashes:
            raise RuntimeError(
                f"Dry-run unexpectedly changed a formal source: {after_hashes}"
            )
        print("dry-run successful: no files were written")
        print("all_questions.json hash unchanged: true")
        print("SQLite hash unchanged: true")
        return 0

    validate_backup(json_path, json_backup, "JSON")
    validate_backup(database_path, database_backup, "SQLite")

    connection = open_database(database_path, read_only=False)
    json_replaced = False
    try:
        connection.execute("BEGIN IMMEDIATE")
        insert_sqlite_questions(connection)
        updated_rows = [*rows, *(json_record(question) for question in QUESTIONS)]
        write_json_bank(json_path, updated_rows)
        json_replaced = True
        validate_after(updated_rows, connection)
        connection.commit()
        print("apply successful: both formal sources contain IDs 4136 and 4137")
        return 0
    except Exception:
        connection.rollback()
        if json_replaced:
            shutil.copyfile(json_backup, json_path)
            if sha256(json_path) != sha256(json_backup):
                raise RuntimeError("JSON rollback from backup failed")
            print("apply failed: JSON restored from verified backup")
        print("apply failed: SQLite transaction rolled back")
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
