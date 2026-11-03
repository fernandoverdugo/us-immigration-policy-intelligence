from scripts.load_postgres import corpus_tier


def test_rules_are_core_rulemaking():
    assert corpus_tier("Rule") == "core_rulemaking"
    assert corpus_tier("Proposed Rule") == "core_rulemaking"


def test_notices_are_supplemental():
    assert corpus_tier("Notice") == "supplemental_notice"
