-- temporal schema
-- Holds paleoclimate and volcanic forcing datasets for EDOP temporal enrichment.
--
-- Tables:
--   temporal.lmr_climate    — LMR v2.1 climate reconstructions (PDSI, air temp, prate), 0–1998 CE, 2° grid
--   temporal.evolv2k_v4  — eVolv2k v4 volcanic stratospheric sulfur injection events

CREATE SCHEMA IF NOT EXISTS temporal;

-- ---------------------------------------------------------------------------
-- LMR v2.1 climate grid
-- One row per 2° grid cell. Each variable is a 2001-element real[] array of annual
-- ensemble means; index position = year CE (arr[1] = year 0 CE in PostgreSQL 1-indexing).
-- lon stored as native 0–358 (LMR convention); geom uses -180/180 for spatial ops.
-- Columns: pdsi (Palmer DSI), air (2m temperature, K), prate (precip rate, kg/m²/s)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS temporal.lmr_climate (
    id      SERIAL PRIMARY KEY,
    lat     REAL NOT NULL,
    lon     REAL NOT NULL,
    pdsi    REAL[] NOT NULL,
    geom    geometry(Point, 4326)
);

CREATE INDEX IF NOT EXISTS lmr_climate_geom_idx ON temporal.lmr_climate USING GIST (geom);
CREATE INDEX IF NOT EXISTS lmr_climate_latlon_idx ON temporal.lmr_climate (lat, lon);

-- ---------------------------------------------------------------------------
-- eVolv2k v4  (Sigl & Toohey 2024)
-- One row per eruption event. year_ad is negative for BCE.
-- vssi_tg is the key forcing variable (volcanic stratospheric sulfur injection, Tg).
-- asymmetry: 1.0 = NH only, 0.0 = SH only, 0.5 = equatorial/global.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS temporal.evolv2k_v4 (
    id          SERIAL PRIMARY KEY,
    year_ad     SMALLINT NOT NULL,
    month       SMALLINT,
    day         SMALLINT,
    lat         REAL,
    so4_grl     REAL,
    so4_ant     REAL,
    vssi_tg     REAL NOT NULL,
    vssi_1sig   REAL,
    asymmetry   REAL,
    location    TEXT,
    tephra      BOOLEAN,
    reference   TEXT
);

CREATE INDEX IF NOT EXISTS evolv2k_year_idx ON temporal.evolv2k_v4 (year_ad);
