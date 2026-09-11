"""
Debug pagination link detection.
"""

import re
import requests
from bs4 import BeautifulSoup

BASE = "https://www.indiabix.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}

url = BASE + "/aptitude/percentage/"
resp = requests.get(url, headers=HEADERS, timeout=20)
soup = BeautifulSoup(resp.text, "html.parser")

print("=== Testing Next link detection ===\n")

# Current approach
next_link = soup.find("a", string=re.compile(r"^\s*Next\s*$", re.IGNORECASE))
print(f"Method 1 (string regex): {next_link}")

# Try with text parameter
next_link2 = soup.find("a", text=re.compile(r"^\s*Next\s*$", re.IGNORECASE))
print(f"Method 2 (text regex): {next_link2}")

# Try finding all links with "Next" in text
all_links = soup.find_all("a", href=True)
next_candidates = [a for a in all_links if "next" in a.get_text().lower()]
print(f"\nAll links with 'next' in text: {len(next_candidates)}")
for a in next_candidates:
    print(f"  Text: '{a.get_text()}' (stripped: '{a.get_text().strip()}')")
    print(f"  Href: {a.get('href')}")
    print(f"  Classes: {a.get('class', [])}")
    print()
