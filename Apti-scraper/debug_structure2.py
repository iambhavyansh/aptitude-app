"""
Find the actual per-question container structure.
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

# We know there are 5 questions based on hidden inputs
hidden_answers = soup.find_all("input", id=re.compile(r"^hdnAnswer_\d+$"))
print(f"Found {len(hidden_answers)} questions based on hidden inputs\n")

# For each hidden input, find its containing card/question block
for i, hidden in enumerate(hidden_answers, 1):
    qid = hidden['id'].split('_')[-1]
    print(f"=== Question {i} (QID: {qid}) ===")

    # Find the immediate container that has all parts of this question
    parent = hidden.parent
    depth = 0
    while parent and depth < 10:
        # Check if this parent contains the options for this qid
        opt_a = parent.find(id=f"tdOptionDt_A_{qid}")
        opt_b = parent.find(id=f"tdOptionDt_B_{qid}")

        if opt_a and opt_b:
            classes = parent.get('class', [])
            print(f"  Question container: <{parent.name}> class={classes}")

            # Look for question text element
            qtxt_candidates = parent.find_all(class_=re.compile("qtxt|question"))
            if qtxt_candidates:
                print(f"  Question text candidates: {len(qtxt_candidates)}")
                print(f"    First 80 chars: {qtxt_candidates[0].get_text(' ', strip=True)[:80]}")

            break

        parent = parent.parent
        depth += 1

    if depth >= 10:
        print("  ERROR: Could not find question container!")

    print()
