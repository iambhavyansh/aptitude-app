#!/usr/bin/env python3
"""
Monitor the scraper's progress.
"""

import json
import time
import sys
from pathlib import Path

output_file = Path("questions.json")
last_count = 0

print("Monitoring scraper progress... (Ctrl+C to stop monitoring)\n")

try:
    while True:
        if output_file.exists():
            try:
                with open(output_file) as f:
                    data = json.load(f)
                count = len(data)

                if count != last_count:
                    from collections import Counter
                    by_main = Counter(q['main_tag'] for q in data)

                    timestamp = time.strftime("%H:%M:%S")
                    print(f"[{timestamp}] Total: {count} questions", end="")
                    if by_main:
                        print(f" | By section: {dict(by_main)}")
                    else:
                        print()

                    last_count = count
            except (json.JSONDecodeError, IOError):
                pass  # File being written, try again

        time.sleep(30)  # Check every 30 seconds

except KeyboardInterrupt:
    print("\nMonitoring stopped.")
    sys.exit(0)
