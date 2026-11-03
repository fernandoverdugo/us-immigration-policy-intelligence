from __future__ import annotations

from typing import Any

from .config import AGENCY_NAME_PHRASES, HIGH_SIGNAL_TERMS, TITLE_TERMS


def title_text(document: dict[str, Any]) -> str:
    text = str(document.get("title") or "").lower()
    for phrase in AGENCY_NAME_PHRASES:
        text = text.replace(phrase, " ")
    return " ".join(text.split())


def supporting_text(document: dict[str, Any]) -> str:
    values = [
        document.get("abstract"),
        document.get("action"),
        document.get("excerpts"),
    ]
    text = " ".join(str(value) for value in values if value).lower()
    for phrase in AGENCY_NAME_PHRASES:
        text = text.replace(phrase, " ")
    return " ".join(text.split())


def references_title_8(document: dict[str, Any]) -> bool:
    for ref in document.get("cfr_references") or []:
        if str(ref.get("title")) == "8":
            return True
    return False


def matched_terms(document: dict[str, Any]) -> list[str]:
    title = title_text(document)
    context = supporting_text(document)

    matches = {term for term in TITLE_TERMS if term in title}
    matches.update(term for term in HIGH_SIGNAL_TERMS if term in context)
    return sorted(matches)


def include_document(document: dict[str, Any], source_agency: str) -> tuple[bool, list[str]]:
    reasons: list[str] = []

    if references_title_8(document):
        reasons.append("title_8_cfr")

    if matched_terms(document):
        reasons.append("immigration_lexicon")

    if source_agency == "eoir":
        reasons.append("eoir_scope")

    if source_agency == "uscis":
        reasons.append("uscis_scope")

    return bool(reasons), reasons
