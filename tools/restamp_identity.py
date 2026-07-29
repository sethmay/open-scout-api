"""Re-stamp the dataset's published identity: the API base URL and/or the repository slug.

This exists to make the last 1.0 blocker cheap. The API base URL is the schema `$id` prefix,
the documented API root, and the jsDelivr pin path, and it appears in ~1,900 files - so
"decide the permanent home" has felt like a one-way door. It is not: it is one command, and
this tool proves it by verifying nothing stale survives and nothing unrelated moved.

Two identities move INDEPENDENTLY, which is the whole point:

  --api-base   the published root that schema `$id`s and every documented URL hang off.
               Make this a CUSTOM DOMAIN and it never has to change again, even if the repo
               moves between owners or orgs. That is the durable answer.
  --repo       owner/name of the GitHub repository: source links, tool User-Agent strings,
               and the Zenodo related_identifier.

Deliberately NOT touched:
  * `creators` in .zenodo.json - authorship is a person, not a host.
  * any other repo owned by the same account (README links github.com/<owner>/camp-finder,
    which is a different project and must not follow this move).
  * dist/ - generated, and rebuilt from these values anyway.

    python tools/restamp_identity.py --api-base https://api.example.org            # dry run
    python tools/restamp_identity.py --repo scouting-data/open-scout-api --apply
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "dist", ".workbench", "node_modules", "__pycache__", ".claude"}
# Every extension that can contain the published host as a literal. `cookbook/` introduced the
# repo's first .ts/.cs/.sh/.js files, and each language's helper names the default base once --
# so omitting them made this tool (and its own post-apply verification pass, which reuses the
# same walk) silently blind to nine occurrences: a move would report success while nine files
# still pointed at the dead host, and nothing downstream would catch it because CI exports
# OSA_BASE. Add the suffix here whenever a new language lands under cookbook/.
TEXT_SUFFIXES = {".json", ".py", ".ts", ".cs", ".sh", ".js", ".md", ".yml", ".yaml", ".html",
                 ".txt", ".sql"}


def current_identity() -> tuple[str, str]:
    """Read today's values out of build.py rather than hardcoding them here."""
    src = (ROOT / "tools" / "build.py").read_text("utf-8")
    m = re.search(r'^BASE_URL\s*=\s*"([^"]+)"', src, re.M)
    if not m:
        raise SystemExit("could not find BASE_URL in tools/build.py")
    api = m.group(1).rstrip("/")
    r = re.search(r'github\.com/([A-Za-z0-9._-]+/[A-Za-z0-9._-]+)', src)
    return api, (r.group(1) if r else "")


def walk() -> list[Path]:
    out = []
    for p in ROOT.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in p.relative_to(ROOT).parts):
            continue
        out.append(p)
    return sorted(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--api-base", help="new published root, e.g. https://api.example.org (no trailing slash)")
    ap.add_argument("--repo", help="new GitHub repository slug, e.g. org/open-scout-api")
    ap.add_argument("--apply", action="store_true", help="write the changes (default is a dry run)")
    a = ap.parse_args()
    if not a.api_base and not a.repo:
        ap.error("give --api-base and/or --repo")

    old_api, old_repo = current_identity()
    subs: list[tuple[str, str, str]] = []
    if a.api_base:
        new = a.api_base.rstrip("/")
        if new == old_api:
            print(f"api-base already {new}")
        else:
            subs.append(("api base", old_api, new))
    if a.repo:
        if not re.fullmatch(r"[A-Za-z0-9._-]+/[A-Za-z0-9._-]+", a.repo):
            ap.error("--repo must look like owner/name")
        if a.repo == old_repo:
            print(f"repo already {a.repo}")
        else:
            # scoped to THIS repo, so a sibling project under the same owner is untouched
            subs.append(("repo slug", f"github.com/{old_repo}", f"github.com/{a.repo}"))
    if not subs:
        return

    print("planned substitutions:")
    for label, o, n in subs:
        print(f"  {label:10} {o}  ->  {n}")

    touched: dict[str, int] = {}
    total = 0
    for p in walk():
        try:
            body = p.read_text("utf-8")
        except UnicodeDecodeError:
            continue
        new_body = body
        for _label, o, n in subs:
            new_body = new_body.replace(o, n)
        if new_body == body:
            continue
        hits = sum(body.count(o) for _l, o, _n in subs)
        rel = p.relative_to(ROOT).as_posix()
        touched[rel.split("/")[0] if "/" in rel else rel] = touched.get(
            rel.split("/")[0] if "/" in rel else rel, 0) + hits
        total += hits
        if a.apply:
            p.write_text(new_body, encoding="utf-8", newline="\n")

    print(f"\n{'rewrote' if a.apply else 'would rewrite'} {total} occurrences, grouped by top level:")
    for k, v in sorted(touched.items(), key=lambda kv: -kv[1]):
        print(f"  {k:22} {v}")

    # the author is a person and must never follow the host
    z = ROOT / ".zenodo.json"
    if z.exists():
        creators = json.loads(z.read_text("utf-8")).get("creators", [])
        print(f"\n.zenodo.json creators left alone: {[c.get('name') for c in creators]}")

    if not a.apply:
        print("\ndry run - nothing written. Re-run with --apply, then:")
        print("  python tools/validate_data.py && python tools/build.py && "
              "python tools/build_sqlite.py && python tools/validate_examples.py")
        return

    # --- verify: nothing stale survives in the scoped patterns -------------------
    stale = []
    for p in walk():
        try:
            body = p.read_text("utf-8")
        except UnicodeDecodeError:
            continue
        for label, o, _n in subs:
            if o in body:
                stale.append((p.relative_to(ROOT).as_posix(), label))
    if stale:
        print(f"\nSTALE REFERENCES REMAIN ({len(stale)}):")
        for f, label in stale[:20]:
            print(f"   {f}: {label}")
        raise SystemExit(1)
    print("\nverified: zero stale references to the old identity")
    print("now run the validators and the build; then update the CHANGELOG and tag.")


if __name__ == "__main__":
    main()
