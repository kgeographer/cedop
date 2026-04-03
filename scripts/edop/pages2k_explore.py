"""
pages2k_explore.py
------------------
Fetches the PAGES 2k v2.0.0 directory listing from NOAA, downloads
the .txt metadata files (one per proxy record), parses each for
key fields, and writes a summary CSV.

Output: data/pages2k2017/pages2k_summary.csv
        columns: filename, site_name, archive, lat, lon,
                 earliest_year, latest_year, resolution, location_desc

Run from repo root:
    ~/envs/_edop/bin/python3 scripts/edop/pages2k_explore.py

Set DOWNLOAD=False to parse already-downloaded .txt files only.
"""

import os
import re
import time
import requests
import pandas as pd
from html.parser import HTMLParser

BASE_URL = "https://www.ncei.noaa.gov/pub/data/paleo/pages2k/pages2k-temperature-v2-2017/data-current-version/"
DATA_DIR = "data/pages2k2017"
DOWNLOAD = True          # set False once files are downloaded
PAUSE_SEC = 0.3          # polite delay between requests

# ---------------------------------------------------------------------------
# 1. Fetch directory listing and extract .txt filenames
# ---------------------------------------------------------------------------

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for name, val in attrs:
                if name == "href" and val.endswith(".txt"):
                    self.links.append(val)

def get_txt_filenames():
    print(f"Fetching directory listing from {BASE_URL} ...")
    r = requests.get(BASE_URL, timeout=30)
    r.raise_for_status()
    parser = LinkParser()
    parser.feed(r.text)
    filenames = [f for f in parser.links if not f.startswith("readme")]
    print(f"  Found {len(filenames)} .txt proxy records")
    return filenames

# ---------------------------------------------------------------------------
# 2. Download .txt files
# ---------------------------------------------------------------------------

def download_files(filenames):
    os.makedirs(DATA_DIR, exist_ok=True)
    n = len(filenames)
    for i, fname in enumerate(filenames, 1):
        dest = os.path.join(DATA_DIR, fname)
        if os.path.exists(dest):
            continue
        url = BASE_URL + fname
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            with open(dest, "w", encoding="utf-8", errors="replace") as f:
                f.write(r.text)
            if i % 50 == 0:
                print(f"  Downloaded {i}/{n} ...")
            time.sleep(PAUSE_SEC)
        except Exception as e:
            print(f"  ERROR downloading {fname}: {e}")

# ---------------------------------------------------------------------------
# 3. Parse a single .txt file for key metadata fields
# ---------------------------------------------------------------------------

FIELD_MAP = {
    "Site_Name":         "site_name",
    "Location":          "location_desc",
    "Northernmost_Latitude": "lat",
    "Southernmost_Latitude": "lat_s",
    "Easternmost_Longitude": "lon",
    "Westernmost_Longitude": "lon_w",
    "Archive":           "archive",
    "Earliest_Year":     "earliest_year",
    "Most_Recent_Year":  "latest_year",
    "Time_Unit":         "time_unit",
}

def parse_txt(filepath):
    record = {"filename": os.path.basename(filepath)}
    try:
        with open(filepath, encoding="utf-8", errors="replace") as f:
            for line in f:
                if not line.startswith("#"):
                    break
                # lines like: #	Site_Name: Quelccaya Ice Cap
                m = re.match(r"#\s+([\w_]+):\s+(.*)", line)
                if m:
                    key, val = m.group(1).strip(), m.group(2).strip()
                    if key in FIELD_MAP:
                        record[FIELD_MAP[key]] = val
    except Exception as e:
        record["error"] = str(e)

    # use northernmost lat / easternmost lon as representative point
    for fld in ["lat_s", "lon_w"]:
        record.pop(fld, None)

    # coerce numeric fields
    for fld in ["lat", "lon", "earliest_year", "latest_year"]:
        try:
            record[fld] = float(record[fld])
        except (KeyError, ValueError):
            record[fld] = None

    return record

# ---------------------------------------------------------------------------
# 4. Main
# ---------------------------------------------------------------------------

def main():
    filenames = get_txt_filenames()

    if DOWNLOAD:
        print(f"Downloading {len(filenames)} .txt files to {DATA_DIR}/ ...")
        download_files(filenames)
        print("  Done.")

    # parse all local .txt files
    print("Parsing downloaded files ...")
    records = []
    for fname in os.listdir(DATA_DIR):
        if fname.endswith(".txt") and fname != "readme-pages2k2017.txt":
            records.append(parse_txt(os.path.join(DATA_DIR, fname)))

    df = pd.DataFrame(records)

    # derived: record length in years
    df["span_years"] = df["latest_year"] - df["earliest_year"]

    # summary by archive type
    print(f"\n{len(df)} records parsed\n")
    print("Archive types:")
    print(df["archive"].value_counts().to_string())
    print(f"\nLatitude range: {df['lat'].min():.1f} to {df['lat'].max():.1f}")
    print(f"Year range:     {df['earliest_year'].min():.0f} to {df['latest_year'].max():.0f}")
    print(f"Median span:    {df['span_years'].median():.0f} years")

    out = os.path.join(DATA_DIR, "pages2k_summary.csv")
    df.to_csv(out, index=False)
    print(f"\nSummary written to {out}")

if __name__ == "__main__":
    main()
