# CareerLens AI

**AI-driven personalized skill-gap identification & career readiness platform.**

CareerLens AI turns a student's existing evidence (resume, projects, GitHub, assessments) into an
explainable skill profile, compares it against a selected target career, prioritizes what to learn
next, generates a prerequisite-aware learning roadmap, verifies skills through assessments, and keeps
a career-readiness dashboard up to date as new evidence comes in.

This is a working end-to-end MVP, not a mockup: every button on the demo path is wired to a real
FastAPI backend and a real database, the skill-gap/roadmap/readiness math is deterministic and
explainable, and the whole loop (assessment → skill level update → roadmap regeneration → readiness
change) has been verified to work against the seeded demo account.

## 1. Problem statement

Students often know what career they want but not exactly which skills it requires, which of their
own skills are strong vs. weak, whether their claimed skills are actually verified, or what to learn
next and in what order.

## 2. Solution

An evidence-based skill intelligence platform with five deterministic engines (Gap, Roadmap,
Readiness, Assessment/Verification) wrapped around an AI service used only for resume understanding
and natural-language explanation — never for the underlying scoring.

## 3. Feature list

- Email/password auth (JWT, Argon2 password hashing), multi-step onboarding
- Resume upload (PDF/DOCX) with AI skill extraction (live LLM or deterministic demo fallback)
- Canonical skill ontology: 76 skills across 13 categories with a prerequisite dependency graph
- Career catalog: 8 curated careers with weighted required skills (importance + target level)
- Skill Gap Engine: deterministic `Gap = max(0, Required − Current)` plus a weighted, normalized
  priority score (importance × dependency impact × evidence-confidence adjustment) with a plain-English
  explanation for every skill
- Personalized Roadmap Engine: topological sort over the skill dependency graph, phase-by-phase
  "why / what to learn / what to build / how to prove it", regenerated automatically after new evidence
- Assessment engine: MCQ assessments (6 assessments, 39 questions) that update skill level and
  verification status, and trigger roadmap regeneration
- Proof-of-Skill state machine: `self_reported → evidence_found → assessed → verified`
- Career Readiness Engine: transparent 5-factor weighted score with an explanation for each factor
- Progress analytics (readiness trend, category distribution, verified vs. unverified, assessment
  scores) via Recharts
- Optional GitHub public-repo analysis and free-text job-description matching
- Aggregate ("Placement Insights") analytics with no individual student data exposed
- Full pytest suite for the deterministic engines (21 tests, all passing)

## 4. Technology stack

**Frontend:** React + TypeScript + Vite + Tailwind CSS v4, React Router, Recharts, Lucide icons.
**Backend:** Python, FastAPI, Pydantic, SQLAlchemy 2.x, PyMuPDF (PDF), python-docx (DOCX), JWT + Argon2.
**Database:** SQLite by default (zero-setup, portable); PostgreSQL via Docker Compose for a
production-shaped deployment. Schema is Postgres-safe (no SQLite-only types).
**AI:** Provider-agnostic `AIService` abstraction. Live mode calls the Anthropic Messages API
(structured-JSON prompting, Pydantic-style validation of the response); demo mode uses deterministic
keyword/skill matching so the whole product works with zero external dependencies.

## 5. Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md).

## 6. Folder structure

```
careerlens-ai/
├── backend/
│   ├── app/
│   │   ├── main.py, config.py, database.py, models.py, schemas.py, auth.py, ai_service.py
│   │   ├── engines/        # gap, roadmap, readiness, assessment scoring — all deterministic
│   │   ├── routers/        # auth, profile, skills, careers, evidence, gap, roadmap, assessments, dashboard
│   │   └── seed.py         # skills, careers, dependencies, resources, assessments, demo student
│   ├── tests/test_core.py  # pytest suite (auth + all four engines)
│   ├── requirements.txt, Dockerfile, .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/          # Login, Register, Onboarding, Dashboard, Profile, Skills, Careers, ...
│   │   ├── components/     # AppShell (sidebar/topbar), Gauge, States, SkillBits
│   │   ├── context/        # AuthContext
│   │   └── lib/api.ts      # typed fetch client
│   ├── Dockerfile, nginx.conf
├── docker-compose.yml
├── ARCHITECTURE.md, API.md, AI_METHODOLOGY.md, DATABASE.md, DEMO_GUIDE.md
```

## 7. Setup (local development, no Docker required)

### Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env         # defaults to SQLite + demo AI mode — works with no further config
python -m app.seed           # seeds skills/careers/assessments + demo student
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev                  # http://localhost:5173, proxies /api to http://localhost:8000
```

## 8. Environment variables

See `backend/.env.example`:

| Variable | Purpose | Default |
|---|---|---|
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./careerlens.db` |
| `JWT_SECRET` | JWT signing secret | dev placeholder — **change in production** |
| `AI_MODE` | `demo` or `live` | `demo` |
| `AI_API_KEY` | Anthropic API key, only used when `AI_MODE=live` | empty |
| `AI_MODEL` | model id for live mode | `claude-sonnet-4-6` |
| `GITHUB_TOKEN` | optional, raises GitHub API rate limits | empty |
| `UPLOAD_DIR` | where uploaded resumes are stored | `./uploads` |

## 9. Database setup & 10. Seed data

`python -m app.seed` creates all tables (via SQLAlchemy `create_all`, no separate migration step needed
for the MVP) and populates: 76 skills, 48 dependencies, 8 careers with 89 career-skill requirements,
22 learning resources, 6 assessments (39 questions), and one fully-populated demo student. Re-running
seed is a no-op once data exists — delete the DB file (or the Postgres volume) to reseed from scratch.

## 11. Running locally

Run the backend and frontend commands above in two terminals. Health check: `GET /api/health`.

## 12. Docker setup

```bash
cp backend/.env.example backend/.env
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Postgres: localhost:5432 (user/pass/db: `careerlens`)

The backend container runs `python -m app.seed` on startup before serving, against Postgres.

## 13. AI setup

Defaults to `AI_MODE=demo` — fully functional with **zero external API calls**, using deterministic
keyword-matching extraction. To enable live AI resume extraction, set `AI_MODE=live` and `AI_API_KEY`
in `backend/.env`. If the live call fails for any reason (bad key, network, malformed response), the
service automatically falls back to demo mode for that request — the product never hard-fails because
of AI availability.

## 14. Demo account

```
Email:    demo.student@careerlens.ai
Password: DemoPass123!
```

Pre-loaded with a realistic DevOps Engineer skill profile (see [DEMO_GUIDE.md](DEMO_GUIDE.md) for the
exact walkthrough).

## 15. API overview

See [API.md](API.md) for the full endpoint list.

## 16. Testing

```bash
cd backend
pytest tests/ -v
```

21 tests covering auth, skill-level bands, gap calculation (including dependency/importance-weighted
priority and coverage capping), readiness scoring, roadmap prerequisite ordering, and assessment
scoring / verification-status transitions. All passing as of this build.

## 17. Deployment

The `docker-compose.yml` is production-shaped (separate Postgres, backend, and nginx-served frontend
containers) but for a real deployment you should: set a strong `JWT_SECRET`, put the backend behind
HTTPS, restrict CORS origins in `backend/app/main.py`, and run the frontend build behind a CDN.

## 18. Known limitations

- The skill/career dataset is curated but intentionally scoped down from the "15 careers / 100+
  skills" ideal to keep the demo stable (8 careers, 76 skills) — the data model supports growing this
  freely.
- MCQ assessments only exist for 6 of the 76 skills (Docker, Linux, Python, AWS, CI/CD, SQL); other
  skills can still gain levels via resume/project/GitHub evidence, just not via a quiz yet.
- The frontend's `lucide-react` version doesn't ship a "GitHub" brand icon; a generic `GitBranch` icon
  is used instead.
- No Alembic migration history is included — schema changes are applied via `create_all`, which is
  fine for a hackathon MVP but should move to real migrations before production use.
- GitHub integration and job-description matching are best-effort/optional features, as specified.

## 19. Future improvements

- Expand the skill/career/assessment dataset toward the full 100+/15/all-skills target
- Replace `create_all` with Alembic migrations
- Add pgvector-based embedding similarity for semantic (not just exact-match) skill extraction
- Add coding/scenario assessment types beyond MCQ
- Add an interactive skill dependency graph visualization (currently text/list based)
- Split the frontend production bundle (currently a single ~700KB chunk) via route-based code-splitting
