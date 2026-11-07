# SQL analysis

This directory contains compact aggregate outputs generated from the current committed Federal Register corpus through PostgreSQL.

The current snapshot contains **1,062 unique documents** published from 2017 through the current 2026 retrieval period. The corpus separates formal **Rules / Proposed Rules** from the much larger supplemental **Notice** layer.

## Key findings

### Regulatory activity varies substantially over time

Core rulemaking activity (Rules + Proposed Rules) peaks at **20 documents in 2020** within the current corpus. Total scoped activity reaches **137 documents in 2023**, driven primarily by notices.

Because 2026 is still in progress, its annual total should not be compared with completed calendar years as a final-year count.

### USCIS dominates the supplemental notice corpus

USCIS accounts for **853 notices** in the current scoped snapshot. Formal rulemaking is more distributed: EOIR contributes **46 Rules and 17 Proposed Rules**, while CBP contributes **18 Rules and 4 Proposed Rules**.

These counts describe the project's scoped Federal Register corpus and should not be interpreted as complete measures of all agency activity outside the inclusion rules.

### Immigration-court and asylum regulations are prominent

The most frequently referenced CFR parts include:

- **8 CFR Part 1003** — 43 documents
- **8 CFR Part 1208** — 35 documents
- **8 CFR Part 208** — 26 documents
- **8 CFR Part 1240** — 22 documents

This concentration is consistent with substantial activity involving immigration proceedings, asylum, and removal-related regulatory frameworks.

### RINs provide a useful rulemaking linkage mechanism

The current snapshot contains **56 Regulation Identifier Numbers (RINs)** that appear across multiple corpus documents.

Sixteen RINs contain both a Proposed Rule and a later Rule. Their proposal-to-final intervals range from **82 to 714 days**, with a **median of 200 days**.

The timing analysis is descriptive. A shared RIN is useful evidence of a common regulatory action, but the first proposal and first final rule under a RIN do not necessarily capture every intermediate or legally relevant stage.

### Genuine cross-agency scoped documents are uncommon

Only **3 documents** in the current snapshot are associated with more than one of the four project agency scopes:

- EOIR + ICE — *Imposition and Collection of Civil Penalties for Certain Immigration-Related Violations* (2025)
- EOIR + USCIS — *Procedures for Asylum and Bars to Asylum Eligibility* (2019)
- EOIR + USCIS — *Implementing Bilateral and Multilateral Asylum Cooperative Agreements Under the Immigration and Nationality Act* (2019)

This result uses the project's scoped-agency evidence rather than Federal Register parent/child agency metadata.

## Reproducibility

The source SQL lives in `database/queries/`.

The analytical workflow:

1. retrieves the Federal Register corpus,
2. applies the auditable inclusion rules,
3. loads the normalized PostgreSQL schema,
4. executes the SQL analytical layer,
5. publishes compact aggregate outputs.

The generated CSV files in `analysis/outputs/` are compact analytical outputs. Raw API responses and the full generated document corpus are intentionally not committed.
