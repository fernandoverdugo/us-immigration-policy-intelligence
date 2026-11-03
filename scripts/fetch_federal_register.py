from __future__ import annotations

import json
from pathlib import Path

from src.ingestion.config import AGENCY_SLUGS, END_DATE, START_DATE
from src.ingestion.federal_register import fetch_all_documents
from src.ingestion.filtering import include_document, matched_terms

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    included = []

    for agency_key, agency_slug in AGENCY_SLUGS.items():
        documents = fetch_all_documents(
            agency_slug=agency_slug,
            start_date=START_DATE,
            end_date=END_DATE,
        )

        raw_path = RAW_DIR / f"federal_register_{agency_key}.json"
        raw_path.write_text(json.dumps(documents, indent=2), encoding="utf-8")

        for document in documents:
            keep, reasons = include_document(document, agency_key)
            if keep:
                record = dict(document)
                record["source_agency_scope"] = agency_key
                record["inclusion_reasons"] = reasons
                record["matched_terms"] = matched_terms(document)
                included.append(record)

        print(f"{agency_key}: fetched {len(documents)} documents")

    deduped = {
        document["document_number"]: document
        for document in included
        if document.get("document_number")
    }

    output_path = PROCESSED_DIR / "federal_register_corpus.json"
    output_path.write_text(
        json.dumps(list(deduped.values()), indent=2),
        encoding="utf-8",
    )

    print(f"included: {len(deduped)} unique documents")


if __name__ == "__main__":
    main()
