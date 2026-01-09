-- Schema for WHC Wikipedia text/semantic data
-- Parallels edop_band_* tables but uses whc_ prefix

-- Band summaries (LLM-generated summaries per city per band)
DROP TABLE IF EXISTS whc_band_summaries CASCADE;
CREATE TABLE whc_band_summaries (
    city_id INTEGER NOT NULL REFERENCES wh_cities(id),
    band TEXT NOT NULL CHECK (band IN ('history', 'environment', 'culture', 'modern')),
    status TEXT NOT NULL,  -- 'ok' or 'no_content'
    summary TEXT,
    source_chars INTEGER,
    summary_chars INTEGER,
    input_tokens INTEGER,
    output_tokens INTEGER,
    processed_at TIMESTAMP,
    PRIMARY KEY (city_id, band)
);

-- Band clusters (k-means cluster assignments from text embeddings)
DROP TABLE IF EXISTS whc_band_clusters CASCADE;
CREATE TABLE whc_band_clusters (
    city_id INTEGER NOT NULL REFERENCES wh_cities(id),
    band TEXT NOT NULL CHECK (band IN ('history', 'environment', 'culture', 'modern', 'composite')),
    cluster_id INTEGER NOT NULL,
    distance_to_centroid DOUBLE PRECISION,
    PRIMARY KEY (city_id, band)
);

-- Band similarity (top-10 most similar cities per band)
DROP TABLE IF EXISTS whc_band_similarity CASCADE;
CREATE TABLE whc_band_similarity (
    city_a INTEGER NOT NULL REFERENCES wh_cities(id),
    city_b INTEGER NOT NULL REFERENCES wh_cities(id),
    band TEXT NOT NULL CHECK (band IN ('history', 'environment', 'culture', 'modern', 'composite')),
    similarity DOUBLE PRECISION NOT NULL,
    rank INTEGER NOT NULL,  -- 1-10 rank among top similar
    PRIMARY KEY (city_a, band, rank)
);

CREATE INDEX idx_whc_band_similarity_city_b ON whc_band_similarity(city_b);
CREATE INDEX idx_whc_band_similarity_band ON whc_band_similarity(band);

-- Metadata about the embedding model and clustering config
DROP TABLE IF EXISTS whc_band_metadata CASCADE;
CREATE TABLE whc_band_metadata (
    id INTEGER PRIMARY KEY DEFAULT 1 CHECK (id = 1),
    embedding_model TEXT NOT NULL,
    n_clusters INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE whc_band_summaries IS 'LLM-generated summaries of Wikipedia content per city per semantic band';
COMMENT ON TABLE whc_band_clusters IS 'K-means cluster assignments from text embedding similarity';
COMMENT ON TABLE whc_band_similarity IS 'Top-10 most similar cities by text embedding per band';
COMMENT ON TABLE whc_band_metadata IS 'Configuration metadata for embedding/clustering';
