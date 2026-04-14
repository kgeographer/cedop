# WHG API Investigation — 2026-04-14

Investigation conducted for the purpose of filing well-informed issues with the WHG maintainer (Stephen Gadd). All tests run against `https://whgazetteer.org`. API schema retrieved from `/api/schema/?format=json`.

## Context: What WHG Is and How It Works

Understanding the system architecture is prerequisite to filing useful issues.

**The accessioning pipeline (dataset contributor path):**
1. Upload dataset (LPF or LP-TSV format; fclasses now required)
2. **Reconciling** — dataset records sent against the WHG index (13M+ Wikidata + GeoNames records) in two passes: Pass 1 (higher confidence), Pass 2 (broader/fuzzy)
3. **Human review** — curator reviews each candidate pass-by-pass, marking `closeMatch` or `no match`; confirmed matches add name variants, geometry, and LOD links to the record
4. **Published / Accessioning / Indexed** — enriched records enter the WHG graph and become searchable

**The `/reconcile` endpoint is a convenience geocoding tool**, not a dataset pipeline endpoint. Stephen built it for users who have place name references in texts and need geometry candidates — the OpenRefine use case. It returns raw pass-1/pass-2 candidates without the human review layer. The expectation is that the caller does their own triage.

**Wikidata in the index:** WHG ingested a select set of Wikidata records (not all of Wikidata). The value is the LOD bridge: a Wikidata match brings in linked GeoNames, LoC, VIAF identifiers and geometry the source dataset may lack. The cost is address-string pollution in search results (e.g. "34 Primrose Bank Road, Edinburgh" becomes a candidate when searching "Edinburgh"). This is a known tradeoff.

**fclasses and legacy records:** LPF 2 made fclasses required. Legacy records in the index that predate this requirement were assigned `["X"]` (unknown type) rather than left null. Clients should treat `["X"]` as a legitimate but unclassified record — not noise to filter. Records with `fclasses: []` (empty list) are Wikidata stubs without GeoNames classification and can be treated as lower-confidence candidates.

**Stephen's new indexing pipeline:** Stephen is designing an approach that generates high-quality candidates from a unified index (all of GeoNames, TGN, Wikidata places, and more), intended to obviate the need for the reconciliation step. Status as of April 2026: "don't hold your breath, it'll be a long while yet." Issues should be filed against the current system.

---

## Endpoints Confirmed

### `GET /suggest/entity`

| Parameter | Type | Notes |
|-----------|------|-------|
| `prefix` | string | Matched against names and alt_names |
| `limit` | integer | Max results (default 10) |
| `cursor` | integer | Pagination offset |
| `exact` | boolean | When true, matches only entries where prefix is a listed alt_name |
| `fclasses` | string | Comma-separated GeoNames classes: A, H, L, P, R, S, T |
| `countries` | string | Comma-separated ISO 3166-1 alpha-2 codes |
| `namespaces` | string | `whg`, `gn`, `tgn`, `wd`, `osm`, `pl`, etc. |
| `token` | string | Query parameter (not Bearer) |

### `POST /reconcile`

| Parameter | Type | Notes |
|-----------|------|-------|
| `query` | string | Free-text |
| `mode` | string | `exact`, `fuzzy`, `starts`, `in` (default: `fuzzy`) |
| `fclasses` | array/string | Same GeoNames classes |
| `countries` | array | ISO codes |
| `lat`, `lng`, `radius` | float | Circular spatial filter (km) |
| `bounds` | GeoJSON | Polygon spatial filter |
| `start`, `end` | integer | Temporal filter (negative = BCE) |
| `size` | integer | Max 1000 (default 100) |
| `dataset` | integer | Restrict to single dataset |

### `GET /entity/{entity_id}/api`

- `entity_id` format: `place:5424806` (WHG parent ID) or `place:gn:2449067` (child namespace ID)
- Token passed as `?token=` query param

---

## Issues Found

### Issue 1: `fclasses` filter uses AND-not-ANY semantics

**Problem:** Tombouctou (`place:5424806`) has `fclasses: ["P", "S"]`. Querying `fclasses=P` returns a US hamlet "Timbuktu" (`fclasses: ["P"]`) ahead of Tombouctou, because the filter requires exact set match, not "any class in common."

**Effect on CEDOP:** We cannot use `fclasses=P` to mean "populated places" — any historical city with dual classification (P+S is common) is excluded. We removed the fclasses filter entirely from our suggest call as a workaround.

**Expected behavior:** `fclasses=P` should return any entity that has P among its fclasses, not only entities whose fclasses set equals `{P}`.

---

### Issue 2: `period:` entities leak through all filters

**Problem:** Querying `prefix=Ur&fclasses=S&countries=IQ` returns PeriodO period entities (`period:`) at score=100 ahead of places. The `countries` and `fclasses` parameters are applied only to place-type entities; period entities pass through unconditionally.

**Effect on CEDOP:** We must filter client-side on `id.startsWith("place:")` to exclude period noise. This is a leaky abstraction — filters that the user expects to constrain entity type don't.

**Expected behavior:** Spatial and feature-class filters should not apply to period entities at all, OR there should be an explicit `entity_type=place` parameter.

---

### Issue 3: Ranking is opaque and not prominence-based

**Problem:** Top results almost always score 100 regardless of historical significance. Tombouctou (UNESCO WHS, 90,000 population) returns tied at score=100 with a Ghanaian village and a US hamlet. There is no documented ranking model, and no way to request "most historically significant" result first.

**Effect on CEDOP:** "Take top result" is unreliable for place-lookup UX. Edinburgh (Scotland) returns a US result first. Our workaround: present all candidates to the user and let them choose.

**Expected behavior:** Score should reflect some combination of string match quality + data richness (number of linked records, attestations, dataset coverage). A prominence-based tiebreaker would dramatically improve usability.

**Note:** The WHG UI itself ranks Midlothian first for "Edinburgh" because it knows the "Edinburgh" variant and has 5 linked records in the elastic index — the data for prominence ranking exists, it's just not exposed through the API.

---

### Issue 4: `/reconcile` returns child namespace IDs, not WHG parent IDs

**Problem:** Reconcile returns `place:gn:2449067`, `place:wd:Q9427` — source-namespace records — rather than WHG canonical parent IDs (`place:5424806`). Child-namespace entity records have sparse properties (no fclasses, no geometry in extend). Suggest returns WHG parent IDs.

**Effect on CEDOP:** We initially used reconcile+extend to get candidates with geometry; extend returned empty geometry for child IDs. This forced us to abandon the reconcile pipeline entirely and switch to suggest+entity instead, requiring N+1 HTTP calls per search.

**Expected behavior:** Reconcile should return WHG parent IDs (or offer a `return_canonical=true` option), consistent with the suggest endpoint. Or: extend should return geometry for child IDs.

---

### Issue 5: Temporal filter on `/reconcile` penalizes well-attested places

**Problem:** `reconcile(Ur, start=-3000, end=-2000)` returns `place:pl:912985` ("Ur(i)") at score=100 and `place:5774555` ("Ur", Tell al-Muqayyar, Iraq) at score=41. The score drop is unexplained. Likely cause: sparse `when` metadata coverage means most WHG entries lack temporal data, and the temporal filter penalizes (rather than simply filters) entries with no temporal data.

**Expected behavior:** Temporal filter should exclude temporally-incompatible entries, not penalize entries with no temporal metadata. An `undated=true` option exists but its interaction with scoring is undocumented.

---

### Issue 6: `fclasses=null` on research-contributed places causes silent filtering

**Problem:** Many WHG places from specialized research datasets have `fclasses: null` (e.g. Samarkand from a research dataset). Any client filtering on fclasses will silently drop these.

**Effect on CEDOP:** Our original workaround (skip null-fclasses entries) was too aggressive and dropped legitimate historical places. We now skip only entries with `fclasses: []` (empty list), which catches Wikidata-only stubs but preserves null-fclasses research entries.

**Expected behavior:** WHG should populate fclasses for research dataset places, or document which datasets lack fclasses so clients can handle appropriately.

---

### Issue 7: Broken documentation link in service manifest

**Problem:** `GET /reconcile` (service metadata) embeds a documentation URL: `/content/technical/apis.html#reconciliation-service-api`. This URL returns 404.

Also: `/api/overview/` and `/api/` return 404 despite being implied by the URL structure.

---

### Issue 8: Token exposed in service manifest

**Problem:** The reconcile service metadata response embeds the caller's token in full in the `suggest` service path URL. Any downstream tool consuming the service manifest (e.g. OpenRefine) receives the token in plain text in the response body.

---

## Our Current Workaround

`_whg_search_candidates()` in `app/api/routes.py`:
1. `GET /suggest/entity?prefix=X&exact=true&limit=5` — returns WHG parent IDs
2. Filter: keep only `id.startsWith("place:")` — excludes period entities
3. `GET /entity/{id}/api` for each candidate — gets geometry, fclasses, country codes
4. Filter: skip entries with `fclasses == []` (Wikidata stubs without GeoNames classification)
5. Return structured candidates to client for user selection

**Cost:** N+1 HTTP calls (1 suggest + up to 5 entity calls). Typical latency 3–6 seconds. A server-side "return only canonical place entities with geometry" flag would eliminate most of this.

---

## Issues to File (Priority Order)

**1. Suggest ranking: prominence data exists but isn't used**
The WHG GUI ranks by linked record count (Midlothian ranks first for "Edinburgh" because it has 5 linked records). The API does not expose this — all results score 100. Edinburgh of the Seven Seas (Tristan da Cunha) returns before Edinburgh, Scotland. Concrete ask: expose a `sort_by=linked_records` option, or use it as a tiebreaker by default.

**2. `fclasses` filter: ANY semantics vs. AND semantics**
`fclasses=P` returns only records whose fclasses set is exactly `{P}`. Tombouctou has `["P","S"]` and is excluded. Expected behavior: return any record that has P among its fclasses. Simple fix, high impact for historical place lookup where dual classification is common.

**3. `period:` entities bypass all filters**
Querying `prefix=Ur&fclasses=S&countries=IQ` returns PeriodO period entities (`period:...`) at score=100 ahead of places. Countries and fclasses filters don't apply to period-type entities. Needs either an `entity_type=place` parameter or period entities excluded from suggest/reconcile results by default.

**4. Reconcile returns child namespace IDs, not WHG canonical IDs**
`/reconcile` returns `place:gn:2449067` (child record); `/suggest/entity` returns `place:5424806` (WHG parent). The child ID has sparse properties and empty geometry in `/extend`. Callers who use both endpoints get incompatible ID spaces. Concrete ask: a `return_canonical=true` option on reconcile, or documentation that reconcile IDs cannot be used with entity/extend.

**Not filing (known tradeoffs):**
- Wikidata address-string pollution — accepted cost of the Wikidata ingestion decision
- Temporal filter scoring — sparse `when` metadata coverage is a data quality issue, not an API bug
- Broken documentation link — mention in passing but not a separate issue

---

## Test curl Commands

Note: plain `curl` is blocked with "Bot access denied". Requires Mozilla UA:
```
-A "Mozilla/5.0 (compatible; CEDOP/1.0; +https://cedop.kgeographer.org)"
```

### Edinburgh — suggest vs. reconcile comparison (run 2026-04-14)

**Suggest** top 3: (1) Edinburgh of the Seven Seas, SH — score 100; (2) Edinburg, US — score 100; (3) Dùn Èideann, GB (`place:gn:2650225`) — score 100. Scottish Edinburgh is third, behind a South Atlantic settlement and a US hamlet, all tied at 100.

**Reconcile** top 2: (1) Dùn Èideann, GB (`place:gn:2650225`) — score 100; (2) Edinburgh, TGN (`place:tgn:7019109`) — score 99, `match: true`. Scottish Edinburgh is first. Then three Wikidata address records ("7 John's Place, Leith, Edinburgh" etc.) at score 99.

Conclusion: **reconcile ranks better than suggest for Edinburgh** but pollutes with Wikidata address-string matches. Suggest has a ranking problem; reconcile has a noise problem.

```bash
# Basic suggest — Edinburgh
curl -s -A "Mozilla/5.0 (compatible; CEDOP/1.0; +https://cedop.kgeographer.org)" \
  "https://whgazetteer.org/suggest/entity?prefix=Edinburgh&limit=5&token=TOKEN" | python3 -m json.tool

# With country filter
curl -s "https://whgazetteer.org/suggest/entity?prefix=Edinburgh&limit=5&countries=GB&token=TOKEN" | python3 -m json.tool

# Timbuktu with fclasses=P (demonstrates AND bug)
curl -s "https://whgazetteer.org/suggest/entity?prefix=Timbuktu&fclasses=P&limit=5&token=TOKEN" | python3 -m json.tool

# Timbuktu with exact=true (correct result)
curl -s "https://whgazetteer.org/suggest/entity?prefix=Timbuktu&exact=true&limit=5&token=TOKEN" | python3 -m json.tool

# Ur with temporal filter via reconcile
curl -s -X POST "https://whgazetteer.org/reconcile" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"queries": {"q1": {"query": "Ur", "start": -3000, "end": -2000, "fclasses": ["S"], "countries": ["IQ"]}}}' | python3 -m json.tool

# Entity detail for Tombouctou
curl -s "https://whgazetteer.org/entity/place:5424806/api?token=TOKEN" | python3 -m json.tool
```
