from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db
from ..engines import level_band

router = APIRouter(prefix="/api/skills", tags=["skills"])


@router.get("", response_model=list[schemas.SkillOut])
def list_skills(category: str | None = None, db: Session = Depends(get_db)):
    q = db.query(models.Skill)
    if category:
        q = q.filter(models.Skill.category == category)
    return q.order_by(models.Skill.category, models.Skill.name).all()


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    rows = db.query(models.Skill.category).distinct().all()
    return sorted({r[0] for r in rows})


@router.get("/profile", response_model=list[schemas.SkillProfileItem])
def skill_profile(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    rows = (
        db.query(models.StudentProgress, models.Skill)
        .join(models.Skill, models.Skill.id == models.StudentProgress.skill_id)
        .filter(models.StudentProgress.user_id == current_user.id)
        .order_by(models.StudentProgress.level.desc())
        .all()
    )
    result = []
    for progress, skill in rows:
        latest_ev = (
            db.query(models.EvidenceSkill)
            .join(models.Evidence, models.Evidence.id == models.EvidenceSkill.evidence_id)
            .filter(models.Evidence.user_id == current_user.id, models.EvidenceSkill.skill_id == skill.id)
            .order_by(models.Evidence.created_at.desc())
            .first()
        )
        result.append(
            schemas.SkillProfileItem(
                skill=schemas.SkillOut.model_validate(skill),
                level=progress.level,
                status=progress.status,
                band=level_band(progress.level),
                has_resume_evidence=progress.has_resume_evidence,
                has_project_evidence=progress.has_project_evidence,
                has_github_evidence=progress.has_github_evidence,
                has_certification=progress.has_certification,
                best_assessment_percent=progress.best_assessment_percent,
                has_practical_evidence=getattr(progress, 'has_practical_evidence', False),
                best_practical_score=getattr(progress, 'best_practical_score', None),
                latest_evidence_excerpt=latest_ev.excerpt if latest_ev else None,
            )
        )
    return result


@router.get("/{skill_id}", response_model=schemas.SkillOut)
def get_skill(skill_id: str, db: Session = Depends(get_db)):
    return db.query(models.Skill).filter(models.Skill.id == skill_id).first()


@router.get("/{skill_id}/dependencies")
def get_skill_dependencies(skill_id: str, db: Session = Depends(get_db)):
    prereqs = (
        db.query(models.Skill)
        .join(models.SkillDependency, models.SkillDependency.prerequisite_skill_id == models.Skill.id)
        .filter(models.SkillDependency.skill_id == skill_id)
        .all()
    )
    dependents = (
        db.query(models.Skill)
        .join(models.SkillDependency, models.SkillDependency.skill_id == models.Skill.id)
        .filter(models.SkillDependency.prerequisite_skill_id == skill_id)
        .all()
    )
    return {
        "prerequisites": [schemas.SkillOut.model_validate(s) for s in prereqs],
        "unlocks": [schemas.SkillOut.model_validate(s) for s in dependents],
    }
