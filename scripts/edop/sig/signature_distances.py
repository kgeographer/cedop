"""
signature_distances.py — Pairwise distance matrix for a set of rev1 signatures.

Flattens each signature to a numeric vector, z-score normalizes, then computes
Euclidean and cosine distances. Prints matrices and ranks most/least similar pairs.

Usage:
    python scripts/edop/sig/signature_distances.py set_personal_v1
"""
import sys
import json
import argparse
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

OUTPUT_DIR = ROOT / "output" / "edop" / "signatures"

# (label, dotpath) — dotpath navigates nested dicts with '.'
FIELDS = [
    # A: Physiographic
    ("elev_min",          "signature.A_physiographic.elevation.min_m.s"),
    ("elev_max",          "signature.A_physiographic.elevation.max_m.s"),
    ("relief_range_m",    "signature.A_physiographic.relief_range_m"),
    ("relief_position",   "signature.A_physiographic.relief_position"),
    ("slope_s",           "signature.A_physiographic.slope_deg.s"),
    ("slope_u",           "signature.A_physiographic.slope_deg.u"),
    ("stream_gradient",   "signature.A_physiographic.stream_gradient_mpm.s"),
    ("karst_s",           "signature.A_physiographic.karst_pct.s"),
    ("karst_u",           "signature.A_physiographic.karst_pct.u"),
    ("permafrost",        "signature.A_physiographic.permafrost_pct.s"),
    # B: Hydroclimatic
    ("discharge_annual",  "signature.B_hydroclimatic.discharge_m3s.annual.s"),
    ("discharge_min",     "signature.B_hydroclimatic.discharge_m3s.min_monthly.s"),
    ("discharge_max",     "signature.B_hydroclimatic.discharge_m3s.max_monthly.s"),
    ("runoff",            "signature.B_hydroclimatic.runoff_mmyr.s"),
    ("gw_depth",          "signature.B_hydroclimatic.groundwater_depth_cm.s"),
    ("river_area_s",      "signature.B_hydroclimatic.river_area_ha.s"),
    ("river_area_u",      "signature.B_hydroclimatic.river_area_ha.u"),
    ("wetland_g1_s",      "signature.B_hydroclimatic.wetland_pct.group1.s"),
    ("wetland_g1_u",      "signature.B_hydroclimatic.wetland_pct.group1.u"),
    ("wetland_g2_s",      "signature.B_hydroclimatic.wetland_pct.group2.s"),
    ("wetland_g2_u",      "signature.B_hydroclimatic.wetland_pct.group2.u"),
    ("reservoir_vol",     "signature.B_hydroclimatic.reservoir_vol_upstream.u"),
    ("clay_s",            "signature.B_hydroclimatic.soil_texture.clay_pct.s"),
    ("clay_u",            "signature.B_hydroclimatic.soil_texture.clay_pct.u"),
    ("silt_s",            "signature.B_hydroclimatic.soil_texture.silt_pct.s"),
    ("silt_u",            "signature.B_hydroclimatic.soil_texture.silt_pct.u"),
    ("sand_s",            "signature.B_hydroclimatic.soil_texture.sand_pct.s"),
    ("sand_u",            "signature.B_hydroclimatic.soil_texture.sand_pct.u"),
    # C: Bioclimatic
    ("temp_annual_s",     "signature.C_bioclimatic.temperature_c.annual_mean.s"),
    ("temp_annual_u",     "signature.C_bioclimatic.temperature_c.annual_mean.u"),
    ("temp_min",          "signature.C_bioclimatic.temperature_c.min_monthly.s"),
    ("temp_max",          "signature.C_bioclimatic.temperature_c.max_monthly.s"),
    ("precip_s",          "signature.C_bioclimatic.precipitation_mmyr.annual.s"),
    ("precip_u",          "signature.C_bioclimatic.precipitation_mmyr.annual.u"),
    ("aridity_s",         "signature.C_bioclimatic.aridity_index.s"),
    ("aridity_u",         "signature.C_bioclimatic.aridity_index.u"),
    # D: Anthropocene
    ("pop_density",       "signature.D_anthropocene.population_density_pkm2.s"),
    ("cropland_s",        "signature.D_anthropocene.cropland_pct.s"),
    ("cropland_u",        "signature.D_anthropocene.cropland_pct.u"),
    ("footprint_s",       "signature.D_anthropocene.human_footprint_2009.s"),
    ("footprint_u",       "signature.D_anthropocene.human_footprint_2009.u"),
    ("gdp",               "signature.D_anthropocene.gdp_usd_km2.s"),
    ("hdi",               "signature.D_anthropocene.hdi.s"),
    # Coastality
    ("dist_sink_km",      "signature.coastality.dist_sink_km"),
]


def get_nested(obj: dict, path: str):
    for key in path.split("."):
        if not isinstance(obj, dict) or key not in obj:
            return None
        obj = obj[key]
    return obj


def load_vectors(set_name: str):
    sig_dir = OUTPUT_DIR / set_name
    files   = sorted(sig_dir.glob("*.json"))
    if not files:
        print(f"No signatures found in {sig_dir}")
        sys.exit(1)

    names, vectors = [], []
    for f in files:
        sig = json.loads(f.read_text())
        names.append(sig["location"]["name"])
        vectors.append([get_nested(sig, path) for _, path in FIELDS])
    return names, vectors


def normalize(matrix: np.ndarray) -> np.ndarray:
    mean = np.nanmean(matrix, axis=0)
    std  = np.nanstd(matrix, axis=0)
    std[std == 0] = 1.0
    return (matrix - mean) / std


def cosine_dist(a, b) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(1.0 - np.dot(a, b) / denom) if denom else 1.0


def print_matrix(names, matrix, title):
    w     = max(len(n) for n in names)
    col_w = 7
    print(f"\n{title}")
    header = "  ".join(f"{n[:col_w]:>{col_w}}" for n in names)
    print(" " * (w + 2) + header)
    for i, row_name in enumerate(names):
        cells = "  ".join(
            "   —   " if i == j else f"{matrix[i,j]:>7.3f}"
            for j in range(len(names))
        )
        print(f"{row_name:<{w}}  {cells}")


def print_ranked_pairs(names, matrix, n=5):
    pairs = sorted(
        (matrix[i, j], names[i], names[j])
        for i in range(len(names))
        for j in range(i + 1, len(names))
    )
    print("  Most similar:")
    for d, a, b in pairs[:n]:
        print(f"    {a} ↔ {b}:  {d:.3f}")
    print("  Most different:")
    for d, a, b in reversed(pairs[-n:]):
        print(f"    {a} ↔ {b}:  {d:.3f}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("set_name", nargs="?", default="set_personal_v1")
    args = parser.parse_args()

    names, vectors = load_vectors(args.set_name)

    mat = np.array(
        [[v if v is not None else np.nan for v in row] for row in vectors],
        dtype=float
    )

    # Report and impute nulls
    null_counts = np.isnan(mat).sum(axis=0)
    if null_counts.any():
        print("Nulls imputed with column mean:")
        for i, (label, _) in enumerate(FIELDS):
            if null_counts[i]:
                print(f"  {label}: {int(null_counts[i])} null(s)")

    col_means = np.nanmean(mat, axis=0)
    for col in range(mat.shape[1]):
        mask = np.isnan(mat[:, col])
        mat[mask, col] = col_means[col]

    normed = normalize(mat)

    # Euclidean
    n = len(names)
    euc = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            euc[i, j] = np.linalg.norm(normed[i] - normed[j])

    # Cosine
    cos = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            cos[i, j] = cosine_dist(normed[i], normed[j])

    print_matrix(names, euc, "Euclidean distance (z-score normalized)")
    print_ranked_pairs(names, euc)

    print_matrix(names, cos, "Cosine distance (z-score normalized)")
    print_ranked_pairs(names, cos)


if __name__ == "__main__":
    main()
