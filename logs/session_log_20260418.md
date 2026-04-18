# Session Log — 2026-04-18

## Summary

Two threads: (1) edops.kgeographer.org deployment and routing restructure (continued from Apr 17); (2) data exploration phase planning and repo scaffolding.

---

## 1. Routing and deployment (continued)

Resolved remaining issues from Apr 17 routing work:

- `edops.kgeographer.org/` now serves EDOPS landing page directly (no URL redirect) via host-based routing in `pages.py` — checks `Host` header, serves `edops.html` when host contains "edops", `index.html` otherwise
- Fixed erroneous `proxy_pass http://127.0.0.1:8001/edops` in cedop nginx block (left over from failed nginx rewrite attempt); restored to `http://127.0.0.1:8001`
- sandbox header: `EDOP` → `EDOPS`, link updated to `/edops`
- index.html EDOP tile: `/edop` → `/edops`
- All routes verified live on production

---

## 2. Data exploration phase

### Context

Following a strategic session with Opus on next steps, the data exploration phase was defined as the immediate priority — systematic characterization of the EDOPS signature dataset before correspondence testing, PCA, or rubric design. Key framing from that session:

- Marginal distributions for all scalar variables globally are prerequisite working knowledge
- The local/upstream divergence distribution (where does Ur sit globally?) is the quantitative foundation for the s/u duality claim
- Do not start D-PLACE correspondence testing until exploration findings are documented
- Band F detail=summary mode (means/ranges only, no annual arrays) is worth adding before batch exploration runs

### Files created

- **`docs/edop/data_exploration.md`** — task list, conventions, guardrails, directory conventions, exploration log format
- **`scripts/edop/explore/`** — exploration scripts directory (with .gitkeep)
- **`notebooks/edop/explore/`** — exploration notebooks directory (with .gitkeep)
- **`output/edop/explore/`** — exploration outputs directory (gitignored)
- **`logs/exploration_log.md`** — accreting findings log, seeded empty

### CLAUDE.md updates

- Directory structure updated (new templates, explore/ dirs, logs structure)
- Page routes updated (edops, sandbox, workbench, /edop redirect)
- Sandbox and Workbench sections added/updated
- Deployment section: both URLs documented
- New "Data Exploration Phase" section added with task summary and guardrails

---

## Files changed

- `app/web/pages.py` — host-based routing for edops.kgeographer.org
- `app/templates/sandbox.html` — header EDOPS label + link fix
- `app/templates/index.html` — EDOP tile → /edops
- `CLAUDE.md` — structure, routes, deployment, exploration phase section
- `docs/edop/data_exploration.md` — new exploration phase document
- `logs/exploration_log.md` — new accreting findings log
- `scripts/edop/explore/.gitkeep` — directory scaffold
- `notebooks/edop/explore/.gitkeep` — directory scaffold
