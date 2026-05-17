# Session Log — 16 May 2026

## Participants
Karl Grossner, Claude Sonnet 4.6 (CC)

## Context
Continuing ESDA spatial statistics phase, `esda` branch. Previous session completed aridity at L6+L8 and established `spatial/esda_findings.md`. This session: discharge (`dis_m3_pyr`) at both scales in a single notebook, plus conceptual grounding in log transforms and spatial structure.

---

## 1. Notebook 03 — Discharge at L6 and L8 (`03_discharge_l6_l8_moran.ipynb`)

Single notebook covering both scales. Variable: `dis_m3_pyr` (mean annual discharge, m³/s, cumulative upstream — no upstream variant). 32 cells: Part 1 (L6, cells 2–18), Part 2 (L8, cells 20–30), Part 3 cross-scale comparison (cell 32).

### Design decisions
- Global constants at top: `SIGNIFICANCE=0.05`, `SEED=42`, `COLOURS={...}`, `quad_map`
- Both raw AND log I computed before LISA — discharge is the first variable where the distinction matters enough to show both
- Log-transformed values used for LISA and scatter plots
- GDFs named `gdf6`/`gdf8` to coexist in same kernel
- No `plt.show()` anywhere (see METH.2)

### Distribution (Step 2, both scales)

Raw discharge histogram: nearly every basin shows as 0 because the Amazon (~200,000 m³/s) dominates the x-axis; the vast majority of basins are imperceptible. Log transform reveals the full distribution — this was a teachable moment for Karl on why log transforms are used for heavy-tailed variables (compresses range so proportional variation is visible).

L6 mean = 338 m³/s, median = 5.0; raw skewness ~41. Log transform is canonical.

### Global Moran's I

| Scale | I (raw) | I (log) | Δ (log−raw) |
|-------|---------|---------|-------------|
| L6 | 0.3986 | 0.5822 | +0.1836 |
| L8 | 0.3689 | 0.5629 | +0.1941 |

Key contrast: I_log is ~0.41 below aridity at both scales. Adjacent basins share aridity values tightly (same climate zone); they share discharge values loosely (may drain into completely different river systems across a watershed divide).

For discharge, the log transform is not cosmetic — it raises I by +0.18, changing interpretation from "weakly" to "moderately" autocorrelated. Rule established: for skewness > ~5, raw and log I measure different things.

**Scale direction reversal**: aridity I increases with finer resolution (+0.026); discharge I decreases (−0.019). Mechanism: at L8 more adjacent basin pairs straddle watershed divides with sharply different discharge. Climate gradients have no equivalent discontinuity. Scale direction is now a variable-type diagnostic for the characterisation pipeline.

### LISA (L6, log-transformed)

```
HH:  3,346  (20.4%)
LL:  3,107  (18.9%)
HL:    124  (0.8%)
LH:    300  (1.8%)
NS:  9,520  (58.1%)
```

Near-parity HH≈LL vs aridity's strong LL dominance (30% vs 4.6%). LH appears at 1.8% — impossible for aridity, natural for discharge (small endorheic/rain-shadow basins embedded in high-flow surroundings).

### LISA (L8, log-transformed)

```
HH: 29,819  (15.6%)
LL: 44,890  (23.5%)
HL:    626  (0.3%)
LH:  6,752  (3.5%)
NS: 108,588 (56.9%)
```

HH/LL reversal across scales (L6: HH>LL; L8: LL>HH) as small headwater/endorheic basins push LL ahead. LH grows 22.5× vs 11.6× basin count — the watershed-divide effect made explicit.

### Map observations

L6 LISA cluster map: Blue Danube and Rhine clearly visible; Atacama well-defined; Siberia (LL) as a massive interior endorheic/low-discharge expanse.

L8: individual river corridors visually traceable. NS zones (interfluves) prominent.

### Cross-scale comparison (cell 32)

| Class | L6 % | L8 % | Δ | L6 n | L8 n | ratio |
|---|---|---|---|---|---|---|
| HH | 20.4 | 15.6 | −4.8 | 3,346 | 29,819 | 8.9× |
| LL | 18.9 | 23.5 | +4.6 | 3,107 | 44,890 | 14.4× |
| HL | 0.8 | 0.3 | −0.4 | 124 | 626 | 5.0× |
| LH | 1.8 | 3.5 | +1.7 | 300 | 6,752 | 22.5× |
| NS | 58.1 | 56.9 | −1.1 | — | — | — |

---

## 2. ESDA findings log — DIS entries added

Added to `spatial/esda_findings.md`:

- **DIS.1** — Research question: interfluve NS zones and settlement patterns (flagged for polity phase — Karl noted Mesopotamia as the canonical interfluve case; discharge LISA class is a meaningful descriptor for historical place analysis beyond the discharge value itself)
- **DIS.2** — Global I: network topology produces ~0.41 lower I than climate gradients
- **DIS.3** — Log transform is not cosmetic for discharge: Δ=+0.18 (vs aridity +0.010)
- **DIS.4** — Scale direction reversal: discharge I ↓ with finer resolution (opposite of aridity)
- **DIS.5** — LISA class structure: HH≈LL parity, LH class appears (impossible for aridity)
- **DIS.6** — Scale effects on LISA classes: LH grows 22.5× vs 11.6× basin count; HH/LL reversal

---

## Next

- Commit current state
- Next variable: likely a climate variable (runoff, precipitation) for further calibration, or a terrain variable (elevation/slope) to contrast with both climate and network-topology structure
- Scripted pipeline (`scripts/edop/explore/12_spatial_moran.py`) deferred until Karl has seen enough contrasting variables to build intuitions
- polity flag: test LISA discharge class distribution of D-PLACE societies / Cliopatria polity centroids against global basin baseline; subsistence type filter recommended
