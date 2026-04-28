"""
test_band_t.py
--------------
Smoke tests for Band T (temporal enrichment): LMR climate series and
eVolv2k volcanic events.

Uses Timbuktu 1000–1100 CE — the Northern Song / volcanic quiet period
identified in Task 7 (F7.7) as the deepest volcanic minimum in the record.
Expected: non-empty climate series, no volcanic events (or very few at 5 Tg).
"""

import pytest


def test_temporal_structure(timbuktu_temporal):
    """Return dict has all expected top-level keys."""
    t = timbuktu_temporal
    assert "error" not in t, f"temporal returned error: {t.get('error')}"
    for key in ("grid_cell", "year_start", "year_end",
                "pdsi_series", "pdsi_mean", "pdsi_min", "pdsi_max",
                "air_series", "air_mean_anom_k",
                "prate_series", "prate_mean_anom_mm_day",
                "volcanic_events"):
        assert key in t, f"Missing key: {key}"


def test_temporal_series_length(timbuktu_temporal):
    """Series length matches the requested year range (inclusive)."""
    t = timbuktu_temporal
    expected = t["year_end"] - t["year_start"] + 1  # 1000–1100 = 101 years
    assert len(t["pdsi_series"])  == expected
    assert len(t["air_series"])   == expected
    assert len(t["prate_series"]) == expected


def test_temporal_year_range(timbuktu_temporal):
    """Each entry in the series has a year within the requested range."""
    t = timbuktu_temporal
    for series_key in ("pdsi_series", "air_series", "prate_series"):
        years = [entry["year"] for entry in t[series_key]]
        assert min(years) >= t["year_start"]
        assert max(years) <= t["year_end"]


def test_temporal_grid_cell_plausible(timbuktu_temporal):
    """Nearest LMR cell to Timbuktu (~17°N, 3°W) should be within 2° on each axis."""
    cell = timbuktu_temporal["grid_cell"]
    assert 15 <= cell["lat"] <= 19
    assert -5 <= cell["lon"] <= -1


def test_temporal_volcanic_quiet_period(timbuktu_temporal):
    """
    1000–1100 CE is the deepest volcanic minimum in eVolv2k (F7.7):
    low total VSSI, no Samalas-class events. One small event (1028, 7.78 Tg)
    is present — the quiet is relative, not zero.
    """
    events = timbuktu_temporal["volcanic_events"]
    total_vssi = sum(e["vssi_tg"] for e in events)
    assert total_vssi < 20, (
        f"Expected low total VSSI in 1000–1100 CE quiet period; got {total_vssi} Tg "
        f"from {len(events)} event(s): {events}"
    )
    assert all(e["vssi_tg"] < 30 for e in events), (
        f"Unexpected major eruption in 1000–1100 CE: {events}"
    )


def test_temporal_samalas_in_correct_window(db_available):
    """
    Samalas 1257 CE (59 Tg) must appear when querying 1250–1270 CE.
    Validates eVolv2k filtering and year-range logic.
    """
    if not db_available:
        pytest.skip("DB not available")
    from app.db.temporal import get_temporal_context
    result = get_temporal_context(lat=16.76618535, lon=-3.00777252,
                                  year_start=1250, year_end=1270)
    events = result.get("volcanic_events", [])
    years = [e["year_ad"] for e in events]
    assert 1257 in years, f"Samalas 1257 not found in events: {events}"
    samalas = next(e for e in events if e["year_ad"] == 1257)
    assert samalas["vssi_tg"] > 50, f"Samalas VSSI unexpectedly low: {samalas['vssi_tg']}"


def test_bce_query_lmr_out_of_range(athens_bce_temporal):
    """BCE query returns lmr_status=out_of_range with empty climate series."""
    t = athens_bce_temporal
    assert t["lmr_status"] == "out_of_range"
    assert t["pdsi_series"] == []
    assert t["air_series"] == []
    assert t["prate_series"] == []
    assert t["grid_cell"] is None


def test_bce_query_426_event(athens_bce_temporal):
    """
    426 BCE has a 59.33 Tg eruption — the largest in the eVolv2k record
    outside the CE period. Must appear in a 500–400 BCE query.
    """
    events = athens_bce_temporal["volcanic_events"]
    years = [e["year_ad"] for e in events]
    assert -426 in years, f"426 BCE eruption not found; events: {events}"
    event = next(e for e in events if e["year_ad"] == -426)
    assert event["vssi_tg"] > 50, f"426 BCE VSSI unexpectedly low: {event['vssi_tg']}"


def test_bce_query_volcanic_aggregates(athens_bce_temporal):
    """Aggregated volcanic fields are computed correctly for a BCE window."""
    t = athens_bce_temporal
    assert t["volcanic_event_count"] == len(t["volcanic_events"])
    assert t["volcanic_vssi_sum_tg"] == round(
        sum(e["vssi_tg"] for e in t["volcanic_events"]), 2
    )
    # 426 BCE event is 59 Tg — years_since_last_major should be computable
    assert t["years_since_last_major"] is not None
