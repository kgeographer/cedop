# D-PLACE Environment-Culture Correlation Analysis

**Date:** 18 January 2026
**Data:** 1,133 D-PLACE societies with EDOP basin assignments
**Method:** ANOVA F-test with eta-squared effect sizes
**Bands:** A, B, C only (excluding D: Anthropocene markers - anachronistic for historical inquiry)

---

## Key Finding

EDOP signature fields—particularly temperature and water availability—significantly predict which subsistence strategies societies adopted. Bands A-C capture environmental constraints operating over centuries to millennia, making them relevant for historical inquiry.

---

## Band C: Bioclimatic Proxies (Strongest Effects)

**Temperature → Agriculture Intensity** (η² = 0.40, F = 140.5, n = 1,045)
- No agriculture: mean temp 7.6°C
- Extensive/shifting agriculture: mean temp 23.6°C
- Interpretation: Agricultural societies emerged in warmer climates; hunting/gathering persisted in colder regions.

**Temperature → Dominant Subsistence** (η² = 0.38, F = 99.7, n = 1,132)
- Hunting dominant: mean min temp -5.8°C
- Extensive agriculture dominant: mean min temp 21.4°C
- Clean gradient from cold-climate foraging to warm-climate farming.

**Temperature → Agriculture Percentage** (η² = 0.34, F = 63.5, n = 1,132)
- 0-5% agriculture: mean temp 8.3°C
- 76-85% agriculture: mean temp 22.5°C

---

## Band B: Hydro-climatic Baselines (Moderate Effects)

**Runoff → Domestic Animal Type** (η² = 0.17, F = 34.0, n = 1,039)
- Camelids: 55 mm/yr runoff (arid environments)
- Pigs: 1,431 mm/yr runoff (wet environments)
- Interpretation: Water availability constrains which animals are viable for husbandry.

**Groundwater Depth → Agriculture Intensity** (η² = 0.14, F = 34.9, n = 1,045)
- Extensive/shifting: 198 cm depth
- Intensive irrigated: 447 cm depth
- Interpretation: Deeper groundwater associated with irrigation-dependent agriculture.

**Runoff → Dominant Subsistence** (η² = 0.11, F = 19.9, n = 1,132)
- Pastoralism: 110 mm/yr (arid)
- Fishing: 744 mm/yr (wet)

---

## Band A: Physiographic Bedrock (Weaker but Stable)

**Elevation → Subsistence Patterns** (η² = 0.05-0.07)
- Fishing: low elevation (36m minimum)
- Gathering: high elevation (2,134m maximum)
- Equines: higher elevations; Deer: lower elevations

These effects are weaker but represent constraints stable over geological timescales.

---

## Summary by Band

| Band | Label | Significant Correlations | Avg Effect Size (η²) |
|------|-------|-------------------------|---------------------|
| A | Physiographic bedrock | 12 | 0.044 |
| B | Hydro-climatic baselines | 35 | 0.064 |
| C | Bioclimatic proxies | 65 | 0.144 |

---

## Why Band D Was Excluded

Band D (Anthropocene markers) includes GDP, Human Development Index, and other modern metrics (2000s data). D-PLACE societies have focal years 1850-1940. Correlating historical cultural patterns with modern economic indicators is anachronistic and misleading, even if statistically significant.

---

## Demo Narrative for Collaborators

> "EDOP assigns environmental signatures to any geographic location based on hydrological sub-basins. When we link these signatures to the D-PLACE database of 1,291 ethnographically documented societies, we find that environmental dimensions—particularly temperature and water availability—explain a substantial portion of variance in subsistence strategies.
>
> Societies in warm climates (mean temp 23°C) practiced extensive agriculture; those in cold climates (mean temp 8°C) relied on hunting and gathering. Arid environments (55 mm/yr runoff) supported camelid pastoralism; wet environments (1,400 mm/yr) supported pig husbandry.
>
> These correlations use EDOP's curated signature fields organized by persistence bands—from geological bedrock features stable over millennia to climate patterns operating over decades. By excluding modern Anthropocene markers, we focus on environmental constraints relevant to historical inquiry."

---

## Files

- `correlations_signature_bands_ABC.csv` — Full correlation results (230 variable pairs)
- `analysis_narrative_18Jan2026.md` — This file
