-- Cub Scout adventures per rank and adventure area.
--
-- TRAP: two assumptions, both wrong. First, that an adventure belongs to one rank --
--       Slingshot is offered at six ranks and BB Guns at five, so `GROUP BY adventure_id`
--       double-counts nothing but `JOIN ... ON rank_id` fans out, and a UNIQUE index on
--       adventure_id would reject the data. Second, that every adventure has an `area`:
--       area is the six-way required-adventure grid, so every elective is NULL, and so
--       are the special electives -- and even some required adventures leave it unset.
--       `GROUP BY area` therefore silently drops most of the catalogue.
-- FIX:  treat (adventure_id, rank_id) as the key and area as optional. Bucket NULL area
--       explicitly instead of letting it vanish.

SELECT ar.rank_id                                                    AS rank,
       SUM(CASE WHEN ar.area = 'character_leadership' THEN 1 ELSE 0 END) AS char_lead,
       SUM(CASE WHEN ar.area = 'citizenship'          THEN 1 ELSE 0 END) AS citizenship,
       SUM(CASE WHEN ar.area = 'outdoors'             THEN 1 ELSE 0 END) AS outdoors,
       SUM(CASE WHEN ar.area = 'personal_fitness'     THEN 1 ELSE 0 END) AS fitness,
       SUM(CASE WHEN ar.area = 'personal_safety'      THEN 1 ELSE 0 END) AS safety,
       SUM(CASE WHEN ar.area = 'family_reverence'     THEN 1 ELSE 0 END) AS family_rev,
       -- The bucket a `GROUP BY area` loses: it is the largest one.
       SUM(CASE WHEN ar.area IS NULL THEN 1 ELSE 0 END)               AS no_area,
       COUNT(*)                                                       AS total,
       (SELECT COUNT(*) FROM adventure_ranks x
         WHERE x.rank_id = ar.rank_id
           AND (SELECT COUNT(*) FROM adventure_ranks y
                 WHERE y.adventure_id = x.adventure_id) > 1)          AS shared_with_other_ranks
FROM adventure_ranks ar
GROUP BY ar.rank_id
ORDER BY total DESC, rank;

-- @assert an adventure can belong to several ranks: adventure_id is not a key here
-- | SELECT EXISTS(
-- |   SELECT adventure_id FROM adventure_ranks
-- |    GROUP BY adventure_id HAVING COUNT(DISTINCT rank_id) > 1);

-- @assert (adventure_id, rank_id) IS the key -- no rank lists the same adventure twice
-- | SELECT NOT EXISTS(
-- |   SELECT 1 FROM adventure_ranks GROUP BY adventure_id, rank_id HAVING COUNT(*) > 1);

-- @assert area is optional, and the missing side is not confined to electives
-- | SELECT EXISTS(SELECT 1 FROM adventure_ranks WHERE area IS NULL AND category = 'elective')
-- |    AND EXISTS(SELECT 1 FROM adventure_ranks WHERE area IS NULL AND category = 'required')
-- |    AND EXISTS(SELECT 1 FROM adventure_ranks WHERE area IS NOT NULL);

-- @assert where areas apply they form a complete grid: every such rank covers every area
-- | SELECT NOT EXISTS(
-- |   SELECT 1
-- |     FROM (SELECT DISTINCT rank_id FROM adventure_ranks WHERE area IS NOT NULL) r
-- |    CROSS JOIN (SELECT DISTINCT area FROM adventure_ranks WHERE area IS NOT NULL) a
-- |    WHERE NOT EXISTS(SELECT 1 FROM adventure_ranks x
-- |                      WHERE x.rank_id = r.rank_id AND x.area = a.area));

-- @assert exactly one adventure fills each (rank, area) slot -- the grid has no doubles
-- | SELECT NOT EXISTS(
-- |   SELECT 1 FROM adventure_ranks WHERE area IS NOT NULL
-- |    GROUP BY rank_id, area HAVING COUNT(*) <> 1);

-- @assert every row resolves to both an adventure and a rank that exist
-- | SELECT NOT EXISTS(
-- |   SELECT 1 FROM adventure_ranks ar
-- |    WHERE NOT EXISTS(SELECT 1 FROM adventures a WHERE a.id = ar.adventure_id)
-- |       OR NOT EXISTS(SELECT 1 FROM ranks r WHERE r.id = ar.rank_id));
