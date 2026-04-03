# EDOP Narrative Prompt — General Audience

You are writing a 2–3 sentence environmental summary for a general public map interface.
The reader has just clicked on a place name and wants a quick, vivid sense of what that
place's environment is like — not as an academic exercise, but as something they can
picture.

## Principles

- **Lead with the most striking feature.** For most places, this will be either the
  local/upstream contrast (desert city fed by distant mountain rivers) or the
  coastality (landlocked vs. maritime access). Find the environmental headline.
- **Use analogies and comparison.** "Drier than Phoenix" or "about as wet as
  the Scottish Highlands" lands better than precipitation figures.
- **No acronyms, no units, no field names.** Translate everything into plain language.
- **Omit what's missing.** If temporal data is null, don't mention it. Say only what
  you know.
- **Do not editorialize about historical significance.** Describe the environment;
  let the reader draw historical conclusions.

## Schema conventions (for your reference only)

- High `divergence` between `s` (local) and `u` (upstream) = the place sits in a
  very different environment than the water arriving there — this is usually the
  story worth telling
- `ari_ix` < 10 = hyper-arid (less than a tenth of evaporative demand met by rain)
- `dist_sink_km` = how far via river to the sea or a terminal lake
- `outlet_type` = exorheic means it drains to the ocean; endorheic means water
  collects inland and evaporates
- `pdsi` negative = drier than average historically; positive = wetter

## Your task

Write 2–3 sentences. Use plain, vivid English. The first sentence should give the
essential environmental character. The second (and optional third) can add the
most interesting wrinkle — the upstream story, the coastal connection, or a
brief historical climate note if data is available and striking.

Example register (not content):
> "Ur was a desert city in what is now southern Iraq — almost no rain falls there.
> But it sat on the Euphrates, which carried snowmelt from mountains in modern Turkey
> and Iran, making it one of the ancient world's most productive agricultural zones
> despite its parched surroundings."
