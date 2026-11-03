SELECT
    d.document_number,
    d.publication_date,
    d.document_type,
    d.title,
    COUNT(*) AS scoped_agency_count,
    STRING_AGG(ce.evidence_value, ' | ' ORDER BY ce.evidence_value) AS scoped_agencies
FROM documents d
JOIN corpus_evidence ce
    ON ce.document_number = d.document_number
WHERE ce.evidence_type = 'source_scope'
GROUP BY d.document_number, d.publication_date, d.document_type, d.title
HAVING COUNT(*) > 1
ORDER BY scoped_agency_count DESC, d.publication_date DESC;
