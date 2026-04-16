"""
load_seshat.py

Load Seshat General History Databank exports into seshat schema.
Source files are pipe-delimited CSVs in data/seshat/.

Usage:
    python3 scripts/cdop/load_seshat.py

Requires seshat schema (run sql/cdop/seshat_schema.sql first).
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.shared.db_utils import db_connect

DATA_DIR = Path("data/seshat")


def parse_bool(v):
    if v is None:
        return None
    return v.strip().lower() == 'true'

def parse_int(v):
    v = (v or '').strip()
    try:
        return int(v) if v else None
    except ValueError:
        return None

def nullify(v):
    v = (v or '').strip()
    return v if v else None


def load_general(cur):
    path = next(DATA_DIR.glob("general_data_*.csv"))
    print(f"Loading general: {path.name}")
    cur.execute("TRUNCATE seshat.general RESTART IDENTITY")

    sql = """
        INSERT INTO seshat.general
            (section, subsection, polity_name, polity_new_id, polity_old_id,
             variable_name, value_from, value_to, year_from, year_to,
             confidence, is_disputed, is_uncertain, expert_checked)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    with open(path, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f, delimiter='|'))

    batch = []
    for r in rows:
        batch.append((
            nullify(r.get('section')), nullify(r.get('subsection')),
            nullify(r.get('polity_name')), nullify(r.get('polity_new_ID')),
            nullify(r.get('polity_old_ID')), nullify(r.get('variable_name')),
            nullify(r.get('value_from')), nullify(r.get('value_to')),
            parse_int(r.get('year_from')), parse_int(r.get('year_to')),
            nullify(r.get('confidence')),
            parse_bool(r.get('is_disputed')), parse_bool(r.get('is_uncertain')),
            parse_bool(r.get('expert_checked'))
        ))
    cur.executemany(sql, batch)
    print(f"  Inserted {len(batch)} rows")


def load_social(cur):
    path = next(DATA_DIR.glob("social_complexity_data_*.csv"))
    print(f"Loading social: {path.name}")
    cur.execute("TRUNCATE seshat.social RESTART IDENTITY")

    sql = """
        INSERT INTO seshat.social
            (subsection, variable_name, year_from, year_to,
             polity_name, polity_new_id, polity_old_id,
             value_from, value_to, confidence,
             is_disputed, is_uncertain, expert_checked, drb_reviewed)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    with open(path, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f, delimiter='|'))

    batch = []
    for r in rows:
        batch.append((
            nullify(r.get('subsection')), nullify(r.get('variable_name')),
            parse_int(r.get('year_from')), parse_int(r.get('year_to')),
            nullify(r.get('polity_name')), nullify(r.get('polity_new_ID')),
            nullify(r.get('polity_old_ID')),
            nullify(r.get('value_from')), nullify(r.get('value_to')),
            nullify(r.get('confidence')),
            parse_bool(r.get('is_disputed')), parse_bool(r.get('is_uncertain')),
            parse_bool(r.get('expert_checked')), parse_bool(r.get('DRB_reviewed'))
        ))
    cur.executemany(sql, batch)
    print(f"  Inserted {len(batch)} rows")


def main():
    conn = db_connect()
    cur = conn.cursor()

    load_general(cur)
    conn.commit()

    load_social(cur)
    conn.commit()

    print("\nRow counts:")
    for t in ["general", "social"]:
        cur.execute(f"SELECT COUNT(*) FROM seshat.{t}")
        print(f"  seshat.{t}: {cur.fetchone()[0]}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
