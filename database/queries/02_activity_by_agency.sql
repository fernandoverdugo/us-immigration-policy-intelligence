SELECT
    ce.evidence_value AS agency_scope,
    d.document_type,
    COUNT(DISTINCT d.document_number) AS document_count
FROM documents d
JOIN corpus_evidence ce
    ON ce.document_number = d.document_number
WHERE ce.evidence_type = 'source_scope'
GROUP BY ce.evidence_value, d.document_type
ORDER BY document_count DESC, ce.evidence_value, d.document_type;
