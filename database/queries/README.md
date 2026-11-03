# SQL analytical layer

Milestone 3 uses PostgreSQL as the primary analytical engine.

## Query set

1. `01_activity_by_year.sql` — annual document volume by Federal Register document type
2. `02_activity_by_agency.sql` — document volume by issuing agency and type
3. `03_top_cfr_parts.sql` — most frequently referenced CFR titles and parts
4. `04_rin_reuse.sql` — Regulation Identifier Numbers appearing across multiple documents
5. `05_rulemaking_lifecycle.sql` — proposal-to-final timing for RINs with both stages
6. `06_multi_agency_documents.sql` — jointly issued documents
7. `07_year_over_year.sql` — annual core/supplemental activity and year-over-year change

## Run

After loading PostgreSQL:

```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/immigration_policy"
python -m scripts.run_sql_analysis
```

Outputs are written to `data/processed/sql/` as CSV files and summarized in
`data/processed/sql_summary.json`.

The SQL layer is intentionally kept separate from visualization and NLP so that
the relational analytical logic is directly reviewable.
