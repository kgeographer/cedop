"""
load_dplace_cldf.py

Load D-PLACE CLDF v3.3.0 into the dplace schema.
Source data loaded as-is; no modifications.

Usage:
    python3 scripts/cdop/load_dplace_cldf.py [--cldf-dir data/dplace/cldf]

Requires dplace schema to exist (run sql/cdop/dplace_schema.sql first).
"""

import csv
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.shared.db_utils import db_connect


CLDF_DIR = Path("data/dplace/cldf")


def load_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def truncate_tables(cur):
    print("Truncating existing dplace tables...")
    # Order respects FK constraints
    for t in ["dplace.data", "dplace.codes", "dplace.variables",
              "dplace.societies", "dplace.contributions"]:
        cur.execute(f"TRUNCATE {t} CASCADE")


def insert_contributions(cur, rows):
    print(f"Loading contributions ({len(rows)} rows)...")
    sql = """
        INSERT INTO dplace.contributions (id, name, description, contributor, citation, doi, type, source)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (id) DO NOTHING
    """
    for r in rows:
        cur.execute(sql, (
            r.get("ID"), r.get("Name"), r.get("Description"),
            r.get("Contributor"), r.get("Citation"), r.get("DOI"),
            r.get("type"), r.get("Source")
        ))


def insert_societies(cur, rows):
    print(f"Loading societies ({len(rows)} rows)...")
    sql = """
        INSERT INTO dplace.societies
            (id, name, latitude, longitude, glottocode, name_and_id_in_source,
             xd_id, alt_names_by_society, main_focal_year, hraf_name_id, hraf_id,
             origlat, origlong, comment, glottocode_comment, region, type,
             language_level_glottocodes, iso639p3code, contribution_id)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (id) DO NOTHING
    """
    def f(r, k):
        v = r.get(k, "").strip()
        return v if v else None

    def fi(r, k):
        v = f(r, k)
        try:
            return int(v) if v else None
        except ValueError:
            return None

    def ff(r, k):
        v = f(r, k)
        try:
            return float(v) if v else None
        except ValueError:
            return None

    for r in rows:
        cur.execute(sql, (
            f(r,"ID"), f(r,"Name"), ff(r,"Latitude"), ff(r,"Longitude"),
            f(r,"Glottocode"), f(r,"Name_and_ID_in_source"), f(r,"xd_id"),
            f(r,"alt_names_by_society"), fi(r,"main_focal_year"),
            f(r,"HRAF_name_ID"), f(r,"HRAF_ID"),
            ff(r,"origLat"), ff(r,"origLong"),
            f(r,"comment"), f(r,"glottocode_comment"), f(r,"region"),
            f(r,"type"), f(r,"Language_Level_Glottocodes"), f(r,"ISO639P3code"),
            f(r,"Contribution_ID")
        ))


def insert_variables(cur, rows):
    print(f"Loading variables ({len(rows)} rows)...")
    sql = """
        INSERT INTO dplace.variables
            (id, name, description, columnspec, category, type, unit,
             source_comment, changes, comment, contribution_id)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (id) DO NOTHING
    """
    def f(r, k):
        v = r.get(k, "").strip()
        return v if v else None

    for r in rows:
        cur.execute(sql, (
            f(r,"ID"), f(r,"Name"), f(r,"Description"), f(r,"ColumnSpec"),
            f(r,"category"), f(r,"type"), f(r,"unit"),
            f(r,"source_comment"), f(r,"changes"), f(r,"comment"),
            f(r,"Contribution_ID")
        ))


def insert_codes(cur, rows):
    print(f"Loading codes ({len(rows)} rows)...")
    sql = """
        INSERT INTO dplace.codes (id, var_id, name, description, ord)
        VALUES (%s,%s,%s,%s,%s)
        ON CONFLICT (id) DO NOTHING
    """
    def f(r, k):
        v = r.get(k, "").strip()
        return v if v else None

    def fi(r, k):
        v = f(r, k)
        try:
            return int(v) if v else None
        except ValueError:
            return None

    for r in rows:
        cur.execute(sql, (
            f(r,"ID"), f(r,"Var_ID"), f(r,"Name"), f(r,"Description"), fi(r,"ord")
        ))


def insert_data(cur, rows, batch_size=5000):
    print(f"Loading data ({len(rows)} rows)...")
    sql = """
        INSERT INTO dplace.data
            (id, soc_id, var_id, value, code_id, comment, source,
             sub_case, year, source_coded_data, admin_comment)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (id) DO NOTHING
    """
    def f(r, k):
        v = r.get(k, "").strip()
        return v if v else None

    batch = []
    for i, r in enumerate(rows):
        batch.append((
            f(r,"ID"), f(r,"Soc_ID"), f(r,"Var_ID"), f(r,"Value"),
            f(r,"Code_ID"), f(r,"Comment"), f(r,"Source"),
            f(r,"sub_case"), f(r,"year"), f(r,"source_coded_data"),
            f(r,"admin_comment")
        ))
        if len(batch) >= batch_size:
            cur.executemany(sql, batch)
            print(f"  ...{i+1} rows inserted")
            batch = []
    if batch:
        cur.executemany(sql, batch)
    print(f"  ...{len(rows)} total rows inserted")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cldf-dir", default=str(CLDF_DIR))
    parser.add_argument("--truncate", action="store_true",
                        help="Truncate tables before loading (default: use ON CONFLICT DO NOTHING)")
    args = parser.parse_args()

    cldf = Path(args.cldf_dir)
    conn = db_connect()
    cur = conn.cursor()

    if args.truncate:
        truncate_tables(cur)
        conn.commit()

    insert_contributions(cur, load_csv(cldf / "contributions.csv"))
    conn.commit()

    insert_societies(cur, load_csv(cldf / "societies.csv"))
    conn.commit()

    insert_variables(cur, load_csv(cldf / "variables.csv"))
    conn.commit()

    insert_codes(cur, load_csv(cldf / "codes.csv"))
    conn.commit()

    insert_data(cur, load_csv(cldf / "data.csv"))
    conn.commit()

    print("\nDone. Row counts:")
    for t in ["contributions", "societies", "variables", "codes", "data"]:
        cur.execute(f"SELECT COUNT(*) FROM dplace.{t}")
        print(f"  dplace.{t}: {cur.fetchone()[0]}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
