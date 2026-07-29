-- List the Eagle-required merit badges without mislabelling the historical ones.
--
-- TRAP: `WHERE eagle_required = 0` for "not required", or `if (!badge.eagle_required)` in
--       any language. eagle_required is TRI-STATE: 1 required, 0 not required, NULL
--       UNKNOWN. Every discontinued badge is NULL, because the flag describes today's
--       requirements and a badge withdrawn decades ago has no answer. SQL is the safer
--       language here -- `= 0` silently drops NULL rows rather than coercing them false --
--       but the same query then reports a total that does not add up.
-- FIX:  branch on all three states. Filter `current = 1` when you mean today's list, and
--       treat NULL as "no claim made", never as a negative.

-- The census that makes the tri-state visible: NULL is confined to non-current badges.
SELECT CASE eagle_required WHEN 1 THEN 'required' WHEN 0 THEN 'not required'
                           ELSE 'unknown (NULL)' END      AS eagle_required,
       CASE current WHEN 1 THEN 'current' ELSE 'historical' END AS lifecycle,
       COUNT(*)                                            AS badges
FROM merit_badges
GROUP BY eagle_required, current
ORDER BY current DESC, eagle_required DESC;

SELECT m.id                                               AS badge,
       m.name,
       CASE m.current WHEN 1 THEN 'current' ELSE 'historical' END AS lifecycle
FROM merit_badges m
WHERE m.eagle_required = 1        -- deliberate: 1 only, never `<> 0`
ORDER BY m.current DESC, m.id;

-- @assert the unknown state is populated -- a two-valued reading of this column is wrong
-- | SELECT EXISTS(SELECT 1 FROM merit_badges WHERE eagle_required IS NULL);

-- @assert unknown is confined to historical badges: every current badge makes a claim
-- | SELECT NOT EXISTS(
-- |   SELECT 1 FROM merit_badges WHERE eagle_required IS NULL AND current = 1);

-- @assert the naive negative filter is strictly smaller than "everything not required"
-- | SELECT (SELECT COUNT(*) FROM merit_badges WHERE eagle_required = 0)
-- |      < (SELECT COUNT(*) FROM merit_badges WHERE eagle_required IS NOT 1);

-- @assert the three states are exhaustive, so a CASE over them cannot fall through
-- | SELECT (SELECT COUNT(*) FROM merit_badges)
-- |      = (SELECT COUNT(*) FROM merit_badges
-- |          WHERE eagle_required IS NULL OR eagle_required IN (0, 1));

-- @assert the flag is not a proxy for currency: a badge can be flagged and retired
-- | SELECT EXISTS(SELECT 1 FROM merit_badges WHERE eagle_required = 1 AND current = 0);
