"""
Debug subtopic discovery to see what's going wrong.
"""

import requests
from bs4 import BeautifulSoup

BASE = "https://www.indiabix.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}

# Test with aptitude
index_path = "/aptitude/questions-and-answers/"
main_tag = "aptitude"

url = BASE + index_path
print(f"Fetching: {url}\n")

resp = requests.get(url, headers=HEADERS, timeout=20)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

print("=== All links on the page ===")
prefix = f"/{main_tag}/"
all_links = soup.find_all("a", href=True)

print(f"Total links: {len(all_links)}")
print(f"\nLinks starting with '{prefix}':")

count = 0
for a in all_links:
    href = a["href"]
    if href.startswith(BASE):
        href = href[len(BASE):]

    if href.startswith(prefix):
        count += 1
        if count <= 20:  # Show first 20
            print(f"  {href}")
            print(f"    Text: {a.get_text(strip=True)[:50]}")

print(f"\nTotal links with prefix '{prefix}': {count}")

# Check what the actual structure is
print("\n=== Checking for topic list containers ===")
topics_divs = soup.find_all(class_=lambda x: x and ('topic' in str(x).lower() or 'category' in str(x).lower()))
print(f"Found {len(topics_divs)} divs with 'topic' or 'category' in class")

# Look for common sidebar/navigation patterns
print("\n=== Sidebar/navigation elements ===")
sidebars = soup.find_all(['aside', 'nav'])
print(f"Found {len(sidebars)} aside/nav elements")
