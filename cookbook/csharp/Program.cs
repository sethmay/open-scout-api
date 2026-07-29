// The C# starter: four recipes, each killing one documented trap in the published data.
//
// TRAP: the whole file exists because this dataset models change and uncertainty as data, so a
//       naive consumer gets a plausible WRONG ANSWER instead of an error -- a hardcoded host that
//       silently 404s, a feature filter that matches nothing, a null Eagle flag folded into false,
//       a state centroid plotted as a campsite.
// FIX:  each recipe below states its own TRAP/FIX and proves it with Check(), so running this
//       program is the test. Every Check is an invariant, never a record count.
//
// Run:  dotnet run                 (OSA_BASE overrides the host; see Osa.cs)

using System.Text.Json;
using System.Text.Json.Serialization;
using OpenScoutApi.Cookbook;
using OpenScoutApi.Generated;

await Recipes.DiscoverAsync();
await Recipes.FeatureHierarchyAsync();
await Recipes.EagleRequiredTriStateAsync();
await Recipes.GeoPrecisionAsync();

static class Recipes
{
    /// <summary>Resolve the API surface from v1/meta.json instead of hardcoding host and paths.
    ///
    /// TRAP: pasting the published host and a guessed layout into your app. The host is explicitly
    ///       provisional pre-1.0 and is also the $id prefix of every schema, so a move invalidates
    ///       both at once. Guessing a path is the same bug one level down: asking for an endpoint
    ///       that was never published returns 404, which naive code reports as "no results".
    /// FIX:  read the base from configuration once, then resolve every path out of meta.endpoints,
    ///       the machine-readable index of the whole surface, and fail loudly when one is absent.
    /// </summary>
    public static async Task DiscoverAsync()
    {
        var meta = await Osa.MetaAsync();

        // `unofficial` is const:true and required, precisely so a consumer cannot read a subset of
        // this document and lose the no-affiliation fact.
        Osa.Check(meta.Unofficial, "meta must assert unofficial");
        Osa.Check(meta.BaseUrl.StartsWith("http", StringComparison.Ordinal), "meta.base_url must be absolute");

        // Templated endpoints ship with their placeholders, e.g. v1/councils/{id}.json, so a client
        // formats the published template rather than inventing a directory layout.
        string[] templated = [.. meta.Endpoints.Where(e => e.Contains('{'))];
        string[] collections = [.. meta.Endpoints.Where(e => !e.Contains('{'))];
        Osa.Check(
            templated.Length > 0 && collections.Length > 0,
            "meta must publish both templated and collection endpoints");

        // The vocabularies are referenced twice on purpose -- `vocab` says which files are code
        // lists, `endpoints` says what is served. A vocab file missing from `endpoints` would mean
        // published codes with no published definition.
        Osa.Check(
            meta.Vocab.All(meta.Endpoints.Contains),
            "every vocabulary in meta.vocab must also be a published endpoint");

        // EndpointAsync throws rather than handing back a URL the API does not serve.
        var template = await Osa.EndpointAsync("v1/councils/{id}.json");
        var council = await Osa.GetAsync<VersionedEntity>(template.Replace("{id}", "mississippi-riverlands"));
        Osa.Check(council.Kind == "council", "a council document must declare kind=council");

        // Exactly one version may be open (valid_to null) -- that is what "current" means here, and
        // it is why a consumer must never assume versions[0] is the live one.
        Osa.Check(
            council.Versions.Count(v => v.ValidTo.ValueKind == JsonValueKind.Null) <= 1,
            "an entity may have at most one open version");

        // The licensing carve-out travels with the discovery document, not just the README:
        // requirement text is (c) Scouting America and is NOT under this dataset's licence.
        Osa.Check(
            meta.TextRights.Contains("Scouting America", StringComparison.Ordinal),
            "meta must carry the text_rights carve-out");

        Console.WriteLine("recipe 1  discovery");
        Row("base", Osa.Base);
        Row("version", $"{meta.Version} (generated {meta.GeneratedAt})");
        Row("license", $"{meta.License}  (requirement text: see meta.text_rights)");
        Row("endpoints", $"{collections.Length} collections + {templated.Length} templated");
        Row("vocabularies", $"{meta.Vocab.Count} of {meta.Endpoints.Count(e => e.StartsWith("v1/vocab/", StringComparison.Ordinal))} served");
        Row("resolved", $"{template} -> {council.Id}  versions={council.Versions.Count} events={council.Events.Count}");
    }

    /// <summary>Expand a coarse camp feature code to everything beneath it before filtering.
    ///
    /// TRAP: `camp.Features.Contains("aquatics")` finds almost nothing. Feature codes form a
    ///       hierarchy through each vocab term's `broader`, and a camp is tagged with the specific
    ///       code it offers (`kayaking`), not with the parent.
    /// FIX:  invert `broader` into a parent -> children index, take the TRANSITIVE closure of the
    ///       code you were asked about, then match a camp if any of its features is in that set.
    /// </summary>
    public static async Task FeatureHierarchyAsync()
    {
        var vocab = await Osa.GetAsync<Vocabulary>("v1/vocab/camp-features.json");

        // `broader` points up, one level, and nothing in the file lists a term's children, so the
        // index has to be inverted. The tree is shallow today and that is not a contract: a
        // hand-written two-level lookup would silently miss the day a third level lands.
        var children = vocab.Terms
            .Where(t => t.Broader is not null)
            .GroupBy(t => t.Broader!, t => t.Code)
            .ToDictionary(g => g.Key, g => g.ToArray(), StringComparer.Ordinal);

        const string Root = "aquatics";
        HashSet<string> closure = new(StringComparer.Ordinal) { Root };
        Queue<string> pending = new(closure);
        while (pending.TryDequeue(out var code))
        {
            if (!children.TryGetValue(code, out var kids))
            {
                continue;
            }

            foreach (var child in kids)
            {
                if (closure.Add(child))
                {
                    pending.Enqueue(child);
                }
            }
        }

        var camps = await Osa.ItemsAsync<CurrentCamp>("v1/current/camps.json");
        var naive = camps.Count(c => c.Features.Contains(Root));
        var correct = camps.Count(c => c.Features.Any(closure.Contains));

        Osa.Check(closure.Contains("kayaking"), $"the {Root} closure must contain its child terms");
        Osa.Check(closure.Count > 1, "a parent term that expands to itself means the broader index broke");
        Osa.Check(correct > naive, "closure matching must find camps that exact-code matching misses");

        // The closure must be closed: every member's parent chain has to land back inside it, or the
        // walk stopped early and the filter is quietly under-counting.
        var byCode = vocab.Terms.ToDictionary(t => t.Code, StringComparer.Ordinal);
        Osa.Check(
            closure.All(c => c == Root || (byCode[c].Broader is { } p && closure.Contains(p))),
            "every non-root member of a closure must have its parent in the closure");

        // Referential integrity in the same direction: a code on a camp that the vocabulary does not
        // define would be unexpandable, so the closure walk could never reach it.
        Osa.Check(
            camps.SelectMany(c => c.Features).All(byCode.ContainsKey),
            "every feature code on a camp must be defined in the vocabulary");

        // Aliases are the same trap in a different coat: a camp page saying "sea kayaking" resolves
        // to the `kayaking` code, so an alias string must never be matched against `features`.
        var aliased = vocab.Terms.Count(t => t.Aliases.Count > 0);

        Console.WriteLine("\nrecipe 2  feature hierarchy");
        Row("vocabulary", $"{vocab.Terms.Count} terms, {children.Count} with children, {aliased} with aliases");
        Row($"{Root} closure", $"{closure.Count} codes: {string.Join(", ", closure.Order(StringComparer.Ordinal).Take(6))}, ...");
        Row("exact match", $"{naive} camps  <- the wrong answer");
        Row("closure match", $"{correct} camps  <- {correct - naive} camps a literal filter drops");
    }

    /// <summary>Read eagle_required as three states, because bool? here really means three states.
    ///
    /// TRAP: `!badge.EagleRequired.GetValueOrDefault()` reads as "not Eagle-required" and is a bug.
    ///       null means UNKNOWN -- badges retired before the modern published list cannot be sourced
    ///       either way -- and GetValueOrDefault() launders that unknown into a confident false.
    ///       C# makes this especially easy to hit: `??`, `== true`, and `GetValueOrDefault()` all
    ///       compile clean and all lose the distinction.
    /// FIX:  branch on true / false / null explicitly and report the third bucket to the user.
    /// </summary>
    public static async Task EagleRequiredTriStateAsync()
    {
        var badges = await Osa.ItemsAsync<MeritBadgeIndexItem>("v1/merit-badges/index.json");

        // The three-way branch, written out. A switch over bool? is exhaustive, so the compiler will
        // not let the unknown arm be forgotten -- which is the whole reason to write it this way.
        List<MeritBadgeIndexItem> required = [], notRequired = [], unknown = [];
        foreach (var badge in badges)
        {
            var bucket = badge.EagleRequired switch
            {
                true => required,
                false => notRequired,
                null => unknown,
            };
            bucket.Add(badge);
        }

        // A switch over bool? is exhaustive, so "the three buckets partition the index" is a fact
        // about the switch, not about the data -- there is no dataset that fails it. What the data
        // can fail is that all three states are actually populated, which is the claim that makes
        // the tri-state worth writing at all.
        Osa.Check(unknown.Count > 0, "a plain bool cannot model this field: some badges are UNKNOWN");
        Osa.Check(required.Count > 0 && notRequired.Count > 0, "both known states must be represented");

        // The contract that makes the tri-state tractable: anything still offered has a real answer,
        // so a consumer showing only current badges never has to render "unknown".
        Osa.Check(
            unknown.All(b => !b.Current),
            "eagle_required may only be unknown for non-current badges");
        // (`current => eagle_required is not null` is the same statement contrapositive, so it is
        // deliberately not asserted twice.)

        // The damage, measured rather than asserted in prose: the naive predicate silently absorbs
        // every unknown badge into its "not required" answer. `naive == notRequired + unknown` is
        // the definition of GetValueOrDefault() and no dataset can fail it, so the falsifiable form
        // is asserted instead -- the fold moves badges, and (per the checks above) they are real
        // non-current badges rather than an artefact of the count.
        var naive = badges.Count(b => !b.EagleRequired.GetValueOrDefault());
        Osa.Check(naive > notRequired.Count, "that fold is not harmless -- it moves badges");

        Console.WriteLine("\nrecipe 3  eagle_required tri-state");
        Row("true", $"{required.Count} badges");
        Row("false", $"{notRequired.Count} badges");
        Row("null (unknown)", $"{unknown.Count} badges, all non-current, e.g. {unknown[0].Id}");
        Row("naive !x ?? false", $"{naive} 'not required'  <- overstates by {naive - notRequired.Count}");
    }

    /// <summary>Only plot a camp pin when the coordinate is precise enough to be a place.
    ///
    /// TRAP: `map.Pin(camp.Lat, camp.Lon)` over every camp. A coordinate here can be a state or
    ///       council-office centroid: accurate enough to colour a region, wrong enough that a pin
    ///       asserts a campsite in the middle of a city. Nulls are the smaller half of the problem.
    /// FIX:  partition on geo_precision -- `exact` is pinnable, `approximate` is a region hint, a
    ///       missing coordinate is unplaceable -- and render the three differently.
    /// </summary>
    public static async Task GeoPrecisionAsync()
    {
        var camps = await Osa.ItemsAsync<CurrentCamp>("v1/current/camps.json");

        CurrentCamp[] pinnable = [.. camps.Where(c => c is { Lat: not null, Lon: not null, GeoPrecision: "exact" })];
        CurrentCamp[] softPlot = [.. camps.Where(c => c is { Lat: not null, Lon: not null, GeoPrecision: "approximate" })];
        CurrentCamp[] unplaceable = [.. camps.Where(c => c.Lat is null || c.Lon is null)];

        Osa.Check(
            pinnable.Length + softPlot.Length + unplaceable.Length == camps.Count,
            "the three buckets must partition the collection -- an unhandled geo_precision means "
                + "camps are being dropped or double-counted");

        // The invariant that makes the partition safe to write: precision is never absent from a
        // published coordinate, so there is no fourth "located but unlabelled" case to guess at.
        Osa.Check(
            camps.Where(c => c.Lat is not null).All(c => c.GeoPrecision is not null),
            "every camp with a coordinate must carry a non-null geo_precision");
        Osa.Check(
            camps.All(c => (c.Lat is null) == (c.Lon is null)),
            "a coordinate must be published as a pair or not at all");
        Osa.Check(softPlot.Length > 0, "approximate coordinates exist; a two-way split would hide them");

        // Reservations are the second half of the same trap. Distinct camps share one property, and
        // it is the property that got geocoded, so pinning per camp stacks identical markers on top
        // of each other -- render one pin per reservation and list the camps under it.
        var stacked = pinnable.Concat(softPlot)
            .Where(c => c.Reservation is not null)
            .GroupBy(c => c.Reservation!.Id, StringComparer.Ordinal)
            .Count(g => g.Count() > 1);
        Osa.Check(stacked > 0, "camps sharing a reservation exist; a per-camp pin would stack them");

        Console.WriteLine("\nrecipe 4  geo precision");
        Row("exact", $"{pinnable.Length} camps  -> pin it");
        Row("approximate", $"{softPlot.Length} camps  -> region hint only, e.g. {softPlot[0].Id}");
        Row("no coordinate", $"{unplaceable.Length} camps  -> list, never map");
        Row("shared property", $"{stacked} reservations hold >1 located camp -> one pin per property");
    }

    static void Row(string label, string value) => Console.WriteLine($"  {label,-18}{value}");
}

/// <summary>An open vocabulary file (v1/vocab/*.json). Not in the generated types: the published
/// schema set does not pin vocabulary documents, because the term LISTS are open and grow.</summary>
sealed record Vocabulary
{
    [JsonPropertyName("id")]
    public string Id { get; init; } = "";

    [JsonPropertyName("title")]
    public string Title { get; init; } = "";

    [JsonPropertyName("terms")]
    public IReadOnlyList<VocabTerm> Terms { get; init; } = [];
}

/// <summary>One term. <c>Broader</c> is a single parent code or absent -- the hierarchy is expressed
/// upwards only, so children have to be derived.</summary>
sealed record VocabTerm
{
    [JsonPropertyName("code")]
    public string Code { get; init; } = "";

    [JsonPropertyName("label")]
    public string Label { get; init; } = "";

    [JsonPropertyName("category")]
    public string Category { get; init; } = "";

    [JsonPropertyName("broader")]
    public string? Broader { get; init; }

    [JsonPropertyName("aliases")]
    public IReadOnlyList<string> Aliases { get; init; } = [];
}
