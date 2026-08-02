"""Controlled correction for JY P.93 Q13 / existing question ID3840.

Default execution is a read-only dry-run. Only an explicit --apply may write,
and apply mode requires byte-identical JSON and SQLite backups.

References:
- docs/corrections/id3840_jy_p93_q13_electronic_policy_answer_option_correction_20260716.md
- docs/answer_audit/id3840_electronic_policy_version_review_20260716.md
- docs/corrections/correction_ledger_20260716.md
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
    ROOT / "backups" / "all_questions_before_id3840_correction_20260716.json"
)
DEFAULT_DATABASE_BACKUP = (
    ROOT / "backups" / "insurance_exam_before_id3840_correction_20260716.db"
)

TARGET_ID = 3_840
EXPECTED_JSON_COUNT = 4_128
EXPECTED_SQLITE_COUNT = 4_141
EXPECTED_MAX_ID = 4_141
EXPECTED_SUBJECT = "B 保險實務-分類"
EXPECTED_UNIT = "04 人身保險意義、功能、分類"
EXPECTED_CONTENT = "目前人身保險業所簽發的保單為"
CURRENT_OPTIONS = [
    "僅提供紙本保單",
    "可利用網路投保來簽發電子保單",
    "不限紙本保單",
    "僅選項",
]
EXPECTED_OPTIONS = [
    "僅提供紙本保單",
    "可利用網路投保來簽發電子保單",
    "不限紙本保單",
    "僅選項2、3為真",
]
CURRENT_ANSWER = "2"
EXPECTED_ANSWER = "4"
EXPECTED_EXPLANATION = (
    "依保險業辦理電子商務相關規範，保險業可辦理符合規定之網路投保，"
    "並得依要保人指定方式交付紙本或電子保單。因此保單不限於紙本，且"
    "符合規範時可透過網路投保簽發電子保單，第2、3項為真，答案為第4項。"
    "電子保單仍須符合適用商品、身分驗證、要保人同意及其他相關規範。"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dry-run or apply the approved correction for ID3840."
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
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_json_bank(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig") as stream:
        data = json.load(stream)
    if not isinstance(data, list) or not all(isinstance(row, dict) for row in data):
        raise RuntimeError("all_questions.json must contain a list of objects")
    return data


def open_database(path: Path, *, read_only: bool) -> sqlite3.Connection:
    if read_only:
        connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    else:
        connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def decode_options(raw: Any, *, label: str) -> list[str]:
    if isinstance(raw, list):
        options = raw
    elif isinstance(raw, str):
        try:
            options = json.loads(raw)
        except json.JSONDecodeError as error:
            raise RuntimeError(f"{label} options are invalid JSON") from error
    else:
        raise RuntimeError(f"{label} options have unsupported type")
    if not isinstance(options, list) or not all(isinstance(item, str) for item in options):
        raise RuntimeError(f"{label} options must be a list of strings")
    return options


def select_target(connection: sqlite3.Connection) -> dict[str, Any]:
    row = connection.execute(
        """
        SELECT id, subject, unit, content, options, correct_answer, explanation
        FROM questions WHERE id = ?
        """,
        (TARGET_ID,),
    ).fetchone()
    if row is None:
        raise RuntimeError("SQLite ID3840 does not exist")
    return dict(row)


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


def validate_before(
    rows: list[dict[str, Any]], connection: sqlite3.Connection
) -> tuple[dict[str, Any], dict[str, Any]]:
    if len(rows) != EXPECTED_JSON_COUNT:
        raise RuntimeError(f"JSON count is {len(rows)}; expected {EXPECTED_JSON_COUNT}")
    if max(int(row["id"]) for row in rows) != EXPECTED_MAX_ID:
        raise RuntimeError("Unexpected JSON max(id)")
    targets = [row for row in rows if int(row.get("id", -1)) == TARGET_ID]
    if len(targets) != 1:
        raise RuntimeError(f"JSON ID3840 match count is {len(targets)}; expected 1")
    json_row = targets[0]

    sqlite_count, sqlite_max = connection.execute(
        "SELECT COUNT(*), MAX(id) FROM questions"
    ).fetchone()
    if sqlite_count != EXPECTED_SQLITE_COUNT or sqlite_max != EXPECTED_MAX_ID:
        raise RuntimeError(
            f"Unexpected SQLite count/max: {(sqlite_count, sqlite_max)}"
        )
    sqlite_row = select_target(connection)

    for label, row in (("JSON", json_row), ("SQLite", sqlite_row)):
        if row.get("subject") != EXPECTED_SUBJECT:
            raise RuntimeError(f"{label} ID3840 subject changed")
        if row.get("unit") != EXPECTED_UNIT:
            raise RuntimeError(f"{label} ID3840 unit changed")
        if row.get("content") != EXPECTED_CONTENT:
            raise RuntimeError(f"{label} ID3840 content changed")
        if decode_options(row.get("options"), label=label) != CURRENT_OPTIONS:
            raise RuntimeError(f"{label} ID3840 current options do not match guard")
        if str(row.get("correct_answer")) != CURRENT_ANSWER:
            raise RuntimeError(f"{label} ID3840 current answer is not {CURRENT_ANSWER}")
    if sqlite_row.get("explanation") not in ("", None):
        raise RuntimeError("SQLite ID3840 explanation is no longer empty")
    if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
        raise RuntimeError("SQLite integrity_check failed before correction")
    return json_row, sqlite_row


def validate_backup(live: Path, backup: Path, label: str) -> None:
    if not backup.is_file():
        raise RuntimeError(f"{label} backup is required but missing: {backup}")
    if sha256(live) != sha256(backup):
        raise RuntimeError(f"{label} backup is not byte-identical to live file")


def write_json_bank(path: Path, rows: list[dict[str, Any]]) -> None:
    temporary = path.with_name(path.name + ".3840.tmp")
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
    if len(rows) != EXPECTED_JSON_COUNT:
        raise RuntimeError("JSON question count changed")
    sqlite_count = connection.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    if sqlite_count != EXPECTED_SQLITE_COUNT:
        raise RuntimeError("SQLite question count changed")

    json_row = next(row for row in rows if int(row.get("id", -1)) == TARGET_ID)
    sqlite_row = select_target(connection)
    for label, row in (("JSON", json_row), ("SQLite", sqlite_row)):
        if decode_options(row.get("options"), label=label) != EXPECTED_OPTIONS:
            raise RuntimeError(f"{label} ID3840 options validation failed")
        if str(row.get("correct_answer")) != EXPECTED_ANSWER:
            raise RuntimeError(f"{label} ID3840 answer validation failed")
        if row.get("content") != EXPECTED_CONTENT:
            raise RuntimeError(f"{label} ID3840 content changed")
    if sqlite_row.get("explanation") != EXPECTED_EXPLANATION:
        raise RuntimeError("SQLite ID3840 explanation validation failed")

    if stable_hash([row for row in rows if int(row.get("id", -1)) != TARGET_ID]) != json_other_hash_before:
        raise RuntimeError("A non-target JSON question changed")
    if sqlite_non_target_hash(connection) != sqlite_other_hash_before:
        raise RuntimeError("A non-target SQLite question changed")
    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    if integrity != "ok":
        raise RuntimeError(f"SQLite integrity_check failed after correction: {integrity}")
    print(f"JSON question count unchanged: {len(rows)}")
    print(f"SQLite question count unchanged: {sqlite_count}")
    print("non-target questions unchanged: yes")
    print(f"SQLite integrity_check: {integrity}")


def print_plan(sqlite_row: dict[str, Any]) -> None:
    print("planned correction:")
    print(f"  question_id: {TARGET_ID}")
    print(f"  content unchanged: {EXPECTED_CONTENT!r}")
    print(f"  current options: {decode_options(sqlite_row['options'], label='SQLite')!r}")
    print(f"  expected options: {EXPECTED_OPTIONS!r}")
    print(f"  current correct_answer: {sqlite_row['correct_answer']!r}")
    print(f"  expected correct_answer: {EXPECTED_ANSWER!r}")
    print(f"  current SQLite explanation: {sqlite_row['explanation']!r}")
    print(f"  expected explanation: {EXPECTED_EXPLANATION!r}")


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
        json_row, sqlite_row = validate_before(rows, connection)
        print_plan(sqlite_row)

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
            print("dry-run successful: ID3840 was not modified")
            return 0

        validate_backup(json_path, args.json_backup.expanduser().resolve(), "JSON")
        validate_backup(
            database_path,
            args.database_backup.expanduser().resolve(),
            "SQLite",
        )
        json_other_hash_before = stable_hash(
            [row for row in rows if int(row.get("id", -1)) != TARGET_ID]
        )
        sqlite_other_hash_before = sqlite_non_target_hash(connection)
        original_json_bytes = json_path.read_bytes()

        connection.execute("BEGIN IMMEDIATE")
        json_row["options"] = list(EXPECTED_OPTIONS)
        json_row["correct_answer"] = EXPECTED_ANSWER
        cursor = connection.execute(
            """
            UPDATE questions
            SET options = ?, correct_answer = ?, explanation = ?
            WHERE id = ? AND correct_answer = ? AND options = ?
            """,
            (
                json.dumps(EXPECTED_OPTIONS, ensure_ascii=False),
                EXPECTED_ANSWER,
                EXPECTED_EXPLANATION,
                TARGET_ID,
                CURRENT_ANSWER,
                json.dumps(CURRENT_OPTIONS, ensure_ascii=False),
            ),
        )
        if cursor.rowcount != 1:
            raise RuntimeError(f"SQLite ID3840 update affected {cursor.rowcount} rows")

        validate_after(
            rows,
            connection,
            json_other_hash_before=json_other_hash_before,
            sqlite_other_hash_before=sqlite_other_hash_before,
        )
        write_json_bank(json_path, rows)
        connection.commit()
        original_json_bytes = None
        print("apply successful: ID3840 corrected in JSON and SQLite")
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
