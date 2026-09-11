"""
Test script to validate scraper selectors against the percentage topic only.
This will scrape just 1-2 pages to verify everything works before running the full scraper.
"""

import json
import re
import time
import random
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

def parse_question_block(block, main_tag, sub_tag):
    """Extract one question's data from a ques-wrapper div."""
    hidden = block.find("input", id=re.compile(r"^hdnAnswer_\d+$"))
    if not hidden:
        return None

    qid = hidden["id"].split("_")[-1]
    answer_letter = hidden.get("value", "").strip()

    # Question text
    qtext_el = block.find(class_=re.compile("qtxt|ques-text|bix-td-qtxt"))
    if qtext_el:
        question_text = qtext_el.get_text(" ", strip=True)
    else:
        question_text = block.get_text(" ", strip=True)[:500]

    # Options
    options = {}
    for letter in ["A", "B", "C", "D", "E"]:
        opt_el = block.find(id=f"tdOptionDt_{letter}_{qid}")
        if opt_el:
            options[letter] = opt_el.get_text(" ", strip=True)

    # Explanation
    explanation = ""
    exp_div = block.find(id=f"divAnswer_{qid}")
    if exp_div:
        exp_text = exp_div.get_text(" ", strip=True)
        explanation = re.sub(r"^Answer:\s*Option\s*[A-E]?\s*Explanation:\s*", "", exp_text)

    return {
        "qid": qid,
        "main_tag": main_tag,
        "sub_tag": sub_tag,
        "question": question_text,
        "options": options,
        "answer": answer_letter,
        "explanation": explanation,
    }

def find_next_page_url(soup):
    """Find the 'Next' pagination link."""
    # Find all links and check if their text contains "Next"
    for link in soup.find_all("a", href=True):
        if link.get_text(strip=True).lower() == "next":
            href = link["href"]
            if href and href != "#":
                if href.startswith("/"):
                    return BASE + href
                if href.startswith("http"):
                    return href
    return None

def main():
    url = BASE + "/aptitude/percentage/"
    questions = []
    page_count = 0
    max_pages = 2  # Test just 2 pages

    print(f"Testing scraper on: {url}\n")

    while url and page_count < max_pages:
        page_count += 1
        print(f"Scraping page {page_count}: {url}")

        try:
            soup = get_soup(url)
        except requests.RequestException as e:
            print(f"ERROR: {e}")
            break

        blocks = soup.find_all(class_="bix-div-container")
        print(f"  Found {len(blocks)} question blocks")

        for block in blocks:
            q = parse_question_block(block, "aptitude", "percentage")
            if q:
                questions.append(q)

        print(f"  Extracted {len(questions)} total questions so far")

        # Find next page
        next_url = find_next_page_url(soup)
        if next_url:
            print(f"  Next page: {next_url}")
            time.sleep(random.uniform(1.5, 3.0))
            url = next_url
        else:
            print("  No next page found")
            break

    print(f"\n{'='*60}")
    print(f"Total questions scraped: {len(questions)}")
    print(f"{'='*60}\n")

    # Print first 2 questions as samples
    for i, q in enumerate(questions[:2], 1):
        print(f"Sample Question #{i}:")
        print(f"  QID: {q['qid']}")
        print(f"  Question: {q['question'][:100]}...")
        print(f"  Options: {list(q['options'].keys())}")
        print(f"  Answer: {q['answer']}")
        print(f"  Explanation: {q['explanation'][:80]}...")
        print()

    # Save to test output
    with open("test_output.json", "w") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(questions)} questions to test_output.json")

if __name__ == "__main__":
    main()
