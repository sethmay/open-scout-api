# C# starter

A console app that reads the published dataset with `System.Text.Json` and the generated records
in `Generated/V1.cs`. No NuGet packages: `System.Text.Json` is in the shared framework, so this
directory runs on a machine with no feed configured.

```
dotnet run
```

`OSA_BASE` overrides the host, and may be either an `http(s)` root or a built `dist/` directory:

```
OSA_BASE=http://127.0.0.1:8000 dotnet run
OSA_BASE=../../dist dotnet run
```

Falling back to the published host is the only place a URL is written down (`Osa.cs`); the base is
provisional pre-1.0, so no recipe names it. `--base <value>` works too, for running by hand.

Each recipe asserts invariants with `Osa.Check` and throws on failure, so a nonzero exit means one
of the lessons below stopped being true. The assertions are structural — supersets, partitions,
exhaustiveness — never record counts, because the dataset grows every week.

## Traps demonstrated

| Recipe | The wrong answer | The fix |
| --- | --- | --- |
| `DiscoverAsync` | a hardcoded host and guessed paths; a withdrawn endpoint 404s and reads as "no results" | resolve the base from configuration and every path from `v1/meta.json` |
| `FeatureHierarchyAsync` | `Features.Contains("aquatics")` matches 61 of 448 camps | expand the code's transitive closure over each vocab term's `broader`, then match — 321 camps |
| `EagleRequiredTriStateAsync` | `!badge.EagleRequired.GetValueOrDefault()` calls 126 UNKNOWN badges "not required" | branch on `true` / `false` / `null` explicitly and report the third bucket |
| `GeoPrecisionAsync` | pinning every `lat`/`lon`; `approximate` coordinates are property or regional centroids | partition on `geo_precision`, and render one pin per shared reservation |

`Osa.cs` is the C# mirror of `../python/osa.py` and holds only plumbing — base resolution, JSON
decode, the collection envelope, `MetaAsync`, `EndpointAsync`, `Check`. The trap-fixing logic stays
inline in `Program.cs` on purpose: that logic is what you copy into your own app, so hiding it
behind a helper would defeat the point.
