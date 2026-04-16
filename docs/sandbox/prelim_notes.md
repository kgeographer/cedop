<!-- sandbox requirements for a EDOP signature dashboard -->
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
