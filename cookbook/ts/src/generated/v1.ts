/**
 * GENERATED FILE -- DO NOT EDIT.
 * Regenerate with `python tools/gen_types.py`; CI fails on drift (`--check`).
 * Source of truth: schema/v1/published-*.schema.json
 */


export interface CurrentCouncil {
  readonly id: string;
  readonly name: string;
  readonly bsa_number: number | null;
  readonly hq_city: string | null;
  readonly hq_state: string | null;
  readonly website: string | null;
  readonly territory: string | null;
  readonly territory_number: number | null;
  readonly verified_at: string;
  readonly method: string;
  readonly confidence: number;
}

export interface CurrentTerritory {
  readonly id: string;
  readonly number: number | null;
  readonly name: string;
  readonly division_type: "council_service_territory" | "national_service_territory" | "region" | "area";
  readonly verified_at: string;
  readonly method: string;
  readonly confidence: number;
}

export interface CurrentMeritBadge {
  readonly id: string;
  readonly name: string;
  /** Short original-prose summary of what a Scout does to earn the badge, written for browsing. Deliberately NOT the pamphlet or requirement wording: requirement text is © Scouting America and is published only under the `text_rights` carve-out on requirement-sets, so this field is original and CC-licen… */
  readonly description: string | null;
  readonly tags: readonly string[];
  readonly eagle_required: boolean;
  readonly url: string | null;
  readonly verified_at: string;
  readonly method: string;
  readonly confidence: number;
}

/** Set when this camp shares a location with other distinct camps: a grouping so consumers render one reservation pin per property. `id` is a STABLE OPAQUE GROUPING KEY — deliberately a bare slug, NOT a '{kind}:{slug}' entity reference, because no reservation entity exists. If a reservation dataset is… */
export interface CurrentCampReservation {
  readonly id: string;
  readonly name?: string | null;
}

export interface CurrentCamp {
  readonly id: string;
  readonly name: string;
  readonly camp_type: string;
  readonly operator: "council" | "national" | "other" | "unknown";
  readonly council: string | null;
  readonly parent: string | null;
  readonly state: string | null;
  readonly city: string | null;
  readonly lat: number | null;
  readonly lon: number | null;
  readonly geo_precision: "exact" | "approximate" | null;
  readonly elevation_ft?: number | null;
  readonly july_high_f?: number | null;
  readonly july_low_f?: number | null;
  /** Set when this camp shares a location with other distinct camps: a grouping so consumers render one reservation pin per property. `id` is a STABLE OPAQUE GROUPING KEY — deliberately a bare slug, NOT a '{kind}:{slug}' entity reference, because no reservation entity exists. If a reservation dataset is… */
  readonly reservation: CurrentCampReservation | null;
  readonly website: string | null;
  readonly program_types: readonly string[];
  readonly summary: string | null;
  /** What this camp offers, as codes from the open `camp-features` vocabulary published at v1/vocab/camp-features.json. Sorted, unique, and flattened for filtering: the canonical per-camp document (v1/camps/{id}.json) carries the same features as objects with an optional prose `note`, which is deliberat… */
  readonly features: readonly string[];
  /** The subset of `features` a camp presents as a headline draw rather than table stakes — the same feature can be signature at one camp and unremarkable at another (a climbing tower is ordinary in Colorado and a real differentiator on the prairie). Intended for ranking and badge rendering in list view… */
  readonly features_signature: readonly string[];
  /** How complete the source behind `features` was, in the same spirit as `geo_precision` for coordinates. `guide`: a camp-specific document was read (leader's/program guide, schedule, or labelled map) — averages 21 features per camp. `camp_page`: a descriptive page owned by the camp or council — averag… */
  readonly features_source_tier: "guide" | "camp_page" | "portal" | null;
  /** Date of the last deliberate features survey of this camp against its own sources. Four states, and the distinction matters: `null` + empty `features` = never surveyed, nothing is known; `null` + non-empty = features arrived from a bulk import and were never deliberately verified; a date + non-empty… */
  readonly features_verified_at: string | null;
  readonly council_name: string | null;
  readonly council_website: string | null;
  readonly council_number: number | null;
  readonly url: string | null;
  readonly operating_status: "active" | "not_operating" | "closed";
  readonly verified_at: string;
  readonly imported_at: string | null;
  readonly method: string;
  readonly confidence: number;
}

export interface CurrentRank {
  readonly id: string;
  readonly name: string;
  readonly program: string;
  readonly order: number;
  readonly url: string | null;
  readonly verified_at: string;
  readonly method: string;
  readonly confidence: number;
}

export interface CurrentAward {
  readonly id: string;
  readonly name: string;
  readonly category: string;
  readonly audience: "youth" | "adult" | "both";
  readonly programs?: readonly string[];
  readonly square_knot_no: string | null;
  readonly url?: string | null;
  readonly verified_at: string;
  readonly method: string;
  readonly confidence: number;
}

export interface CurrentOALodge {
  readonly id: string;
  readonly name: string;
  readonly council: string | null;
  readonly section: string | null;
  readonly hq_state?: string | null;
  readonly lat?: number | null;
  readonly lon?: number | null;
  readonly verified_at: string;
  readonly method: string;
  readonly confidence: number;
}

/** The in-force requirement-set document for a subject (rank or merit badge): effective_to is null. A requirement-set is immutable and effective-dated rather than versioned, so it has no `current` flag. Requirement CONTENT lives in the per-document file v1/requirement-sets/{id}.json — this projection… */
export interface CurrentRequirementSet {
  readonly id: string;
  readonly subject: string;
  readonly effective_from: string;
  readonly includes_official_text: boolean;
  readonly verified_at: string;
  readonly method: string;
  readonly confidence: number;
}

/** A Cub Scout adventure currently offered. `ranks` is the reverse index of the rank requirement-sets, which remain authoritative for grouping and choose-counts. The shooting-sports adventures carry a null `url` and have no requirement-set; join v1/requirement-sets/index.json on subject 'adventure:<id… */
export interface CurrentAdventure {
  readonly id: string;
  readonly name: string;
  readonly program: string;
  readonly ranks: readonly string[];
  /** Vocabulary CODE from v1/vocab/adventure-categories.json, never a display label. */
  readonly category: string;
  /** The requirement area this adventure fills for its rank, or null for electives. Every rank's six required adventures cover the six areas of v1/vocab/adventure-areas.json exactly once each. A vocabulary CODE, never a display label — two Arrow of Light adventures are *named* after areas, so publishing… */
  readonly area: string | null;
  readonly url: string | null;
  readonly verified_at: string;
  readonly method: string;
  readonly confidence: number;
}

/** A youth leadership position. `unit_types` are vocabulary CODES from v1/vocab/position-unit-types.json, never display labels. Which RANKS accept a position is not here: it is an edge, and it differs — Bugler counts for Star and Life but not Eagle. Read the rank's requirement-set for that. */
export interface CurrentPosition {
  readonly id: string;
  readonly name: string;
  readonly audience: "youth" | "adult" | "both";
  readonly unit_types: readonly string[];
  readonly verified_at: string;
  readonly method: string;
  readonly confidence: number;
}

/** An adult training course currently offered. `code` is Scouting America's printed course code (Y01, S11, WS10), the stable key; the course name is not. `delivery` and `renew_months` come from the TRAINED LEADER REQUIREMENTS chart. */
export interface CurrentTraining {
  readonly id: string;
  readonly name: string;
  readonly code: string | null;
  readonly delivery: "classroom" | "online" | "both" | "unknown";
  readonly renew_months: number | null;
  readonly verified_at: string;
  readonly method: string;
  readonly confidence: number;
}

/** Root schema for the denormalized, current-only consumer projections emitted by tools/build.py to v1/current/*.json (councils, territories, merit-badges, camps, ranks, awards, oa-lodges, requirement-sets). NOT the canonical layer — flattened, current-only (entities with an open valid_to:null version… */
export interface CurrentCollection {
  readonly $schema?: string;
  readonly version: string;
  readonly generated_at: string;
  readonly kind: "council" | "territory" | "merit-badge" | "camp" | "rank" | "award" | "oa-lodge" | "requirement-set" | "adventure" | "position" | "training";
  readonly count: number;
  readonly items: readonly (Readonly<Record<string, unknown>>)[];
}

export type Slug = string;

export interface CouncilIndexItem {
  readonly id: Slug;
  readonly name: string;
  readonly bsa_number: number | null;
  readonly hq_state: string | null;
  readonly territory: string | null;
  readonly current: boolean;
}

/** The territories listing is categorically mixed — current Council Service Territories, closed National Service Territories, and pre-2021 regions — so `division_type` and `number` are exposed here: a consumer must not infer either by parsing the name or the id. */
export interface TerritoryIndexItem {
  readonly id: Slug;
  readonly name: string;
  readonly number: number | null;
  readonly division_type: "council_service_territory" | "national_service_territory" | "region" | "area";
  readonly current: boolean;
}

export interface MeritBadgeIndexItem {
  readonly id: Slug;
  readonly name: string;
  /** null means UNKNOWN, not false — historical badges retired before the modern published Eagle list cannot be sourced either way. Entities with `current: true` always carry a real boolean. */
  readonly eagle_required: boolean | null;
  readonly current: boolean;
}

export interface CampIndexItem {
  readonly id: Slug;
  readonly name: string;
  readonly camp_type: string;
  readonly operator: string;
  readonly council: string | null;
  readonly state: string | null;
  readonly current: boolean;
}

export interface RankIndexItem {
  readonly id: Slug;
  readonly name: string;
  readonly program: string;
  readonly order: number;
  readonly current: boolean;
}

export interface AwardIndexItem {
  readonly id: Slug;
  readonly name: string;
  readonly category: string;
  readonly audience: string;
  readonly current: boolean;
}

export interface OALodgeIndexItem {
  readonly id: Slug;
  readonly name: string;
  readonly council: string | null;
  readonly section: string | null;
  readonly current: boolean;
}

export type HistoricalDate = string;

/** A requirement-set document is immutable and effective-dated rather than versioned, so it carries effective_from/effective_to instead of a `current` flag; `effective_to: null` means it is the in-force edition for its subject. */
export interface RequirementSetIndexItem {
  readonly id: Slug;
  readonly subject: string;
  readonly effective_from: HistoricalDate;
  readonly effective_to: HistoricalDate | null;
  readonly includes_official_text: boolean;
}

export interface AdventureIndexItem {
  readonly id: Slug;
  readonly name: string;
  readonly program: string;
  /** Vocabulary CODE from v1/vocab/adventure-categories.json, never a display label. */
  readonly category: string;
  readonly current: boolean;
}

/** One year of merit badge popularity ranks. `metric` is carried here too so a listing cannot be mistaken for earned counts. */
export interface BadgeRankingIndexItem {
  readonly id: string;
  readonly year: number;
  readonly metric: "earned_rank";
  readonly complete: boolean;
  readonly count: number;
}

export interface PositionIndexItem {
  readonly id: Slug;
  readonly name: string;
  readonly audience: "youth" | "adult" | "both";
  readonly current: boolean;
}

export interface TrainingIndexItem {
  readonly id: Slug;
  readonly name: string;
  readonly code: string | null;
  readonly current: boolean;
}

/** One row of the TRAINED LEADER REQUIREMENTS chart, keyed by (position, unit_type). `registration_codes` is the join key a consumer holds from my.scouting; the position name is not stable enough to match on. */
export interface TrainingRequirementIndexItem {
  readonly id: Slug;
  readonly position_name: string;
  readonly registration_codes: readonly string[];
  readonly unit_type: "pack" | "troop" | "team" | "crew" | "ship" | "other";
}

/** Root schema for the lightweight listing projections emitted by tools/build.py to v1/{dataset}/index.json (councils, territories, merit-badges, camps, ranks, awards, oa-lodges, requirement-sets). One entry per entity INCLUDING retired/defunct ones — a `current` boolean says whether the entity has an… */
export interface IndexCollection {
  readonly $schema?: string;
  readonly version: string;
  readonly generated_at: string;
  readonly kind: "council" | "territory" | "merit-badge" | "camp" | "rank" | "award" | "oa-lodge" | "requirement-set" | "adventure" | "merit-badge-ranking" | "position" | "training" | "training-requirement";
  readonly count: number;
  readonly items: readonly (Readonly<Record<string, unknown>>)[];
}

/** One attribute snapshot. Half-open window: `valid_from` null means 'from the beginning of what we know', `valid_to` null means current. Exactly one version per entity may have valid_to null (enforced by tools/validate_data.py). Attribute fields beyond these are dataset-specific and validated against… */
export interface Version {
  readonly valid_from: HistoricalDate | null;
  readonly valid_to: HistoricalDate | null;
  readonly provenance: Readonly<Record<string, unknown>>;
  readonly [extra: string]: unknown;
}

export type EntityRef = string;

export interface EventParticipantsItem {
  readonly ref: EntityRef;
  readonly role: string;
}

/** A lifecycle event PROJECTED onto this entity from the dataset's _events.json. Stored once there, copied here for convenience: an entity carries every event it participates in, whichever role it plays. */
export interface Event {
  readonly id: Slug;
  readonly type: "established" | "renamed" | "merged" | "split" | "absorbed" | "transferred" | "reorganized" | "discontinued" | "reinstated" | "superseded";
  readonly date: HistoricalDate | null;
  readonly participants: readonly EventParticipantsItem[];
  readonly notes?: string | null;
  readonly provenance: Readonly<Record<string, unknown>>;
}

export interface VersionedEntity {
  readonly $schema: string;
  readonly id: Slug;
  readonly kind: string;
  readonly notes: string | null;
  readonly versions: readonly Version[];
  readonly events: readonly Event[];
  readonly [extra: string]: unknown;
}

export interface VersionedEntityWithRequirementSets {
  readonly $schema: string;
  readonly id: Slug;
  readonly kind: string;
  readonly notes: string | null;
  readonly versions: readonly Version[];
  readonly events: readonly Event[];
  /** Ids of every requirement-set edition whose `subject` is this entity, oldest and newest alike - not just the one in force. Fetch v1/requirement-sets/{id}.json for the tree, or read the effective windows and `supersedes` chain to pick the edition that applied on a given date. */
  readonly requirement_sets: readonly Slug[];
  readonly [extra: string]: unknown;
}

export interface RequirementSetDocumentSourceDocument {
  readonly title: string;
  readonly [extra: string]: unknown;
}

/** An effective-dated requirement document (merit badge or rank edition). Not a versioned entity: editions are immutable and chained by `supersedes`, so there are no `versions` and no `events`. */
export interface RequirementSetDocument {
  readonly $schema: string;
  readonly id: Slug;
  readonly kind: string;
  readonly subject: EntityRef;
  readonly effective_from: HistoricalDate;
  readonly effective_to: HistoricalDate | null;
  readonly supersedes: string | null;
  readonly source_document: RequirementSetDocumentSourceDocument;
  readonly includes_official_text: boolean;
  readonly text_rights?: string | null;
  readonly requirements: readonly unknown[];
  readonly notes?: string | null;
  readonly provenance: Readonly<Record<string, unknown>>;
  readonly [extra: string]: unknown;
}

/** One row of the TRAINED LEADER REQUIREMENTS chart: what an adult in this position, in this unit type, must complete to be Position Trained. Not a versioned entity - the chart is a single edition and the row has no identity apart from it. `registration_codes` is the join key a consumer already holds… */
export interface TrainingRequirementDocument {
  readonly position_name: string;
  readonly registration_codes: readonly string[];
  readonly unit_type: "pack" | "troop" | "team" | "crew" | "ship" | "other";
  readonly requires: readonly unknown[];
  readonly provenance: Readonly<Record<string, unknown>>;
  readonly [extra: string]: unknown;
}

export interface BadgeRankingDocumentRankingsItem {
  readonly rank: number;
  readonly subject: string;
}

/** One year of merit badge popularity ranks. Like a requirement-set it is a dated document, not a versioned entity, so it carries neither `versions` nor `events`. `metric` is pinned because the numbers are RANKS, not counts, and a consumer that mistook one for the other would draw volume conclusions t… */
export interface BadgeRankingDocument {
  readonly year: number;
  readonly metric: "earned_rank";
  readonly complete: boolean;
  readonly rankings: readonly BadgeRankingDocumentRankingsItem[];
  readonly [extra: string]: unknown;
}

/** Contract for the per-entity endpoints emitted by tools/build.py to v1/{dataset}/{id}.json. These are the DEEP surface: the canonical entity plus everything the build projects onto it, and for camps they are the only place the prose `note` on a program feature appears. Scope is deliberate: this sche… */
export interface EntityDocument {
  readonly $schema: string;
  readonly id: Slug;
  readonly kind: "council" | "territory" | "merit-badge" | "camp" | "rank" | "award" | "oa-lodge" | "requirement-set" | "adventure" | "merit-badge-ranking" | "position" | "training" | "training-requirement";
  readonly [extra: string]: unknown;
}

/** Contract for v1/meta.json, the entry point a consumer reads first: what this dataset is, which release it is, where the schemas live, what every endpoint is called, and the licensing split. Pinning it matters more than its size suggests - `endpoints` and `vocab` are the machine-readable index of th… */
export interface Meta {
  readonly $schema: string;
  readonly name: string;
  /** The release this tree was built from; '+unreleased' marks a build ahead of the newest CHANGELOG entry. */
  readonly version: string;
  readonly generated_at: string;
  readonly base_url: string;
  /** Covers the dataset EXCEPT the official requirement text described by `text_rights`. */
  readonly license: string;
  /** Always true, and deliberately not optional: this is a community project with no Scouting America affiliation, and a consumer must not be able to lose that by reading a subset of the document. */
  readonly unofficial: true;
  readonly disclaimer: string;
  readonly schemas: string;
  readonly text_rights: string;
  /** Per-dataset counts. `total` spans every entity including historical ones; `current` counts those with an open version. Extra per-dataset keys (e.g. camps' `merged`) may appear. */
  readonly datasets: Readonly<Record<string, unknown>>;
  readonly vocab: readonly string[];
  readonly endpoints: readonly string[];
  readonly [extra: string]: unknown;
}

/** Item shape selected by the envelope `kind` of a CurrentCollection. */
export interface CurrentByKind {
  readonly "adventure": CurrentAdventure;
  readonly "award": CurrentAward;
  readonly "camp": CurrentCamp;
  readonly "council": CurrentCouncil;
  readonly "merit-badge": CurrentMeritBadge;
  readonly "oa-lodge": CurrentOALodge;
  readonly "position": CurrentPosition;
  readonly "rank": CurrentRank;
  readonly "requirement-set": CurrentRequirementSet;
  readonly "territory": CurrentTerritory;
  readonly "training": CurrentTraining;
}

/** Item shape selected by the envelope `kind` of a IndexCollection. */
export interface IndexByKind {
  readonly "adventure": AdventureIndexItem;
  readonly "award": AwardIndexItem;
  readonly "camp": CampIndexItem;
  readonly "council": CouncilIndexItem;
  readonly "merit-badge": MeritBadgeIndexItem;
  readonly "merit-badge-ranking": BadgeRankingIndexItem;
  readonly "oa-lodge": OALodgeIndexItem;
  readonly "position": PositionIndexItem;
  readonly "rank": RankIndexItem;
  readonly "requirement-set": RequirementSetIndexItem;
  readonly "territory": TerritoryIndexItem;
  readonly "training": TrainingIndexItem;
  readonly "training-requirement": TrainingRequirementIndexItem;
}

/** Item shape selected by the envelope `kind` of a EntityDocument. */
export interface EntityDocumentByKind {
  readonly "adventure": VersionedEntityWithRequirementSets;
  readonly "award": VersionedEntityWithRequirementSets;
  readonly "camp": VersionedEntity;
  readonly "council": VersionedEntity;
  readonly "merit-badge": VersionedEntityWithRequirementSets;
  readonly "merit-badge-ranking": BadgeRankingDocument;
  readonly "oa-lodge": VersionedEntity;
  readonly "position": VersionedEntity;
  readonly "rank": VersionedEntityWithRequirementSets;
  readonly "requirement-set": RequirementSetDocument;
  readonly "territory": VersionedEntity;
  readonly "training": VersionedEntity;
  readonly "training-requirement": TrainingRequirementDocument;
}

/**
 * The bare `{retired-id: surviving-id}` map published at v1/{dataset}/aliases.json.
 * Deliberately unenveloped and carrying no `$schema`: its only sane use is a direct
 * lookup, and a `$schema` key in a bare map would read as an alias.
 */
export type AliasMap = Readonly<Record<string, string>>;
