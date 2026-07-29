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

# The badge idiom `[![alt](inner)](outer)` must be matched FIRST and consumed whole: LINK's text
# group would otherwise swallow the inner image and capture `inner`, leaving `outer` unchecked --
# which is precisely the construct the README's badge block is made of.
NESTED = re.compile(
    r"\[\s*\!\[(?:[^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)\s*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)"
)
# [text](target) but not ![img](target); captures the target only.
LINK = re.compile(r"(?<!\!)\[(?:[^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
IMAGE = re.compile(r"\!\[(?:[^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$", re.M)
FENCE = re.compile(r"^(\s*)(```|~~~)")


def strip_fences(text: str) -> str:
    """Blank fenced code blocks, preserving line count.

    A `# comment` inside a shell snippet otherwise registers as a HEADING and manufactures a
    phantom anchor, so a link to a nonexistent heading validates -- a gate that can pass a broken
    anchor is worse than no gate.
    """
    out, fence = [], None
    for line in text.splitlines():
        m = FENCE.match(line)
        if fence is None and m:
            fence = m.group(2)
            out.append("")
        elif fence is not None:
            out.append("")
            if m and m.group(2)[0] == fence[0]:
                fence = None
        else:
            out.append(line)
    return "\n".join(out)


def strip_code(text: str) -> str:
    """Fence-stripped AND inline-code-stripped: what the LINK/IMAGE scan should see.

    Prose that *discusses* link syntax must not be checked as a link -- LESSONS.md's own entry
    about an illustrative `[x](./nope)` failed the gate it was describing.

    Deliberately NOT used for headings: GitHub keeps the TEXT of a code span in the anchor, so
    `### Additive-only under \\`v1\\`` really does anchor at `#additive-only-under-v1`. Blanking
    inline code before slugging silently shortened such anchors and broke correct links.
    """
    return re.sub(r"`+[^`]*`+", lambda m: " " * len(m.group(0)), strip_fences(text))


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
    """Every anchor GitHub would serve for this file.

    GitHub disambiguates repeated headings by appending `-1`, `-2`, ... so mirror that rather
    than silently collapsing them into one anchor.
    """
    if not path.exists() or path.suffix != ".md":
        return set()
    text = strip_fences(path.read_text(encoding="utf-8", errors="replace"))
    out: set[str] = set()
    seen: dict[str, int] = {}
    for m in HEADING.finditer(text):
        base = slug(m.group(2))
        n = seen.get(base, 0)
        out.add(base if n == 0 else f"{base}-{n}")
        seen[base] = n + 1
    return out


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
        text = strip_code(md.read_text(encoding="utf-8", errors="replace"))
        own = anchors(md)

        # Nested badge constructs first, taking BOTH targets, then blanked so the flat patterns
        # cannot re-match their halves and mis-attribute the inner URL as the link target.
        targets: list[tuple[str, bool]] = []
        for m in NESTED.finditer(text):
            targets.append((m.group(1), True))    # the image
            targets.append((m.group(2), False))   # the wrapping link
        flat = NESTED.sub(lambda m: " " * len(m.group(0)), text)
        targets += [(m.group(1), False) for m in LINK.finditer(flat)]
        targets += [(m.group(1), True) for m in IMAGE.finditer(flat)]

        for raw, is_image in targets:
                target = raw.strip()
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
