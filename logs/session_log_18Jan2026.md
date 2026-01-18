# Session Log: 18 January 2026

## Summary
Integrated D-PLACE cultural database with EDOP environmental signatures. Computed correlations between signature fields and cultural variables, identifying compelling environment-culture relationships for collaborator demos.

## D-PLACE Integration

### Data Overview
- **D-PLACE**: Database of Places, Language, Culture, and Environment
- 1,291 societies with coordinates, 94 anthropological variables, 121k coded observations
- Focal years typically 1850-1940 (ethnographic present)

### Tables Added (gaz schema)
- `dplace_societies` — 1,291 societies with coordinates, region, focal year
- `dplace_variables` — 94 anthropological variables (subsistence, kinship, housing, politics)
- `dplace_codes` — coded values for categorical variables
- `dplace_data` — 121k observations linking societies to variable values

### Spatial Joins
Added columns to `dplace_societies`:
- `basin_id` — FK to basin08.hybas_id (1,133 assigned, 87.8%)
- `eco_id` — FK to Ecoregions2017 (1,123 assigned, 87.0%)
- ~160 unassigned are island/coastal societies outside polygon coverage

## Correlation Analysis

### Scripts Created
1. `scripts/dplace_env_correlations_exploratory.py` — uses hand-picked basin08 variables
2. `scripts/dplace_env_correlations_signature.py` — uses EDOP curated signature fields (Bands A-C)

**Important distinction:** The signature script uses the 47 curated fields from `v_basin08_persist` organized by persistence band. This validates EDOP's framework rather than exploring arbitrary correlations.

### Key Finding: Band D Excluded
Band D (Anthropocene markers: GDP, HDI, etc.) shows strong correlations but is **anachronistic** — correlating 1850-1940 cultural patterns with 2000s economic data. Excluded from analysis.

### Results (Bands A-C, p < 0.001)

**Band C (Bioclimatic) — Strongest effects:**
- Temperature → Agriculture intensity (η² = 0.40)
  - No agriculture: 7.6°C; Extensive: 23.6°C
- Temperature → Dominant subsistence (η² = 0.38)
  - Hunting: -5.8°C min; Extensive agriculture: 21.4°C min

**Band B (Hydro-climatic) — Moderate effects:**
- Runoff → Domestic animal type (η² = 0.17)
  - Camelids: 55 mm/yr; Pigs: 1,431 mm/yr
- Groundwater depth → Agriculture intensity (η² = 0.14)

**Band A (Physiographic) — Weaker but stable:**
- Elevation → Subsistence patterns (η² = 0.05-0.07)
  - Fishing at low elevation; Gathering at high

### Summary by Band
| Band | Significant Correlations | Avg η² |
|------|-------------------------|--------|
| A (Physiographic) | 12 | 0.044 |
| B (Hydro-climatic) | 35 | 0.064 |
| C (Bioclimatic) | 65 | 0.144 |

## Output Files
- `output/dplace/correlations_signature_bands_ABC.csv` — full results (230 pairs)
- `output/dplace/analysis_narrative_18Jan2026.md` — demo narrative for collaborators

## Files Created/Modified
- `scripts/dplace_env_correlations_exploratory.py` — new
- `scripts/dplace_env_correlations_signature.py` — new
- `gaz.dplace_societies` — added basin_id, eco_id columns

## Demo Narrative
> "EDOP assigns environmental signatures to any geographic location. When linked to D-PLACE's 1,291 ethnographically documented societies, environmental dimensions—particularly temperature and water availability—explain substantial variance in subsistence strategies. Warm climates enabled agriculture; arid environments supported camelid pastoralism; wet environments supported pig husbandry. These correlations use signature fields organized by persistence bands, excluding modern Anthropocene markers to focus on historically relevant constraints."

## Next Steps
- Consider UI for D-PLACE exploration (new tab?)
- API endpoints for society lookup
- Map visualization with society points colored by subsistence type
