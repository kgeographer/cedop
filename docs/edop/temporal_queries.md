# EDOP Temporal Query Test Cases

Running record of `/api/temporal` explorations: coordinates, year ranges, observations,
and verification status. Feeds the curated example set for the future Temporal UI tab.

**Verification levels**:
- `DATA` — observable directly from the PDSI/eVolv2k values; no historical claim
- `DATED` — historical dates are established; sourced
- `HYPOTHESIS` — a plausible connection requiring scholarly verification
- `UNVERIFIED` — stated without checking; flag for follow-up

---

## Test Cases

### Ur (ancient Mesopotamia)
**Coordinates**: 30.96N, 46.10E
**LMR grid cell**: 30N, 46E

#### 400–700 CE
```
/api/temporal?lat=30.96&lon=46.10&year_start=400&year_end=700&vssi_min=5
```

**Volcanic events in window**:
| Year | vssi_tg | Location | Asymmetry |
|------|---------|----------|-----------|
| 432  | 13.98   | Ilopango, Tierra Blanca Joven (El Salvador) | 0.35 (SH-leaning) |
| 536  | 18.81   | Unknown (NH eruption) | 1.0 (NH only) |
| 540  | 31.85   | Unknown | 0.64 (NH-leaning) |
| 574  | 24.14   | Unknown | 0.53 (near-equatorial) |
| 626  | 13.20   | Unknown (NH) | 1.0 |
| 682  | 27.19   | Unknown | 0.53 |

**PDSI observations**:
- 400–460 CE: mildly positive (near-normal to slightly wet) `DATA`
- 460–500 CE: gradual drying, several negative years `DATA`
- 536–560 CE: PDSI slightly *positive* at Ur following 536 eruption (0.26 in 536,
  peak 0.52 in 550) — volcanic cooling may have reduced evapotranspiration in this
  already-arid region, counterintuitively increasing moisture balance `DATA/HYPOTHESIS`
- 628–695 CE: sustained drought cluster, PDSI mostly −0.2 to −0.4 `DATA`

**Historical context — 536 CE**:
- The 536 CE eruption is well-documented in historical sources as causing
  "mystery fog," crop failures, and famine in Europe and Asia `DATED`
- At Ur specifically, PDSI is *positive* in 536–553 CE, then neutral — the
  regional response was not the famine signal seen at higher latitudes `DATA`

**Historical context — 628–695 CE drought**:
- Islamic expansion out of Arabia began ~632 CE (Rashidun Caliphate) `DATED`
- The drought at Ur (in Mesopotamia, the *conquered* territory) coincides
  temporally with the expansion period `DATA + DATED`
- **Caution**: (1) PDSI here measures Mesopotamia, not the Arabian source region;
  (2) climate-as-driver-of-expansion is a contested hypothesis in scholarship,
  not settled consensus `HYPOTHESIS — needs verification`
- TODO: check LMR PDSI for Arabian Peninsula grid cells (24N, 46E or similar)
  to see if source-region conditions differed

---

### Kaifeng (Northern Song capital)
**Coordinates**: 34.80N, 114.30E
**LMR grid cell**: 34N, 114E
**Context**: Northern Song dynasty capital (Bianjing). Song founded 960 CE;
expansion southward documented in Cliopatria for 962–980 CE.

#### 900–1050 CE
```
/api/temporal?lat=34.80&lon=114.30&year_start=900&year_end=1050&vssi_min=5
```

**Volcanic events in window**:
| Year | vssi_tg | Location | Asymmetry |
|------|---------|----------|-----------|
| 900  | 5.56    | Unknown  | 0.58 (NH-leaning) |
| 916  | 6.08    | Unknown  | 0.68 (NH-leaning) |
| 939  | 16.23   | Katla (Iceland) | 1.0 (NH only) |
| 976  | 6.24    | Unknown  | 0.63 (NH-leaning) |
| 1028 | 7.78    | Unknown  | 0.88 (NH-dominant) |

**PDSI by decade**:
| Decade | Mean  | Notes |
|--------|-------|-------|
| 900s   | 0.090 | Near-normal |
| 910s   | 0.148 | Slightly wet |
| 920s   | 0.105 | Near-normal |
| 930s   | 0.175 | Modestly wet |
| 940s   | 0.483 | **Notably wet** — late Five Dynasties period |
| 950s   | 0.439 | **Notably wet** — Song founded 960 CE |
| 960s   | 0.187 | Moderate; Song expansion 962–980 CE |
| 970s   | 0.367 | Moderate-wet; expansion period |
| 980s   | 0.328 | Moderate-wet |
| 990s–1040s | 0.25–0.32 | Sustained mild positive, no major drought |

**Observations**:
- Kaifeng region is consistently PDSI-positive throughout — no drought stress at the
  capital during the expansion period `DATA`
- The 940s–950s wet spike precedes Song unification (960 CE) by ~20 years; occurs
  in the late Five Dynasties period `DATA + DATED`
- Katla 939 CE (16.2 Tg, pure NH) falls at the onset of the wet 940s; volcanic
  cooling at mid-latitudes may have shifted precipitation patterns northward
  toward the Yellow River basin `HYPOTHESIS — needs verification`
- The primary EDOP finding for Northern Song remains **spatial**: southward expansion
  brought access to dramatically wetter territory (subtropical south vs. continental north).
  This temporal layer shows conditions at the *capital* were favorable throughout,
  consistent with a stable political base supporting expansion. `DATA + INTERPRETATION`
- **Caution**: favorable PDSI at the capital does not explain the expansion; many
  political, military, and economic factors were primary. Climate context is
  background, not cause. `INTERPRETATION CEILING`

---

## Candidate Test Cases (not yet run)

These are plausible historical moments to probe — chosen for well-documented
climate-society interactions or for Federico's ancient water infrastructure focus.

| Place | Coords | Period | Rationale |
|-------|--------|--------|-----------|
| Ur (Mesopotamia) | 30.96N, 46.10E | 2000–1700 BCE | Akkadian Empire collapse, drought hypotheses |
| Çatalhöyük (Anatolia) | 37.67N, 32.83E | 6500–5500 BCE | Outside LMR range (pre-2000 CE) |
| Rome | 41.89N, 12.48E | 100–600 CE | Late antiquity, Justinianic plague |
| Chang'an (Xi'an) | 34.27N, 108.93E | 600–900 CE | Tang Dynasty and An Lushan Rebellion |
| Angkor Wat | 13.41N, 103.87E | 900–1500 CE | Khmer hydraulic infrastructure, drought/collapse |
| Timbuktu | 16.77N, -3.01E | 1300–1600 CE | Mali/Songhai empires, trans-Saharan trade |
| Tenochtitlan (Mexico City) | 19.43N, -99.13E | 1400–1520 CE | Aztec expansion and drought |

**Note**: LMR v2.1 covers 0–1998 CE only. Pre-CE cases require different datasets.

---

## UI Tab Design Notes

A future **Temporal** tab in the EDOP UI should offer:
- Free-form lat/lon + year range + vssi_min inputs
- A dropdown of curated examples (the cases above, once verified)
- Output: PDSI time series chart + volcanic events table
- Clear provenance labels: "LMR v2.1 PDSI reconstruction" and "eVolv2k v4"
- Uncertainty framing: 2° spatial resolution, ensemble mean, palaeoclimate proxy

Curated examples should include a brief framing question (e.g., "Was Mesopotamia
in drought during the early Islamic expansion?") and a note that the tool provides
data context, not causal explanation.
