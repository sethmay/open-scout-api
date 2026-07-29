// Shared plumbing for the C# cookbook -- the mirror of cookbook/python/osa.py, and just as boring
// on purpose: base resolution, JSON decode, the collection envelope, meta, and Check().
//
// TRAP: none lives here. Every trap-fixing rule stays inline in Program.cs, because that rule is
//       exactly what a consumer copies into their own app; folding it into a helper would hide the
//       one thing the cookbook exists to show.
//
// Base resolution order:
//   1. $OSA_BASE              -- what the CI runner sets (a local http://127.0.0.1:PORT)
//   2. --base <value> in argv -- for running by hand
//   3. the published host     -- provisional pre-1.0, hence named in exactly one place
//
// A base may be an http(s) root or a built dist/ directory, so this runs unchanged against CI,
// production, and an offline checkout.

using System.Text.Json;
using System.Text.Json.Serialization;
using OpenScoutApi.Generated;

namespace OpenScoutApi.Cookbook;

/// <summary>A recipe's invariant did not hold. Escaping Main is what makes the process exit
/// nonzero, which is how the CI gate learns that a lesson stopped being true.</summary>
public sealed class CheckException(string message) : Exception(message);

/// <summary>The envelope shared by every <c>v1/current/*.json</c> and
/// <c>v1/{dataset}/index.json</c>: <c>{$schema, version, generated_at, kind, count, items[]}</c>.
/// The generated CurrentCollection/IndexCollection records leave <c>items</c> weakly typed because
/// one schema covers ten kinds; this generic mirror lets a caller name the item record it wants.
/// </summary>
public sealed record Collection<T>
{
    [JsonPropertyName("version")]
    public string Version { get; init; } = "";

    [JsonPropertyName("generated_at")]
    public string GeneratedAt { get; init; } = "";

    [JsonPropertyName("kind")]
    public string Kind { get; init; } = "";

    [JsonPropertyName("count")]
    public int Count { get; init; }

    [JsonPropertyName("items")]
    public IReadOnlyList<T> Items { get; init; } = [];
}

public static class Osa
{
    // Provisional pre-1.0: this host is expected to move (see TODO.md "v1.0 readiness"), which is
    // exactly why the string appears once, here, and in no recipe.
    const string DefaultBase = "https://sethmay.github.io/open-scout-api";

    const string UserAgent = "open-scout-api-cookbook (+https://github.com/sethmay/open-scout-api)";

    /// <summary>The API root, without a trailing slash.</summary>
    public static string Base { get; } = ResolveBase();

    static readonly bool IsHttp =
        Base.StartsWith("http://", StringComparison.Ordinal)
        || Base.StartsWith("https://", StringComparison.Ordinal);

    // One client per process. A fresh HttpClient per request strands sockets in TIME_WAIT, and the
    // cookbook is the first C# a consumer copies, so it should not teach that.
    static readonly HttpClient Http = new() { Timeout = TimeSpan.FromSeconds(30) };

    // No PropertyNamingPolicy, ever. Published field names are snake_case and the generated records
    // carry an explicit [JsonPropertyName] for every one; a policy would compete with those
    // attributes and quietly bind some fields while leaving others at their default.
    static readonly JsonSerializerOptions Options = new() { PropertyNamingPolicy = null };

    static Meta? metaCache;

    static string ResolveBase()
    {
        if (Environment.GetEnvironmentVariable("OSA_BASE") is { Length: > 0 } env)
        {
            return env.TrimEnd('/');
        }

        var argv = Environment.GetCommandLineArgs();
        var i = Array.IndexOf(argv, "--base");
        return i >= 0 && i + 1 < argv.Length ? argv[i + 1].TrimEnd('/') : DefaultBase;
    }

    /// <summary>Fetch and decode one published file. <paramref name="path"/> is relative, e.g.
    /// <c>v1/meta.json</c>.</summary>
    public static async Task<T> GetAsync<T>(string path)
    {
        path = path.TrimStart('/');
        var json = IsHttp
            ? await FetchAsync($"{Base}/{path}")
            : await File.ReadAllTextAsync(Path.Combine(Base, path.Replace('/', Path.DirectorySeparatorChar)));
        return JsonSerializer.Deserialize<T>(json, Options)
            ?? throw new CheckException($"{path}: decoded to null");
    }

    static async Task<string> FetchAsync(string url)
    {
        using var request = new HttpRequestMessage(HttpMethod.Get, url);
        request.Headers.Add("User-Agent", UserAgent);
        using var response = await Http.SendAsync(request);
        // A 404 must surface as a failure, never as an empty result set: "no positions" and "the
        // positions endpoint moved" are different facts and only one of them is recoverable.
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadAsStringAsync();
    }

    /// <summary>The <c>items</c> array of a collection projection, envelope discarded.</summary>
    public static async Task<IReadOnlyList<T>> ItemsAsync<T>(string path)
    {
        var doc = await GetAsync<Collection<T>>(path);
        Check(doc.Count == doc.Items.Count, $"{path}: count disagrees with items length");
        return doc.Items;
    }

    /// <summary>The discovery document, fetched once per process.</summary>
    public static async Task<Meta> MetaAsync() => metaCache ??= await GetAsync<Meta>("v1/meta.json");

    /// <summary>Look a (possibly templated) endpoint up in <c>meta.endpoints</c> instead of assuming
    /// it exists. Returns the template itself, e.g. <c>v1/councils/{id}.json</c>, for the caller to
    /// fill in. Throws when the running API does not publish it -- which is the point: a consumer
    /// pinned to a withdrawn endpoint should fail once, loudly, not 404 forever.</summary>
    public static async Task<string> EndpointAsync(string template)
    {
        var endpoints = (await MetaAsync()).Endpoints;
        Check(
            endpoints.Contains(template),
            $"'{template}' is not published; meta lists {endpoints.Count} endpoints");
        return template;
    }

    /// <summary>Assert an invariant. Recipes assert invariants, never record counts: the dataset
    /// grows every week, so <c>camps.Count == 448</c> is a time bomb while
    /// <c>closure.Contains("kayaking")</c> is a contract.</summary>
    public static void Check(bool condition, string message)
    {
        if (!condition)
        {
            throw new CheckException(message);
        }
    }
}
