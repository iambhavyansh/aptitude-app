#!/bin/bash

echo "=== Aptitude Quiz Platform Setup ==="
echo ""

# Navigate to project root
cd "$(dirname "$0")/.."

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  No .env file found!"
    echo "Please create .env from .env.example and configure your DATABASE_URL"
    echo ""
    echo "Run: cp .env.example .env"
    echo "Then edit .env with your Supabase connection string"
    exit 1
fi

# Initialize database
echo ""
echo "Initializing database..."
python scripts/init_db.py

# Import questions
echo ""
echo "Importing questions..."
if [ -f "data/questions_ready.json" ]; then
    echo "Found scraped questions (740 questions)..."
    python scripts/import_questions.py data/questions_ready.json
else
    echo "Using sample questions (8 questions)..."
    python scripts/import_questions.py data/sample_questions.json
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the application:"
echo "  ./scripts/run.sh"
echo ""
echo "Then visit: http://localhost:8000"
