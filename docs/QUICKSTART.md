# Quick Start Guide

## First Time Setup

1. **Create your environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your database credentials:**
   ```bash
   nano .env  # or use any text editor
   ```
   
   Required fields:
   - `DATABASE_URL`: Your Supabase PostgreSQL connection string
   - `ADMIN_PASSWORD`: Choose a secure password for admin access
   - `SECRET_KEY`: Any random string (used for session security)

3. **Run the setup script:**
   ```bash
   ./setup.sh
   ```
   
   This will:
   - Create a Python virtual environment
   - Install all dependencies
   - Initialize the database tables
   - Import 8 sample questions

## Running the App

```bash
./run.sh
```

Or manually:
```bash
source venv/bin/activate
python main.py
```

Visit: **http://localhost:8000**

## Testing the Complete Flow

### As Admin:

1. Go to `http://localhost:8000/admin/login`
2. Enter your admin password (from `.env`)
3. Create a quiz:
   - Title: "Sample Quiz"
   - Time: 10 minutes
   - Marks: +1 for correct, -0.25 for wrong
   - Check "Show explanations"
   - Select 2-3 questions from each topic using sliders
   - Click "Create Quiz"
4. Copy the share link from the results page

### As Participant:

1. Open the share link in a different browser/incognito window
2. Enter your name (e.g., "Test User")
3. Take the quiz
4. Watch the timer countdown
5. Submit and view your score with explanations

### Back as Admin:

1. Go back to admin dashboard
2. Click "View Results" on the quiz you created
3. See the participant's score, time taken, and submission timestamp

## Troubleshooting

**Database connection error:**
- Verify your `DATABASE_URL` in `.env` is correct
- Check that your Supabase project is active
- Format: `postgresql://postgres:[password]@[host]/postgres`

**Module not found:**
- Make sure virtual environment is activated: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

**Port already in use:**
- Change the port in `main.py` (last line): `uvicorn.run(app, host="0.0.0.0", port=8001)`

## Next Steps

- Add more questions by creating JSON files and importing them
- Customize the scraper to pull questions from IndiaBix
- Share quiz links with friends/classmates
- Monitor results from the admin dashboard
