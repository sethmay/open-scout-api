-- Follow council mergers and absorptions back to the councils they consumed.
--
-- TRAP: assuming a merger overwrote its predecessor. It did not: the absorbed council keeps
--       its own row and its own id forever, with current = 0. So a lookup of an old council
--       id still succeeds -- which is the point, historic records reference it -- and code
--       that treats "row exists" as "council operates today" reports hundreds of live
--       councils that closed decades ago. The second trap is `date`: it is frequently NULL
--       (the event is documented, the year is not), so ORDER BY date, WHERE date > '2000'
--       and any date arithmetic silently discard those events.
-- FIX:  read `current` for the lifecycle question and the events table for the lineage.
--       Participants live in the event's JSON, each `{ref, role}` with a `council:` prefix
--       on the ref -- strip the prefix to join. Bucket NULL dates rather than sorting them
--       into oblivion.

WITH participants AS (
    SELECT e.dataset, e.id AS event_id, e.type, e.date,
           json_extract(p.value, '$.role')                          AS role,
           -- refs are namespaced ('council:annawon'), so the entity id is after the colon
           substr(json_extract(p.value, '$.ref'),
                  instr(json_extract(p.value, '$.ref'), ':') + 1)    AS entity_id
    FROM events e, json_each(e.data, '$.participants') p
    WHERE e.dataset = 'councils'
)
SELECT pre.type,
       COALESCE(pre.date, '(undated)')                              AS occurred,
       gone.name                                                    AS predecessor,
       gone.id                                                      AS predecessor_id,
       CASE gone.current WHEN 1 THEN 'STILL CURRENT'
                         ELSE 'retired, row retained' END           AS predecessor_row,
       (SELECT kept.name
          FROM participants s JOIN councils kept ON kept.id = s.entity_id
         WHERE s.event_id = pre.event_id
           AND s.role IN ('continuing', 'successor'))                AS into_council
FROM participants pre
JOIN councils gone ON gone.id = pre.entity_id
WHERE pre.role = 'predecessor'
-- Undated events first: they are the ones a date sort would have hidden.
ORDER BY pre.date IS NULL DESC, pre.date DESC, predecessor
LIMIT 20;

-- @assert every participant ref resolves to a council row -- lineage is never dangling
-- | SELECT NOT EXISTS(
-- |   SELECT 1 FROM events e, json_each(e.data, '$.participants') p
-- |    WHERE e.dataset = 'councils'
-- |      AND NOT EXISTS(
-- |            SELECT 1 FROM councils c
-- |             WHERE c.id = substr(json_extract(p.value, '$.ref'),
-- |                                 instr(json_extract(p.value, '$.ref'), ':') + 1)));

-- @assert the predecessor row survives the merger and is marked non-current
-- | SELECT NOT EXISTS(
-- |   SELECT 1 FROM events e, json_each(e.data, '$.participants') p
-- |    JOIN councils c ON c.id = substr(json_extract(p.value, '$.ref'),
-- |                                     instr(json_extract(p.value, '$.ref'), ':') + 1)
-- |    WHERE e.dataset = 'councils'
-- |      AND json_extract(p.value, '$.role') = 'predecessor'
-- |      AND c.current = 1);

-- @assert the surviving side of a merger IS current, so the pair is genuinely directional
-- | SELECT EXISTS(
-- |   SELECT 1 FROM events e, json_each(e.data, '$.participants') p
-- |    JOIN councils c ON c.id = substr(json_extract(p.value, '$.ref'),
-- |                                     instr(json_extract(p.value, '$.ref'), ':') + 1)
-- |    WHERE e.dataset = 'councils'
-- |      AND json_extract(p.value, '$.role') IN ('continuing', 'successor')
-- |      AND c.current = 1);

-- @assert undated events exist, so any date predicate is a silent filter
-- | SELECT EXISTS(SELECT 1 FROM events WHERE date IS NULL);

-- @assert a single event can consume several predecessors -- do not expect a 1:1 pair
-- | SELECT EXISTS(
-- |   SELECT e.id FROM events e, json_each(e.data, '$.participants') p
-- |    WHERE e.dataset = 'councils' AND json_extract(p.value, '$.role') = 'predecessor'
-- |    GROUP BY e.id HAVING COUNT(*) > 1);

-- @assert every event names at least one participant, so the join can never blank out
-- | SELECT NOT EXISTS(
-- |   SELECT 1 FROM events e
-- |    WHERE COALESCE(json_array_length(e.data, '$.participants'), 0) = 0);
