from scripts.run_nlp_analysis import build_text

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


def test_build_text_handles_missing_abstract():
    frame = pd.DataFrame(
        {
            "title": ["Immigration Rule"],
            "abstract": [None],
        }
    )

    text = build_text(frame)
    assert text.iloc[0] == "Immigration Rule."
