# EDOPS API — Draft Parameter Specification
*April 2026 — gestural design artifact, not an implementation spec*

Base URL: `https://cedop.kgeographer.org/api`

---

## `GET /api/signature`
*Environmental signature for a point location*

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `lat` | float | — | Required if no `name` |
| `lon` | float | — | Required if no `name` |
| `name` | string | — | Place name; resolved via WHG API |
| `neighborhood` | string | `basin` | `basin` \| `buffer` \| `upstream` \| `three_tier` |
| `level` | int | `8` | HydroATLAS Pfafstetter level: `8` or `10` |
| `radius_km` | float | — | Required if `neighborhood=buffer` |
| `decay_lambda` | float | `0.3` | Decay parameter for upstream weighting; range 0–1 |
| `bands` | string | `all` | `A` \| `B` \| `C` \| `D` \| `all`; comma-separated for subset |
| `period` | string | — | ISO 8601 interval (`0900/1000`, `-3000/-2500`) or PeriodO URI; controls band scoping now, will inform temporal dataset selection in later phases |
| `narrative` | bool | `false` | Include LLM-generated natural language summary |
| `format` | string | `full` | `full` \| `compact` \| `vector` |

---

## `POST /api/signature`
*Environmental signature for a polygon (area-based units)*

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `geom` | string | — | WKT polygon geometry (EPSG:4326) |
| `level` | int | `8` | HydroATLAS level for intersecting basins |
| `bands` | string | `all` | Same as point endpoint |
| `period` | string | — | ISO 8601 interval or PeriodO URI; same semantics as point endpoint |
| `aggregation` | string | `distribution` | `distribution` \| `mean` \| `zones` |
| `narrative` | bool | `false` | |
| `format` | string | `full` | |

---

## `POST /api/trajectory`
*Signature sequence for a polity across time slices (polygon series)*

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `geoms` | array | — | Array of WKT polygons, one per time slice |
| `dates` | array | — | Array of years (CE) corresponding to each geometry; alternative to `period` |
| `period` | string | — | PeriodO URI resolving to a named historical period; alternative to `dates` array |
| `variable` | string | — | Variable to track, e.g. `ari_ix`, `pre_mm_yr` |
| `bands` | string | `B` | |
| `aggregation` | string | `distribution` | |

---

## `GET /api/similar`
*Places with most similar signatures to a query location*

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `lat` | float | — | |
| `lon` | float | — | |
| `name` | string | — | |
| `corpus` | string | `reba` | `reba` \| `dplace` \| `whg` \| `basins` |
| `n` | int | `10` | Number of results |
| `bands` | string | `B` | Variables used for similarity |
| `neighborhood` | string | `basin` | Applied to query point |

---

## `GET /api/compare`
*Side-by-side signatures for two or more locations*

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `locations` | string | — | Comma-separated `lat,lon` pairs or place names |
| `bands` | string | `all` | |
| `neighborhood` | string | `basin` | Applied uniformly to all locations |
| `narrative` | bool | `false` | Per-location and contrast summaries |

---

## `GET /api/health`
*Service status check — no parameters*

---

## Notes

- All responses are JSON. Content type: `application/json`.
- `format=compact` returns a flattened key-value structure suitable for tabular use.
- `format=vector` returns only the numeric fields as an ordered array, for similarity computation.
- Endpoints marked with `[*]` in the prospectus are listed here for design completeness; implementation is pending.
- Neighborhood parameters (`level`, `decay_lambda`, `radius_km`) are echoed back in the response `neighborhood` block for reproducibility.
