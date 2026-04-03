# EDOPS API — Design Requirements
*Draft — April 2026*

This document specifies behavioral requirements for the EDOPS API. It sits between the prospectus (what the service does and why) and the API parameter spec (what callers pass and receive). Audience: developers. It grows as design questions and use scenarios are resolved — each "what happens when...?" answer belongs here.

---

## Response Completeness

**REQ-01: Never silently degrade.**
If a requested parameter combination cannot be fully satisfied, the response must still be returned with the available data, and every unsatisfied component must be explicitly flagged. Returning nulls without explanation is not acceptable.

**REQ-02: Partial responses are valid; unexplained partial responses are not.**
A signature that omits temporal data because it is unavailable for the requested period is a correct response, provided the `coverage` block documents what was requested, what was available, and what fallback (if any) was applied.

**REQ-03: The `coverage` block is never omitted.**
Every signature response includes a `coverage` block documenting the data source and temporal basis for each component. Fields within `coverage` may be null when not yet implemented, but the block itself is always present.

---

## Temporal Parameter Behavior

**REQ-04: `period` controls band scoping in the near term.**
When a `period` parameter is supplied, Group D (Anthropocene markers) variables are suppressed for pre-industrial periods, and Group C variables are flagged as potentially anachronistic. Groups A and B are returned as contemporary baselines unless a matching temporal dataset is available.

**REQ-05: Fallback to contemporary baseline when temporal data is absent.**
If a `period` is requested and no matching temporal dataset covers the location, the service returns the contemporary baseline for affected variables with `"temporal_basis": "contemporary_baseline"` and `"period_requested"` set to the requested value. It does not return an error.

**REQ-06: Partial temporal coverage is reported field by field.**
If temporal data is available for some variables (e.g. volcanic forcing as a global signal) but not others (e.g. dendrochronology absent in the region), each variable's `coverage` entry reflects its own data source and temporal basis independently.

**REQ-07: PeriodO URIs are resolved server-side.**
A `period` supplied as a PeriodO URI is resolved to its ISO 8601 interval before processing. Both the original URI and the resolved interval are echoed in `meta.period` of the response.

---

## Coverage Transparency

**REQ-08: A coverage pre-check endpoint is available.**
`/api/coverage` (or `coverage_only=true` on any signature endpoint) returns only the `coverage` block for a given location and period, without computing the full signature. This allows callers to check data availability and set user expectations before requesting a full response.

**REQ-09: `fallbacks_applied` lists every substitution made.**
The `coverage.fallbacks_applied` array enumerates each case where a fallback was applied — e.g. `"pre_mm_yr: contemporary_baseline substituted for requested period 0900/1000 (no dendrochronology coverage at this location)"`.

---

## Neighborhood and Topology Edge Cases

**REQ-10: Endorheic basins are handled explicitly.**
For points falling in endorheic basins (no marine outlet), upstream traversal is suppressed and coastality fields are set to `null` with `"outlet_type": "endorheic"`. The response is not an error; it is a valid signature with a documented structural constraint.

**REQ-11: Unresolvable place names return a structured error.**
If a `name` parameter cannot be resolved via WHG, the response returns a structured error object (not an HTTP 500) with the unresolved name and suggested alternatives if available.

**REQ-12: Points near basin boundaries are flagged.**
If a point falls within a configurable distance threshold of a basin boundary (indicating MAUP sensitivity), the response includes a `neighborhood.boundary_proximity_warning` flag. The signature is still returned.

**REQ-13: Confluence and coastal edge cases are documented, not suppressed.**
Points identified as confluence cities, coastal settlements with small containing basins, or points spanning major basin divides are flagged in `neighborhood.edge_case` with a brief classification. These are informative signals, not errors.

---

## Response Formats

**REQ-14: `format=full` is the default and always includes the `coverage` block.**

**REQ-15: `format=compact` returns a flattened key-value structure.**
Nested s/u pairs are flattened to `pre_mm_yr_s`, `pre_mm_yr_u`, etc. The `coverage` block is omitted but available on request via `include_coverage=true`.

**REQ-16: `format=vector` returns only numeric fields as an ordered array.**
Field order is fixed and versioned. The vector is suitable for similarity computation. The `coverage` block is omitted.

---

## General

**REQ-17: Neighborhood parameters are echoed in every response.**
The `neighborhood` block of every response documents the exact parameters used to compute the signature (type, level, decay_lambda, radius_km as applicable), enabling reproducibility.

**REQ-18: API version is included in every response.**
`meta.version` reflects the service version at time of response, allowing callers to detect schema changes.
