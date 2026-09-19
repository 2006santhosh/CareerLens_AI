import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app import models
from app.engines.gap_engine import run_gap_analysis
from app.engines.readiness_engine import compute_readiness
from app.engines.roadmap_engine import generate_roadmap
from app.engines.assessment_engine import submit_assessment, get_or_create_progress
from app.engines import level_band

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture()
def db():
    return TestingSessionLocal()


@pytest.fixture()
def basic_data(db):
    """A tiny 3-skill, 1-career dataset with a dependency chain: A -> B -> C."""
    a = models.Skill(name="Skill A", category="Cat", difficulty="Beginner")
    b = models.Skill(name="Skill B", category="Cat", difficulty="Intermediate")
    c = models.Skill(name="Skill C", category="Cat", difficulty="Advanced")
    db.add_all([a, b, c])
    db.flush()
    db.add(models.SkillDependency(skill_id=b.id, prerequisite_skill_id=a.id))
    db.add(models.SkillDependency(skill_id=c.id, prerequisite_skill_id=b.id))

    career = models.Career(name="Test Career", description="desc")
    db.add(career)
    db.flush()
    db.add(models.CareerSkill(career_id=career.id, skill_id=a.id, required_level=80, importance="High"))
    db.add(models.CareerSkill(career_id=career.id, skill_id=b.id, required_level=60, importance="Medium"))
    db.add(models.CareerSkill(career_id=career.id, skill_id=c.id, required_level=40, importance="Low"))
    db.commit()
    return {"a": a, "b": b, "c": c, "career": career}


@pytest.fixture()
def user(db):
    u = models.User(full_name="Test User", email="test@example.com", password_hash="x")
    db.add(u)
    db.flush()
    db.add(models.StudentProfile(user_id=u.id))
    db.commit()
    return u


# ---------------- Auth ----------------

def test_register_and_login():
    resp = client.post("/api/auth/register", json={
        "full_name": "Jane Doe", "email": "jane@example.com", "password": "supersecret",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()

    resp = client.post("/api/auth/login", json={"email": "jane@example.com", "password": "supersecret"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "jane@example.com"


def test_login_wrong_password_rejected():
    client.post("/api/auth/register", json={
        "full_name": "Bob", "email": "bob@example.com", "password": "correctpassword",
    })
    resp = client.post("/api/auth/login", json={"email": "bob@example.com", "password": "wrongpassword"})
    assert resp.status_code == 401


def test_protected_route_requires_token():
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


# ---------------- Skill level bands ----------------

@pytest.mark.parametrize("level,expected", [
    (0, "Beginner"), (20, "Beginner"), (21, "Basic"), (40, "Basic"),
    (41, "Developing"), (60, "Developing"), (61, "Proficient"), (80, "Proficient"),
    (81, "Advanced"), (100, "Advanced"),
])
def test_level_band_boundaries(level, expected):
    assert level_band(level) == expected


# ---------------- Gap engine ----------------

def test_gap_calculation_is_deterministic(db, basic_data, user):
    progress = models.StudentProgress(user_id=user.id, skill_id=basic_data["a"].id, level=30, status="self_reported")
    db.add(progress)
    db.commit()

    analysis = run_gap_analysis(db, user.id, basic_data["career"].id)
    gap_a = next(g for g in analysis["gaps"] if g["skill"].name == "Skill A")
    assert gap_a["gap"] == 80 - 30
    assert gap_a["current_level"] == 30

    # Skill with no progress at all has full gap
    gap_c = next(g for g in analysis["gaps"] if g["skill"].name == "Skill C")
    assert gap_c["gap"] == 40
    assert gap_c["current_level"] == 0


def test_gap_priority_reflects_dependency_and_importance(db, basic_data, user):
    analysis = run_gap_analysis(db, user.id, basic_data["career"].id)
    scores = {g["skill"].name: g["priority_score"] for g in analysis["gaps"]}
    # Skill A: High importance + unlocks B (dependency impact) + full gap -> should be the top priority
    assert scores["Skill A"] == max(scores.values())


def test_gap_coverage_capped_at_required_level(db, basic_data, user):
    # Over-achieving a skill should not push coverage above 100% for that skill
    progress = models.StudentProgress(user_id=user.id, skill_id=basic_data["a"].id, level=100, status="verified")
    db.add(progress)
    db.commit()
    analysis = run_gap_analysis(db, user.id, basic_data["career"].id)
    assert analysis["skill_coverage"] <= 100.0


# ---------------- Readiness engine ----------------

def test_readiness_is_zero_with_no_progress(db, basic_data, user):
    result = compute_readiness(db, user.id, basic_data["career"].id)
    assert result["overall_readiness"] == 0.0


def test_readiness_increases_with_progress(db, basic_data, user):
    before = compute_readiness(db, user.id, basic_data["career"].id)
    progress = models.StudentProgress(
        user_id=user.id, skill_id=basic_data["a"].id, level=80, status="verified",
        has_project_evidence=True, best_assessment_percent=90.0,
    )
    db.add(progress)
    db.commit()
    after = compute_readiness(db, user.id, basic_data["career"].id)
    assert after["overall_readiness"] > before["overall_readiness"]


# ---------------- Roadmap engine: dependency ordering ----------------

def test_roadmap_respects_prerequisite_order(db, basic_data, user):
    roadmap = generate_roadmap(db, user.id, basic_data["career"].id)
    order = [item.skill.name for item in roadmap.items]
    # A must come before B, B must come before C
    assert order.index("Skill A") < order.index("Skill B") < order.index("Skill C")


def test_roadmap_excludes_fully_met_skills(db, basic_data, user):
    # Fully satisfy Skill C; it should not appear in the roadmap
    progress = models.StudentProgress(user_id=user.id, skill_id=basic_data["c"].id, level=100, status="verified")
    db.add(progress)
    db.commit()
    roadmap = generate_roadmap(db, user.id, basic_data["career"].id)
    names = [item.skill.name for item in roadmap.items]
    assert "Skill C" not in names


# ---------------- Assessment scoring + adaptive roadmap ----------------

def test_assessment_scoring_updates_skill_level_and_status(db, basic_data, user):
    assessment = models.Assessment(skill_id=basic_data["a"].id, title="Skill A Test", type="MCQ")
    db.add(assessment)
    db.flush()
    q1 = models.AssessmentQuestion(assessment_id=assessment.id, prompt="Q1", options=["x", "y"], correct_index=0)
    q2 = models.AssessmentQuestion(assessment_id=assessment.id, prompt="Q2", options=["x", "y"], correct_index=1)
    db.add_all([q1, q2])
    db.commit()

    progress = get_or_create_progress(db, user.id, basic_data["a"].id)
    assert progress.level == 0

    result = submit_assessment(db, user.id, assessment, {q1.id: 0, q2.id: 1})  # both correct
    assert result["score"] == 2
    assert result["percent"] == 100.0
    assert result["updated_skill_level"] > result["previous_skill_level"]
    assert result["new_status"] in ("assessed", "verified")
