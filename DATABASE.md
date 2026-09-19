# Database

SQLite by default (`sqlite:///./careerlens.db`), PostgreSQL in Docker Compose. The schema is written
to be Postgres-safe (string UUIDs, no SQLite-only types) so switching `DATABASE_URL` is the only
change needed. Tables are created via SQLAlchemy `Base.metadata.create_all()` — see "Known
limitations" in the README regarding migrations.

## Core tables

| Table | Purpose |
|---|---|
| `users` | Account + academic info |
| `student_profiles` | 1:1 with users — target career, weekly hours, learning style, GitHub username |
| `skills` | Canonical skill ontology (name, category, description, difficulty) |
| `skill_aliases` | Synonym mapping (e.g. "Postgres" → "PostgreSQL") |
| `skill_dependencies` | Directed prerequisite edges (`skill_id` requires `prerequisite_skill_id`) |
| `careers` | Career catalog (name, description, responsibilities) |
| `career_skills` | Per-career required skill + target level + importance (High/Medium/Low) |
| `evidence` | One row per resume upload / manual project / GitHub analysis / certification |
| `evidence_skills` | Many-to-many: which skills a piece of evidence supports, with confidence |
| `learning_resources` | Curated resources per skill (title, type, hours, url) |
| `roadmaps` | Versioned, one-active-at-a-time roadmap per (user, career) |
| `roadmap_items` | Ordered phases within a roadmap, with status (pending/in_progress/completed) |
| `assessments` | MCQ assessment per skill |
| `assessment_questions` | Questions + options + correct index (never sent to the client) |
| `assessment_attempts` | Every submission, with before/after skill level |
| `student_progress` | **The canonical per-user-per-skill record**: level, verification status, evidence flags |
| `readiness_snapshots` | Time series of readiness scores, powers the Analytics trend chart |

## Key relationships

- `student_progress` is the single source of truth for "how good is this student at this skill right
  now" — every engine (gap, roadmap, readiness) reads from it, and every evidence-producing action
  (resume upload, manual evidence, GitHub analysis, assessment submission) writes to it.
- `skill_dependencies` forms a DAG used by the roadmap engine's topological sort and by the gap
  engine's "dependency impact" multiplier.
- `roadmaps` are versioned rather than mutated in place: generating a new roadmap deactivates the old
  one (`is_active=False`) and inserts a new `version`, so history is preserved.

## Indexes

Foreign-key columns used in hot-path queries (`user_id`, `skill_id`, `career_id`, `assessment_id`,
`roadmap_id`, `evidence_id`) are indexed. `users.email` has a unique index for login lookups.
`(career_id, skill_id)` on `career_skills` and `(user_id, skill_id)` on `student_progress` are unique
constraints to prevent duplicate rows.
