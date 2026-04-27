# EDOPS Data Sources — Primary Literature and Qualifications

## Epistemological framing

EDOPS assembles an environmental signature from several large-scale reconstructed and modeled datasets. None of these datasets are neutral measurements. Each is a constructed argument — built from methodological choices about what to model, what proxies to trust, how to handle gaps, and how to aggregate across space and time. The visual and numerical authority that a signature value projects to a user is not a property of the underlying data; it is an artifact of presentation.

DH researchers in particular are at risk of treating quantitative data as authoritative in ways they would never extend to a textual source. A medieval chronicle gets interrogated — who wrote it, for whom, under what constraints. A CSV from PANGAEA tends to get ingested. EDOPS documentation should resist this asymmetry by surfacing qualifications from the dataset authors themselves, not as fine print but as first-class context.

The development of the EDOPS signature is a scientific experiment in GISci. Its efficacy for specific historical use cases is to be determined, not assumed. Some aspects of the signature will prove solidly useful; others may require an entire salt shaker, not a grain. Users should understand this going in.

---

## Confidence tiers

A rough framework for how much interpretive weight to place on different components:

| Tier | Type | Examples | Caveat |
|---|---|---|---|
| 1 | Measured, contemporary | Basin geometry (area, elevation, slope) | SRTM-derived; errors bounded and documented |
| 2 | Modeled, recent | Band B hydrology, Band C climate | Calibrated to instrumental record; contemporary data silently returned for ancient queries |
| 3 | Reconstructed, temporal | LMR anomalies (Band T) | Proxy-density dependent; geographically biased; anomalies not absolute values |
| 4 | Modeled, ancient | HYDE BCE land use (Band T) | Reconstruction under high uncertainty; treat as hypothesis-generating, not evidentiary |

---

## LMR v2.1 — Last Millennium Reanalysis

### Primary papers

**Tardif, R., Hakim, G.J., Perkins, W.A., Horlick, K.A., Erb, M.P., Emile-Geay, J., Anderson, D.M., Steig, E.J., and Noone, D. (2019)**
"Last Millennium Reanalysis with an expanded proxy database and seasonal proxy modeling."
*Climate of the Past*, 15, 1251–1273.
→ **Confidence: high.** This is the v2.1 methodology paper. Read for proxy database composition, ensemble construction, and documented limitations.

**Hakim, G.J., Emile-Geay, J., Steig, E.J., Noone, D., Anderson, D.M., Tardif, R., Steiger, N., and Perkins, W.A. (2016)**
"The last millennium climate reanalysis project: Framework and first results."
*Journal of Geophysical Research: Atmospheres*, 121, 6745–6764.
→ **Confidence: high.** Original LMR framework. Useful for understanding the particle filter / data assimilation methodology and its assumptions.

### Known qualifications (from exploration findings F10.1–F10.5, F11.1–F11.6)

- **Values are anomalies, not absolute climate.** LMR returns departures from a model climatology prior. The prior is not zero; the anomaly is not temperature. Label clearly in any API output; never imply absolute values.
- **Funnel/regression-to-prior effect.** Reconstruction amplitude is suppressed before ~700 CE due to sparse proxies. The grand mean stays near zero in early centuries not because climate was stable, but because the reconstruction lacks power. Reliable window is approximately 700–1900 CE.
- **Proxy network is geographically biased.** Coverage is densest in Europe and North America (tree rings, ice cores, documentary records). East Asia, South Asia, Africa, and the Southern Hemisphere are systematically underrepresented. A query for medieval China returns a less well-constrained reconstruction than a query for medieval France — not because Chinese climate was less variable, but because fewer East Asian proxies have been incorporated. This must be disclosed explicitly, not buried.
- **2°×2° spatial resolution (~200 km).** Multiple adjacent L8 basins return identical values. LMR characterises regional climate states, not local conditions.
- **Volcanic forcing is attenuated.** LMR's model prior has no volcanic forcing. The volcanic signal must emerge entirely from proxy assimilation and is detectable at basin level only for Samalas-class events (>~50 Tg). Do not use LMR temperature to confirm or deny eVolv2k volcanic events.
- **Within-run spread is the recommended uncertainty field** but does not capture geographic proxy density variation. A qualitative disclosure by region is also needed.

---

## HYDE 3.x — History Database of the Global Environment

### Primary papers

**Klein Goldewijk, K., Beusen, A., Van Drecht, G., and De Vos, M. (2011)**
"The HYDE 3.1 spatially explicit database of human-induced global land-use change over the past 12,000 years."
*Global Ecology and Biogeography*, 20, 73–86.
→ **Confidence: high.** Foundational methodology paper. Read for reconstruction approach, uncertainty discussion, and the role of population estimates as the primary driver.

**Klein Goldewijk, K., Beusen, A., Doelman, J., and Stehfest, E. (2017)**
"Anthropogenic land use estimates for the Holocene: HYDE 3.2."
*Earth System Science Data*, 9, 927–953.
→ **Confidence: high.** ESSD data papers include explicit uncertainty sections. This is the version to read for temporal coverage and reconstruction caveats.

**HYDE 3.3 / 3.4**: May be incremental data releases on PANGAEA rather than new journal papers. Check PANGAEA and the PBL Netherlands Environmental Assessment Agency directly for the authoritative dataset DOI and associated documentation.
→ **Confidence: uncertain on exact version/citation.** Verify before citing.

### Known qualifications (from exploration findings F8.x, F9.x)

- **BCE values are model reconstructions, not measurements.** Pre-CE HYDE values are estimated from population reconstructions and land-use models. Uncertainty grows rapidly going back in time. The further from the instrumental/documentary record, the more these are best understood as modeled scenarios rather than historical ground truth.
- **HYDE pre-populates all habitable cells.** Population density shows a near-constant zero-fraction across all epochs — this is a model artifact, not empirical history. HYDE assumes all habitable land was inhabited at some level even in deep prehistory.
- **Spatial allocation uncertainty.** HYDE and EarthStat agree globally (~15M km² cropland) but diverge substantially at the sub-basin scale. The Ur example (60% EarthStat vs 18% HYDE cropland fraction at 2000 CE) illustrates spatial allocation uncertainty in agricultural hotspots, not calibration error. Do not treat sub-basin HYDE values as precise.
- **1000 BCE is the defensible baseline** for anomaly reporting. Ratios are interpretable (2.8×–23× for cropland) from this point. Earlier baselines produce unstable ratios.
- **Grazing land more extensive than cropland** at all epochs; emerges earliest. Colonial-era pastoral transformation drives the expansion signal more than industrialization.
- **Urban area and total rice near-zero globally** — not useful as default Band T fields; treat as opt-in.

---

## BasinATLAS / HydroATLAS / HydroSHEDS

### Primary papers

**Linke, S., Lehner, B., Ouellet Dallaire, C., Wilby, J., Grill, G., Tockner, K., Internationaletal. (2019)**
"Global hydro-environmental sub-basin and river reach characteristics at high spatial resolution."
*Scientific Data*, 6, 283.
→ **Confidence: high.** This is the HydroATLAS / BasinATLAS paper. The technical documentation (separate PDF) is extensive and contains variable-specific caveats — read both.

**Lehner, B., Verdin, K., and Jarvis, A. (2008)**
"New global hydrography derived from spaceborne elevation data."
*Eos*, 89(10), 93–94.
→ **Confidence: high.** Original HydroSHEDS paper (SRTM-derived hydrography).

**Lehner, B. and Grill, G. (2013)**
"Global river hydrography and network routing: Baseline data and new approaches to study the world's large river systems."
*Hydrological Processes*, 27, 2171–2186.
→ **Confidence: moderate.** HydroSHEDS update and expanded methodology.

### Known qualifications

- **All BasinATLAS variables are static and contemporary.** There is no temporal dimension in Bands A–E. A query for a Neolithic site in Mesopotamia returns exactly the same basin topology, climate, and land cover values as a query for the same location today. Band C (WorldClim) is contemporary climatology; it is silently wrong for any historical query. This is possibly the most consequential limitation for DH users and must be disclosed prominently.
- **`_u` (upstream) values assume present-day drainage topology**, not historical. Where rivers have been substantially redirected, dammed, or altered, the upstream characterisation reflects the modern system.
- **Temperature fields stored as °C × 10** — divide by 10 for display. API handles this; noting for documentation completeness.
- **Endorheic basins** (`endo != 0`, n=31,021) behave differently in upstream traversal — `dist_sink=0` and no ocean outlet. Documented in the HydroSHEDS technical specifications.

---

## eVolv2k v4 — Volcanic stratospheric sulfur injections

### Primary papers

**Toohey, M. and Sigl, M. (2017)**
"Volcanic stratospheric sulfur injections and aerosol optical depth from 500 BCE to 1900 CE."
*Earth System Science Data*, 9, 809–831.
→ **Confidence: high.** This is the v3 methodology paper and the most thorough documentation of the catalog's construction, uncertainty, and coverage gaps.

**eVolv2k v4**: The exploration notebooks cite "Sigl & Toohey 2024, PANGAEA." This may be a PANGAEA dataset record (with a DOI) rather than a peer-reviewed journal paper, or a 2024 paper outside current knowledge. Check PANGAEA directly for the v4 dataset and its associated documentation before citing.
→ **Confidence: uncertain on v4 citation.** The v3 Toohey & Sigl (2017) paper remains the foundational methodological reference regardless.

### Known qualifications (from exploration findings F7.x, F11.3–F11.4)

- **Catalog is NH-biased by construction.** Ice core records from Greenland and Antarctica are the primary data source; NH eruptions are better represented than SH. Hemispheric asymmetry is returned as a per-event field only; do not filter events by hemisphere for global queries.
- **Coverage gaps before ~500 BCE and after ~1900 CE.** The LMR window (0–1998 CE) is the operational range. eVolv2k extends to ~500 BCE but with decreasing reliability.
- **VSSI uncertainty grows with event age.** Older events have wider uncertainty on the sulfur injection estimate. Dating uncertainty for some events is ±several years.
- **5 Tg is the confirmed operational threshold** for EDOP API defaults. 10 Tg would exclude Krakatoa and Kuwae. At 5 Tg + 100yr window, 96.8% of query windows contain ≥1 event.
- **LMR cannot corroborate eVolv2k.** LMR temperature is not a reliable proxy for volcanic forcing below ~50 Tg at basin or hemisphere scale. The two datasets are complementary and independent; do not use one to validate the other. Pinatubo (1991, ~20 Tg → ~0.5°C global cooling) is the empirically grounded calibration reference for communicating volcanic magnitude to non-specialists.

---

## Anthromes — Anthropogenic Biomes (Ellis et al.)

The Anthromes layer in HYDE is the Ellis et al. classification applied to HYDE's gridded land use and population data. The lineage has three papers covering progressively longer temporal spans.

### Primary papers

**Ellis, E.C. and Ramankutty, N. (2008)**
"Putting people in the map: anthropogenic biomes of the world."
*Frontiers in Ecology and the Environment*, 6(8), 439–447.
→ **Confidence: high.** Original Anthromes concept paper. Introduces the 21-class scheme and the theoretical framing of "anthromes" as the anthropogenic counterpart to natural biomes. Read for the classification logic and what the classes are meant to represent.

**Ellis, E.C., Klein Goldewijk, K., Siebert, S., Lightman, D., and Ramankutty, N. (2010)**
"Anthropogenic transformation of the biomes, 1700 to 2000."
*Global Ecology and Biogeography*, 19(5), 589–606.
→ **Confidence: high on content, moderate on exact volume/page.** The most directly relevant paper for EDOPS — explicitly applies the Anthromes classification using HYDE data for 1700–2000. Klein Goldewijk's co-authorship is the direct HYDE connection. This is the paper to read for how class assignment works from HYDE inputs and what the class boundaries mean in terms of land use intensity.

**Ellis, E.C., Gauthier, N., Klein Goldewijk, K., Bliege Bird, R., Boivin, N., Díaz, S., Fuller, D.Q., Gill, J.L., Kaplan, J.O., Kingston, N., Locke, H., McMichael, C.N.H., Ranco, D., Rick, T.C., Shaw, M.R., Stephens, L., Svenning, J.-C., and Watson, J.E.M. (2021)**
"People have shaped most of terrestrial nature for at least 10,000 years."
*PNAS*, 118(17), e2023483118.
→ **Confidence: moderate on exact details.** Anthromes 12k — extends coverage to 10,000+ years before present, also using HYDE as the primary land use input. If the HYDE Anthromes layer includes pre-CE epochs, this is the likely methodological source. The paper also makes a broader argument about human influence on biomes that is relevant to how Anthromes values should be interpreted.

### Version and data file note

The HYDE download may include Anthromes as a separate bundled layer with its own readme. The class numbering (including the "class 70 = no definition" mentioned in the exploration plan) and exact class count (21 in v2; may differ in 12k) should be verified against the actual data files before notebook design. The readme or metadata file is the authoritative source for the version-specific class scheme and citation.

### Known qualifications

- **Anthromes are a classification, not a measurement.** Each cell is assigned a class based on thresholds applied to HYDE population density and land use fractions. The class boundaries are argued choices, not natural discontinuities.
- **Class assignment inherits HYDE's uncertainty.** All of HYDE's reconstruction limitations (F8.x) propagate directly into the Anthromes classification. A cell classified as "cropland" in 500 CE is only as reliable as HYDE's cropland estimate at that location and epoch.
- **Class 70 / "no definition" epochs**: in earlier epochs where HYDE has insufficient data to assign a class, cells return a null/undefined class. The fraction of undefined cells rises sharply pre-CE. Any analysis must account for this explicitly.
- **The 21-class scheme collapses to far fewer meaningful classes** for most historical queries. Village, rangeland, and wild/semi-natural dominate the pre-industrial world; urban and dense-settlement classes are rare outside a handful of sites. The effective information content per query may be low.
- **Transitions between classes are potentially more informative than the classes themselves** — a cell moving from semi-natural to cropland between epochs is a historically meaningful event. Whether the API exposes trajectories or just snapshots is a design decision.

---

## Reading notes

These papers will reward careful reading beyond the abstract. Specific sections to prioritise:

- **LMR**: Tardif et al. §2 (proxy database), §4 (validation), and any supplementary tables listing proxy counts by region and century. The geographic distribution of proxies is the key to understanding everything else about the reconstruction.
- **HYDE**: Klein Goldewijk et al. (2017) §3–4 (methodology) and §6 (uncertainty). The reconstruction is anchored by population estimates which themselves carry substantial uncertainty; understanding the uncertainty cascade is important.
- **BasinATLAS**: Linke et al. (2019) supplementary technical documentation more than the paper itself. Each variable group has its own provenance and limitations.
- **eVolv2k**: Toohey & Sigl (2017) §3 (VSSI estimation) and §5 (uncertainty and limitations). The distinction between ice-core sulfate signal and VSSI (stratospheric injection) involves a scaling that introduces its own uncertainty.
- **Anthromes**: Ellis & Ramankutty (2008) for the classification logic; Ellis et al. (2010) for the HYDE-linked temporal version. Focus on how class thresholds are defined and what HYDE inputs drive class assignment — that's where the uncertainty enters.
