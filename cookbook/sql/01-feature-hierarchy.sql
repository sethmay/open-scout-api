-- Expand a coarse camp feature code to everything tagged beneath it.
--
-- TRAP: `WHERE code = 'aquatics'` finds almost nothing. Feature codes are hierarchical
--       through feature_vocab.broader, and a camp is tagged with the most specific code it
--       earns ('kayaking'), so a literal match returns only the camps too vaguely surveyed
--       to carry a leaf code -- the least informative rows, looking like the whole answer.
-- FIX:  compute the transitive closure over `broader` with a recursive CTE, then match
--       camp_features against the closure. Depth is not fixed -- ice_fishing sits under
--       fishing, which sits under aquatics -- so a single self-join is also wrong.

WITH RECURSIVE descendants(root, code) AS (
    -- Seed every term as its own descendant: the closure must include the coarse code
    -- itself, because a camp surveyed only from a guide really is tagged just 'aquatics'.
    SELECT code, code FROM feature_vocab
    UNION       -- UNION, not UNION ALL: dedupes, and terminates even if `broader` cycles
    SELECT d.root, v.code FROM feature_vocab v JOIN descendants d ON v.broader = d.code
)
SELECT v.code                                                          AS coarse_code,
       COUNT(DISTINCT d.code)                                          AS codes_in_closure,
       (SELECT COUNT(DISTINCT f.camp_id) FROM camp_features f
         WHERE f.code = v.code)                                        AS naive_camps,
       COUNT(DISTINCT f.camp_id)                                       AS closure_camps
FROM feature_vocab v
JOIN descendants d ON d.root = v.code
LEFT JOIN camp_features f ON f.code = d.code
WHERE v.broader IS NULL          -- the roots are the codes a human types into a filter
GROUP BY v.code
HAVING codes_in_closure > 1      -- a childless term cannot mislead, so leave it out
ORDER BY closure_camps - naive_camps DESC, v.code;

-- @assert the aquatics closure reaches its leaves, including the depth-two one
-- | WITH RECURSIVE sub(code) AS (
-- |   SELECT 'aquatics'
-- |   UNION SELECT v.code FROM feature_vocab v JOIN sub ON v.broader = sub.code)
-- | SELECT NOT EXISTS(
-- |   SELECT code FROM (SELECT 'kayaking' AS code UNION ALL SELECT 'canoeing'
-- |                     UNION ALL SELECT 'ice_fishing') want
-- |   WHERE want.code NOT IN (SELECT code FROM sub));

-- @assert closure matching strictly beats literal matching for a parent code
-- | WITH RECURSIVE sub(code) AS (
-- |   SELECT 'aquatics'
-- |   UNION SELECT v.code FROM feature_vocab v JOIN sub ON v.broader = sub.code)
-- | SELECT (SELECT COUNT(DISTINCT camp_id) FROM camp_features
-- |          WHERE code IN (SELECT code FROM sub))
-- |      > (SELECT COUNT(DISTINCT camp_id) FROM camp_features WHERE code = 'aquatics');

-- @assert every `broader` resolves to a real term, so the walk never dead-ends
-- | SELECT NOT EXISTS(
-- |   SELECT 1 FROM feature_vocab v WHERE v.broader IS NOT NULL
-- |     AND NOT EXISTS(SELECT 1 FROM feature_vocab p WHERE p.code = v.broader));

-- @assert camps are tagged with vocabulary codes only, so the join loses nothing
-- | SELECT NOT EXISTS(
-- |   SELECT 1 FROM camp_features f
-- |    WHERE NOT EXISTS(SELECT 1 FROM feature_vocab v WHERE v.code = f.code));
