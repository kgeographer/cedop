<!-- design requirements for a EDOP signature dashboard -->
## research dashboard for EDOP signatured

### user01
the initial user is a humanities researcher (e.g. history, archaeology, classics, philology, etc.) pursuing questions with a spatil/geographic component

### use scenario 01: user01 evaluating in-progress signature development
- EDOPS is in development, with signature data elements and corresponding API parameters being added in tendem.
- Goals for signature development are explicit, encoded as a json schems in docs/edip/edops_schema.json
- As the signature is elaborate/articulated, its in-progress state needs to be displayed in a GUI for {user} to evaluate
- __UX actions__
  - user enters place name, offered list of candidate matches w/sufficient info to choose; od "not found"
  - user chooses BasinATLAS resolution (e.g. 08, 06)
  - user chooses set of signature "bands" to return (A-D from basin data; E (coastality), F (climate for timespan))
  - if F is chosen, user must enter start/end years as integers
  - "Get signature" button delivers requested signature payload in browsable band divisions, plus a summary (~10 elements drawn from attributes within bands)
  - Ecoregion returned is linked to Wikipedia article if available; link retrieves content in modal
  - Signature retrieval expose a button for "LLM interpretation" which delivers a 2-paragraph interpretation of the signature results.
  


### screen requirements
- Initial page load:
  - header with EDOP logo and page title ("Sandbox")
  - Level dropdown choice (BasinATLAS 08 to start)
  - input for search 
    - if text, against 2.6m place records in World Historical Gazetteer (WHG); "Place lookup"
  - if raw lat,lon pair, finds local basin
  - Get signature button, disabled until place search result is accepted
  - Basic instruction, e.g. "Resolve a place and get its signature to begin"


- After place is resolved, two action buttons appear:
  - **Preview neighborhood** — loads a hydro-context map in the right panel (`#sb-sig-panel`) showing:
    - Point location marker
    - Immediately containing basin polygon (highlighted)
    - Adjacent basins within ~50km, colored by `up_area` (graduated: larger upstream area = darker/more saturated — visually identifies river-channel basins)
    - River polylines from `gaz.rivers` filtered to main channels (`ord_clas >= 4` or `dis_av_cms` threshold), graduated by discharge weight
    - Purpose: lets user assess the hydro situation and make an informed choice of scale/neighborhood before requesting a signature. Addresses the fundamental problem that point containment assigns floodplain/river-adjacent sites to small local basins rather than the main channel basin.
  - **Get signature** — proceeds with current basin assignment (containment); in future, neighborhood choice from preview informs which basin is used

- Fail states:
  - WHG lookup returns no match → display message "Not found in WHG. Options: enter lat/lon directly | search Geonames | try an LLM-assisted lookup"
  - Requested date range is outside LMR coverage (pre-0 CE or post-~2000 CE) → display message noting the gap; offer to proceed with bands A–E only; note that pre-Common Era paleoclimate data at this resolution is not currently available


### user scenarios

Scenarios ground UI/UX design in real research questions. A good scenario starts from a **historical paradox** — something the researcher already finds puzzling — not a task flow. The signature's job is to resolve or deepen the paradox. Two types are documented here: one that largely works with current EDOPS capabilities, one that exercises current limits. When scenarios accumulate they will move to a dedicated `docs/gui/scenarios.md`.

---

#### scenario 01: Timbuktu — the desert intellectual capital (works)

**User**: historian / Africanist with interest in medieval Islamic civilization and trans-Saharan trade

**Entry question**: *"Timbuktu was clearly a successful center of trade and Islamic scholarship during the Mali and Songhai empires. Given its location at the edge of the Sahara, how could that setting possibly support a civilizational center?"*

**Walkthrough**:

1. User types "Timbuktu" in the place lookup. WHG returns candidates including Tombouctou [ML] — exact match with alt name "Timbuktu". User selects it.
2. User checks bands A, B, C, E (physical + coastality) and F (temporal), enters `1350` to `1600` CE (Mali/Songhai peak).
3. Clicks "Get signature" → payload loads.

**What the signature shows**:

- **Band A (Physiographic)**: low flat plain at the Saharan margin, very low relief — confirms the surface reading of an inhospitable desert-edge location
- **Band B — local `s` values**: low precipitation, high aridity index, minimal local runoff — the site looks fragile
- **Band B — upstream `u` values**: the Niger headwaters drain the Fouta Djallon highlands in Guinea, where annual rainfall exceeds 1,500mm. The `s/u` divergence on precipitation is large — Timbuktu sits on a river fed by distant highlands, not its local catchment
- **Band C (Bioclimatic)**: local biome is Sahel/desert edge; upstream biome profile includes Guinea highland forest/savanna — the divergence is visible in vegetation productivity measures too
- **Band E (Coastality)**: not coastal in the marine sense, but `dist_sink` captures proximity to the river mouth system; the Niger Inland Delta immediately upstream creates an enormous productive floodplain — this is the ecological anchor
- **Band F (Temporal, 1350–1600)**: LMR PDSI for the period shows conditions broadly comparable to the modern mean in the Sahel; no catastrophic drought forcing during the empire peak; eVolv2k shows some volcanic events but no sustained forcing

**Payoff**: The signature resolves the paradox the same way it resolves Ur: allochthonous water. The Niger brings rainfall from Guinea highlands 1,500 km upstream, sustaining agriculture and the Niger Inland Delta fisheries that fed the city. The `s/u` divergence is the structural explanation. Timbuktu's genius loci is not its local environment but its position as the hinge between river-borne surplus (south) and trans-Saharan caravan trade (north) — the signature provides the physical half of that argument; the cultural-geographic half belongs to CDOP.

**Design implications**:
- `s/u` divergence should be the lead display item in Band B, not buried
- Upstream biome contrast in Band C deserves a natural-language gloss ("your upstream basin spans X biomes")
- Band E needs prose interpretation — `dist_sink` values are not self-explanatory to humanities readers
- The narrative button should frame the interpretation around the user's question, not just describe values

---

#### scenario 02: Ur — the hyper-arid cradle (exercises current limits)

**User**: archaeologist / ancient Near East historian

**Entry question**: *"Ur is described as situated in a near-hyper-arid environment, yet it was among the earliest and most densely settled urban centers in the ancient world. How do I square that?"*

**Walkthrough**:

1. User types "Ur" in the place lookup. WHG returns no match. → **Fail state 1**: sandbox offers: enter lat/lon directly | search Geonames | LLM-assisted lookup. User enters coordinates (~30.96°N, 46.10°E) and proceeds.
2. User checks bands A, B, C, E and F (temporal), enters `−2100` to `−1800` (Ur III period).
3. Clicks "Get signature" → bands A–E load; Band F triggers **Fail state 2**: date range is prior to LMR coverage (floor ~0 CE). Sandbox notifies the user: "Temporal climate data is not available before approximately 0 CE. Ur III period climate is outside current EDOPS scope. Proceeding with physical signature only." Bands A–E render normally.

**What the signature shows (A–E)**:

- **Band A**: flat alluvial plain, very low elevation — expected
- **Band B — local `s`**: low precipitation, high aridity — confirms the paradox
- **Band B — upstream `u`**: Euphrates headwaters drain the Taurus and Zagros; `s/u` divergence on precipitation is large — allochthonous water again
- **Band C**: local desert/xeric biome vs. upstream alpine/temperate montane — strong contrast
- **Band E**: `dist_sink` near zero — Ur was at the head of the Persian Gulf in the third millennium BCE; high coastality index

**What the temporal question surfaces**: The user's climate question for the Ur III period is currently unanswerable within EDOPS. This is not merely a tool gap — pre-Common Era paleoclimate data at sub-basin resolution is a genuine research frontier. The fail state should say so honestly and note what *is* available (pollen cores, isotope records) as pointers for further research outside the tool.

**Design implications from fail states**:
- WHG no-match message must not be a dead end — offer lat/lon entry prominently as the primary fallback
- Temporal out-of-range notification should be informative, not just an error — name the data gap, suggest what bands still apply
- "Good luck" tone is appropriate: EDOPS is honest about what it can and can't do
