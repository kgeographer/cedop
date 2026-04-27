    # EDOPS Band T Characterization Plan

*Draft — April 2026 (rev. 25 April 2026)*
*Companion to `data_exploration.md`; covers the period-queryable layers: eVolv2k v4, HYDE 3.5, LMR v2.1.*

> **Naming**: The band formerly designated "F" is renamed **Band T** (temporal). The defining property of these layers is that returned values depend on a date or window passed by the user, not just the location. T conveys that property in a way that reads intuitively for users approaching the API.

---

## Purpose

Tasks 1–6 characterized the static basin signature (Bands A–E) — variables stored as columns on `basin08`/`basin06` and returned as fixed attributes of a location. The remaining signature components are structurally different: their value depends on the time window the user passes. LMR returns a climate state at a date; eVolv2k returns events within a window; HYDE returns the human landscape at a slice. Characterizing these requires its own methodology — sampling rather than full-population statistics, temporal as well as spatial structure, and explicit attention to how the layer's response varies with the query parameters that drive it.

This document defines tasks 7–12, with explicit hand-offs to Claude Code for notebook implementation. Findings will continue to accumulate in `logs/exploration_log.md` under section headings paralleling the static-band tasks. The output is working knowledge for signature design and an empirical basis for the parameter rubric the prospectus calls for.

---

## Architectural Note: A Different Kind of Band

Bands A–E share a defining property: each variable has a single value per basin, computed once and stored. A query at any time returns the same value. The Band T layers don't behave that way. LMR returns a time series, queryable by year or window. eVolv2k returns an event subset, filtered by date range. HYDE returns a value at a snapped time slice. The user's date or window is part of the query, not a presentation choice on a fixed value.

This has direct implications for characterization:

The unit of analysis is not "a basin" but "a (location, time) point" or "(location, window)." Distributions are computed across samples of these joint inputs, not across the basin population.

The variance decomposition matters. For LMR temperature at a sample of locations across the full 1–2000 CE range, how much of the variance is geographic (different places have different climates) vs. temporal (climate changed)? The signature's content changes meaning depending on which dominates. This question doesn't arise for static bands.

Aggregation choices are part of the design, not a downstream concern. A 100-year window can be summarized as a mean, a trend, anomaly relative to a reference period, or quantiles. Each choice produces a different signature value with different interpretive load. The characterization phase needs to work through these choices empirically rather than commit to one in advance.

The API parameter space is larger. Query parameters will now need to include period start/end, aggregation method, and (for ensemble layers like LMR) ensemble handling. The rubric for which combinations to recommend per use case is itself a deliverable of this phase.

---

## Per-Layer Task Plan

The three layers are largely independent and can be developed in parallel. Recommended sequencing: **eVolv2k first** (smallest, simplest, builds workflow confidence), **HYDE second** (most design questions, most novel, freshly added), **LMR last** (deepest internally, benefits from understanding the volcanic forcing component first). Anthromes deferred to Task 12.

---

### eVolv2k v4

#### Task 7 — eVolv2k event distribution and aggregation design

The catalog is small (~256 events over 2,400 years) and its characterization is direct, but the aggregation design for time-window queries is the actual deliverable.

**Method**: Load the full event catalog. Compute frequency over time (events per century), VSSI distribution (mean, median, quantiles, max), latitude distribution, hemispheric asymmetry distribution. Identify the documented quiet periods (Roman ~100 BCE–200 CE, Medieval ~950–1100 CE) and active periods empirically. Cross-check coverage of canonical events from the historical record (Tambora 1815, Samalas 1257, Krakatoa 1883, the 1452/1453 Kuwae candidate, etc.).

**Substantive questions**:

For typical query window sizes (50, 100, 200 years), how often is the window empty? How often does it contain ≥1 major event (VSSI > some threshold)? This determines whether returning an event count is informative or whether most queries get null.

What aggregation summarizes the catalog content for a window most usefully — count, sum of VSSI, time since most recent major event, or all three? An honest characterization will probably indicate that there's no single right answer and that the API should expose multiple summaries.

For coastal vs. interior queries, does hemispheric asymmetry of an event matter for relevance? A southern-hemisphere event's climate effect is concentrated in the southern hemisphere; for a query about Kaifeng in 1000 CE, a southern-hemisphere eruption is mechanically less relevant than a northern one. Worth deciding whether to filter by hemispheric overlap with the query location, or to return all events and let the user weight.

**Artifact**: `notebooks/edop/explore/07_evolv2k_distribution.ipynb`. Catalog statistics. Empty-window analysis at three window sizes. Recommended aggregation summaries for the API. Note on hemispheric filtering.

---

### HYDE 3.5

#### Task 8 — HYDE per-epoch marginal distributions and temporal structure

Mirror the static-band Task 1 approach, but per-epoch rather than once-globally. The five starter variables (cropland, grazing_land, urban_area, population_density, total_rice) are the working set.

**Method**: Open the netCDFs via xarray. For each variable, at each of ~8 representative time slices (8000 BCE, 4000 BCE, 1000 BCE, 0 CE, 1000 CE, 1500 CE, 1900 CE, 2000 CE), compute the global distribution: mean, median, % zero, % null, skew, p95, p99. Plot histograms and the trajectory of these statistics over time.

**Substantive questions**:

What fraction of cells are zero at each epoch? In 8000 BCE this should be near 100%; by 2000 CE far less. The trajectory of the zero rate is itself a finding about the data — when does anthropogenic land use become a globally non-trivial signal?

How does the distribution shape evolve? Pre-agricultural cells are uniformly zero; modern cells are heavy-tailed (a few cells are nearly 100% cropland). This affects normalization choices for any cross-time aggregation.

How do the five variables correlate with each other within an epoch? Cropland and population are likely highly correlated in the modern era; less so deep in time when subsistence patterns were more diverse. The correlation structure itself is time-varying.

What's a defensible baseline period for "absence of significant anthropogenic modification" against which a query window's anthropogenic content can be reported as anomaly? 8000 BCE is too early for some regions; 4000 BCE is too late for others. May need region-specific.

**Artifact**: `notebooks/edop/explore/08_hyde_distributions.ipynb`. Per-variable, per-epoch summary table. Histogram gallery (5 variables × 8 epochs = 40 panels, or condensed). Within-epoch correlation matrices for the 5 variables, at 3–4 epochs. Note on baseline period choice.

---

#### Task 9 — HYDE basin aggregation and s/u characterization

The aggregation logic from HYDE's 5-arc-min cells to L8 sub-basins is its own design problem, and the s/u duality applied to HYDE variables is potentially the most analytically interesting thing the layer offers.

**Method**: Implement two aggregation rules: (1) area-weighted mean over cells intersecting each basin polygon, (2) centroid lookup (single-cell value at basin centroid). For a sample of ~500 basins spanning the size and latitude range, compute both at a recent epoch (2000 CE) and report the disagreement distribution. Then, for the same sample at multiple historical epochs, compute local (`s`) and upstream-network (`u`) values for each HYDE variable using the same `next_down` traversal that produces the static `u` columns.

**Substantive questions**:

For what fraction of basins do the two aggregation rules disagree by more than some threshold? If disagreement is concentrated in large, low-latitude basins, document the pattern and choose accordingly. If it's pervasive, area-weighted aggregation is the only defensible choice.

For HYDE variables, how does the s/u divergence distribution compare to the climate-variable divergences characterized in Task 3? Prediction: HYDE divergence is much wider, especially for early-civilization basins where the upstream catchment includes the agricultural heartland and the local basin is downstream periphery (the Ur configuration in Task F3.8). If this prediction holds, HYDE's s/u contribution is a more substantive signal than for climate.

How does the HYDE 2000 CE basin-aggregated value compare to the static BasinATLAS `cropland_extent` at the same basins? Cross-layer sanity check. Substantial disagreement is a finding about either layer.

**Artifact**: `notebooks/edop/explore/09_hyde_basin_aggregation.ipynb`. Aggregation-rule disagreement distribution. s/u divergence distributions per HYDE variable. Cross-layer comparison plot. A documented choice of aggregation rule with rationale.

---

### LMR v2.1

#### Task 10 — LMR temporal/spatial structure and grid behavior

Establish baseline structural facts about the dataset before any signature design.

**On the ensemble dimension**: LMR is a paleoclimate reanalysis — a hybrid of climate model dynamics and proxy data assimilation. The reconstruction is run 20 times with different random subsets of available proxies (and slightly different model prior states). Each of the 20 runs is one ensemble member. At any (location, year), querying LMR returns 20 plausible values, not one. The mean across members is the central estimate; the standard deviation across members is the reconstruction uncertainty — narrow when proxies are abundant and mutually consistent (modern centuries, well-sampled regions), wide when proxies are sparse or noisy (deeper time, far from proxy networks). **API design decision**: signatures will return ensemble mean + standard deviation per variable, not the full ensemble. Mean alone hides uncertainty that varies substantially with location and period; the full ensemble is heavy and only useful for advanced users who can request it via a separate parameter if needed.

**Method**: Open the LMR netCDF holdings; document grid (2°×2°, ~7,000 land cells globally), variables (PDSI, surface air temperature, precipitation rate, SLP), temporal coverage (1–2000 CE annual), ensemble dimension (20 members). For a sample of ~50 land grid cells distributed across major climate zones, plot the full 2,000-year time series for each variable — both ensemble mean and ensemble spread.

**Substantive questions**:

How much variance at a sample of locations is geographic vs. temporal? Compute the decomposition: total variance across (location × year) sample, partitioned into between-location and within-location-across-time. If geographic variance dominates strongly (likely for temperature), the signature's "what climate prevailed at time T" content is dominated by where rather than when, and a long-window mean is largely interchangeable with the static Band C value. If temporal variance is substantial (likely for PDSI), the time-dependence is the actual contribution.

How does the ensemble spread compare to the temporal variance at a single location? Given that the API will return mean + standard deviation, the practical question is the typical magnitude of the std relative to the signal at decadal scale, and how it varies with location and period. This characterizes how interpretable the standard-deviation field will be in practice — uniformly small (rarely informative) vs. variable (a real second dimension of the LMR signature).

How does the LMR ensemble-mean value, averaged over a recent reference window (say 1850–1900), compare to the static BasinATLAS Band C value (`temp_yr`, `precip_yr`) at the same location? Sanity check on the two layers' internal coherence — they should agree closely, since BasinATLAS Band C is roughly a contemporary climatology and LMR's late-period values should converge on the same.

**Artifact**: `notebooks/edop/explore/10_lmr_structure.ipynb`. Variance decomposition table. Time-series gallery for a sample of locations. Comparison scatter (LMR 1850–1900 vs. Band C). Documented choice of which variables warrant time-series exposure in the API and which are best summarized as window means. Ensemble std distribution across the geographic sample (characterizes how much the std field will vary in practice).

---

#### Task 11 — LMR period and event fingerprints

Test whether known historical climate periods and volcanic responses appear in the data as expected. This task spans LMR and eVolv2k and is a sanity check on both.

**On the test periods**: The two most-discussed anomalies in LMR's covered window are the **Medieval Climate Anomaly** (MCA, ~950–1250 CE; also called Medieval Warm Period) — a period of regional Northern-Hemisphere warming, most pronounced in Europe and parts of East Asia, coincident with Norse settlement of Greenland, English viticulture, and Northern Song / Northern European agricultural expansion — and the **Little Ice Age** (LIA, ~1300–1850 CE) — a multi-century NH cooling, glacial advance, harsh winters, recurrent crop failures. Both are heavily NH-biased; recent paleoclimate work has emphasized their regional rather than globally synchronous character. They are the natural sanity-check periods because a reconstruction that didn't show them at the right NH locations would be suspect.

**Method**: For a representative sample of ~30 locations (Mediterranean, East Asian, South Asian, European, North American, equatorial), extract LMR variables for documented periods: MCA (~950–1250 CE), LIA (~1300–1850 CE), 4.2k-event vicinity, late antique transition (~500–700 CE). Compare to the surrounding 2,000-year reference. Separately, for the largest eVolv2k events (e.g., Samalas 1257, Tambora 1815, the 1452 Kuwae candidate), extract LMR temperature in years 0, +1, +2, +3, +5 post-eruption at hemisphere-relevant locations.

**Substantive questions**:

Do MCA and LIA emerge as coherent, statistically detectable anomalies in the regions where the historical literature claims them? If not — or if they appear in different magnitudes than expected — that's a finding about LMR itself, not just about climate history.

For major volcanic events, is there a temperature drop signal at lag 0–3 years in the appropriate hemisphere? Magnitude relative to the eruption's VSSI? This is the cleanest available test of LMR's volcanic forcing response and bridges Tasks 7 and 10–11.

For users running historical-period queries, what's the recommended baseline window against which anomalies should be reported — the full 2,000-year mean, the surrounding 200 years, the pre-industrial 1700–1850?

**Artifact**: `notebooks/edop/explore/11_lmr_periods_volcanics.ipynb`. Tables of period anomalies per region. Composite volcanic-response curves. A short note recommending baseline-window conventions for the API.

---

### Anthromes (superseded)

#### Task 12 — ~~Anthromes categorical typology over time~~ *Superseded — see `docs/edop/classification_plan.md`*

The case for incorporating the Anthromes (Ellis et al.) classification as a Band T field was considered and rejected after analysis. Anthromes is informationally redundant with the continuous HYDE fields already in Band T, structurally brittle at class boundaries under HYDE's reconstruction uncertainty, temporally coarse (six time slices only in the DGG version), and conceptually in tension with EDOPS's process-aware framing.

In its place, `docs/edop/classification_plan.md` defines a data-driven per-band typology (Tasks 12–22) native to EDOPS, producing named cluster types from the signature's own variables rather than importing an external categorical scheme. The Band T analogue (Task 22, deferred) will use HYDE fields to produce an epoch-conditioned anthropogenic typology once the static-band typology methodology is stable.

No notebook artifact for this task.

---

## Cross-Layer Interaction Questions

These are not separate tasks but synthesis questions to consider once 7–11 are complete:

**LMR ↔ eVolv2k coupling**: Already partially addressed in Task 11. The systematic version is whether LMR's PDSI and temperature anomalies aggregate over the eVolv2k catalog in a way that recovers the major events. This is a methods-paper-quality finding either way.

**HYDE ↔ LMR coupling**: At long timescales, do regions of intensified HYDE land use correlate with LMR climate anomalies? The Yellow River deforestation argument from the prospectus is exactly this — anthropogenic landscape change as a partial driver of hydrological/climate signals. Hard to test rigorously but the data is there.

**Cross-layer query patterns**: For a typical historical query (say, "characterize Kaifeng in 1000 CE"), what's the joint output of all three Band T layers? Is the combined signature interpretable, or does it produce too many fields for a non-specialist user? This is a UI/narrative question more than an analytical one, but worth surfacing during characterization.

---

## Sampling Design and API Load

Band T characterization can't run over the full basin population the way Tasks 1–6 did. The cost is roughly O(basins × time slices × variables) for each layer. A working sample design:

**Geographic sample**: ~500 L8 basins, stratified by the Task 5 k-means clusters (oversampling small clusters for representation). Reused across all Band T tasks for cross-task comparability.

**Temporal sample**: 8 epochs for HYDE characterization (Task 8 list); for LMR, a 50-year-window sample at the same 8 dates plus the full continuous series at ~30 priority locations; for eVolv2k, the full catalog (small enough).

**Total characterization load**: tractable for a single overnight run if API responses are cached. The lightweight T-band summary mode (`?bands=T&detail=summary`) noted in `data_exploration.md` is a prerequisite — annual time series for 500 basins is too heavy for batch characterization.

This is also a finding-in-itself: the sample sizes that make characterization tractable are also the sample sizes that make user-facing batch operations (UC-4, UC-6) tractable. The numbers should be documented as practical guidance, not just methodological choices.

---

## API Guidance Implications

The characterization phase produces, as a deliverable, the parameter rubric the prospectus calls for. By the end of Tasks 7–11, the following questions should have empirically grounded answers:

For a UC-1 single-place query at a historical date, which Band T components add interpretable content and which add noise? Specifically: should annual LMR series be returned, or windowed means? Should the eVolv2k summary be present-by-default or opt-in? Should HYDE be returned for the query date, the query date minus a baseline, or both?

For UC-2 pairwise comparison, do Band T differences add comparison signal or do they swamp the static-band differences with temporal noise?

For UC-4 batch correspondence experiments, what window size around the documented occupation period of each cultural unit produces the best temporal match without prohibitive API load?

For UC-7 historical baseline queries explicitly, which Band T layers should be foregrounded vs. suppressed, and what does "pre-industrial baseline" mean operationally for each?

These don't need to be answered comprehensively before notebooks land — they're the questions characterization is in service of.

---

## What NOT to Do During Band T Characterization

**Don't tune Band T variable selection against a cultural-correspondence target.** Same guardrail as Phase 1. The temptation is stronger here because Band T is closer to where cultural questions live; the discipline is the same.

**Don't conflate the three layers' uncertainties.** LMR has ensemble spread that scales with reconstruction skill; eVolv2k has known coverage gaps and dating uncertainty for older events; HYDE has reconstruction uncertainty that grows rapidly back in time, especially before the radiocarbon-supported window. These are different kinds of uncertainty and need different treatment in characterization output.

**Don't generalize from individual sites before sample distributions are in hand.** The three exemplars (Timbuktu, Ur, Kaifeng) will be temptation cases for HYDE in particular; resist the same way as in Phase 1. Run the global-sample distributions first.

**Don't let HYDE's deep-past values feel more authoritative than they are.** Pre-CE HYDE values are reconstruction outputs, not measurements. Treat with appropriate epistemic humility in any characterization claim.

---

## Directory Conventions

Following Phase 1:

```
notebooks/edop/explore/
  07_evolv2k_distribution.ipynb
  08_hyde_distributions.ipynb
  09_hyde_basin_aggregation.ipynb
  10_lmr_structure.ipynb
  11_lmr_periods_volcanics.ipynb
  12_anthromes.ipynb              (superseded — see docs/edop/classification_plan.md)

output/edop/explore/
  07_*.csv  07_*.png
  ...

logs/exploration_log.md  (continuing from Task 6)
```

Each task entry in the log follows the existing convention: Date · Task · Method · Finding · Implication.

---

*Decisions taken in the 25 April revision: Band F → Band T; sequencing eVolv2k → HYDE → LMR; LMR signatures will expose ensemble mean + standard deviation per variable, with full-ensemble access available via opt-in parameter for advanced users; Anthromes added as deferred Task 12 with specifics TBD. Sample size of 500 geographic basins retained as working assumption pending review against actual notebook runtimes.*

*27 April revision: Task 12 (Anthromes) superseded. Anthromes rejected as informationally redundant with HYDE fields, temporally coarse (6 time steps), and brittle under reconstruction uncertainty. Replaced by data-driven per-band classification typology; see `docs/edop/classification_plan.md` (Tasks 12–22). Exploration phase (Tasks 1–11) closed.*