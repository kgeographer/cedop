from fastapi import APIRouter, HTTPException
from typing import Any, Dict, Optional, Tuple
import json
import urllib.parse
import urllib.request
import ssl
import certifi

from app.db.signature import get_signature
from app.settings import settings

from pathlib import Path
import re

router = APIRouter(prefix="/api", tags=["api"])


# -----------------------
# Utility helpers
# -----------------------

def _http_get_json(url: str, timeout_sec: int = 20) -> Dict[str, Any]:
    ctx = ssl.create_default_context(cafile=certifi.where())
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout_sec, context=ctx) as resp:
        raw = resp.read().decode("utf-8")
    return json.loads(raw)


def _whg_suggest_first(prefix: str) -> Optional[Dict[str, Any]]:
    """Call WHG suggest endpoint and return the top-ranked result, if any."""
    if not settings.WHG_API_TOKEN:
        raise HTTPException(status_code=500, detail="WHG_API_TOKEN not configured on server")

    params = {
        "prefix": prefix,
        "limit": 3,
        "cursor": 0,
        "exact": "false",
    }
    # WHG may require authentication for suggest; include token when configured.
    if settings.WHG_API_TOKEN:
        params["token"] = settings.WHG_API_TOKEN

    url = "https://whgazetteer.org/suggest/entity?" + urllib.parse.urlencode(params)
    data = _http_get_json(url)
    results = data.get("result") or []
    return results[0] if results else None


def _whg_entity(place_id: str) -> Dict[str, Any]:
    """Fetch WHG entity detail for a place id (e.g. 'place:5424806')."""
    if not settings.WHG_API_TOKEN:
        raise HTTPException(status_code=500, detail="WHG_API_TOKEN not configured on server")

    encoded_id = urllib.parse.quote(place_id, safe="")
    token = urllib.parse.quote(settings.WHG_API_TOKEN)
    url = f"https://whgazetteer.org/entity/{encoded_id}/api?token={token}"
    return _http_get_json(url)


def _extract_lonlat(entity: Dict[str, Any]) -> Optional[Tuple[float, float]]:
    """Extract (lon, lat) from a WHG entity response."""
    geoms = entity.get("geoms") or []
    if not geoms:
        return None

    g0 = geoms[0] or {}

    # Preferred: GeoJSON coordinates
    gj = g0.get("geojson")
    if isinstance(gj, dict):
        coords = gj.get("coordinates")
        if isinstance(coords, (list, tuple)) and len(coords) >= 2:
            return float(coords[0]), float(coords[1])

    # Fallbacks
    coords = g0.get("coordinates")
    if isinstance(coords, (list, tuple)) and len(coords) >= 2:
        return float(coords[0]), float(coords[1])

    centroid = g0.get("centroid")
    if isinstance(centroid, (list, tuple)) and len(centroid) >= 2:
        return float(centroid[0]), float(centroid[1])

    return None


# -----------------------
# World Heritage seed helpers
# -----------------------

_WH_SEED_PATH = Path(__file__).resolve().parents[1] / "data" / "world_heritage_seed.json"


def _parse_wkt_point(wkt: str) -> Optional[Tuple[float, float]]:
    """Parse WKT like 'POINT (lon lat)' or 'POINT(lon lat)' into (lon, lat)."""
    if not wkt:
        return None
    m = re.match(r"^\s*POINT\s*\(\s*([-0-9.]+)\s+([-0-9.]+)\s*\)\s*$", wkt)
    if not m:
        return None
    return float(m.group(1)), float(m.group(2))


def _load_wh_seed() -> list[Dict[str, Any]]:
    """Load and normalize the WH seed JSON into a list of dicts with GeoJSON Point."""
    if not _WH_SEED_PATH.exists():
        raise FileNotFoundError(f"World Heritage seed file not found at {_WH_SEED_PATH}")

    raw = json.loads(_WH_SEED_PATH.read_text(encoding="utf-8"))
    out: list[Dict[str, Any]] = []

    if not isinstance(raw, list):
        raise ValueError("World Heritage seed file must be a JSON array")

    for row in raw:
        if not isinstance(row, dict):
            continue
        wkt = row.get("geom")
        lonlat = _parse_wkt_point(wkt) if isinstance(wkt, str) else None
        if not lonlat:
            continue
        lon, lat = lonlat
        out.append(
            {
                "id_no": row.get("id_no"),
                "name_en": row.get("name_en"),
                "states_name_en": row.get("states_name_en"),
                "short_description_en": row.get("short_description_en"),
                "location": {"type": "Point", "coordinates": [lon, lat]},
            }
        )

    return out


def _get_cluster_labels() -> Dict[int, str]:
    """Fetch cluster labels for WH sites from database."""
    import psycopg
    import os

    try:
        conn = psycopg.connect(
            host=os.environ.get("PGHOST", "localhost"),
            port=os.environ.get("PGPORT", "5435"),
            dbname=os.environ.get("PGDATABASE", "edop"),
            user=os.environ.get("PGUSER", "postgres"),
            password=os.environ.get("PGPASSWORD", ""),
        )
        with conn.cursor() as cur:
            cur.execute("""
                SELECT s.id_no, c.cluster_label
                FROM edop_clusters c
                JOIN edop_wh_sites s ON s.site_id = c.site_id
            """)
            return {row[0]: row[1] for row in cur.fetchall()}
    except Exception:
        return {}
    finally:
        if 'conn' in locals():
            conn.close()


# -----------------------
# API endpoints
# -----------------------

@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/signature")
def signature(lat: float, lon: float):
    sig = get_signature(lat=lat, lon=lon)
    if sig is None:
        raise HTTPException(status_code=404, detail="No basin covers this point")
    return sig


@router.get("/resolve")
def resolve(name: str):
    """Resolve a place name using WHG suggest + entity detail.

    Returns a ResolvedPlace-style payload with GeoJSON Point coordinates
    when available.
    """
    name = (name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Missing required query parameter: name")

    try:
        first = _whg_suggest_first(name)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"WHG suggest failed: {e}")

    if not first:
        return {
            "label": name,
            "source": "whg",
            "meta": {"status": "not_found"},
        }

    place_id = first.get("id")
    if not place_id:
        return {
            "label": first.get("name") or name,
            "source": "whg",
            "meta": {"status": "no_id", "suggest": first},
        }

    try:
        entity = _whg_entity(str(place_id))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"WHG entity failed: {e}")

    lonlat = _extract_lonlat(entity)
    if not lonlat:
        return {
            "label": entity.get("title") or first.get("name") or name,
            "source": "whg",
            "meta": {
                "status": "no_geometry",
                "whg_id": place_id,
                "score": first.get("score"),
                "description": first.get("description"),
            },
        }

    lon, lat = lonlat
    return {
        "label": entity.get("title") or first.get("name") or name,
        "source": "whg",
        "location": {
            "type": "Point",
            "coordinates": [lon, lat],
        },
        "meta": {
            "status": "ok",
            "whg_id": place_id,
            "score": first.get("score"),
            "description": first.get("description"),
            "ccodes": entity.get("ccodes"),
            "dataset": entity.get("dataset"),
            "dataset_id": entity.get("dataset_id"),
        },
    }

@router.get("/wh-sites")
def wh_sites():
    """Return the small World Heritage seed set used by the pilot UI."""
    try:
        sites = _load_wh_seed()
        cluster_labels = _get_cluster_labels()

        # Add cluster_label to each site
        for site in sites:
            id_no = site.get("id_no")
            site["cluster_label"] = cluster_labels.get(id_no)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"count": len(sites), "sites": sites}


@router.get("/similar")
def similar(id_no: int, limit: int = 5):
    """Return most similar WH sites to the given site by id_no."""
    import psycopg
    import os

    try:
        conn = psycopg.connect(
            host=os.environ.get("PGHOST", "localhost"),
            port=os.environ.get("PGPORT", "5435"),
            dbname=os.environ.get("PGDATABASE", "edop"),
            user=os.environ.get("PGUSER", "postgres"),
            password=os.environ.get("PGPASSWORD", ""),
        )
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    b.id_no,
                    b.name_en,
                    b.lon,
                    b.lat,
                    ROUND(sim.distance::numeric, 2) as distance,
                    c.cluster_label
                FROM edop_similarity sim
                JOIN edop_wh_sites a ON a.site_id = sim.site_a
                JOIN edop_wh_sites b ON b.site_id = sim.site_b
                LEFT JOIN edop_clusters c ON c.site_id = b.site_id
                WHERE a.id_no = %s
                ORDER BY sim.distance ASC
                LIMIT %s
            """, (id_no, limit))

            results = []
            for row in cur.fetchall():
                results.append({
                    "id_no": row[0],
                    "name_en": row[1],
                    "lon": float(row[2]),
                    "lat": float(row[3]),
                    "distance": float(row[4]),
                    "cluster_label": row[5]
                })

            return {"source_id_no": id_no, "similar": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()


@router.get("/similar-text")
def similar_text(id_no: int, limit: int = 5):
    """Return most similar WH sites by text/semantic similarity."""
    import psycopg
    import os

    try:
        conn = psycopg.connect(
            host=os.environ.get("PGHOST", "localhost"),
            port=os.environ.get("PGPORT", "5435"),
            dbname=os.environ.get("PGDATABASE", "edop"),
            user=os.environ.get("PGUSER", "postgres"),
            password=os.environ.get("PGPASSWORD", ""),
        )
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    b.id_no,
                    b.name_en,
                    b.lon,
                    b.lat,
                    ROUND(sim.similarity::numeric, 3) as similarity,
                    c.cluster_label
                FROM edop_text_similarity sim
                JOIN edop_wh_sites a ON a.site_id = sim.site_a
                JOIN edop_wh_sites b ON b.site_id = sim.site_b
                LEFT JOIN edop_text_clusters c ON c.site_id = b.site_id
                WHERE a.id_no = %s
                ORDER BY sim.similarity DESC
                LIMIT %s
            """, (id_no, limit))

            results = []
            for row in cur.fetchall():
                results.append({
                    "id_no": row[0],
                    "name_en": row[1],
                    "lon": float(row[2]),
                    "lat": float(row[3]),
                    "similarity": float(row[4]),
                    "cluster_label": row[5]
                })

            return {"source_id_no": id_no, "similar": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()


# -----------------------
# WHC Cities (258) endpoints
# -----------------------

@router.get("/whc-cities")
def whc_cities():
    """Return all 258 World Heritage Cities with coordinates and cluster info."""
    import psycopg
    import os

    try:
        conn = psycopg.connect(
            host=os.environ.get("PGHOST", "localhost"),
            port=os.environ.get("PGPORT", "5435"),
            dbname=os.environ.get("PGDATABASE", "edop"),
            user=os.environ.get("PGUSER", "postgres"),
            password=os.environ.get("PGPASSWORD", ""),
        )
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    c.id,
                    c.city,
                    c.country,
                    c.region,
                    ST_X(c.geom) as lon,
                    ST_Y(c.geom) as lat,
                    ec.cluster_id as env_cluster,
                    ec.cluster_label as env_cluster_label
                FROM wh_cities c
                LEFT JOIN whc_clusters ec ON ec.city_id = c.id
                WHERE c.geom IS NOT NULL
                ORDER BY c.region, c.country, c.city
            """)

            cities = []
            for row in cur.fetchall():
                cities.append({
                    "id": row[0],
                    "city": row[1],
                    "country": row[2],
                    "region": row[3],
                    "location": {
                        "type": "Point",
                        "coordinates": [float(row[4]), float(row[5])]
                    } if row[4] and row[5] else None,
                    "env_cluster": row[6],
                    "env_cluster_label": row[7]
                })

            return {"count": len(cities), "cities": cities}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()


@router.get("/whc-similar")
def whc_similar(city_id: int, limit: int = 5):
    """Return most similar WHC cities by environmental signature."""
    import psycopg
    import os

    try:
        conn = psycopg.connect(
            host=os.environ.get("PGHOST", "localhost"),
            port=os.environ.get("PGPORT", "5435"),
            dbname=os.environ.get("PGDATABASE", "edop"),
            user=os.environ.get("PGUSER", "postgres"),
            password=os.environ.get("PGPASSWORD", ""),
        )
        with conn.cursor() as cur:
            # whc_similarity stores upper triangle (city_a < city_b)
            # Need to query both directions
            cur.execute("""
                WITH similarities AS (
                    SELECT city_b as other_id, distance, similarity
                    FROM whc_similarity
                    WHERE city_a = %s
                    UNION ALL
                    SELECT city_a as other_id, distance, similarity
                    FROM whc_similarity
                    WHERE city_b = %s
                )
                SELECT
                    c.id,
                    c.city,
                    c.country,
                    c.region,
                    ST_X(c.geom) as lon,
                    ST_Y(c.geom) as lat,
                    ROUND(s.distance::numeric, 2) as distance,
                    ec.cluster_id as env_cluster,
                    ec.cluster_label as env_cluster_label
                FROM similarities s
                JOIN wh_cities c ON c.id = s.other_id
                LEFT JOIN whc_clusters ec ON ec.city_id = c.id
                ORDER BY s.distance ASC
                LIMIT %s
            """, (city_id, city_id, limit))

            results = []
            for row in cur.fetchall():
                results.append({
                    "id": row[0],
                    "city": row[1],
                    "country": row[2],
                    "region": row[3],
                    "lon": float(row[4]) if row[4] else None,
                    "lat": float(row[5]) if row[5] else None,
                    "distance": float(row[6]),
                    "env_cluster": row[7],
                    "env_cluster_label": row[8]
                })

            return {"source_city_id": city_id, "similar": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()


@router.get("/whc-similar-text")
def whc_similar_text(city_id: int, band: str = "composite", limit: int = 5):
    """Return most similar WHC cities by text/semantic similarity."""
    import psycopg
    import os

    valid_bands = ['history', 'environment', 'culture', 'modern', 'composite']
    if band not in valid_bands:
        raise HTTPException(status_code=400, detail=f"Invalid band. Must be one of: {valid_bands}")

    try:
        conn = psycopg.connect(
            host=os.environ.get("PGHOST", "localhost"),
            port=os.environ.get("PGPORT", "5435"),
            dbname=os.environ.get("PGDATABASE", "edop"),
            user=os.environ.get("PGUSER", "postgres"),
            password=os.environ.get("PGPASSWORD", ""),
        )
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    c.id,
                    c.city,
                    c.country,
                    c.region,
                    ST_X(c.geom) as lon,
                    ST_Y(c.geom) as lat,
                    ROUND(s.similarity::numeric, 3) as similarity,
                    tc.cluster_id as text_cluster
                FROM whc_band_similarity s
                JOIN wh_cities c ON c.id = s.city_b
                LEFT JOIN whc_band_clusters tc ON tc.city_id = c.id AND tc.band = %s
                WHERE s.city_a = %s AND s.band = %s
                ORDER BY s.rank ASC
                LIMIT %s
            """, (band, city_id, band, limit))

            results = []
            for row in cur.fetchall():
                results.append({
                    "id": row[0],
                    "city": row[1],
                    "country": row[2],
                    "region": row[3],
                    "lon": float(row[4]) if row[4] else None,
                    "lat": float(row[5]) if row[5] else None,
                    "similarity": float(row[6]),
                    "text_cluster": row[7]
                })

            return {"source_city_id": city_id, "band": band, "similar": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()


@router.get("/whc-summaries")
def whc_summaries(city_id: int):
    """Return band summaries for a WHC city."""
    import psycopg
    import os

    try:
        conn = psycopg.connect(
            host=os.environ.get("PGHOST", "localhost"),
            port=os.environ.get("PGPORT", "5435"),
            dbname=os.environ.get("PGDATABASE", "edop"),
            user=os.environ.get("PGUSER", "postgres"),
            password=os.environ.get("PGPASSWORD", ""),
        )
        with conn.cursor() as cur:
            # Get city name
            cur.execute("SELECT city, country FROM wh_cities WHERE id = %s", (city_id,))
            city_row = cur.fetchone()
            if not city_row:
                raise HTTPException(status_code=404, detail="City not found")

            # Get summaries in desired order
            cur.execute("""
                SELECT band, summary
                FROM whc_band_summaries
                WHERE city_id = %s AND status = 'ok'
                ORDER BY CASE band
                    WHEN 'environment' THEN 1
                    WHEN 'history' THEN 2
                    WHEN 'culture' THEN 3
                    WHEN 'modern' THEN 4
                END
            """, (city_id,))

            summaries = []
            for row in cur.fetchall():
                summaries.append({
                    "band": row[0],
                    "summary": row[1]
                })

            return {
                "city_id": city_id,
                "city": city_row[0],
                "country": city_row[1],
                "summaries": summaries
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()


# -----------------------
# Basin Cluster endpoints
# -----------------------

@router.get("/basin-clusters")
def basin_clusters():
    """Return all basin clusters with basin and city counts."""
    import psycopg
    import os

    try:
        conn = psycopg.connect(
            host=os.environ.get("PGHOST", "localhost"),
            port=os.environ.get("PGPORT", "5435"),
            dbname=os.environ.get("PGDATABASE", "edop"),
            user=os.environ.get("PGUSER", "postgres"),
            password=os.environ.get("PGPASSWORD", ""),
        )
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    b.cluster_id,
                    COUNT(DISTINCT b.id) as basin_count,
                    COUNT(DISTINCT c.id) as city_count
                FROM basin08 b
                LEFT JOIN wh_cities c ON c.basin_id = b.id
                WHERE b.cluster_id IS NOT NULL
                GROUP BY b.cluster_id
                ORDER BY b.cluster_id
            """)

            clusters = []
            for row in cur.fetchall():
                clusters.append({
                    "cluster_id": row[0],
                    "basin_count": row[1],
                    "city_count": row[2]
                })

            return {"clusters": clusters}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()


@router.get("/basin-clusters/{cluster_id}/cities")
def basin_cluster_cities(cluster_id: int):
    """Return cities in basins of a given cluster."""
    import psycopg
    import os

    try:
        conn = psycopg.connect(
            host=os.environ.get("PGHOST", "localhost"),
            port=os.environ.get("PGPORT", "5435"),
            dbname=os.environ.get("PGDATABASE", "edop"),
            user=os.environ.get("PGUSER", "postgres"),
            password=os.environ.get("PGPASSWORD", ""),
        )
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    c.id,
                    c.city,
                    c.country,
                    c.region,
                    ST_X(c.geom) as lon,
                    ST_Y(c.geom) as lat
                FROM wh_cities c
                JOIN basin08 b ON c.basin_id = b.id
                WHERE b.cluster_id = %s
                ORDER BY c.country, c.city
            """, (cluster_id,))

            cities = []
            for row in cur.fetchall():
                cities.append({
                    "id": row[0],
                    "city": row[1],
                    "country": row[2],
                    "region": row[3],
                    "lon": float(row[4]) if row[4] else None,
                    "lat": float(row[5]) if row[5] else None
                })

            return {
                "cluster_id": cluster_id,
                "city_count": len(cities),
                "cities": cities
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()