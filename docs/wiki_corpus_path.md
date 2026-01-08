# Way Forward: Building a Wikipedia-Based Corpus for Cultural Landscape Analysis

This is a concrete, staged approach to assembling a reusable text corpus for ~250 World Heritage Cities plus a selected set of archaeological / hybrid sites, framed around **semantic bands** and designed to support multiple downstream embedding strategies.

---

## A. Inputs and IDs

### A1. World Heritage Cities base set (≈250)
- Stable place IDs
- Geometry (via World Historical Gazetteer reconciliation)
- Wikipedia URLs / slugs

These form the initial, coherent testbed (extant cities with rich discourse).

### A2. Candidate archaeological / hybrid additions (from WH Sites)
- Source: UNESCO English short descriptions of World Heritage Sites
- Goal: identify *additional* places representing former settlements / archaeological landscapes

These are not replacements for cities, but a complementary expansion.

### A3. Unified place registry
Create a single spine table / TSV, e.g. `places_target`:

- `place_id` (canonical, e.g. `whc_###`, `whs_####`)
- `label`
- `place_type` (`city`, `archaeological`, `hybrid`)
- `source_set` (`WHC`, `WHS-derived`)
- `wiki_slug` (or full URL)
- geometry pointer (present for cities now; optional for sites)

Everything downstream joins to this.

---

## B. Archaeological Classification from WH Site Descriptions

### B1. Multi-class scheme (explicit, non-binary)

Classify WH Sites into:

- **`archaeological_dominant`**  
  Significance primarily from material remains, excavation, ruins.
- **`living_city_dominant`**  
  Historic urban fabric with ongoing settlement and modern life.
- **`hybrid_layered_continuity`**  
  Long-lived places combining deep archaeology and living urban form.

(Optional: `other_cultural_nonsettlement` to exclude industrial, sacred, or landscape-only sites.)

### B2. LLM-assisted classification (bounded task)
Prompt the LLM with:
- Site title
- UNESCO short description (+ criteria if available)

Require output:
- `class`
- `confidence` (low / medium / high)
- `evidence_phrases` (quoted from description)
- `notes` (1 sentence)

Use:
- High-confidence archaeological → auto-include
- Low-confidence + hybrids → short manual review list

### B3. Resolve Wikipedia pages
- Identify correct Wikipedia slugs for selected WH Sites
- Add them to `places_target`

Result: ~300 Wikipedia URLs total.

---

## C. Wikipedia Harvesting Strategy

### C1. Use MediaWiki API (not HTML scraping)
For each `wiki_slug`:
- Retrieve lead + sectioned content
- Request cleaned plain text where possible
- Preserve:
  - section titles
  - heading hierarchy
  - section text

### C2. Map section headings to **semantic bands**
Do not rely on exact headings; normalize via mapping.

**Semantic bands:**

1. **Historical narrative**
   - History, Etymology, Archaeology, Excavation, Early periods, Colonial era

2. **Environmental / spatial setting**
   - Geography, Location, Geology, Topography, Climate, Environment

3. **Cultural / institutional life**
   - Culture, Religion, Architecture, Arts, Education, Demographics (selective), Notable people (summarized)

4. **Modern urban function**
   - Economy, Transport / Transportation, Infrastructure, Government, Industry, Tourism

**Explicit exclusions:**
- References
- External links
- See also
- Notes
- Further reading

### C3. Store harvested text in a long-form sections table
Example table: `wiki_sections`

- `place_id`
- `wiki_slug`
- `section_title_raw`
- `band` (`history`, `environment`, `culture`, `modern`)
- `heading_level`
- `text`
- `char_count` / `token_est`
- `retrieved_at`

This preserves maximum flexibility.

---

## D. Normalization Rules (Prevent Length Bias)

### D1. Build derived corpora from `wiki_sections`

#### Corpus Variant A: **Band-capped composite text** (default)
For each place:
- Concatenate bands in fixed order:
  1. environment
  2. history
  3. culture
  4. modern
- Apply per-band caps (tokens or chars), e.g.:
  - environment: 400
  - history: 600
  - culture: 400
  - modern: 300
- Missing bands remain empty (no substitution)

Store as: `place_text_composite`

#### Corpus Variant B: **Multi-embedding by band**
Store separate texts:
- `place_text_environment`
- `place_text_history`
- `place_text_culture`
- `place_text_modern`

Enables divergence analysis (environmental vs cultural similarity).

### D2. Coverage metadata
For each place:
- bands present
- token counts per band
- % missing

This becomes essential for interpretation and UI signaling.

---

## E. Optional LLM Normalization Layer (Later)

Not required for corpus construction, but useful experimentally.

- Input: banded raw text
- Output: 250–500 word structured summary with subheads:
  - History
  - Setting
  - Culture
  - Modern function
- Strict rule:
  - “Use only provided text”
  - “If information is missing, state ‘Not described in source’”

Store as: `place_summary_text`

Raw text remains authoritative.

---

## F. End State (Before Embeddings)

At the end of corpus construction, you have:

1. **`places_target`**  
   IDs, types (city / archaeological / hybrid), wiki slugs, geometry pointers

2. **`wiki_sections`**  
   All harvested text with semantic band mapping

3. **`place_text_composite`**  
   Normalized, band-capped text per place

4. **`place_text_by_band`**  
   Band-specific texts + coverage stats

5. *(Optional)* **`place_summary_text`**  
   LLM-standardized profiles

From this spine, you can:
- generate embeddings in multiple ways
- test stability vs normalization
- compare environment ↔ culture systematically
- expand to archaeology without re-harvesting text