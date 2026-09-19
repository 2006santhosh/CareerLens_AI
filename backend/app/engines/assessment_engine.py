"""
Assessment scoring engine + Proof-of-Skill state machine.

Scoring is 100% deterministic (multiple choice correctness). The resulting
score updates the canonical StudentProgress.level using a transparent
blend of the previous level and the new demonstrated performance, then
advances the skill's verification status:

    self_reported -> evidence_found -> assessed -> verified
"""
from sqlalchemy.orm import Session

from .. import models


def get_or_create_progress(db: Session, user_id: str, skill_id: str) -> models.StudentProgress:
    progress = (
        db.query(models.StudentProgress)
        .filter(models.StudentProgress.user_id == user_id, models.StudentProgress.skill_id == skill_id)
        .first()
    )
    if not progress:
        progress = models.StudentProgress(user_id=user_id, skill_id=skill_id, level=0, status="self_reported")
        db.add(progress)
        db.flush()
    return progress


def advance_status(progress: models.StudentProgress) -> None:
    """Recompute verification status from accumulated evidence signals."""
    has_any_evidence = (
        progress.has_resume_evidence or progress.has_project_evidence
        or progress.has_github_evidence or progress.has_certification
    )
    has_strong_assessment = (progress.best_assessment_percent or 0) >= 70

    if has_strong_assessment and has_any_evidence:
        progress.status = "verified"
    elif progress.best_assessment_percent is not None:
        progress.status = "assessed"
    elif has_any_evidence:
        progress.status = "evidence_found"
    else:
        progress.status = "self_reported"


def submit_assessment(db: Session, user_id: str, assessment: models.Assessment, answers: dict[str, int]) -> dict:
    questions = assessment.questions
    total = len(questions)
    correct_map = {}
    score = 0
    for q in questions:
        correct_map[q.id] = q.correct_index
        if answers.get(q.id) == q.correct_index:
            score += 1

    percent = round((score / total) * 100, 1) if total else 0.0

    progress = get_or_create_progress(db, user_id, assessment.skill_id)
    previous_level = progress.level

    # Blend: new level leans toward demonstrated performance but doesn't
    # discard prior evidence-based level entirely.
    demonstrated_level = round(percent)
    updated_level = round(previous_level * 0.35 + demonstrated_level * 0.65)
    updated_level = max(previous_level, updated_level) if percent >= 50 else max(previous_level - 5, min(previous_level, updated_level))
    updated_level = max(0, min(100, updated_level))

    progress.level = updated_level
    progress.best_assessment_percent = max(percent, progress.best_assessment_percent or 0)
    advance_status(progress)

    attempt = models.AssessmentAttempt(
        user_id=user_id,
        assessment_id=assessment.id,
        score=score,
        total=total,
        percent=percent,
        previous_skill_level=previous_level,
        updated_skill_level=updated_level,
    )
    db.add(attempt)
    db.commit()
    db.refresh(progress)

    return {
        "score": score,
        "total": total,
        "percent": percent,
        "previous_skill_level": previous_level,
        "updated_skill_level": updated_level,
        "new_status": progress.status,
        "correct_answers": correct_map,
    }
