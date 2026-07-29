"""Shared plumbing for the Python cookbook recipes. Standard library only.

This module deliberately contains ONLY the boring parts: resolving the base, fetching and
decoding JSON, reading the discovery document, and a check helper. The interesting
per-dataset logic lives inline in each recipe, because that logic is what a consumer has to
copy into their own app -- hiding it behind a helper would defeat the point of the cookbook.

Base resolution order:
  1. $OSA_BASE                 -- what the CI runner sets (a local http://127.0.0.1:PORT)
  2. --base <value> in argv    -- for running a recipe by hand
  3. the published host        -- provisional pre-1.0, hence never hardcoded in a recipe

A base may be an http(s) URL or a local directory (a built ``dist/``), so recipes work
offline against a checkout without changing a line.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Any

# Provisional pre-1.0: the base URL is expected to move (see TODO.md "v1.0 readiness"), which
# is exactly why this string appears once, here, and in no recipe.
DEFAULT_BASE = "https://sethmay.github.io/open-scout-api"

USER_AGENT = "open-scout-api-cookbook (+https://github.com/sethmay/open-scout-api)"

_meta_cache: dict[str, Any] | None = None


class CheckError(AssertionError):
    """A recipe's invariant did not hold."""


def check(cond: object, msg: str) -> None:
    """Assert an invariant. Unlike ``assert`` this survives ``python -O``.

    Recipes assert invariants, never record counts: the dataset grows every week, so
    ``len(camps) == 448`` is a time bomb while ``closure >= {"kayaking"}`` is a real contract.
    """
    if not cond:
        raise CheckError(msg)


def base() -> str:
    """The API root, without a trailing slash."""
    env = os.environ.get("OSA_BASE")
    if env:
        return env.rstrip("/")
    argv = sys.argv
    if "--base" in argv:
        i = argv.index("--base")
        if i + 1 < len(argv):
            return argv[i + 1].rstrip("/")
    return DEFAULT_BASE


def get(path: str) -> Any:
    """Fetch and decode one published JSON file. ``path`` is relative, e.g. ``v1/meta.json``."""
    root = base()
    path = path.lstrip("/")
    if root.startswith(("http://", "https://")):
        req = urllib.request.Request(f"{root}/{path}", headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 - fixed scheme above
            return json.loads(resp.read().decode("utf-8"))
    return json.loads((Path(root) / path).read_text(encoding="utf-8"))


def meta() -> dict[str, Any]:
    """The discovery document, fetched once per process."""
    global _meta_cache
    if _meta_cache is None:
        _meta_cache = get("v1/meta.json")
    return _meta_cache


def endpoint(template: str) -> str:
    """Look a templated endpoint up in ``meta.endpoints`` instead of assuming it exists.

    Returns the template itself (e.g. ``v1/councils/{id}.json``) so a caller can format it.
    Raises if the running API does not publish it -- which is the point: a consumer pinned to
    an endpoint that went away should fail loudly rather than 404 silently per-request.
    """
    endpoints = meta()["endpoints"]
    if template not in endpoints:
        raise KeyError(f"{template!r} is not published; meta lists {len(endpoints)} endpoints")
    return template


def items(path: str) -> list[dict[str, Any]]:
    """The ``items`` array of a collection projection, with the envelope discarded.

    Every ``v1/current/*.json`` and ``v1/{dataset}/index.json`` file shares the envelope
    ``{$schema, version, generated_at, kind, count, items[]}``.
    """
    doc = get(path)
    check(doc["count"] == len(doc["items"]), f"{path}: count disagrees with items length")
    return doc["items"]
