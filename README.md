# U.S. Immigration Policy Intelligence

An API-driven data engineering and NLP project for analyzing federal immigration rulemaking over time.

## Milestone 1: Federal Register ingestion

The first milestone builds a reproducible corpus of immigration-related Federal Register documents from 2017 through 2026.

### Initial agency scope

- U.S. Citizenship and Immigration Services (USCIS)
- U.S. Customs and Border Protection (CBP)
- U.S. Immigration and Customs Enforcement (ICE)
- Executive Office for Immigration Review (EOIR)

### Corpus inclusion strategy

Agency membership alone is not sufficient because some agencies, especially CBP, publish substantial non-immigration material.

Documents are retained when they meet at least one of these conditions:

1. They reference Title 8 of the Code of Federal Regulations.
2. Their title or abstract contains an immigration-policy term from the controlled project lexicon.
3. They are issued by EOIR.
4. They are issued by USCIS and are not clearly unrelated administrative material.

The raw API response is retained separately from the normalized analytical corpus so that inclusion logic can be audited and revised.

## Planned architecture

Federal Register API → raw JSON snapshots → normalization and validation → PostgreSQL → SQL analytics/NLP → FastAPI → web application

## Next milestones

1. Federal Register ingestion and corpus validation
2. PostgreSQL schema and loading
3. SQL-based exploratory analysis
4. NLP and semantic retrieval
5. FastAPI service
6. Web application and deployment
