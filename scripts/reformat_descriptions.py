from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from app.collectors.values import html_to_text
from app.services.description import description_fields


def main() -> None:
    database = Path(__file__).resolve().parents[1] / "jobs.db"
    connection = sqlite3.connect(database)
    rows = connection.execute(
        "SELECT job_id, source, raw_payload FROM job_sources WHERE raw_payload IS NOT NULL"
    ).fetchall()
    descriptions: dict[int, str] = {}
    for job_id, source, raw in rows:
        payload = json.loads(raw)
        for field in description_fields(source):
            value = payload.get(field)
            if not isinstance(value, str) or not value.strip():
                continue
            formatted = html_to_text(value)
            if len(formatted) > len(descriptions.get(job_id, "")):
                descriptions[job_id] = formatted
            break
    connection.executemany(
        "UPDATE jobs SET description = ? WHERE id = ?",
        [(description, job_id) for job_id, description in descriptions.items()],
    )
    connection.commit()
    connection.close()
    print(f"Descrições reformatadas: {len(descriptions)}")


if __name__ == "__main__":
    main()
