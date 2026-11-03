SELECT
    EXTRACT(YEAR FROM publication_date)::int AS publication_year,
    document_type,
    COUNT(*) AS document_count
FROM documents
WHERE publication_date IS NOT NULL
GROUP BY publication_year, document_type
ORDER BY publication_year, document_type;
