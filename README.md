# Aptitude Quiz Platform

A lightweight quiz platform for aptitude practice with friends and classmates. Admin creates quizzes, participants take them via shared links.

## 📁 Project Structure

```
aptitude-test-platform/
├── main.py                      # FastAPI application (main entry point)
├── config.py                    # Configuration from .env
├── database.py                  # Database connection setup
├── models.py                    # SQLAlchemy database models
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (create from .env.example)
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
├── README.md                    # This file
│
├── templates/                   # HTML templates (Jinja2)
│   ├── base.html
│   ├── home.html
│   ├── admin_login.html
│   ├── admin_dashboard.html
│   ├── quiz_start.html
│   ├── take_quiz.html
│   ├── quiz_result.html
│   └── quiz_results.html
│
├── scripts/                     # Utility scripts
│   ├── setup.sh                 # One-command project setup
│   ├── run.sh                   # Start the application
│   ├── init_db.py               # Initialize database tables
│   ├── import_questions.py      # Import questions from JSON
│   ├── convert_format.py        # Convert scraped format to import format
│   └── scraper.py               # Web scraper template
│
├── data/                        # Question data files
│   ├── sample_questions.json    # 8 sample questions for testing
│   ├── questions_scraped.json   # Original scraped questions (740)
│   └── questions_ready.json     # Converted questions ready for import (740)
│
└── docs/                        # Additional documentation
    ├── QUICKSTART.md            # Quick start guide
    └── PROJECT_SUMMARY.md       # Technical overview
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8+
- PostgreSQL database (Supabase recommended)

### 2. Setup

```bash
# Clone or navigate to project directory
cd aptitude-test-platform

# Create environment file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

**Required .env variables:**
```
DATABASE_URL=postgresql://postgres:[password]@[host]/postgres
ADMIN_PASSWORD=your_secure_password
SECRET_KEY=any-random-string
```

Get your `DATABASE_URL` from Supabase: Settings → Database → Connection String (URI mode)

### 3. Run Setup Script

```bash
./scripts/setup.sh
```

This will:
- Create Python virtual environment
- Install all dependencies
- Initialize database tables
- Import questions (740 scraped questions or 8 sample questions)

### 4. Start the Application

```bash
./scripts/run.sh
```

Visit: **http://localhost:8000**

## 📊 Features

### Admin Features
- Password-protected dashboard
- Create quizzes with custom settings:
  - Select questions by topic (with sliders)
  - Set time limits
  - Configure marking scheme (positive/negative marking)
  - Toggle explanations visibility
- View results for all participants
- Get shareable quiz links

### Participant Features
- Take quiz via shared link
- Countdown timer with auto-submit
- View score after submission
- See correct answers and explanations (if enabled by admin)

### Quiz Mechanics
- **Locked question sets**: Questions randomly selected once at creation
- **Individual timers**: Each participant's timer starts when they begin
- **Auto-submit**: Quiz automatically submits when time expires
- **Flexible scoring**: Support for negative marking

## 📚 Usage Guide

### As Admin

1. **Login**
   - Go to `http://localhost:8000/admin/login`
   - Enter your admin password (from `.env`)

2. **Create Quiz**
   - Set quiz title and time limit
   - Configure marking: marks for correct (+1), marks for wrong (-0.25 or 0)
   - Use sliders to select number of questions from each topic
   - Toggle "Show explanations" if you want participants to see answers
   - Click "Create Quiz"

3. **Share Quiz**
   - Copy the share link from the results page
   - Send it to participants via any messaging platform

4. **View Results**
   - Click "View Results" on any quiz
   - See all participant scores, time taken, and submission times

### As Participant

1. **Access Quiz**
   - Open the shared link
   - Enter your name
   - Click "Start Quiz"

2. **Take Quiz**
   - Answer questions (timer visible in top-right)
   - Click "Submit Quiz" when done
   - Quiz auto-submits if time expires

3. **View Results**
   - See your score immediately
   - Review correct answers (if enabled by admin)
   - Read explanations for each question

## 🗄️ Database Schema

- **topics**: Topic categories (main_tag, sub_tag)
- **questions**: Question bank with options, correct answer, explanation
- **quizzes**: Quiz metadata and locked question set (question_ids array)
- **attempts**: Individual participant attempts with answers and scores

## 📝 Adding More Questions

### Option 1: Use Existing Scraped Questions
Already done! 740 questions across 47 topics imported via `setup.sh`

### Option 2: Add More from JSON
```bash
# Create JSON file following this format:
[
  {
    "qid": "unique_id",
    "main_tag": "Aptitude",
    "sub_tag": "Time and Work",
    "question": "Question text?",
    "options": {
      "A": "Option A",
      "B": "Option B",
      "C": "Option C",
      "D": "Option D"
    },
    "correct_answer": "A",
    "explanation": "Explanation text"
  }
]

# Import it
source venv/bin/activate
python scripts/import_questions.py your_questions.json
```

### Option 3: Scrape More Questions
Customize `scripts/scraper.py` to scrape from your source, then:
```bash
python scripts/scraper.py
python scripts/convert_format.py scraped.json converted.json
python scripts/import_questions.py converted.json
```

## 🛠️ Available Topics (740 Questions)

The scraped questions cover 47 topics:

**Aptitude Topics:**
- Numbers (88), Problems on Trains (26), Time & Work (25)
- Decimal Fraction (26), Problems on HCF & LCM (19)
- Area, Percentage, Profit & Loss, Time & Distance, etc.

**Reasoning Topics:**
- Logical Deduction (51), Statement & Argument (55)
- Course of Action (50), Series Completion (23)
- Statement & Assumption, Statement & Conclusion, etc.

**Math Topics:**
- Probability, Permutation & Combination, Simple/Compound Interest
- Boats & Streams, Pipes & Cistern, Calendar, Clock, etc.

## 🔧 Troubleshooting

**Database connection error:**
```bash
# Verify DATABASE_URL in .env
# Format: postgresql://postgres:[password]@[host]/postgres
# Check Supabase project is active
```

**Module not found:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Port already in use:**
```python
# Edit main.py, last line:
uvicorn.run(app, host="0.0.0.0", port=8001)
```

**Import questions fails:**
```bash
# Check file path relative to project root
python scripts/import_questions.py data/questions_ready.json
```

## 🏗️ Design Decisions

- **Simple auth**: Single shared admin password (perfect for small groups)
- **In-memory sessions**: Fine for local/classroom use; resets on restart
- **Client-side timer**: JavaScript countdown, no websockets needed
- **Locked question sets**: Same questions for all participants in a quiz
- **Server-side rendering**: Jinja2 templates, no separate frontend build
- **No real-time updates**: Admin manually refreshes results page

## 📄 License

MIT - Free for personal/educational use

## 🤝 Contributing

This is a personal/educational project. Feel free to fork and customize for your needs!
