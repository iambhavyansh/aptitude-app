"""
Step 1c: We found the answer is stored in a hidden <input id="hdnAnswer_NNN"
class="jq-hdnakq"> element. Text content is empty because it's an <input> -
the real value is in the 'value' attribute. This script prints that,
alongside the question number, to confirm the format (e.g. "A", "1", etc.)
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
    soup = BeautifulSoup(resp.text, "html.parser")

    hidden_inputs = soup.find_all("input", id=re.compile(r"^hdnAnswer_\d+$"))
    print(f"Found {len(hidden_inputs)} hidden answer inputs\n")

    for inp in hidden_inputs:
        qid = inp.get("id")
        value = inp.get("value")
        # print all attributes in case value isn't where we expect
        print(f"{qid}: value={value!r} all_attrs={dict(inp.attrs)}")

    # Also print full outer HTML of the first one so we see every attribute
    if hidden_inputs:
        print("\n=== Full HTML of first hidden input ===")
        print(hidden_inputs[0])

        # And print the surrounding question container to map qid -> question text
        print("\n=== Parent chain of first hidden input (to find question container id) ===")
        parent = hidden_inputs[0].parent
        depth = 0
        while parent and depth < 5:
            print(f"depth={depth} tag={parent.name} id={parent.get('id')} class={parent.get('class')}")
            parent = parent.parent
            depth += 1

if __name__ == "__main__":
    main()