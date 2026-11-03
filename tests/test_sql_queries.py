from pathlib import Path


QUERY_DIR = Path("database/queries")


def test_expected_sql_queries_exist():
    expected = {
        "01_activity_by_year.sql",
        "02_activity_by_agency.sql",
        "03_top_cfr_parts.sql",
        "04_rin_reuse.sql",
        "05_rulemaking_lifecycle.sql",
        "06_multi_agency_documents.sql",
        "07_year_over_year.sql",
    }

    found = {path.name for path in QUERY_DIR.glob("*.sql")}
    assert expected.issubset(found)


def test_queries_do_not_use_select_star():
    for query_path in QUERY_DIR.glob("*.sql"):
        sql = query_path.read_text(encoding="utf-8").lower()
        assert "select *" not in sql
