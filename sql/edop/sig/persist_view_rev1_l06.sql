-- v_basin06_persist_rev1
-- Same structure as v_basin08_persist_rev1, sourced from basin06 (BasinATLAS Level 06).
-- 16,397 basins globally; Timbuktu assignment: ~382,644 km² upstream (Niger regional basin).

CREATE OR REPLACE VIEW v_basin06_persist_rev1 AS
SELECT
  b.id,
  b.clz_cl_smj AS zone_id,
  z.genz_name  AS zone_name,
  b.cls_cl_smj AS strata_id,
  s.gens_code  AS strata_code,
  b.glc_cl_smj AS land_cover_id,
  g.glc_name   AS land_cover_name,

-- A: Physiographic
  b.ele_mt_smn AS elev_min,
  b.ele_mt_smx AS elev_max,
  b.slp_dg_sav AS slope_avg,
  b.slp_dg_uav AS slope_upstream,
  b.sgr_dk_sav AS stream_gradient,
  b.lit_cl_smj AS lithology,
  l.class_name AS lith_class,
  b.kar_pc_sse AS karst,
  b.kar_pc_use AS karst_upstream,

-- B: Hydroclimatic
  b.dis_m3_pyr AS discharge_yr,
  b.dis_m3_pmn AS discharge_min,
  b.dis_m3_pmx AS discharge_max,
  b.ria_ha_ssu AS river_area,
  b.ria_ha_usu AS river_area_upstream,
  b.run_mm_syr AS runoff,
  b.gwt_cm_sav AS gw_table_depth,
  b.wet_pc_sg1 AS wet_pct_grp1,
  b.wet_pc_sg2 AS wet_pct_grp2,
  b.wet_pc_ug1 AS wet_pct_grp1_upstream,
  b.wet_pc_ug2 AS wet_pct_grp2_upstream,
  b.wet_cl_smj AS wetland_class_id,
  w.glwd_name  AS wetland_class,
  b.rev_mc_usu AS reservoir_vol,
  b.cly_pc_sav AS pct_clay,
  b.slt_pc_sav AS pct_silt,
  b.snd_pc_sav AS pct_sand,
  b.cly_pc_uav AS pct_clay_upstream,
  b.slt_pc_uav AS pct_silt_upstream,
  b.snd_pc_uav AS pct_sand_upstream,

-- C: Bioclimatic
  b.tmp_dc_syr / 10.0 AS temp_yr,
  b.tmp_dc_smn / 10.0 AS temp_min,
  b.tmp_dc_smx / 10.0 AS temp_max,
  b.tmp_dc_uyr / 10.0 AS temp_yr_upstream,
  b.pre_mm_syr        AS precip_yr,
  b.pre_mm_uyr        AS precip_yr_upstream,
  b.ari_ix_sav        AS aridity,
  b.ari_ix_uav        AS aridity_upstream,
  b.prm_pc_sse        AS permafrost_extent,
  b.tbi_cl_smj        AS biome_id,
  tb.biome_name       AS biome,
  b.tec_cl_smj        AS eco_id,
  te.ecoregion_name   AS ecoregion,
  b.fmh_cl_smj        AS freshwater_type,
  fm.mht_name         AS freshwater_ecoregion_class,
  b.fec_cl_smj        AS freshwater_ecoreg,
  fe.ecoregion_name   AS freshwater_ecoregion_name,
  b.pnv_cl_smj        AS pnveg_id,
  p.pnv_name          AS pnv_majority,
  pnv.pnv_shares      AS pnv_shares,

-- D: Anthropocene
  b.crp_pc_sse AS cropland_extent,
  b.crp_pc_use AS cropland_extent_upstream,
  b.ppd_pk_sav AS pop_density,
  b.hft_ix_s09 AS human_footprint_09,
  b.hft_ix_u09 AS human_footprint_09_upstream,
  b.gdp_ud_sav AS gdp_avg,
  b.hdi_ix_sav / 1000.0 AS human_dev_idx,

-- Coastality
  b.dist_sink  AS dist_sink,
  b.endo       AS endorheic,
  b.coast      AS coast_flag,

-- Scale
  b.up_area    AS up_area,

  b.geom

FROM public.basin06 b
LEFT JOIN public.lu_cls s
  ON s.gens_id = b.cls_cl_smj::varchar
LEFT JOIN public.lu_fec fe
  ON fe.eco_id = b.fec_cl_smj
LEFT JOIN public.lu_fmh fm
  ON fm.mht_id = b.fmh_cl_smj
LEFT JOIN public.lu_glc g
  ON g.glc_id = b.glc_cl_smj::varchar
LEFT JOIN public.lu_clz z
  ON z.genz_id = b.clz_cl_smj
LEFT JOIN public.lu_lit l
  ON l.glim_id = b.lit_cl_smj
LEFT JOIN public.lu_pnv p
  ON p.pnv_id = b.pnv_cl_smj
LEFT JOIN LATERAL (
  SELECT jsonb_object_agg(lp.pnv_name, v.pct) AS pnv_shares
  FROM (VALUES
    (1,  b.pnv_pc_s01), (2,  b.pnv_pc_s02), (3,  b.pnv_pc_s03),
    (4,  b.pnv_pc_s04), (5,  b.pnv_pc_s05), (6,  b.pnv_pc_s06),
    (7,  b.pnv_pc_s07), (8,  b.pnv_pc_s08), (9,  b.pnv_pc_s09),
    (10, b.pnv_pc_s10), (11, b.pnv_pc_s11), (12, b.pnv_pc_s12),
    (13, b.pnv_pc_s13), (14, b.pnv_pc_s14), (15, b.pnv_pc_s15)
  ) AS v(pnv_id, pct)
  JOIN public.lu_pnv lp ON lp.pnv_id = v.pnv_id
  WHERE v.pct IS NOT NULL AND v.pct > 0
) pnv ON TRUE
LEFT JOIN public.lu_tbi tb
  ON tb.biome_id = b.tbi_cl_smj
LEFT JOIN public.lu_tec te
  ON te.eco_id = b.tec_cl_smj
LEFT JOIN public.lu_wet w
  ON w.glwd_id = b.wet_cl_smj;
