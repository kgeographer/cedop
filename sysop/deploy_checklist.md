# CEDOP Deployment Checklist

**Keep this current.** When you make a local schema change or data load, add it here immediately.

## Standard Deploy Steps

```bash
# On kgeographer-1:
cd /var/www/cedop && git pull
sudo systemctl restart cedop
sudo systemctl status cedop
```

## One-Time / Already Done on Hetzner

- [x] `pip install anthropic` (2026-04-14)
- [x] `pg_restore` `public.basin06` from local dump (2026-04-14)
- [x] `pg_restore` `gaz.hydrorivers` from local dump (2026-04-14)
- [x] `ALTER TABLE public.basin08 ADD COLUMN geog geography(MultiPolygon, 4326)` + populate + GIST index (2026-04-14)
- [x] Create view `public.v_basin08_persist_rev1` via `sql/edop/sig/persist_view_rev1.sql` (2026-04-14)
- [x] `CREATE INDEX idx_basin08_geog ON public.basin08 USING GIST (geog);` (2026-04-14)

## Pending / Next Deploy

- [ ] `ALTER TABLE temporal.lmr_pdsi RENAME TO lmr_climate;`
- [ ] Copy `data/lmr_v2.1/air_MCruns_ensemble_mean_LMRv2.1.nc` and `prate_MCruns_ensemble_mean_LMRv2.1.nc` to Hetzner
- [ ] Run `~/envs/cedop/bin/python3 scripts/edop/load_temporal.py --air --prate` on Hetzner

## Template: New Schema Change Entry

```
- [ ] <description> — run: `<command or file>`  (added: YYYY-MM-DD)
```
