-- Year-over-year movement in merit badge popularity, using only ordinal operations.
--
-- TRAP: AVG(earned_rank), SUM(earned_rank), or "rank 5 is twice as popular as rank 10".
--       The metric is `earned_rank` -- a position in a published ordering. There are no
--       counts anywhere in this dataset, so nothing here is summable, and the gap between
--       rank 1 and 2 is not the gap between 130 and 131. Comparing raw places across years
--       is a second-order version of the same mistake: the field is not the same size every
--       year (a badge can hold the same place in a larger field and have lost ground).
-- FIX:  compare a badge to itself with LAG over year, refuse to span a missing year, and
--       normalise to a within-year percentile when you need a cross-year magnitude.

WITH field AS (
    -- The field size IS the year's maximum rank, because each year is a complete 1..N.
    SELECT year, MAX(earned_rank) AS n FROM merit_badge_rankings GROUP BY year
),
moved AS (
    SELECT r.merit_badge_id, r.year, r.earned_rank,
           LAG(r.earned_rank) OVER w AS prev_rank,
           LAG(r.year)        OVER w AS prev_year
    FROM merit_badge_rankings r
    WINDOW w AS (PARTITION BY r.merit_badge_id ORDER BY r.year)
)
SELECT m.name                                              AS badge,
       mv.prev_year || '->' || mv.year                      AS years,
       mv.prev_rank                                        AS was,
       mv.earned_rank                                       AS now_at,
       mv.prev_rank - mv.earned_rank                        AS places_gained,
       -- Percentile is the cross-year-safe magnitude: place divided by that year's field.
       printf('%+.1f pts', 100.0 * (mv.prev_rank * 1.0 / pf.n - mv.earned_rank * 1.0 / cf.n))
                                                            AS percentile_shift
FROM moved mv
JOIN merit_badges m ON m.id = mv.merit_badge_id
JOIN field cf ON cf.year = mv.year
JOIN field pf ON pf.year = mv.prev_year
WHERE mv.year = (SELECT MAX(year) FROM merit_badge_rankings)
  AND mv.prev_year = mv.year - 1        -- never straddle a year the source did not publish
ORDER BY ABS(mv.prev_rank - mv.earned_rank) DESC, badge
LIMIT 15;

-- @assert every year is a complete 1..N ranking: no gaps, no ties, no duplicate badges
-- | SELECT NOT EXISTS(
-- |   SELECT 1 FROM (
-- |     SELECT year, COUNT(*) AS rows_, COUNT(DISTINCT earned_rank) AS ranks_,
-- |            COUNT(DISTINCT merit_badge_id) AS badges_,
-- |            MIN(earned_rank) AS lo, MAX(earned_rank) AS hi
-- |     FROM merit_badge_rankings GROUP BY year)
-- |    WHERE lo <> 1 OR hi <> rows_ OR ranks_ <> rows_ OR badges_ <> rows_);

-- @assert the field size changes between years, so a raw place delta is not commensurable
-- | SELECT (SELECT COUNT(DISTINCT n) FROM
-- |          (SELECT year, MAX(earned_rank) AS n FROM merit_badge_rankings GROUP BY year)) > 1;

-- @assert every ranked subject resolves to a badge, so the join drops nothing silently
-- | SELECT NOT EXISTS(
-- |   SELECT 1 FROM merit_badge_rankings r
-- |    WHERE NOT EXISTS(SELECT 1 FROM merit_badges m WHERE m.id = r.merit_badge_id));

-- @assert at least two consecutive years exist, or there is no trend to compute at all
-- | SELECT EXISTS(
-- |   SELECT 1 FROM merit_badge_rankings a
-- |    WHERE EXISTS(SELECT 1 FROM merit_badge_rankings b WHERE b.year = a.year - 1));

-- @assert movement runs both ways -- these are positions being reshuffled, not a total
-- | SELECT EXISTS(SELECT 1 FROM (
-- |     SELECT earned_rank - LAG(earned_rank) OVER (PARTITION BY merit_badge_id
-- |                                                 ORDER BY year) AS d
-- |     FROM merit_badge_rankings) WHERE d < 0)
-- |    AND EXISTS(SELECT 1 FROM (
-- |     SELECT earned_rank - LAG(earned_rank) OVER (PARTITION BY merit_badge_id
-- |                                                 ORDER BY year) AS d
-- |     FROM merit_badge_rankings) WHERE d > 0);
