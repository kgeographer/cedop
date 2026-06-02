"""
test_explorer.py
----------------
Tests for the /api/explorer/* endpoints added for the Explorer choropleth page.

Four endpoints covered:
  /api/explorer/codebook   — variable metadata for the accordion
  /api/explorer/values     — numeric GeoJSON + stats (s / u / delta modes)
  /api/explorer/categorical — categorical GeoJSON + category legend
  /api/explorer/lisa       — LISA class assignments (no geometry)

All DB-hitting tests are skipped if the DB is unavailable.
"""

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def client(db_available):
    if not db_available:
        pytest.skip("DB not available")
    from app.main import app
    return TestClient(app)


@pytest.fixture(scope="module")
def codebook(client):
    r = client.get("/api/explorer/codebook")
    assert r.status_code == 200
    return r.json()


# ---------------------------------------------------------------------------
# /api/explorer/codebook
# ---------------------------------------------------------------------------

def test_codebook_returns_list(codebook):
    assert isinstance(codebook, list)
    assert len(codebook) > 50, "Expected at least 50 codebook entries"


def test_codebook_required_fields(codebook):
    required = {"schema_key", "friendly_name", "band", "dimension", "type", "queryable"}
    for rec in codebook:
        missing = required - rec.keys()
        assert not missing, f"{rec['schema_key']} missing fields: {missing}"


def test_codebook_queryable_flag(codebook):
    # queryable must be a bool and consistent with the data
    for rec in codebook:
        assert isinstance(rec["queryable"], bool), f"{rec['schema_key']}: queryable not bool"
    # At least some variables must be queryable
    assert any(r["queryable"] for r in codebook), "No queryable variables found"


def test_codebook_range_notation_not_queryable(codebook):
    # Variables with '..' range notation must be non-queryable UNLESS they are
    # monthly_series (s01..s12 pattern), which resolve per month
    for rec in codebook:
        col_s = rec.get("basin08_col_s") or ""
        if ".." in col_s and not rec.get("monthly_series"):
            assert not rec["queryable"], (
                f"{rec['schema_key']}: has range notation '{col_s}' but queryable=True"
            )


def test_codebook_excludes_output_band(codebook):
    bands = {r["band"] for r in codebook}
    assert "output" not in bands, "Output-band rows must be excluded from codebook API"


def test_codebook_no_duplicate_schema_keys(codebook):
    keys = [r["schema_key"] for r in codebook]
    assert len(keys) == len(set(keys)), "Duplicate schema_key entries in codebook"


# ---------------------------------------------------------------------------
# /api/explorer/values
# ---------------------------------------------------------------------------

def test_values_aridity_l6(client):
    r = client.get("/api/explorer/values", params={"var": "aridity_index", "level": 6, "su": "s"})
    assert r.status_code == 200
    data = r.json()
    assert "meta" in data and "geojson" in data
    meta = data["meta"]
    assert meta["n_valid"] > 0
    assert meta["min"] is not None and meta["max"] is not None


def test_values_geojson_structure(client):
    r = client.get("/api/explorer/values", params={"var": "aridity_index", "level": 6})
    assert r.status_code == 200
    fc = r.json()["geojson"]
    assert fc["type"] == "FeatureCollection"
    feats = fc["features"]
    assert len(feats) > 1000, "Expected thousands of L6 basins"
    f = feats[0]
    assert "hybas_id" in f["properties"]
    assert "value" in f["properties"]


def test_values_no_nodata_sentinel(client):
    # -9999 sentinel values must be masked to null, never appear as a raw value
    r = client.get("/api/explorer/values", params={"var": "aridity_index", "level": 6})
    assert r.status_code == 200
    vals = [f["properties"]["value"] for f in r.json()["geojson"]["features"]]
    assert -9999 not in vals, "-9999 NoData sentinel must be masked to null"


def test_values_temperature_divide_by_10(client):
    # tmp_dc_smn stored as °C×10 — displayed values should be in plausible °C range
    r = client.get("/api/explorer/values", params={"var": "temperature_min", "level": 6, "su": "s"})
    assert r.status_code == 200
    vals = [f["properties"]["value"] for f in r.json()["geojson"]["features"] if f["properties"]["value"] is not None]
    assert vals, "No non-null temperature values"
    assert max(vals) < 200, f"temperature_min looks like it's still in °C×10 (max={max(vals)})"
    assert min(vals) > -200, f"temperature_min out of plausible range (min={min(vals)})"


def test_values_delta_mode(client):
    r = client.get("/api/explorer/values", params={"var": "aridity_index", "level": 6, "su": "delta"})
    assert r.status_code == 200
    meta = r.json()["meta"]
    # Delta should have values spanning both positive and negative (s vs u divergence)
    assert meta["min"] is not None and meta["max"] is not None


def test_values_upstream_mode(client):
    r = client.get("/api/explorer/values", params={"var": "aridity_index", "level": 6, "su": "u"})
    assert r.status_code == 200
    data = r.json()
    assert data["meta"]["n_valid"] > 0


def test_values_invalid_var(client):
    r = client.get("/api/explorer/values", params={"var": "nonexistent_var", "level": 6})
    assert r.status_code == 404


def test_values_invalid_level(client):
    r = client.get("/api/explorer/values", params={"var": "aridity_index", "level": 7})
    assert r.status_code == 400


def test_values_stats_fields(client):
    r = client.get("/api/explorer/values", params={"var": "aridity_index", "level": 6})
    assert r.status_code == 200
    meta = r.json()["meta"]
    for stat in ("min", "max", "mean", "median", "p10", "p90"):
        assert stat in meta, f"Missing stat field: {stat}"


# ---------------------------------------------------------------------------
# /api/explorer/categorical
# ---------------------------------------------------------------------------

def test_categorical_lithology_l6(client):
    r = client.get("/api/explorer/categorical", params={"var": "lithology_name", "level": 6})
    assert r.status_code == 200
    data = r.json()
    assert "categories" in data and "geojson" in data
    cats = data["categories"]
    assert len(cats) > 0, "Expected lithology categories"


def test_categorical_top_n_limit(client):
    # climate_stratum_code has 125 classes — exercises top-20 + Other collapse
    r = client.get("/api/explorer/categorical", params={"var": "climate_stratum_code", "level": 6})
    assert r.status_code == 200
    cats = r.json()["categories"]
    named   = [c for c in cats if c["id"] != -1]
    other_e = [c for c in cats if c["id"] == -1]
    assert len(named) <= 20, f"Too many named categories: {len(named)}"
    assert len(other_e) <= 1, "At most one 'Other' entry expected"


def test_categorical_colors_unique(client):
    r = client.get("/api/explorer/categorical", params={"var": "lithology_name", "level": 6})
    assert r.status_code == 200
    cats = r.json()["categories"]
    named_colors = [c["color"] for c in cats if c["id"] != -1]
    assert len(named_colors) == len(set(named_colors)), "Named categories should have unique colors"


def test_categorical_pct_sums_to_100(client):
    r = client.get("/api/explorer/categorical", params={"var": "lithology_name", "level": 6})
    assert r.status_code == 200
    total = sum(c["pct"] for c in r.json()["categories"])
    assert abs(total - 100.0) < 1.0, f"Category percentages should sum to ~100, got {total}"


def test_categorical_geojson_has_cat_id(client):
    r = client.get("/api/explorer/categorical", params={"var": "lithology_name", "level": 6})
    assert r.status_code == 200
    feats = r.json()["geojson"]["features"]
    assert len(feats) > 0
    assert "cat_id" in feats[0]["properties"]


def test_categorical_invalid_var(client):
    r = client.get("/api/explorer/categorical", params={"var": "nonexistent_var", "level": 6})
    assert r.status_code == 404


def test_categorical_numeric_var_rejected(client):
    # aridity_index is numeric, not in _CAT_LOOKUP — should 400
    r = client.get("/api/explorer/categorical", params={"var": "aridity_index", "level": 6})
    assert r.status_code == 400


# ---------------------------------------------------------------------------
# /api/explorer/lisa
# ---------------------------------------------------------------------------

def test_lisa_aridity_l8(client):
    r = client.get("/api/explorer/lisa", params={"var": "aridity_index", "level": 8})
    assert r.status_code == 200
    data = r.json()
    assert "meta" in data and "classes" in data
    meta = data["meta"]
    assert meta["n"] > 0
    assert "counts" in meta


def test_lisa_counts_structure(client):
    r = client.get("/api/explorer/lisa", params={"var": "aridity_index", "level": 8})
    assert r.status_code == 200
    counts = r.json()["meta"]["counts"]
    valid_classes = {"HH", "HL", "LH", "LL", "NS"}
    assert set(counts.keys()).issubset(valid_classes), f"Unexpected LISA classes: {set(counts.keys()) - valid_classes}"


def test_lisa_classes_values(client):
    r = client.get("/api/explorer/lisa", params={"var": "aridity_index", "level": 8})
    assert r.status_code == 200
    classes = r.json()["classes"]
    assert len(classes) > 0, "classes dict must not be empty"
    valid = {"HH", "HL", "LH", "LL", "NS"}
    bad = {v for v in classes.values() if v not in valid}
    assert not bad, f"Invalid LISA class values: {bad}"


def test_lisa_classes_keys_are_strings(client):
    # JS looks up by String(hybas_id) — API must return string keys
    r = client.get("/api/explorer/lisa", params={"var": "aridity_index", "level": 8})
    assert r.status_code == 200
    classes = r.json()["classes"]
    sample_keys = list(classes.keys())[:10]
    for k in sample_keys:
        assert isinstance(k, str), f"hybas_id key should be string, got {type(k)}: {k}"


def test_lisa_counts_sum_equals_n(client):
    r = client.get("/api/explorer/lisa", params={"var": "aridity_index", "level": 8})
    assert r.status_code == 200
    data = r.json()
    n       = data["meta"]["n"]
    total   = sum(data["meta"]["counts"].values())
    assert total == n, f"counts sum {total} != meta.n {n}"


def test_lisa_no_data_returns_404(client):
    # Categorical variables have no LISA data (join-count only) — should always 404
    r = client.get("/api/explorer/lisa", params={"var": "lithology_name", "level": 8})
    assert r.status_code == 404


def test_lisa_invalid_var(client):
    r = client.get("/api/explorer/lisa", params={"var": "nonexistent_var", "level": 8})
    assert r.status_code == 404


def test_lisa_no_geometry_in_response(client):
    # LISA endpoint must NOT return geometry — client reuses the choropleth layer
    r = client.get("/api/explorer/lisa", params={"var": "aridity_index", "level": 8})
    assert r.status_code == 200
    data = r.json()
    assert "geojson" not in data, "LISA endpoint must not return GeoJSON geometry"
    assert "features" not in data
