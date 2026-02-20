-- Basin cluster labels table
-- Maps cluster_id (from basin08.cluster_id / basin08_pca_clusters) to a descriptive label.
-- Populated by scripts/edop/populate_basin_cluster_labels.py from basin08_cluster_labels_manual.json.
-- Re-run that script after any re-clustering to update labels.

CREATE TABLE IF NOT EXISTS basin_cluster_labels (
    cluster_id  INTEGER PRIMARY KEY,
    label       TEXT    NOT NULL
);
