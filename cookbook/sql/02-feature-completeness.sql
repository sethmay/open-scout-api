-- Read a camp's feature list against the tier of source it was surveyed from.
--
-- TRAP: ranking camps by feature count. The list is only as deep as the page it was read
--       from: `guide` is a council/national listing (coarse but uniform), `camp_page` is
--       the camp's own site (deep but uneven), `portal` is a registration portal (shallow
--       -- only what is on sale this season). An empty list is not "no archery", it is
--       "nobody has looked": 82 camps have never been surveyed at all and carry no tier.
-- FIX:  always read features_source_tier and features_verified_at beside the list, and
--       compare camps only within a tier. Absence of a tier is modelled, not defaulted.

WITH surveyed AS (
    -- The open version (valid_to IS NULL) is the current one, which is the same rule the
    -- `current` flag on the typed columns encodes.
    SELECT c.id,
           json_extract(v.value, '$.features_source_tier')  AS tier,
           json_extract(v.value, '$.features_verified_at')   AS verified_at
    FROM camps c, json_each(c.data, '$.versions') v
    WHERE json_extract(v.value, '$.valid_to') IS NULL
),
per_camp AS (
    SELECT camp_id, COUNT(*) AS features, SUM(signature) AS signature_features
    FROM camp_features GROUP BY camp_id
)
SELECT COALESCE(s.tier, '(never surveyed)')                  AS source_tier,
       COUNT(*)                                              AS camps,
       SUM(CASE WHEN p.camp_id IS NULL THEN 1 ELSE 0 END)    AS camps_with_empty_list,
       MIN(COALESCE(p.features, 0))                          AS min_features,
       MAX(COALESCE(p.features, 0))                          AS max_features,
       SUM(COALESCE(p.signature_features, 0))                AS signature_features,
       COALESCE(MIN(s.verified_at), '-')                      AS oldest_survey,
       COALESCE(MAX(s.verified_at), '-')                      AS newest_survey
FROM surveyed s
LEFT JOIN per_camp p ON p.camp_id = s.id
GROUP BY s.tier
ORDER BY camps DESC;

-- @assert the tier vocabulary is closed, so a consumer can enumerate it up front
-- | SELECT NOT EXISTS(
-- |   SELECT 1 FROM camps c, json_each(c.data, '$.versions') v
-- |    WHERE json_extract(v.value, '$.valid_to') IS NULL
-- |      AND json_extract(v.value, '$.features_source_tier') IS NOT NULL
-- |      AND json_extract(v.value, '$.features_source_tier')
-- |          NOT IN ('guide', 'camp_page', 'portal'));

-- @assert an unsurveyed camp claims neither a survey date nor a single feature
-- | SELECT NOT EXISTS(
-- |   SELECT 1 FROM camps c, json_each(c.data, '$.versions') v
-- |    WHERE json_extract(v.value, '$.valid_to') IS NULL
-- |      AND json_extract(v.value, '$.features_source_tier') IS NULL
-- |      AND (json_extract(v.value, '$.features_verified_at') IS NOT NULL
-- |           OR EXISTS(SELECT 1 FROM camp_features f WHERE f.camp_id = c.id)));

-- @assert every surveyed camp has a date, so "when" is never guesswork
-- | SELECT NOT EXISTS(
-- |   SELECT 1 FROM camps c, json_each(c.data, '$.versions') v
-- |    WHERE json_extract(v.value, '$.valid_to') IS NULL
-- |      AND json_extract(v.value, '$.features_source_tier') IS NOT NULL
-- |      AND json_extract(v.value, '$.features_verified_at') IS NULL);

-- @assert verified_at is a property of the survey pass, identical for all of a camp's rows
-- | SELECT NOT EXISTS(
-- |   SELECT 1 FROM camp_features f JOIN camps c ON c.id = f.camp_id,
-- |        json_each(c.data, '$.versions') v
-- |    WHERE json_extract(v.value, '$.valid_to') IS NULL
-- |      AND f.verified_at IS NOT json_extract(v.value, '$.features_verified_at'));

-- @assert more than one tier is in play, so cross-tier feature counts are incomparable
-- | SELECT (SELECT COUNT(DISTINCT json_extract(v.value, '$.features_source_tier'))
-- |           FROM camps c, json_each(c.data, '$.versions') v
-- |          WHERE json_extract(v.value, '$.valid_to') IS NULL) > 1;
