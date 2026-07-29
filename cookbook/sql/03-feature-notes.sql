-- Recover the per-feature prose that the flat JSON projection drops.
--
-- TRAP: reading current/camps.json and concluding no per-feature detail exists. That file
--       flattens `features` to a bare array of codes because carrying the notes would grow
--       the collection by roughly 40%. The note lives on the entity document, and the
--       SQLite build lifts it into camp_features.note -- 'aquatics' vs "aquatics classes
--       are held in the Adriatic" is the difference between a filter and an answer.
-- FIX:  query camp_features, not the flat list. `note` and `signature` are independent:
--       a signature feature need not be annotated, and most annotated ones are not
--       signature, so neither column can be inferred from the other.

SELECT f.code                                             AS feature,
       COUNT(*)                                           AS camps_tagged,
       SUM(CASE WHEN f.note IS NOT NULL THEN 1 ELSE 0 END) AS with_note,
       SUM(f.signature)                                   AS signature
FROM camp_features f
GROUP BY f.code
HAVING with_note > 0
ORDER BY with_note DESC, feature
LIMIT 15;

-- The notes are this dataset's own prose (CC BY-NC-SA), regenerated from public camp
-- pages -- truncated here only to keep the output readable.
SELECT f.camp_id                                          AS camp,
       f.code                                             AS feature,
       CASE f.signature WHEN 1 THEN 'signature' ELSE '' END AS flag,
       substr(f.note, 1, 58)
         || CASE WHEN length(f.note) > 58 THEN '...' ELSE '' END AS note
FROM camp_features f
WHERE f.note IS NOT NULL
ORDER BY f.signature DESC, f.camp_id, f.code
LIMIT 20;

-- @assert the detail the flat projection omits is actually present here
-- | SELECT EXISTS(SELECT 1 FROM camp_features WHERE note IS NOT NULL AND note <> '');

-- @assert `note` and `signature` vary independently -- neither implies the other
-- | SELECT EXISTS(SELECT 1 FROM camp_features WHERE signature = 1 AND note IS NULL)
-- |    AND EXISTS(SELECT 1 FROM camp_features WHERE signature = 0 AND note IS NOT NULL);

-- @assert notes are per feature, not per camp: some camps mix annotated and bare rows
-- | SELECT EXISTS(
-- |   SELECT camp_id FROM camp_features GROUP BY camp_id
-- |    HAVING COUNT(note) > 0 AND COUNT(note) < COUNT(*));

-- @assert a note never merely restates the vocabulary label it hangs off
-- | SELECT NOT EXISTS(
-- |   SELECT 1 FROM camp_features f JOIN feature_vocab v ON v.code = f.code
-- |    WHERE f.note IS NOT NULL AND lower(trim(f.note)) = lower(trim(v.label)));

-- @assert every annotated row still resolves to a camp that exists
-- | SELECT NOT EXISTS(
-- |   SELECT 1 FROM camp_features f
-- |    WHERE f.note IS NOT NULL
-- |      AND NOT EXISTS(SELECT 1 FROM camps c WHERE c.id = f.camp_id));
