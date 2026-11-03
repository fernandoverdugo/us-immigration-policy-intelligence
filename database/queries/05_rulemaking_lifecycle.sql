WITH rin_documents AS (
    SELECT
        dri.rin,
        d.document_number,
        d.document_type,
        d.publication_date,
        d.effective_on,
        d.title
    FROM document_regulation_identifiers dri
    JOIN documents d
        ON d.document_number = dri.document_number
    WHERE d.document_type IN ('Proposed Rule', 'Rule')
),
proposals AS (
    SELECT
        rin,
        MIN(publication_date) AS first_proposed_date
    FROM rin_documents
    WHERE document_type = 'Proposed Rule'
    GROUP BY rin
),
finals AS (
    SELECT
        rin,
        MIN(publication_date) AS first_final_date
    FROM rin_documents
    WHERE document_type = 'Rule'
    GROUP BY rin
)
SELECT
    p.rin,
    p.first_proposed_date,
    f.first_final_date,
    (f.first_final_date - p.first_proposed_date) AS days_proposal_to_final
FROM proposals p
JOIN finals f
    USING (rin)
WHERE f.first_final_date >= p.first_proposed_date
ORDER BY days_proposal_to_final DESC, p.rin;
