import json
from sqlalchemy.orm import Session
from ..models import PracticalAssessment, PracticalSubmission, StudentProgress, Roadmap, RoadmapItem
from ..engines.roadmap_engine import generate_roadmap

def grade_docker_containerize(files: dict[str, str]) -> tuple[float, list[dict[str, str]]]:
    feedback = []
    score = 0.0
    total_checks = 5
    
    dockerfile = files.get("Dockerfile", "")
    
    # Check 1: Dockerfile exists
    if dockerfile:
        feedback.append({"check": "Dockerfile exists", "status": "pass"})
        score += 1
    else:
        feedback.append({"check": "Dockerfile exists", "status": "fail"})
        return 0.0, feedback
        
    # Check 2: FROM instruction
    if "FROM" in dockerfile:
        feedback.append({"check": "Base image configured (FROM)", "status": "pass"})
        score += 1
    else:
        feedback.append({"check": "Base image configured (FROM)", "status": "fail"})
        
    # Check 3: COPY instruction
    if "COPY" in dockerfile or "ADD" in dockerfile:
        feedback.append({"check": "Application files copied", "status": "pass"})
        score += 1
    else:
        feedback.append({"check": "Application files copied", "status": "fail"})
        
    # Check 4: Port exposed
    if "EXPOSE" in dockerfile:
        feedback.append({"check": "Port exposed", "status": "pass"})
        score += 1
    else:
        feedback.append({"check": "Port exposed", "status": "fail"})
        
    # Check 5: CMD or ENTRYPOINT
    if "CMD" in dockerfile or "ENTRYPOINT" in dockerfile:
        feedback.append({"check": "Startup command configured", "status": "pass"})
        score += 1
    else:
        feedback.append({"check": "Startup command configured", "status": "fail"})
        
    return (score / total_checks) * 100.0, feedback

def submit_practical_assessment(
    db: Session,
    user_id: str,
    assessment: PracticalAssessment,
    files: dict[str, str]
) -> tuple[PracticalSubmission, bool]:
    
    if assessment.validation_type == "docker_containerize":
        score, feedback = grade_docker_containerize(files)
    else:
        score, feedback = 0.0, [{"check": "Unknown validation type", "status": "fail"}]
        
    passed = score >= 80.0
    
    progress = db.query(StudentProgress).filter_by(
        user_id=user_id, skill_id=assessment.skill_id
    ).first()
    
    if not progress:
        progress = StudentProgress(user_id=user_id, skill_id=assessment.skill_id)
        db.add(progress)
        
    previous_level = progress.level
    updated_level = previous_level
    
    # Boost skill level
    if passed:
        # Boost based on previous level, simulating practical proof
        boost = max(10, min(100 - previous_level, int(score / 5)))
        updated_level = min(100, previous_level + boost)
        progress.has_practical_evidence = True
        if progress.best_practical_score is None or score > progress.best_practical_score:
            progress.best_practical_score = score
            
        progress.level = updated_level
        progress.status = "verified" # Advance to verified!
        
    submission = PracticalSubmission(
        user_id=user_id,
        assessment_id=assessment.id,
        score=score,
        passed=passed,
        feedback=json.dumps(feedback),
        previous_skill_level=previous_level,
        updated_skill_level=updated_level
    )
    db.add(submission)
    db.commit()
    
    # Check roadmap update
    roadmap_updated = False
    if passed:
        active_roadmap = db.query(Roadmap).filter_by(user_id=user_id, is_active=True).first()
        if active_roadmap:
            generate_roadmap(
                db, 
                user_id, 
                active_roadmap.career_id, 
                generated_reason=f"Updated because you verified your {assessment.skill.name} skill with a practical assessment."
            )
            roadmap_updated = True
            
    return submission, roadmap_updated
