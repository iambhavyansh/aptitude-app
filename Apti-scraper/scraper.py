"""
IndiaBix Aptitude Scraper

Structure confirmed via inspection:
- Topic pages: https://www.indiabix.com/aptitude/<topic-slug>/
- Each question wrapped in div.ques-wrapper
- Question id (qid) embedded in ids like tdOptionDt_A_<qid>, hdnAnswer_<qid>
- Correct answer: <input id="hdnAnswer_<qid>" value="A/B/C/D/E">  (static, no JS needed)
- Explanation: <div id="divAnswer_<qid>" class="bix-div-answer">
- Pagination: "Next" link with an href like /aptitude/percentage/017002
  (not predictable - must follow the link on each page until absent)

Usage:
    pip install requests beautifulsoup4
    python scraper.py

Output: questions.json (appended incrementally, safe to resume/rerun)
"""

import json
import re
import time
import random
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE = "https://www.indiabix.com"

# Add more topic index pages here as needed. Each of these lists sub-topics
# (e.g. /aptitude/questions-and-answers/ lists percentage, time-and-work, etc.)
TOPIC_INDEXES = {
    "aptitude": "/aptitude/questions-and-answers/",
    "logical-reasoning": "/logical-reasoning/questions-and-answers/",
    "verbal-reasoning": "/verbal-reasoning/questions-and-answers/",
    "non-verbal-reasoning": "/non-verbal-reasoning/questions-and-answers/",
    "verbal-ability": "/verbal-ability/questions-and-answers/",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

OUTPUT_FILE = Path("questions.json")
DELAY_RANGE = (1.5, 3.0)  # polite delay between requests, seconds


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


def discover_subtopics(index_path, main_tag):
    """Given a topic index page, find all sub-topic links under it."""
    url = BASE + index_path
    soup = get_soup(url)
    subtopics = []
    # Sub-topic links live in the sidebar/quick-links area and point to
    # /<main_tag>/<sub-topic-slug>/ paths. Filter to same main_tag prefix.
    prefix = f"/{main_tag}/"
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith(BASE):
            href = href[len(BASE):]
        # Filter: starts with prefix, not the index page itself, has exactly 3 parts (/, main_tag, sub-topic)
        if href.startswith(prefix) and href != index_path:
            # Count slashes: /aptitude/percentage/ has 3 slashes at positions 0, 9, and end
            parts = href.strip("/").split("/")
            if len(parts) == 2:  # e.g., ['aptitude', 'percentage']
                slug = parts[1]
                if slug and slug not in seen and slug != "questions-and-answers":
                    seen.add(slug)
                    subtopics.append(href if href.endswith("/") else href + "/")
    return subtopics


def parse_question_block(block, main_tag, sub_tag):
    """Extract one question's data from a ques-wrapper div."""
    # Question id: pull from any child id matching hdnAnswer_<qid>
    hidden = block.find("input", id=re.compile(r"^hdnAnswer_\d+$"))
    if not hidden:
        return None
    qid = hidden["id"].split("_")[-1]
    answer_letter = hidden.get("value", "").strip()

    # Question text: usually in a div with class containing 'bix-td-qtxt' or similar
    qtext_el = block.find(class_=re.compile("qtxt|ques-text|bix-td-qtxt"))
    if qtext_el:
        question_text = qtext_el.get_text(" ", strip=True)
    else:
        # fallback: first significant text block before options
        question_text = block.get_text(" ", strip=True)[:500]

    # Options: divs with id tdOptionDt_<LETTER>_<qid>
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
        # Strip the leading "Answer: Option X Explanation:" boilerplate if present
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
        print(f"  scraping {sub_tag} page {page_num}: {url}")
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

    # Resume support: load existing output if present
    if OUTPUT_FILE.exists():
        try:
            existing = json.loads(OUTPUT_FILE.read_text())
            all_questions = existing
            seen_qids = {q["qid"] for q in existing}
            print(f"Resuming: loaded {len(all_questions)} existing questions")
        except Exception:
            pass

    for main_tag, index_path in TOPIC_INDEXES.items():
        print(f"Discovering subtopics for {main_tag}...")
        try:
            subtopics = discover_subtopics(index_path, main_tag)
        except requests.RequestException as e:
            print(f"  ERROR discovering {main_tag}: {e}")
            continue
        print(f"  found {len(subtopics)} subtopics")
        polite_sleep()

        for sub_path in subtopics:
            sub_tag = sub_path.strip("/").split("/")[-1]
            print(f"  Scraping {sub_tag}...")
            scrape_topic(sub_path, main_tag, sub_tag, all_questions, seen_qids)
            # Save incrementally after every subtopic so a crash doesn't lose progress
            OUTPUT_FILE.write_text(json.dumps(all_questions, indent=2, ensure_ascii=False))
            print(f"    saved. Total questions so far: {len(all_questions)}")

    print(f"\n{'='*60}")
    print(f"SCRAPING COMPLETE")
    print(f"{'='*60}")
    print(f"Total questions scraped: {len(all_questions)}")

    # Generate breakdown by sub_tag
    from collections import Counter
    by_main = Counter(q["main_tag"] for q in all_questions)
    by_sub = Counter(q["sub_tag"] for q in all_questions)

    print(f"\nBreakdown by main category:")
    for tag, count in sorted(by_main.items()):
        print(f"  {tag}: {count} questions")

    print(f"\nBreakdown by sub-topic:")
    for tag, count in sorted(by_sub.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {tag}: {count} questions")

    # Flag suspiciously low counts (< 5 questions might indicate scraper issues)
    low_count_topics = [tag for tag, count in by_sub.items() if count < 5]
    if low_count_topics:
        print(f"\n⚠️  Topics with < 5 questions (possible scraper issues):")
        for tag in sorted(low_count_topics):
            print(f"  {tag}: {by_sub[tag]} questions")

    print(f"\nOutput saved to: {OUTPUT_FILE.absolute()}")


if __name__ == "__main__":
    main()