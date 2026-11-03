from src.ingestion.filtering import include_document, matched_terms, references_title_8


def test_title_8_reference_is_detected():
    document = {"cfr_references": [{"title": 8, "part": 208}]}
    assert references_title_8(document)


def test_immigration_term_is_detected():
    document = {"title": "Changes to asylum procedures"}
    assert "asylum" in matched_terms(document)


def test_cbp_trade_only_document_is_not_automatically_included():
    document = {
        "title": "Tariff Classification of Steel Products",
        "abstract": "Customs classification guidance.",
        "cfr_references": [{"title": 19, "part": 177}],
    }
    keep, reasons = include_document(document, "cbp")
    assert not keep
    assert reasons == []


def test_eoir_document_is_in_scope():
    document = {"title": "Administrative notice"}
    keep, reasons = include_document(document, "eoir")
    assert keep
    assert "eoir_scope" in reasons
