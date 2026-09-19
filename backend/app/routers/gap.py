from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db
from ..engines.gap_engine import run_gap_analysis

router = APIRouter(prefix="/api/gap-analysis", tags=["gap-analysis"])


def _to_out(analysis: dict) -> schemas.GapAnalysisOut:
    return schemas.GapAnalysisOut(
        career=schemas.CareerOut.model_validate(analysis["career"]),
        skill_coverage=analysis["skill_coverage"],
        strong_skills=analysis["strong_skills"],
        partial_skills=analysis["partial_skills"],
        critical_gaps=analysis["critical_gaps"],
        total_required_skills=analysis["total_required_skills"],
        gaps=[
            schemas.GapItem(
                skill=schemas.SkillOut.model_validate(g["skill"]),
                required_level=g["required_level"],
                current_level=g["current_level"],
                gap=g["gap"],
                importance=g["importance"],
                priority_score=g["priority_score"],
                reason=g["reason"],
                is_prerequisite_for=g["is_prerequisite_for"],
            )
            for g in analysis["gaps"]
        ],
    )


@router.post("", response_model=schemas.GapAnalysisOut)
def analyze_current_target(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if not current_user.profile.target_career_id:
        raise HTTPException(status_code=400, detail="Select a target career first.")
    analysis = run_gap_analysis(db, current_user.id, current_user.profile.target_career_id)
    return _to_out(analysis)


@router.get("/{career_id}", response_model=schemas.GapAnalysisOut)
def analyze_career(career_id: str, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    try:
        analysis = run_gap_analysis(db, current_user.id, career_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Career not found")
    return _to_out(analysis)
