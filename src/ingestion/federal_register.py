from __future__ import annotations

import time
from typing import Any

import requests

BASE_URL = "https://www.federalregister.gov/api/v1/documents.json"

DEFAULT_FIELDS = [
    "abstract",
    "action",
    "agencies",
    "cfr_references",
    "citation",
    "comment_url",
    "comments_close_on",
    "correction_of",
    "document_number",
    "effective_on",
    "end_page",
    "excerpts",
    "html_url",
    "json_url",
    "mods_url",
    "pdf_url",
    "publication_date",
    "raw_text_url",
    "regulation_id_numbers",
    "significant",
    "start_page",
    "subtype",
    "title",
    "type",
]


def build_params(
    agency_slug: str,
    start_date: str,
    end_date: str,
    page: int = 1,
    per_page: int = 1000,
) -> list[tuple[str, str | int]]:
    params: list[tuple[str, str | int]] = [
        ("conditions[agencies][]", agency_slug),
        ("conditions[publication_date][gte]", start_date),
        ("conditions[publication_date][lte]", end_date),
        ("order", "oldest"),
        ("page", page),
        ("per_page", per_page),
    ]
    params.extend(("fields[]", field) for field in DEFAULT_FIELDS)
    return params


def fetch_page(
    agency_slug: str,
    start_date: str,
    end_date: str,
    page: int = 1,
    per_page: int = 1000,
    timeout: int = 60,
) -> dict[str, Any]:
    response = requests.get(
        BASE_URL,
        params=build_params(
            agency_slug=agency_slug,
            start_date=start_date,
            end_date=end_date,
            page=page,
            per_page=per_page,
        ),
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def fetch_all_documents(
    agency_slug: str,
    start_date: str,
    end_date: str,
    pause_seconds: float = 0.15,
) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    page = 1

    while True:
        payload = fetch_page(
            agency_slug=agency_slug,
            start_date=start_date,
            end_date=end_date,
            page=page,
        )
        results = payload.get("results", [])
        documents.extend(results)

        total_pages = payload.get("total_pages")
        if total_pages is not None and page >= total_pages:
            break
        if not results:
            break

        page += 1
        time.sleep(pause_seconds)

    return documents
