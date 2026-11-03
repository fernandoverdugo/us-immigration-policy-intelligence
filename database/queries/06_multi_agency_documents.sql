SELECT
    d.document_number,
    d.publication_date,
    d.document_type,
    d.title,
    COUNT(*) AS agency_count,
    STRING_AGG(a.name, ' | ' ORDER BY a.name) AS agencies
FROM documents d
JOIN document_agencies da
    ON da.document_number = d.document_number
JOIN agencies a
    ON a.agency_id = da.agency_id
GROUP BY d.document_number, d.publication_date, d.document_type, d.title
HAVING COUNT(*) > 1
ORDER BY agency_count DESC, d.publication_date DESC;
