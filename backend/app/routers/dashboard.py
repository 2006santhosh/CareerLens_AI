from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..config import settings
from ..database import get_db
from ..engines.gap_engine import run_gap_analysis
from ..engines.readiness_engine import compute_readiness
from ..engines.roadmap_engine import get_active_roadmap, roadmap_progress_percent
from ..engines import level_band

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/readiness", response_model=schemas.ReadinessOut)
def readiness(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if not current_user.profile.target_career_id:
        raise HTTPException(status_code=400, detail="Select a target career first.")
    result = compute_readiness(db, current_user.id, current_user.profile.target_career_id)
    return schemas.ReadinessOut(**result)


@router.get("/dashboard", response_model=schemas.DashboardOut)
def dashboard(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    career = None
    readiness_out = None
    top_gaps = []
    roadmap_progress = 0.0
    roadmap_weeks = []
    next_action = "Complete your onboarding and select a target career to get started."

    profile = current_user.profile
    total_profile_skills = db.query(models.StudentProgress).filter(models.StudentProgress.user_id == current_user.id).count()
    verified_count = (
        db.query(models.StudentProgress)
        .filter(models.StudentProgress.user_id == current_user.id, models.StudentProgress.status == "verified")
        .count()
    )

    if profile.target_career_id:
        career = db.query(models.Career).filter(models.Career.id == profile.target_career_id).first()
        readiness_result = compute_readiness(db, current_user.id, profile.target_career_id)
        readiness_out = schemas.ReadinessOut(**readiness_result)

        analysis = run_gap_analysis(db, current_user.id, profile.target_career_id)
        top_gaps = [
            schemas.GapItem(
                skill=schemas.SkillOut.model_validate(g["skill"]), required_level=g["required_level"],
                current_level=g["current_level"], gap=g["gap"], importance=g["importance"],
                priority_score=g["priority_score"], reason=g["reason"], is_prerequisite_for=g["is_prerequisite_for"],
            )
            for g in analysis["gaps"][:4] if g["gap"] > 0
        ]

        roadmap = get_active_roadmap(db, current_user.id, profile.target_career_id)
        if roadmap:
            roadmap_progress = roadmap_progress_percent(roadmap)
            next_pending = next((i for i in roadmap.items if i.status != "completed"), None)
            if next_pending:
                next_action = f"Complete: {next_pending.skill.name} — {next_pending.what_to_learn}"
            else:
                next_action = "You've completed every item in your roadmap! Generate a refreshed one for new goals."

            items_per_week = 1
            for idx, item in enumerate(roadmap.items):
                week_num = (idx // items_per_week) + 1
                roadmap_weeks.append({
                    "week": week_num,
                    "skill": item.skill.name,
                    "status": item.status,
                })
        else:
            next_action = f"Run a skill gap analysis for {career.name}, then generate your personalized roadmap."

    return schemas.DashboardOut(
        full_name=current_user.full_name,
        target_career=schemas.CareerOut.model_validate(career) if career else None,
        readiness=readiness_out,
        verified_skills_count=verified_count,
        total_profile_skills=total_profile_skills,
        roadmap_progress_percent=roadmap_progress,
        top_gaps=top_gaps,
        next_best_action=next_action,
        roadmap_weeks=roadmap_weeks,
        ai_mode=settings.ai_mode,
    )


@router.get("/analytics/progress", response_model=schemas.AnalyticsOut)
def analytics_progress(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    snapshots = (
        db.query(models.ReadinessSnapshot)
        .filter(models.ReadinessSnapshot.user_id == current_user.id)
        .order_by(models.ReadinessSnapshot.created_at)
        .all()
    )
    readiness_trend = [
        schemas.ProgressPoint(date=s.created_at.strftime("%Y-%m-%d %H:%M"), overall_readiness=s.overall_readiness)
        for s in snapshots
    ]

    progress_rows = (
        db.query(models.StudentProgress, models.Skill)
        .join(models.Skill, models.Skill.id == models.StudentProgress.skill_id)
        .filter(models.StudentProgress.user_id == current_user.id)
        .all()
    )
    by_category: dict[str, list[int]] = {}
    verified, unverified = 0, 0
    for progress, skill in progress_rows:
        by_category.setdefault(skill.category, []).append(progress.level)
        if progress.status == "verified":
            verified += 1
        else:
            unverified += 1

    category_distribution = [
        schemas.CategoryBreakdown(category=cat, average_level=round(sum(levels) / len(levels)), skill_count=len(levels))
        for cat, levels in sorted(by_category.items())
    ]

    attempts = (
        db.query(models.AssessmentAttempt, models.Assessment, models.Skill)
        .join(models.Assessment, models.Assessment.id == models.AssessmentAttempt.assessment_id)
        .join(models.Skill, models.Skill.id == models.Assessment.skill_id)
        .filter(models.AssessmentAttempt.user_id == current_user.id)
        .order_by(models.AssessmentAttempt.created_at)
        .all()
    )
    assessment_scores = [
        {"skill": skill.name, "percent": att.percent, "date": att.created_at.strftime("%Y-%m-%d")}
        for att, assessment, skill in attempts
    ]

    top_remaining_gaps = []
    if current_user.profile.target_career_id:
        analysis = run_gap_analysis(db, current_user.id, current_user.profile.target_career_id)
        top_remaining_gaps = [g["skill"].name for g in analysis["gaps"] if g["gap"] > 0][:5]

    return schemas.AnalyticsOut(
        readiness_trend=readiness_trend,
        category_distribution=category_distribution,
        verified_vs_unverified={"verified": verified, "unverified": unverified},
        assessment_scores=assessment_scores,
        top_remaining_gaps=top_remaining_gaps,
    )


@router.get("/placement/analytics")
def placement_analytics(db: Session = Depends(get_db)):
    """Aggregate, anonymized demo analytics (no individual student data exposed)."""
    rows = (
        db.query(models.Skill.name, models.StudentProgress.level)
        .join(models.StudentProgress, models.StudentProgress.skill_id == models.Skill.id)
        .all()
    )
    gap_counter: dict[str, int] = {}
    for name, level in rows:
        if level < 50:
            gap_counter[name] = gap_counter.get(name, 0) + 1
    common_gaps = sorted(gap_counter.items(), key=lambda kv: kv[1], reverse=True)[:5]
    return {
        "note": "Aggregate demo analytics only. No individual student data is exposed.",
        "most_common_skill_gaps": [{"skill": name, "students_affected": count} for name, count in common_gaps],
        "total_students": db.query(models.User).count(),
    }
