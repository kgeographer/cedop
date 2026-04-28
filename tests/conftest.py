"""
Shared fixtures for EDOPS tests.

All tests that hit the database are skipped automatically if the DB is
unreachable, so the suite can run safely in environments without a live DB.
"""

import os
import pytest
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Reference sites used across multiple test modules
# ---------------------------------------------------------------------------
TIMBUKTU = {"lat": 16.76618535, "lon": -3.00777252}  # hyperarid, large exotic river
ROME     = {"lat": 41.8967,     "lon": 12.4822}       # Mediterranean
KAIFENG  = {"lat": 34.7972,     "lon": 114.3075}      # Yellow River lowland


@pytest.fixture(scope="session")
def db_available():
    """Return True if the DB is reachable, False otherwise."""
    try:
        import psycopg
        conn_kwargs = {
            "dbname":   os.getenv("DB_NAME") or os.getenv("PGDATABASE", "cedop"),
            "user":     os.getenv("DB_USER") or os.getenv("PGUSER"),
            "host":     os.getenv("DB_HOST") or os.getenv("PGHOST", "localhost"),
            "port":     os.getenv("DB_PORT") or os.getenv("PGPORT", "5432"),
            "connect_timeout": 3,
        }
        conn_kwargs = {k: v for k, v in conn_kwargs.items() if v}
        with psycopg.connect(**conn_kwargs):
            return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def timbuktu_sig(db_available):
    if not db_available:
        pytest.skip("DB not available")
    from app.db.signature import get_signature
    sig = get_signature(**TIMBUKTU)
    assert sig is not None, "No basin found for Timbuktu reference point"
    return sig


@pytest.fixture(scope="session")
def timbuktu_temporal(db_available):
    if not db_available:
        pytest.skip("DB not available")
    from app.db.temporal import get_temporal_context
    return get_temporal_context(**TIMBUKTU, year_start=1000, year_end=1100)
