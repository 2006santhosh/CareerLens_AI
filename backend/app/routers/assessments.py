from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db
from ..engines.assessment_engine import submit_assessment, get_or_create_progress
from ..engines.roadmap_engine import generate_roadmap, get_active_roadmap

router = APIRouter(prefix="/api/assessments", tags=["assessments"])


@router.get("", response_model=list[schemas.AssessmentListItem])
def list_assessments(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    assessments = db.query(models.Assessment).all()
    result = []
    for a in assessments:
        skill = db.query(models.Skill).filter(models.Skill.id == a.skill_id).first()
        attempts = (
            db.query(models.AssessmentAttempt)
            .filter(models.AssessmentAttempt.assessment_id == a.id, models.AssessmentAttempt.user_id == current_user.id)
            .all()
        )
        best = max((att.percent for att in attempts), default=None)
        result.append(
            schemas.AssessmentListItem(
                id=a.id, skill=schemas.SkillOut.model_validate(skill), title=a.title, type=a.type,
                question_count=len(a.questions), best_percent=best, attempts=len(attempts),
            )
        )
    return result


@router.get("/{assessment_id}", response_model=schemas.AssessmentOut)
def get_assessment(assessment_id: str, db: Session = Depends(get_db)):
    a = db.query(models.Assessment).filter(models.Assessment.id == assessment_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Assessment not found")
    skill = db.query(models.Skill).filter(models.Skill.id == a.skill_id).first()
    return schemas.AssessmentOut(
        id=a.id, skill=schemas.SkillOut.model_validate(skill), title=a.title, description=a.description,
        type=a.type, questions=[schemas.AssessmentQuestionOut.model_validate(q) for q in a.questions],
    )


@router.post("/{assessment_id}/submit", response_model=schemas.AssessmentResultOut)
def submit(
    assessment_id: str,
    payload: schemas.AssessmentSubmitRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    assessment = db.query(models.Assessment).filter(models.Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    result = submit_assessment(db, current_user.id, assessment, payload.answers)

    # Adaptive roadmap: regenerate if the user has an active roadmap for their target career
    roadmap_updated = False
    target_career_id = current_user.profile.target_career_id
    if target_career_id:
        existing = get_active_roadmap(db, current_user.id, target_career_id)
        if existing:
            skill = db.query(models.Skill).filter(models.Skill.id == assessment.skill_id).first()
            generate_roadmap(
                db, current_user.id, target_career_id,
                reason=f"Roadmap updated based on your {skill.name} assessment "
                       f"(level {result['previous_skill_level']} -> {result['updated_skill_level']}).",
            )
            roadmap_updated = True

    return schemas.AssessmentResultOut(**result, roadmap_updated=roadmap_updated)
