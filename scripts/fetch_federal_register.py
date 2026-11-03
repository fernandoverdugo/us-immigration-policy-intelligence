from __future__ import annotations

import json
from pathlib import Path

from src.ingestion.config import AGENCY_SLUGS, END_DATE, START_DATE
from src.ingestion.federal_register import fetch_all_documents
from src.ingestion.filtering import include_document, matched_terms

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")


def merge_document(
    deduped: dict[str, dict],
    document: dict,
    agency_key: str,
    reasons: list[str],
) -> None:
    document_number = document.get("document_number")
    if not document_number:
        return

    if document_number not in deduped:
        record = dict(document)
        record["source_agency_scopes"] = [agency_key]
        record["inclusion_reasons"] = sorted(set(reasons))
        record["matched_terms"] = matched_terms(document)
        deduped[document_number] = record
        return

    existing = deduped[document_number]
    existing["source_agency_scopes"] = sorted(
        set(existing["source_agency_scopes"]) | {agency_key}
    )
    existing["inclusion_reasons"] = sorted(
        set(existing["inclusion_reasons"]) | set(reasons)
    )
    existing["matched_terms"] = sorted(
        set(existing["matched_terms"]) | set(matched_terms(document))
    )


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    deduped: dict[str, dict] = {}

    for agency_key, agency_slug in AGENCY_SLUGS.items():
        documents = fetch_all_documents(
            agency_slug=agency_slug,
            start_date=START_DATE,
            end_date=END_DATE,
        )

        raw_path = RAW_DIR / f"federal_register_{agency_key}.json"
        raw_path.write_text(json.dumps(documents, indent=2), encoding="utf-8")

        included_count = 0
        for document in documents:
            keep, reasons = include_document(document, agency_key)
            if keep:
                included_count += 1
                merge_document(deduped, document, agency_key, reasons)

        print(
            f"{agency_key}: fetched {len(documents)} documents; "
            f"included {included_count} agency-document hits"
        )

    output_path = PROCESSED_DIR / "federal_register_corpus.json"
    output_path.write_text(
        json.dumps(list(deduped.values()), indent=2),
        encoding="utf-8",
    )

    print(f"included: {len(deduped)} unique documents")


if __name__ == "__main__":
    main()
