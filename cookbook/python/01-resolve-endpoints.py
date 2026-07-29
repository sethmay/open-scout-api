"""Discover the API from meta.json instead of hardcoding its host and paths.

TRAP: pasting `https://sethmay.github.io/open-scout-api` into your app. That host is
      explicitly provisional pre-1.0 and is expected to move; it is also the `$id` prefix of
      every schema, so a move invalidates hardcoded URLs and hand-written path constants at
      the same time. Assuming an endpoint exists is the same bug one level down: guessing
      `v1/current/positions.json` gets you a 404 handled as "no positions".
FIX:  read the base once from configuration, then resolve every path out of `v1/meta.json`,
      which is the machine-readable index of the whole surface. Ask meta whether an endpoint
      is published rather than discovering it by request failure.

This is recipe 01 because every other recipe depends on it: none of them names a URL.
"""

from osa import base, check, endpoint, get, meta

m = meta()

# `unofficial` is `const: true` and required by the published contract precisely so a consumer
# cannot read a subset of this document and lose the no-affiliation fact.
check(m["unofficial"] is True, "meta must assert unofficial")
check(m["base_url"].startswith("http"), "meta.base_url must be absolute")

# Templated endpoints are listed with their placeholders, e.g. `v1/councils/{id}.json`, so a
# consumer builds URLs from the published template instead of inventing a layout.
templated = [e for e in m["endpoints"] if "{" in e]
collections = [e for e in m["endpoints"] if "{" not in e]
check(templated and collections, "meta must publish both templated and collection endpoints")

# endpoint() raises rather than returning a URL the API does not serve: a consumer pinned to a
# withdrawn endpoint should fail once, loudly, not 404 on every request forever.
council_doc = endpoint("v1/councils/{id}.json")
one = get(council_doc.format(id="mississippi-riverlands"))
check(one["kind"] == "council", "a council document must declare kind=council")

# Every published file names its own contract, which is what makes codegen possible.
check(m["$schema"].endswith("published-meta.schema.json"), "meta must name its own contract")
for e in collections[:5]:
    check("$schema" in get(e), f"{e} must name its contract")

# The licensing carve-out travels with the discovery document, not just the README: requirement
# text is © Scouting America and is NOT under this dataset's CC BY-NC-SA license.
check("Scouting America" in m["text_rights"], "meta must carry the text_rights carve-out")

print(f"base            {base()}")
print(f"version         {m['version']} (generated {m['generated_at']})")
print(f"license         {m['license']}  (requirement text: see meta.text_rights)")
print(f"endpoints       {len(collections)} collections + {len(templated)} templated")
print(f"vocabularies    {len(m['vocab'])}")
print(f"datasets        {', '.join(f'{k}={v['total']}' for k, v in m['datasets'].items())}")
print(f"resolved        {council_doc} -> {one['versions'][0]['name']}")
