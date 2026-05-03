"""
test_api_examples.py
--------------------
Smoke tests that mirror the example curl requests in app/static/api_guide.html.
One test per example; all are skipped if the DB is unavailable.

Examples tested:
  1. Athens         — bands=AB    (static only, no temporal)
  2. Samarkand      — bands=ABCDE (full baseline, no temporal)
  3. Rome           — bands=ABCT, from_year=1,   to_year=400   (imperial period)
  4. Kaifeng        — bands=ABCT, from_year=960, to_year=1127  (Song dynasty)
  5. Timbuktu       — bands=ABT,  from_year=1200, to_year=1600 (medieval)
  6. Kaifeng L6     — bands=ABC,  level=6         (regional scale)
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client(db_available):
    if not db_available:
        pytest.skip("DB not available")
    from app.main import app
    return TestClient(app)


# ---------------------------------------------------------------------------
# 1. Athens — bands=AB
# ---------------------------------------------------------------------------

def test_athens_bands_ab(client):
    r = client.get("/api/signature", params={"lat": 37.97, "lon": 23.73, "bands": "AB"})
    assert r.status_code == 200
    data = r.json()
    pg = data["profile_groups"]
    assert "A" in pg and "B" in pg
    assert "C" not in pg and "T" not in pg
    assert len(pg["A"]["items"]) > 0


# ---------------------------------------------------------------------------
# 2. Samarkand — bands=ABCDE
# ---------------------------------------------------------------------------

def test_samarkand_bands_abcde(client):
    r = client.get("/api/signature", params={"lat": 39.65, "lon": 66.98, "bands": "ABCDE"})
    assert r.status_code == 200
    pg = r.json()["profile_groups"]
    for band in ("A", "B", "C", "D", "E"):
        assert band in pg, f"Missing band {band}"
    assert "T" not in pg


# ---------------------------------------------------------------------------
# 3. Rome — bands=ABCT, early imperial period
# ---------------------------------------------------------------------------

def test_rome_bands_abct(client):
    r = client.get("/api/signature", params={
        "lat": 41.9, "lon": 12.5,
        "bands": "ABCT", "from_year": 1, "to_year": 400,
    })
    assert r.status_code == 200
    data = r.json()
    pg = data["profile_groups"]
    for band in ("A", "B", "C", "T"):
        assert band in pg, f"Missing band {band}"

    t = pg["T"]
    assert t.get("_status") == "ok", f"Band T status: {t.get('_status')}"
    assert len(t["pdsi_series"]) > 0, "pdsi_series empty for Rome 1–400 CE"
    assert len(t["air_series"]) > 0
    assert len(t["prate_series"]) > 0


# ---------------------------------------------------------------------------
# 4. Kaifeng — bands=ABCT, Song dynasty capital
# ---------------------------------------------------------------------------

def test_kaifeng_bands_abct(client):
    r = client.get("/api/signature", params={
        "lat": 34.8, "lon": 114.3,
        "bands": "ABCT", "from_year": 960, "to_year": 1127,
    })
    assert r.status_code == 200
    data = r.json()
    pg = data["profile_groups"]
    for band in ("A", "B", "C", "T"):
        assert band in pg, f"Missing band {band}"

    t = pg["T"]
    assert t.get("_status") == "ok", f"Band T status: {t.get('_status')}"
    assert len(t["pdsi_series"]) == 1127 - 960 + 1, (
        f"Expected {1127-960+1} PDSI years; got {len(t['pdsi_series'])}"
    )
    # HYDE land use should be present for this medieval window
    hyde = t.get("hyde_land_use", [])
    assert len(hyde) > 0, "Expected HYDE land-use epochs for Kaifeng 960–1127"


# ---------------------------------------------------------------------------
# 5. Timbuktu — bands=ABT, medieval period
# ---------------------------------------------------------------------------

def test_timbuktu_bands_abt(client):
    r = client.get("/api/signature", params={
        "lat": 16.77, "lon": -3.01,
        "bands": "ABT", "from_year": 1200, "to_year": 1600,
    })
    assert r.status_code == 200
    pg = r.json()["profile_groups"]
    assert "A" in pg and "B" in pg and "T" in pg
    assert "C" not in pg

    t = pg["T"]
    assert t.get("_status") == "ok"
    assert len(t["pdsi_series"]) == 1600 - 1200 + 1


# ---------------------------------------------------------------------------
# 6. Kaifeng — bands=ABC, level=6 (regional scale)
# ---------------------------------------------------------------------------

def test_kaifeng_level6(client):
    r = client.get("/api/signature", params={
        "lat": 34.8, "lon": 114.3,
        "bands": "ABC", "level": 6,
    })
    assert r.status_code == 200
    data = r.json()
    assert data["meta"]["query"]["level"] == 6
    pg = data["profile_groups"]
    for band in ("A", "B", "C"):
        assert band in pg
    assert "T" not in pg
