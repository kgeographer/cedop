-- seshat schema: faithful load of Seshat Global History Databank
-- Sources: general_data and social_complexity_data exports (2026-04-16)
-- Pipe-delimited CSV; long format (one row per polity × variable × time slice)
-- Join to gaz.clio_polities via: seshat.*.polity_new_id = gaz.clio_polities.seshatid

CREATE SCHEMA IF NOT EXISTS seshat;

-- General Variables (544 unique polities, 23 variables, 8,170 rows)
CREATE TABLE IF NOT EXISTS seshat.general (
    id                  serial PRIMARY KEY,
    section             text,
    subsection          text,
    polity_name         text,
    polity_new_id       text,
    polity_old_id       text,
    variable_name       text,
    value_from          text,
    value_to            text,
    year_from           integer,
    year_to             integer,
    confidence          text,
    is_disputed         boolean,
    is_uncertain        boolean,
    expert_checked      boolean
);

CREATE INDEX IF NOT EXISTS idx_seshat_general_polity  ON seshat.general(polity_new_id);
CREATE INDEX IF NOT EXISTS idx_seshat_general_var     ON seshat.general(variable_name);
CREATE INDEX IF NOT EXISTS idx_seshat_general_years   ON seshat.general(year_from, year_to);

-- Social Complexity Variables (621 unique polities, 77 variables, 26,164 rows)
CREATE TABLE IF NOT EXISTS seshat.social (
    id                  serial PRIMARY KEY,
    subsection          text,
    variable_name       text,
    year_from           integer,
    year_to             integer,
    polity_name         text,
    polity_new_id       text,
    polity_old_id       text,
    value_from          text,
    value_to            text,
    confidence          text,
    is_disputed         boolean,
    is_uncertain        boolean,
    expert_checked      boolean,
    drb_reviewed        boolean
);

CREATE INDEX IF NOT EXISTS idx_seshat_social_polity   ON seshat.social(polity_new_id);
CREATE INDEX IF NOT EXISTS idx_seshat_social_var      ON seshat.social(variable_name);
CREATE INDEX IF NOT EXISTS idx_seshat_social_years    ON seshat.social(year_from, year_to);
