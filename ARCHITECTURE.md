# Architecture

## High-level shape

```
React (Vite/TS/Tailwind)
   │  fetch("/api/...")
   ▼
FastAPI (modular monolith)
   ├── auth            — register/login/me (JWT + Argon2)
   ├── profile         — onboarding + profile CRUD
   ├── skills          — canonical skill catalog + per-user skill profile
   ├── careers         — career catalog + detail + match %
   ├── evidence        — resume upload, manual evidence, GitHub, job-description matching
   ├── gap             — POST /gap-analysis, GET /gap-analysis/{career_id}
   ├── roadmap         — generate / current / item status
   ├── assessments     — list / detail / submit
   ├── dashboard       — dashboard, readiness, analytics, placement (aggregate)
   └── engines/        — gap_engine, roadmap_engine, readiness_engine, assessment_engine (all deterministic)
   └── ai_service.py   — the ONLY place that talks to an LLM (live) or the demo fallback
   ▼
SQLAlchemy ORM ──► SQLite (dev) / PostgreSQL (docker-compose)
```

This is intentionally a **modular monolith**, per the project brief: no microservices, no message
queue, no separate ML-serving process. Everything the deterministic engines need lives in the same
process and the same transaction as the request that triggered it, so state (skill level → gap →
roadmap → readiness → dashboard) never drifts out of sync.

## Why a modular monolith and not microservices

- A hackathon-scale team cannot operate multiple deployables reliably in the time available.
- The core value proposition (explainable, deterministic gap/roadmap/readiness calculations) benefits
  from being able to reason about all inputs in one transaction — splitting it into services would
  just add network calls and eventual-consistency bugs for no product benefit.
- The AI service is already isolated behind one module (`ai_service.py`), so if a real system later
  needed to move it out-of-process (e.g. because of GPU / rate-limit isolation), that's a one-file
  change, not a rewrite.

## Request flow: the core adaptive loop

1. `POST /api/assessments/{id}/submit` → `assessment_engine.submit_assessment()`
   - Deterministically scores the MCQ answers
   - Blends the new demonstrated score into `StudentProgress.level`
   - Advances `StudentProgress.status` through the verification state machine
   - Commits to the database
2. The same request checks whether the user has an **active roadmap** for their target career. If so,
   it calls `roadmap_engine.generate_roadmap()` again with an explanatory `generated_reason`, which:
   - Re-runs the gap analysis (now reflecting the updated skill level)
   - Re-does the topological sort over remaining gaps
   - Deactivates the old roadmap version and inserts a new one (versioned, not overwritten)
3. The frontend's `AssessmentResult.roadmap_updated` flag drives the "Your roadmap has been updated
   based on your latest assessment" banner.
4. The next time the dashboard, gap-analysis, or roadmap pages are loaded, they read the **current
   database state** — nothing is cached client-side beyond a single page's fetch, so a page refresh
   always reflects the latest evidence.

## Engines are pure functions over the database, not the LLM

Every scoring decision (`Gap`, `Priority`, `Readiness`, assessment → skill level, roadmap ordering) is
implemented in `backend/app/engines/*.py` using plain arithmetic and graph traversal — no LLM call is
on the critical path for any of these. The LLM (via `ai_service.py`) is only used for:

- Resume/skill extraction from unstructured text (`extract_resume`)
- Nothing else — even `explain_gap()` is a Python string template, not an LLM call, so gap
  explanations are instant and 100% reproducible in demo mode.

This split is what the project brief calls "DATA + DETERMINISTIC LOGIC + AI, not AI → everything."

## Frontend architecture

```
React
 ├── pages/            one file per route, each owns its own data fetching (no global cache layer
 │                      — a deliberate simplification; see README "Known limitations")
 ├── components/
 │    ├── AppShell.tsx  sidebar + topbar shell, ProtectedRoute / RequireAuthOnly guards
 │    ├── Gauge.tsx      radial readiness gauge (SVG)
 │    ├── States.tsx     Loading / Error / Empty state primitives, reused everywhere
 │    └── SkillBits.tsx  level-band badge, verification-status badge, importance tag
 ├── context/AuthContext.tsx   holds the current user, login/register/logout, token in localStorage
 └── lib/api.ts          typed fetch wrapper (adds bearer token, handles 401 → redirect to /login,
                          surfaces backend error `detail` messages)
```

## Design system

A distinct "instrument panel" visual identity (deep ink-navy sidebar, warm paper content area, amber
accent for progress/signal, teal for verified/success, coral reserved for critical gaps), with a
serif display face (Fraunces) for headings and a monospace face (IBM Plex Mono) for the numeric
skill-level and percentage data — chosen because the product's whole value proposition is
measurement/instrumentation of skill readiness, not a generic dashboard.
