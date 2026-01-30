# ICH Data Exploration Summary

**Date:** 2026-01-30
**Dataset:** UNESCO Intangible Cultural Heritage (730 elements)
**Schema:** `cdop`

---

## 1. Data Overview

| Table | Rows | Description |
|-------|------|-------------|
| `ich_elements` | 730 | Core metadata (ich_id, label, countries, year, list, concepts) |
| `ich_summaries` | 730 | Full text descriptions (~1,200 chars avg) |
| `ich_toponyms_ner` | 5,348 | NER-extracted place names (552 elements, 75%) |
| `ich_toponyms_cleaner` | 5,116 | Cleaned toponyms |
| `ich_lptsv_raw` | 5,348 | Linked Places TSV format with feature classes |

### UNESCO Lists

| List Code | Name | Count |
|-----------|------|-------|
| RL | Representative List | 611 |
| USL | Urgent Safeguarding List | 82 |
| GSP | Good Safeguarding Practices | 37 |

### Inscriptions by Year

| Year | Count | | Year | Count |
|------|-------|---|------|-------|
| 2008 | 90 | | 2016 | 41 |
| 2009 | 85 | | 2017 | 42 |
| 2010 | 47 | | 2018 | 39 |
| 2011 | 33 | | 2019 | 40 |
| 2012 | 32 | | 2020 | 35 |
| 2013 | 30 | | 2021 | 47 |
| 2014 | 38 | | 2022 | 48 |
| 2015 | 28 | | 2023 | 55 |

---

## 2. Concept Taxonomy Analysis

### 2.1 Concept Distribution

**Total distinct concepts:** 423

#### Environmental Concepts (6 total)

| Concept | Element Count |
|---------|---------------|
| Mountains | 71 |
| Grasslands, savannahs | 35 |
| Marine, coastal and island areas | 33 |
| Drylands | 29 |
| Forests | 27 |
| Inland wetlands | 9 |

**Total environmental-tagged:** ~200 elements (some overlap)

#### Top Cultural/Practice Concepts (30)

| Concept | Count | | Concept | Count |
|---------|-------|---|---------|-------|
| Vocal music | 144 | | Food preparation | 32 |
| Agro-ecosystems | 131 | | Rituals | 31 |
| Performing arts | 111 | | Oral tradition | 26 |
| Urban areas | 110 | | Ritual dance | 26 |
| Social practices, rituals and festive events | 106 | | Textile arts | 26 |
| Instrumental music | 99 | | Non-ecosystem specific | 24 |
| Dance | 97 | | Masks | 24 |
| Festivals | 61 | | Oral traditions and expressions | 24 |
| Religious practice | 56 | | Craft workers | 22 |
| Traditional craftsmanship | 55 | | Polyphonic singing | 21 |
| Technical skills | 55 | | Sports competitions | 20 |
| Procession | 53 | | Percussion instruments | 19 |
| Theatre | 38 | | Epic poetry | 18 |
| Weaving | 38 | | Decorative arts | 18 |

*Note: "Agro-ecosystems" (131) is a hybrid human-environment concept*

### 2.2 Environmental-Cultural Co-occurrence

Top co-occurring concept pairs (environmental + cultural):

| Environmental Concept | Cultural Concept | Count |
|-----------------------|------------------|-------|
| Mountains | Vocal music | 17 |
| Mountains | Performing arts | 12 |
| Mountains | Instrumental music | 10 |
| Drylands | Vocal music | 9 |
| Marine, coastal | Vocal music | 8 |
| Mountains | Social practices, rituals | 8 |
| Mountains | Dance | 8 |
| Grasslands, savannahs | Vocal music | 7 |
| Mountains | Festivals | 7 |
| Drylands | Dance | 7 |

**Key Finding:** Vocal music strongly co-occurs with all environmental concepts. Mountains dominate environmental tagging and have the richest cultural associations.

---

## 3. Geographic Analysis

### 3.1 Elements by Country (Top 20)

| Country | Count | | Country | Count |
|---------|-------|---|---------|-------|
| China | 43 | | Kyrgyzstan | 15 |
| Türkiye | 30 | | Mongolia | 15 |
| France | 28 | | Uzbekistan | 15 |
| Spain | 25 | | India | 15 |
| Iran | 24 | | Peru | 14 |
| Azerbaijan | 23 | | Colombia | 14 |
| Croatia | 22 | | Oman | 14 |
| Republic of Korea | 22 | | Morocco | 13 |
| Japan | 22 | | Kazakhstan | 13 |
| Italy | 19 | | Saudi Arabia | 13 |

### 3.2 Elements by UN Subregion

| Subregion | Elements | | Subregion | Elements |
|-----------|----------|---|-----------|----------|
| Southern Europe | 92 | | Northern Africa | 31 |
| Western Asia | 83 | | Southern Asia | 27 |
| Eastern Asia | 79 | | Northern Europe | 24 |
| Western Europe | 61 | | Central America | 22 |
| Eastern Europe | 50 | | Caribbean | 11 |
| South America | 47 | | Southern Africa | 5 |
| Central Asia | 45 | | Middle Africa | 3 |
| Eastern Africa | 39 | | Polynesia | 2 |
| South-Eastern Asia | 36 | | Melanesia | 1 |
| Western Africa | 31 | | | |

**Geographic Coverage:**
- Europe dominates (Southern + Western + Eastern + Northern = 227 elements)
- Asia well-represented (Western + Eastern + Central + S.E. + Southern = 270 elements)
- Africa moderate (Eastern + Western + Northern + Southern + Middle = 109 elements)
- Americas present (South + Central + Caribbean = 80 elements)
- Oceania sparse (Polynesia + Melanesia = 3 elements)

### 3.3 Country Name Mapping Issues

16 ICH country names don't match `gaz.admin0.name` directly:

| ICH Country Name | Suggested admin0 match |
|------------------|------------------------|
| Bolivia (Plurinational State of) | Bolivia |
| Bosnia and Herzegovina | Bosnia and Herz. |
| Central African Republic | Central African Rep. |
| Democratic People's Republic of Korea | North Korea |
| Democratic Republic of the Congo | Dem. Rep. Congo |
| Dominican Republic | Dominican Rep. |
| Iran (Islamic Republic of) | Iran |
| Lao People's Democratic Republic | Laos |
| Micronesia (Federated States of) | Micronesia |
| Republic of Korea | South Korea |
| Republic of Moldova | Moldova |
| Russian Federation | Russia |
| Syrian Arab Republic | Syria |
| Türkiye | Turkey |
| Venezuela (Bolivarian Republic of) | Venezuela |
| Viet Nam | Vietnam |

*Action: Create mapping table or use fuzzy matching for subregion analysis*

### 3.4 Multinational Elements (Cultural Diffusion)

Elements inscribed by multiple countries indicate transnational cultural practices:

| Countries | Element | Notes |
|-----------|---------|-------|
| 24 | Falconry, a living human heritage | Pan-Eurasian |
| 16 | Arabic calligraphy | MENA region |
| 15 | Date palm knowledge and traditions | MENA + North Africa |
| 12 | Nawrouz/Nowruz (New Year) | Persian cultural sphere |
| 10 | Transhumance (seasonal livestock movement) | Mediterranean Europe |
| 10 | Seal engraving arts | MENA region |
| 8 | Midwifery practices | Diverse: Europe, Africa, Asia, Americas |
| 8 | Lipizzan horse breeding | Central/Southern Europe |
| 8 | Dry stone walling | Mediterranean Europe |
| 7 | Mediterranean diet | Mediterranean basin |
| 7 | Sericulture (silk production) | Silk Road corridor |
| 7 | Nasreddin Hodja traditions | Turkic cultural sphere |

**Diffusion patterns identified:**
- **MENA/Arab**: Calligraphy, date palms, seals
- **Turkic/Central Asian**: Nasreddin, Nowruz, silk
- **Mediterranean European**: Transhumance, dry stone, diet
- **Pan-Eurasian**: Falconry (24 countries!)

### 3.5 Toponym Density Distribution

| Toponyms per Element | Element Count | Percentage |
|---------------------|---------------|------------|
| 0 toponyms | 178 | 24% |
| 1-5 toponyms | 249 | 34% |
| 6-10 toponyms | 138 | 19% |
| 11-20 toponyms | 100 | 14% |
| 20+ toponyms | 65 | 9% |

**552 elements (76%)** have at least one extracted toponym.

---

## 4. Sample Elements by Environmental Concept

### Mountains (sample)
- **Hudhud chants of the Ifugao** (Philippines) - rice terrace traditions
- **Andean cosmovision of the Kallawaya** (Bolivia) - Andean medicine
- **Regong arts** (China) - Tibetan Plateau

### Drylands (sample)
- **Uyghur Muqam of Xinjiang** (China) - Central Asian music
- **Al-Sirah Al-Hilaliyyah epic** (Egypt) - Bedouin traditions
- **Cultural space of the Bedu in Petra and Wadi Rum** (Jordan)

### Marine/Coastal (sample)
- **Language, dance and music of the Garifuna** (Belize, Guatemala, Honduras, Nicaragua)
- **Wayang puppet theatre** (Indonesia)
- **Vanuatu sand drawings** (Vanuatu)

---

## 5. Text Analysis

### 5.1 Summary Length Distribution

| Metric | Value |
|--------|-------|
| Total summaries | 730 |
| Avg characters | 1,213 |
| Median characters | 1,304 |
| Min characters | 23 |
| Max characters | 1,805 |

| Length Bucket | Count | Notes |
|---------------|-------|-------|
| < 500 chars | 54 | Short/incomplete |
| 500-999 chars | 36 | Below average |
| 1000-1499 chars | 621 | **Majority (85%)** |
| 1500-1999 chars | 19 | Longest |

**Word count:** Avg 186 words, Median 200 words (range: 4-256)

### 5.2 Data Quality Issues

**Shortest summaries (potential issues):**

| ich_id | Label | Chars | Issue |
|--------|-------|-------|-------|
| 01852 | Culture of Ukrainian borscht cooking | 23 | "Case of extreme urgency" only |
| 00169 | Mbende Jerusarema dance | 180 | Truncated |
| 00089 | Shashmaqom music | 219 | Very brief |
| 00166 | Taquile and its textile art | 238 | Brief |
| 00145 | Olonkho, Yakut heroic epos | 253 | Brief |

*Note: 54 elements have < 500 chars - may need supplementation*

**Longest summaries:**
- Koogere oral tradition (Basongora) - 1,805 chars
- Centre for traditional culture (school museum) - 1,728 chars

### 5.3 Environmental Terms in Text

Terms appearing in summary text (unstructured mentions):

| Term | Elements | | Term | Elements |
|------|----------|---|------|----------|
| rain* | 146 | | coast | 21 |
| sea | 109 | | dry | 21 |
| island | 39 | | fishing | 18 |
| mountain | 32 | | forest | 16 |
| river | 31 | | desert | 13 |
| agricultural | 25 | | climate | 13 |

*Note: "rain" includes "terrain", "training" etc. - needs refinement*

### 5.4 Embedding Readiness

| Metric | Value |
|--------|-------|
| Total characters | 885,852 |
| Est. tokens (~4 chars/token) | ~221,000 |
| Avg tokens/element | ~303 |
| OpenAI ada-002 cost | ~$0.02 |

**Assessment:** Corpus is small and affordable for embedding. 85% of summaries are 1000-1500 chars (200 words) - consistent length is good for similarity search.

---

## 6. Toponym Quality Assessment

### 6.1 Table Comparison

| Table | Rows | Elements | Notes |
|-------|------|----------|-------|
| `ich_toponyms_ner` | 5,348 | 552 (76%) | Raw NER extraction |
| `ich_toponyms_cleaner` | 5,116 | 552 | 232 rows removed |
| `ich_lptsv_raw` | 5,348 | 552 | Linked Places TSV format |

### 6.2 NER False Positives (removed by cleaning)

Top items removed from NER → cleaner:

| Removed Term | Occurrences | Reason |
|--------------|-------------|--------|
| 'States' | 10 | Fragment |
| 'UAE' | 9 | Abbreviation |
| 'South', 'North' | 8, 7 | Directional fragment |
| 'Zhejiang' | 7 | Province retained elsewhere |
| 'Roma', 'Slovak', 'Kyrgyz' | 6 each | Ethnic group, not place |
| 'Republic' | 6 | Fragment |
| 'USA', 'UK' | 6, 3 | Abbreviations |
| 'Quran' | 4 | Not a place |
| 'symposia' | 3 | False positive |
| 'Pi' | 3 | Single syllable noise |

### 6.3 The Gnarly Part: Sub-country Normalization

| Category | Count | Percentage |
|----------|-------|------------|
| Total toponyms (cleaner) | 5,116 | 100% |
| Country-level matches | 929 | 18.2% |
| **Sub-country (need geocoding)** | **4,187** | **81.8%** |

**Why sub-country geocoding is difficult:**

1. **Migration destinations mixed in** - toponyms include diaspora locations:
   - "Safeguarding of folk music heritage" (Hungary) → includes Australia, Canada, US, Great Britain
   - "Momoeria, New Year's celebration" (Greece) → includes Australia, United States

2. **Multi-word administrative names**:
   - "Dong Autonomous Prefecture", "Abu Dhabi City Region"
   - "Qiandongnan Miao" (partial name)

3. **Non-standard romanization**:
   - "Bandar - e - Dayyer", "Bandar - e - Lenge" (Persian transliteration)
   - "Abu - Musā" (spacing issues)

4. **Ambiguous/generic terms**:
   - "Eastern Region", "Western Region", "Outer Islands"
   - "Gulf", "Peninsula", "Province"

5. **Diacritics and special characters**:
   - Turkish: Bakımlı, Çorum, Yeşilköy
   - French: Déguèla, Ségou
   - Portuguese: Bisalhães, Alcântara
   - Spanish: Yuruparí, San Luis Potosí

### 6.4 Word Count Distribution (cleaner)

| Word Count | Toponyms | Notes |
|------------|----------|-------|
| 1 word | 4,041 (79%) | Easiest to match |
| 2 words | 886 (17%) | Moderate difficulty |
| 3 words | 128 (3%) | Complex |
| 4+ words | 61 (1%) | Very complex |

### 6.5 LPTSV Format Assessment

```
Sample record:
{
  'id': '01558_1',
  'title': 'Aachen',
  'ccodes': 'AT;FR;DE;NO;CH',    # Multiple countries
  'title_source': 'UNESCO ICH',
  'attestation_year': 2020,
  'fclasses': 'S;P;A;H;T;R'      # Non-discriminating placeholder
}
```

**Issues for WHG reconciliation:**

1. **fclasses is useless**: All 5,348 rows have identical value `S;P;A;H;T;R` (all GeoNames classes) - provides no filtering
2. **ccodes for multinational elements**: "Aachen" has 5 country codes - which is correct?
3. **No coordinates**: Requires geocoding via gazetteer lookup
4. **No hierarchy hints**: No admin1/admin2 context to disambiguate

### 6.6 Most Frequent Toponyms (ambiguity risk)

| Toponym | Elements | Notes |
|---------|----------|-------|
| China | 43 | Country (easy) |
| Japan | 35 | Country (easy) |
| France | 31 | Country (easy) |
| Europe | 19 | Continent (too broad) |
| Korea | 20 | Ambiguous (North/South) |
| United States | 14 | Often diaspora, not practice location |

### 6.7 Sample Problematic Elements

**[00202] Grand song of the Dong ethnic group** (China)
- Sub-country toponyms: Congjiang, Dong Autonomous Prefecture, Guizhou, Liping, Qiandongnan Miao, Rongjiang, Rongjiang River
- Issue: Mix of counties, prefectures, provinces, rivers

**[01177] Safeguarding of folk music heritage** (Hungary)
- Toponyms include: Australia, Canada, Eastern Europe, Great Britain, South Korea, United States
- Issue: Diaspora locations, not practice location

**[00534] Traditional skills of building Iranian boats** (Iran)
- Toponyms: Abu - Musā, Bandar - e - Dayyer, Bandar - e - Lenge, etc.
- Issue: Non-standard transliteration with embedded spaces/hyphens

---

## 7. Known Data Quality Issues

### Toponym NER
- 232 false positives removed (but more remain in cleaner)
- Ethnic group names retained as places (Roma, Aymara)
- Diaspora locations mixed with practice locations
- Non-standard romanization and transliteration

### Concept Taxonomy
- 423 distinct concepts (original plan noted 909 - may count concept instances)
- Some concepts overlap (e.g., "Oral tradition" vs "Oral traditions and expressions")
- Environmental concepts are mutually exclusive in the data

### Summary Text
- 54 elements have very short summaries (< 500 chars)
- 1 element (Ukrainian borscht) has only placeholder text (23 chars)

### LPTSV for Gazetteer Reconciliation
- fclasses field is non-discriminating (all values identical)
- No coordinate data - full geocoding required
- Country codes ambiguous for multinational elements
- No admin hierarchy context for disambiguation

---

## 8. Next Steps

### Completed
- [x] Phase 1: Concept Taxonomy Analysis
- [x] Phase 2: Geographic Analysis
- [x] Phase 3: Text Analysis Preparation
- [x] Phase 4: Toponym Quality Assessment

### Future: Embeddings Pipeline
1. Add `ich_embeddings` table with pgvector
2. Generate embeddings for `ich_summaries.text`
3. Enable similarity search across ICH elements
4. Link to EDOP signatures via toponym geolocation (if toponyms can be resolved)

### Future: Toponym Normalization (the gnarly work)
Potential approaches:
1. **Country-level only**: Use 929 country-level toponyms, ignore sub-country
2. **Admin1 matching**: Match single-word toponyms against GeoNames admin1 names within country
3. **Fuzzy WHG lookup**: Use WHG API with country constraint for best-effort matching
4. **Manual curation**: For 552 elements, manual review might be feasible
5. **LLM-assisted**: Use LLM to identify "practice location" vs "diaspora/migration" toponyms

### Future: Data Quality Fixes
- Supplement 54 short summaries (< 500 chars)
- Create country name mapping table for UN subregion joins
- Separate practice locations from diaspora mentions
- Normalize transliteration variants (Bandar-e vs Bandar - e)

---

*Generated by ICH exploration scripts in `scripts/cdop/`*
