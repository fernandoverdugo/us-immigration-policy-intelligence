from __future__ import annotations

import csv
import json
import os
from pathlib import Path

import psycopg

QUERY_DIR = Path("database/queries")
OUTPUT_DIR = Path("data/processed/sql")


def run_query(connection: psycopg.Connection, query_path: Path) -> tuple[list[str], list[tuple]]:
    with connection.cursor() as cursor:
        cursor.execute(query_path.read_text(encoding="utf-8"))
        rows = cursor.fetchall()
        columns = [column.name for column in cursor.description]
    return columns, rows


def write_csv(path: Path, columns: list[str], rows: list[tuple]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        writer.writerows(rows)


def main() -> None:
    database_url = os.environ["DATABASE_URL"]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    summary = {}

    with psycopg.connect(database_url) as connection:
        for query_path in sorted(QUERY_DIR.glob("*.sql")):
            columns, rows = run_query(connection, query_path)
            output_path = OUTPUT_DIR / f"{query_path.stem}.csv"
            write_csv(output_path, columns, rows)

            summary[query_path.stem] = {
                "row_count": len(rows),
                "columns": columns,
                "output": str(output_path),
            }

    Path("data/processed/sql_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    for name, details in summary.items():
        print(f"{name}: {details['row_count']} rows -> {details['output']}")


if __name__ == "__main__":
    main()
