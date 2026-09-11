# Project Summary

## What's Been Built

A complete, functional quiz platform with:

### Backend (FastAPI + PostgreSQL)
- **Database Models**: Topics, Questions, Quizzes, Attempts
- **Admin Authentication**: Simple password-based session management
- **Quiz Logic**: Random question selection, locked question sets, scoring with negative marking
- **Timer Logic**: Client-side countdown with auto-submit

### Frontend (Jinja2 Templates + Vanilla JS)
- **Admin Interface**: Login, dashboard, quiz creation form, results view
- **Participant Interface**: Quiz landing page, taking interface with timer, results display
- **Responsive Design**: Clean, minimal CSS that works across devices

### Key Features Implemented
✅ Single admin password authentication (no user accounts)
✅ Topic-based question selection with sliders
✅ Configurable time limits and marking schemes
✅ Locked random question sets (same questions for all participants)
✅ Individual participant sessions with independent timers
✅ Auto-submit on time expiry
✅ Optional explanations toggle
✅ Results dashboard showing all participant scores
✅ Shareable quiz links

## File Breakdown

**Core Application:**
- `main.py` - FastAPI app with all routes (admin + participant flows)
- `models.py` - SQLAlchemy database models
- `database.py` - Database connection setup
- `config.py` - Environment variable loading

**Database Setup:**
- `init_db.py` - Creates all tables
- `import_questions.py` - Imports questions from JSON
- `sample_questions.json` - 8 sample questions across 4 topics

**Scraper (Template):**
- `scraper.py` - Placeholder for IndiaBix scraping (needs customization)

**Templates (9 HTML files):**
- `base.html` - Base layout with CSS
- `home.html` - Landing page
- `admin_login.html` - Admin login form
- `admin_dashboard.html` - Quiz creation + quiz list
- `quiz_results.html` - Admin results view (participants + share link)
- `quiz_start.html` - Participant landing (enter name)
- `take_quiz.html` - Quiz taking interface with timer
- `quiz_result.html` - Individual result with explanations

**Scripts:**
- `setup.sh` - One-command setup (venv + deps + db + sample data)
- `run.sh` - Start the application
- `.env.example` - Environment template

**Documentation:**
- `README.md` - Full project documentation
- `QUICKSTART.md` - Step-by-step getting started guide

## How to Use (Summary)

1. **Setup:**
   ```bash
   cp .env.example .env
   # Edit .env with your DATABASE_URL and ADMIN_PASSWORD
   ./setup.sh
   ```

2. **Run:**
   ```bash
   ./run.sh
   # Visit http://localhost:8000
   ```

3. **Admin Flow:**
   - Login at `/admin/login`
   - Create quiz with topic sliders
   - Get shareable link from results page

4. **Participant Flow:**
   - Open shared link
   - Enter name → starts timer
   - Take quiz → auto-submits on timeout
   - View score (+ explanations if enabled)

## What You Need to Provide

1. **Supabase Database:**
   - Create a free Supabase project
   - Copy the PostgreSQL connection string
   - Add it to `.env` as `DATABASE_URL`

2. **Choose Admin Password:**
   - Set `ADMIN_PASSWORD` in `.env`

That's it! Everything else is ready to go.

## Design Decisions Made

1. **Simple auth over OAuth**: One shared admin password keeps it lightweight for small groups
2. **In-memory sessions**: Fine for personal/classroom use; resets on server restart
3. **Client-side timer**: JavaScript countdown, no websockets needed
4. **Locked question sets**: Random selection happens once at quiz creation, not per-attempt
5. **Server-side rendering**: Jinja2 templates, no separate frontend build step
6. **No real-time updates**: Admin manually refreshes results page

## Adding More Questions

Either:
- Create JSON files matching the sample format and import them
- Customize `scraper.py` to pull from IndiaBix (requires inspecting their HTML structure)
- Manually add via SQL (not recommended)

## Testing Checklist

Before sharing with others, test:
- [ ] Create quiz as admin
- [ ] Take quiz as participant (different browser/incognito)
- [ ] Verify timer auto-submits
- [ ] Check scoring math (correct + wrong + unanswered)
- [ ] Verify explanations toggle works
- [ ] Check results page shows participant data
- [ ] Test negative marking calculation

## Known Limitations

- Sessions stored in memory (lost on restart)
- No user accounts or persistent login
- No question editing UI (must edit DB directly or re-import)
- No pagination on results (fine for small groups)
- Timer uses client time (can be manipulated, but this is for practice, not exams)

## Future Ideas (Not Implemented)

- Export results to CSV/Excel
- Question bank management UI
- Practice mode (no timer, immediate feedback)
- Analytics/charts
- Mobile app
- Multi-language support
