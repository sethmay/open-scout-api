"""Run every cookbook recipe against a locally-built dist/ and fail on any error.

A rotten example is worse than no example, so the cookbook is gated exactly like the data is.
The gate is deliberately semantic, not a syntax check: each recipe asserts its own invariants
and exits nonzero when they break, so "the recipe ran" and "the recipe is still correct" are
the same fact.

How it runs:

  * serves ``dist/`` over http on a free loopback port and exports ``OSA_BASE`` to it, so every
    language exercises real HTTP with no file:// path translation and no network egress;
  * Python / shell / C# / TypeScript recipes are subprocesses that must exit 0 and print
    something (a recipe that produces no output is not a demonstration);
  * SQL recipes run against ``dist/v1/open-scout-api.sqlite``, whose ``-- @assert`` blocks are
    evaluated as queries that must each return one truthy scalar;
  * every recipe must carry a ``TRAP:`` line in its header, which is what keeps the collection
    from drifting back into "how to call fetch".

Node and .NET are skipped (loudly) when their toolchains are absent, so a contributor with
neither installed can still gate the Python, shell and SQL surfaces. CI has all of them.

Usage:
  python tools/validate_cookbook.py
  python tools/validate_cookbook.py --only python,sql
  python tools/validate_cookbook.py --strict    every skipped suite becomes a failure (CI)
  python tools/validate_cookbook.py --base https://sethmay.github.io/open-scout-api
"""

from __future__ import annotations

import functools
import http.server
import itertools
import os
import re
import shutil
import socket
import sqlite3
import subprocess
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
COOKBOOK = ROOT / "cookbook"
SQLITE = DIST / "v1" / "open-scout-api.sqlite"

TIMEOUT = 180  # generous: a recipe may walk every requirement-set document
INSTALL_TIMEOUT = 600

SUITES = ("python", "sql", "shell", "ts", "csharp", "starters")


class Result:
    def __init__(self, strict: bool = False) -> None:
        self.passed: list[str] = []
        self.failed: list[tuple[str, str]] = []
        self.skipped: list[tuple[str, str]] = []
        # A skip is the right local behaviour -- a contributor with no .NET installed should
        # still be able to gate Python and SQL. In CI it is a hole: if jq or node went missing
        # from the image, that suite would silently contribute zero coverage and the build would
        # stay green. --strict turns every skip into a failure, so CI cannot lose a suite quietly.
        self.strict = strict

    def ok(self, name: str) -> None:
        self.passed.append(name)
        print(f"  ok    {name}")

    def fail(self, name: str, why: str) -> None:
        self.failed.append((name, why))
        print(f"  FAIL  {name}\n{indent(why)}")

    def skip(self, name: str, why: str) -> None:
        if self.strict:
            self.fail(name, f"{why} (--strict: a skipped suite is a failure)")
            return
        self.skipped.append((name, why))
        print(f"  skip  {name} ({why})")


def indent(text: str, prefix: str = "        ") -> str:
    body = text.strip().splitlines() or ["(no output)"]
    return "\n".join(prefix + line for line in body[-30:])


# --- the local API -----------------------------------------------------------------------


REQUESTS = itertools.count()


def serve_dist() -> tuple[str, http.server.ThreadingHTTPServer]:
    """Serve dist/ on a free loopback port, counting hits. Returns (base_url, server).

    The counter is not diagnostics -- it is the gate on the gate. A recipe that ignores
    ``OSA_BASE`` still passes every assertion, because it silently talks to the LIVE published
    site instead of the tree under test; that is exactly how the WSLENV bug survived to review.
    Counting requests is the only way this process can tell "validated dist/" from "validated
    production", so each suite asserts it actually generated traffic.
    """

    class Counting(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args: object) -> None:  # silence per-request logs
            pass

        def do_GET(self) -> None:
            next(REQUESTS)
            super().do_GET()

    handler = functools.partial(Counting, directory=str(DIST))
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{port}", httpd


# --- shared checks -----------------------------------------------------------------------


def header_trap(path: Path) -> str | None:
    """Every recipe states the wrong answer it prevents. Returns an error message or None."""
    head = path.read_text(encoding="utf-8", errors="replace")[:4000]
    if "TRAP:" not in head:
        return (
            "missing a `TRAP:` line in the file header. Every recipe must name the wrong answer "
            "a naive consumer gets; see cookbook/README.md."
        )
    return None


def run(cmd: list[str], cwd: Path, env: dict[str, str], timeout: int = TIMEOUT) -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout, check=False
        )
    except subprocess.TimeoutExpired:
        return False, f"timed out after {timeout}s"
    except OSError as exc:
        return False, f"could not execute {cmd[0]}: {exc}"
    out = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0:
        return False, f"exit {proc.returncode}\n{out}"
    if not (proc.stdout or "").strip():
        return False, f"exited 0 but printed nothing; a recipe must show its result\n{out}"
    return True, out


def bash_tools_missing(tools: tuple[str, ...]) -> list[str]:
    """Which of ``tools`` are unavailable to a shell recipe, probed INSIDE bash.

    ``shutil.which`` answers the wrong question on Windows: the gate's ``bash`` is WSL, so a
    recipe runs against WSL's PATH, not the Windows one. A Windows-side lookup therefore both
    skips suites that would have worked and would pass suites that cannot run. On Linux CI the
    two are equivalent. ``-lc`` so a login shell picks up ``~/.profile`` (hence ``~/.local/bin``).
    """
    bash = shutil.which("bash")
    if bash is None:
        return ["bash"]
    probe = "; ".join(f"command -v {t} >/dev/null 2>&1 || echo {t}" for t in tools)
    try:
        proc = subprocess.run(
            [bash, "-lc", probe], capture_output=True, text=True, timeout=60, check=False
        )
    except (subprocess.TimeoutExpired, OSError):
        return list(tools)
    return proc.stdout.split()


# --- suites ------------------------------------------------------------------------------


def suite_scripts(
    res: Result, label: str, directory: Path, cmd: list[str], env: dict[str, str], glob: str
) -> None:
    files = sorted(p for p in directory.glob(glob) if p.name != "osa.py")
    if not files:
        res.skip(label, f"no {glob} under {directory.relative_to(ROOT).as_posix()}")
        return
    for path in files:
        name = f"{label}/{path.name}"
        if err := header_trap(path):
            res.fail(name, err)
            continue
        ok, out = run([*cmd, path.name], path.parent, env)
        res.ok(name) if ok else res.fail(name, out)


def suite_sql(res: Result, env: dict[str, str]) -> None:
    directory = COOKBOOK / "sql"
    files = sorted(directory.glob("*.sql"))
    if not files:
        res.skip("sql", "no *.sql under cookbook/sql")
        return
    if not SQLITE.exists():
        res.skip("sql", f"{SQLITE.relative_to(ROOT).as_posix()} missing; run build_sqlite.py")
        return
    con = sqlite3.connect(f"file:{SQLITE.as_posix()}?mode=ro", uri=True)
    try:
        for path in files:
            name = f"sql/{path.name}"
            if err := header_trap(path):
                res.fail(name, err)
                continue
            try:
                asserts = parse_asserts(path)
                if not asserts:
                    res.fail(name, "no `-- @assert` block; every SQL recipe must assert")
                    continue
                body = strip_asserts(path.read_text(encoding="utf-8"))
                rows = run_sql(con, body)
                if not rows:
                    res.fail(name, "the demo query returned no rows")
                    continue
                bad = [d for d, q in asserts if not truthy(con, q)]
                if bad:
                    res.fail(name, "invariant failed: " + "; ".join(bad))
                    continue
            # `MalformedAssert` is ours. `sqlite3.Warning` is belt-and-braces: it is NOT a
            # subclass of `sqlite3.Error`, and although 3.11+ raises `ProgrammingError` (which IS
            # an Error) for a multi-statement `execute`, the DB-API permits Warning and it would
            # otherwise escape and crash the whole gate rather than failing one recipe.
            except (sqlite3.Error, sqlite3.Warning, MalformedAssert) as exc:
                res.fail(name, f"{type(exc).__name__}: {exc}")
                continue
            res.ok(f"{name} ({len(rows)} rows, {len(asserts)} invariants)")
    finally:
        con.close()


class MalformedAssert(Exception):
    """An ``@assert`` header with no query under it."""


def parse_asserts(path: Path) -> list[tuple[str, str]]:
    """Read ``-- @assert <description>`` blocks, each continued by ``-- | <sql>`` lines.

    A header with no ``-- | `` continuation RAISES rather than being skipped. Dropping it
    silently was the dangerous behaviour: a file with three asserts and one typo would run two,
    report "2 invariants", and pass -- the missing invariant invisible, because suite_sql only
    fails a file with ZERO asserts.
    """
    out: list[tuple[str, str]] = []
    desc: str | None = None
    query: list[str] = []

    def close(where: str) -> None:
        nonlocal desc, query
        if desc is None:
            return
        if not query:
            raise MalformedAssert(f"`@assert {desc}` has no `-- | <sql>` continuation ({where})")
        out.append((desc, "\n".join(query)))
        desc, query = None, []

    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        s = line.strip()
        if m := re.match(r"^--\s*@assert\s+(.+)$", s):
            close(f"before line {i}")
            desc, query = m.group(1).strip(), []
        elif desc is not None and (m := re.match(r"^--\s*\|\s?(.*)$", s)):
            query.append(m.group(1))
        elif desc is not None and query and s and not s.startswith("--"):
            close(f"line {i}")
    close("end of file")
    return out


def strip_asserts(sql: str) -> str:
    keep = [ln for ln in sql.splitlines() if not re.match(r"^\s*--\s*(@assert|\|)", ln)]
    return "\n".join(keep)


def run_sql(con: sqlite3.Connection, body: str) -> list[tuple]:
    """Execute every statement; return the rows of the last one that produced any."""
    rows: list[tuple] = []
    for stmt in split_statements(body):
        cur = con.execute(stmt)
        fetched = cur.fetchall()
        if fetched:
            rows = fetched
    return rows


def split_statements(body: str) -> list[str]:
    """Split on statement boundaries, not on every ``;``.

    A naive ``body.split(";")`` truncates any statement containing a semicolon inside a comment
    or a string literal, and does it silently -- the prefix still parses and still returns rows,
    so the recipe looks like it passed while having executed something else.
    ``sqlite3.complete_statement`` is the tokenizer-aware answer.
    """
    stmts, buf = [], ""
    for line in body.splitlines(keepends=True):
        buf += line
        if buf.strip() and sqlite3.complete_statement(buf):
            stmts.append(buf)
            buf = ""
    if buf.strip():
        stmts.append(buf)  # trailing statement with no terminating semicolon
    return [
        s for s in stmts
        if not all(ln.strip().startswith("--") or not ln.strip() for ln in s.splitlines())
    ]


def truthy(con: sqlite3.Connection, query: str) -> bool:
    rows = con.execute(query).fetchall()
    return len(rows) == 1 and len(rows[0]) == 1 and bool(rows[0][0])


def trap_failures(res: Result, label: str, paths: list[Path]) -> bool:
    """Report a missing ``TRAP:`` header for every path. True if any failed."""
    bad = False
    for path in paths:
        if err := header_trap(path):
            res.fail(f"{label}/{path.name}", err)
            bad = True
    return bad


def suite_ts(res: Result, env: dict[str, str]) -> None:
    directory = COOKBOOK / "ts"
    if not (directory / "package.json").exists():
        res.skip("ts", "no cookbook/ts/package.json")
        return
    # Resolve to the absolute path, never the bare name: on Windows npm is a `.CMD` shim, and
    # CreateProcess does not apply PATHEXT, so subprocess would raise WinError 2 for "npm" even
    # though which() found it. Linux is unaffected either way.
    npm = shutil.which("npm")
    if npm is None:
        res.skip("ts", "npm not on PATH")
        return
    # The TRAP rule is what keeps this collection from drifting back into "how to call fetch", so
    # it must apply to every suite -- npm/dotnet run opaque test binaries, so check the headers
    # here rather than leaving these two languages on author discipline alone. Every offender is
    # reported, not just the first: this runs before the expensive install, so stopping early
    # saves nothing and hides work.
    if trap_failures(res, "ts", sorted((directory / "src" / "recipes").glob("*.test.ts"))):
        return
    if not (directory / "node_modules").exists():
        install = "ci" if (directory / "package-lock.json").exists() else "install"
        ok, out = run(
            [npm, install, "--no-audit", "--no-fund"], directory, env, INSTALL_TIMEOUT
        )
        if not ok:
            res.fail("ts/npm-install", out)
            return
    ok, out = run([npm, "test", "--silent"], directory, env)
    res.ok("ts/npm-test") if ok else res.fail("ts/npm-test", out)


def suite_csharp(res: Result, env: dict[str, str]) -> None:
    projects = sorted((COOKBOOK / "csharp").glob("*.csproj"))
    if not projects:
        res.skip("csharp", "no cookbook/csharp/*.csproj")
        return
    dotnet = shutil.which("dotnet")
    if dotnet is None:
        res.skip("csharp", "dotnet not on PATH")
        return
    # Same reasoning as suite_ts. Restricted to hand-written sources: `Generated/` is codegen
    # output and `obj/`/`bin/` are build artifacts (the SDK emits its own .cs files there), none of
    # which is a recipe or will ever carry a TRAP line. Excluded by name rather than by relying on
    # glob being non-recursive, so the intent survives someone reaching for rglob.
    skip = {"Generated", "obj", "bin"}
    sources = [p for p in sorted((COOKBOOK / "csharp").rglob("*.cs"))
               if not skip & set(p.parts)]
    if trap_failures(res, "csharp", sources):
        return
    for proj in projects:
        ok, out = run(
            [dotnet, "run", "--project", proj.name, "-v", "quiet"],
            proj.parent,
            env,
            INSTALL_TIMEOUT,
        )
        res.ok(f"csharp/{proj.stem}") if ok else res.fail(f"csharp/{proj.stem}", out)


def suite_starters(res: Result, env: dict[str, str]) -> None:
    """Starter apps are real CLIs, so they gate through a canned ``--selftest`` scenario."""
    directory = COOKBOOK / "starters"
    entries = sorted(directory.glob("*/main.py"))
    if not entries:
        res.skip("starters", "no cookbook/starters/*/main.py")
        return
    for path in entries:
        name = f"starters/{path.parent.name}"
        if err := header_trap(path):
            res.fail(name, err)
            continue
        ok, out = run([sys.executable, "main.py", "--selftest"], path.parent, env)
        res.ok(name) if ok else res.fail(name, out)


def main() -> int:
    argv = sys.argv[1:]
    only = SUITES
    if "--only" in argv:
        only = tuple(s.strip() for s in argv[argv.index("--only") + 1].split(",") if s.strip())
        if unknown := set(only) - set(SUITES):
            print(f"unknown suite(s): {', '.join(sorted(unknown))}; known: {', '.join(SUITES)}")
            return 2

    if not COOKBOOK.exists():
        print("cookbook/ does not exist")
        return 1

    httpd = None
    if "--base" in argv:
        base = argv[argv.index("--base") + 1].rstrip("/")
    else:
        if not (DIST / "v1" / "meta.json").exists():
            print("dist/ is not built; run `python tools/build.py` first")
            return 1
        base, httpd = serve_dist()

    # PYTHONPATH so recipes and starters share cookbook/python/osa.py without a package install.
    #
    # WSLENV is load-bearing on Windows, not decoration: the gate's `bash` is WSL, and a Windows
    # environment variable does NOT reach a WSL process unless it is named in WSLENV. Without it
    # every shell recipe silently fell through to its own default and validated the LIVE PUBLISHED
    # SITE instead of the dist/ this gate just built and served -- so the suite passed while
    # saying nothing about the tree under test, and an unreachable local dist read as a pass.
    # `/u` passes the value through unchanged (no Win->Unix path translation, which would corrupt
    # a URL). Harmless on Linux CI, where the variable propagates normally.
    # Extended, never clobbered: a developer may already export WSLENV for their own tooling, and
    # replacing it would silently break whatever depended on it.
    wslenv = "OSA_BASE/u"
    if existing := os.environ.get("WSLENV"):
        names = [e for e in existing.split(":") if e and e.split("/")[0] != "OSA_BASE"]
        wslenv = ":".join([*names, wslenv])
    env = {
        **os.environ,
        "OSA_BASE": base,
        "WSLENV": wslenv,
        "PYTHONPATH": os.pathsep.join(
            [str(COOKBOOK / "python"), os.environ.get("PYTHONPATH", "")]
        ).rstrip(os.pathsep),
    }
    print(f"cookbook gate: OSA_BASE={base}")

    res = Result(strict="--strict" in argv)

    def ran(label: str, before: int) -> None:
        """Assert the suite actually talked to OUR server, not the published site.

        Only meaningful when we are serving; with an explicit --base the traffic is elsewhere
        by design. `sql` is exempt: it opens the SQLite artifact directly and makes no requests.
        """
        if httpd is None or label == "sql":
            return
        if next(REQUESTS) - before <= 1:
            res.fail(
                f"{label} (base honoured?)",
                f"the suite passed without fetching from {base}. It ignored OSA_BASE and "
                f"validated something else -- most likely the live published site.",
            )

    try:
        if "python" in only:
            print("python recipes")
            n = next(REQUESTS)
            suite_scripts(res, "python", COOKBOOK / "python", [sys.executable], env, "*.py")
            ran("python", n)
        if "starters" in only:
            print("starter apps")
            n = next(REQUESTS)
            suite_starters(res, env)
            ran("starters", n)
        if "sql" in only:
            print("sql recipes")
            suite_sql(res, env)
        if "shell" in only:
            print("shell recipes")
            missing = bash_tools_missing(("curl", "jq"))
            if missing:
                res.skip("shell", f"missing {', '.join(missing)}")
            else:
                # `-l` so a recipe sees exactly the PATH that bash_tools_missing() probed; a
                # plain `bash script.sh` sources no profile, so a user-local jq would be
                # detected and then not found.
                n = next(REQUESTS)
                suite_scripts(res, "shell", COOKBOOK / "shell", ["bash", "-l"], env, "*.sh")
                ran("shell", n)
        if "ts" in only:
            print("typescript")
            n = next(REQUESTS)
            suite_ts(res, env)
            ran("ts", n)
        if "csharp" in only:
            print("c#")
            n = next(REQUESTS)
            suite_csharp(res, env)
            ran("csharp", n)
    finally:
        if httpd is not None:
            httpd.shutdown()

    print(
        f"\n{len(res.passed)} passed, {len(res.failed)} failed, {len(res.skipped)} skipped"
    )
    for name, why in res.skipped:
        print(f"  SKIPPED {name}: {why}")
    if res.failed:
        for name, _ in res.failed:
            print(f"  FAILED  {name}")
        return 1
    if not res.passed:
        print("no recipes ran at all, which is not a pass")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
