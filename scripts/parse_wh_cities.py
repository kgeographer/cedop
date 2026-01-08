#!/usr/bin/env python3
"""
Parse Wikipedia "Organization of World Heritage Cities" member-city HTML
(view-source saved HTML fragment) into a TSV.

Expected structure:
  <h3>Region</h3>
  <ul>
    <li><a href="/wiki/City" title="City">City</a> (... country/flags ...)</li>
    ...
  </ul>

Output columns:
  region, city, href, slug, title, country, country_href, country_slug
"""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Optional
from bs4 import BeautifulSoup, Tag


WIKI_PREFIX = "/wiki/"
W_INDEX_PREFIX = "/w/index.php?"


def href_to_slug(href: str) -> str:
    """
    Extract a reasonable "slug" from a Wikipedia href.
    - /wiki/Foo -> Foo
    - /w/index.php?title=Foo&... -> Foo
    - otherwise -> href as-is (best-effort)
    """
    if href.startswith(WIKI_PREFIX):
        return href[len(WIKI_PREFIX):]
    if href.startswith(W_INDEX_PREFIX):
        # pull title=... if present
        m = re.search(r"(?:\?|&)title=([^&]+)", href)
        if m:
            return m.group(1)
    return href


def is_city_anchor(a: Tag) -> bool:
    """
    Heuristic: in these list items, the first <a> is the city.
    We still exclude obvious non-article anchors if any.
    """
    href = (a.get("href") or "").strip()
    if not href:
        return False
    # Accept normal wiki links and index.php links (including redlinks).
    return href.startswith(WIKI_PREFIX) or href.startswith(W_INDEX_PREFIX)


def parse_wh_cities_html(html_path: Path) -> list[dict[str, str]]:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")

    rows: list[dict[str, str]] = []
    current_region: Optional[str] = None

    # Walk in document order to associate <li> with the most recent <h3>.
    for node in soup.find_all(["h3", "li"]):
        if node.name == "h3":
            # Region name is the visible text in the h3
            region = node.get_text(" ", strip=True)
            if region:
                current_region = region
            continue

        # node is <li>
        if current_region is None:
            # In case there are list items before the first region header
            current_region = ""

        # The city link is the first <a> in the <li>
        a_tags = node.find_all("a", recursive=True)
        city_a = None
        for a in a_tags:
            if is_city_anchor(a):
                city_a = a
                break

        if city_a is None:
            continue

        city_text = city_a.get_text(" ", strip=True)
        href = (city_a.get("href") or "").strip()
        title = (city_a.get("title") or "").strip()
        slug = href_to_slug(href)

        # The country link is typically the last <a> in the <li>
        country_a: Optional[Tag] = None
        for a in reversed(a_tags):
            if is_city_anchor(a):
                country_a = a
                break

        country = ""
        country_href = ""
        country_slug = ""
        if country_a is not None:
            country = country_a.get_text(" ", strip=True)
            country_href = (country_a.get("href") or "").strip()
            country_slug = href_to_slug(country_href) if country_href else ""

        # If we somehow only found the city link, avoid duplicating city as country
        if country_href == href:
            country = ""
            country_href = ""
            country_slug = ""

        if not city_text or not href:
            continue

        rows.append(
            {
                "region": current_region,
                "city": city_text,
                "href": href,
                "slug": slug,
                "title": title,
                "country": country,
                "country_href": country_href,
                "country_slug": country_slug,
            }
        )

    return rows


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    fieldnames = [
        "region",
        "city",
        "href",
        "slug",
        "title",
        "country",
        "country_href",
        "country_slug",
    ]
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("html_file", help="Path to saved HTML (e.g., wh_cities_raw.html)")
    ap.add_argument(
        "-o",
        "--out",
        default="wh_cities.tsv",
        help="Output TSV path (default: wh_cities.tsv)",
    )
    args = ap.parse_args()

    html_path = Path(args.html_file)
    out_path = Path(args.out)

    rows = parse_wh_cities_html(html_path)
    write_tsv(rows, out_path)

    print(f"Wrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()