# Session Log: 30 January 2026

## Summary

Completed ICH data exploration (4 phases) and prototyped an LLM-based extraction pipeline to address toponym normalization challenges that prevented WHG integration.

---

## Part 1: ICH Data Exploration (Phases 1-4)

Executed the planned exploration of UNESCO Intangible Cultural Heritage data in `cdop` schema.

### Phase 1: Concept Taxonomy Analysis
- 423 distinct concepts identified
- 6 environmental concepts: Mountains (71), Grasslands (35), Marine/coastal (33), Drylands (29), Forests (27), Inland wetlands (9)
- Vocal music is the strongest co-occurring cultural practice with environmental concepts

### Phase 2: Geographic Analysis
- Top countries: China (43), Türkiye (30), France (28), Spain (25)
- Top UN subregion: Southern Europe (92 elements)
- Multinational max: Falconry (24 countries)
- 16 country names need mapping to `gaz.admin0`
- Identified cultural diffusion zones: MENA/Arab, Turkic/Central Asian, Mediterranean European

### Phase 3: Text Analysis
- 730 summaries, avg 1,213 chars / 186 words
- 85% fall in 1000-1500 char range (consistent)
- 54 elements have short summaries (<500 chars)
- Embedding cost estimate: ~$0.02 for OpenAI ada-002

### Phase 4: Toponym Quality Assessment
- 5,116 cleaned toponyms across 552 elements
- **81.8% are sub-country level** (need geocoding)
- Only 18.2% match country names (easy)
- `fclasses` field is useless (all identical: S;P;A;H;T;R)
- Key problems identified:
  - Diaspora pollution (migration destinations mixed with practice locations)
  - Non-standard romanization (Persian transliteration issues)
  - No admin hierarchy context

**Output:** `docs/cdop/ich_exploration_summary.md`

**Scripts created:**
- `scripts/cdop/ich_explore_concepts.py`
- `scripts/cdop/ich_explore_geography.py`
- `scripts/cdop/ich_explore_text.py`
- `scripts/cdop/ich_explore_toponyms.py`

---

## Part 2: Git Operations

### Commit and Merge
- Committed ICH exploration work to `cedop-restructure` branch
- Merged `cedop-restructure` → `main` (fast-forward)
- Removed large file `output/edop/basin08_pca_coords.npy` (109MB) from history using soft reset
- Added file to `.gitignore`
- Pushed to remote: `7f54ee5`

---

## Part 3: Epistemic Discussion

Discussed fundamental questions about cultural geography:

1. **Hearth vs. Diaspora**: Are we mapping where practices originated or where they exist now?
2. **Temporal anchoring**: D-PLACE has observation dates; ICH is "living heritage" (continuous present)
3. **Spatial claims**: D-PLACE society centroids are defensible; ICH country lists are political recognition

**Key insight**: ICH may be better suited for diffusion analysis than environmental correlation. The multinational inscriptions are diffusion patterns, not environmental determinism.

---

## Part 4: LLM Extraction Prototype

### Discovery
User revealed that `ich_summaries` contains short UNESCO website descriptions, but full nomination documents exist in `app/data/ich/extracted_clean_02/` (566 files, avg ~9,100 chars).

Key findings:
- 29 docs have explicit lat/lon coordinates
- 62 docs have structured "Geographic location" sections
- Documents contain environmental context NER couldn't capture

### Prototype Design

Created LLM extraction pipeline with schema:
```json
{
  "practice_locations": [...],     // Where practice is performed
  "diaspora_locations": [...],     // Where practitioners migrated TO
  "coordinates": {...},            // Explicit lat/lon if present
  "environmental_features": [...], // Physical geography terms
  "environmental_summary": "..."   // Synthesized context
}
```

**Critical distinction**: Prompt explicitly separates practice locations from diaspora locations - solving the key normalization problem.

### Results (5 sample documents)

| ID | Element | Practice | Diaspora | Coords | Env Features |
|----|---------|----------|----------|--------|--------------|
| 00204 | Gesar epic | 7 | 7 | ✓ | 12 |
| 00207 | Regong arts | 7 | 6 | ✓ | 2 |
| 00172 | Silbo Gomero | 8 | 4 | ✗ | 7 |
| 00200 | Nanjing brocade | 5 | 0 | ✓ | 3 |
| 00203 | Yueju opera | 7 | 5 | ✓ | 2 |

**Output:** `output/cdop/ich_llm_extractions.json`

**Script:** `scripts/cdop/ich_llm_extract.py`

### Validation
- Diaspora detection works (emigrant communities correctly identified)
- Coordinate extraction works (including degree/minute → decimal conversion)
- Hierarchical locations captured (village → county → prefecture → province)
- Environmental context extracted (physical geography terms)
- Extraction notes catch ambiguities

---

## Files Created/Modified

### New Files
- `docs/cdop/ich_exploration_summary.md` - Comprehensive exploration findings
- `scripts/cdop/ich_explore_concepts.py`
- `scripts/cdop/ich_explore_geography.py`
- `scripts/cdop/ich_explore_text.py`
- `scripts/cdop/ich_explore_toponyms.py`
- `scripts/cdop/ich_sample_selection.py`
- `scripts/cdop/ich_compare_sources.py`
- `scripts/cdop/ich_llm_extract.py`
- `output/cdop/ich_llm_extractions.json`

### Modified
- `.gitignore` - Added large numpy file exclusion

---

## Part 5: Triage and Batch Extraction

### Triage Results
Ran quality triage on 566 nomination documents:

| Tier | Description | Count | % |
|------|-------------|-------|---|
| A | Has explicit coordinates | 21 | 3.7% |
| B | Has "Geographic location" section | 51 | 9.0% |
| C | Long doc with place indicators | 201 | 35.5% |
| D | Short or vague | 293 | 51.8% |

Note: Tier D classification was over-pessimistic due to regex bias toward English/Chinese admin terms.

### Tier A+B Extraction (72 docs)
- 72/72 successful (100%)
- 25 with explicit coordinates (35%)
- Avg 9.8 practice locations per doc
- Avg 1.6 diaspora locations per doc
- 54% have clean practice-only geography (no diaspora)

### Tier D Sample (10 docs)
- 10/10 successful
- 8/10 (80%) have 3+ practice locations = salvageable
- 7/10 have environmental features

**Estimated salvage rate for full corpus: ~86% (487/566 docs)**

---

## Part 6: Full Corpus Extraction (Tier C+D)

Ran LLM extraction on remaining 494 documents (Tier C: 201, Tier D: 293).

### Results
- 494/494 successful (100%) - one initial failure (00743) was retried and fixed
- 6 with explicit coordinates
- Avg 5.2 practice locations per doc
- Avg 0.9 diaspora locations per doc

### Final Corpus Summary

| Tier | Docs | Successful | Coords | Avg Practice |
|------|------|------------|--------|--------------|
| A+B | 72 | 72 (100%) | 25 | 9.8 |
| C+D | 494 | 494 (100%) | 6 | 5.2 |
| **Total** | **566** | **566 (100%)** | **31** | **5.8** |

**Output:** `output/cdop/ich_llm_extractions_tier_cd.json`

**Script:** `scripts/cdop/ich_llm_extract_batch_cd.py`

---

## Next Steps

1. **Design storage schema** - `cdop.ich_locations_llm` table
2. **Geocoding pipeline** - Convert extracted locations to coordinates
3. **EDOP linkage** - Connect ICH locations to environmental signatures
4. **Embeddings** - Generate from full nomination text for similarity search

---

## Session Notes

- Model used for extraction: `claude-sonnet-4-20250514`
- The hearth vs. diaspora distinction is now addressable via LLM extraction
- Environmental tagging in ICH metadata (the 6 concepts) remains valuable as curated institutional claims, even if toponyms are messy
- Full nomination documents are 4-26x richer than website summaries
