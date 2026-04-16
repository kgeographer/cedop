-- dplace schema: faithful load of D-PLACE CLDF v3.3.0
-- Source: https://zenodo.org/doi/10.5281/zenodo.3935419
-- No modifications to source data; column names lowercased for PostgreSQL.
-- Run once to create; loader script populates.

CREATE SCHEMA IF NOT EXISTS dplace;

-- Contributions (datasets + phylogenies)
CREATE TABLE IF NOT EXISTS dplace.contributions (
    id                  text PRIMARY KEY,
    name                text,
    description         text,
    contributor         text,
    citation            text,
    doi                 text,
    type                text,
    source              text
);

-- Societies (all 6,684 rows: cultural datasets + phylogeny languoids)
CREATE TABLE IF NOT EXISTS dplace.societies (
    id                          text PRIMARY KEY,
    name                        text,
    latitude                    double precision,
    longitude                   double precision,
    glottocode                  text,
    name_and_id_in_source       text,
    xd_id                       text,
    alt_names_by_society        text,
    main_focal_year             integer,
    hraf_name_id                text,
    hraf_id                     text,
    origlat                     double precision,
    origlong                    double precision,
    comment                     text,
    glottocode_comment          text,
    region                      text,
    type                        text,
    language_level_glottocodes  text,
    iso639p3code                text,
    contribution_id             text REFERENCES dplace.contributions(id)
);

CREATE INDEX IF NOT EXISTS idx_dplace_societies_contribution ON dplace.societies(contribution_id);
CREATE INDEX IF NOT EXISTS idx_dplace_societies_xd_id ON dplace.societies(xd_id);

-- Variables (parameters: cultural + environmental)
CREATE TABLE IF NOT EXISTS dplace.variables (
    id              text PRIMARY KEY,
    name            text,
    description     text,
    columnspec      text,
    category        text,
    type            text,
    unit            text,
    source_comment  text,
    changes         text,
    comment         text,
    contribution_id text REFERENCES dplace.contributions(id)
);

CREATE INDEX IF NOT EXISTS idx_dplace_variables_contribution ON dplace.variables(contribution_id);
CREATE INDEX IF NOT EXISTS idx_dplace_variables_category ON dplace.variables(category);

-- Codes (categorical value definitions)
CREATE TABLE IF NOT EXISTS dplace.codes (
    id          text PRIMARY KEY,
    var_id      text REFERENCES dplace.variables(id),
    name        text,
    description text,
    ord         integer
);

CREATE INDEX IF NOT EXISTS idx_dplace_codes_var ON dplace.codes(var_id);

-- Data (677,862 coded datapoints)
CREATE TABLE IF NOT EXISTS dplace.data (
    id                  text PRIMARY KEY,
    soc_id              text REFERENCES dplace.societies(id),
    var_id              text REFERENCES dplace.variables(id),
    value               text,
    code_id             text,
    comment             text,
    source              text,
    sub_case            text,
    year                text,
    source_coded_data   text,
    admin_comment       text
);

CREATE INDEX IF NOT EXISTS idx_dplace_data_soc ON dplace.data(soc_id);
CREATE INDEX IF NOT EXISTS idx_dplace_data_var ON dplace.data(var_id);
CREATE INDEX IF NOT EXISTS idx_dplace_data_soc_var ON dplace.data(soc_id, var_id);
