"""Controlled inclusion of approved JY unit03 Q35/Q36 versioned questions.

Default execution is dry-run and never writes data. Use --apply only after
approved backups exist and formal inclusion has been explicitly authorized.

References:
- docs/answer_audit/jy_unit03_q35_q36_official_law_support_20260716.md
- docs/answer_audit/jy_unit03_q35_q36_versioned_question_draft_20260716.md
- docs/answer_audit/jy_unit03_q35_q36_inclusion_plan_20260716.md
- docs/corrections/p91_q35_jy_missing_candidate_20260716.md
- docs/corrections/p91_q36_jy_missing_candidate_20260716.md
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = REPO_ROOT / "all_questions.json"
DEFAULT_DATABASE = REPO_ROOT / "platform" / "instance" / "insurance_exam.db"
DEFAULT_JSON_BACKUP = (
    REPO_ROOT
    / "backups"
    / "all_questions_before_missing_questions_4139_4140_20260716.json"
)
DEFAULT_DATABASE_BACKUP = (
    REPO_ROOT
    / "backups"
    / "insurance_exam_before_missing_questions_4139_4140_20260716.db"
)

EXPECTED_JSON_COUNT = 4125
EXPECTED_DATABASE_COUNT = 4138
EXPECTED_MAX_ID = 4138

SUBJECT = "B 保險實務-分類"
UNIT = "03 保險費架構、解約金、準備金、保單紅利"
OPTIONS = [
    "二十年滿期生死合險修正制",
    "二十五年滿期生死合險修正制",
    "二十年繳費終身保險修正制",
    "一年定期修正制",
]

NEW_QUESTIONS: tuple[dict[str, Any], ...] = (
    {
        "id": 4139,
        "case_id": "MISS-20260716-0010",
        "subject": SUBJECT,
        "unit": UNIT,
        "content": (
            "依當時《保險業各種準備金提存辦法》規定，民國88年1月1日起訂定之"
            "保險期間超過一年之人壽保險契約，若其純保險費較二十五年繳費"
            "二十五年滿期生死合險為大者，應採用下列何種修正制計算最低責任準備金？"
        ),
        "options": OPTIONS,
        "correct_answer": "2",
        "explanation": (
            "依當時《保險業各種準備金提存辦法》規定，民國88年1月1日起訂定、"
            "保險期間超過一年之人壽保險契約，若其純保險費較二十五年繳費"
            "二十五年滿期生死合險為大者，最低責任準備金採二十五年滿期生死合險"
            "修正制，因此答案為第2項。此為歷史契約適用規定，不代表未附時點限制"
            "的現行法規定。"
        ),
        "evidence_file": "docs/corrections/p91_q35_jy_missing_candidate_20260716.md",
    },
    {
        "id": 4140,
        "case_id": "MISS-20260716-0011",
        "subject": SUBJECT,
        "unit": UNIT,
        "content": (
            "依當時《保險業各種準備金提存辦法》規定，民國95年1月1日起訂定之"
            "保險期間超過一年之人壽保險契約，若其純保險費較二十年繳費終身保險"
            "為大者，應採用下列何種修正制計算最低責任準備金？"
        ),
        "options": OPTIONS,
        "correct_answer": "3",
        "explanation": (
            "依當時《保險業各種準備金提存辦法》規定，民國95年1月1日起訂定、"
            "保險期間超過一年之人壽保險契約，若其純保險費較二十年繳費終身保險"
            "為大者，最低責任準備金採二十年繳費終身保險修正制，因此答案為第3項。"
            "此為歷史契約適用規定，不代表未附時點限制的現行法規定。"
        ),
        "evidence_file": "docs/corrections/p91_q36_jy_missing_candidate_20260716.md",
    },
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_questions(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig") as stream:
        data = json.load(stream)
    if not isinstance(data, list):
        raise RuntimeError("all_questions.json root must be a list")
    return data


def json_payload(question: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": question["id"],
        "subject": question["subject"],
        "unit": question["unit"],
        "content": question["content"],
        "options": list(question["options"]),
        "correct_answer": question["correct_answer"],
        "explanation": question["explanation"],
    }


def database_row(connection: sqlite3.Connection, question_id: int) -> tuple[Any, ...] | None:
    return connection.execute(
        """
        SELECT id, subject, unit, content, options, correct_answer, explanation
        FROM questions
        WHERE id = ?
        """,
        (question_id,),
    ).fetchone()


def validate_preconditions(
    questions: list[dict[str, Any]], connection: sqlite3.Connection
) -> None:
    json_ids = {int(item["id"]) for item in questions}
    json_max = max(json_ids)
    database_count, database_max = connection.execute(
        "SELECT COUNT(*), MAX(id) FROM questions"
    ).fetchone()

    if len(questions) != EXPECTED_JSON_COUNT:
        raise RuntimeError(
            f"JSON count mismatch: expected {EXPECTED_JSON_COUNT}, got {len(questions)}"
        )
    if json_max != EXPECTED_MAX_ID:
        raise RuntimeError(
            f"JSON max id mismatch: expected {EXPECTED_MAX_ID}, got {json_max}"
        )
    if database_count != EXPECTED_DATABASE_COUNT:
        raise RuntimeError(
            "SQLite count mismatch: "
            f"expected {EXPECTED_DATABASE_COUNT}, got {database_count}"
        )
    if database_max != EXPECTED_MAX_ID:
        raise RuntimeError(
            f"SQLite max id mismatch: expected {EXPECTED_MAX_ID}, got {database_max}"
        )

    existing_json_pairs = {
        (str(item.get("content", "")).strip(), tuple(item.get("options") or []))
        for item in questions
    }
    for question in NEW_QUESTIONS:
        question_id = question["id"]
        if question_id in json_ids:
            raise RuntimeError(f"ID {question_id} already exists in JSON")
        if database_row(connection, question_id) is not None:
            raise RuntimeError(f"ID {question_id} already exists in SQLite")
        pair = (question["content"], tuple(question["options"]))
        if pair in existing_json_pairs:
            raise RuntimeError(
                f"Exact content/options already exist in JSON for target ID {question_id}"
            )
        duplicate = connection.execute(
            "SELECT id FROM questions WHERE TRIM(content) = ? AND options = ?",
            (
                question["content"].strip(),
                json.dumps(question["options"], ensure_ascii=False),
            ),
        ).fetchone()
        if duplicate is not None:
            raise RuntimeError(
                f"Exact content/options already exist in SQLite as ID {duplicate[0]}"
            )


def print_plan() -> None:
    print("Planned additions:")
    for question in NEW_QUESTIONS:
        print(json.dumps(question, ensure_ascii=False, indent=2))


def require_matching_backup(source: Path, backup: Path, label: str) -> None:
    if not backup.is_file():
        raise RuntimeError(f"{label} backup does not exist: {backup}")
    if sha256(source) != sha256(backup):
        raise RuntimeError(f"{label} backup is not byte-identical to current source")


def apply_changes(
    json_path: Path,
    database_path: Path,
    json_backup: Path,
    database_backup: Path,
) -> None:
    require_matching_backup(json_path, json_backup, "JSON")
    require_matching_backup(database_path, database_backup, "SQLite")

    questions = load_questions(json_path)
    original_json_by_id = {int(item["id"]): item for item in questions}

    with sqlite3.connect(database_path) as connection:
        connection.execute("BEGIN IMMEDIATE")
        try:
            validate_preconditions(questions, connection)
            original_database_rows = {
                row[0]: row
                for row in connection.execute(
                    """
                    SELECT id, subject, unit, content, options, correct_answer, explanation
                    FROM questions
                    """
                )
            }

            updated_questions = questions + [
                json_payload(question) for question in NEW_QUESTIONS
            ]
            with json_path.open("w", encoding="utf-8") as stream:
                json.dump(updated_questions, stream, ensure_ascii=False, indent=2)
                stream.write("\n")

            for question in NEW_QUESTIONS:
                connection.execute(
                    """
                    INSERT INTO questions
                        (id, subject, unit, content, options, correct_answer, explanation)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        question["id"],
                        question["subject"],
                        question["unit"],
                        question["content"],
                        json.dumps(question["options"], ensure_ascii=False),
                        question["correct_answer"],
                        question["explanation"],
                    ),
                )

            new_count, new_max = connection.execute(
                "SELECT COUNT(*), MAX(id) FROM questions"
            ).fetchone()
            if new_count != EXPECTED_DATABASE_COUNT + len(NEW_QUESTIONS):
                raise RuntimeError(f"Unexpected SQLite count after apply: {new_count}")
            if new_max != NEW_QUESTIONS[-1]["id"]:
                raise RuntimeError(f"Unexpected SQLite max id after apply: {new_max}")
            if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise RuntimeError("SQLite integrity_check failed")

            for question in NEW_QUESTIONS:
                expected = (
                    question["id"],
                    question["subject"],
                    question["unit"],
                    question["content"],
                    json.dumps(question["options"], ensure_ascii=False),
                    question["correct_answer"],
                    question["explanation"],
                )
                if database_row(connection, question["id"]) != expected:
                    raise RuntimeError(
                        f"SQLite verification failed for ID {question['id']}"
                    )

            target_ids = {question["id"] for question in NEW_QUESTIONS}
            for row in connection.execute(
                """
                SELECT id, subject, unit, content, options, correct_answer, explanation
                FROM questions
                WHERE id NOT IN (?, ?)
                """,
                tuple(sorted(target_ids)),
            ):
                if original_database_rows.get(row[0]) != row:
                    raise RuntimeError(f"Unexpected SQLite change to ID {row[0]}")

            connection.commit()
        except Exception:
            connection.rollback()
            raise

    verified_questions = load_questions(json_path)
    if len(verified_questions) != EXPECTED_JSON_COUNT + len(NEW_QUESTIONS):
        raise RuntimeError("Unexpected JSON count after apply")
    verified_by_id = {int(item["id"]): item for item in verified_questions}
    for existing_id, original in original_json_by_id.items():
        if verified_by_id.get(existing_id) != original:
            raise RuntimeError(f"Unexpected JSON change to ID {existing_id}")
    for question in NEW_QUESTIONS:
        if verified_by_id.get(question["id"]) != json_payload(question):
            raise RuntimeError(f"JSON verification failed for ID {question['id']}")

    print("Apply completed and verified.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Apply approved additions")
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--json-backup", type=Path, default=DEFAULT_JSON_BACKUP)
    parser.add_argument(
        "--database-backup", type=Path, default=DEFAULT_DATABASE_BACKUP
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    json_path = args.json.resolve()
    database_path = args.database.resolve()
    before_json_hash = sha256(json_path)
    before_database_hash = sha256(database_path)

    questions = load_questions(json_path)
    with sqlite3.connect(f"file:{database_path.as_posix()}?mode=ro", uri=True) as connection:
        validate_preconditions(questions, connection)

    print_plan()
    if args.apply:
        apply_changes(
            json_path,
            database_path,
            args.json_backup.resolve(),
            args.database_backup.resolve(),
        )
        return

    after_json_hash = sha256(json_path)
    after_database_hash = sha256(database_path)
    if before_json_hash != after_json_hash:
        raise RuntimeError("Dry-run changed all_questions.json")
    if before_database_hash != after_database_hash:
        raise RuntimeError("Dry-run changed SQLite database")
    print(f"all_questions.json SHA-256 unchanged: {after_json_hash}")
    print(f"SQLite SHA-256 unchanged: {after_database_hash}")
    print("Dry-run completed; no files were modified.")


if __name__ == "__main__":
    main()
