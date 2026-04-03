# EDOP Narrative Prompts

System prompts for Claude API calls that generate natural-language interpretations
of EDOP environmental signatures. Each prompt targets a specific audience and
delivery context.

## Usage (intended, not yet implemented)

```python
import anthropic
from pathlib import Path

def generate_narrative(signature: dict, audience: str) -> str:
    prompt = Path(f"prompts/edop_narrative_{audience}.md").read_text()
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=512,
        system=prompt,
        messages=[{"role": "user", "content": json.dumps(signature, indent=2)}]
    )
    return response.content[0].text
```

The `audience` parameter maps to a file:

| audience | file | context |
|---|---|---|
| `scientific` | `edop_narrative_scientific.md` | Research tools, API consumers |
| `whg_portal` | `edop_narrative_whg_portal.md` | WHG place portal page |
| `general` | `edop_narrative_general.md` | Public-facing map interfaces |

## Input

A fully-assembled EDOP signature JSON (see `docs/edop/signature_schema_draft.json`).
Null fields and `[*]`-marked fields are present but empty — prompts are written to
handle these gracefully.

## Delivery options under consideration

- **Synchronous**: narrative included in signature payload; +1–3s latency
- **On-demand endpoint**: `GET /api/narrative?lat=X&lon=Y&period=P&audience=whg_portal`
- **Streaming**: signature returned immediately, narrative streamed as second chunk
- **Cached**: pre-generated for bounded sets (WHG cities, WH sites)
