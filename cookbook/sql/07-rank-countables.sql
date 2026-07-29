-- The numbers a rank actually requires: tenure months and the two badge counts.
--
-- TRAP: reading badges_cumulative as "badges to earn at this rank". Eagle's requirement 3
--       carries earn=10 and cumulative=21: ten more badges, twenty-one held in total. Swap
--       them and you overstate the rank's work twofold. The second confusion is
--       badges_from_eagle_required -- that is how many of the rank's badges must come from
--       the 18-badge flagged list (Star 4 of 6, Life 3 of 5), and Eagle leaves it NULL
--       because Eagle does not count from a list: its requirement 3 is a 14-slot graph,
--       three of whose slots are either/or choices. 18 and 14 are different numbers about
--       different things, and neither is a badge total.
-- FIX:  read earn and cumulative as distinct columns, and treat NULL as "this rank does not
--       express the requirement that way" rather than zero.

SELECT ra.program,
       ra.rank_id                                                     AS rank,
       ra.requirement                                                 AS req,
       COALESCE(CAST(ra.tenure_months AS TEXT), '-')                  AS tenure_months,
       COALESCE(CAST(ra.badges_earn AS TEXT), '-')                    AS badges_earn,
       COALESCE(CAST(ra.badges_cumulative AS TEXT), '-')              AS badges_cumulative,
       COALESCE(CAST(ra.badges_from_eagle_required AS TEXT), '-')     AS from_flagged_list,
       CASE WHEN ra.badges_earn IS NOT NULL AND ra.badges_cumulative IS NOT NULL
            THEN 'earn ' || ra.badges_earn || ' more, hold '
                 || ra.badges_cumulative || ' total'
            WHEN ra.tenure_months IS NOT NULL
            THEN 'serve ' || ra.tenure_months || ' months'
            ELSE '' END                                               AS reading
FROM rank_advancement ra
ORDER BY ra.program, ra.rank_id, ra.requirement;

-- @assert cumulative is never below earn -- a total and an increment, not interchangeable
-- | SELECT NOT EXISTS(
-- |   SELECT 1 FROM rank_advancement
-- |    WHERE badges_earn IS NOT NULL AND badges_cumulative IS NOT NULL
-- |      AND badges_cumulative < badges_earn);

-- @assert cumulative strictly exceeds earn somewhere, so the columns are not redundant
-- | SELECT EXISTS(SELECT 1 FROM rank_advancement WHERE badges_cumulative > badges_earn);

-- @assert the flagged-list quota is a subset of that rank's own badges, never a total
-- | SELECT NOT EXISTS(
-- |   SELECT 1 FROM rank_advancement
-- |    WHERE badges_from_eagle_required IS NOT NULL
-- |      AND (badges_earn IS NULL OR badges_from_eagle_required > badges_earn));

-- @assert Eagle expresses no flagged-list quota while Star and Life both do
-- | SELECT (SELECT badges_from_eagle_required FROM rank_advancement
-- |          WHERE rank_id = 'eagle' AND badges_earn IS NOT NULL) IS NULL
-- |    AND NOT EXISTS(SELECT 1 FROM rank_advancement
-- |                    WHERE rank_id IN ('star', 'life') AND badges_earn IS NOT NULL
-- |                      AND badges_from_eagle_required IS NULL);

-- @assert the flagged badge list and Eagle's requirement-3 slot count are different sizes
-- | WITH eagle3 AS (
-- |   SELECT r.value AS node
-- |     FROM requirement_sets rs, json_each(rs.data, '$.requirements') r
-- |    WHERE rs.subject = 'rank:eagle' AND rs.effective_to IS NULL
-- |      AND json_extract(r.value, '$.number') = '3')
-- | SELECT (SELECT COUNT(*) FROM eagle3, json_each(eagle3.node, '$.children'))
-- |     <> (SELECT COUNT(*) FROM merit_badges WHERE eagle_required = 1);

-- @assert Eagle's requirement-3 badge counts match the in-force requirement document
-- | WITH eagle3 AS (
-- |   SELECT r.value AS node
-- |     FROM requirement_sets rs, json_each(rs.data, '$.requirements') r
-- |    WHERE rs.subject = 'rank:eagle' AND rs.effective_to IS NULL
-- |      AND json_extract(r.value, '$.number') = '3')
-- | SELECT (SELECT json_extract(node, '$.badge_count.earn') FROM eagle3)
-- |      = (SELECT badges_earn FROM rank_advancement
-- |          WHERE rank_id = 'eagle' AND requirement = '3')
-- |   AND (SELECT json_extract(node, '$.badge_count.cumulative') FROM eagle3)
-- |      = (SELECT badges_cumulative FROM rank_advancement
-- |          WHERE rank_id = 'eagle' AND requirement = '3');

-- @assert every advancement row hangs off a rank that exists
-- | SELECT NOT EXISTS(
-- |   SELECT 1 FROM rank_advancement ra
-- |    WHERE NOT EXISTS(SELECT 1 FROM ranks r WHERE r.id = ra.rank_id));
