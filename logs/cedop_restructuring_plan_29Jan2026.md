# CEDOP Restructuring Plan

Reorganize the EDOP project into a "Computing Place" umbrella (CEDOP) that can house both EDOP and future CDOP modules.

## Phase 1: Repository and Directory Restructuring

### 1.1 Rename Repository
- Rename GitHub repo from `edop` → `cedop` (via GitHub settings)
- Update local remote: `git remote set-url origin git@github.com:kgeographer/cedop.git`
- Update all documentation references to the repo URL

### 1.2 Reorganize scripts/
**Current:** 41 scripts flat in `scripts/`, plus `scripts/corpus/`

**New structure:**
```
scripts/
├── edop/           # All existing scripts move here
│   ├── corpus/     # Existing corpus scripts
│   ├── basin08_*.py
│   ├── populate_*.py
│   ├── pca_cluster_persist.py
│   └── ... (all current scripts)
├── cdop/           # Empty for now
└── shared/         # Utilities used by both modules
    ├── utils.py
    └── db_utils.py  # (renamed from edop_db.py)
```

### 1.3 Reorganize output/
**Current:** Mixed outputs (basin08_*, corpus/, corpus_258/, dplace/)

**New structure:**
```
output/
├── edop/
│   ├── basin08_*.npy, *.json, *.png
│   ├── corpus/
│   ├── corpus_258/
│   ├── dplace/
│   └── *.tsv, *.jsonl
└── cdop/           # Empty for now
```

### 1.4 Reorganize sql/
**Current:** 17 SQL files, mixed naming

**New structure:**
```
sql/
├── edop/           # EDOP-specific schemas
│   ├── edop_matrix_schema.sql
│   ├── edop_pca_schema.sql
│   ├── edop_gaz_*.sql
│   ├── whc_*.sql
│   ├── basin_atlas_08.sql
│   └── world-heritage.sql
├── cdop/           # Empty for now
└── shared/         # Files related to shared gaz schema
    ├── ecoregions.sql
    └── cliopatria.sql
```

---

## Phase 2: Database Changes

### 2.1 Rename Database
Rename database from `edop` → `cedop`:

```sql
-- On PostgreSQL server (run as superuser, no active connections to edop)
ALTER DATABASE edop RENAME TO cedop;
```

### 2.2 Create CDOP Schema
```sql
-- Connect to cedop database, create cdop schema
CREATE SCHEMA IF NOT EXISTS cdop;
```

### 2.3 Keep Existing Tables in Place
- Existing `edop_*` tables remain in `public` schema (no migration)
- `gaz` schema unchanged (shared gazetteer data)
- New CDOP tables will go in `cdop` schema

### 2.4 Centralize Database Connections
Instead of updating 20+ hardcoded connection strings, create a centralized `db_connect()` function:

**Create `scripts/shared/db_utils.py`** (renamed from edop_db.py):
```python
import os
import psycopg

def db_connect(schema=None):
    """Return a database connection. Optionally set search_path to schema."""
    conn = psycopg.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", "5432"),
        dbname=os.environ.get("PGDATABASE", "cedop"),
        user=os.environ.get("PGUSER"),
        password=os.environ.get("PGPASSWORD")
    )
    if schema:
        conn.execute(f"SET search_path TO {schema}, public")
    return conn
```

**Update app/api/routes.py:**
- Import from shared module or add similar function in app/db/
- Replace all inline `psycopg.connect(...)` calls with `db_connect()`
- Single place to change database name in future

**Update scripts:**
- All scripts import `from scripts.shared.db_utils import db_connect`
- Remove inline connection logic

**Environment files:**
- Local `.env`: `PGDATABASE=cedop`
- (Server updates deferred to Phase 6)

---

## Phase 3: Code Updates

### 3.1 Update Import Paths in Scripts
After moving scripts to `scripts/edop/`, update any relative imports:
- `from utils import ...` → `from scripts.shared.utils import ...`
- Or add `__init__.py` files and use package imports

### 3.2 Update Output Paths in Scripts
Scripts that write to `output/` need path updates:
- `output/basin08_*.npy` → `output/edop/basin08_*.npy`
- `output/corpus/` → `output/edop/corpus/`

### 3.3 Update SQL File References
Scripts loading SQL files need updated paths:
- `sql/edop_matrix_schema.sql` → `sql/edop/edop_matrix_schema.sql`

---

## Phase 4: Application Updates

### 4.1 FastAPI App Structure (Minimal Changes for Now)
Keep current structure but prepare for future CDOP routes:
```
app/
├── main.py              # Keep title="EDOP Pilot" for now
├── api/
│   ├── routes.py        # Current EDOP routes (rename to edop_routes.py later)
│   └── cdop_routes.py   # Future CDOP routes
└── ...
```

### 4.2 Update Hardcoded References
**app/main.py:**
- Keep `title="EDOP Pilot"` for now (FastAPI docs title)

**app/api/routes.py:**
- User-Agent: `"EDOP/1.0"` → `"CEDOP/1.0"` (reflects umbrella project)
- Database connections → use centralized `db_connect()` function

**app/templates/base.html:**
- Title: Keep "EDOP Pilot" (no change)
- Update GitHub link to cedop repo
- About modal: Defer updates

**app/templates/index.html:**
- CSS IDs stay as-is (`edopTabs`) - internal implementation detail
- About modal: Defer updates

---

## Phase 5: Documentation Updates

### 5.1 Files to Update
- `CLAUDE.md` - Update project overview for CEDOP umbrella
- `docs/EDOP_LOG.md` - Add entry for restructuring
- `prompts/seed-prompt-ongoing.md` - Update references
- `README.md` (if exists) - Major rewrite for CEDOP

### 5.2 Create New Documentation
- `docs/CDOP_LOG.md` - Development journal for CDOP (when work begins)
- Update architecture section in CLAUDE.md for new structure

---

## Phase 6: Deployment Updates (DEFERRED)

**Status:** Deferred until CDOP work is publishable.

For now, continue using `edop.kgeographer.org`. When ready:
- Either set up separate `cdop.kgeographer.org`
- Or rework Apache/DNS to serve both from a unified domain

Server changes (deferred):
- Systemd service rename
- Environment file locations
- Code directory rename

---

## Implementation Order

### Local Development First:
1. **Create new directory structure** (scripts/edop, scripts/cdop, scripts/shared, output/edop, output/cdop, sql/edop, sql/cdop, sql/shared)
2. **Move existing files** to new locations
3. **Create db_utils.py** with centralized `db_connect()` function (default: "cedop")
4. **Update import paths** in moved scripts to use shared modules
5. **Refactor routes.py** - replace inline connections with `db_connect()`
6. **Refactor scripts** - use `db_connect()` from shared module
7. **Rename local database**: `ALTER DATABASE edop RENAME TO cedop;`
8. **Update .env**: `PGDATABASE=cedop`
9. **Create cdop schema**: `CREATE SCHEMA cdop;`
10. **Update User-Agent** in routes.py to "CEDOP/1.0"
11. **Update GitHub link** in base.html
12. **Update documentation** (CLAUDE.md, EDOP_LOG.md)
13. **Test locally** - verify all endpoints and UI tabs work

### GitHub (after local testing):
14. **Commit all changes** with descriptive message
15. **Rename GitHub repo** via Settings → `cedop`
16. **Update local remote**: `git remote set-url origin git@github.com:kgeographer/cedop.git`
17. **Push changes**

### Server Deployment (DEFERRED):
- Database rename and config updates deferred until CDOP work is ready

---

## Verification Plan

After restructuring:
1. Run `uvicorn app.main:app --reload` - verify app starts
2. Test `/api/health` endpoint
3. Test `/api/signature?lat=16.76618535&lon=-3.00777252` (Timbuktu)
4. Navigate all UI tabs to verify nothing broke
5. Run a sample script from new location to verify paths work

---

## Files to Modify

**Move/Reorganize:**
- `scripts/*.py` → `scripts/edop/*.py` (except utils.py, edop_db.py)
- `scripts/corpus/` → `scripts/edop/corpus/`
- `scripts/utils.py` → `scripts/shared/utils.py`
- `scripts/edop_db.py` → `scripts/shared/db_utils.py` (rename + enhance with db_connect())
- `output/*` → `output/edop/*`
- `sql/edop_*.sql`, `sql/whc_*.sql`, `sql/basin_atlas_08.sql`, `sql/world-heritage.sql` → `sql/edop/`
- `sql/ecoregions.sql`, `sql/cliopatria.sql` → `sql/shared/`

**Edit (centralize database connections):**
- `scripts/shared/db_utils.py` - Add `db_connect()` function with "cedop" default
- `app/api/routes.py` - Replace ~20+ inline connections with db_connect()
- All scripts - Import and use `db_connect()` from shared module
- `.env` file - Set `PGDATABASE=cedop`

**Edit (branding/documentation):**
- `app/api/routes.py` - User-Agent: "EDOP/1.0" → "CEDOP/1.0"
- `app/templates/base.html` - Update GitHub link to cedop repo
- `CLAUDE.md` - Update project overview for CEDOP umbrella
- `docs/EDOP_LOG.md` - Add restructuring entry

**Edit (import paths after moving scripts):**
- All scripts that import from utils.py or edop_db.py

**Create:**
- `scripts/cdop/__init__.py` (empty)
- `scripts/shared/__init__.py`
- `scripts/edop/__init__.py`
- `output/cdop/` (empty directory)
- `sql/cdop/` (empty directory)

**Database:**
- Rename database: `edop` → `cedop`
- Create schema: `cdop`
