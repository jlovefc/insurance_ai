"""Apply READY-FIX-BATCH-20260716-001 to the formal SQLite question bank.

Evidence:
- docs/corrections/correction_ledger_20260716.md
- docs/corrections/id3815_jy_p89_term_insurance_answer_correction_20260716.md
- docs/corrections/id3785_jy_p90_reserve_option_pollution_correction_20260716.md

The default mode is read-only dry-run. Pass --apply explicitly to write.
Only questions.id 3815 and 3785 are permitted update targets.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any


BATCH_ID = "READY-FIX-BATCH-20260716-001"
EXPECTED_QUESTION_COUNT = 4_135
ALLOWED_IDS = frozenset({3815, 3785})
REFERENCE_ID = 2670
DEFAULT_DATABASE = (
    Path(__file__).resolve().parents[1]
    / "platform"
    / "instance"
    / "insurance_exam.db"
)

EXPECTED: dict[int, dict[str, Any]] = {
    3815: {
        "options": ["B", "C", "AC", "ABC"],
        "correct_answer": "1",
        "explanation": (
            "此題B錯誤。其他因素不變，保險費與利率高低成反比。"
            "正式考試也可能換問何者正確，則答案就會是3。"
        ),
    },
    3785: {
        "content": (
            "責任準備金計算與提存牽涉複雜的精算技術與法令規定，"
            "會因保險契約之 A.保險期間；B.繳費方式；C.契約生效日；"
            "D.繳費期間，而有差別。"
        ),
        "options": ["ABD", "BD", "ABC", "ABCD"],
        "correct_answer": "4",
        "explanation": "",
    },
}

SELECT_FIELDS = (
    "id, subject, unit, content, options, correct_answer, explanation"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"Apply {BATCH_ID} to the insurance exam SQLite database."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Read and validate only (default).",
    )
    mode.add_argument(
        "--apply",
        action="store_true",
        help="Apply the two approved updates in a transaction.",
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=DEFAULT_DATABASE,
        help=f"SQLite database path (default: {DEFAULT_DATABASE})",
    )
    return parser.parse_args()


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def read_question(connection: sqlite3.Connection, question_id: int) -> dict[str, Any]:
    row = connection.execute(
        f"SELECT {SELECT_FIELDS} FROM questions WHERE id = ?",
        (question_id,),
    ).fetchone()
    if row is None:
        raise RuntimeError(f"questions.id={question_id} was not found")
    return row_to_dict(row)


def printable_question(question: dict[str, Any]) -> dict[str, Any]:
    result = dict(question)
    try:
        result["options"] = json.loads(result["options"])
    except (TypeError, json.JSONDecodeError):
        pass
    return result


def print_question(label: str, question: dict[str, Any]) -> None:
    print(f"{label}: {json.dumps(printable_question(question), ensure_ascii=False)}")


def validate_allowed_ids() -> None:
    if set(EXPECTED) != ALLOWED_IDS:
        raise RuntimeError(
            f"Script target mismatch: expected only {sorted(ALLOWED_IDS)}, "
            f"got {sorted(EXPECTED)}"
        )


def validate_database(connection: sqlite3.Connection) -> None:
    count = connection.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    if count != EXPECTED_QUESTION_COUNT:
        raise RuntimeError(
            f"Unexpected questions count: {count}; expected {EXPECTED_QUESTION_COUNT}"
        )
    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    if integrity != "ok":
        raise RuntimeError(f"SQLite integrity_check failed: {integrity}")
    print(f"questions count: {count}")
    print(f"integrity_check: {integrity}")


def validate_expected(question_id: int, question: dict[str, Any]) -> None:
    expected = EXPECTED[question_id]
    actual_options = json.loads(question["options"])
    if actual_options != expected["options"]:
        raise RuntimeError(
            f"ID{question_id} options mismatch: {actual_options!r}"
        )
    for field in ("correct_answer", "explanation"):
        if question[field] != expected[field]:
            raise RuntimeError(
                f"ID{question_id} {field} mismatch: {question[field]!r}"
            )
    if "content" in expected and question["content"] != expected["content"]:
        raise RuntimeError(
            f"ID{question_id} content mismatch: {question['content']!r}"
        )


def apply_updates(connection: sqlite3.Connection) -> None:
    for question_id in sorted(ALLOWED_IDS):
        expected = EXPECTED[question_id]
        if question_id == 3815:
            cursor = connection.execute(
                """
                UPDATE questions
                SET options = ?, correct_answer = ?, explanation = ?
                WHERE id = ?
                """,
                (
                    json.dumps(expected["options"], ensure_ascii=False),
                    expected["correct_answer"],
                    expected["explanation"],
                    question_id,
                ),
            )
        elif question_id == 3785:
            cursor = connection.execute(
                """
                UPDATE questions
                SET content = ?, options = ?, correct_answer = ?, explanation = ?
                WHERE id = ?
                """,
                (
                    expected["content"],
                    json.dumps(expected["options"], ensure_ascii=False),
                    expected["correct_answer"],
                    expected["explanation"],
                    question_id,
                ),
            )
        else:  # Defensive guard even if constants are edited later.
            raise RuntimeError(f"Refusing unauthorized question id: {question_id}")
        if cursor.rowcount != 1:
            raise RuntimeError(
                f"ID{question_id} update affected {cursor.rowcount} rows; expected 1"
            )


def main() -> int:
    args = parse_args()
    validate_allowed_ids()
    database = args.database.expanduser().resolve()
    if not database.is_file():
        raise FileNotFoundError(f"Database not found: {database}")

    apply_mode = bool(args.apply)
    print(f"batch_id: {BATCH_ID}")
    print(f"mode: {'apply' if apply_mode else 'dry-run'}")
    print(f"database: {database}")

    if apply_mode:
        connection = sqlite3.connect(database)
    else:
        uri = database.as_uri() + "?mode=ro"
        connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row

    try:
        before = {
            question_id: read_question(connection, question_id)
            for question_id in sorted(ALLOWED_IDS)
        }
        reference_before = read_question(connection, REFERENCE_ID)
        for question_id, question in before.items():
            print_question(f"before ID{question_id}", question)
        print_question(f"reference ID{REFERENCE_ID}", reference_before)
        validate_database(connection)

        if not apply_mode:
            print("dry-run: no UPDATE statements executed; database remains read-only")
            for question_id, question in before.items():
                matches = True
                try:
                    validate_expected(question_id, question)
                except RuntimeError:
                    matches = False
                print(f"ID{question_id} already matches expected values: {matches}")
            return 0

        connection.execute("BEGIN IMMEDIATE")
        apply_updates(connection)
        after = {
            question_id: read_question(connection, question_id)
            for question_id in sorted(ALLOWED_IDS)
        }
        reference_after = read_question(connection, REFERENCE_ID)
        for question_id, question in after.items():
            validate_expected(question_id, question)
            print_question(f"after ID{question_id}", question)
        if reference_after != reference_before:
            raise RuntimeError(f"ID{REFERENCE_ID} changed unexpectedly")
        print_question(f"unchanged ID{REFERENCE_ID}", reference_after)
        validate_database(connection)
        connection.commit()
        print("apply completed and committed")
        return 0
    except Exception:
        if apply_mode:
            connection.rollback()
            print("apply failed; transaction rolled back")
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())

