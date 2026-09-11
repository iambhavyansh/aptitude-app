"""Import scraped questions from JSON into database"""
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, engine
from models import Base, Topic, Question

def import_questions(json_file: str):
    """Import questions from JSON file into database"""
    db = SessionLocal()

    try:
        # Load JSON
        with open(json_file, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)

        print(f"Loaded {len(questions_data)} questions from {json_file}")

        # Track topics
        topics_map = {}

        for q_data in questions_data:
            # Get or create topic
            main_tag = q_data['main_tag']
            sub_tag = q_data['sub_tag']

            if sub_tag not in topics_map:
                topic = db.query(Topic).filter(Topic.sub_tag == sub_tag).first()
                if not topic:
                    topic = Topic(main_tag=main_tag, sub_tag=sub_tag)
                    db.add(topic)
                    db.flush()
                    print(f"Created topic: {main_tag} > {sub_tag}")
                topics_map[sub_tag] = topic.id

            topic_id = topics_map[sub_tag]

            # Check if question already exists
            existing = db.query(Question).filter(Question.qid == q_data['qid']).first()
            if existing:
                print(f"Skipping duplicate question: {q_data['qid']}")
                continue

            # Create question
            question = Question(
                qid=q_data['qid'],
                topic_id=topic_id,
                main_tag=main_tag,
                sub_tag=sub_tag,
                question_text=q_data['question'],
                options=q_data['options'],
                correct_answer=q_data['correct_answer'],
                explanation=q_data.get('explanation', ''),
                source=q_data.get('source', 'IndiaBix')
            )
            db.add(question)

        db.commit()
        print(f"Successfully imported questions!")

        # Print summary
        topic_count = db.query(Topic).count()
        question_count = db.query(Question).count()
        print(f"\nDatabase summary:")
        print(f"  Topics: {topic_count}")
        print(f"  Questions: {question_count}")

    except Exception as e:
        db.rollback()
        print(f"Error importing questions: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    json_file = "data/sample_questions.json"
    if len(sys.argv) > 1:
        json_file = sys.argv[1]

    print(f"Importing from {json_file}...")
    import_questions(json_file)
