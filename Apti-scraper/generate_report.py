#!/usr/bin/env python3
"""
Final Summary Report for IndiaBix Scraper
"""

import json
from collections import Counter

print("="*70)
print("INDIABIX SCRAPER - FINAL SUMMARY REPORT")
print("="*70)
print()

# Load all questions
with open('questions.json') as f:
    all_questions = json.load(f)

# Load clean questions
with open('questions_clean.json') as f:
    clean_questions = json.load(f)

print(f"📊 SCRAPING RESULTS")
print(f"{'─'*70}")
print(f"Total questions scraped:        {len(all_questions)}")
print(f"Usable questions (text-based):  {len(clean_questions)}")
print(f"Excluded (require images):      {len(all_questions) - len(clean_questions)}")
print(f"Success rate:                   {len(clean_questions)/len(all_questions)*100:.1f}%")
print()

# Section breakdown
by_main = Counter(q['main_tag'] for q in clean_questions)
by_sub = Counter(q['sub_tag'] for q in clean_questions)

print(f"📚 BREAKDOWN BY SECTION")
print(f"{'─'*70}")
for tag, count in sorted(by_main.items()):
    pct = count / len(clean_questions) * 100
    print(f"  {tag:25} {count:4} questions ({pct:5.1f}%)")
print()

print(f"🎯 SUBTOPICS SUMMARY")
print(f"{'─'*70}")
print(f"Total unique subtopics:         {len(by_sub)}")
print()

print(f"Top 25 subtopics by question count:")
for i, (tag, count) in enumerate(by_sub.most_common(25), 1):
    print(f"  {i:2}. {tag:35} {count:3} questions")
print()

# Low count topics
low_count = [(tag, count) for tag, count in by_sub.items() if count < 5]
if low_count:
    print(f"⚠️  SUBTOPICS WITH LOW QUESTION COUNTS (<5)")
    print(f"{'─'*70}")
    print(f"These may indicate scraper issues or naturally small topics:")
    for tag, count in sorted(low_count, key=lambda x: x[1]):
        print(f"  {tag:35} {count} question(s)")
    print()

# Data quality check - sample questions
print(f"✅ DATA QUALITY CHECK")
print(f"{'─'*70}")

# Check unique QIDs
unique_qids = len(set(q['qid'] for q in clean_questions))
print(f"Unique QIDs:                    {unique_qids}/{len(clean_questions)}")
if unique_qids == len(clean_questions):
    print(f"  ✅ No duplicate questions")
else:
    print(f"  ⚠️  {len(clean_questions) - unique_qids} duplicate(s) found")

# Check completeness
questions_with_answer = sum(1 for q in clean_questions if q.get('answer'))
questions_with_explanation = sum(1 for q in clean_questions if q.get('explanation'))
questions_with_options = sum(1 for q in clean_questions if len(q.get('options', {})) >= 4)

print(f"Questions with answer:          {questions_with_answer}/{len(clean_questions)} ({questions_with_answer/len(clean_questions)*100:.1f}%)")
print(f"Questions with explanation:     {questions_with_explanation}/{len(clean_questions)} ({questions_with_explanation/len(clean_questions)*100:.1f}%)")
print(f"Questions with 4+ options:      {questions_with_options}/{len(clean_questions)} ({questions_with_options/len(clean_questions)*100:.1f}%)")
print()

# Sample question
print(f"📝 SAMPLE QUESTION")
print(f"{'─'*70}")
sample = clean_questions[100]
print(f"QID: {sample['qid']}")
print(f"Section: {sample['main_tag']} / {sample['sub_tag']}")
print(f"Question: {sample['question'][:150]}...")
print(f"Options:")
for k, v in sorted(sample['options'].items()):
    print(f"  {k}: {v[:80]}")
print(f"Answer: {sample['answer']}")
print(f"Explanation: {sample['explanation'][:150]}...")
print()

print(f"="*70)
print(f"📁 OUTPUT FILES")
print(f"="*70)
print(f"questions.json                  - All scraped questions (963)")
print(f"questions_clean.json            - Usable questions only (740)")
print(f"questions_excluded_images.json  - Image-based questions (223)")
print()

print(f"="*70)
print(f"✅ SCRAPING COMPLETE!")
print(f"="*70)
print(f"Ready to use: questions_clean.json with {len(clean_questions)} verified questions")
print()
