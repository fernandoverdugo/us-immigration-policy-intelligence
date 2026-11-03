WITH yearly AS (
    SELECT
        EXTRACT(YEAR FROM publication_date)::int AS publication_year,
        COUNT(*) FILTER (WHERE corpus_tier = 'core_rulemaking') AS core_rulemaking_count,
        COUNT(*) FILTER (WHERE corpus_tier = 'supplemental_notice') AS supplemental_notice_count,
        COUNT(*) AS total_count
    FROM documents
    WHERE publication_date IS NOT NULL
    GROUP BY publication_year
),
with_lag AS (
    SELECT
        *,
        LAG(total_count) OVER (ORDER BY publication_year) AS prior_total_count
    FROM yearly
)
SELECT
    publication_year,
    core_rulemaking_count,
    supplemental_notice_count,
    total_count,
    prior_total_count,
    CASE
        WHEN prior_total_count IS NULL OR prior_total_count = 0 THEN NULL
        ELSE ROUND(
            100.0 * (total_count - prior_total_count) / prior_total_count,
            1
        )
    END AS total_yoy_pct
FROM with_lag
ORDER BY publication_year;
