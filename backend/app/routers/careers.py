from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/api/careers", tags=["careers"])


def _match_percent(db: Session, user_id: str, career_id: str) -> float:
    career_skills = (
        db.query(models.CareerSkill).filter(models.CareerSkill.career_id == career_id).all()
    )
    if not career_skills:
        return 0.0
    progress = {
        p.skill_id: p.level
        for p in db.query(models.StudentProgress).filter(models.StudentProgress.user_id == user_id).all()
    }
    total, covered = 0.0, 0.0
    for cs in career_skills:
        total += cs.required_level
        covered += min(progress.get(cs.skill_id, 0), cs.required_level)
    return round((covered / total) * 100, 1) if total else 0.0


@router.get("", response_model=list[schemas.CareerOut])
def list_careers(db: Session = Depends(get_db)):
    return db.query(models.Career).order_by(models.Career.name).all()


@router.get("/{career_id}", response_model=schemas.CareerDetailOut)
def get_career(
    career_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    career = db.query(models.Career).filter(models.Career.id == career_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career not found")

    rows = (
        db.query(models.CareerSkill, models.Skill)
        .join(models.Skill, models.Skill.id == models.CareerSkill.skill_id)
        .filter(models.CareerSkill.career_id == career_id)
        .order_by(models.CareerSkill.importance.desc(), models.CareerSkill.required_level.desc())
        .all()
    )
    skills_out = [
        schemas.CareerSkillOut(
            skill=schemas.SkillOut.model_validate(skill),
            required_level=cs.required_level,
            importance=cs.importance,
            is_required=cs.is_required,
        )
        for cs, skill in rows
    ]

    return schemas.CareerDetailOut(
        id=career.id,
        name=career.name,
        description=career.description,
        responsibilities=career.responsibilities,
        skills=skills_out,
        match_percent=_match_percent(db, current_user.id, career_id),
    )
