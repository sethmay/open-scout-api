"""Check every relative Markdown link and heading anchor in the repo's docs.

A README is the one file where a broken link is both most visible and least likely to be noticed
by any existing gate: nothing else in this repo reads Markdown. Splitting the README into
docs/*.md multiplied the cross-links, so they get a check.

Verifies, for every tracked `.md` file:
  - a relative link target exists on disk (`./docs/foo.md`, `../README.md`, `./LICENSE`);
  - an `#anchor` resolves to a real heading in the target file, using GitHub's slug rules;
  - an image link points at a file that exists and is not gitignored (a `.jpg` screenshot would
    be silently dropped by this repo's .gitignore, which is exactly the trap this catches).

External `http(s)` links are NOT fetched -- that would make the check flaky and slow. Use
`--external` to include them when you actually want that.

Usage:
  python tools/check_links.py
  python tools/check_links.py --external
"""

from __future__ import annotations

import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "node_modules", "dist", ".workbench", "__pycache__", ".claude", "obj", "bin"}

# [text](target) but not ![img](target); captures the target only.
LINK = re.compile(r"(?<!\!)\[(?:[^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
IMAGE = re.compile(r"\!\[(?:[^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$", re.M)


def slug(heading: str) -> str:
    """GitHub's anchor rule: lowercase, strip punctuation, spaces to hyphens.

    Underscores SURVIVE. `_` is a word character, and github-slugger only strips the emphasis
    markers `*` and `~` -- so a heading like "Coordinates: `geo_precision`" anchors at
    `#coordinates-geo_precision`. Stripping `_` here made this checker reject that correct link
    and accept a broken one, which is worse than having no checker.
    """
    s = heading.strip().lower()
    s = re.sub(r"`([^`]*)`", r"\1", s)              # inline code keeps its text
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)  # links keep their text
    s = re.sub(r"[*~]", "", s)
    s = re.sub(r"[^\w\s-]", "", s)                  # \w keeps letters, digits and underscore
    # Per-space, NOT `\s+`: github-slugger replaces each space individually and does not collapse
    # runs, so "tier — how" (space, em dash, space) anchors with TWO hyphens once the dash is gone.
    return re.sub(r"\s", "-", s).strip("-")


def anchors(path: Path) -> set[str]:
    if not path.exists() or path.suffix != ".md":
        return set()
    text = path.read_text(encoding="utf-8", errors="replace")
    return {slug(m.group(2)) for m in HEADING.finditer(text)}


def markdown_files() -> list[Path]:
    return sorted(
        p for p in ROOT.rglob("*.md")
        if not SKIP_DIRS & set(p.relative_to(ROOT).parts)
    )


def ignored(path: Path) -> bool:
    """True if git would ignore this file -- a silently-dropped image is the trap here."""
    r = subprocess.run(
        ["git", "check-ignore", "-q", str(path)], cwd=ROOT, capture_output=True, check=False
    )
    return r.returncode == 0


def main() -> int:
    check_external = "--external" in sys.argv
    errs: list[str] = []
    n_links = n_imgs = n_ext = 0

    for md in markdown_files():
        rel = md.relative_to(ROOT).as_posix()
        text = md.read_text(encoding="utf-8", errors="replace")
        own = anchors(md)

        for pattern, is_image in ((LINK, False), (IMAGE, True)):
            for m in pattern.finditer(text):
                target = m.group(1).strip()
                if target.startswith(("http://", "https://")):
                    n_ext += 1
                    if check_external:
                        try:
                            req = urllib.request.Request(target, method="HEAD",
                                                         headers={"User-Agent": "link-check"})
                            urllib.request.urlopen(req, timeout=20)  # noqa: S310
                        except Exception as exc:  # noqa: BLE001 - report, do not raise
                            errs.append(f"{rel}: external {target} -> {type(exc).__name__}")
                    continue
                if target.startswith(("mailto:", "#")):
                    if target.startswith("#") and (a := target[1:]) and a not in own:
                        errs.append(f"{rel}: own anchor '#{a}' matches no heading here")
                    n_links += 1
                    continue

                path_part, _, anchor = target.partition("#")
                dest = (md.parent / path_part).resolve() if path_part else md
                if not dest.exists():
                    errs.append(f"{rel}: link target does not exist -> {target}")
                    continue
                if is_image:
                    n_imgs += 1
                    if ignored(dest):
                        errs.append(
                            f"{rel}: image {target} IS GITIGNORED -- it will not be committed "
                            f"and will render broken on GitHub"
                        )
                else:
                    n_links += 1
                if anchor and dest.suffix == ".md" and anchor not in anchors(dest):
                    errs.append(f"{rel}: anchor '#{anchor}' not found in {path_part}")

    print(f"checked {len(markdown_files())} markdown files: "
          f"{n_links} relative links, {n_imgs} images, {n_ext} external"
          f"{' (fetched)' if check_external else ' (not fetched)'}")
    if errs:
        print(f"\n{len(errs)} problem(s):")
        for e in errs:
            print(f"  {e}")
        return 1
    print("all links and anchors resolve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
