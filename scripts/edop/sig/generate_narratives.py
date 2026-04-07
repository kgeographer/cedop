"""
generate_narratives.py — Generate plain-language narrative summaries for rev1 signatures.

Reads signatures from output/edop/signatures/{set_name}/, flattens each to a
structured text digest, calls the Claude API using the general narrative prompt,
and writes the result back into the signature JSON under narrative.text.

Usage:
    python scripts/edop/sig/generate_narratives.py set_personal_v1
    python scripts/edop/sig/generate_narratives.py set_personal_v1 --place timbuktu
    python scripts/edop/sig/generate_narratives.py set_personal_v1 --model claude-opus-4-6
"""
import sys
import json
import argparse
from pathlib import Path

import anthropic
from dotenv import load_dotenv

ROOT       = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")
OUTPUT_DIR = ROOT / "output" / "edop" / "signatures"
PROMPT_DIR = ROOT / "prompts"
STYLES = {
    "rev1":       "edop_narrative_rev1.md",
    "scientific": "edop_narrative_scientific.md",
    "general":    "edop_narrative_general.md",
}

DEFAULT_MODEL  = "claude-sonnet-4-6"
DEFAULT_TOKENS = 500


def get(obj, *keys, default=None):
    """Safe nested get."""
    for k in keys:
        if not isinstance(obj, dict):
            return default
        obj = obj.get(k, default)
        if obj is None:
            return default
    return obj


def flatten_signature(sig: dict) -> str:
    """Convert a rev1 signature JSON to a structured plain-text digest for the LLM."""
    loc   = sig.get("location", {})
    s     = sig.get("signature", {})
    meta  = sig.get("meta", {})
    A     = s.get("A_physiographic", {})
    B     = s.get("B_hydroclimatic", {})
    C     = s.get("C_bioclimatic", {})
    D     = s.get("D_anthropocene", {})
    coast = s.get("coastality", {})
    ep    = loc.get("elevation_point", {})
    basin = loc.get("basin", {})

    def fmt(v, decimals=1):
        if v is None: return "n/a"
        return f"{float(v):.{decimals}f}"

    def su(label, sv, uv, unit="", note=""):
        sv_s = fmt(sv)
        uv_s = fmt(uv)
        if sv_s == uv_s:
            line = f"  {label}: {sv_s}{unit}"
        else:
            line = f"  {label}: {sv_s}{unit} local / {uv_s}{unit} upstream"
        if note:
            line += f"  ({note})"
        return line

    lines = []
    lines.append(f"Location: {loc.get('name', 'Unknown')}")
    lines.append(f"Basin: HydroATLAS Level 8, {fmt(get(basin,'sub_area_km2'), 0)} km² local sub-basin")
    lines.append(f"Point elevation: {fmt(ep.get('value_m'), 0)} m")
    lines.append(f"Outlet: {coast.get('outlet_type','unknown')}, "
                 f"{fmt(coast.get('dist_sink_km'), 0)} km flow distance to marine outlet")
    lines.append("")

    # A: Terrain
    lines.append("TERRAIN")
    elev = A.get("elevation", {})
    lines.append(f"  Elevation range: {get(elev,'min_m','s')}–{get(elev,'max_m','s')} m")
    rp = A.get("relief_position")
    if rp is not None:
        lines.append(f"  Relief position: {float(rp):.2f}  (0 = basin floor, 1 = ridge)")
    lines.append(su("Slope", get(A,"slope_deg","s"), get(A,"slope_deg","u"), "°"))
    lines.append(f"  Stream gradient: {fmt(get(A,'stream_gradient_mpm','s'))} m/km")
    lines.append(f"  Lithology: {get(A,'lithology','class_name','s') or 'n/a'}")
    lines.append(su("Karst extent", get(A,"karst_pct","s"), get(A,"karst_pct","u"), "%"))
    lines.append(f"  Permafrost: {fmt(get(A,'permafrost_pct','s'))}%")
    lines.append("")

    # B: Water
    lines.append("WATER")
    dis = B.get("discharge_m3s", {})
    lines.append(f"  Annual discharge: {fmt(get(dis,'annual','s'))} m³/s "
                 f"(monthly range: {fmt(get(dis,'min_monthly','s'))}–{fmt(get(dis,'max_monthly','s'))} m³/s)")
    lines.append(f"  Annual runoff: {fmt(get(B,'runoff_mmyr','s'), 0)} mm/yr")
    lines.append(f"  Groundwater depth: {fmt(get(B,'groundwater_depth_cm','s'), 0)} cm")
    lines.append(su("River area",
                    get(B,"river_area_ha","s"), get(B,"river_area_ha","u"), " ha"))
    wl = B.get("wetland_pct", {})
    lines.append(su("Wetland (group 1)",
                    get(wl,"group1","s"), get(wl,"group1","u"), "%"))
    st = B.get("soil_texture", {})
    lines.append(f"  Soil texture: {fmt(get(st,'clay_pct','s'),0)}% clay / "
                 f"{fmt(get(st,'silt_pct','s'),0)}% silt / "
                 f"{fmt(get(st,'sand_pct','s'),0)}% sand  (local)")
    lines.append("")

    # C: Climate
    lines.append("CLIMATE")
    tmp = C.get("temperature_c", {})
    lines.append(su("Mean annual temperature",
                    get(tmp,"annual_mean","s"), get(tmp,"annual_mean","u"), "°C"))
    lines.append(f"  Monthly range: {fmt(get(tmp,'min_monthly','s'))}°C – "
                 f"{fmt(get(tmp,'max_monthly','s'))}°C")
    pre = C.get("precipitation_mmyr", {})
    lines.append(su("Annual precipitation",
                    get(pre,"annual","s"), get(pre,"annual","u"), " mm"))
    ari = C.get("aridity_index", {})
    lines.append(su("Aridity index",
                    ari.get("s"), ari.get("u"), "",
                    "lower=drier; <10 hyper-arid, 10–65 arid/semi-arid, 65+ sub-humid/humid"))
    lines.append(f"  Climate zone: {get(C,'climate_zone','name','s') or 'n/a'}")
    lines.append(f"  Climate stratum: {get(C,'climate_stratum','code','s') or 'n/a'}")
    lines.append(f"  Biome: {get(C,'biome','name','s') or 'n/a'}")
    lines.append(f"  Terrestrial ecoregion: {get(C,'ecoregion_terrestrial','name','s') or 'n/a'}")
    pnv = C.get("potential_natural_vegetation", {})
    lines.append(f"  Potential natural vegetation: {get(pnv,'majority_name','s') or 'n/a'}")
    shares = get(pnv, "shares", "s")
    if shares and isinstance(shares, dict):
        share_str = ", ".join(f"{k} {v}%" for k, v in list(shares.items())[:3])
        lines.append(f"    Composition: {share_str}")
    lines.append("")

    # D: Human context
    lines.append("PRESENT-DAY HUMAN CONTEXT  (for contrast; not historical)")
    lines.append(f"  Population density: {fmt(get(D,'population_density_pkm2','s'), 0)} persons/km²")
    lines.append(su("Cropland", get(D,"cropland_pct","s"), get(D,"cropland_pct","u"), "%"))
    lines.append(su("Human footprint index",
                    get(D,"human_footprint_2009","s"), get(D,"human_footprint_2009","u")))
    lines.append(f"  GDP: {fmt(get(D,'gdp_usd_km2','s'), 0)} USD/km²")
    lines.append(f"  HDI: {fmt(get(D,'hdi','s'), 3)}")
    lines.append("")

    # Temporal
    tmp_block = s.get("temporal", {})
    if tmp_block.get("period_ce"):
        lines.append(f"TEMPORAL QUERY PERIOD: {tmp_block['period_ce'][0]}–{tmp_block['period_ce'][1]} CE")
        lines.append("  (LMR and eVolv2k data: not yet implemented — all null)")
    else:
        lines.append("TEMPORAL: no period specified; contemporary baseline only")

    return "\n".join(lines)


def generate_narrative(sig: dict, system_prompt: str, model: str, max_tokens: int) -> str:
    client = anthropic.Anthropic()
    text   = flatten_signature(sig)
    name   = sig["location"]["name"]

    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[
            {"role": "user", "content": f"Write the environmental narrative for:\n\n{text}"}
        ]
    )
    return response.content[0].text


def main():
    parser = argparse.ArgumentParser(
        description="Generate plain-language narratives for EDOPS rev1 signatures."
    )
    parser.add_argument("set_name", nargs="?", default="set_personal_v1")
    parser.add_argument("--place",  help="Slug of a single place (e.g. timbuktu)")
    parser.add_argument("--model",  default=DEFAULT_MODEL)
    parser.add_argument("--tokens", type=int, default=DEFAULT_TOKENS)
    parser.add_argument("--style",  default="rev1", choices=STYLES.keys(),
                        help="Narrative style: rev1 (default), scientific, general")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the flattened digest only; don't call the API")
    args = parser.parse_args()

    system_prompt = (PROMPT_DIR / STYLES[args.style]).read_text()
    sig_dir       = OUTPUT_DIR / args.set_name

    files = sorted(sig_dir.glob("*.json"))
    if args.place:
        files = [f for f in files if f.stem == args.place]
    if not files:
        print(f"No matching signatures found in {sig_dir}")
        sys.exit(1)

    for f in files:
        sig  = json.loads(f.read_text())
        name = sig["location"]["name"]

        if args.dry_run:
            print(f"\n{'='*60}")
            print(f"DIGEST: {name}")
            print('='*60)
            print(flatten_signature(sig))
            continue

        print(f"  {name}...", end=" ", flush=True)
        narrative = generate_narrative(sig, system_prompt, args.model, args.tokens)

        sig["narrative"] = {
            "text":  narrative,
            "model": args.model,
            "prompt_file": STYLES[args.style],
            "style": args.style
        }
        f.write_text(json.dumps(sig, indent=2, ensure_ascii=False, default=str))
        print("done")
        print(f"\n{narrative}\n")

    if not args.dry_run:
        print(f"\nNarratives written to {sig_dir}")


if __name__ == "__main__":
    main()
