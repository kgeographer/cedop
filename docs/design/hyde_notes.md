HYDE data design notes

** KG ?s in response to CC notebook findings **: 
- What happens when a request overlaps or spans time steps, e.g. 150-250?
- the cells cover ocean as well, can those be skipped if a table is row-per-call?
- a basin may enclose cells with very different values; that info loss seems very problemmatic. is there a way to preserve the detail that HYDE provides?
- what is meant by "land use anomaly fields"? why bring the analytic step of a baseline into the picture?

---

** Opus Response **
Good questions, all of them practical in a way that surfaces real design choices rather than just implementation details. Working through them in order.

**1. Time-step overlap and spanning.** The HYDE temporal grid is irregular: millennial in BCE, centennial 100–1700, decadal 1710–1950, annual after. A query window of 150–250 CE spans two HYDE slices (100 CE and 200 CE). Three reasonable response strategies:

*Snap to nearest.* Return the single HYDE slice closest to the window's midpoint. Simplest. For 150–250 CE midpoint = 200, return 200 CE. Wrong direction of error: pretends temporal precision the data doesn't support.

*Return all overlapping slices.* For 150–250 CE, return both 100 CE and 200 CE values, let the consumer interpolate or reason. More honest about the data's temporal granularity, but pushes work onto the consumer and inflates payload.

*Return interpolated value with bounds.* Linear-interpolate between the two bounding slices to get a single value at the window midpoint, but include the bounding slice values and dates in the response so the consumer can see what's behind the interpolation. This is the LMR-style mean+std treatment applied to HYDE: return the central estimate plus the source data that bounds it.

I'd argue for the third for the default API path, with the second available via a parameter for users doing serious historical work who don't want any interpolation in their data. Document explicitly in the API response what was done — a `temporal_method` field saying "interpolated_between_100CE_and_200CE" or "exact_match_200CE" so the consumer never has to wonder. The window-spanning case is a particular instance of the general truth that HYDE's temporal resolution is itself non-uniform, and the API response should make the underlying granularity visible rather than smoothing it away.

For longer windows that span many slices (a query for 1500–1900 CE spans 1500, 1600, 1700, 1710 onward decadally), the question shifts: is the user asking "what was the typical state across this window" or "how did the state change across this window"? Mean across slices answers the first; trajectory (return per-slice values) answers the second. This maps onto the same window-aggregation question that LMR has — mean, range, anomaly, trend — and the API design should expose the same set of options across both layers for consistency. A user querying a 400-year window for both LMR climate and HYDE land use should get the same kind of summary structure from each.

**2. Ocean cells.** Yes, easy and correct to skip. HYDE's ocean cells are NoData (-9999 on the ASCII grids; equivalent in NetCDF). For any basin-aggregation operation the masking is automatic if you handle NoData correctly: `xarray` respects fill values and `numpy` masked arrays propagate correctly through aggregation functions. The practical gotcha is making sure you're using `np.nanmean` rather than `np.mean`, or equivalent xarray methods that ignore NaN. Once that's in place, ocean cells contribute nothing to any computation.

The deeper version of this question: BasinATLAS itself is a terrestrial dataset. There are no L8 sub-basins where HYDE values would need to come from ocean cells, because HydroSHEDS basins don't extend offshore. Coastal basins by definition end at the coastline. The only edge case is when a basin polygon has been buffered (in the buffer-neighborhood option) to extend a few km past the coast — there a small fraction of the buffer might fall over ocean. Same masking approach handles it.

**3. Within-basin cell heterogeneity — the information-loss question.** This is the most important of your four questions. You're right that aggregating a basin's worth of HYDE cells to a single value loses real information, and the loss is asymmetric across regions in ways that matter.

For most temperate-zone L8 basins (~14 km characteristic, smaller than HYDE's ~9 km cell size), the issue is mild — the basin contains one or two cells, and the heterogeneity within the basin from HYDE's perspective is whatever the cell values happen to be. But for larger basins — high-latitude continental interior basins, Sahelian basins, Australian basins — a single basin can contain dozens of HYDE cells with substantially different values. A basin that spans an irrigated valley plus surrounding desert will average out to a middle cropland value that doesn't describe either the valley or the desert. That's the information loss you're flagging, and it's a real problem.

Several treatments, in increasing order of preserved detail:

*Mean only.* Current default. Simple, lossy.

*Mean + standard deviation.* Same architectural move as LMR. The std field tells the consumer "this basin contains substantial within-basin variation" without exposing the cell-level data. A high std for cropland in a basin means the basin contains both heavily-cropped and uncropped areas, which is qualitatively different from a uniformly moderate-cropping basin with the same mean. Cheap to compute, fits the existing signature shape.

*Mean + percentiles (e.g. p10, p50, p90).* More information than std for the same number of fields, and more interpretable. A basin with mean cropland 0.2 and (p10=0, p90=0.6) clearly contains both empty and heavily-cropped cells; a basin with mean 0.2 and (p10=0.15, p90=0.25) is uniformly low-cropland. For HYDE specifically, the percentile distribution is more informative than the std because HYDE's distributions are heavy-tailed and bimodal — a few cells with very high values can produce a misleading std.

*Cell-level distribution as a histogram.* Return the binned distribution of cell values within the basin (e.g. five bins). Most informative compact representation. Adds payload weight but bounded.

*Sub-basin clustering.* For polygon and large-basin queries, cluster the cells within the polygon into a small number of environmentally distinct sub-zones. Ruth's UC-5 already calls for this for polygon inputs ("optionally a clustering of intersecting basins into environmental sub-zones"); the same logic applies cell-level for large basins.

For the default API response, I'd recommend mean + std + a small number of percentiles (p10/p50/p90), packaged in a sub-object so it doesn't bloat the top-level signature. Something like:

```
"hyde_cropland": {
  "mean": 0.21,
  "std": 0.18,
  "p10": 0.0,
  "p50": 0.18,
  "p90": 0.52,
  "n_cells": 12,
  "epoch": "1000_CE"
}
```

The `n_cells` field is itself diagnostic — a basin with n_cells=1 has no within-basin heterogeneity to characterize, and the std/percentiles are degenerate. A basin with n_cells=40 has rich within-basin structure that the percentiles capture. Consumers can interrogate the structure when it matters and ignore it when it doesn't.

The cell-level histogram is worth holding in reserve as an opt-in field for advanced users (UC-5 polygon work especially), but probably overkill for default UC-1 queries.

This is the same architectural principle you've been applying throughout EDOPS: don't collapse, expose. The s/u duality is information-preserving rather than collapsing local and upstream into a single value. The mean+std for LMR is information-preserving rather than reporting only the mean. HYDE's within-basin heterogeneity gets the same treatment, and it's defensible as a methodological position rather than a quirk of one variable's handling.

**4. "Land-use anomaly fields" and why baselines.** This is fair to question, because the anomaly framing is doing work that needs justification and isn't always the right move.

The motivation in F8.7 was specifically about *interpretability for non-specialists*. A raw cropland value of 0.18 (km² of cropland per cell, or a fraction depending on units) means little to a historian who doesn't know what cropland fractions look like globally. A statement that "this location had 23× the global average pre-agricultural cropland presence at 1000 CE" is more interpretable, even if it requires a baseline convention. Anomalies make values comparable across locations and across times. They turn raw data into something a narrative layer (the LLM summary in UC-1) can actually phrase meaningfully.

But your push-back is legitimate. Three problems with anomalies:

*The baseline is global, the meaning is local.* As F8.7 itself acknowledges, a 1000 BCE baseline is "pre-agricultural" only globally — in Mesopotamia, 1000 BCE already had millennia of intensive agriculture. Comparing 1000 CE Mesopotamian cropland against the 1000 BCE *global* baseline is a defensible operation but produces a number that obscures rather than illuminates the local trajectory. A regional baseline would be more honest but introduces enormous complexity (define the regions, justify them, handle edges).

*Anomalies introduce an analytical step into descriptive data.* The signature is supposed to characterize what conditions held at a place at a time. Anomalies pre-process that into "how unusual is this relative to a reference state." That's interpretation, not description. A user who wants the raw value to do their own comparison may find anomalies actively unhelpful.

*They embed a particular research question into the API.* The anomaly framing assumes the user wants to know "how does this differ from a baseline," which is one possible question among many. A user asking "what kind of place is this" doesn't need anomalies; they need raw values. The anomaly is a layer of analysis that rightly belongs in the consumer's research code, not in the descriptive signature.

The cleanest position, I think: **return raw values by default; offer anomalies as opt-in.** The signature describes what was there. The user can compute anomalies against whatever baseline they want — global 1000 BCE, regional pre-agricultural, modern, the location's own pre-occupation state — using their research-question-appropriate reference. The API can expose a convenience anomaly field with a documented baseline as a parameter, but it shouldn't be the default representation. F8.7's "use 1000 BCE as the global baseline" stands as a sensible convention if anomalies are computed at all, but the more conservative architectural move is not to bake the analysis into the descriptive layer in the first place.

This is consistent with how Band C currently works. EDOPS doesn't return temperature anomalies from a pre-industrial baseline by default; it returns temperature values. If a user wants anomalies, they compute them. HYDE land-use should follow the same pattern. The narrative-layer LLM in UC-1 can do the comparison work (using the raw value plus its training-data sense of what 1000 CE cropland fractions typically look like) when it's useful, but the API itself stays descriptive.

This actually simplifies the F8.7 implementation question substantially. The implication isn't "implement a baseline convention in the API"; it's "document for the LLM narrative layer that 1000 BCE is a useful reference epoch for land-use intensity comparisons." That's a prompt-design note, not an API design commitment. Cleaner.

Worth saying explicitly: F8.7's recommendation as written would have introduced exactly the kind of API-level opinion-baking that EDOPS has otherwise been disciplined about avoiding. Your skepticism is well-placed and I think it argues for downgrading F8.7 from a default-API-behavior recommendation to a narrative-layer-guidance note.

============= ************ ============= ************============= ************============= ************

** KG ? **: 

now a more pragmatic question. the approach to implementing hyde data assumed by CC would be to compute for each basin at a level, e.g. L8, build an array of values for each time step. the result a table of 190k rows in the case of L8, 16k rows for L6.  this bakes in a mean across however many cells a basin encloses (overlaps?), baking in the info loss. This troubles me. I have seen so far that L6, with quite large basins may be more useful than 8, even though 8 is our default at the moment. to avoid this baked-in mean situation means a table with as many rows as there are land cells, with an array of values @ time. that is a lot of rows (2.2M to be exact). I have/had tables in postgres with that many and more (place records, e.g. are up to 2.6M). So I am inclined to do the latter, and let operations upon the sets of cells happen on the fly. am I off base?

---

** Opus response **
Not off base at all — you're applying a sound design instinct. The cell-level table is the right move, and the reasoning generalizes beyond just HYDE. Let me work through why and then surface a couple of practical wrinkles worth being aware of.

**The architectural principle first.** The basin-aggregated table bakes one specific aggregation (mean) at one specific basin level (L8) into a stored artifact. Every other question — different aggregation, different basin level, percentiles, sub-basin clustering, anomaly relative to a custom baseline, polygon queries that don't align with basin boundaries — has to be served either by precomputing additional tables (combinatorially expensive) or by punting back to the source data anyway. Storing at the lowest meaningful level of granularity (the cell) means you precompute once and all those questions become spatial queries, not data-pipeline questions. This is the same principle that makes BasinATLAS itself useful — the L8 sub-basin is the irreducible unit, and every coarser representation is derivable on demand.

**On the row count.** 2.2M rows is unremarkable in PostgreSQL/PostGIS terms. You've already worked at that scale with WHG places. With proper indexing (spatial GIST on the cell geometry, btree on time and on `cell_id`), queries that intersect a basin polygon against the cell table will run in milliseconds for typical L8 basins (1-50 cells per basin) and well under a second for the biggest basins (a few hundred cells). The dominant cost will be the time-series array for each cell — if you store all 128 epochs as a PostgreSQL array column, each row is moderately heavy but you read the whole trajectory in one fetch, which is usually what you want. If users typically query single epochs, a normalized `(cell_id, epoch, value)` long-form table is better and the row count balloons to ~280M, still tractable but with different performance characteristics.

The choice between wide (array column per row) and long (normalized epoch rows) depends on query pattern. UC-7 historical-baseline queries hit single epochs; UC-10 territorial trajectory queries hit ranges of epochs. I'd guess a wide-format storage with the time array as a PostgreSQL `real[]` column serves your use cases better — a single basin query fetches N rows (one per cell) and unpacks the arrays in application code or in PostgreSQL using `unnest`. The wide format is also the natural shape coming out of the netCDF, so the ETL is direct.

**On precomputation vs. on-the-fly.** A reasonable hybrid is to store cell-level data as the source of truth and *also* maintain a basin-aggregated cache table for the default mean+std+percentiles representation at L8 and L6. The cache is a materialized view or a derived table refreshed when the source updates (which for HYDE 3.5 is essentially never on production timescales). Default API queries hit the cache for performance; advanced queries (custom aggregation, polygon inputs, sub-basin clustering, time windows that span epochs) hit the cell-level table directly. This gives you the best of both — fast common-case latency, full flexibility when needed — at the cost of some additional complexity and storage. Worth doing, but not before you've measured whether the on-the-fly performance is actually a problem. PostGIS aggregating 50 cells through a basin polygon with a GIST-indexed intersection is not slow.

**One important wrinkle: cell identity across variables.** All five (now seven) HYDE variables share the same grid. Don't store seven copies of cell geometry. One cell table with `cell_id` and geometry, then one variable-time-array table per variable, joined on `cell_id`. Or — probably better — one wide variable table with all variables as separate array columns: `(cell_id, geom, cropland[], grazing[], pasture[], rangeland[], ...)`. Reads are denser, writes are simpler, schema changes when you add an eighth variable are easy. The cell table's geometry column is the expensive part to index and you only want one of those.

**On the polygon question.** This is where the cell-level approach pays its biggest dividend. UC-5 (polygon input — historical polities, study regions) and UC-10 (temporal polygon sequence — territorial expansion) are exactly the use cases where a basin-aggregated table fails. A user submits a Northern Song territorial polygon at 980 CE; that polygon doesn't align with basin boundaries; you need to aggregate HYDE values *over the polygon directly*, weighted by cell-polygon area intersection. With a cell table, this is a single PostGIS query: `ST_Intersection` of cell geometries with the input polygon, area-weighted aggregation in SQL. With a basin-aggregated table, you'd have to either (a) intersect basins with the polygon and propagate the basin means, or (b) abandon the cache and go back to cells anyway. The cell-level architecture is the only one that supports UC-5 and UC-10 cleanly.

**On L6 vs L8 and the "more useful" observation.** Your sense that L6 may be more useful than L8 in some cases is consistent with what F2 found — the variables behave more stably at L6, the noise from tiny basins diminishes, and for many use cases the broader regional characterization is more interpretable than the local sub-basin characterization. With a cell-level HYDE store, you can serve L6 and L8 from the same underlying data without pre-committing. Users can request HYDE values at L6 or L8 (or for arbitrary polygons) and the API does the basin-cell intersection at query time. The basin-level choice becomes a per-query parameter, not a storage decision.

This also means the static Band A–E columns and the cell-level Band T HYDE columns will sit at different levels of granularity in the database, which is fine — they get assembled at query time into the response signature. The architectural inconsistency is real but appropriate: BasinATLAS variables are intrinsically basin-level (they're computed and distributed at basin level by HydroSHEDS), while HYDE is intrinsically cell-level. Storing each at its native granularity preserves what each source actually knows.

**One thing to think through before committing.** The cell table can be queried with arbitrary polygons, but the cells themselves are fixed 5-arcmin grid cells regardless of latitude. That means cell area varies — a cell at 60°N is half the area of a cell at the equator. Any aggregation that means anything physical (total cropland km² in a basin, mean cropland fraction weighted by cell area) needs to know each cell's actual area. Two options: store cell area as a column in the cell table (cheap, ~9MB for 2.2M rows, computed once), or compute it on the fly with `ST_Area` on the geography type (more expensive per query, no storage). I'd store it. The HYDE data itself reports areas in km² already, so the cell-area column is mostly for proportional aggregations across cells of different sizes.

Also worth noting: HYDE's units differ across variables. Cropland is km² per cell; population_density is capita/km². Aggregations behave differently for the two. Sum across cells works for area variables; mean weighted by cell area works for density variables. The aggregation logic needs per-variable rules. Document this clearly in the schema.

**Bottom line.** The cell-level architecture is correct, the row count is fine, the on-the-fly aggregation will be fast enough with proper indexing, and it's the only way to support UC-5 and UC-10 honestly. The work to implement it is a one-time ETL (parse netCDFs, compute cell geometries, compute cell areas, populate the table) plus thoughtful indexing, after which everything else is SQL. Going through the basin-aggregated shortcut to save row count would lock in design decisions you've been working hard not to lock in. Trust your instinct here.