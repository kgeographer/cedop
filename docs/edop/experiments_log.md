# EDOP Experiments Log

Chronological record of exploratory runs, demonstrations, and proof-of-concept extractions.
Each entry notes the script, parameters, output location, and key findings.
Script docstrings cover operational details; this log captures what was learned.

---

## 2026-04-03 — LMR temporal extraction: Kaifeng 950–1000 CE

**Script:** `scripts/edop/temporal_extract.py`
**Parameters:** `--name Kaifeng --lat 34.80 --lon 114.30 --year-start 950 --year-end 1000`
**Output:** `output/edop/temporal/kaifeng_950_1000/`

**Purpose:** Demonstrate LMR temporal enrichment capability for a Northern Song city,
for communication to Ruth Mostern (ISHI/Pitt). Kaifeng was the Northern Song capital;
the 950–1000 window spans the dynasty's founding consolidation.

**Findings:**
- PDSI persistently above climatological mean throughout (+0.314 period mean, all decades positive)
- 950s are the wettest decade (+0.439), just before Song consolidation
- Favorable moisture conditions across the entire expansion period — consistent with
  an agricultural base capable of supporting territorial growth
- Volcanically: 939 Katla (16.23 Tg) and 946 Changbaishan/Millennium Eruption
  (Korea/China border) both fall just before the query window — notable precursors
- 950s onward are relatively quiet, consistent with the Medieval Quiet Period (950–1100 CE)
- Changbaishan is the largest known eruption in East Asia in the last 2,000 years;
  historically documented in Chinese and Korean sources

---

## 2026-04-03 — LMR temporal extraction: Ur 0–100 CE

**Script:** `scripts/edop/temporal_extract.py`
**Parameters:** `--name Ur --lat 30.96 --lon 46.10 --year-start 0 --year-end 100`
**Output:** `output/edop/temporal/ur_0_100/`

**Purpose:** Populate the `temporal` and `volcanic` blocks of `docs/edop/signature_schema_draft.json`
with real extracted values. Ur at 0–100 CE is not a strong demonstrator of temporal signals
(site was already in long decline), but provides a well-formed null result for the schema example.

**Findings:**
- PDSI near-climatological mean throughout (-0.014 period mean), exceptionally low variability
  (std 0.040 — much lower than Kaifeng's 0.166)
- All decadal means within ±0.05 of zero: no sustained drought or wet anomaly
- A correctly-behaved null: the service returns a quiet signal when nothing dramatic is happening
- Dominant volcanic feature is **Okmok II (43 BCE, 48 Tg)** — just outside the query window
  but captured in the 50-year context; one of the largest events in the full eVolv2k catalog
  - Northern Hemisphere-dominant loading (asymmetry 0.87) → relevant to Mesopotamia
  - McConnell et al. (2020, PNAS) link Okmok II to climate/agricultural disruption
    in the late Roman Republic (falls one year after Caesar's assassination)
- Within 0–100 CE itself: modest, mostly Southern Hemisphere events (asymmetry 0.00),
  minimal stratospheric impact over Mesopotamia

---
