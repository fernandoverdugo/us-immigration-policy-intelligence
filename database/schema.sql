CREATE TABLE IF NOT EXISTS agencies (
    agency_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    raw_name TEXT,
    slug TEXT NOT NULL UNIQUE,
    parent_agency_id INTEGER REFERENCES agencies(agency_id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE IF NOT EXISTS documents (
    document_number TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    abstract TEXT,
    action TEXT,
    document_type TEXT NOT NULL,
    subtype TEXT,
    publication_date DATE,
    effective_on DATE,
    comments_close_on DATE,
    citation TEXT,
    start_page INTEGER,
    end_page INTEGER,
    significant BOOLEAN,
    html_url TEXT,
    pdf_url TEXT,
    raw_text_url TEXT,
    corpus_tier TEXT NOT NULL CHECK (
        corpus_tier IN ('core_rulemaking', 'supplemental_notice')
    )
);

CREATE TABLE IF NOT EXISTS document_agencies (
    document_number TEXT NOT NULL REFERENCES documents(document_number) ON DELETE CASCADE,
    agency_id INTEGER NOT NULL REFERENCES agencies(agency_id) ON DELETE CASCADE,
    PRIMARY KEY (document_number, agency_id)
);

CREATE TABLE IF NOT EXISTS cfr_references (
    cfr_reference_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title_number INTEGER NOT NULL,
    part TEXT NOT NULL,
    UNIQUE (title_number, part)
);

CREATE TABLE IF NOT EXISTS document_cfr_references (
    document_number TEXT NOT NULL REFERENCES documents(document_number) ON DELETE CASCADE,
    cfr_reference_id BIGINT NOT NULL REFERENCES cfr_references(cfr_reference_id) ON DELETE CASCADE,
    PRIMARY KEY (document_number, cfr_reference_id)
);

CREATE TABLE IF NOT EXISTS regulation_identifiers (
    rin TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS document_regulation_identifiers (
    document_number TEXT NOT NULL REFERENCES documents(document_number) ON DELETE CASCADE,
    rin TEXT NOT NULL REFERENCES regulation_identifiers(rin) ON DELETE CASCADE,
    PRIMARY KEY (document_number, rin)
);

CREATE TABLE IF NOT EXISTS corpus_evidence (
    document_number TEXT NOT NULL REFERENCES documents(document_number) ON DELETE CASCADE,
    evidence_type TEXT NOT NULL CHECK (
        evidence_type IN ('source_scope', 'inclusion_reason', 'matched_term')
    ),
    evidence_value TEXT NOT NULL,
    PRIMARY KEY (document_number, evidence_type, evidence_value)
);

CREATE INDEX IF NOT EXISTS idx_documents_publication_date
    ON documents(publication_date);

CREATE INDEX IF NOT EXISTS idx_documents_type
    ON documents(document_type);

CREATE INDEX IF NOT EXISTS idx_documents_corpus_tier
    ON documents(corpus_tier);

CREATE INDEX IF NOT EXISTS idx_corpus_evidence_type_value
    ON corpus_evidence(evidence_type, evidence_value);
