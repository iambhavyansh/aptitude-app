"""
Convert scraped questions format to match import script expectations
Converts 'answer' field to 'correct_answer'
"""
import json

def convert_questions(input_file, output_file):
    """Convert scraped format to import format"""
    print(f"Loading questions from {input_file}...")

    with open(input_file, 'r', encoding='utf-8') as f:
        questions = json.load(f)

    print(f"Found {len(questions)} questions")

    # Convert format
    converted = []
    for q in questions:
        converted_q = {
            "qid": q["qid"],
            "main_tag": q["main_tag"],
            "sub_tag": q["sub_tag"],
            "question": q["question"],
            "options": q["options"],
            "correct_answer": q["answer"],  # Rename 'answer' to 'correct_answer'
            "explanation": q.get("explanation", "")
        }
        converted.append(converted_q)

    # Save converted questions
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(converted, f, indent=2, ensure_ascii=False)

    print(f"Converted {len(converted)} questions saved to {output_file}")

    # Show stats
    topics = {}
    for q in converted:
        sub_tag = q["sub_tag"]
        topics[sub_tag] = topics.get(sub_tag, 0) + 1

    print(f"\nBreakdown by topic:")
    for topic, count in sorted(topics.items()):
        print(f"  {topic}: {count} questions")

if __name__ == "__main__":
    import sys
    input_file = sys.argv[1] if len(sys.argv) > 1 else "data/questions_scraped.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "data/questions_ready.json"
    convert_questions(input_file, output_file)
