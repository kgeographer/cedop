"""
app/db/narrative.py
-------------------
Generates a plain-language narrative for an EDOP signature using the Claude API.

Reads the system prompt from prompts/edop_narrative_rev1.md and flattens the
flat signature dict (as returned by /api/signature) into a structured text
digest for the LLM. Optionally incorporates temporal context.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import anthropic

PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "edop_narrative_rev1.md"
DEFAULT_MODEL  = "claude-sonnet-4-6"
DEFAULT_TOKENS = 600

# Aridity index interpretation per EDOP convention
def _aridity_label(v) -> str:
    if v is None: return "unknown"
    v = float(v)
    if v < 10:   return "hyper-arid"
    if v < 20:   return "arid"
    if v < 65:   return "semi-arid"
    if v < 100:  return "sub-humid"
    return "humid"

def _outlet_type(sig: Dict) -> str:
    endo = sig.get("endorheic")
    coast = sig.get("coast_flag")
    if endo:   return "endorheic (drains to inland sink)"
    if coast:  return "coastal (basin touches coast)"
    return "exorheic (drains to ocean)"

def _fmt(v, decimals=1) -> str:
    if v is None: return "n/a"
    try:
        return f"{float(v):.{decimals}f}"
    except (TypeError, ValueError):
        return str(v)


def flatten_signature(sig: Dict[str, Any], place_name: Optional[str] = None,
                      temporal: Optional[Dict[str, Any]] = None) -> str:
    """Convert flat API signature dict to a structured plain-text digest for the LLM."""
    lines = []

    name = place_name or f"({_fmt(sig.get('lat', 'unknown'))}, {_fmt(sig.get('lon', 'unknown'))})"
    lines.append(f"EDOP Environmental Signature — {name}")
    lines.append(f"Basin level: 8 (HydroATLAS)  |  Basin ID: {sig.get('id', 'n/a')}")
    lines.append("")

    # Identity
    lines.append(f"Bioclimate zone: {sig.get('zone_name', 'n/a')} (stratum {sig.get('strata_code', 'n/a')})")
    lines.append(f"Land cover: {sig.get('land_cover_name', 'n/a')}")
    lines.append(f"Biome: {sig.get('biome', 'n/a')}")
    lines.append(f"Ecoregion: {sig.get('ecoregion', 'n/a')}")
    lines.append("")

    # A — Physiographic
    lines.append("A — Physiographic")
    lines.append(f"  Elevation (point): {_fmt(sig.get('elev_point'), 0)} m  "
                 f"(basin range {_fmt(sig.get('elev_min'), 0)}–{_fmt(sig.get('elev_max'), 0)} m, "
                 f"relief position {_fmt(sig.get('relief_position'), 2)})")
    lines.append(f"  Slope: {_fmt(sig.get('slope_avg'), 1)}° local / {_fmt(sig.get('slope_upstream'), 1)}° upstream")
    lines.append(f"  Stream gradient: {_fmt(sig.get('stream_gradient'), 1)} m/km")
    lines.append(f"  Lithology: {sig.get('lith_class', 'n/a')}")
    lines.append(f"  Karst: {_fmt(sig.get('karst'), 0)}% local / {_fmt(sig.get('karst_upstream'), 0)}% upstream")
    lines.append("")

    # B — Hydroclimatic
    lines.append("B — Hydroclimatic")
    lines.append(f"  Discharge: {_fmt(sig.get('discharge_yr'), 2)} m³/s annual mean "
                 f"(range {_fmt(sig.get('discharge_min'), 2)}–{_fmt(sig.get('discharge_max'), 2)})")
    lines.append(f"  Runoff: {_fmt(sig.get('runoff'), 0)} mm/yr")
    lines.append(f"  Groundwater table depth: {_fmt(sig.get('gw_table_depth'), 0)} cm")
    lines.append(f"  Soil texture (local): clay {_fmt(sig.get('pct_clay'), 0)}%  "
                 f"silt {_fmt(sig.get('pct_silt'), 0)}%  sand {_fmt(sig.get('pct_sand'), 0)}%")
    lines.append(f"  Soil texture (upstream): clay {_fmt(sig.get('pct_clay_upstream'), 0)}%  "
                 f"silt {_fmt(sig.get('pct_silt_upstream'), 0)}%  sand {_fmt(sig.get('pct_sand_upstream'), 0)}%")
    lines.append(f"  Wetland cover: {_fmt(sig.get('wet_pct_grp1'), 0)}% local / "
                 f"{_fmt(sig.get('wet_pct_grp1_upstream'), 0)}% upstream  "
                 f"(class: {sig.get('wetland_class', 'n/a')})")
    lines.append(f"  Potential natural vegetation: {sig.get('pnv_majority', 'n/a')}")
    lines.append("")

    # C — Bioclimatic (s/u duality foregrounded)
    lines.append("C — Bioclimatic  [local (s) / upstream (u)]")
    lines.append(f"  Temperature: {_fmt(sig.get('temp_yr'), 1)}°C annual mean (s) / "
                 f"{_fmt(sig.get('temp_yr_upstream'), 1)}°C (u)  "
                 f"[range {_fmt(sig.get('temp_min'), 1)}–{_fmt(sig.get('temp_max'), 1)}°C local]")
    lines.append(f"  Precipitation: {_fmt(sig.get('precip_yr'), 0)} mm/yr (s) / "
                 f"{_fmt(sig.get('precip_yr_upstream'), 0)} mm/yr (u)")
    lines.append(f"  Aridity index (P/PET): {_fmt(sig.get('aridity'), 0)} [{_aridity_label(sig.get('aridity'))}] (s) / "
                 f"{_fmt(sig.get('aridity_upstream'), 0)} [{_aridity_label(sig.get('aridity_upstream'))}] (u)")
    lines.append(f"  Permafrost: {_fmt(sig.get('permafrost_extent'), 0)}% of basin")
    lines.append(f"  Freshwater ecoregion: {sig.get('freshwater_ecoregion_name', 'n/a')}")
    lines.append("")

    # Coastality
    dist = sig.get('dist_sink')
    lines.append("Coastality")
    lines.append(f"  Outlet type: {_outlet_type(sig)}")
    lines.append(f"  Flow distance to outlet: {_fmt(dist, 0)} km" if dist is not None else "  Flow distance: n/a")
    lines.append("")

    # D — Anthropocene (present-day only — flagged for LLM)
    lines.append("D — Anthropocene (present-day only; treat as reference frame, not historical)")
    lines.append(f"  Population density: {_fmt(sig.get('pop_density'), 1)} /km²")
    lines.append(f"  Cropland: {_fmt(sig.get('cropland_extent'), 0)}% local / "
                 f"{_fmt(sig.get('cropland_extent_upstream'), 0)}% upstream")
    lines.append(f"  Human footprint (2009): {_fmt(sig.get('human_footprint_09'), 0)}")
    lines.append(f"  GDP avg: ${_fmt(sig.get('gdp_avg'), 0)}  HDI: {_fmt(sig.get('human_dev_idx'), 3)}")
    lines.append("")

    # Temporal enrichment (optional)
    if temporal and temporal.get("pdsi_series"):
        lines.append(f"Temporal — LMR v2.1 PDSI  "
                     f"(grid cell {temporal['grid_cell']['lat']}N, {temporal['grid_cell']['lon']}E)  "
                     f"{temporal['year_start']}–{temporal['year_end']} CE")
        lines.append(f"  PDSI mean: {temporal['pdsi_mean']}  "
                     f"min: {temporal['pdsi_min']}  max: {temporal['pdsi_max']}")
        events = temporal.get("volcanic_events", [])
        if events:
            lines.append(f"  Major volcanic events (vssi ≥ threshold):")
            for e in events:
                loc = e.get("location") or "unknown source"
                lines.append(f"    {e['year_ad']} CE — {e['vssi_tg']} Tg  {loc}")
        lines.append("")

    return "\n".join(lines)


def get_narrative(
    sig: Dict[str, Any],
    place_name: Optional[str] = None,
    temporal: Optional[Dict[str, Any]] = None,
    model: str = DEFAULT_MODEL,
) -> str:
    """
    Call Claude API and return a plain-language narrative for the signature.

    Parameters
    ----------
    sig         : flat signature dict from /api/signature
    place_name  : display name for the place (e.g. "Timbuktu")
    temporal    : optional temporal context dict from /api/temporal
    model       : Claude model ID

    Returns
    -------
    str — the narrative text, or an error message prefixed with "ERROR:"
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return "ERROR: ANTHROPIC_API_KEY not set"

    try:
        system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"ERROR: prompt file not found at {PROMPT_PATH}"

    digest = flatten_signature(sig, place_name=place_name, temporal=temporal)

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=model,
        max_tokens=DEFAULT_TOKENS,
        system=system_prompt,
        messages=[{"role": "user", "content": digest}],
    )
    return message.content[0].text
