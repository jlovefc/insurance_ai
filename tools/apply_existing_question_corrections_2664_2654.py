"""Dry-run or apply approved corrections for existing questions 2664 and 2654.

Evidence:
- docs/corrections/id2664_jy_p90_q28_reserve_assumption_answer_correction_20260716.md
- docs/corrections/id2654_jy_p91_q49_dividend_interest_answer_correction_20260716.md
- docs/corrections/correction_ledger_20260716.md

The default mode is read-only dry-run. Only an explicit --apply may write.
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
    / "all_questions_before_existing_question_corrections_2664_2654_20260716.json"
)
DEFAULT_DATABASE_BACKUP = (
    ROOT
    / "backups"
    / "insurance_exam_before_existing_question_corrections_2664_2654_20260716.db"
)

TARGET_IDS = (2_654, 2_664)
EXPECTED: dict[int, dict[str, Any]] = {
    2_664: {
        "current_answer": "1",
        "expected_answer": "3",
        "options": ["BC", "BD", "AD", "AC"],
        "expected_explanation": (
            "保險公司採較穩健的責任準備金提存假設時，通常採較低之預定利率"
            "及較高之預定死亡率。較低預定利率會提高準備金，較高預定死亡率"
            "亦使死亡給付成本估計較高，因此答案為AD。"
        ),
    },
    2_654: {
        "current_answer": "1",
        "expected_answer": "3",
        "options": ["高", "不一定", "一樣", "低"],
        "expected_explanation": (
            "選擇儲存生息方式給付紅利時，紅利係另行累積生息，並不改變原保單"
            "約定的保險金額。因此死亡時所給付之保險金額較原保險金額為一樣；"
            "累積紅利若一併給付，屬於保險金額以外的紅利累積給付概念。"
        ),
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dry-run or apply approved corrections for IDs 2664 and 2654."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply both approved corrections after all backup and safety checks.",
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
            raise RuntimeError(f"{label} options are not valid JSON: {raw!r}") from error
    else:
        raise RuntimeError(f"{label} options have unsupported type: {type(raw).__name__}")
    if not isinstance(options, list):
        raise RuntimeError(f"{label} options are not a list: {options!r}")
    return options


def select_sqlite_targets(connection: sqlite3.Connection) -> dict[int, dict[str, Any]]:
    placeholders = ",".join("?" for _ in TARGET_IDS)
    rows = connection.execute(
        f"""
        SELECT id, subject, unit, content, options, correct_answer, explanation
        FROM questions
        WHERE id IN ({placeholders})
        ORDER BY id
        """,
        TARGET_IDS,
    ).fetchall()
    return {row["id"]: dict(row) for row in rows}


def sqlite_non_target_hash(connection: sqlite3.Connection) -> str:
    placeholders = ",".join("?" for _ in TARGET_IDS)
    rows = connection.execute(
        f"""
        SELECT id, subject, unit, content, options, correct_answer, explanation
        FROM questions
        WHERE id NOT IN ({placeholders})
        ORDER BY id
        """,
        TARGET_IDS,
    ).fetchall()
    return stable_hash([list(row) for row in rows])


def validate_targets(
    json_rows: list[dict[str, Any]], sqlite_rows: dict[int, dict[str, Any]]
) -> dict[int, dict[str, Any]]:
    json_by_id = {row.get("id"): row for row in json_rows if row.get("id") in TARGET_IDS}
    if set(json_by_id) != set(TARGET_IDS):
        raise RuntimeError(
            f"Target IDs in JSON are {sorted(json_by_id)}; expected {list(TARGET_IDS)}"
        )
    if set(sqlite_rows) != set(TARGET_IDS):
        raise RuntimeError(
            f"Target IDs in SQLite are {sorted(sqlite_rows)}; expected {list(TARGET_IDS)}"
        )

    for question_id in TARGET_IDS:
        expected = EXPECTED[question_id]
        json_row = json_by_id[question_id]
        sqlite_row = sqlite_rows[question_id]
        for label, row in (("JSON", json_row), ("SQLite", sqlite_row)):
            if str(row.get("correct_answer")) != expected["current_answer"]:
                raise RuntimeError(
                    f"ID{question_id} {label} correct_answer is "
                    f"{row.get('correct_answer')!r}; expected current value "
                    f"{expected['current_answer']!r}"
                )
            options = decode_options(row.get("options"), label=f"ID{question_id} {label}")
            if options != expected["options"]:
                raise RuntimeError(
                    f"ID{question_id} {label} options are {options!r}; "
                    f"expected {expected['options']!r}"
                )
        for field in ("subject", "unit", "content"):
            if json_row.get(field) != sqlite_row.get(field):
                raise RuntimeError(
                    f"ID{question_id} {field} differs between JSON and SQLite"
                )
    return json_by_id


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
    temporary = path.with_name(path.name + ".2664_2654.tmp")
    if temporary.exists():
        raise RuntimeError(f"Refusing to overwrite stale temporary file: {temporary}")
    try:
        text = json.dumps(rows, ensure_ascii=False, indent=2).replace("\n", "\r\n")
        temporary.write_text(text, encoding="utf-8", newline="")
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def print_plan(sqlite_rows: dict[int, dict[str, Any]]) -> None:
    for question_id in TARGET_IDS:
        current = sqlite_rows[question_id]
        expected = EXPECTED[question_id]
        print(f"question_id: {question_id}")
        print(f"  current correct_answer: {current['correct_answer']!r}")
        print(f"  expected correct_answer: {expected['expected_answer']!r}")
        print(f"  current SQLite explanation: {current['explanation']!r}")
        print(f"  expected explanation: {expected['expected_explanation']!r}")


def validate_after(
    json_rows: list[dict[str, Any]],
    connection: sqlite3.Connection,
    *,
    json_count_before: int,
    sqlite_count_before: int,
    json_other_hash_before: str,
    sqlite_other_hash_before: str,
) -> None:
    if len(json_rows) != json_count_before:
        raise RuntimeError("JSON question count changed")
    sqlite_count_after = connection.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    if sqlite_count_after != sqlite_count_before:
        raise RuntimeError("SQLite question count changed")

    json_by_id = {row.get("id"): row for row in json_rows}
    for question_id in TARGET_IDS:
        expected = EXPECTED[question_id]
        json_row = json_by_id[question_id]
        sqlite_row = select_sqlite_targets(connection)[question_id]
        if str(json_row.get("correct_answer")) != expected["expected_answer"]:
            raise RuntimeError(f"JSON ID{question_id} answer validation failed")
        if str(sqlite_row.get("correct_answer")) != expected["expected_answer"]:
            raise RuntimeError(f"SQLite ID{question_id} answer validation failed")
        if sqlite_row.get("explanation") != expected["expected_explanation"]:
            raise RuntimeError(f"SQLite ID{question_id} explanation validation failed")
        for label, row in (("JSON", json_row), ("SQLite", sqlite_row)):
            if decode_options(row.get("options"), label=f"ID{question_id} {label}") != expected["options"]:
                raise RuntimeError(f"{label} ID{question_id} options changed")

    json_other_hash_after = stable_hash(
        [row for row in json_rows if row.get("id") not in TARGET_IDS]
    )
    if json_other_hash_after != json_other_hash_before:
        raise RuntimeError("A non-target JSON question changed")
    if sqlite_non_target_hash(connection) != sqlite_other_hash_before:
        raise RuntimeError("A non-target SQLite question changed")
    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    if integrity != "ok":
        raise RuntimeError(f"SQLite integrity_check failed: {integrity}")
    print(f"JSON question count unchanged: {len(json_rows)}")
    print(f"SQLite question count unchanged: {sqlite_count_after}")
    print("non-target questions unchanged: yes")
    print(f"SQLite integrity_check: {integrity}")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    args = parse_args()
    if set(EXPECTED) != set(TARGET_IDS):
        raise RuntimeError("Script target guard failed")

    json_path = args.json.expanduser().resolve()
    database_path = args.database.expanduser().resolve()
    for path, label in ((json_path, "JSON"), (database_path, "SQLite")):
        if not path.is_file():
            raise FileNotFoundError(f"{label} file not found: {path}")

    apply_mode = bool(args.apply)
    json_hash_before = sha256(json_path)
    database_hash_before = sha256(database_path)
    json_rows = load_json_bank(json_path)
    connection = open_database(database_path, read_only=not apply_mode)

    print(f"mode: {'apply' if apply_mode else 'dry-run'}")
    print(f"all_questions.json: {json_path}")
    print(f"SQLite: {database_path}")
    print(f"JSON sha256 before: {json_hash_before}")
    print(f"SQLite sha256 before: {database_hash_before}")

    original_json_bytes: bytes | None = None
    try:
        sqlite_rows = select_sqlite_targets(connection)
        validate_targets(json_rows, sqlite_rows)
        print_plan(sqlite_rows)

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
            print("dry-run successful: no files were modified")
            return 0

        validate_backup(json_path, args.json_backup.expanduser().resolve(), "JSON")
        validate_backup(
            database_path,
            args.database_backup.expanduser().resolve(),
            "SQLite",
        )
        json_count_before = len(json_rows)
        sqlite_count_before = connection.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        json_other_hash_before = stable_hash(
            [row for row in json_rows if row.get("id") not in TARGET_IDS]
        )
        sqlite_other_hash_before = sqlite_non_target_hash(connection)
        original_json_bytes = json_path.read_bytes()

        connection.execute("BEGIN IMMEDIATE")
        json_by_id = {row.get("id"): row for row in json_rows}
        for question_id in TARGET_IDS:
            expected = EXPECTED[question_id]
            json_by_id[question_id]["correct_answer"] = expected["expected_answer"]
            cursor = connection.execute(
                """
                UPDATE questions
                SET correct_answer = ?, explanation = ?
                WHERE id = ? AND correct_answer = ?
                """,
                (
                    expected["expected_answer"],
                    expected["expected_explanation"],
                    question_id,
                    expected["current_answer"],
                ),
            )
            if cursor.rowcount != 1:
                raise RuntimeError(
                    f"SQLite ID{question_id} update affected {cursor.rowcount} rows"
                )

        validate_after(
            json_rows,
            connection,
            json_count_before=json_count_before,
            sqlite_count_before=sqlite_count_before,
            json_other_hash_before=json_other_hash_before,
            sqlite_other_hash_before=sqlite_other_hash_before,
        )
        write_json_bank(json_path, json_rows)
        connection.commit()
        original_json_bytes = None
        print("apply successful: JSON and SQLite corrections committed")
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
