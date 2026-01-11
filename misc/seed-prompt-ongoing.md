 # EDOP Session Seed

 ## Project Goal
 EDOP (Environmental Dimensions of Place) generates environmental signatures for historical locations using
 HydroATLAS basin data. Building a proof-of-concept for funding partners (ISHI/Pitt, KNAW/CLARIAH) demonstrating:
 - Environmental profiling at scale
 - Meaningful similarity detection (environmental + textual)
 - Clean API design for gazetteer integration

 ## Current State
 - **20 pilot World Heritage Sites** analyzed with:
   - 1,561-dimensional environmental signatures (PCA → 19 dims, k=5 clusters)
   - Wikipedia text corpus: 4 semantic bands (history, environment, culture, modern)
   - LLM-summarized band text → OpenAI embeddings → clustering
   **258 World Heritage cities** analyzed similarly
   **UI displays selected results** using e.g. app/api/routes.py and app/db/signature.py
   **tabs and pills**
      - main
          place search
          coordinates
        basin: list 20 clusters of 190k sub-basins; display on map & list wh cities contained
        wh cities: dropdown selection returns sig, options for similar cities
        wh sites: dropdown selection returns sig, options for similar sites
   **secrets** db and llm service secrets in .env
 - **Key findings**: 
  - Environmental and text similarity are complementary (45% cluster agreement, weak correlation except geography band r=-0.19)

 ## NEXT steps
 - so far, feeding signature.py coords directly from the UI a few ways works fine (dropdowns of wh sites and cities); challenge is to allow users to enter a place name and have it resolved, constraining search by selecting or drawing an area feature on the UI map. resolving a name from external gazetteers is problematic but a work in progress with World Historical Gazetteer API and consult with WHG developer

 ## Key Files
 - `docs/EDOP_LOG.md` — running dev log
 - `docs/session_log_*.md` — detailed work per day
 
  ## Tech Stack
 FastAPI, PostgreSQL/PostGIS, Python (scikit-learn, openai, anthropic, wikipediaapi)
