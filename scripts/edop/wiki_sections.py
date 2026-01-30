import wikipediaapi
import pandas as pd
from collections import Counter
import re
from urllib.parse import unquote

# 1. Setup the API
wiki = wikipediaapi.Wikipedia(
  user_agent="WorldHeritageAudit/1.0 (karl.geog@gmail.com)",
  language='en'
)


def extract_title_from_url(url):
  # Extracts the page title from the Wikipedia URL
  title = url.split('/')[-1]
  return unquote(title).replace('_', ' ')


# 2. Load your file
with open('app/data/wh_cities_urls.txt', 'r') as f:
  urls = [line.strip() for line in f if line.strip()]

all_headings = []
results = []

print(f"Auditing {len(urls)} cities...")

# 3. Iterate and Inventory
for url in urls:
  title = extract_title_from_url(url)
  page = wiki.page(title)

  if page.exists():
    # Get top-level sections only
    sections = [s.title for s in page.sections]
    all_headings.extend(sections)
    results.append({"city": title, "sections": sections})
  else:
    print(f"Warning: Could not find page for {title}")

# 4. Analyze Consistency
heading_counts = Counter(all_headings)
report = pd.DataFrame(heading_counts.items(), columns=['Heading', 'Count'])
report = report.sort_values(by='Count', ascending=False)

# 5. Output the results
print("\n--- TOP HEADINGS BY CONSISTENCY ---")
print(report.head(15))  # Show top 15 most common headers

# Optional: Save to CSV to inspect in Excel
report.to_csv("app/data/section_consistency_report.csv", index=False)