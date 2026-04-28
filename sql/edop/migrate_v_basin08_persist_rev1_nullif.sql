-- migrate_basin_persist_rev1_nullif.sql
-- Fix F1.1: apply NULLIF(col, -9999) to six columns that use -9999 as NoData
-- sentinel in basin08 and basin06. Previously these passed through raw,
-- producing invalid statistics downstream.
--
-- Affected columns (from exploration Task 1 / F1.1):
--   slp_dg_sav (3.4% sentinel), slp_dg_uav (3.4%), sgr_dk_sav (4.1%),
--   cly_pc_sav / slt_pc_sav / snd_pc_sav (9.1% each)
--
-- Applied to both v_basin08_persist_rev1 and v_basin06_persist_rev1.
-- 2026-04-28

CREATE OR REPLACE VIEW v_basin08_persist_rev1 AS
SELECT
    b.id,
    b.clz_cl_smj                              AS zone_id,
    z.genz_name                               AS zone_name,
    b.cls_cl_smj                              AS strata_id,
    s.gens_code                               AS strata_code,
    b.glc_cl_smj                              AS land_cover_id,
    g.glc_name                                AS land_cover_name,
    b.ele_mt_smn                              AS elev_min,
    b.ele_mt_smx                              AS elev_max,
    NULLIF(b.slp_dg_sav, -9999)              AS slope_avg,
    NULLIF(b.slp_dg_uav, -9999)              AS slope_upstream,
    NULLIF(b.sgr_dk_sav, -9999)              AS stream_gradient,
    b.lit_cl_smj                              AS lithology,
    l.class_name                              AS lith_class,
    b.kar_pc_sse                              AS karst,
    b.kar_pc_use                              AS karst_upstream,
    b.dis_m3_pyr                              AS discharge_yr,
    b.dis_m3_pmn                              AS discharge_min,
    b.dis_m3_pmx                              AS discharge_max,
    b.ria_ha_ssu                              AS river_area,
    b.ria_ha_usu                              AS river_area_upstream,
    b.run_mm_syr                              AS runoff,
    b.gwt_cm_sav                              AS gw_table_depth,
    b.wet_pc_sg1                              AS wet_pct_grp1,
    b.wet_pc_sg2                              AS wet_pct_grp2,
    b.wet_pc_ug1                              AS wet_pct_grp1_upstream,
    b.wet_pc_ug2                              AS wet_pct_grp2_upstream,
    b.wet_cl_smj                              AS wetland_class_id,
    w.glwd_name                               AS wetland_class,
    b.rev_mc_usu                              AS reservoir_vol,
    NULLIF(b.cly_pc_sav, -9999)              AS pct_clay,
    NULLIF(b.slt_pc_sav, -9999)              AS pct_silt,
    NULLIF(b.snd_pc_sav, -9999)              AS pct_sand,
    b.cly_pc_uav                              AS pct_clay_upstream,
    b.slt_pc_uav                              AS pct_silt_upstream,
    b.snd_pc_uav                              AS pct_sand_upstream,
    b.tmp_dc_syr::numeric / 10.0             AS temp_yr,
    b.tmp_dc_smn::numeric / 10.0             AS temp_min,
    b.tmp_dc_smx::numeric / 10.0             AS temp_max,
    b.tmp_dc_uyr::numeric / 10.0             AS temp_yr_upstream,
    b.pre_mm_syr                              AS precip_yr,
    b.pre_mm_uyr                              AS precip_yr_upstream,
    b.ari_ix_sav                              AS aridity,
    b.ari_ix_uav                              AS aridity_upstream,
    b.prm_pc_sse                              AS permafrost_extent,
    b.tbi_cl_smj                              AS biome_id,
    tb.biome_name                             AS biome,
    b.tec_cl_smj                              AS eco_id,
    te.ecoregion_name                         AS ecoregion,
    b.fmh_cl_smj                              AS freshwater_type,
    fm.mht_name                               AS freshwater_ecoregion_class,
    b.fec_cl_smj                              AS freshwater_ecoreg,
    fe.ecoregion_name                         AS freshwater_ecoregion_name,
    b.pnv_cl_smj                              AS pnveg_id,
    p.pnv_name                                AS pnv_majority,
    pnv.pnv_shares,
    b.crp_pc_sse                              AS cropland_extent,
    b.crp_pc_use                              AS cropland_extent_upstream,
    b.ppd_pk_sav                              AS pop_density,
    b.hft_ix_s09                              AS human_footprint_09,
    b.hft_ix_u09                              AS human_footprint_09_upstream,
    b.gdp_ud_sav                              AS gdp_avg,
    b.hdi_ix_sav::numeric / 1000.0           AS human_dev_idx,
    b.dist_sink,
    b.endo                                    AS endorheic,
    b.coast                                   AS coast_flag,
    b.up_area,
    b.geom
FROM basin08 b
LEFT JOIN lu_cls  s  ON s.gens_id::text = b.cls_cl_smj::character varying::text
LEFT JOIN lu_fec  fe ON fe.eco_id = b.fec_cl_smj
LEFT JOIN lu_fmh  fm ON fm.mht_id = b.fmh_cl_smj
LEFT JOIN lu_glc  g  ON g.glc_id::text = b.glc_cl_smj::character varying::text
LEFT JOIN lu_clz  z  ON z.genz_id = b.clz_cl_smj
LEFT JOIN lu_lit  l  ON l.glim_id = b.lit_cl_smj
LEFT JOIN lu_pnv  p  ON p.pnv_id = b.pnv_cl_smj
LEFT JOIN LATERAL (
    SELECT jsonb_object_agg(lp.pnv_name, v.pct) AS pnv_shares
    FROM (VALUES
        (1,b.pnv_pc_s01),(2,b.pnv_pc_s02),(3,b.pnv_pc_s03),(4,b.pnv_pc_s04),
        (5,b.pnv_pc_s05),(6,b.pnv_pc_s06),(7,b.pnv_pc_s07),(8,b.pnv_pc_s08),
        (9,b.pnv_pc_s09),(10,b.pnv_pc_s10),(11,b.pnv_pc_s11),(12,b.pnv_pc_s12),
        (13,b.pnv_pc_s13),(14,b.pnv_pc_s14),(15,b.pnv_pc_s15)
    ) v(pnv_id, pct)
    JOIN lu_pnv lp ON lp.pnv_id = v.pnv_id
    WHERE v.pct IS NOT NULL AND v.pct > 0
) pnv ON true
LEFT JOIN lu_tbi  tb ON tb.biome_id = b.tbi_cl_smj
LEFT JOIN lu_tec  te ON te.eco_id = b.tec_cl_smj
LEFT JOIN lu_wet  w  ON w.glwd_id = b.wet_cl_smj;

-- Same fix for L6 view (identical structure, basin06 source table)
CREATE OR REPLACE VIEW v_basin06_persist_rev1 AS
SELECT
    b.id,
    b.clz_cl_smj                              AS zone_id,
    z.genz_name                               AS zone_name,
    b.cls_cl_smj                              AS strata_id,
    s.gens_code                               AS strata_code,
    b.glc_cl_smj                              AS land_cover_id,
    g.glc_name                                AS land_cover_name,
    b.ele_mt_smn                              AS elev_min,
    b.ele_mt_smx                              AS elev_max,
    NULLIF(b.slp_dg_sav, -9999)              AS slope_avg,
    NULLIF(b.slp_dg_uav, -9999)              AS slope_upstream,
    NULLIF(b.sgr_dk_sav, -9999)              AS stream_gradient,
    b.lit_cl_smj                              AS lithology,
    l.class_name                              AS lith_class,
    b.kar_pc_sse                              AS karst,
    b.kar_pc_use                              AS karst_upstream,
    b.dis_m3_pyr                              AS discharge_yr,
    b.dis_m3_pmn                              AS discharge_min,
    b.dis_m3_pmx                              AS discharge_max,
    b.ria_ha_ssu                              AS river_area,
    b.ria_ha_usu                              AS river_area_upstream,
    b.run_mm_syr                              AS runoff,
    b.gwt_cm_sav                              AS gw_table_depth,
    b.wet_pc_sg1                              AS wet_pct_grp1,
    b.wet_pc_sg2                              AS wet_pct_grp2,
    b.wet_pc_ug1                              AS wet_pct_grp1_upstream,
    b.wet_pc_ug2                              AS wet_pct_grp2_upstream,
    b.wet_cl_smj                              AS wetland_class_id,
    w.glwd_name                               AS wetland_class,
    b.rev_mc_usu                              AS reservoir_vol,
    NULLIF(b.cly_pc_sav, -9999)              AS pct_clay,
    NULLIF(b.slt_pc_sav, -9999)              AS pct_silt,
    NULLIF(b.snd_pc_sav, -9999)              AS pct_sand,
    b.cly_pc_uav                              AS pct_clay_upstream,
    b.slt_pc_uav                              AS pct_silt_upstream,
    b.snd_pc_uav                              AS pct_sand_upstream,
    b.tmp_dc_syr::numeric / 10.0             AS temp_yr,
    b.tmp_dc_smn::numeric / 10.0             AS temp_min,
    b.tmp_dc_smx::numeric / 10.0             AS temp_max,
    b.tmp_dc_uyr::numeric / 10.0             AS temp_yr_upstream,
    b.pre_mm_syr                              AS precip_yr,
    b.pre_mm_uyr                              AS precip_yr_upstream,
    b.ari_ix_sav                              AS aridity,
    b.ari_ix_uav                              AS aridity_upstream,
    b.prm_pc_sse                              AS permafrost_extent,
    b.tbi_cl_smj                              AS biome_id,
    tb.biome_name                             AS biome,
    b.tec_cl_smj                              AS eco_id,
    te.ecoregion_name                         AS ecoregion,
    b.fmh_cl_smj                              AS freshwater_type,
    fm.mht_name                               AS freshwater_ecoregion_class,
    b.fec_cl_smj                              AS freshwater_ecoreg,
    fe.ecoregion_name                         AS freshwater_ecoregion_name,
    b.pnv_cl_smj                              AS pnveg_id,
    p.pnv_name                                AS pnv_majority,
    pnv.pnv_shares,
    b.crp_pc_sse                              AS cropland_extent,
    b.crp_pc_use                              AS cropland_extent_upstream,
    b.ppd_pk_sav                              AS pop_density,
    b.hft_ix_s09                              AS human_footprint_09,
    b.hft_ix_u09                              AS human_footprint_09_upstream,
    b.gdp_ud_sav                              AS gdp_avg,
    b.hdi_ix_sav::numeric / 1000.0           AS human_dev_idx,
    b.dist_sink,
    b.endo                                    AS endorheic,
    b.coast                                   AS coast_flag,
    b.up_area,
    b.geom
FROM basin06 b
LEFT JOIN lu_cls  s  ON s.gens_id::text = b.cls_cl_smj::character varying::text
LEFT JOIN lu_fec  fe ON fe.eco_id = b.fec_cl_smj
LEFT JOIN lu_fmh  fm ON fm.mht_id = b.fmh_cl_smj
LEFT JOIN lu_glc  g  ON g.glc_id::text = b.glc_cl_smj::character varying::text
LEFT JOIN lu_clz  z  ON z.genz_id = b.clz_cl_smj
LEFT JOIN lu_lit  l  ON l.glim_id = b.lit_cl_smj
LEFT JOIN lu_pnv  p  ON p.pnv_id = b.pnv_cl_smj
LEFT JOIN LATERAL (
    SELECT jsonb_object_agg(lp.pnv_name, v.pct) AS pnv_shares
    FROM (VALUES
        (1,b.pnv_pc_s01),(2,b.pnv_pc_s02),(3,b.pnv_pc_s03),(4,b.pnv_pc_s04),
        (5,b.pnv_pc_s05),(6,b.pnv_pc_s06),(7,b.pnv_pc_s07),(8,b.pnv_pc_s08),
        (9,b.pnv_pc_s09),(10,b.pnv_pc_s10),(11,b.pnv_pc_s11),(12,b.pnv_pc_s12),
        (13,b.pnv_pc_s13),(14,b.pnv_pc_s14),(15,b.pnv_pc_s15)
    ) v(pnv_id, pct)
    JOIN lu_pnv lp ON lp.pnv_id = v.pnv_id
    WHERE v.pct IS NOT NULL AND v.pct > 0
) pnv ON true
LEFT JOIN lu_tbi  tb ON tb.biome_id = b.tbi_cl_smj
LEFT JOIN lu_tec  te ON te.eco_id = b.tec_cl_smj
LEFT JOIN lu_wet  w  ON w.glwd_id = b.wet_cl_smj;
