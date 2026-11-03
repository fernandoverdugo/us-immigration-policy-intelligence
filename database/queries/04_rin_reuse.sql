SELECT
    dri.rin,
    COUNT(DISTINCT dri.document_number) AS document_count,
    MIN(d.publication_date) AS first_publication_date,
    MAX(d.publication_date) AS latest_publication_date
FROM document_regulation_identifiers dri
JOIN documents d
    ON d.document_number = dri.document_number
GROUP BY dri.rin
HAVING COUNT(DISTINCT dri.document_number) > 1
ORDER BY document_count DESC, latest_publication_date DESC;
