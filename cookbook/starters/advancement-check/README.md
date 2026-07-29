# advancement-check

"What does this Scout still need?" Give it a rank already earned, the merit badges held, and the
positions of responsibility served with months, and it walks the in-force requirement set for
every remaining Scouts BSA rank and reports what is left.

## Usage

    export OSA_BASE=../../../dist          # a built dist/, or the published base from meta.json
    export PYTHONPATH=../../python         # the shared osa.py helper

    python main.py --rank first-class \
        --badges camping,cooking,first-aid,swimming,communication,personal-fitness \
        --positions patrol-leader:6,bugler:12

    python main.py --selftest        # canned scenario, asserts the invariants, exits nonzero on failure

`--base <url-or-directory>` works instead of `OSA_BASE`. A directory (a built `dist/`) is a valid
base, so the tool runs offline against a checkout.

## Traps it demonstrates

**Eagle requirement 3 is a 14-slot graph, not a badge list.** Three of its 14 lettered children
carry `choose: 1`, each satisfied by any one of 2-3 alternatives, so 14 slots span 18 distinct
`merit-badge:` refs. The tool prints slots filled, slots open, and the alternatives inside each
open either/or slot.

**14 slots, 18 flagged badges and 21 cumulative badges are three different numbers.** The 18 is
the `eagle_required` flag list that Star's and Life's `badge_count.from_eagle_required` cites;
`badge_count.cumulative` on Eagle is 21. Conflating them silently misreports a Scout's progress.
The selftest asserts the badge refs in Eagle's tree are *exactly* the flagged list, which is what
makes the distinction between 14 and 18 structural rather than a coincidence.

**`eagle_required: null` means unknown, not false.** Historical badges carry null. The tool counts
only `true`, and says so when a supplied badge is one of the unknowns.

**Position acceptance is asymmetric and lives on the rank, not the position.** Bugler appears in
Star's and Life's leadership trees but not Eagle's; Star and Life also publish a Scoutmaster-
approved project as an alternative to holding a position, and Eagle does not. `position:bugler`
itself carries nothing about any of this, so acceptance is resolved from each rank's own tree.

**`tenure_months` hangs off the leadership requirement.** Four months for Star, six for Life and
Eagle, so the same position can qualify for one rank and not the next.

**The requirement number is not a contract, and neither is the set id.** Leadership is `5` under
Star and Life but `4` under Eagle, so both requirements are located by shape (the one carrying
`position:` refs, the one carrying `badge_count`). The set itself is resolved by
`effective_to is None`, never by pinning the string `star-2024`.

## Licensing

Requirement text is (c) Scouting America and is *not* under this dataset's CC BY-NC-SA license, so
this tool prints structure, refs, slots and counts. It does not merely decline to print the text --
it never reads it: the requirement tree is rebuilt without a `text` field as it is fetched, so a
non-position alternative is reported by its requirement number alone. The document's own
`text_rights` string is printed as a footer.
