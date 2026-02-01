"""
ICH Nomination Document Cleaning Comparison
============================================

Compares heuristic vs LLM-based cleaning of nomination documents.
Tests on samples from different eras/formats to ensure consistency.

Usage:
    python scripts/cdop/ich_clean_compare.py
"""

import re
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv(Path("/Users/karlg/Documents/Repos/_cedop/.env"))

from anthropic import Anthropic

# Paths
PROJECT_ROOT = Path("/Users/karlg/Documents/Repos/_cedop")
RAW_DIR = PROJECT_ROOT / "app" / "data" / "ich" / "extracted_clean_02"
OUTPUT_DIR = PROJECT_ROOT / "output" / "cdop" / "ich_clean_compare"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# HEURISTIC CLEANING
# =============================================================================

def clean_heuristic(text: str) -> str:
    """
    Heuristic-based cleaning of ICH nomination documents.
    Removes boilerplate, instructions, and administrative sections.
    """
    lines = text.split('\n')
    cleaned_lines = []

    # Patterns to skip entirely
    skip_patterns = [
        # Headers
        r'^CONVENTION FOR THE SAFEGUARDING',
        r'^INTERGOVERNMENTAL COMMITTEE',
        r'^(Nineteenth|Twentieth|.*session)',
        r'^Nomination file no\.',
        r'^Representative List',
        r'^Original:\s*(English|French)',
        r'^NOMINATION FILE NO\.',
        r'^FOR INSCRIPTION',

        # Page numbers
        r'^RL\d+\s*[–-]\s*No\.\s*\d+\s*[–-]\s*page',
        r'^\s*page\s*\d+\s*$',
        r'^Form ICH-',

        # Form instructions (common patterns)
        r'^For Criterion [RU]\.\d',
        r'^States shall demonstrate',
        r'^Not to exceed \d+ words',
        r'^Please (explain|describe|identify|provide)',
        r'^This (section|is the|information)',
        r'^The (nomination|brief description|Committee)',
        r'^Overly technical descriptions',
        r'^Submitting States should',
        r'^According to the 2003 Convention',
        r'^In addition to the official',
        r'^Identify concisely',
        r'^A clear and complete',
        r'^The information provided should',
        r'mutually agreed\.$',

        # Checkbox markers
        r'^\s*FORMCHECKBOX',
        r'^\s*☐',
        r'^\s*\[\s*\]',

        # Section instruction headers (verbose)
        r'^.*should receive sufficient information',
        r'^.*should be mutually coherent',
        r'^.*will be particularly helpful',
        r'^.*might include one or more',
        r'^.*should address all the significant',
        r'^.*need not address in detail',

        # Administrative section markers (stop processing after these)
        # We'll handle these differently - mark where to stop
    ]

    # Sections to stop at (administrative/procedural)
    stop_sections = [
        r'^3\.\s*(SAFEGUARDING|Safeguarding)',
        r'^4\.\s*(COMMUNITY PARTICIPATION|Community participation)',
        r'^5\.\s*(INCLUSION|Inventory|INVENTORY)',
        r'^6\.\s*(DOCUMENTATION|Correspondence)',
    ]

    # Section headers to keep (descriptive sections)
    keep_section_headers = [
        r'^[A-D]\.\s+',  # A., B., C., D. sections
        r'^[A-D]\.\d+\.?\s+',  # A.1, B.1, B.2, C.1, C.2, etc.
        r'^1\.\s+',  # Section 1
        r'^2\.\s+',  # Section 2
    ]

    in_content = False
    stop_processing = False

    for line in lines:
        stripped = line.strip()

        # Check if we've hit a stop section
        for stop_pat in stop_sections:
            if re.match(stop_pat, stripped, re.IGNORECASE):
                stop_processing = True
                break

        if stop_processing:
            break

        # Skip empty lines at start
        if not stripped and not cleaned_lines:
            continue

        # Check skip patterns
        should_skip = False
        for pattern in skip_patterns:
            if re.match(pattern, stripped, re.IGNORECASE):
                should_skip = True
                break

        if should_skip:
            continue

        # Skip very short lines that look like form artifacts
        if len(stripped) < 3 and not stripped.isalpha():
            continue

        # Skip lines that are just section letters/numbers without content
        if re.match(r'^[A-Z]\.\s*$', stripped):
            continue

        # Skip lines that look like footnotes
        if re.match(r'^\d+\s+Note of the Secretariat', stripped):
            continue

        # Keep the line
        cleaned_lines.append(line)

    # Join and clean up multiple blank lines
    result = '\n'.join(cleaned_lines)
    result = re.sub(r'\n{3,}', '\n\n', result)
    result = result.strip()

    return result


# =============================================================================
# LLM CLEANING
# =============================================================================

def clean_with_llm(text: str, ich_id: str) -> str:
    """
    Use Claude to extract clean descriptive content from nomination doc.
    """
    client = Anthropic()

    # Truncate if very long (keep first ~15k chars for context window)
    if len(text) > 15000:
        text = text[:15000] + "\n\n[...document truncated...]"

    prompt = f"""You are extracting text from a UNESCO Intangible Cultural Heritage nomination document.

CRITICAL: You must copy text VERBATIM - do not paraphrase, rephrase, add words, or edit in any way.
Copy the exact original text character-for-character. Do not "clean up" grammar or formatting.

EXTRACT verbatim text from these sections only:
- Description of the cultural practice/element
- Geographic locations where it is practiced
- Communities, groups, and practitioners involved
- How knowledge/skills are transmitted
- Social functions and cultural meanings
- Historical context mentioned in descriptions

DELETE entirely (do not include any text from):
- Form headers ("CONVENTION FOR THE SAFEGUARDING...", "INTERGOVERNMENTAL COMMITTEE...")
- Section labels (A., B.1., C.2., 1., 2., etc.) - delete the label, keep the content
- Form instructions ("Not to exceed X words", "Please describe...", "This section should...", "For Criterion...")
- Page numbers and form references (RL10, Form ICH, etc.)
- Checkbox markers (FORMCHECKBOX)
- Safeguarding plans, timetables, and future measures (Section 3+)
- Administrative sections about consent, inventories, documentation
- Questions/prompts asking what to describe

Output the extracted paragraphs with blank lines between them.
COPY TEXT EXACTLY AS IT APPEARS - no editing, no paraphrasing, no additions.

Here is the nomination document:

{text}"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


# =============================================================================
# COMPARISON
# =============================================================================

def compare_cleaning(ich_id: str, description: str):
    """Compare heuristic vs LLM cleaning for one document."""

    # Find the raw file
    raw_file = RAW_DIR / f"{ich_id}_nomination_clean.txt"
    if not raw_file.exists():
        print(f"  Raw file not found: {raw_file}")
        return None

    print(f"\n{'='*60}")
    print(f"Processing {ich_id}: {description}")
    print('='*60)

    with open(raw_file) as f:
        raw_text = f.read()

    print(f"  Raw length: {len(raw_text)} chars")

    # Heuristic cleaning
    print("  Running heuristic cleaning...")
    heuristic_result = clean_heuristic(raw_text)
    print(f"  Heuristic result: {len(heuristic_result)} chars")

    # LLM cleaning
    print("  Running LLM cleaning...")
    try:
        llm_result = clean_with_llm(raw_text, ich_id)
        print(f"  LLM result: {len(llm_result)} chars")
    except Exception as e:
        print(f"  LLM error: {e}")
        llm_result = f"ERROR: {e}"

    # Save results
    heuristic_file = OUTPUT_DIR / f"{ich_id}_heuristic.txt"
    llm_file = OUTPUT_DIR / f"{ich_id}_llm.txt"

    with open(heuristic_file, 'w') as f:
        f.write(heuristic_result)

    with open(llm_file, 'w') as f:
        f.write(llm_result)

    print(f"  Saved to: {OUTPUT_DIR}")

    return {
        'ich_id': ich_id,
        'description': description,
        'raw_len': len(raw_text),
        'heuristic_len': len(heuristic_result),
        'llm_len': len(llm_result) if not llm_result.startswith('ERROR') else 0,
    }


def main():
    """Run comparison on sample documents from different eras."""

    samples = [
        # 2024-2025 new element (.doc)
        ("02329", "2025 USL - Kobyz (Uzbekistan) - .doc"),

        # Gap-fill recent (.doc)
        ("01852", "2022 USL - Ukrainian borscht - .pdf"),

        # Gap-fill 2010 (PDF)
        ("00337", "2010 RL - Chhau dance (India) - .pdf"),

        # Another 2010 PDF for variety
        ("00395", "2010 RL - Naadam festival (Mongolia) - .pdf"),
    ]

    results = []
    for ich_id, description in samples:
        result = compare_cleaning(ich_id, description)
        if result:
            results.append(result)

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    print(f"{'ID':<8} {'Raw':>8} {'Heur':>8} {'LLM':>8} {'H%':>6} {'L%':>6}")
    print('-'*50)
    for r in results:
        h_pct = (r['heuristic_len'] / r['raw_len'] * 100) if r['raw_len'] else 0
        l_pct = (r['llm_len'] / r['raw_len'] * 100) if r['raw_len'] else 0
        print(f"{r['ich_id']:<8} {r['raw_len']:>8} {r['heuristic_len']:>8} {r['llm_len']:>8} {h_pct:>5.1f}% {l_pct:>5.1f}%")

    print(f"\nOutput files saved to: {OUTPUT_DIR}")
    print("Review the _heuristic.txt and _llm.txt files to compare quality.")


if __name__ == "__main__":
    main()
