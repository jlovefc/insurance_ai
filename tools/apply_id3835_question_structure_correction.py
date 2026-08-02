"""Controlled structure correction for JY P.93 Q8 / question ID3835.

Default execution is a read-only dry-run. Only an explicit --apply may write,
and apply mode requires byte-identical JSON and SQLite backups.

References:
- docs/corrections/id3835_jy_p93_q8_option_pollution_correction_20260716.md
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
    ROOT / "backups" / "all_questions_before_id3835_correction_20260716.json"
)
DEFAULT_DATABASE_BACKUP = (
    ROOT / "backups" / "insurance_exam_before_id3835_correction_20260716.db"
)

TARGET_ID = 3_835
EXPECTED_JSON_COUNT = 4_128
EXPECTED_SQLITE_COUNT = 4_141
EXPECTED_MAX_ID = 4_141
EXPECTED_SUBJECT = "B 保險實務-分類"
EXPECTED_UNIT = "04 人身保險意義、功能、分類"
CURRENT_CONTENT = "人身保險的意義，就是由？"
EXPECTED_CONTENT = (
    "人身保險的意義，就是由下列何者出極少的錢，交由人壽保險公司集成龐大"
    "的財力，作妥善的管理與運用，在這些人之中，一旦有人發生不幸或約定事故"
    "的時候，根據公平合理的制度，給與補償，保障他本人或親屬安樂的生活？"
)
COMMON_TAIL = (
    "出極少的錢，交由人壽保險公司集成龐大的財力，作妥善的管理與運用，在這些"
    "人之中，一旦有人發生不幸或約定事故的時候，根據公平合理的制度，給與補償，"
    "保障他本人或親屬安樂的生活"
)
CURRENT_OPTIONS = [
    "許多窮苦的人們",
    "少數的社會熱心人士",
    "千千萬萬的人",
    f"保險公司的員工 {COMMON_TAIL}",
]
EXPECTED_OPTIONS = [
    "許多窮苦的人們",
    "少數的社會熱心人士",
    "千千萬萬的人",
    "保險公司的員工",
]
EXPECTED_ANSWER = "3"
EXPECTED_EXPLANATION = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dry-run or apply the approved structure correction for ID3835."
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
        raise RuntimeError("SQLite ID3835 does not exist")
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
        raise RuntimeError(f"JSON ID3835 match count is {len(targets)}; expected 1")
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
            raise RuntimeError(f"{label} ID3835 subject changed")
        if row.get("unit") != EXPECTED_UNIT:
            raise RuntimeError(f"{label} ID3835 unit changed")
        if row.get("content") != CURRENT_CONTENT:
            raise RuntimeError(f"{label} ID3835 current content does not match guard")
        if decode_options(row.get("options"), label=label) != CURRENT_OPTIONS:
            raise RuntimeError(f"{label} ID3835 current options do not match guard")
        if str(row.get("correct_answer")) != EXPECTED_ANSWER:
            raise RuntimeError(f"{label} ID3835 answer is not {EXPECTED_ANSWER}")
    if sqlite_row.get("explanation") not in ("", None):
        raise RuntimeError("SQLite ID3835 explanation is no longer empty")
    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    if integrity != "ok":
        raise RuntimeError(f"SQLite integrity_check failed before correction: {integrity}")
    return json_row, sqlite_row


def validate_backup(live: Path, backup: Path, label: str) -> None:
    if not backup.is_file():
        raise RuntimeError(f"{label} backup is required but missing: {backup}")
    if sha256(live) != sha256(backup):
        raise RuntimeError(f"{label} backup is not byte-identical to live file")


def write_json_bank(path: Path, rows: list[dict[str, Any]]) -> None:
    temporary = path.with_name(path.name + ".3835.tmp")
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
        if row.get("content") != EXPECTED_CONTENT:
            raise RuntimeError(f"{label} ID3835 content validation failed")
        if decode_options(row.get("options"), label=label) != EXPECTED_OPTIONS:
            raise RuntimeError(f"{label} ID3835 options validation failed")
        if str(row.get("correct_answer")) != EXPECTED_ANSWER:
            raise RuntimeError(f"{label} ID3835 answer changed")
    if sqlite_row.get("explanation") not in ("", None):
        raise RuntimeError("SQLite ID3835 explanation changed")

    json_other_hash_after = stable_hash(
        [row for row in rows if int(row.get("id", -1)) != TARGET_ID]
    )
    if json_other_hash_after != json_other_hash_before:
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
    print(f"  current content: {sqlite_row['content']!r}")
    print(f"  expected content: {EXPECTED_CONTENT!r}")
    print(f"  current options: {decode_options(sqlite_row['options'], label='SQLite')!r}")
    print(f"  expected options: {EXPECTED_OPTIONS!r}")
    print(f"  correct_answer unchanged: {EXPECTED_ANSWER!r}")
    print(f"  SQLite explanation unchanged: {EXPECTED_EXPLANATION!r}")


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
            print("dry-run successful: ID3835 was not modified")
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
        json_row["content"] = EXPECTED_CONTENT
        json_row["options"] = list(EXPECTED_OPTIONS)
        cursor = connection.execute(
            """
            UPDATE questions
            SET content = ?, options = ?
            WHERE id = ? AND content = ? AND options = ? AND correct_answer = ?
            """,
            (
                EXPECTED_CONTENT,
                json.dumps(EXPECTED_OPTIONS, ensure_ascii=False),
                TARGET_ID,
                CURRENT_CONTENT,
                json.dumps(CURRENT_OPTIONS, ensure_ascii=False),
                EXPECTED_ANSWER,
            ),
        )
        if cursor.rowcount != 1:
            raise RuntimeError(f"SQLite ID3835 update affected {cursor.rowcount} rows")

        validate_after(
            rows,
            connection,
            json_other_hash_before=json_other_hash_before,
            sqlite_other_hash_before=sqlite_other_hash_before,
        )
        write_json_bank(json_path, rows)
        connection.commit()
        original_json_bytes = None
        print("apply successful: ID3835 corrected in JSON and SQLite")
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
