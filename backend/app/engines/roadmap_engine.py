"""
Personalized Roadmap Engine.

Builds an ordered, prerequisite-aware learning path from the current gap
analysis. Ordering is deterministic (topological sort over skill
dependencies, tie-broken by gap priority). The LLM (via ai_service) is only
used to phrase the human-readable "why / what to build" text - never to
decide sequencing.
"""
from sqlalchemy.orm import Session

from .. import models
from .gap_engine import run_gap_analysis

WEEKLY_HOURS_MAP = {
    "1-3": 2, "3-5": 4, "5-10": 7, "10+": 12,
}


def _topological_order(db: Session, skill_ids: list[str], priority_lookup: dict[str, float]) -> list[str]:
    deps = db.query(models.SkillDependency).filter(models.SkillDependency.skill_id.in_(skill_ids)).all()
    prereq_map: dict[str, set[str]] = {sid: set() for sid in skill_ids}
    for d in deps:
        if d.prerequisite_skill_id in skill_ids:
            prereq_map[d.skill_id].add(d.prerequisite_skill_id)

    ordered = []
    remaining = set(skill_ids)
    while remaining:
        # skills whose prerequisites (within this gap set) are already ordered
        ready = [sid for sid in remaining if prereq_map[sid].issubset(set(ordered))]
        if not ready:
            # cycle guard - just take whatever remains sorted by priority
            ready = list(remaining)
        ready.sort(key=lambda sid: priority_lookup.get(sid, 0), reverse=True)
        chosen = ready[0]
        ordered.append(chosen)
        remaining.discard(chosen)
    return ordered


def _pick_resources(db: Session, skill_id: str) -> list[models.LearningResource]:
    return db.query(models.LearningResource).filter(models.LearningResource.skill_id == skill_id).limit(2).all()


def generate_roadmap(db: Session, user_id: str, career_id: str, reason: str = "Initial roadmap") -> models.Roadmap:
    analysis = run_gap_analysis(db, user_id, career_id)
    gap_items = [g for g in analysis["gaps"] if g["gap"] > 0]

    skill_ids = [g["skill"].id for g in gap_items]
    priority_lookup = {g["skill"].id: g["priority_score"] for g in gap_items}
    ordered_ids = _topological_order(db, skill_ids, priority_lookup) if skill_ids else []

    gap_by_skill = {g["skill"].id: g for g in gap_items}

    # deactivate old roadmap(s) for this career
    db.query(models.Roadmap).filter(
        models.Roadmap.user_id == user_id,
        models.Roadmap.career_id == career_id,
        models.Roadmap.is_active == True,  # noqa: E712
    ).update({"is_active": False})

    prev_version = (
        db.query(models.Roadmap)
        .filter(models.Roadmap.user_id == user_id, models.Roadmap.career_id == career_id)
        .order_by(models.Roadmap.version.desc())
        .first()
    )
    version = (prev_version.version + 1) if prev_version else 1

    roadmap = models.Roadmap(
        user_id=user_id, career_id=career_id, is_active=True, version=version, generated_reason=reason
    )
    db.add(roadmap)
    db.flush()

    for seq, skill_id in enumerate(ordered_ids, start=1):
        gap = gap_by_skill[skill_id]
        skill = gap["skill"]
        resources = _pick_resources(db, skill_id)
        resource_titles = ", ".join(r.title for r in resources) if resources else "curated practice material"
        hours = max(3, round(gap["gap"] / 100 * 20))

        item = models.RoadmapItem(
            roadmap_id=roadmap.id,
            skill_id=skill_id,
            sequence=seq,
            phase_label=f"Phase {seq}",
            why=gap["reason"],
            what_to_learn=f"{skill.name} — target level {gap['required_level']}, "
                           f"currently at {gap['current_level']}.",
            what_to_build=f"A small project applying {skill.name} "
                           f"(see: {resource_titles}).",
            how_to_prove=f"Complete the {skill.name} assessment and attach a project "
                          f"as evidence to move this skill to Verified.",
            estimated_hours=hours,
            status="pending",
        )
        db.add(item)

    db.commit()
    db.refresh(roadmap)
    return roadmap


def get_active_roadmap(db: Session, user_id: str, career_id: str) -> models.Roadmap | None:
    return (
        db.query(models.Roadmap)
        .filter(
            models.Roadmap.user_id == user_id,
            models.Roadmap.career_id == career_id,
            models.Roadmap.is_active == True,  # noqa: E712
        )
        .first()
    )


def roadmap_progress_percent(roadmap: models.Roadmap) -> float:
    if not roadmap.items:
        return 0.0
    completed = sum(1 for i in roadmap.items if i.status == "completed")
    return round((completed / len(roadmap.items)) * 100, 1)
