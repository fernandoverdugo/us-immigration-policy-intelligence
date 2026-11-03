SELECT
    c.title_number,
    c.part,
    COUNT(DISTINCT dcr.document_number) AS document_count
FROM cfr_references c
JOIN document_cfr_references dcr
    ON dcr.cfr_reference_id = c.cfr_reference_id
GROUP BY c.title_number, c.part
ORDER BY document_count DESC, c.title_number, c.part
LIMIT 25;
