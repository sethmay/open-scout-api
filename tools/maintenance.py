"""Standing health check + re-verification queue for the canonical dataset.

Facts decay at different rates, so one "last verified" date is not enough to plan work
from. This encodes the policy (below) and reports what is due, plus the structural health
checks that are cheap to run and expensive to notice late.

    python tools/maintenance.py                  # report
    python tools/maintenance.py --out FILE.json  # machine-readable
    python tools/maintenance.py --fix-sources    # dedupe provenance sources (the one
                                                 # finding with a safe mechanical repair)

Policy - months before a class of fact is considered due for re-verification:

  signature features   12   a headline draw is the most perishable thing here; a camp
                            trials land sailing for two seasons and drops it
  features             24   ordinary program/facility codes move slowly
  website               6   links rot fastest of all; tools/check_urls.py does the
                            actual fetching, this only reports the age
  provenance           24   identity, council, coordinates - close to inert

Not everything reported is repairable by a tool. "Never surveyed" needs a survey and
"no website" needs a human, and saying so is the point: an empty queue would be a lie.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

SIGNATURE_MONTHS = 12
FEATURES_MONTHS = 24
WEBSITE_MONTHS = 6
PROVENANCE_MONTHS = 24


def read_json(p: Path):
    return json.loads(p.read_text("utf-8"))


def months_since(d: str | None, today: date) -> int | None:
    if not d:
        return None
    try:
        then = date.fromisoformat(d)
    except ValueError:
        return None
    return (today.year - then.year) * 12 + (today.month - then.month)


def entity_files(ds: str) -> list[Path]:
    return sorted(p for p in (DATA / ds).glob("*.json") if p.name != "_events.json")


def open_version(e: dict) -> dict | None:
    for v in e.get("versions", []):
        if v.get("valid_to") is None:
            return v
    return None


def dedupe_sources(srcs: list[dict]) -> list[dict]:
    """Collapse repeats of the same url, keeping the richest entry.

    Repeated passes appended the same url, sometimes bare and sometimes with `accessed`.
    The bare one carries strictly less information, so the entry with an `accessed` date
    wins, and the latest date wins among those. Citations (no url) are never touched.
    """
    best: dict[str, dict] = {}
    out: list[dict] = []
    for s in srcs:
        url = s.get("url")
        if not url:
            out.append(s)
            continue
        prev = best.get(url)
        if prev is None:
            best[url] = s
            out.append(s)
        elif (s.get("accessed") or "") > (prev.get("accessed") or ""):
            out[out.index(prev)] = s
            best[url] = s
    return out


def main() -> None:
    args = sys.argv[1:]
    out_path = Path(args[args.index("--out") + 1]) if "--out" in args else None
    fix = "--fix-sources" in args
    today = date.today()

    camps = [(p, read_json(p)) for p in entity_files("camps")]
    report: dict[str, list] = {}

    # --- re-verification queue -------------------------------------------------
    due_sig, due_feat, due_site, due_prov = [], [], [], []
    never, no_site, imported_unverified = [], [], []
    for p, e in camps:
        v = open_version(e)
        if v is None:
            continue
        cid, feats = e["id"], (v.get("features") or [])
        fva = v.get("features_verified_at")
        age_f = months_since(fva, today)
        if fva is None:
            (imported_unverified if feats else never).append(cid)
        else:
            has_sig = any(f.get("signature") for f in feats)
            if has_sig and age_f is not None and age_f >= SIGNATURE_MONTHS:
                due_sig.append((cid, age_f))
            elif age_f is not None and age_f >= FEATURES_MONTHS:
                due_feat.append((cid, age_f))
        if not v.get("website"):
            no_site.append(cid)
        prov = v.get("provenance") or {}
        newest = max([s.get("accessed") for s in prov.get("sources", []) if s.get("accessed")] or [None],
                     key=lambda x: x or "")
        age_w = months_since(newest, today)
        if age_w is not None and age_w >= WEBSITE_MONTHS and v.get("website"):
            due_site.append((cid, age_w))
        age_p = months_since(prov.get("verified_at"), today)
        if age_p is not None and age_p >= PROVENANCE_MONTHS:
            due_prov.append((cid, age_p))

    # --- vocabulary health: a term nothing uses cannot be filtered on ----------
    vocab = read_json(DATA / "vocab" / "camp-features.json")["terms"]
    used = Counter(f["code"] for _, e in camps for v in [open_version(e)] if v
                   for f in (v.get("features") or []))
    zero = sorted(t["code"] for t in vocab if not used[t["code"]])

    # --- provenance hygiene ----------------------------------------------------
    dupes = []
    for ds in sorted(d.name for d in DATA.iterdir() if d.is_dir() and d.name != "vocab"):
        for p in entity_files(ds):
            e = read_json(p)
            changed = False
            for v in e.get("versions", []) or [e]:
                srcs = (v.get("provenance") or {}).get("sources")
                if not srcs:
                    continue
                dd = dedupe_sources(srcs)
                if len(dd) != len(srcs):
                    dupes.append((f"{ds}/{e.get('id')}", len(srcs) - len(dd)))
                    if fix:
                        v["provenance"]["sources"] = dd
                        changed = True
            if changed:
                p.write_text(json.dumps(e, indent=2, ensure_ascii=False) + "\n",
                             encoding="utf-8", newline="\n")

    report = {
        "generated": today.isoformat(),
        "policy_months": {"signature": SIGNATURE_MONTHS, "features": FEATURES_MONTHS,
                          "website": WEBSITE_MONTHS, "provenance": PROVENANCE_MONTHS},
        "due_signature": due_sig, "due_features": due_feat,
        "due_website": due_site, "due_provenance": due_prov,
        "never_surveyed": never, "imported_unverified": imported_unverified,
        "no_website": no_site, "zero_use_vocab": zero,
        "duplicate_sources": dupes,
    }

    print(f"maintenance report {today} ({len(camps)} camps)\n")
    print("  DUE FOR RE-VERIFICATION (policy above)")
    for label, rows in [("signature features", due_sig), ("features", due_feat),
                        ("website age", due_site), ("provenance", due_prov)]:
        n = len(rows)
        oldest = f"  oldest {max(r[1] for r in rows)}mo" if rows else ""
        print(f"    {label:22} {n:>4}{oldest}")
    print("\n  NEEDS WORK, NOT A CLOCK")
    print(f"    never surveyed         {len(never):>4}  (no features, no survey date)")
    print(f"    imported, unverified   {len(imported_unverified):>4}  (features present, never confirmed)")
    print(f"    no website             {len(no_site):>4}  (link cleared or never had one)")
    print("\n  STRUCTURAL HEALTH")
    print(f"    zero-use vocab terms   {len(zero):>4}  {', '.join(zero[:6])}{' …' if len(zero) > 6 else ''}")
    print(f"    duplicated sources     {len(dupes):>4} entities, "
          f"{sum(d[1] for d in dupes)} redundant entries"
          f"{'  -> FIXED' if fix else '  (rerun with --fix-sources)'}")
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"\n  wrote {out_path}")


if __name__ == "__main__":
    main()
