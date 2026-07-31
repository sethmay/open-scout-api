// GENERATED FILE -- DO NOT EDIT.
// Regenerate with `python tools/gen_types.py`; CI fails on drift (`--check`).
// Source of truth: schema/v1/published-*.schema.json

// The bare `{retired-id: surviving-id}` map published at v1/{dataset}/aliases.json. Deliberately unenveloped and carrying no `$schema`: its only sane use is a direct lookup, and a `$schema` key in a bare map would read as an alias.
global using AliasMap = System.Collections.Generic.IReadOnlyDictionary<string, string>;

using System.Text.Json;
using System.Text.Json.Serialization;

namespace OpenScoutApi.Generated;

/// <summary>Item record name selected by the envelope kind of a CurrentCollection.</summary>
public static class CurrentByKind
{
    public static readonly IReadOnlyDictionary<string, string> Map =
        new Dictionary<string, string> { ["adventure"] = "CurrentAdventure", ["award"] = "CurrentAward", ["camp"] = "CurrentCamp", ["council"] = "CurrentCouncil", ["merit-badge"] = "CurrentMeritBadge", ["oa-lodge"] = "CurrentOALodge", ["position"] = "CurrentPosition", ["rank"] = "CurrentRank", ["requirement-set"] = "CurrentRequirementSet", ["territory"] = "CurrentTerritory", ["training"] = "CurrentTraining" };
}

/// <summary>Item record name selected by the envelope kind of a IndexCollection.</summary>
public static class IndexByKind
{
    public static readonly IReadOnlyDictionary<string, string> Map =
        new Dictionary<string, string> { ["adventure"] = "AdventureIndexItem", ["award"] = "AwardIndexItem", ["camp"] = "CampIndexItem", ["council"] = "CouncilIndexItem", ["merit-badge"] = "MeritBadgeIndexItem", ["merit-badge-ranking"] = "BadgeRankingIndexItem", ["oa-lodge"] = "OALodgeIndexItem", ["position"] = "PositionIndexItem", ["rank"] = "RankIndexItem", ["requirement-set"] = "RequirementSetIndexItem", ["territory"] = "TerritoryIndexItem", ["training"] = "TrainingIndexItem", ["training-requirement"] = "TrainingRequirementIndexItem" };
}

/// <summary>Item record name selected by the envelope kind of a EntityDocument.</summary>
public static class EntityDocumentByKind
{
    public static readonly IReadOnlyDictionary<string, string> Map =
        new Dictionary<string, string> { ["adventure"] = "VersionedEntityWithRequirementSets", ["award"] = "VersionedEntityWithRequirementSets", ["camp"] = "VersionedEntity", ["council"] = "VersionedEntity", ["merit-badge"] = "VersionedEntityWithRequirementSets", ["merit-badge-ranking"] = "BadgeRankingDocument", ["oa-lodge"] = "VersionedEntity", ["position"] = "VersionedEntity", ["rank"] = "VersionedEntityWithRequirementSets", ["requirement-set"] = "RequirementSetDocument", ["territory"] = "VersionedEntity", ["training"] = "VersionedEntity", ["training-requirement"] = "TrainingRequirementDocument" };
}

public sealed record CurrentCouncil
{
    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("name")]
    public required string Name { get; init; }

    [JsonPropertyName("bsa_number")]
    public required int? BsaNumber { get; init; }

    [JsonPropertyName("hq_city")]
    public required string? HqCity { get; init; }

    [JsonPropertyName("hq_state")]
    public required string? HqState { get; init; }

    [JsonPropertyName("website")]
    public required string? Website { get; init; }

    [JsonPropertyName("territory")]
    public required string? Territory { get; init; }

    [JsonPropertyName("territory_number")]
    public required int? TerritoryNumber { get; init; }

    [JsonPropertyName("verified_at")]
    public required string VerifiedAt { get; init; }

    [JsonPropertyName("method")]
    public required string Method { get; init; }

    [JsonPropertyName("confidence")]
    public required double Confidence { get; init; }
}

public sealed record CurrentTerritory
{
    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("number")]
    public required int? Number { get; init; }

    [JsonPropertyName("name")]
    public required string Name { get; init; }

    [JsonPropertyName("division_type")]
    public required string DivisionType { get; init; }

    [JsonPropertyName("verified_at")]
    public required string VerifiedAt { get; init; }

    [JsonPropertyName("method")]
    public required string Method { get; init; }

    [JsonPropertyName("confidence")]
    public required double Confidence { get; init; }
}

public sealed record CurrentMeritBadge
{
    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("name")]
    public required string Name { get; init; }

    /// <summary>Short original-prose summary of what a Scout does to earn the badge, written for browsing. Deliberately NOT the pamphlet or requirement wording: requirement text is © Scouting America and is published only under the `text_rights` carve-out on requirement-sets, so this field is original and CC-licen…</summary>
    [JsonPropertyName("description")]
    public required string? Description { get; init; }

    [JsonPropertyName("tags")]
    public required IReadOnlyList<string> Tags { get; init; }

    [JsonPropertyName("eagle_required")]
    public required bool EagleRequired { get; init; }

    [JsonPropertyName("url")]
    public required string? Url { get; init; }

    [JsonPropertyName("verified_at")]
    public required string VerifiedAt { get; init; }

    [JsonPropertyName("method")]
    public required string Method { get; init; }

    [JsonPropertyName("confidence")]
    public required double Confidence { get; init; }
}

/// <summary>Set when this camp shares a location with other distinct camps: a grouping so consumers render one reservation pin per property. `id` is a STABLE OPAQUE GROUPING KEY — deliberately a bare slug, NOT a '{kind}:{slug}' entity reference, because no reservation entity exists. If a reservation dataset is…</summary>
public sealed record CurrentCampReservation
{
    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("name")]
    public string? Name { get; init; }
}

public sealed record CurrentCamp
{
    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("name")]
    public required string Name { get; init; }

    [JsonPropertyName("camp_type")]
    public required string CampType { get; init; }

    [JsonPropertyName("operator")]
    public required string Operator { get; init; }

    [JsonPropertyName("council")]
    public required string? Council { get; init; }

    [JsonPropertyName("parent")]
    public required string? Parent { get; init; }

    [JsonPropertyName("state")]
    public required string? State { get; init; }

    [JsonPropertyName("city")]
    public required string? City { get; init; }

    [JsonPropertyName("lat")]
    public required double? Lat { get; init; }

    [JsonPropertyName("lon")]
    public required double? Lon { get; init; }

    [JsonPropertyName("geo_precision")]
    public required string? GeoPrecision { get; init; }

    [JsonPropertyName("elevation_ft")]
    public int? ElevationFt { get; init; }

    [JsonPropertyName("july_high_f")]
    public int? JulyHighF { get; init; }

    [JsonPropertyName("july_low_f")]
    public int? JulyLowF { get; init; }

    /// <summary>Set when this camp shares a location with other distinct camps: a grouping so consumers render one reservation pin per property. `id` is a STABLE OPAQUE GROUPING KEY — deliberately a bare slug, NOT a '{kind}:{slug}' entity reference, because no reservation entity exists. If a reservation dataset is…</summary>
    [JsonPropertyName("reservation")]
    public required CurrentCampReservation? Reservation { get; init; }

    [JsonPropertyName("website")]
    public required string? Website { get; init; }

    [JsonPropertyName("program_types")]
    public required IReadOnlyList<string> ProgramTypes { get; init; }

    [JsonPropertyName("summary")]
    public required string? Summary { get; init; }

    /// <summary>What this camp offers, as codes from the open `camp-features` vocabulary published at v1/vocab/camp-features.json. Sorted, unique, and flattened for filtering: the canonical per-camp document (v1/camps/{id}.json) carries the same features as objects with an optional prose `note`, which is deliberat…</summary>
    [JsonPropertyName("features")]
    public required IReadOnlyList<string> Features { get; init; }

    /// <summary>The subset of `features` a camp presents as a headline draw rather than table stakes — the same feature can be signature at one camp and unremarkable at another (a climbing tower is ordinary in Colorado and a real differentiator on the prairie). Intended for ranking and badge rendering in list view…</summary>
    [JsonPropertyName("features_signature")]
    public required IReadOnlyList<string> FeaturesSignature { get; init; }

    /// <summary>How complete the source behind `features` was, in the same spirit as `geo_precision` for coordinates. `guide`: a camp-specific document was read (leader's/program guide, schedule, or labelled map) — averages 21 features per camp. `camp_page`: a descriptive page owned by the camp or council — averag…</summary>
    [JsonPropertyName("features_source_tier")]
    public required string? FeaturesSourceTier { get; init; }

    /// <summary>Date of the last deliberate features survey of this camp against its own sources. Four states, and the distinction matters: `null` + empty `features` = never surveyed, nothing is known; `null` + non-empty = features arrived from a bulk import and were never deliberately verified; a date + non-empty…</summary>
    [JsonPropertyName("features_verified_at")]
    public required string? FeaturesVerifiedAt { get; init; }

    [JsonPropertyName("council_name")]
    public required string? CouncilName { get; init; }

    [JsonPropertyName("council_website")]
    public required string? CouncilWebsite { get; init; }

    [JsonPropertyName("council_number")]
    public required int? CouncilNumber { get; init; }

    [JsonPropertyName("url")]
    public required string? Url { get; init; }

    [JsonPropertyName("operating_status")]
    public required string OperatingStatus { get; init; }

    [JsonPropertyName("verified_at")]
    public required string VerifiedAt { get; init; }

    [JsonPropertyName("imported_at")]
    public required string ImportedAt { get; init; }

    [JsonPropertyName("method")]
    public required string Method { get; init; }

    [JsonPropertyName("confidence")]
    public required double Confidence { get; init; }
}

public sealed record CurrentRank
{
    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("name")]
    public required string Name { get; init; }

    [JsonPropertyName("program")]
    public required string Program { get; init; }

    [JsonPropertyName("order")]
    public required int Order { get; init; }

    [JsonPropertyName("url")]
    public required string? Url { get; init; }

    [JsonPropertyName("verified_at")]
    public required string VerifiedAt { get; init; }

    [JsonPropertyName("method")]
    public required string Method { get; init; }

    [JsonPropertyName("confidence")]
    public required double Confidence { get; init; }
}

public sealed record CurrentAward
{
    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("name")]
    public required string Name { get; init; }

    [JsonPropertyName("category")]
    public required string Category { get; init; }

    [JsonPropertyName("audience")]
    public required string Audience { get; init; }

    [JsonPropertyName("programs")]
    public IReadOnlyList<string>? Programs { get; init; }

    [JsonPropertyName("square_knot_no")]
    public required string? SquareKnotNo { get; init; }

    [JsonPropertyName("url")]
    public string? Url { get; init; }

    [JsonPropertyName("verified_at")]
    public required string VerifiedAt { get; init; }

    [JsonPropertyName("method")]
    public required string Method { get; init; }

    [JsonPropertyName("confidence")]
    public required double Confidence { get; init; }
}

public sealed record CurrentOALodge
{
    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("name")]
    public required string Name { get; init; }

    [JsonPropertyName("council")]
    public required string? Council { get; init; }

    [JsonPropertyName("section")]
    public required string? Section { get; init; }

    [JsonPropertyName("hq_state")]
    public string? HqState { get; init; }

    [JsonPropertyName("lat")]
    public double? Lat { get; init; }

    [JsonPropertyName("lon")]
    public double? Lon { get; init; }

    [JsonPropertyName("verified_at")]
    public required string VerifiedAt { get; init; }

    [JsonPropertyName("method")]
    public required string Method { get; init; }

    [JsonPropertyName("confidence")]
    public required double Confidence { get; init; }
}

/// <summary>The in-force requirement-set document for a subject (rank or merit badge): effective_to is null. A requirement-set is immutable and effective-dated rather than versioned, so it has no `current` flag. Requirement CONTENT lives in the per-document file v1/requirement-sets/{id}.json — this projection…</summary>
public sealed record CurrentRequirementSet
{
    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("subject")]
    public required string Subject { get; init; }

    [JsonPropertyName("effective_from")]
    public required string EffectiveFrom { get; init; }

    [JsonPropertyName("includes_official_text")]
    public required bool IncludesOfficialText { get; init; }

    [JsonPropertyName("verified_at")]
    public required string VerifiedAt { get; init; }

    [JsonPropertyName("method")]
    public required string Method { get; init; }

    [JsonPropertyName("confidence")]
    public required double Confidence { get; init; }
}

/// <summary>A Cub Scout adventure currently offered. `ranks` is the reverse index of the rank requirement-sets, which remain authoritative for grouping and choose-counts. The shooting-sports adventures carry a null `url` and have no requirement-set; join v1/requirement-sets/index.json on subject 'adventure:&lt;id…</summary>
public sealed record CurrentAdventure
{
    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("name")]
    public required string Name { get; init; }

    [JsonPropertyName("program")]
    public required string Program { get; init; }

    [JsonPropertyName("ranks")]
    public required IReadOnlyList<string> Ranks { get; init; }

    /// <summary>Vocabulary CODE from v1/vocab/adventure-categories.json, never a display label.</summary>
    [JsonPropertyName("category")]
    public required string Category { get; init; }

    /// <summary>The requirement area this adventure fills for its rank, or null for electives. Every rank's six required adventures cover the six areas of v1/vocab/adventure-areas.json exactly once each. A vocabulary CODE, never a display label — two Arrow of Light adventures are *named* after areas, so publishing…</summary>
    [JsonPropertyName("area")]
    public required string? Area { get; init; }

    [JsonPropertyName("url")]
    public required string? Url { get; init; }

    [JsonPropertyName("verified_at")]
    public required string VerifiedAt { get; init; }

    [JsonPropertyName("method")]
    public required string Method { get; init; }

    [JsonPropertyName("confidence")]
    public required double Confidence { get; init; }
}

/// <summary>A youth leadership position. `unit_types` are vocabulary CODES from v1/vocab/position-unit-types.json, never display labels. Which RANKS accept a position is not here: it is an edge, and it differs — Bugler counts for Star and Life but not Eagle. Read the rank's requirement-set for that.</summary>
public sealed record CurrentPosition
{
    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("name")]
    public required string Name { get; init; }

    [JsonPropertyName("audience")]
    public required string Audience { get; init; }

    [JsonPropertyName("unit_types")]
    public required IReadOnlyList<string> UnitTypes { get; init; }

    [JsonPropertyName("verified_at")]
    public required string VerifiedAt { get; init; }

    [JsonPropertyName("method")]
    public required string Method { get; init; }

    [JsonPropertyName("confidence")]
    public required double Confidence { get; init; }
}

/// <summary>An adult training course currently offered. `code` is Scouting America's printed course code (Y01, S11, WS10), the stable key; the course name is not. `delivery` and `renew_months` come from the TRAINED LEADER REQUIREMENTS chart.</summary>
public sealed record CurrentTraining
{
    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("name")]
    public required string Name { get; init; }

    [JsonPropertyName("code")]
    public required string? Code { get; init; }

    [JsonPropertyName("delivery")]
    public required string Delivery { get; init; }

    [JsonPropertyName("renew_months")]
    public required int? RenewMonths { get; init; }

    [JsonPropertyName("verified_at")]
    public required string VerifiedAt { get; init; }

    [JsonPropertyName("method")]
    public required string Method { get; init; }

    [JsonPropertyName("confidence")]
    public required double Confidence { get; init; }
}

/// <summary>Root schema for the denormalized, current-only consumer projections emitted by tools/build.py to v1/current/*.json (councils, territories, merit-badges, camps, ranks, awards, oa-lodges, requirement-sets). NOT the canonical layer — flattened, current-only (entities with an open valid_to:null version…</summary>
public sealed record CurrentCollection
{
    [JsonPropertyName("$schema")]
    public string? Schema { get; init; }

    [JsonPropertyName("version")]
    public required string Version { get; init; }

    [JsonPropertyName("generated_at")]
    public required string GeneratedAt { get; init; }

    [JsonPropertyName("kind")]
    public required string Kind { get; init; }

    [JsonPropertyName("count")]
    public required int Count { get; init; }

    [JsonPropertyName("items")]
    public required IReadOnlyList<IReadOnlyDictionary<string, JsonElement>> Items { get; init; }
}

public sealed record CouncilIndexItem
{
    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("name")]
    public required string Name { get; init; }

    [JsonPropertyName("bsa_number")]
    public required int? BsaNumber { get; init; }

    [JsonPropertyName("hq_state")]
    public required string? HqState { get; init; }

    [JsonPropertyName("territory")]
    public required string? Territory { get; init; }

    [JsonPropertyName("current")]
    public required bool Current { get; init; }
}

/// <summary>The territories listing is categorically mixed — current Council Service Territories, closed National Service Territories, and pre-2021 regions — so `division_type` and `number` are exposed here: a consumer must not infer either by parsing the name or the id.</summary>
public sealed record TerritoryIndexItem
{
    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("name")]
    public required string Name { get; init; }

    [JsonPropertyName("number")]
    public required int? Number { get; init; }

    [JsonPropertyName("division_type")]
    public required string DivisionType { get; init; }

    [JsonPropertyName("current")]
    public required bool Current { get; init; }
}

public sealed record MeritBadgeIndexItem
{
    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("name")]
    public required string Name { get; init; }

    /// <summary>null means UNKNOWN, not false — historical badges retired before the modern published Eagle list cannot be sourced either way. Entities with `current: true` always carry a real boolean.</summary>
    [JsonPropertyName("eagle_required")]
    public required bool? EagleRequired { get; init; }

    [JsonPropertyName("current")]
    public required bool Current { get; init; }
}

public sealed record CampIndexItem
{
    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("name")]
    public required string Name { get; init; }

    [JsonPropertyName("camp_type")]
    public required string CampType { get; init; }

    [JsonPropertyName("operator")]
    public required string Operator { get; init; }

    [JsonPropertyName("council")]
    public required string? Council { get; init; }

    [JsonPropertyName("state")]
    public required string? State { get; init; }

    [JsonPropertyName("current")]
    public required bool Current { get; init; }
}

public sealed record RankIndexItem
{
    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("name")]
    public required string Name { get; init; }

    [JsonPropertyName("program")]
    public required string Program { get; init; }

    [JsonPropertyName("order")]
    public required int Order { get; init; }

    [JsonPropertyName("current")]
    public required bool Current { get; init; }
}

public sealed record AwardIndexItem
{
    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("name")]
    public required string Name { get; init; }

    [JsonPropertyName("category")]
    public required string Category { get; init; }

    [JsonPropertyName("audience")]
    public required string Audience { get; init; }

    [JsonPropertyName("current")]
    public required bool Current { get; init; }
}

public sealed record OALodgeIndexItem
{
    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("name")]
    public required string Name { get; init; }

    [JsonPropertyName("council")]
    public required string? Council { get; init; }

    [JsonPropertyName("section")]
    public required string? Section { get; init; }

    [JsonPropertyName("current")]
    public required bool Current { get; init; }
}

/// <summary>A requirement-set document is immutable and effective-dated rather than versioned, so it carries effective_from/effective_to instead of a `current` flag; `effective_to: null` means it is the in-force edition for its subject.</summary>
public sealed record RequirementSetIndexItem
{
    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("subject")]
    public required string Subject { get; init; }

    [JsonPropertyName("effective_from")]
    public required string EffectiveFrom { get; init; }

    [JsonPropertyName("effective_to")]
    public required string? EffectiveTo { get; init; }

    [JsonPropertyName("includes_official_text")]
    public required bool IncludesOfficialText { get; init; }
}

public sealed record AdventureIndexItem
{
    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("name")]
    public required string Name { get; init; }

    [JsonPropertyName("program")]
    public required string Program { get; init; }

    /// <summary>Vocabulary CODE from v1/vocab/adventure-categories.json, never a display label.</summary>
    [JsonPropertyName("category")]
    public required string Category { get; init; }

    [JsonPropertyName("current")]
    public required bool Current { get; init; }
}

/// <summary>One year of merit badge popularity ranks. `metric` is carried here too so a listing cannot be mistaken for earned counts.</summary>
public sealed record BadgeRankingIndexItem
{
    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("year")]
    public required int Year { get; init; }

    [JsonPropertyName("metric")]
    public required string Metric { get; init; }

    [JsonPropertyName("complete")]
    public required bool Complete { get; init; }

    [JsonPropertyName("count")]
    public required int Count { get; init; }
}

public sealed record PositionIndexItem
{
    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("name")]
    public required string Name { get; init; }

    [JsonPropertyName("audience")]
    public required string Audience { get; init; }

    [JsonPropertyName("current")]
    public required bool Current { get; init; }
}

public sealed record TrainingIndexItem
{
    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("name")]
    public required string Name { get; init; }

    [JsonPropertyName("code")]
    public required string? Code { get; init; }

    [JsonPropertyName("current")]
    public required bool Current { get; init; }
}

/// <summary>One row of the TRAINED LEADER REQUIREMENTS chart, keyed by (position, unit_type). `registration_codes` is the join key a consumer holds from my.scouting; the position name is not stable enough to match on.</summary>
public sealed record TrainingRequirementIndexItem
{
    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("position_name")]
    public required string PositionName { get; init; }

    [JsonPropertyName("registration_codes")]
    public required IReadOnlyList<string> RegistrationCodes { get; init; }

    [JsonPropertyName("unit_type")]
    public required string UnitType { get; init; }
}

/// <summary>Root schema for the lightweight listing projections emitted by tools/build.py to v1/{dataset}/index.json (councils, territories, merit-badges, camps, ranks, awards, oa-lodges, requirement-sets). One entry per entity INCLUDING retired/defunct ones — a `current` boolean says whether the entity has an…</summary>
public sealed record IndexCollection
{
    [JsonPropertyName("$schema")]
    public string? Schema { get; init; }

    [JsonPropertyName("version")]
    public required string Version { get; init; }

    [JsonPropertyName("generated_at")]
    public required string GeneratedAt { get; init; }

    [JsonPropertyName("kind")]
    public required string Kind { get; init; }

    [JsonPropertyName("count")]
    public required int Count { get; init; }

    [JsonPropertyName("items")]
    public required IReadOnlyList<IReadOnlyDictionary<string, JsonElement>> Items { get; init; }
}

/// <summary>One attribute snapshot. Half-open window: `valid_from` null means 'from the beginning of what we know', `valid_to` null means current. Exactly one version per entity may have valid_to null (enforced by tools/validate_data.py). Attribute fields beyond these are dataset-specific and validated against…</summary>
public sealed record Version
{
    [JsonPropertyName("valid_from")]
    public required string? ValidFrom { get; init; }

    [JsonPropertyName("valid_to")]
    public required string? ValidTo { get; init; }

    [JsonPropertyName("provenance")]
    public required IReadOnlyDictionary<string, JsonElement> Provenance { get; init; }
}

public sealed record EventParticipantsItem
{
    [JsonPropertyName("ref")]
    public required string Ref { get; init; }

    [JsonPropertyName("role")]
    public required string Role { get; init; }
}

/// <summary>A lifecycle event PROJECTED onto this entity from the dataset's _events.json. Stored once there, copied here for convenience: an entity carries every event it participates in, whichever role it plays.</summary>
public sealed record Event
{
    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("type")]
    public required string Type { get; init; }

    [JsonPropertyName("date")]
    public required string? Date { get; init; }

    [JsonPropertyName("participants")]
    public required IReadOnlyList<EventParticipantsItem> Participants { get; init; }

    [JsonPropertyName("notes")]
    public string? Notes { get; init; }

    [JsonPropertyName("provenance")]
    public required IReadOnlyDictionary<string, JsonElement> Provenance { get; init; }
}

public sealed record VersionedEntity
{
    [JsonPropertyName("$schema")]
    public required string Schema { get; init; }

    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("kind")]
    public required string Kind { get; init; }

    [JsonPropertyName("notes")]
    public required string? Notes { get; init; }

    [JsonPropertyName("versions")]
    public required IReadOnlyList<Version> Versions { get; init; }

    [JsonPropertyName("events")]
    public required IReadOnlyList<Event> Events { get; init; }
}

public sealed record VersionedEntityWithRequirementSets
{
    [JsonPropertyName("$schema")]
    public required string Schema { get; init; }

    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("kind")]
    public required string Kind { get; init; }

    [JsonPropertyName("notes")]
    public required string? Notes { get; init; }

    [JsonPropertyName("versions")]
    public required IReadOnlyList<Version> Versions { get; init; }

    [JsonPropertyName("events")]
    public required IReadOnlyList<Event> Events { get; init; }

    /// <summary>Ids of every requirement-set edition whose `subject` is this entity, oldest and newest alike - not just the one in force. Fetch v1/requirement-sets/{id}.json for the tree, or read the effective windows and `supersedes` chain to pick the edition that applied on a given date.</summary>
    [JsonPropertyName("requirement_sets")]
    public required IReadOnlyList<string> RequirementSets { get; init; }
}

public sealed record RequirementSetDocumentSourceDocument
{
    [JsonPropertyName("title")]
    public required string Title { get; init; }
}

/// <summary>An effective-dated requirement document (merit badge or rank edition). Not a versioned entity: editions are immutable and chained by `supersedes`, so there are no `versions` and no `events`.</summary>
public sealed record RequirementSetDocument
{
    [JsonPropertyName("$schema")]
    public required string Schema { get; init; }

    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("kind")]
    public required string Kind { get; init; }

    [JsonPropertyName("subject")]
    public required string Subject { get; init; }

    [JsonPropertyName("effective_from")]
    public required string EffectiveFrom { get; init; }

    [JsonPropertyName("effective_to")]
    public required string? EffectiveTo { get; init; }

    [JsonPropertyName("supersedes")]
    public required string? Supersedes { get; init; }

    [JsonPropertyName("source_document")]
    public required RequirementSetDocumentSourceDocument SourceDocument { get; init; }

    [JsonPropertyName("includes_official_text")]
    public required bool IncludesOfficialText { get; init; }

    [JsonPropertyName("text_rights")]
    public string? TextRights { get; init; }

    [JsonPropertyName("requirements")]
    public required IReadOnlyList<JsonElement> Requirements { get; init; }

    [JsonPropertyName("notes")]
    public string? Notes { get; init; }

    [JsonPropertyName("provenance")]
    public required IReadOnlyDictionary<string, JsonElement> Provenance { get; init; }
}

/// <summary>One row of the TRAINED LEADER REQUIREMENTS chart: what an adult in this position, in this unit type, must complete to be Position Trained. Not a versioned entity - the chart is a single edition and the row has no identity apart from it. `registration_codes` is the join key a consumer already holds…</summary>
public sealed record TrainingRequirementDocument
{
    [JsonPropertyName("position_name")]
    public required string PositionName { get; init; }

    [JsonPropertyName("registration_codes")]
    public required IReadOnlyList<string> RegistrationCodes { get; init; }

    [JsonPropertyName("unit_type")]
    public required string UnitType { get; init; }

    [JsonPropertyName("requires")]
    public required IReadOnlyList<JsonElement> Requires { get; init; }

    [JsonPropertyName("provenance")]
    public required IReadOnlyDictionary<string, JsonElement> Provenance { get; init; }
}

public sealed record BadgeRankingDocumentRankingsItem
{
    [JsonPropertyName("rank")]
    public required int Rank { get; init; }

    [JsonPropertyName("subject")]
    public required string Subject { get; init; }
}

/// <summary>One year of merit badge popularity ranks. Like a requirement-set it is a dated document, not a versioned entity, so it carries neither `versions` nor `events`. `metric` is pinned because the numbers are RANKS, not counts, and a consumer that mistook one for the other would draw volume conclusions t…</summary>
public sealed record BadgeRankingDocument
{
    [JsonPropertyName("year")]
    public required int Year { get; init; }

    [JsonPropertyName("metric")]
    public required string Metric { get; init; }

    [JsonPropertyName("complete")]
    public required bool Complete { get; init; }

    [JsonPropertyName("rankings")]
    public required IReadOnlyList<BadgeRankingDocumentRankingsItem> Rankings { get; init; }
}

/// <summary>Contract for the per-entity endpoints emitted by tools/build.py to v1/{dataset}/{id}.json. These are the DEEP surface: the canonical entity plus everything the build projects onto it, and for camps they are the only place the prose `note` on a program feature appears. Scope is deliberate: this sche…</summary>
public sealed record EntityDocument
{
    [JsonPropertyName("$schema")]
    public required string Schema { get; init; }

    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("kind")]
    public required string Kind { get; init; }
}

/// <summary>Contract for v1/meta.json, the entry point a consumer reads first: what this dataset is, which release it is, where the schemas live, what every endpoint is called, and the licensing split. Pinning it matters more than its size suggests - `endpoints` and `vocab` are the machine-readable index of th…</summary>
public sealed record Meta
{
    [JsonPropertyName("$schema")]
    public required string Schema { get; init; }

    [JsonPropertyName("name")]
    public required string Name { get; init; }

    /// <summary>The release this tree was built from; '+unreleased' marks a build ahead of the newest CHANGELOG entry.</summary>
    [JsonPropertyName("version")]
    public required string Version { get; init; }

    [JsonPropertyName("generated_at")]
    public required string GeneratedAt { get; init; }

    [JsonPropertyName("base_url")]
    public required string BaseUrl { get; init; }

    /// <summary>Covers the dataset EXCEPT the official requirement text described by `text_rights`.</summary>
    [JsonPropertyName("license")]
    public required string License { get; init; }

    /// <summary>Always true, and deliberately not optional: this is a community project with no Scouting America affiliation, and a consumer must not be able to lose that by reading a subset of the document.</summary>
    [JsonPropertyName("unofficial")]
    public required bool Unofficial { get; init; }

    [JsonPropertyName("disclaimer")]
    public required string Disclaimer { get; init; }

    [JsonPropertyName("schemas")]
    public required string Schemas { get; init; }

    [JsonPropertyName("text_rights")]
    public required string TextRights { get; init; }

    /// <summary>Per-dataset counts. `total` spans every entity including historical ones; `current` counts those with an open version. Extra per-dataset keys (e.g. camps' `merged`) may appear.</summary>
    [JsonPropertyName("datasets")]
    public required IReadOnlyDictionary<string, JsonElement> Datasets { get; init; }

    [JsonPropertyName("vocab")]
    public required IReadOnlyList<string> Vocab { get; init; }

    [JsonPropertyName("endpoints")]
    public required IReadOnlyList<string> Endpoints { get; init; }
}
