"""
Skill Gap Engine.

Fully deterministic. The LLM is never used to compute a gap score -
it is only used (via ai_service.explain_gap, which is itself template-based
and does not call an LLM) to phrase an explanation.

Priority = Gap x CareerImportanceWeight x DependencyImpact x EvidenceConfidenceAdjustment
The result is normalized to a 0-100 scale across the current gap set so
priorities are comparable within one gap analysis run.
"""
from sqlalchemy.orm import Session

from .. import models
from . import IMPORTANCE_WEIGHT
from ..ai_service import ai_service


def evidence_confidence_adjustment(progress: models.StudentProgress | None) -> float:
    """Skills backed by verified evidence get a *lower* multiplier (less urgent to
    re-prove); purely self-reported or absent skills get full weight."""
    if progress is None:
        return 1.0
    if progress.status == "verified":
        return 0.6
    if progress.status == "assessed":
        return 0.8
    if progress.status == "evidence_found":
        return 0.9
    return 1.0


def dependency_impact(db: Session, skill_id: str) -> tuple[float, list[str]]:
    """A skill that unlocks many downstream skills gets a higher impact multiplier."""
    dependents = (
        db.query(models.SkillDependency, models.Skill)
        .join(models.Skill, models.Skill.id == models.SkillDependency.skill_id)
        .filter(models.SkillDependency.prerequisite_skill_id == skill_id)
        .all()
    )
    names = [skill.name for _, skill in dependents]
    impact = 1.0 + 0.25 * min(len(names), 4)
    return impact, names


def run_gap_analysis(db: Session, user_id: str, career_id: str) -> dict:
    career = db.query(models.Career).filter(models.Career.id == career_id).first()
    if not career:
        raise ValueError("Career not found")

    career_skills = (
        db.query(models.CareerSkill, models.Skill)
        .join(models.Skill, models.Skill.id == models.CareerSkill.skill_id)
        .filter(models.CareerSkill.career_id == career_id)
        .all()
    )

    progress_rows = {
        p.skill_id: p
        for p in db.query(models.StudentProgress).filter(models.StudentProgress.user_id == user_id).all()
    }

    raw_items = []
    strong, partial, gaps_count = 0, 0, 0
    coverage_sum = 0.0

    for cs, skill in career_skills:
        progress = progress_rows.get(skill.id)
        current_level = progress.level if progress else 0
        gap = max(0, cs.required_level - current_level)
        coverage_sum += min(current_level, cs.required_level) / cs.required_level if cs.required_level else 1.0

        if gap == 0:
            strong += 1
        elif current_level > 0:
            partial += 1
        else:
            gaps_count += 1

        impact, dependents = dependency_impact(db, skill.id)
        adj = evidence_confidence_adjustment(progress)
        importance_weight = IMPORTANCE_WEIGHT.get(cs.importance, 1.0)
        priority_score = gap * importance_weight * impact * adj

        reason = ai_service.explain_gap(skill.name, cs.required_level, current_level, cs.importance, dependents)

        raw_items.append({
            "skill": skill,
            "required_level": cs.required_level,
            "current_level": current_level,
            "gap": gap,
            "importance": cs.importance,
            "priority_score": priority_score,
            "reason": reason,
            "is_prerequisite_for": dependents,
        })

    max_priority = max((i["priority_score"] for i in raw_items), default=0) or 1
    for item in raw_items:
        item["priority_score"] = round(min(100.0, (item["priority_score"] / max_priority) * 100), 1)

    raw_items.sort(key=lambda i: i["priority_score"], reverse=True)

    total_required = len(career_skills)
    skill_coverage = round((coverage_sum / total_required) * 100, 1) if total_required else 0.0

    return {
        "career": career,
        "skill_coverage": skill_coverage,
        "strong_skills": strong,
        "partial_skills": partial,
        "critical_gaps": gaps_count,
        "total_required_skills": total_required,
        "gaps": raw_items,
    }
