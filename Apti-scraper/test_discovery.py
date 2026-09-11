"""
Test the fixed discover_subtopics function.
"""

import requests
from bs4 import BeautifulSoup

BASE = "https://www.indiabix.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}

def get_soup(url):
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def discover_subtopics(index_path, main_tag):
    """Given a topic index page, find all sub-topic links under it."""
    url = BASE + index_path
    soup = get_soup(url)
    subtopics = []
    prefix = f"/{main_tag}/"
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith(BASE):
            href = href[len(BASE):]
        # Filter: starts with prefix, not the index page itself, has exactly 3 parts (/, main_tag, sub-topic)
        if href.startswith(prefix) and href != index_path:
            parts = href.strip("/").split("/")
            if len(parts) == 2:  # e.g., ['aptitude', 'percentage']
                slug = parts[1]
                if slug and slug not in seen and slug != "questions-and-answers":
                    seen.add(slug)
                    subtopics.append(href if href.endswith("/") else href + "/")
    return subtopics

# Test with aptitude
print("Testing aptitude subtopic discovery...")
subtopics = discover_subtopics("/aptitude/questions-and-answers/", "aptitude")
print(f"Found {len(subtopics)} subtopics:")
for st in sorted(subtopics[:10]):
    print(f"  {st}")

if len(subtopics) > 10:
    print(f"  ... and {len(subtopics) - 10} more")
