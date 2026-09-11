"""
Test the full scraper on a single topic (percentage) to validate all fixes.
"""

import json
import re
import time
import random
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE = "https://www.indiabix.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

OUTPUT_FILE = Path("test_percentage_full.json")
DELAY_RANGE = (1.5, 3.0)


def get_soup(url, retries=3):
    """Fetch URL with retry logic."""
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "html.parser")
        except requests.RequestException as e:
            if attempt == retries - 1:
                raise
            print(f"    Retry {attempt + 1}/{retries} after error: {e}")
            time.sleep(random.uniform(2, 4))


def polite_sleep():
    time.sleep(random.uniform(*DELAY_RANGE))


def parse_question_block(block, main_tag, sub_tag):
    """Extract one question's data from a bix-div-container div."""
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
    """Find the 'Next' pagination link, if any."""
    for link in soup.find_all("a", href=True):
        if link.get_text(strip=True).lower() == "next":
            href = link["href"]
            if href and href != "#":
                if href.startswith("/"):
                    return BASE + href
                if href.startswith("http"):
                    return href
    return None


def scrape_topic(path, main_tag, sub_tag, all_questions, seen_qids):
    url = BASE + path
    page_num = 1
    while url:
        print(f"  page {page_num}: {url}")
        try:
            soup = get_soup(url)
        except requests.RequestException as e:
            print(f"    ERROR fetching {url}: {e}")
            break

        blocks = soup.find_all(class_="bix-div-container")
        page_count = 0
        for block in blocks:
            q = parse_question_block(block, main_tag, sub_tag)
            if q and q["qid"] not in seen_qids:
                seen_qids.add(q["qid"])
                all_questions.append(q)
                page_count += 1

        print(f"    extracted {page_count} new questions")

        next_url = find_next_page_url(soup)
        polite_sleep()
        url = next_url
        page_num += 1


def main():
    all_questions = []
    seen_qids = set()

    print(f"Testing full scrape on percentage topic...\n")
    scrape_topic("/aptitude/percentage/", "aptitude", "percentage", all_questions, seen_qids)

    OUTPUT_FILE.write_text(json.dumps(all_questions, indent=2, ensure_ascii=False))

    print(f"\n{'='*60}")
    print(f"Total questions scraped: {len(all_questions)}")
    print(f"Saved to: {OUTPUT_FILE.absolute()}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
