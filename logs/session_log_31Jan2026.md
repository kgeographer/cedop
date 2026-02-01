# Session Log: 31 January 2026

## Summary

Extended the UNESCO ICH corpus from 730 to 865 elements by crawling 2024-2025 inscriptions, processing nomination documents through LLM cleaning and extraction, and updating the database with concepts and country codes.

---

## Part 1: ICH Corpus Update Pipeline

### Gap-fill and Discovery
- Ran gap-fill check on pre-2024 elements: 32 now have docs available (132 still missing)
- Downloaded 167 new nomination documents (2024-2025 + gap-fill)
- Text extraction: `textutil` for .doc, `pdftotext` for .pdf files

### Document Cleaning
- Compared heuristic vs LLM cleaning approaches
- LLM cleaning chosen for consistency with existing "clean" files
- **Strict verbatim extraction**: prompt explicitly requires character-for-character text copying
- Verified no paraphrasing/editing by exact phrase matching
- Output: 167 cleaned files in `app/data/ich/cleaned_llm/`

### LLM Extraction
- Adapted extraction script from earlier tier batches
- Schema: `practice_locations`, `diaspora_locations`, `environmental_features`, `coordinates`, `environmental_summary`
- Results: 167/167 successful (0 failures)
- Stats: 3 with explicit coordinates, avg 6.6 practice locations, avg 0.7 diaspora locations

### Consolidation
- Merged three extraction batches:
  - tier_ab: 72 docs
  - tier_cd: 494 docs
  - tier_new: 167 docs
- **Total**: 733 unique extractions (0 duplicates)
- Output: `output/cdop/ich_extractions/consolidated_all.json` (1.7 MB)

---

## Part 2: Database Updates

### New Elements and Summaries
- Loaded 135 new elements from `new_summaries.json` (scraped from landing pages)
- Years: 66 from 2024, 69 from 2025
- List types: RL (116), USL (13), GSP (6)
- Fixed BSP → GSP list type mapping
- Tables updated: `cdop.ich_elements`, `cdop.ich_summaries`
- **Total elements now**: 865 (was 730)

### Concept and Country Code Scraping
- Created scraper for ICH landing pages
- Extracted from HTML:
  - Country codes from `/state/country-XX` URLs
  - Primary concepts from `<a class="link primary">`
  - Secondary concepts from `<a class="link secondary">`
- Rate-limited (1s delay), with checkpoint caching
- Results: 135/135 ccodes, 134/135 primary concepts (1 legitimately empty)

---

## Scripts Created

| Script | Purpose |
|--------|---------|
| `ich_corpus_update.py` | UNESCO website crawler (discover, fetch, gap-check) |
| `ich_clean_compare.py` | Compare heuristic vs LLM cleaning |
| `ich_clean_batch.py` | Batch LLM cleaning with verbatim extraction |
| `ich_llm_extract_new.py` | Structured LLM extraction for new docs |
| `ich_consolidate_extractions.py` | Merge extraction batches |
| `ich_load_new_elements.py` | Load elements/summaries to database |
| `ich_scrape_concepts.py` | Scrape concepts and ccodes from landing pages |

---

## Output Files

- `output/cdop/ich_extractions/consolidated_all.json` — 733 structured extractions
- `output/cdop/ich_extractions/tier_new_2026-01.json` — 167 new extractions
- `output/cdop/ich_update/new_summaries.json` — 135 landing page summaries
- `output/cdop/ich_update/gap_check_report.json` — gap-fill status
- `output/cdop/ich_update/concept_scrape_cache.json` — scraped concepts cache
- `app/data/ich/cleaned_llm/` — 167 cleaned document texts

---

## Database State

**`cdop.ich_elements`** (865 rows):
- All 2024-2025 elements have: ich_id, label, countries, year, list, link, ccodes, primary_concepts, secondary_concepts

**`cdop.ich_summaries`** (865 rows):
- Landing page summary text for each element

**Extractions** kept as JSON (not in database):
- Complex nested structure (practice_locations array, diaspora_locations array, etc.)
- JSONB column considered but deferred for now

---

## Decisions Made

1. **LLM cleaning over heuristic**: PDF formatting defeated simple pattern matching
2. **Verbatim extraction**: User requirement - no paraphrasing allowed
3. **Keep extractions as JSON**: Complex schema would require 4+ related tables; JSON queryable with Python/jq
4. **JSONB option noted**: Single table with JSONB column would be pragmatic middle ground if DB needed later
