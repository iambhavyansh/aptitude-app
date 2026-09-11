#!/usr/bin/env python3
"""
Filter questions.json to remove image-based questions with empty options.
Creates questions_clean.json with only usable questions.
"""

import json
from collections import Counter

# Load all questions
with open('questions.json') as f:
    all_questions = json.load(f)

print(f"Original questions: {len(all_questions)}")

# Filter out questions with empty options (image-based)
clean_questions = []
excluded_questions = []

for q in all_questions:
    options = q.get('options', {})
    # Count empty options
    empty_count = sum(1 for v in options.values() if not v or len(v.strip()) < 3)

    # Keep questions where most options have text
    if empty_count < 2:  # Less than 2 empty options = usable
        clean_questions.append(q)
    else:
        excluded_questions.append(q)

print(f"Usable questions: {len(clean_questions)}")
print(f"Excluded (image-based): {len(excluded_questions)}")

# Save cleaned version
with open('questions_clean.json', 'w') as f:
    json.dump(clean_questions, f, indent=2, ensure_ascii=False)

print(f"\n✅ Saved clean questions to: questions_clean.json")

# Save excluded for reference
with open('questions_excluded_images.json', 'w') as f:
    json.dump(excluded_questions, f, indent=2, ensure_ascii=False)

print(f"📋 Saved excluded questions to: questions_excluded_images.json")

# Statistics
by_main = Counter(q['main_tag'] for q in clean_questions)
by_sub = Counter(q['sub_tag'] for q in clean_questions)

print(f"\n{'='*60}")
print(f"CLEAN DATASET SUMMARY")
print(f"{'='*60}")
print(f"Total usable questions: {len(clean_questions)}")

print(f"\nBy section:")
for tag, count in sorted(by_main.items()):
    print(f"  {tag}: {count}")

print(f"\nTop 20 subtopics:")
for tag, count in by_sub.most_common(20):
    print(f"  {tag}: {count}")

print(f"\nSubtopics with < 5 questions:")
low_count = [(tag, count) for tag, count in by_sub.items() if count < 5]
if low_count:
    for tag, count in sorted(low_count):
        print(f"  {tag}: {count}")
else:
    print("  None - all subtopics have 5+ questions!")
