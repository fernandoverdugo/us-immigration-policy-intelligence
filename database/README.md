# PostgreSQL analytical store

Milestone 2 moves the Federal Register corpus from file-based processing into a normalized PostgreSQL database.

## Design goals

- preserve one document with many issuing agencies
- preserve CFR references and Regulation Identifier Numbers (RINs)
- keep corpus-selection evidence auditable
- separate core rulemaking from supplemental notices
- support SQL analysis without duplicating document metadata

## Corpus tiers

`core_rulemaking`

- Rule
- Proposed Rule

`supplemental_notice`

- Notice

The supplemental corpus is retained because Federal Register notices contain meaningful immigration-policy activity such as Temporary Protected Status designations, employment-authorization actions, information collections, and program announcements. It is analyzed separately from formal rulemaking.

## Load

Set a PostgreSQL connection string:

```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/immigration_policy"
```

Run the ingestion pipeline and then load PostgreSQL:

```bash
python -m scripts.fetch_federal_register
python -m scripts.load_postgres
```
