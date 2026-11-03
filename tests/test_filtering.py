from src.ingestion.filtering import include_document, matched_terms, references_title_8


def test_title_8_reference_is_detected():
    document = {"cfr_references": [{"title": 8, "part": 208}]}
    assert references_title_8(document)


def test_immigration_term_is_detected_in_title():
    document = {"title": "Changes to asylum procedures"}
    assert "asylum" in matched_terms(document)


def test_generic_agency_name_does_not_trigger_cbp_document():
    document = {
        "title": "Tariff Classification of Steel Products",
        "abstract": "U.S. Customs and Border Protection is issuing customs classification guidance.",
        "cfr_references": [{"title": 19, "part": 177}],
    }
    keep, reasons = include_document(document, "cbp")
    assert not keep
    assert reasons == []


def test_generic_ice_agency_name_does_not_trigger_document():
    document = {
        "title": "Agency Information Collection Activities",
        "abstract": "U.S. Immigration and Customs Enforcement requests comments.",
        "cfr_references": [],
    }
    keep, reasons = include_document(document, "ice")
    assert not keep
    assert reasons == []


def test_high_signal_abstract_term_can_include_ice_document():
    document = {
        "title": "Agency Information Collection Activities",
        "abstract": "The collection concerns removal proceedings and related records.",
    }
    keep, reasons = include_document(document, "ice")
    assert keep
    assert "immigration_lexicon" in reasons


def test_eoir_document_is_in_scope():
    document = {"title": "Administrative notice"}
    keep, reasons = include_document(document, "eoir")
    assert keep
    assert "eoir_scope" in reasons
