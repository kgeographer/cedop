"""
su_divergence.py — s/u divergence profile for a set of rev1 signatures.

For each place, shows how much each local (s) value differs from its upstream
(u) counterpart. Divergence = (u - s) / mean(|s|, |u|) * 100, signed.
Zero-pair fields (both s and u = 0) are skipped.

Usage:
    python scripts/edop/sig/su_divergence.py set_personal_v1
"""
import sys
import json
import argparse
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

OUTPUT_DIR = ROOT / "output" / "edop" / "signatures"

# (label, s_path, u_path)
SU_PAIRS = [
    ("slope_deg",       "signature.A_physiographic.slope_deg.s",
                        "signature.A_physiographic.slope_deg.u"),
    ("karst_pct",       "signature.A_physiographic.karst_pct.s",
                        "signature.A_physiographic.karst_pct.u"),
    ("river_area_ha",   "signature.B_hydroclimatic.river_area_ha.s",
                        "signature.B_hydroclimatic.river_area_ha.u"),
    ("wetland_g1_pct",  "signature.B_hydroclimatic.wetland_pct.group1.s",
                        "signature.B_hydroclimatic.wetland_pct.group1.u"),
    ("wetland_g2_pct",  "signature.B_hydroclimatic.wetland_pct.group2.s",
                        "signature.B_hydroclimatic.wetland_pct.group2.u"),
    ("clay_pct",        "signature.B_hydroclimatic.soil_texture.clay_pct.s",
                        "signature.B_hydroclimatic.soil_texture.clay_pct.u"),
    ("silt_pct",        "signature.B_hydroclimatic.soil_texture.silt_pct.s",
                        "signature.B_hydroclimatic.soil_texture.silt_pct.u"),
    ("sand_pct",        "signature.B_hydroclimatic.soil_texture.sand_pct.s",
                        "signature.B_hydroclimatic.soil_texture.sand_pct.u"),
    ("temp_annual_c",   "signature.C_bioclimatic.temperature_c.annual_mean.s",
                        "signature.C_bioclimatic.temperature_c.annual_mean.u"),
    ("precip_mmyr",     "signature.C_bioclimatic.precipitation_mmyr.annual.s",
                        "signature.C_bioclimatic.precipitation_mmyr.annual.u"),
    ("aridity_index",   "signature.C_bioclimatic.aridity_index.s",
                        "signature.C_bioclimatic.aridity_index.u"),
    ("cropland_pct",    "signature.D_anthropocene.cropland_pct.s",
                        "signature.D_anthropocene.cropland_pct.u"),
    ("footprint_2009",  "signature.D_anthropocene.human_footprint_2009.s",
                        "signature.D_anthropocene.human_footprint_2009.u"),
]


def get_nested(obj, path):
    for key in path.split("."):
        if not isinstance(obj, dict) or key not in obj:
            return None
        obj = obj[key]
    return obj


def divergence(s, u):
    """Signed symmetric % divergence: (u-s) / mean(|s|,|u|) * 100.
    Returns None if both are 0 or either is None."""
    if s is None or u is None:
        return None
    s, u = float(s), float(u)
    denom = (abs(s) + abs(u)) / 2
    if denom == 0:
        return None
    return (u - s) / denom * 100


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("set_name", nargs="?", default="set_personal_v1")
    args = parser.parse_args()

    sig_dir = OUTPUT_DIR / args.set_name
    files   = sorted(sig_dir.glob("*.json"))
    if not files:
        print(f"No signatures found in {sig_dir}")
        sys.exit(1)

    all_divs = {}  # name -> {label: div}

    for f in files:
        sig  = json.loads(f.read_text())
        name = sig["location"]["name"]
        divs = {}
        for label, s_path, u_path in SU_PAIRS:
            s = get_nested(sig, s_path)
            u = get_nested(sig, u_path)
            d = divergence(s, u)
            if d is not None:
                divs[label] = (float(s), float(u), d)
        all_divs[name] = divs

    # Per-place: ranked by |divergence|
    print("=" * 70)
    print("S/U DIVERGENCE BY PLACE  (upstream vs. local, signed %)")
    print("  positive = upstream wetter/higher/larger than local")
    print("  negative = local exceeds upstream")
    print("=" * 70)

    for f in files:
        sig  = json.loads(f.read_text())
        name = sig["location"]["name"]
        outlet = sig["signature"]["coastality"]["outlet_type"]
        dist   = sig["signature"]["coastality"]["dist_sink_km"]
        divs   = all_divs[name]

        print(f"\n{name}  [{outlet}, {dist} km to outlet]")
        ranked = sorted(divs.items(), key=lambda x: abs(x[1][2]), reverse=True)
        for label, (s, u, d) in ranked:
            bar_len = int(abs(d) / 5)
            bar = ("+" if d > 0 else "-") * min(bar_len, 30)
            print(f"  {label:<18} s={s:>8.2f}  u={u:>8.2f}  {d:>+7.1f}%  {bar}")

    # Cross-place summary: which dimensions diverge most on average
    print("\n" + "=" * 70)
    print("MEAN ABSOLUTE DIVERGENCE BY DIMENSION (across all places)")
    print("=" * 70)
    dim_abs = {}
    for name, divs in all_divs.items():
        for label, (s, u, d) in divs.items():
            dim_abs.setdefault(label, []).append(abs(d))

    ranked_dims = sorted(dim_abs.items(), key=lambda x: np.mean(x[1]), reverse=True)
    for label, vals in ranked_dims:
        mean_d = np.mean(vals)
        max_d  = np.max(vals)
        bar    = "█" * int(mean_d / 5)
        print(f"  {label:<18}  mean={mean_d:>6.1f}%  max={max_d:>7.1f}%  {bar}")


if __name__ == "__main__":
    main()
