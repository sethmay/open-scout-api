-- Audit camp coordinates before plotting any of them.
--
-- TRAP: pinning every (lat, lon) on a map. A quarter of the coordinates are `approximate`
--       -- city or state-level backfills good enough to answer "which state" and useless for
--       "drive me there". They are indistinguishable from surveyed coordinates by value
--       alone: both are plausible decimals inside the right state. Rendering them together
--       produces a map that is confidently wrong, with camps sitting in fields and lakes.
-- FIX:  read geo_precision alongside the pair and let it drive the rendering. It is
--       tri-state like every other claim here: `exact`, `approximate`, or NULL for "no
--       coordinate at all" -- and NULL precision never accompanies a coordinate, so the
--       column is safe to switch on rather than guess from.

WITH camp_now AS (
    -- The open version (valid_to IS NULL) is the current one, matching the `current` flag.
    SELECT c.id, c.name, c.state,
           json_extract(v.value, '$.geo_precision')  AS geo_precision,
           json_extract(v.value, '$.lat')            AS lat,
           json_extract(v.value, '$.lon')            AS lon
    FROM camps c, json_each(c.data, '$.versions') v
    WHERE json_extract(v.value, '$.valid_to') IS NULL
)
SELECT COALESCE(geo_precision, '(no coordinate)')                  AS geo_precision,
       COUNT(*)                                                    AS camps,
       SUM(CASE WHEN lat IS NOT NULL AND lon IS NOT NULL
                THEN 1 ELSE 0 END)                                 AS with_coordinates,
       COUNT(DISTINCT state)                                       AS states,
       CASE geo_precision
            WHEN 'exact' THEN 'safe to pin'
            WHEN 'approximate' THEN 'show as a region, never a pin'
            ELSE 'nothing to draw' END                             AS rendering,
       -- Rounded to keep the digits from implying precision the row does not have.
       CASE WHEN MIN(lat) IS NULL THEN '-'
            ELSE printf('%.1f .. %.1f', MIN(lat), MAX(lat)) END      AS lat_span
FROM camp_now
GROUP BY geo_precision
ORDER BY camps DESC;

-- @assert no camp carries a coordinate without stating its precision
-- | SELECT NOT EXISTS(
-- |   SELECT 1 FROM camps c, json_each(c.data, '$.versions') v
-- |    WHERE json_extract(v.value, '$.valid_to') IS NULL
-- |      AND json_extract(v.value, '$.geo_precision') IS NULL
-- |      AND (json_extract(v.value, '$.lat') IS NOT NULL
-- |           OR json_extract(v.value, '$.lon') IS NOT NULL));

-- @assert the converse also holds: a stated precision always has a coordinate to describe
-- | SELECT NOT EXISTS(
-- |   SELECT 1 FROM camps c, json_each(c.data, '$.versions') v
-- |    WHERE json_extract(v.value, '$.valid_to') IS NULL
-- |      AND json_extract(v.value, '$.geo_precision') IS NOT NULL
-- |      AND (json_extract(v.value, '$.lat') IS NULL
-- |           OR json_extract(v.value, '$.lon') IS NULL));

-- @assert the precision vocabulary is closed, so a CASE over it cannot fall through
-- | SELECT NOT EXISTS(
-- |   SELECT 1 FROM camps c, json_each(c.data, '$.versions') v
-- |    WHERE json_extract(v.value, '$.valid_to') IS NULL
-- |      AND json_extract(v.value, '$.geo_precision') IS NOT NULL
-- |      AND json_extract(v.value, '$.geo_precision') NOT IN ('exact', 'approximate'));

-- @assert approximate coordinates are actually present -- filtering them is not academic
-- | SELECT EXISTS(
-- |   SELECT 1 FROM camps c, json_each(c.data, '$.versions') v
-- |    WHERE json_extract(v.value, '$.valid_to') IS NULL
-- |      AND json_extract(v.value, '$.geo_precision') = 'approximate');

-- @assert mappable camps are a strict subset of camps with coordinates
-- | SELECT (SELECT COUNT(*) FROM camps c, json_each(c.data, '$.versions') v
-- |          WHERE json_extract(v.value, '$.valid_to') IS NULL
-- |            AND json_extract(v.value, '$.geo_precision') = 'exact')
-- |      < (SELECT COUNT(*) FROM camps c, json_each(c.data, '$.versions') v
-- |          WHERE json_extract(v.value, '$.valid_to') IS NULL
-- |            AND json_extract(v.value, '$.lat') IS NOT NULL);

-- @assert every camp has exactly one open version, so the join cannot duplicate a camp
-- | SELECT NOT EXISTS(
-- |   SELECT 1 FROM camps c
-- |    WHERE (SELECT COUNT(*) FROM json_each(c.data, '$.versions') v
-- |            WHERE json_extract(v.value, '$.valid_to') IS NULL) <> 1);
