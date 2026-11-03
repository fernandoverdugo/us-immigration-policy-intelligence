SELECT
    a.name AS agency_name,
    d.document_type,
    COUNT(*) AS document_count
FROM documents d
JOIN document_agencies da
    ON da.document_number = d.document_number
JOIN agencies a
    ON a.agency_id = da.agency_id
GROUP BY a.name, d.document_type
ORDER BY document_count DESC, a.name, d.document_type;
