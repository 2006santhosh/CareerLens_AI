from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db
from ..engines.assessment_engine import get_or_create_progress, advance_status

router = APIRouter(prefix="/api", tags=["profile"])


def _skill_by_name(db: Session, name: str) -> models.Skill | None:
    skill = db.query(models.Skill).filter(models.Skill.name.ilike(name)).first()
    if skill:
        return skill
    alias = db.query(models.SkillAlias).filter(models.SkillAlias.alias.ilike(name)).first()
    if alias:
        return db.query(models.Skill).filter(models.Skill.id == alias.skill_id).first()
    return None


@router.post("/onboarding", response_model=schemas.ProfileOut)
def complete_onboarding(
    payload: schemas.OnboardingRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    career = db.query(models.Career).filter(models.Career.id == payload.target_career_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="Selected career not found.")

    current_user.college = payload.college or current_user.college
    current_user.degree = payload.degree or current_user.degree
    current_user.department = payload.department or current_user.department
    current_user.graduation_year = payload.graduation_year or current_user.graduation_year
    current_user.onboarding_complete = True

    profile = current_user.profile
    profile.target_career_id = payload.target_career_id
    profile.weekly_hours = payload.weekly_hours
    profile.preferred_learning_style = payload.preferred_learning_style
    profile.career_interests = ",".join(payload.career_interests)

    for entry in payload.current_skills:
        name = entry.get("name")
        level = int(entry.get("level", 0))
        skill = _skill_by_name(db, name) if name else None
        if not skill:
            continue
        progress = get_or_create_progress(db, current_user.id, skill.id)
        progress.level = max(progress.level, level)
        advance_status(progress)

    db.commit()
    db.refresh(profile)

    return schemas.ProfileOut(
        user=schemas.UserOut.model_validate(current_user),
        target_career_id=career.id,
        target_career_name=career.name,
        weekly_hours=profile.weekly_hours,
        preferred_learning_style=profile.preferred_learning_style,
        career_interests=profile.career_interests,
        github_username=profile.github_username,
    )


@router.get("/profile", response_model=schemas.ProfileOut)
def get_profile(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    profile = current_user.profile
    career = db.query(models.Career).filter(models.Career.id == profile.target_career_id).first() if profile.target_career_id else None
    return schemas.ProfileOut(
        user=schemas.UserOut.model_validate(current_user),
        target_career_id=career.id if career else None,
        target_career_name=career.name if career else None,
        weekly_hours=profile.weekly_hours,
        preferred_learning_style=profile.preferred_learning_style,
        career_interests=profile.career_interests,
        github_username=profile.github_username,
    )


@router.put("/profile", response_model=schemas.ProfileOut)
def update_profile(
    payload: schemas.ProfileUpdateRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    profile = current_user.profile
    if payload.weekly_hours is not None:
        profile.weekly_hours = payload.weekly_hours
    if payload.preferred_learning_style is not None:
        profile.preferred_learning_style = payload.preferred_learning_style
    if payload.career_interests is not None:
        profile.career_interests = ",".join(payload.career_interests)
    if payload.target_career_id is not None:
        career_exists = db.query(models.Career).filter(models.Career.id == payload.target_career_id).first()
        if not career_exists:
            raise HTTPException(status_code=404, detail="Career not found.")
        profile.target_career_id = payload.target_career_id
    if payload.github_username is not None:
        profile.github_username = payload.github_username

    db.commit()
    db.refresh(profile)
    career = db.query(models.Career).filter(models.Career.id == profile.target_career_id).first() if profile.target_career_id else None
    return schemas.ProfileOut(
        user=schemas.UserOut.model_validate(current_user),
        target_career_id=career.id if career else None,
        target_career_name=career.name if career else None,
        weekly_hours=profile.weekly_hours,
        preferred_learning_style=profile.preferred_learning_style,
        career_interests=profile.career_interests,
        github_username=profile.github_username,
    )
