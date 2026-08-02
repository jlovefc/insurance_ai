"""Controlled inclusion of approved JY unit04 questions as IDs 4142-4146.

Default execution is a read-only dry-run. Only an explicit --apply may write,
and apply mode requires byte-identical JSON and SQLite backups.

References:
- docs/answer_audit/jy_unit04_q26_q28_q30_inclusion_plan_20260716.md
- docs/answer_audit/jy_unit04_q36_q38_inclusion_plan_20260716.md
- docs/answer_audit/jy_unit04_q26_q28_q30_q36_q38_inclusion_decision_20260716.md
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
    ROOT / "backups" / "all_questions_before_unit04_4142_4146_inclusion_20260716.json"
)
DEFAULT_DATABASE_BACKUP = (
    ROOT / "backups" / "insurance_exam_before_unit04_4142_4146_inclusion_20260716.db"
)

EXPECTED_JSON_COUNT = 4_128
EXPECTED_SQLITE_COUNT = 4_141
EXPECTED_MAX_ID = 4_141
SUBJECT = "B 保險實務-分類"
UNIT = "04 人身保險意義、功能、分類"

QUESTIONS: tuple[dict[str, Any], ...] = (
    {
        "id": 4142,
        "source": "JY P.94 Q26",
        "subject": SUBJECT,
        "unit": UNIT,
        "content": (
            "人身保險對個人的功能有哪些？ A.後顧無憂、晚景可恃；"
            "B.安定就業、穩定發展；C.保證信用、有利投資；D.享受優惠、稅捐減免"
        ),
        "options": ["AB", "BC", "CD", "ABCD"],
        "correct_answer": "4",
        "explanation": (
            "後顧無憂、晚景可恃，安定就業、穩定發展，保證信用、有利投資，"
            "以及享受優惠、稅捐減免，均屬教材列舉之人身保險對個人的功能，"
            "因此答案為ABCD。"
        ),
    },
    {
        "id": 4143,
        "source": "JY P.94 Q28",
        "subject": SUBJECT,
        "unit": UNIT,
        "content": (
            "人身保險對社會有那些功能？ A.透過再保、拓展外交；"
            "B.互助共濟、社會安寧；C.鼓勵儲蓄、平均財富；D.促進教育、提高素質"
        ),
        "options": ["AB", "AC", "BC", "BCD"],
        "correct_answer": "4",
        "explanation": (
            "互助共濟、社會安寧，鼓勵儲蓄、平均財富，以及促進教育、提高素質，"
            "均屬教材列舉之人身保險對社會的功能；透過再保、拓展外交屬對國家的"
            "功能，因此答案為BCD。"
        ),
    },
    {
        "id": 4144,
        "source": "JY P.94 Q30",
        "subject": SUBJECT,
        "unit": UNIT,
        "content": (
            "人身保險對國家的功能有哪些？ A.形成資本，以增國富；"
            "B.穩定經濟，安定政治；C.大眾理財，豐富多元；D.健全經營，整合金融"
        ),
        "options": ["ABD", "ABC", "ABCD", "ACD"],
        "correct_answer": "1",
        "explanation": (
            "形成資本、以增國富，穩定經濟、安定政治，以及健全經營、整合金融，"
            "均屬教材列舉之人身保險對國家的功能；大眾理財、豐富多元不屬本題"
            "列舉的國家功能，因此答案為ABD。"
        ),
    },
    {
        "id": 4145,
        "source": "JY P.95 Q36",
        "subject": SUBJECT,
        "unit": UNIT,
        "content": "依審查日有效之《保險法》第13條規定，人身保險包括下列哪四類？",
        "options": [
            "生存保險、死亡保險、生死合險、傷害保險",
            "人壽保險、傷害保險、健康保險、投資型保險",
            "人壽保險、健康保險、傷害保險、年金保險",
            "生存保險、死亡保險、生死合險、年金保險",
        ],
        "correct_answer": "3",
        "explanation": (
            "依審查日有效之《保險法》第13條規定，人身保險包括人壽保險、"
            "健康保險、傷害保險及年金保險，因此答案為第3項。投資型保險依"
            "商品性質分為投資型人壽保險或投資型年金保險，並非第13條之外的"
            "獨立第五類。"
        ),
    },
    {
        "id": 4146,
        "source": "JY P.95 Q38",
        "subject": SUBJECT,
        "unit": UNIT,
        "content": (
            "依人身保險市場的商品型態及主管機關商品分類，下列哪些屬於人身"
            "保險商品？ A.傷害保險；B.健康保險；C.投資型保險商品；D.責任保險"
        ),
        "options": ["AB", "ABC", "BC", "BCD"],
        "correct_answer": "2",
        "explanation": (
            "傷害保險與健康保險均屬《保險法》第13條所列人身保險類別；投資型"
            "保險亦屬人身保險商品，依商品性質分為投資型人壽保險或投資型年金"
            "保險。責任保險則屬財產保險，因此答案為ABC。投資型保險並不是"
            "第13條之外的獨立第五類。"
        ),
    },
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
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


def load_json(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig") as stream:
        rows = json.load(stream)
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise RuntimeError("all_questions.json must contain a list of objects")
    return rows


def payload(question: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": question["id"],
        "subject": question["subject"],
        "unit": question["unit"],
        "content": question["content"],
        "options": list(question["options"]),
        "correct_answer": question["correct_answer"],
        "explanation": question["explanation"],
    }


def open_database(path: Path, *, read_only: bool) -> sqlite3.Connection:
    if read_only:
        connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    else:
        connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def validate_before(
    rows: list[dict[str, Any]], connection: sqlite3.Connection
) -> None:
    ids = {int(row["id"]) for row in rows}
    if len(rows) != EXPECTED_JSON_COUNT or max(ids) != EXPECTED_MAX_ID:
        raise RuntimeError(
            f"Unexpected JSON count/max: {(len(rows), max(ids))}; "
            f"expected {(EXPECTED_JSON_COUNT, EXPECTED_MAX_ID)}"
        )
    sqlite_count, sqlite_max = connection.execute(
        "SELECT COUNT(*), MAX(id) FROM questions"
    ).fetchone()
    if (sqlite_count, sqlite_max) != (EXPECTED_SQLITE_COUNT, EXPECTED_MAX_ID):
        raise RuntimeError(
            f"Unexpected SQLite count/max: {(sqlite_count, sqlite_max)}; "
            f"expected {(EXPECTED_SQLITE_COUNT, EXPECTED_MAX_ID)}"
        )

    json_pairs = {
        (str(row.get("content", "")).strip(), tuple(row.get("options") or []))
        for row in rows
    }
    for question in QUESTIONS:
        target_id = question["id"]
        if target_id in ids:
            raise RuntimeError(f"ID {target_id} already exists in JSON")
        if connection.execute(
            "SELECT 1 FROM questions WHERE id = ?", (target_id,)
        ).fetchone():
            raise RuntimeError(f"ID {target_id} already exists in SQLite")
        pair = (question["content"].strip(), tuple(question["options"]))
        if pair in json_pairs:
            raise RuntimeError(
                f"Exact content/options for ID {target_id} already exist in JSON"
            )
        candidates = connection.execute(
            "SELECT id, options FROM questions WHERE TRIM(content) = ?",
            (question["content"].strip(),),
        ).fetchall()
        for candidate in candidates:
            try:
                options = json.loads(candidate["options"])
            except (TypeError, json.JSONDecodeError):
                options = candidate["options"]
            if options == question["options"]:
                raise RuntimeError(
                    f"Exact content/options for ID {target_id} already exist "
                    f"in SQLite as ID {candidate['id']}"
                )

    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    if integrity != "ok":
        raise RuntimeError(f"SQLite integrity_check failed: {integrity}")


def require_backup(live: Path, backup: Path, label: str) -> None:
    if not backup.is_file():
        raise RuntimeError(f"{label} backup is missing: {backup}")
    if sha256(live) != sha256(backup):
        raise RuntimeError(f"{label} backup is not byte-identical to live file")


def sqlite_rows_hash(
    connection: sqlite3.Connection, excluded_ids: set[int]
) -> str:
    placeholders = ",".join("?" for _ in excluded_ids)
    rows = connection.execute(
        f"""
        SELECT id, content, options, correct_answer, unit, explanation,
               difficulty, created_at, subject, is_important
        FROM questions WHERE id NOT IN ({placeholders}) ORDER BY id
        """,
        tuple(sorted(excluded_ids)),
    ).fetchall()
    return stable_hash([list(row) for row in rows])


def write_json(path: Path, rows: list[dict[str, Any]]) -> None:
    temporary = path.with_name(path.name + ".4142_4146.tmp")
    if temporary.exists():
        raise RuntimeError(f"Refusing to overwrite temporary file: {temporary}")
    try:
        with temporary.open("w", encoding="utf-8", newline="") as stream:
            json.dump(rows, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def apply_changes(
    json_path: Path,
    database_path: Path,
    json_backup: Path,
    database_backup: Path,
) -> None:
    require_backup(json_path, json_backup, "JSON")
    require_backup(database_path, database_backup, "SQLite")
    rows = load_json(json_path)
    target_ids = {question["id"] for question in QUESTIONS}
    json_other_hash = stable_hash(rows)
    original_json = json_path.read_bytes()

    connection = open_database(database_path, read_only=False)
    try:
        validate_before(rows, connection)
        sqlite_other_hash = sqlite_rows_hash(connection, target_ids)
        connection.execute("BEGIN IMMEDIATE")
        for question in QUESTIONS:
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

        new_rows = [*rows, *(payload(question) for question in QUESTIONS)]
        if len(new_rows) != EXPECTED_JSON_COUNT + len(QUESTIONS):
            raise RuntimeError("Unexpected JSON count after apply")
        write_json(json_path, new_rows)

        count, maximum = connection.execute(
            "SELECT COUNT(*), MAX(id) FROM questions"
        ).fetchone()
        if (count, maximum) != (
            EXPECTED_SQLITE_COUNT + len(QUESTIONS),
            QUESTIONS[-1]["id"],
        ):
            raise RuntimeError(f"Unexpected SQLite count/max: {(count, maximum)}")
        for question in QUESTIONS:
            row = connection.execute(
                """
                SELECT id, subject, unit, content, options, correct_answer, explanation
                FROM questions WHERE id = ?
                """,
                (question["id"],),
            ).fetchone()
            if row is None:
                raise RuntimeError(f"SQLite ID {question['id']} is missing")
            actual = dict(row)
            actual["options"] = json.loads(actual["options"])
            if actual != payload(question):
                raise RuntimeError(f"SQLite ID {question['id']} verification failed")
        if sqlite_rows_hash(connection, target_ids) != sqlite_other_hash:
            raise RuntimeError("A non-target SQLite question changed")
        if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("SQLite integrity_check failed after apply")
        if stable_hash(rows) != json_other_hash:
            raise RuntimeError("A pre-existing JSON question changed in memory")
        connection.commit()
    except Exception:
        connection.rollback()
        json_path.write_bytes(original_json)
        raise
    finally:
        connection.close()

    verified = load_json(json_path)
    verified_by_id = {int(row["id"]): row for row in verified}
    if len(verified) != EXPECTED_JSON_COUNT + len(QUESTIONS):
        raise RuntimeError("JSON count verification failed")
    for question in QUESTIONS:
        if verified_by_id.get(question["id"]) != payload(question):
            raise RuntimeError(f"JSON ID {question['id']} verification failed")
    print("apply successful: IDs 4142-4146 added to JSON and SQLite")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()
    json_path = args.json.expanduser().resolve()
    database_path = args.database.expanduser().resolve()
    json_hash_before = sha256(json_path)
    database_hash_before = sha256(database_path)
    rows = load_json(json_path)

    with open_database(database_path, read_only=not args.apply) as connection:
        validate_before(rows, connection)

    print(f"mode: {'apply' if args.apply else 'dry-run'}")
    print("planned additions:")
    for question in QUESTIONS:
        print(json.dumps(question, ensure_ascii=False, indent=2))

    if args.apply:
        apply_changes(
            json_path,
            database_path,
            args.json_backup.expanduser().resolve(),
            args.database_backup.expanduser().resolve(),
        )
        return 0

    json_hash_after = sha256(json_path)
    database_hash_after = sha256(database_path)
    if json_hash_after != json_hash_before:
        raise RuntimeError("Dry-run changed all_questions.json")
    if database_hash_after != database_hash_before:
        raise RuntimeError("Dry-run changed SQLite")
    print(f"JSON SHA-256 unchanged: {json_hash_after}")
    print(f"SQLite SHA-256 unchanged: {database_hash_after}")
    print("dry-run successful: IDs 4142-4146 were not written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
