# Data

## Raw

`data/raw/` stores Federal Register API responses by agency. Raw files are not committed by default.

## Processed

`data/processed/federal_register_corpus.json` is the deduplicated Milestone 1 analytical corpus.

Every retained document includes:

- `source_agency_scope`
- `inclusion_reasons`
- `matched_terms`

These fields make the corpus-selection process auditable.

## Source

FederalRegister.gov public API.

The project uses FederalRegister.gov as a machine-readable research source. For legal research or authoritative legal citation, users should verify documents against the official Federal Register edition linked by the source site.
