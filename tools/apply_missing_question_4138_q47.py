"""Dry-run or apply the approved inclusion plan for Q47 as ID 4138.

Evidence and planning:
- docs/answer_audit/jy_unit03_q47_equivalence_decision_20260716.md
- docs/answer_audit/jy_unit03_q47_inclusion_plan_20260716.md
- docs/corrections/p91_q47_jy_missing_candidate_20260716.md

The default mode is a read-only dry-run. Only an explicit --apply may write.
Apply mode additionally requires byte-identical JSON and SQLite backups.
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
    ROOT
    / "backups"
    / "all_questions_before_missing_question_4138_q47_20260716.json"
)
DEFAULT_DATABASE_BACKUP = (
    ROOT
    / "backups"
    / "insurance_exam_before_missing_question_4138_q47_20260716.db"
)

EXPECTED_JSON_COUNT = 4_124
EXPECTED_SQLITE_COUNT = 4_137
EXPECTED_MAX_ID = 4_137
TARGET_ID = 4_138

QUESTION: dict[str, Any] = {
    "id": TARGET_ID,
    "case_id": "MISS-20260716-0013",
    "subject": "B 保險實務-分類",
    "unit": "03 保險費架構、解約金、準備金、保單紅利",
    "content": "保單紅利支付的方法有？",
    "options": ["BCD", "ACD", "ABCD", "ABC"],
    "correct_answer": "3",
    "explanation": (
        "保單紅利支付方法包括購買增額繳清金額、積存方法、抵繳保費及"
        "現金支付方法，因此答案為ABCD。"
    ),
    "evidence_file": "docs/corrections/p91_q47_jy_missing_candidate_20260716.md",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dry-run or apply the approved inclusion of Q47 as ID 4138."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Add ID 4138 after all backup and safety checks.",
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


def stable_hash(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_json_bank(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not all(isinstance(row, dict) for row in data):
        raise RuntimeError("all_questions.json must contain a list of objects")
    return data


def json_record() -> dict[str, Any]:
    """Return ID 4138 using only the existing formal JSON schema."""
    return {
        "id": QUESTION["id"],
        "subject": QUESTION["subject"],
        "unit": QUESTION["unit"],
        "content": QUESTION["content"],
        "options": QUESTION["options"],
        "correct_answer": QUESTION["correct_answer"],
    }


def printable_record() -> dict[str, Any]:
    return dict(QUESTION)


def open_database(path: Path, *, read_only: bool) -> sqlite3.Connection:
    if read_only:
        connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    else:
        connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def validate_json_before(rows: list[dict[str, Any]]) -> None:
    ids = [row.get("id") for row in rows]
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
        row.get("id")
        for row in rows
        if row.get("content") == QUESTION["content"]
        and row.get("options") == QUESTION["options"]
    ]
    if exact:
        raise RuntimeError(
            f"Exact Q47 content and options already exist in JSON as IDs {exact}"
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
        "SELECT id, options FROM questions WHERE content = ?",
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
            f"Exact Q47 content and options already exist in SQLite as IDs {exact_ids}"
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
            f"{label} backup is not byte-identical to the live file: "
            f"live={live_hash}, backup={backup_hash}"
        )
    print(f"{label} backup verified: {backup}")
    print(f"{label} backup sha256: {backup_hash}")


def write_json_bank(path: Path, rows: list[dict[str, Any]]) -> None:
    temporary = path.with_name(path.name + ".4138_q47.tmp")
    if temporary.exists():
        raise RuntimeError(f"Refusing to overwrite stale temporary file: {temporary}")
    try:
        text = json.dumps(rows, ensure_ascii=False, indent=2).replace("\n", "\r\n")
        temporary.write_text(text, encoding="utf-8", newline="")
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def insert_sqlite_question(connection: sqlite3.Connection) -> None:
    cursor = connection.execute(
        """
        INSERT INTO questions
            (id, content, options, correct_answer, unit, explanation, subject)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            QUESTION["id"],
            QUESTION["content"],
            json.dumps(QUESTION["options"], ensure_ascii=False),
            QUESTION["correct_answer"],
            QUESTION["unit"],
            QUESTION["explanation"],
            QUESTION["subject"],
        ),
    )
    if cursor.rowcount != 1:
        raise RuntimeError(
            f"SQLite insert for ID {TARGET_ID} affected {cursor.rowcount} rows"
        )


def sqlite_non_target_hash(connection: sqlite3.Connection) -> str:
    rows = connection.execute(
        """
        SELECT id, content, options, correct_answer, unit, explanation,
               difficulty, created_at, subject, is_important
        FROM questions
        WHERE id != ?
        ORDER BY id
        """,
        (TARGET_ID,),
    ).fetchall()
    return stable_hash([list(row) for row in rows])


def validate_after(
    rows: list[dict[str, Any]],
    connection: sqlite3.Connection,
    *,
    json_other_hash_before: str,
    sqlite_other_hash_before: str,
) -> None:
    if len(rows) != EXPECTED_JSON_COUNT + 1:
        raise RuntimeError(
            f"JSON post-apply count is {len(rows)}; expected {EXPECTED_JSON_COUNT + 1}"
        )
    json_matches = [row for row in rows if row.get("id") == TARGET_ID]
    if json_matches != [json_record()]:
        raise RuntimeError("JSON ID 4138 does not match the approved record")

    count, maximum = connection.execute(
        "SELECT COUNT(*), MAX(id) FROM questions"
    ).fetchone()
    if count != EXPECTED_SQLITE_COUNT + 1 or maximum != TARGET_ID:
        raise RuntimeError(
            f"SQLite post-apply count/max is {(count, maximum)}; "
            f"expected {(EXPECTED_SQLITE_COUNT + 1, TARGET_ID)}"
        )
    row = connection.execute(
        """
        SELECT id, subject, unit, content, options, correct_answer, explanation
        FROM questions WHERE id = ?
        """,
        (TARGET_ID,),
    ).fetchone()
    if row is None:
        raise RuntimeError("SQLite ID 4138 was not inserted")
    actual = dict(row)
    actual["options"] = json.loads(actual["options"])
    expected = {
        "id": QUESTION["id"],
        "subject": QUESTION["subject"],
        "unit": QUESTION["unit"],
        "content": QUESTION["content"],
        "options": QUESTION["options"],
        "correct_answer": QUESTION["correct_answer"],
        "explanation": QUESTION["explanation"],
    }
    if actual != expected:
        raise RuntimeError(f"SQLite ID 4138 mismatch: {actual!r}")

    json_other_hash_after = stable_hash(
        [row for row in rows if row.get("id") != TARGET_ID]
    )
    if json_other_hash_after != json_other_hash_before:
        raise RuntimeError("A non-target JSON question changed")
    if sqlite_non_target_hash(connection) != sqlite_other_hash_before:
        raise RuntimeError("A non-target SQLite question changed")

    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    if integrity != "ok":
        raise RuntimeError(f"SQLite integrity_check failed after apply: {integrity}")
    print(f"JSON post-apply count: {len(rows)}")
    print(f"SQLite post-apply count: {count}")
    print(f"SQLite integrity_check: {integrity}")
    print("non-target questions unchanged: yes")


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
    print(f"all_questions.json: {json_path}")
    print(f"SQLite: {database_path}")
    print(f"JSON sha256 before: {json_hash_before}")
    print(f"SQLite sha256 before: {database_hash_before}")

    try:
        validate_json_before(rows)
        validate_sqlite_before(connection)
        print("planned addition:")
        print(json.dumps(printable_record(), ensure_ascii=False, indent=2))

        if not apply_mode:
            connection.close()
            connection = None
            json_hash_after = sha256(json_path)
            database_hash_after = sha256(database_path)
            print(f"JSON sha256 after:  {json_hash_after}")
            print(f"SQLite sha256 after: {database_hash_after}")
            if json_hash_after != json_hash_before:
                raise RuntimeError("Dry-run changed all_questions.json")
            if database_hash_after != database_hash_before:
                raise RuntimeError("Dry-run changed SQLite")
            print("dry-run successful: ID 4138 was not written")
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
        print("apply successful: ID 4138 added to JSON and SQLite")
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
