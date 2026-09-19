from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db
from ..engines.roadmap_engine import generate_roadmap, get_active_roadmap, roadmap_progress_percent

router = APIRouter(prefix="/api/roadmaps", tags=["roadmaps"])


def _to_out(roadmap: models.Roadmap, db: Session) -> schemas.RoadmapOut:
    career = db.query(models.Career).filter(models.Career.id == roadmap.career_id).first()
    return schemas.RoadmapOut(
        id=roadmap.id,
        career=schemas.CareerOut.model_validate(career),
        version=roadmap.version,
        generated_reason=roadmap.generated_reason,
        items=[schemas.RoadmapItemOut.model_validate(i) for i in roadmap.items],
        progress_percent=roadmap_progress_percent(roadmap),
    )


@router.post("/generate", response_model=schemas.RoadmapOut)
def generate(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if not current_user.profile.target_career_id:
        raise HTTPException(status_code=400, detail="Select a target career first.")
    roadmap = generate_roadmap(db, current_user.id, current_user.profile.target_career_id,
                                reason="Generated from your current skill gap analysis.")
    return _to_out(roadmap, db)


@router.get("/current", response_model=schemas.RoadmapOut)
def current(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if not current_user.profile.target_career_id:
        raise HTTPException(status_code=400, detail="Select a target career first.")
    roadmap = get_active_roadmap(db, current_user.id, current_user.profile.target_career_id)
    if not roadmap:
        raise HTTPException(status_code=404, detail="No roadmap yet. Generate one first.")
    return _to_out(roadmap, db)


@router.patch("/items/{item_id}", response_model=schemas.RoadmapItemOut)
def update_item_status(
    item_id: str,
    payload: schemas.RoadmapItemStatusUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    item = (
        db.query(models.RoadmapItem)
        .join(models.Roadmap, models.Roadmap.id == models.RoadmapItem.roadmap_id)
        .filter(models.RoadmapItem.id == item_id, models.Roadmap.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Roadmap item not found")
    if payload.status not in ("pending", "in_progress", "completed"):
        raise HTTPException(status_code=400, detail="Invalid status")
    item.status = payload.status
    db.commit()
    db.refresh(item)
    return item
