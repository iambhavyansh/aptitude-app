"""
Step 1b: Dump the main content area of an IndiaBix page to find the real
question/answer markup. The previous approach (searching for literal
"Answer: Option" text) failed because the text isn't laid out that way in
the raw HTML - it's likely split across elements or revealed by JS/CSS.

This version:
1. Saves the FULL raw HTML to a file so we can grep/search it properly.
2. Tries several likely selectors for the question container and prints
   whatever it finds.
3. Prints a list of every id containing a digit (question blocks are often
   div id="question_316" style ids) so we can spot the pattern.
"""

import re
import requests
from bs4 import BeautifulSoup

URL = "https://www.indiabix.com/aptitude/percentage/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

def main():
    resp = requests.get(URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    html = resp.text

    # Save raw HTML for manual inspection / grep
    with open("raw_page.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Saved raw HTML to raw_page.html ({len(html)} chars)")

    soup = BeautifulSoup(html, "html.parser")

    # Find all ids that look like question containers (numeric suffix)
    print("\n=== Elements with numeric-suffixed ids (likely question blocks) ===")
    numeric_id_els = soup.find_all(id=re.compile(r"\d+$"))
    seen_prefixes = set()
    for el in numeric_id_els[:40]:
        prefix = re.sub(r"\d+$", "", el.get("id", ""))
        if prefix not in seen_prefixes:
            seen_prefixes.add(prefix)
            print(f"  tag={el.name} id={el.get('id')} class={el.get('class')}")

    # Find anything with "answer" in its id or class (case-insensitive)
    print("\n=== Elements with 'answer' in id/class ===")
    answer_els = soup.find_all(
        lambda tag: (tag.get("id") and "answer" in tag.get("id").lower())
        or (tag.get("class") and any("answer" in c.lower() for c in tag.get("class")))
    )
    for el in answer_els[:20]:
        print(f"  tag={el.name} id={el.get('id')} class={el.get('class')}")
        print(f"    text preview: {el.get_text(strip=True)[:100]}")

    # Find anything with "correct" or "right" in id/class (common naming for the right option)
    print("\n=== Elements with 'correct'/'right'/'jq-' in id/class ===")
    correct_els = soup.find_all(
        lambda tag: tag.get("class")
        and any(
            re.search(r"correct|right|jq-", c, re.IGNORECASE)
            for c in tag.get("class")
        )
    )
    for el in correct_els[:20]:
        print(f"  tag={el.name} id={el.get('id')} class={el.get('class')}")
        print(f"    text preview: {el.get_text(strip=True)[:100]}")

    # Print the first <script> tags - IndiaBix commonly stores the answer key
    # in an inline JS variable/JSON rather than in the option markup itself.
    print("\n=== Inline <script> tags mentioning 'answer' or 'correct' ===")
    for script in soup.find_all("script"):
        content = script.string or ""
        if content and re.search(r"answer|correct", content, re.IGNORECASE):
            print(content[:1500])
            print("---")

if __name__ == "__main__":
    main()