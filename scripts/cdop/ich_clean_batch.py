"""
ICH Nomination Document Batch Cleaning
======================================

Cleans all new nomination documents using LLM-based verbatim extraction.
Removes form boilerplate while preserving exact original text.

Usage:
    python scripts/cdop/ich_clean_batch.py [--limit N]
"""

import json
import time
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv(Path("/Users/karlg/Documents/Repos/_cedop/.env"))

from anthropic import Anthropic

# Paths
PROJECT_ROOT = Path("/Users/karlg/Documents/Repos/_cedop")
RAW_DIR = PROJECT_ROOT / "app" / "data" / "ich" / "extracted_clean_02"
OUTPUT_DIR = PROJECT_ROOT / "app" / "data" / "ich" / "cleaned_llm"
PROGRESS_FILE = PROJECT_ROOT / "output" / "cdop" / "ich_update" / "clean_progress.json"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Rate limiting
REQUEST_DELAY = 0.5  # seconds between API calls


def clean_with_llm(client: Anthropic, text: str, ich_id: str) -> str:
    """
    Use Claude to extract clean descriptive content VERBATIM from nomination doc.
    """
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


def load_progress():
    """Load progress from checkpoint file."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {'completed': [], 'failed': [], 'skipped': []}


def save_progress(progress):
    """Save progress to checkpoint file."""
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)


def get_files_to_process():
    """Find all nomination files that need cleaning."""
    # Find all *_nomination_clean.txt files (the new extractions)
    nomination_files = list(RAW_DIR.glob("*_nomination_clean.txt"))

    # Sort by ich_id
    nomination_files.sort(key=lambda p: p.stem.split('_')[0])

    return nomination_files


def main():
    parser = argparse.ArgumentParser(description="Batch clean ICH nomination documents")
    parser.add_argument('--limit', type=int, help='Limit number to process')
    parser.add_argument('--resume', action='store_true', help='Resume from checkpoint')
    args = parser.parse_args()

    client = Anthropic()

    # Get files to process
    files = get_files_to_process()
    print(f"Found {len(files)} nomination files to clean")

    # Load progress
    if args.resume:
        progress = load_progress()
        print(f"Resuming: {len(progress['completed'])} already done")
    else:
        progress = {'completed': [], 'failed': [], 'skipped': []}

    completed_ids = set(progress['completed'])

    # Apply limit
    if args.limit:
        files = files[:args.limit]

    # Process files
    total = len(files)
    for i, raw_file in enumerate(files):
        ich_id = raw_file.stem.split('_')[0]

        # Skip if already done
        if ich_id in completed_ids:
            print(f"[{i+1}/{total}] {ich_id} - already done, skipping")
            continue

        # Check if output exists
        out_file = OUTPUT_DIR / f"{ich_id}_cleaned.txt"
        if out_file.exists():
            print(f"[{i+1}/{total}] {ich_id} - output exists, skipping")
            progress['skipped'].append(ich_id)
            continue

        print(f"[{i+1}/{total}] Cleaning {ich_id}...", end=" ", flush=True)

        try:
            # Read raw text
            with open(raw_file) as f:
                raw_text = f.read()

            # Clean with LLM
            cleaned = clean_with_llm(client, raw_text, ich_id)

            # Save output
            with open(out_file, 'w') as f:
                f.write(cleaned)

            progress['completed'].append(ich_id)
            print(f"done ({len(cleaned)} chars)")

            # Rate limiting
            time.sleep(REQUEST_DELAY)

        except Exception as e:
            print(f"FAILED: {e}")
            progress['failed'].append({'ich_id': ich_id, 'error': str(e)})

        # Checkpoint every 10
        if (i + 1) % 10 == 0:
            save_progress(progress)
            print(f"  [Checkpoint: {len(progress['completed'])} completed]")

    # Final save
    save_progress(progress)

    # Summary
    print(f"\n{'='*60}")
    print("BATCH CLEANING COMPLETE")
    print('='*60)
    print(f"  Completed: {len(progress['completed'])}")
    print(f"  Failed: {len(progress['failed'])}")
    print(f"  Skipped: {len(progress['skipped'])}")
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print(f"Progress file: {PROGRESS_FILE}")


if __name__ == "__main__":
    main()
