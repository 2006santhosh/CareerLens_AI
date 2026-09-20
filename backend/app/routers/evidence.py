import json
import os
import re
import uuid

import fitz  # PyMuPDF
import httpx
from docx import Document as DocxDocument
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..config import settings
from ..database import get_db
from ..ai_service import ai_service
from ..engines.assessment_engine import get_or_create_progress, advance_status

router = APIRouter(prefix="/api", tags=["evidence"])


# ---------------- helpers ----------------

def _extract_text_from_pdf(path: str) -> str:
    doc = fitz.open(path)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text


def _extract_text_from_docx(path: str) -> str:
    doc = DocxDocument(path)
    return "\n".join(p.text for p in doc.paragraphs)


def _canonical_skill_names(db: Session) -> list[str]:
    return [s.name for s in db.query(models.Skill.name).all()] if False else [s[0] for s in db.query(models.Skill.name).all()]


def _skill_by_name(db: Session, name: str) -> models.Skill | None:
    skill = db.query(models.Skill).filter(models.Skill.name.ilike(name)).first()
    if skill:
        return skill
    alias = db.query(models.SkillAlias).filter(models.SkillAlias.alias.ilike(name)).first()
    if alias:
        return db.query(models.Skill).filter(models.Skill.id == alias.skill_id).first()
    return None


def _apply_extraction(db: Session, user_id: str, extraction: dict, evidence: models.Evidence) -> None:
    for item in extraction.get("skills", []):
        skill = _skill_by_name(db, item.get("name", ""))
        if not skill:
            continue
        confidence = float(item.get("confidence", 0.6))
        db.add(models.EvidenceSkill(evidence_id=evidence.id, skill_id=skill.id, confidence=confidence,
                                     excerpt=item.get("evidence", "")))
        progress = get_or_create_progress(db, user_id, skill.id)
        # Confidence-weighted baseline level bump from resume evidence
        candidate_level = round(40 + confidence * 40)  # 40-80 range
        progress.level = max(progress.level, candidate_level)
        progress.has_resume_evidence = True
        advance_status(progress)


# ---------------- resume upload ----------------

@router.post("/resumes/upload", response_model=schemas.ResumeAnalysisOut)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in (".pdf", ".docx"):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX resumes are supported.")

    contents = await file.read()
    if len(contents) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File exceeds {settings.max_upload_mb}MB limit.")

    safe_name = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(settings.upload_dir, safe_name)
    with open(path, "wb") as f:
        f.write(contents)

    try:
        text = _extract_text_from_pdf(path) if ext == ".pdf" else _extract_text_from_docx(path)
    except Exception:
        raise HTTPException(status_code=422, detail="Could not parse this file. Please try another file or "
                                                      "add your skills manually on the Skills page.")

    if not text.strip():
        raise HTTPException(status_code=422, detail="No readable text found in this file. "
                                                      "Please add your skills manually instead.")

    canonical_names = [s[0] for s in db.query(models.Skill.name).all()]
    aliases = [a[0] for a in db.query(models.SkillAlias.alias).all()]
    extraction = ai_service.extract_resume(text, canonical_names, aliases)

    evidence = models.Evidence(
        user_id=current_user.id,
        type="resume",
        title=f"Resume: {file.filename}",
        description="Parsed resume evidence.",
        source_filename=file.filename,
        raw_extracted_json=json.dumps(extraction),
    )
    db.add(evidence)
    db.flush()

    _apply_extraction(db, current_user.id, extraction, evidence)

    current_user.profile.resume_filename = file.filename
    db.commit()

    return schemas.ResumeAnalysisOut(
        filename=file.filename,
        ai_mode=extraction.get("ai_mode", "demo"),
        extracted_skills=[schemas.ExtractedSkill(**s) for s in extraction.get("skills", [])],
        projects=extraction.get("projects", []),
        certifications=extraction.get("certifications", []),
        education=extraction.get("education", []),
        message=f"Extracted {len(extraction.get('skills', []))} skills from your resume "
                f"({'live AI' if extraction.get('ai_mode') == 'live' else 'demo AI'} mode).",
    )


# ---------------- manual evidence ----------------

@router.get("/evidence", response_model=list[schemas.EvidenceOut])
def list_evidence(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(models.Evidence)
        .filter(models.Evidence.user_id == current_user.id)
        .order_by(models.Evidence.created_at.desc())
        .all()
    )


@router.post("/evidence", response_model=schemas.EvidenceOut)
def create_evidence(
    payload: schemas.EvidenceCreateRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    evidence = models.Evidence(
        user_id=current_user.id, type=payload.type, title=payload.title, description=payload.description
    )
    db.add(evidence)
    db.flush()

    for name in payload.skill_names:
        skill = _skill_by_name(db, name)
        if not skill:
            continue
        db.add(models.EvidenceSkill(evidence_id=evidence.id, skill_id=skill.id, confidence=0.8))
        progress = get_or_create_progress(db, current_user.id, skill.id)
        if payload.type == "project":
            progress.has_project_evidence = True
            progress.level = max(progress.level, 45)
        elif payload.type == "certification":
            progress.has_certification = True
            progress.level = max(progress.level, 55)
        elif payload.type == "github":
            progress.has_github_evidence = True
            progress.level = max(progress.level, 35)
        advance_status(progress)

    db.commit()
    db.refresh(evidence)
    return evidence


@router.delete("/evidence/{evidence_id}")
def delete_evidence(
    evidence_id: str, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)
):
    evidence = (
        db.query(models.Evidence)
        .filter(models.Evidence.id == evidence_id, models.Evidence.user_id == current_user.id)
        .first()
    )
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    db.query(models.EvidenceSkill).filter(models.EvidenceSkill.evidence_id == evidence_id).delete()
    db.delete(evidence)
    db.commit()
    return {"deleted": True}


# ---------------- GitHub (optional, best-effort) ----------------

@router.post("/github/analyze")
async def analyze_github(username: str, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    try:
        headers = {"Authorization": f"token {settings.github_token}"} if settings.github_token else {}
        headers["Accept"] = "application/vnd.github.v3+json"
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(f"https://api.github.com/users/{username}/repos?per_page=5&sort=updated", headers=headers)
            if resp.status_code != 200:
                raise HTTPException(status_code=502, detail="GitHub is unavailable right now. You can add project evidence manually instead.")
            repos = resp.json()
            
            skill_evidence: dict[str, list[str]] = {}
            
            for repo in repos:
                repo_name = repo["name"]
                owner = repo["owner"]["login"]
                
                # Check languages/topics
                lang = repo.get("language")
                if lang:
                    skill_evidence.setdefault(lang, []).append(f"Primary language '{lang}' in repository {repo_name}.")
                for topic in (repo.get("topics", []) or []):
                    skill_evidence.setdefault(topic, []).append(f"Topic '{topic}' tagged in repository {repo_name}.")
                    
                # Check root contents
                contents_resp = await client.get(f"https://api.github.com/repos/{owner}/{repo_name}/contents", headers=headers)
                if contents_resp.status_code == 200:
                    contents = contents_resp.json()
                    if isinstance(contents, list):
                        file_names = {item["name"].lower() for item in contents if item["type"] == "file"}
                        dir_names = {item["name"].lower() for item in contents if item["type"] == "dir"}
                        
                        if "dockerfile" in file_names or "docker-compose.yml" in file_names:
                            skill_evidence.setdefault("Docker", []).append(f"Detected Dockerfile/docker-compose.yml in repository {repo_name}.")
                        if ".github" in dir_names:
                            skill_evidence.setdefault("CI/CD", []).append(f"Detected .github workflows in repository {repo_name}.")
                        if "package.json" in file_names:
                            skill_evidence.setdefault("JavaScript", []).append(f"Detected package.json in repository {repo_name}.")
                            skill_evidence.setdefault("Node.js", []).append(f"Detected package.json in repository {repo_name}.")
                        if "requirements.txt" in file_names or "pyproject.toml" in file_names:
                            skill_evidence.setdefault("Python", []).append(f"Detected Python dependencies in repository {repo_name}.")
                            
                            # For MVP: best-effort content fetch for requirements.txt
                            if "requirements.txt" in file_names:
                                req_url = next((i["download_url"] for i in contents if i["name"].lower() == "requirements.txt"), None)
                                if req_url:
                                    req_resp = await client.get(req_url)
                                    if req_resp.status_code == 200:
                                        req_text = req_resp.text.lower()
                                        if "fastapi" in req_text:
                                            skill_evidence.setdefault("FastAPI", []).append(f"Detected FastAPI dependency in {repo_name}/requirements.txt.")
                                        if "django" in req_text:
                                            skill_evidence.setdefault("Django", []).append(f"Detected Django dependency in {repo_name}/requirements.txt.")
                                        if "flask" in req_text:
                                            skill_evidence.setdefault("Flask", []).append(f"Detected Flask dependency in {repo_name}/requirements.txt.")
                                        if "pandas" in req_text:
                                            skill_evidence.setdefault("Pandas", []).append(f"Detected Pandas in {repo_name}/requirements.txt.")

    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="GitHub is unavailable right now. You can add project evidence manually instead.")

    canonical_names = [s[0] for s in db.query(models.Skill.name).all()]
    matched = []
    
    evidence = models.Evidence(
        user_id=current_user.id, type="github", title=f"GitHub: {username}",
        description=f"Public repository analysis (supporting evidence only).",
    )
    db.add(evidence)
    db.flush()
    
    for raw_skill, reasons in skill_evidence.items():
        # find matching canonical skill
        matched_canonical = next((n for n in canonical_names if n.lower() == raw_skill.lower()), None)
        if not matched_canonical:
            continue
            
        if matched_canonical not in matched:
            matched.append(matched_canonical)
            
        skill = _skill_by_name(db, matched_canonical)
        if not skill:
            continue
            
        # Combine reasons
        combined_reasons = " ".join(set(reasons))
        db.add(models.EvidenceSkill(evidence_id=evidence.id, skill_id=skill.id, confidence=0.6, excerpt=combined_reasons))
        
        progress = get_or_create_progress(db, current_user.id, skill.id)
        progress.has_github_evidence = True
        progress.level = max(progress.level, 30)
        advance_status(progress)

    current_user.profile.github_username = username
    db.commit()

    return {"username": username, "repos_analyzed": len(repos), "matched_skills": matched}


# ---------------- job description matching ----------------

@router.post("/job-description/analyze", response_model=schemas.JobDescriptionMatchOut)
def analyze_job_description(
    payload: schemas.JobDescriptionRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    canonical_names = [s[0] for s in db.query(models.Skill.name).all()]
    aliases = [a[0] for a in db.query(models.SkillAlias.alias).all()]
    extracted = ai_service.extract_job_description(payload.text, canonical_names, aliases)
    
    required_raw = extracted.get("skills", [])
    
    # Map to canonical names
    required = []
    for r in required_raw:
        skill = _skill_by_name(db, r)
        if skill and skill.name not in required:
            required.append(skill.name)

    if not required:
        raise HTTPException(status_code=422, detail="Could not detect any known skills in this text.")

    # Create a custom career for this JD
    custom_title = extracted.get("title", "Custom Job Match")
    career = models.Career(name=f"{custom_title} ({current_user.id[:8]})", description="Dynamically generated from job description.", responsibilities="N/A")
    db.add(career)
    db.flush()
    
    skill_map = {s.name: s.id for s in db.query(models.Skill).filter(models.Skill.name.in_(required)).all()}
    
    for name in required:
        sid = skill_map.get(name)
        if sid:
            db.add(models.CareerSkill(career_id=career.id, skill_id=sid, required_level=70, importance="High", is_required=True))

    db.commit()

    progress = {
        p.skill_id: p.level
        for p in db.query(models.StudentProgress).filter(models.StudentProgress.user_id == current_user.id).all()
    }

    matched, missing = [], []
    for name in required:
        sid = skill_map.get(name)
        level = progress.get(sid, 0) if sid else 0
        (matched if level >= 40 else missing).append(name)

    match_percent = round((len(matched) / len(required)) * 100, 1) if required else 0.0
    return schemas.JobDescriptionMatchOut(match_percent=match_percent, matched_skills=matched, missing_skills=missing, career_id=career.id)
