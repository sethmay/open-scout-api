-- Which leadership positions each rank accepts, split by unit type.
--
-- TRAP: assuming "a position of responsibility" is one list. Acceptance is a property of
--       the (rank, unit_type) pair, not of the position. Bugler counts toward Star and Life
--       but NOT Eagle, and a Scouts BSA troop and a crew/ship accept almost disjoint sets.
--       Read the `positions` table alone and you get job titles with nothing saying where
--       any of them counts -- the asymmetry lives on the rank's requirement tree, not the
--       position entity, so it cannot be recovered from `positions`.
-- FIX:  join rank_positions, and key every lookup on (rank_id, position_id, unit_type).
--       Star and Life additionally allow a Scoutmaster-approved leadership project, which
--       is not a position at all and therefore has no row here.

SELECT p.name                                                             AS position,
       MAX(CASE WHEN r.rank_id = 'star'  AND r.unit_type = 'scout_troop'
                THEN 'x' ELSE '.' END)                                    AS star_troop,
       MAX(CASE WHEN r.rank_id = 'life'  AND r.unit_type = 'scout_troop'
                THEN 'x' ELSE '.' END)                                    AS life_troop,
       MAX(CASE WHEN r.rank_id = 'eagle' AND r.unit_type = 'scout_troop'
                THEN 'x' ELSE '.' END)                                    AS eagle_troop,
       MAX(CASE WHEN r.rank_id = 'star'  AND r.unit_type = 'crew_or_ship'
                THEN 'x' ELSE '.' END)                                    AS star_crew,
       MAX(CASE WHEN r.rank_id = 'life'  AND r.unit_type = 'crew_or_ship'
                THEN 'x' ELSE '.' END)                                    AS life_crew,
       MAX(CASE WHEN r.rank_id = 'eagle' AND r.unit_type = 'crew_or_ship'
                THEN 'x' ELSE '.' END)                                    AS eagle_crew,
       COUNT(DISTINCT r.unit_type)                                        AS unit_types
FROM rank_positions r
JOIN positions p ON p.id = r.position_id
GROUP BY r.position_id
-- Rows where the rank columns disagree are the whole point, so sort them to the top.
ORDER BY (star_troop <> eagle_troop) DESC, (star_troop <> star_crew) DESC, p.name;

-- @assert Star and Eagle do not accept the same troop positions
-- | SELECT EXISTS(
-- |   SELECT position_id FROM rank_positions
-- |    WHERE rank_id = 'star' AND unit_type = 'scout_troop'
-- |   EXCEPT
-- |   SELECT position_id FROM rank_positions
-- |    WHERE rank_id = 'eagle' AND unit_type = 'scout_troop');

-- @assert Bugler counts for Star in a troop and does not count for Eagle
-- | SELECT EXISTS(SELECT 1 FROM rank_positions
-- |                WHERE rank_id = 'star' AND position_id = 'bugler'
-- |                  AND unit_type = 'scout_troop')
-- |    AND NOT EXISTS(SELECT 1 FROM rank_positions
-- |                    WHERE rank_id = 'eagle' AND position_id = 'bugler');

-- @assert Star's troop set is a strict superset of Eagle's: Eagle adds no position
-- | SELECT NOT EXISTS(
-- |   SELECT position_id FROM rank_positions
-- |    WHERE rank_id = 'eagle' AND unit_type = 'scout_troop'
-- |   EXCEPT
-- |   SELECT position_id FROM rank_positions
-- |    WHERE rank_id = 'star' AND unit_type = 'scout_troop');

-- @assert both unit types are present AND acceptance is not uniform across them
-- | SELECT (SELECT COUNT(DISTINCT unit_type) FROM rank_positions) = 2
-- |    AND EXISTS(SELECT position_id FROM rank_positions GROUP BY position_id
-- |                HAVING COUNT(DISTINCT unit_type) = 1);

-- Both directions, and per rank: neither side may be dropped, emptied, or shrunk to a subset
-- of the other without this failing. This is the only assert that covers the TRAP at :5.
-- @assert for every rank, each unit type accepts a position the other rejects
-- | WITH pairs(rank_id, mine, theirs) AS (
-- |   SELECT DISTINCT rank_id, 'scout_troop', 'crew_or_ship' FROM rank_positions
-- |   UNION ALL
-- |   SELECT DISTINCT rank_id, 'crew_or_ship', 'scout_troop' FROM rank_positions)
-- | SELECT NOT EXISTS(
-- |   SELECT 1 FROM pairs p
-- |    WHERE NOT EXISTS(
-- |      SELECT position_id FROM rank_positions
-- |       WHERE rank_id = p.rank_id AND unit_type = p.mine
-- |      EXCEPT
-- |      SELECT position_id FROM rank_positions
-- |       WHERE rank_id = p.rank_id AND unit_type = p.theirs));

-- @assert the unit_type vocabulary is closed, so a pivot cannot miss a column
-- | SELECT NOT EXISTS(
-- |   SELECT 1 FROM rank_positions
-- |    WHERE unit_type IS NULL OR unit_type NOT IN ('scout_troop', 'crew_or_ship'));

-- @assert every accepted position resolves to a real position entity
-- | SELECT NOT EXISTS(
-- |   SELECT 1 FROM rank_positions r
-- |    WHERE NOT EXISTS(SELECT 1 FROM positions p WHERE p.id = r.position_id));
