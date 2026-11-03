from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import psycopg

SCHEMA_PATH = Path("database/schema.sql")
DEFAULT_CORPUS_PATH = Path("data/processed/federal_register_corpus.json")


def corpus_tier(document_type: str | None) -> str:
    if document_type in {"Rule", "Proposed Rule"}:
        return "core_rulemaking"
    return "supplemental_notice"


def load_schema(connection: psycopg.Connection) -> None:
    connection.execute(SCHEMA_PATH.read_text(encoding="utf-8"))


def upsert_agency(connection: psycopg.Connection, agency: dict[str, Any]) -> None:
    connection.execute(
        """
        INSERT INTO agencies (agency_id, name, raw_name, slug, parent_agency_id)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (agency_id) DO UPDATE SET
            name = EXCLUDED.name,
            raw_name = EXCLUDED.raw_name,
            slug = EXCLUDED.slug,
            parent_agency_id = EXCLUDED.parent_agency_id
        """,
        (
            agency["id"],
            agency["name"],
            agency.get("raw_name"),
            agency["slug"],
            agency.get("parent_id"),
        ),
    )


def insert_document(connection: psycopg.Connection, document: dict[str, Any]) -> None:
    connection.execute(
        """
        INSERT INTO documents (
            document_number,
            title,
            abstract,
            action,
            document_type,
            subtype,
            publication_date,
            effective_on,
            comments_close_on,
            citation,
            start_page,
            end_page,
            significant,
            html_url,
            pdf_url,
            raw_text_url,
            corpus_tier
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (document_number) DO UPDATE SET
            title = EXCLUDED.title,
            abstract = EXCLUDED.abstract,
            action = EXCLUDED.action,
            document_type = EXCLUDED.document_type,
            subtype = EXCLUDED.subtype,
            publication_date = EXCLUDED.publication_date,
            effective_on = EXCLUDED.effective_on,
            comments_close_on = EXCLUDED.comments_close_on,
            citation = EXCLUDED.citation,
            start_page = EXCLUDED.start_page,
            end_page = EXCLUDED.end_page,
            significant = EXCLUDED.significant,
            html_url = EXCLUDED.html_url,
            pdf_url = EXCLUDED.pdf_url,
            raw_text_url = EXCLUDED.raw_text_url,
            corpus_tier = EXCLUDED.corpus_tier
        """,
        (
            document["document_number"],
            document["title"],
            document.get("abstract"),
            document.get("action"),
            document.get("type") or "unknown",
            document.get("subtype"),
            document.get("publication_date"),
            document.get("effective_on"),
            document.get("comments_close_on"),
            document.get("citation"),
            document.get("start_page"),
            document.get("end_page"),
            document.get("significant"),
            document.get("html_url"),
            document.get("pdf_url"),
            document.get("raw_text_url"),
            corpus_tier(document.get("type")),
        ),
    )


def link_agencies(connection: psycopg.Connection, document: dict[str, Any]) -> None:
    agencies = document.get("agencies") or []

    for agency in agencies:
        upsert_agency(connection, agency)

    for agency in agencies:
        connection.execute(
            """
            INSERT INTO document_agencies (document_number, agency_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
            """,
            (document["document_number"], agency["id"]),
        )


def link_cfr_references(connection: psycopg.Connection, document: dict[str, Any]) -> None:
    for reference in document.get("cfr_references") or []:
        title = reference.get("title")
        part = reference.get("part")
        if title is None or part is None:
            continue

        row = connection.execute(
            """
            INSERT INTO cfr_references (title_number, part)
            VALUES (%s, %s)
            ON CONFLICT (title_number, part)
            DO UPDATE SET part = EXCLUDED.part
            RETURNING cfr_reference_id
            """,
            (int(title), str(part)),
        ).fetchone()

        connection.execute(
            """
            INSERT INTO document_cfr_references (
                document_number,
                cfr_reference_id
            )
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
            """,
            (document["document_number"], row[0]),
        )


def link_rins(connection: psycopg.Connection, document: dict[str, Any]) -> None:
    for rin in document.get("regulation_id_numbers") or []:
        connection.execute(
            """
            INSERT INTO regulation_identifiers (rin)
            VALUES (%s)
            ON CONFLICT DO NOTHING
            """,
            (rin,),
        )
        connection.execute(
            """
            INSERT INTO document_regulation_identifiers (document_number, rin)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
            """,
            (document["document_number"], rin),
        )


def link_corpus_evidence(connection: psycopg.Connection, document: dict[str, Any]) -> None:
    evidence_groups = {
        "source_scope": document.get("source_agency_scopes") or [],
        "inclusion_reason": document.get("inclusion_reasons") or [],
        "matched_term": document.get("matched_terms") or [],
    }

    for evidence_type, values in evidence_groups.items():
        for value in values:
            connection.execute(
                """
                INSERT INTO corpus_evidence (
                    document_number,
                    evidence_type,
                    evidence_value
                )
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING
                """,
                (document["document_number"], evidence_type, value),
            )


def load_document(connection: psycopg.Connection, document: dict[str, Any]) -> None:
    insert_document(connection, document)
    link_agencies(connection, document)
    link_cfr_references(connection, document)
    link_rins(connection, document)
    link_corpus_evidence(connection, document)


def main() -> None:
    database_url = os.environ["DATABASE_URL"]
    corpus_path = Path(os.environ.get("CORPUS_PATH", DEFAULT_CORPUS_PATH))
    documents = json.loads(corpus_path.read_text(encoding="utf-8"))

    with psycopg.connect(database_url) as connection:
        load_schema(connection)
        for document in documents:
            load_document(connection, document)
        connection.commit()

        counts = connection.execute(
            """
            SELECT
                COUNT(*) AS documents,
                COUNT(*) FILTER (WHERE corpus_tier = 'core_rulemaking') AS core_rulemaking,
                COUNT(*) FILTER (WHERE corpus_tier = 'supplemental_notice') AS supplemental_notice
            FROM documents
            """
        ).fetchone()

    print(
        f"loaded {counts[0]} documents "
        f"({counts[1]} core rulemaking; {counts[2]} supplemental notices)"
    )


if __name__ == "__main__":
    main()
