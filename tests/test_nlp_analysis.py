from scripts.run_nlp_analysis import build_text, nlp_scope

import pandas as pd


def test_build_text_combines_title_and_abstract():
    frame = pd.DataFrame(
        {
            "title": ["Asylum Procedures"],
            "abstract": ["Changes to eligibility standards."],
        }
    )

    text = build_text(frame)
    assert text.iloc[0] == "Asylum Procedures. Changes to eligibility standards."


def test_build_text_collapses_whitespace():
    frame = pd.DataFrame(
        {
            "title": ["Asylum   Procedures"],
            "abstract": ["Changes\n to   eligibility standards."],
        }
    )

    text = build_text(frame)
    assert text.iloc[0] == "Asylum Procedures. Changes to eligibility standards."


def test_build_text_handles_missing_abstract():
    frame = pd.DataFrame(
        {
            "title": ["Immigration Rule"],
            "abstract": [None],
        }
    )

    text = build_text(frame)
    assert text.iloc[0] == "Immigration Rule."


def test_information_collection_notice_is_administrative():
    frame = pd.DataFrame(
        {
            "document_type": ["Notice"],
            "title": ["Visa Waiver Program Carrier Agreement"],
            "abstract": [
                "This notice concerns an information collection under the "
                "Paperwork Reduction Act."
            ],
        }
    )

    scope = nlp_scope(frame)
    assert scope.iloc[0] == "administrative_information_collection"


def test_rule_is_substantive_policy():
    frame = pd.DataFrame(
        {
            "document_type": ["Rule"],
            "title": ["Procedures for Asylum and Bars to Asylum Eligibility"],
            "abstract": ["This final rule revises asylum procedures."],
        }
    )

    scope = nlp_scope(frame)
    assert scope.iloc[0] == "substantive_policy"
