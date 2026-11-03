from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

RAW_DIR = Path("data/raw")
CORPUS_PATH = Path("data/processed/federal_register_corpus.json")
OUTPUT_PATH = Path("corpus_quality_summary.json")


def main() -> None:
    processed = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))

    fetched = {}
    for path in RAW_DIR.glob("federal_register_*.json"):
        agency = path.stem.replace("federal_register_", "")
        fetched[agency] = len(json.loads(path.read_text(encoding="utf-8")))

    by_agency = Counter()
    by_year = Counter()
    by_type = Counter()
    by_reason = Counter()
    multi_agency_documents = 0

    for document in processed:
        scopes = document.get("source_agency_scopes") or []
        for agency in scopes:
            by_agency[agency] += 1

        if len(scopes) > 1:
            multi_agency_documents += 1

        publication_date = document.get("publication_date") or ""
        if len(publication_date) >= 4:
            by_year[publication_date[:4]] += 1

        by_type[document.get("type") or "unknown"] += 1

        for reason in document.get("inclusion_reasons", []):
            by_reason[reason] += 1

    report = {
        "fetched_by_agency": dict(sorted(fetched.items())),
        "included_unique": len(processed),
        "included_document_associations_by_agency": dict(sorted(by_agency.items())),
        "multi_agency_documents": multi_agency_documents,
        "included_by_year": dict(sorted(by_year.items())),
        "included_by_document_type": dict(sorted(by_type.items())),
        "included_by_reason": dict(sorted(by_reason.items())),
        "sample_documents": [
            {
                "document_number": document.get("document_number"),
                "source_agency_scopes": document.get("source_agency_scopes"),
                "publication_date": document.get("publication_date"),
                "type": document.get("type"),
                "title": document.get("title"),
                "inclusion_reasons": document.get("inclusion_reasons"),
                "matched_terms": document.get("matched_terms"),
            }
            for document in processed[:40]
        ],
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
