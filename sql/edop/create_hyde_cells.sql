-- sql/edop/create_hyde_cells.sql
-- HYDE 3.4 land-use cell table and time-step reference.
--
-- temporal.hyde_times  : 128-row lookup, array index → year (astronomical, year 0 = 1 BCE)
-- temporal.hyde_cells  : one row per HYDE land cell (2,215,829 rows)
--                        geometry = 5-arcmin cell polygon, EPSG:4326
--                        array columns = 128 time steps, values in km²
--
-- Load order: run this file, then load_hyde_cells.py (populates both tables,
-- computes area_km2 via ST_Area, builds GIST index).

CREATE TABLE IF NOT EXISTS temporal.hyde_times (
    step_idx  smallint PRIMARY KEY,   -- 0-based index into cell array columns
    year_ce   integer  NOT NULL       -- astronomical year (negative = BCE, 0 = 1 BCE)
);

CREATE TABLE IF NOT EXISTS temporal.hyde_cells (
    cell_id   integer                  PRIMARY KEY,
    geom      geometry(Polygon, 4326)  NOT NULL,
    area_km2  real,                               -- km², filled after load via ST_Area
    cropland  real[]                   NOT NULL,  -- km² per cell, 128 time steps
    grazing   real[]                   NOT NULL,
    pasture   real[]                   NOT NULL,
    rangeland real[]                   NOT NULL
);

-- Indexes built by load script after data is loaded (faster than building during insert):
--   idx_hyde_cells_geom     — GIST on geom (polygon bounding-box queries)
--   idx_hyde_cells_centroid — GIST on ST_Centroid(geom) (polygon-interior aggregation predicate)
-- ANALYZE run after indexes to freshen planner statistics.
