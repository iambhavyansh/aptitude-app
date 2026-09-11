"""
Debug script to inspect the actual HTML structure of the percentage page.
"""

import requests
from bs4 import BeautifulSoup

BASE = "https://www.indiabix.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}

url = BASE + "/aptitude/percentage/"
print(f"Fetching: {url}\n")

resp = requests.get(url, headers=HEADERS, timeout=20)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

# Check for different question wrapper patterns
print("=== Searching for question containers ===")
print(f"div.ques-wrapper: {len(soup.find_all('div', class_='ques-wrapper'))}")
print(f"div containing 'ques': {len(soup.find_all('div', class_=lambda x: x and 'ques' in str(x).lower()))}")
print(f"All divs with 'bix' in class: {len(soup.find_all('div', class_=lambda x: x and 'bix' in str(x).lower()))}")

# Look for hidden answer inputs (these should definitely be there)
import re
hidden_answers = soup.find_all("input", id=re.compile(r"^hdnAnswer_\d+$"))
print(f"\nHidden answer inputs found: {len(hidden_answers)}")

if hidden_answers:
    print("\nFirst 5 hidden answer IDs:")
    for inp in hidden_answers[:5]:
        print(f"  {inp.get('id')} = {inp.get('value')}")

    # Trace parent structure of first hidden input
    print("\n=== Parent structure of first hidden input ===")
    parent = hidden_answers[0].parent
    depth = 0
    while parent and depth < 8:
        classes = parent.get('class', [])
        pid = parent.get('id', '')
        print(f"  Level {depth}: <{parent.name}> id='{pid}' class={classes}")
        parent = parent.parent
        depth += 1

# Look for pagination
print("\n=== Pagination links ===")
all_links = soup.find_all('a', href=True)
next_candidates = [a for a in all_links if 'next' in a.get_text().lower()]
print(f"Links with 'next' text: {len(next_candidates)}")
for a in next_candidates[:3]:
    print(f"  Text: '{a.get_text().strip()}' | href: {a.get('href')}")

# Look for page numbers
page_links = [a for a in all_links if a.get('href', '').startswith('/aptitude/percentage/')]
print(f"\nLinks to /aptitude/percentage/: {len(page_links)}")
for a in page_links[:10]:
    print(f"  {a.get_text().strip()[:30]} -> {a.get('href')}")
