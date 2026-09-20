from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db
from ..engines.readiness_engine import compute_readiness
from ..engines.assessment_engine import get_or_create_progress
from .gap import _to_out as gap_to_out

router = APIRouter(prefix="/api/simulator", tags=["simulator"])


@router.post("/simulate", response_model=schemas.SimulatorResponse)
def simulate(
    payload: schemas.SimulatorRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    try:
        db.begin_nested() # Create a savepoint
        
        # Apply overrides
        for override in payload.overrides:
            progress = get_or_create_progress(db, current_user.id, override.skill_id)
            if override.level is not None:
                progress.level = override.level
            if override.status is not None:
                progress.status = override.status
            if override.has_project_evidence is not None:
                progress.has_project_evidence = override.has_project_evidence
            if override.has_github_evidence is not None:
                progress.has_github_evidence = override.has_github_evidence
            
        db.flush() # flush changes so they are picked up by the engines
        
        # Re-run readiness and gap analysis WITHOUT saving snapshot
        readiness_dict = compute_readiness(db, current_user.id, payload.career_id, save_snapshot=False)
        from ..engines.gap_engine import run_gap_analysis
        gap_dict = run_gap_analysis(db, current_user.id, payload.career_id)
        
        db.rollback() # Discard the savepoint (revert overrides)
        
        return schemas.SimulatorResponse(
            readiness=schemas.ReadinessOut(**readiness_dict),
            gap_analysis=gap_to_out(gap_dict)
        )
    except Exception as e:
        db.rollback()
        raise e
