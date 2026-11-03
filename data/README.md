# Data

## Raw

`data/raw/` stores Federal Register API responses by agency. Raw files are not committed by default.

## Processed

`data/processed/federal_register_corpus.json` is the deduplicated analytical corpus generated from the configured Federal Register publication-date window.

Every retained document includes:

- `source_agency_scopes`
- `inclusion_reasons`
- `matched_terms`

These fields make corpus selection auditable, including documents associated with more than one project agency scope.

## Snapshot metadata

`analysis/corpus_snapshot.json` records the retrieval timestamp, configured publication-date window, source, document counts, and scoped-agency associations for the current committed analytical snapshot.

Because the configured window extends through 2026 and the year is still in progress, rerunning ingestion can change current-year counts and downstream analytical outputs.

## Source

FederalRegister.gov public API.

The project uses FederalRegister.gov as a machine-readable research source. For legal research or authoritative legal citation, users should verify documents against the official Federal Register edition linked by the source site.
