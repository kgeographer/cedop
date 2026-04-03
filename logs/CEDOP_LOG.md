### CEDOP LOG
----
#### 03 Apr 2026
- **Design session**: developed EDOPS API and signature design artifacts in `docs/edop/`:
  - `signature_schema_draft.json` — dummy instance for Ur; full JSON structure including s/u/near_u tiers, coastality block, coverage block, period in meta
  - `api_spec_draft.md` — gestural parameter spec for 5 endpoints; `period` parameter (ISO 8601 interval or PeriodO URI) added as speculative later-phase feature
  - `api_requirements_draft.md` — behavioral requirements REQ-01 through REQ-18; coverage transparency, temporal fallback, and edge case handling
  - `prospectus_20260402.md` — editorial revision pass: reorganized to 9 sections, coastality subsection developed from `docs/coastality_v2.md` (decoupling thesis, Yaghan case), temporal depth subsection added naming Ruth's suggested historical climate datasets
- **PAGES 2k / LMR exploration**: investigated historical climate datasets suggested by Ruth Mostern
  - PAGES 2k v2.0.0 (2017): 692 georeferenced proxy records, Common Era, LiPD format — point records not gridded; exploration script at `scripts/edop/pages2k_explore.py`
  - Neukom 2019 NetCDF (`pages2k_ngeo19_recons.nc`): confirmed global mean only (dims: year × ensemble), not spatially resolved — not suitable for EDOP point queries
  - **Last Millennium Reanalysis v2.1** (Tardif et al. 2019): spatially gridded NetCDF, 91 lat × 180 lon (2°×2°), 2001 years × 20 MC ensemble runs; variables include `pdsi`, `air`, `prate`, `pr_wtr`, `sst`, `prmsl`
  - **POC extraction successful**: `pdsi` at Ur (30.0N, 46.0E), 900–1000 CE — mean PDSI ≈ 0 (slightly dry), range -1.02 to +0.87, ensemble spread ≈ 0.31; interpretable interannual variability
  - Key implementation note: LMRv2.1 time coordinates are `cftime.DatetimeNoLeap` objects — year extraction requires `t.year`, not direct integer comparison; lon convention is 0–358 (not ±180)
  - Scripts: `scripts/edop/lmr_extract.py` (download + point extraction, cftime-aware)
  - Installed: `xarray`, `netCDF4`; `requirements.txt` updated

#### 02 Apr 2026
- **ISHI meeting**: video call with Ruth Mostern (Pitt, director ISHI) and her group to discuss institutional support and potential hosting of EDOPS. Outcome: highly positive. Ruth offered a **$15k year-long contract** to advance EDOPS development, framing it as a second flagship initiative for ISHI alongside World Historical Gazetteer. Contract details to be worked out; prior WHG contract arrangements at Pitt provide the administrative template.
- **Research program status**: EDOPS is now a funded, institutionally-backed research program. First concrete deliverable: demonstrable tools and examples for a **symposium/advisory meeting planned for Fall 2026** (September/October). Ruth is identifying participants from Pitt environmental sciences and ecology, and from Princeton and Merced; aim is to constitute an informal advisory committee for EDOPS.
- **Ruth's research interests and suggested data sources**: as an environmental historian (most recent book: 1000-year history of the Yellow River) and Song Dynasty specialist, Ruth is specifically interested in EDOPS utility for historical periods. She named several global historical environmental datasets not yet considered for integration:
  - **Tree-ring climate reconstructions** (likely PAGES 2k or similar dendrochronology compilations)
  - **Ship log weather data** (likely CLIWOC or similar)
  - **Volcanic forcing records** (likely Sigl et al. ice-core derived series)
  - Integration approach and feasibility remain to be developed; these are time-series datasets with their own spatial resolution and uncertainty characteristics, structurally different from the static BasinATLAS baseline. They speak directly to the temporal mismatch problem (outline Section 7).
- **Design session (pre-meeting)**: developed `docs/edops_use_cases.md` — a structured use cases document establishing 10 UCs that drive service design requirements. Key conceptual outcomes:
  - Use cases precede and drive signature algorithm and API design, not the reverse
  - Neighborhood type is a first-class parameter of UC-1 (single-place profile), not a separate use case; upstream exposure is intrinsic to the basic signature
  - Coastality (`dist_sink`, outlet type) added as a first-class signature component — a distinct process geometry (what a place can reach downstream) complementing upstream exposure (what flows to a place)
  - Signature serialization: JSON document, not flat vector; similarity metrics derived from JSON field subsets at query time
  - UC-10 added: territorial expansion as environmental trajectory — temporal sequence of polygon signatures revealing environmental motivation or consequence of polity expansion (anchored by Northern Song 962–980 CE aridity example, which Ruth has previously found compelling)

#### 27 Feb 2026
- **Basin topology exploration** (`notebooks/edop/01_basin_topology.ipynb`, branch: `topology-explore`): sanity-checked `basin08` DAG structure; key findings:
  - DAG integrity confirmed: zero broken `next_down` links, all `next_sink` values valid
  - **Endorheic basins** (`endo != 0`, n=31,021) must be filtered from upstream traversal — they have `dist_sink=0` and contaminate distance calculations; `get_upstream_catchment()` now includes `WHERE endo=0`
  - **`dist_sink` as metric proxy**: after endorheic filter, Pearson r=0.994 between hop depth and metric flow distance — validates using `dist_sink` differences as a distance proxy without HydroRIVERS
  - **Point-to-basin matching**: naive containment (`ST_Covers`) finds wrong basin for 4/5 test cases (floodplain/delta fragments); `find_main_basin()` using max `up_area` within 0.25° radius is substantially better; added to helper functions
  - **`next_down` vs `next_sink`**: confirmed `next_down` is the traversal field; `next_sink` is a partition key only — corrects an error in outline Section 10
- **s/u variable audit** (Ur and Manaus compared): local/upstream duality is real and meaningful at Ur (aridity +320%, precip +175%, elevation +7525%) but near-zero at Manaus (precip +8%, aridity +5%) — divergence magnitude is itself an environmental characterization of position; Ur is a textbook alluvial dependency case, Manaus sits inside a homogeneous system
- **Weighting scheme comparison** (Ur): distance-decay weighting diverges substantially from flat/area-weighted for temperature (+24%) and precipitation (-63%); HydroATLAS pre-computed `_u` values match flat/area closely, confirming they carry no distance decay — the assumption EDOP is designed to relax
- **Direct hydrology variables**: `dis_m3_pyr` (natural discharge), `run_mm_syr` (runoff), `gwt_cm_sav` (groundwater depth) are already in the signature payload (Group B, `v_basin08_persist`). These are delivered/integrated measures — discharge at Ur is 991 m³/s despite 94mm/yr local precipitation. The `_u` climate counterparts are *not* yet in the payload; their addition would enable the s/u contrast that gives the delivered values their explanatory context.
- **LLM natural language summarization**: the s/u contrast is the key structured input that elevates LLM summaries from flat description to environmental interpretation. Without it: *"Ur has aridity index 5 and 94mm/yr precipitation."* With it: *"Ur sits in a hyper-arid local environment but is fed by a catchment receiving 258mm/yr — characteristic of alluvial civilizations dependent on distant water sources."* Adding upstream climate `_u` fields to the payload is a prerequisite for meaningful LLM summarization and should be treated as such in the implementation roadmap.

#### 26 Feb 2026
- **Goodchild consultation**: shared EDOP outline with PhD advisor Michael Goodchild (UCSB); his response reframed the central conceptual problem. Key points: scale is not just a MAUP issue but a question of *convolution functions* — the spatial extent of environmental influence on a place depends on the underlying process (water quality, air pollution, noise, social familiarity). Goes beyond Esri-style geographic enrichment (no distance) or the exposome literature (also no distance). Goodchild identifies "action-at-a-distance" as the core issue: different processes have different geometries and decay characteristics; GWR addresses this but conceptual underpinnings remain vague.
- **Outline revised to v3** (`pitches/EDOP_outline_v3.md`); key additions over v2 and the earlier PDF:
  - **Conceptual framing**: EDOP repositioned as *process-aware environmental characterization* — what a place experiences, not merely what surrounds it; explicit contrast with commercial enrichment tools
  - **Local/upstream duality**: `s`/`u` fields in HydroATLAS treated as a first-class architectural feature, not a data detail; divergence between local and upstream values is itself environmentally meaningful
  - **Distance-weighted upstream profiles** (Section 7, expanded): `next_sink` DAG traversal with topological depth as POC decay proxy; exponential decay `exp(-λ × depth)` preferred over inverse-depth; HydroRIVERS polylines as rigorous metric extension and independent signature dimension
  - **Process-type typology** (Section 7): hydrological (network-constrained), atmospheric (Euclidean directional), acoustic (rapid Euclidean decay), social/acquaintance (network-structured); hydrological designated first implementation
  - **Section 9 (new)**: Signature validation via settlement correspondence — historical settlement patterns (Reba et al. urban dataset, Cliopatria polities, D-PLACE societies) as external validation signal and objective function for parameter tuning; scale sensitivity and decay-parameter experiments become testable
  - **Section 10 (new)**: Drainage topology implementation — `next_sink` DAG, recursive CTE for upstream catchment retrieval, three neighborhood types (siblings, catchment, downstream corridor); spot-check on Tigris-Euphrates recommended before building aggregation logic
  - Scale sensitivity study across HydroATLAS levels designated as first paper contribution

#### 21 Feb 2026
- **Research direction**: `pitches/EDOP_outline_revised.pdf` submitted to ISHI group (Pitt) and PhD advisor Goodchild (UCSB) as pre-grant proposal framing EDOP as GIScience infrastructure. Outlines full design intent including area-based signatures, multi-scale basin evaluation (MAUP), spatial autocorrelation treatment, and temporal mismatch handling. Awaiting response before committing to next phase scope.
- **Cliopatria geometry analysis**: explored redundancy in `gaz.clio_polities` — 15,690 rows, 1,618 polities, only 11,864 globally distinct geometries (24% redundancy). Parenthesized names (97 distinct) largely co-exist with plain versions and likely represent different spatial readings of the same entity; deferred to Cliopatria team. Planned approach: distinct geometry table with FK, keyed by `MD5(ST_AsBinary(geom))`, reducing areal interpolation jobs by ~24%.
- **Basin cluster label fix**: hardcoded JS `CLUSTER_LABELS` were mismatched after Jan 2026 re-clustering. Fixed by adding `basin_cluster_labels` DB table, `populate_basin_cluster_labels.py` script, and updating `/api/basin-clusters` to return labels from DB. JS now uses API label with hardcoded map as fallback. (branch: `basins_fix`, merged to main)

#### 08 Feb 2026
- **Git cleanup**: expanded `.gitignore` for large data (`app/data/clio/`, `app/data/ich/`, `output/`), binary files, and lock files; removed `.DS_Store` and `__pycache__` from tracking
- **Repository reorganization commit**: moved `library/` → `articles/`, `docs/prospectus*` → `docs/cdop/`, removed old `prompts/`; added logos, Computing Place images, CDOP docs
- **Computing Place splash page**: new `index.html` landing page with project description and three module tiles (EDOP active, CDOP and Integrations disabled)
- Created `base_cedop.html` lightweight base template (no Leaflet/main.js); existing EDOP app moved to `edop.html` served at `/edop`
- Added `/about` page with architecture diagram
- Updated `base.html` EDOP header: logo links back to `/`, title updated to "EDOP | Computing Place"
- Updated FastAPI metadata from "EDOP Pilot" to "Computing Place"
- **Deployment**: DNS changed from `edop.kgeographer.org` to `cedop.kgeographer.org`; renamed database `edop` → `cedop`, working directory `/var/www/edop` → `/var/www/cedop`, systemd service `edop` → `cedop`; updated Apache vhost; enabled SSL via certbot
- Added `README.md` for GitHub repo with project description and logo
- **Polity-basin overlay script** (`scripts/edop/polity_basin_overlay.py`): areal interpolation demo
  - Queries Cliopatria temporal polity geometries, finds intersecting basin08 sub-basins
  - Computes area-weighted composite environmental signatures per time slice
  - Northern Song (962–980 CE): 3 territorial phases, 1407→2506→4217 basins
  - Generates static maps (aridity-colored basins within polity boundaries) and signature comparison chart
  - **Slide series mode**: fixed spatial extent (980 CE bbox) and shared color scale across 3 PNGs for slide animation showing expansion + environmental shift (precip 691→1117 mm/yr, aridity 64→102)
  - CSV export of polity signatures to `output/edop/polity_overlay/`
- **Discussion doc**: `docs/edop/polity_signature_distributions.md` — approaches for comparing polity environmental signatures as distributions rather than monolithic means (Wasserstein distance, summary statistics, point clouds, typological histograms over basin clusters); for discussion with ISHI and Seshat collaborators

#### 31 Jan 2026
- **ICH Corpus Update**: Extended UNESCO Intangible Cultural Heritage corpus from 730 to 865 elements
- Crawled UNESCO ICH website for 2024-2025 inscriptions (66 from 2024, 69 from 2025)
- Gap-fill check: identified 32 pre-2024 elements with newly available nomination docs
- Downloaded and extracted text from 167 new nomination documents
- LLM-cleaned documents using strict verbatim extraction prompts (preserved original text)
- Ran structured LLM extraction (Claude Sonnet) for practice_locations, diaspora_locations, environmental_features, coordinates
- **Consolidated extractions**: 733 total (72 tier_ab + 494 tier_cd + 167 tier_new) → `output/cdop/ich_extractions/consolidated_all.json`
- Scraped landing pages for concepts and country codes (135 new elements)
- Updated database: `ich_elements` and `ich_summaries` tables now include 2024-2025 data with ccodes and concepts
- **Scripts**: `ich_corpus_update.py`, `ich_clean_batch.py`, `ich_llm_extract_new.py`, `ich_consolidate_extractions.py`, `ich_load_new_elements.py`, `ich_scrape_concepts.py`

#### 29 Jan 2026
- **CEDOP restructuring**: reorganized repository to support future CDOP module
- new directory structure: `scripts/edop/`, `scripts/cdop/`, `scripts/shared/`; same pattern for `output/` and `sql/`
- created centralized `db_connect()` function in `scripts/shared/db_utils.py` and `app/db/connection.py`
- refactored `app/api/routes.py`: replaced 20+ inline `psycopg.connect()` calls with `db_connect()`
- updated User-Agent from `EDOP/1.0` to `CEDOP/1.0`
- default database name changed from `edop` to `cedop` in connection logic
- updated `CLAUDE.md` with new architecture documentation

#### 19 Jan 2026
- **pre-launch bug fixes** for v0.1 demo to Pitt collaborators
- fixed ecoregion geometry: removed non-existent `oneearth_slug` column from `/api/eco/geom` query
- fixed societies map: changed `L.layerGroup()` to `L.featureGroup()` for `getBounds()` support
- fixed societies zoom: replaced `fitBounds()` with `setView([20, 0], 1)` for fixed global view
- fixed WHG search ranking: changed `mode: "exact"` to `mode: "fuzzy"` — Denver CO now ranks first
- fixed WHG popover close button: added `sanitize: false` and `html: true` to popover options
- **societies loading spinner**: shows during 6-7s initial fetch, hides accordions until ready
- **variable description tooltips**: question mark icons on EA042/EA034 headers, hover shows D-PLACE descriptions
- added `variable_info` to `/api/societies` response with variable names and descriptions
- header styling: smaller About/API links, subtle badge (`bg-secondary rounded-pill`)

#### 18 Jan 2026
- integrated D-PLACE cultural database: 1,291 societies, 94 anthropological variables, 121k observations
- spatial join: added `basin_id`, `eco_id`, `bioregion_id` to `dplace_societies` (87% basin, 99% bioregion coverage)
- created correlation scripts: `dplace_env_correlations_signature.py` uses EDOP signature fields by band
- **key finding**: temperature explains 40% of variance in agriculture intensity; runoff explains 17% of domestic animal type
- excluded Band D (Anthropocene markers) as anachronistic for historical inquiry
- output: `output/dplace/correlations_signature_bands_ABC.csv`, `analysis_narrative_18Jan2026.md`
- **Societies tab UI**: new tab displaying 1,291 societies as map markers
- `/api/societies` endpoint returns societies with bioregion and EA042 subsistence data
- accordion-style subsistence filter (EA042): 7 categories with color-coded radio buttons
- markers colored by subsistence type; filtered view fades non-matching markers
- **top ecoregions by realm**: selecting subsistence filter shows top 3 ecoregions per realm in 2-column display
- API joins through OneEarth hierarchy (Bioregions2023 → Subrealm2023 → Realm2023) for proper realm names
- **basin clusters display**: toggle between "Ecoregions by realm" and "Basin clusters" views
- fixed cluster join bug: was using `basin08_pca_clusters` table instead of `basin08.cluster_id`
- **renamed cluster labels**: replaced geographic names with environmental descriptors
  - "High Andes" → "Cold high plateau", "Mediterranean" → "Warm semi-arid upland", etc.
  - labels now based on temperature/moisture/elevation, no geographic references
- **Religion query (EA034)**: second accordion for "High gods" with 4 categories
  - Absent (277), Otiose (258), Active not moral (42), Active supporting morality (198)
  - color gradient from light pink to dark red reflecting belief intensity
  - selecting religion resets subsistence filter and vice versa (one query active at a time)
- **environmental correlation**: societies with moralizing high gods have half the precipitation of those without

#### 17 Jan 2026
- created `scripts/summarize_ecoregion_text.py` — Claude Sonnet batch summarization of ecoregion Wikipedia text
- added `summary` column to `eco_wikitext` table; generated 821 summaries (150-200 words, geo/eco focus)
- added `/api/eco/wikitext?eco_id=X` endpoint returning summary and wiki_url
- redesigned ecoregion detail card: name + OneEarth/Wikipedia buttons + summary paragraph
- reordered realms list: priority realms (Subarctic America, North America, Eastern Eurasia) sorted to top with note about completeness

#### 16 Jan 2026
- overhauled Ecoregions tab UX: map now shows child features matching the list (not parent geometry)
- added 3 new geometry endpoints: `/api/eco/subrealms/geom`, `/api/eco/bioregions/geom`, `/api/eco/ecoregions/geom`
- created `displayEcoFeatures()` function with 10-color palette, tooltips, bidirectional hover highlighting
- wired up `gaz.bioregion_meta` table: bioregion list shows human-readable titles where available
- added OneEarth external links with icon indicators (Bootstrap Icons CDN)
- fixed nested `<a>` tag issue in bioregion list rendering (invalid HTML → `<span>` with onclick)
- **added click-to-drill-down on map features** — clicking a polygon triggers same navigation as clicking list item

#### 15 Jan 2026
- diagnosed Wikipedia extraction issue: MediaWiki's `exlimit` silently limits full-text extracts to 1 page per batch request
- fixed `scripts/refetch_wiki_extracts.py` to fetch one title at a time (0.2s delay, ~3 min for 847 titles)
- created `public.eco_wikitext` table with FK to `gaz."Ecoregions2017"`, full-text search index
- loaded 751/847 ecoregion Wikipedia extracts (88.5% initial coverage)
- created `scripts/triage_missing_ecoregions.py` for automated candidate discovery
- triaged 96 missing ecoregions: 7 strong matches, 19 partial, 45 redirects, 25 no match
- manual review of 71 candidates: accepted 66 full articles + 4 section extracts, rejected 1 false positive
- created `scripts/fetch_reviewed_extracts.py` to handle section extraction from broader articles
- **final result: 821/847 ecoregions with Wikipedia text (96.9% coverage)**

#### 11 Jan 2026
- created `docs/edop_database_schema.md` — comprehensive reference for all source and result tables to reduce context-building between Claude Code sessions
- implemented full 1565-dimensional basin clustering pipeline for all 190,675 basins:
  - `scripts/basin08_sparse_matrix.py`: extracts 27 numerical + 15 PNV + 1519 one-hot categorical features → sparse matrix (97.88% sparse, 13 MB)
  - `scripts/basin08_pca.py`: TruncatedSVD reduces to 150 components (86.2% variance)
  - `scripts/basin08_cluster_analysis.py`: tests k=5-50, analyzes silhouette/elbow/Calinski-Harabasz
  - `scripts/basin08_clustering_k20.py`: final k=20 clustering, creates `basin08_pca_clusters` table
- new table `basin08_pca_clusters` (190,675 rows): hybas_id → cluster_id based on full environmental signature
- cluster sizes range from 4,263 to 18,736 basins (reasonably balanced)
- cluster labeling via `scripts/basin08_cluster_labels.py`: analyzes centroids, biomes, WHC city membership
- created `output/basin08_cluster_labels_manual.json` — editable labels derived from biome + city analysis (e.g., "Mediterranean / Warm Temperate", "Tropical Coastal", "Arctic Tundra")
- output files in `output/`: sparse matrix, PCA products, cluster assignments/centroids/labels
- **PCA vs FAMD validation** (`scripts/basin08_famd_comparison.py`): 50k sample comparison shows moderate agreement (ARI=0.437, NMI=0.609, ~60% best-match). PCA acceptable for exploratory work; FAMD more defensible for rigorous analysis.
- note: exploratory work; clusters subject to revision based on downstream utility

#### 10 Jan 2026


#### 09 Jan 2026
- scaled up environmental analysis from 20 pilot sites to 258 World Heritage Cities (WHC)
- merged WHG reconciliation data into `wh_cities` table: 258 geometries added, 254 basin_ids assigned (4 island cities outside HydroATLAS coverage)
- created `whc_*` schema parallel to pilot `edop_*`: `whc_matrix` (254×893 features), `whc_pca_coords` (50 components), `whc_similarity` (32,131 pairs), `whc_clusters` (k=10)
- environmental clustering reveals meaningful groups: Mediterranean (49), Arid/desert (21), Northern Europe (15), High altitude (22), Central Europe temperate (55), East Asia monsoon (39), Tropical wet (26)
- persisted wiki/semantic data to database: `whc_band_summaries` (1,032 rows), `whc_band_clusters` (1,217), `whc_band_similarity` (12,170)
- added 3 new API endpoints: `/api/whc-cities`, `/api/whc-similar`, `/api/whc-similar-text`
- created **WHC Cities** tab in UI with grouped dropdown (by UNESCO region), dual similarity buttons, cluster badges
- Timbuktu validation: env-similar → Agadez, Khiva, Zabid (arid); text-similar → Agadez, Dakar, Marrakesh (West African cultural)

#### 07 Jan 2026
- scaled up Wikipedia text corpus pipeline from 20 pilot sites to 258 WHC cities
- used `wh_cities` database table as source; output to `output/corpus_258/` (file-only, no database)
- harvested 7,757 Wikipedia sections; average 3.7/4 bands mapped per city
- LLM summarization: 258 cities × 4 bands; ~$8.90 cost (1.3M input tokens, 329k output)
- generated OpenAI embeddings (`text-embedding-3-small`) with k=8 clustering
- text clusters show regional/cultural coherence: Northern European, Mediterranean, Hispanic World, South Asian, Lusophone, Central/Eastern European, Islamic/Arab, Mixed/Colonial
- high similarity pairs validate approach: Kutná Hora↔Český Krumlov, Quedlinburg↔Goslar, Arequipa↔Cusco
- completed WHG reconciliation for coordinates: uploaded LP-TSV to WHG, matched 258/258, exported geometry

#### 06 Jan 2026
- built Wikipedia corpus pipeline: harvest → band mapping → LLM summarization → embeddings
- created `scripts/corpus/` with `harvest_sections.py`, `summarize_bands.py`, `generate_band_embeddings.py`
- harvested 674 Wikipedia sections for 20 pilot sites via MediaWiki API
- developed semantic band mapping (history, environment, culture, modern) with aggressive pattern matching — 67% content coverage
- used Claude API to summarize each band per site into 150-300 word normalized summaries
- generated OpenAI embeddings (`text-embedding-3-small`) per band + composite; stored in new tables `edop_band_embeddings`, `edop_band_similarity`, `edop_band_clusters`
- correlation analysis: environment text band tracks physical environment (r=-0.19); history band shows no relationship (r=+0.01)
- text clustering reveals discourse types: European imperial (Vienna, Venice), trade routes (Timbuktu, Samarkand), indigenous monuments (Angkor, Cahokia)
- cluster agreement between text and environmental: 45% (vs 20% chance) — complementary signals, not redundant
- added `wiki_slug` column to `edop_wh_sites`; populated for 20 pilot sites

#### 05 Jan 2026
- created `scripts/generate_text_embeddings.py`: OpenAI embeddings from Wikipedia lead+history text
- new tables: `edop_text_embeddings`, `edop_text_similarity`, `edop_text_clusters` (k=5)
- text clusters show semantic coherence: natural parks, archaeological sites, European cities, trade routes, Chinese heritage
- key finding: only 1/20 sites shares nearest neighbor between environmental and text similarity — dimensions largely orthogonal
- added `/api/similar-text` endpoint mirroring `/api/similar`
- UI updated with dual buttons: "Similar (env)" and "Similar (semantic)" with dynamic headings/descriptions
- created `scripts/cliopatria_to_lpf.py`: transforms Seshat/Cliopatria polities GeoJSON to Linked Places Format (1,547 polities, 449 MB)
- removed `.env` from git tracking (API keys); pushed clean `embedding` branch

#### 04 Jan 2026 (w/ChatGPT)
- began integrating Wikipedia text as a second similarity signal for 20 exemplar World Heritage sites
- implemented `fetch_wikipedia_wh.py` using MediaWiki API (no HTML scraping); retrieves canonical title, pageid, URL, lead text
- added diagnostics showing large variance in lead length (≈30–550 words), making lead-only embeddings unreliable
- inventoried Wikipedia section structure via `action=parse&prop=sections`; stored section metadata as JSON
- found 16/20 sites include top-level “History*” sections (often “History” or “Historical overview”)
- implemented logic to retrieve history-like sections via section index and wikitext
- began constructing provisional documents as lead + history text; paused before embeddings to reason about normalization and truncation
- completed cleanup and normalization of Wikipedia-derived text; generated `wh_wikipedia_leads.tsv` suitable for text embeddings
- accepted residual variation in text length as reflective of WH site typology (ensemble vs city vs landscape); pipeline now ready for embedding-based similarity analysis- 

#### 04 Jan 2026 (w/Claude)
- exposed similarity analysis in web UI: cluster label badge displays on WH site selection (e.g., "Temperate Lowland Heritage")
- implemented "Most Similar" button with `/api/similar?id_no=<id>&limit=5` endpoint querying `edop_similarity` table
- color-coded similar sites: 5-color palette (ColorBrewer Set1) for map markers with matching swatches in ranked list
- map auto-zooms to fit source + all similar sites; same-cluster sites highlighted in green
- fixed description toggle bug: empty string display value was falsy, now uses `display = 'block'` with `=== 'none'` check
- modernized CSS: introduced custom properties (`--page-inline-padding: 1.5rem`) and logical properties (`padding-inline`, `padding-block`) for RTL-friendly layout
- work committed to `moregui` branch

#### 03 Jan 2026
- using Claude Code created persistence matrix for 20 WH sites: 1561 dimensions (27 numerical normalized, 9 categorical one-hot encoded [1519 total categories], 15 PNV share columns)
- new schema: `edop_norm_ranges`, `edop_wh_sites`, `edop_matrix` (20×1565)
- PCA analysis: 19 components, no dominant axis; PC1 (11.8%) temp/terrain, PC2 (10.6%) hydro/development, PC3 (8.7%) wetland
- persisted PCA products: `edop_pca_coords`, `edop_pca_variance`, `edop_similarity` (380 pairwise distances), `edop_clusters` (k=5)
- clustering reveals: temperate/urban (8 sites), extreme environments (3), high altitude (3), arid/warm (5), outlier Cahokia
- similarity queries now possible: e.g. sites most like Timbuktu → Göbekli Tepe, Uluru, Beijing, Samarkand

#### 02 Jan 2026
- gathered 47 attributes from `basins08` into a signature in 4 groups (A-D) in order of "peristence" as proposed by Gemini and agreed by committee (3 ots and KG). 
- new payload of all signature data to main UI page, rendered as a Summary (11 seleted fields, followed by 4 accordions for the groups
- relative elevation position within basin is now computed on the fly and part of payload.


#### 01 Jan 2026
- wired a "Resolve" button to WHG API endpoints (run a `/suggest/entity?` call, then an `/entity/{entity_id}/api` call with a resulting place id and it works nicely, ~1.8s
- index.html now with inputs for lon/lat or name, returning an "Environmental profile" (`signature` internally), and point feature on Leaflet map
- implemented World Heritage Site lookup for 20 varied locales on its own tab
- added point elevation from external sources (try OpenTopoData (mapzen) first, then Open-Meteo elevation API
- TODO: compute relative elevation position within the basin

```
Interpretation:
	•	~0.0 → near basin minimum (valley floor / lowlands)
	•	~1.0 → near basin maximum (ridge / highlands)
	•	~0.5 → mid-slope / plateau-ish
```

#### 31 Dec 2025
```
rsync -av --progress --partial \
  -e "ssh -i ~/.ssh/do_nov2016 -o ServerAliveInterval=1800" \
  basins_l08.gpkg \
  karlg@107.170.199.83:/home/karlg/xfer/
```
OR

```ssh edop-droplet
rsync -av --progress --partial basins_l08.gpkg edop-droplet:/home/karlg/xfer/
```
psql access: `on droplet: `sudo -u postgres psql`

```
sudo -u postgres ogr2ogr \
  -f PostgreSQL \
  PG:"dbname=edop user=postgres" \
  /tmp/basins_l08.gpkg \
  BasinATLAS_v10_lev08 \
  -nln basin08 \
  -lco GEOMETRY_NAME=geom \
  -lco FID=id \
  -lco SPATIAL_INDEX=GIST \
  -progress
```

#### 30 Dec 2025
- exported level 08 from BasinATLAS_v10.gdb as geopackage
  - `ogr2ogr -f GPKG basins_l08.gpkg BasinATLAS_v10.gdb BasinATLAS_v10_lev08`
- imported to local postgres db on :5435 __edop__ as __basin08__ table
- imported 3 of 11 'lookup' tables for codes in climate zones, climate strata, landcover fields: __lu_clz__, __lu_cls__, __lu_glc__.
- created view __v\_basin08\_basic__

```
select * FROM public.v_basin08_basic WHERE ST_Covers(
  geom, ST_SetSRID(ST_MakePoint(-3.00777252, 16.76618535), 4326)
) ORDER BY area_km2 ASC LIMIT 1;
```
- for Timbuktu:

```
{
	"zone_id" : 17,
	"zone_name" : "Extremely hot and xeric",
	"strata_id" : 124,
	"strata_code" : "Q5",
	"land_cover_id" : 14,
	"land_cover_name" : "Sparse herbaceous or sparse shrub cover",
	"pop_density" : 86.87200164794922,
	"elev_min" : 262,
	"elev_max" : 276,
	"runoff" : 18,
	"discharge_yr" : 0.7110000252723694,
	"geom" : "MULTIPOLYGON (((-3.2708333335914404 16.899999999600368,...)))
}
```

#### 29 Dec 2025
- settled on BasinAtlas as initial focus for data 
  - https://www.hydrosheds.org/products/hydrobasins
  - 299 fields; 12 hierarchical levels of spatial resolution
  - starting with level 08 (190675 rows)
  - license is CC-By 4.0
- ecoregions2017 has only __eco\_name__ available; download: [Ecoregions2017.zip](https://storage.googleapis.com/teow2016/Ecoregions2017.zip) (E. Dinerstein)
- OneEarth.org has nice landing pages for these, but licensing prevents hoped-for reuse in LLM schema induction. Map: [https://www.oneearth.org/navigator/](https://www.oneearth.org/navigator/); [Terms of use](https://www.oneearth.org/terms/)
- ecoregions are "areas of land containing a distinct set of natural communities and species, different from their nearest neighboring ecoregions"
- elevation data considered (future)
  - SRTM (Shuttle Radar Topography Mission): 30m (1 arc-second) global
  - NASADEM (30m): improved SRTM
  - Copernicus DEM (GLO-30 / GLO-90)


