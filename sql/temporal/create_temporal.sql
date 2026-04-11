-- temporal schema
-- Holds paleoclimate and volcanic forcing datasets for EDOP temporal enrichment.
--
-- Tables:
--   temporal.lmr_pdsi    — LMR v2.1 PDSI reconstruction, 0–1998 CE, 2° grid
--   temporal.evolv2k_v4  — eVolv2k v4 volcanic stratospheric sulfur injection events

CREATE SCHEMA IF NOT EXISTS temporal;

-- ---------------------------------------------------------------------------
-- LMR v2.1 PDSI
-- One row per 2° grid cell. pdsi[] is a 2001-element array of annual ensemble
-- means; index position = year CE (pdsi[0] = year 0, pdsi[536] = year 536, etc.)
-- lon stored as native 0–358 (LMR convention); geom uses -180/180 for spatial ops.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS temporal.lmr_pdsi (
    id      SERIAL PRIMARY KEY,
    lat     REAL NOT NULL,
    lon     REAL NOT NULL,
    pdsi    REAL[] NOT NULL,
    geom    geometry(Point, 4326)
);

CREATE INDEX IF NOT EXISTS lmr_pdsi_geom_idx ON temporal.lmr_pdsi USING GIST (geom);
CREATE INDEX IF NOT EXISTS lmr_pdsi_latlon_idx ON temporal.lmr_pdsi (lat, lon);

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
