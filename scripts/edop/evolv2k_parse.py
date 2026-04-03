"""
evolv2k_parse.py
----------------
Parses the eVolv2k v4 tab-delimited file (Sigl & Toohey 2024, PANGAEA)
and writes a clean CSV to data/volcano/.

The .tab format has a multi-line comment header ending with '*/,
followed by a single header row with long PANGAEA-style column labels,
then the data rows.

Run from repo root:
    ~/envs/_edop/bin/python3 scripts/edop/evolv2k_parse.py
"""

import io
import pandas as pd
from pathlib import Path

TAB_FILE = Path("data/volcano/Sigl-Toohey_2024_eVolv2k_v4.tab")
OUT_CSV  = Path("data/volcano/evolv2k_v4.csv")

# Short column names mapped in order to the 13 PANGAEA columns
COLUMNS = [
    "year_ad",       # Eruption year (AD convention; no year 0)
    "year_iso",      # ISO 8601 year (includes year 0)
    "month",
    "day",
    "lat",           # Estimated eruption latitude
    "so4_grl",       # Greenland cumulative sulfate deposition (kg/m²)
    "so4_ant",       # Antarctic cumulative sulfate deposition (kg/m²)
    "vssi_tg",       # Volcanic stratospheric sulfur injection (Tg)
    "vssi_1sig",     # 1-sigma uncertainty (Tg)
    "asymmetry",     # DG/(DG+DA); 1.0 = NH only, 0.0 = SH only
    "location",      # Named volcano or 'N/A'
    "tephra",        # Tephra detected in ice cores (Y/N)
    "reference",
]

def parse():
    text = TAB_FILE.read_text(encoding="utf-8")

    # Strip the /* ... */ header block
    end_of_header = text.index("*/") + 2
    data_block = text[end_of_header:].lstrip("\n")

    df = pd.read_csv(
        io.StringIO(data_block),
        sep="\t",
        header=0,           # one header row with long PANGAEA labels
        names=COLUMNS,      # replace with short names
        encoding="utf-8",
    )

    print(f"Loaded {len(df)} eruption records")
    print(f"Year range: {df['year_ad'].min()} – {df['year_ad'].max()} CE")
    print(f"Columns: {list(df.columns)}")
    print(f"\nSample (first 5):")
    print(df.head().to_string(index=False))

    df.to_csv(OUT_CSV, index=False)
    print(f"\nSaved: {OUT_CSV}")
    return df

if __name__ == "__main__":
    parse()
