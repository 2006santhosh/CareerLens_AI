import uuid
from datetime import datetime
from sqlalchemy import (
    String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


def gen_id() -> str:
    return uuid.uuid4().hex


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    full_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    college: Mapped[str] = mapped_column(String(255), nullable=True)
    degree: Mapped[str] = mapped_column(String(255), nullable=True)
    department: Mapped[str] = mapped_column(String(255), nullable=True)
    graduation_year: Mapped[int] = mapped_column(Integer, nullable=True)
    onboarding_complete: Mapped[bool] = mapped_column(Boolean, default=False)

    profile: Mapped["StudentProfile"] = relationship(back_populates="user", uselist=False)


class StudentProfile(Base, TimestampMixin):
    __tablename__ = "student_profiles"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), unique=True, index=True)
    target_career_id: Mapped[str] = mapped_column(String(36), ForeignKey("careers.id"), nullable=True)
    weekly_hours: Mapped[str] = mapped_column(String(50), nullable=True)  # e.g. "5-10"
    preferred_learning_style: Mapped[str] = mapped_column(String(50), nullable=True)
    career_interests: Mapped[str] = mapped_column(Text, nullable=True)  # comma separated
    github_username: Mapped[str] = mapped_column(String(255), nullable=True)
    resume_filename: Mapped[str] = mapped_column(String(255), nullable=True)

    user: Mapped["User"] = relationship(back_populates="profile")
    target_career: Mapped["Career"] = relationship()


class Skill(Base, TimestampMixin):
    __tablename__ = "skills"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    name: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str] = mapped_column(String(30), default="Intermediate")  # Beginner/Intermediate/Advanced


class SkillAlias(Base):
    __tablename__ = "skill_aliases"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    skill_id: Mapped[str] = mapped_column(String(36), ForeignKey("skills.id"), index=True)
    alias: Mapped[str] = mapped_column(String(150), index=True)


class SkillDependency(Base):
    __tablename__ = "skill_dependencies"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    skill_id: Mapped[str] = mapped_column(String(36), ForeignKey("skills.id"), index=True)
    prerequisite_skill_id: Mapped[str] = mapped_column(String(36), ForeignKey("skills.id"), index=True)


class Career(Base, TimestampMixin):
    __tablename__ = "careers"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    name: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text)
    responsibilities: Mapped[str] = mapped_column(Text, nullable=True)  # newline separated


class CareerSkill(Base):
    __tablename__ = "career_skills"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    career_id: Mapped[str] = mapped_column(String(36), ForeignKey("careers.id"), index=True)
    skill_id: Mapped[str] = mapped_column(String(36), ForeignKey("skills.id"), index=True)
    required_level: Mapped[int] = mapped_column(Integer)  # 0-100 target proficiency
    importance: Mapped[str] = mapped_column(String(20), default="Medium")  # High/Medium/Low
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)  # required vs recommended
    __table_args__ = (UniqueConstraint("career_id", "skill_id", name="uq_career_skill"),)


class Evidence(Base, TimestampMixin):
    __tablename__ = "evidence"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    type: Mapped[str] = mapped_column(String(30))  # resume/project/github/certification/assessment/self_reported
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    source_filename: Mapped[str] = mapped_column(String(255), nullable=True)
    raw_extracted_json: Mapped[str] = mapped_column(Text, nullable=True)


class EvidenceSkill(Base):
    __tablename__ = "evidence_skills"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    evidence_id: Mapped[str] = mapped_column(String(36), ForeignKey("evidence.id"), index=True)
    skill_id: Mapped[str] = mapped_column(String(36), ForeignKey("skills.id"), index=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.7)
    excerpt: Mapped[str] = mapped_column(Text, nullable=True)


class LearningResource(Base):
    __tablename__ = "learning_resources"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    skill_id: Mapped[str] = mapped_column(String(36), ForeignKey("skills.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(String(30))  # Course/Documentation/Video/Tutorial/Practice/Project
    difficulty: Mapped[str] = mapped_column(String(30), default="Intermediate")
    estimated_hours: Mapped[int] = mapped_column(Integer, default=4)
    url: Mapped[str] = mapped_column(String(500), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)


class Roadmap(Base, TimestampMixin):
    __tablename__ = "roadmaps"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    career_id: Mapped[str] = mapped_column(String(36), ForeignKey("careers.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    generated_reason: Mapped[str] = mapped_column(Text, nullable=True)

    items: Mapped[list["RoadmapItem"]] = relationship(back_populates="roadmap", order_by="RoadmapItem.sequence")


class RoadmapItem(Base, TimestampMixin):
    __tablename__ = "roadmap_items"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    roadmap_id: Mapped[str] = mapped_column(String(36), ForeignKey("roadmaps.id"), index=True)
    skill_id: Mapped[str] = mapped_column(String(36), ForeignKey("skills.id"))
    sequence: Mapped[int] = mapped_column(Integer)
    phase_label: Mapped[str] = mapped_column(String(50))  # "Phase 1"
    why: Mapped[str] = mapped_column(Text)
    what_to_learn: Mapped[str] = mapped_column(Text)
    what_to_build: Mapped[str] = mapped_column(Text)
    how_to_prove: Mapped[str] = mapped_column(Text)
    estimated_hours: Mapped[int] = mapped_column(Integer, default=6)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending/in_progress/completed

    roadmap: Mapped["Roadmap"] = relationship(back_populates="items")
    skill: Mapped["Skill"] = relationship()


class Assessment(Base):
    __tablename__ = "assessments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    skill_id: Mapped[str] = mapped_column(String(36), ForeignKey("skills.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(String(30), default="MCQ")

    questions: Mapped[list["AssessmentQuestion"]] = relationship(back_populates="assessment")


class AssessmentQuestion(Base):
    __tablename__ = "assessment_questions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    assessment_id: Mapped[str] = mapped_column(String(36), ForeignKey("assessments.id"), index=True)
    prompt: Mapped[str] = mapped_column(Text)
    options: Mapped[str] = mapped_column(JSON)  # list[str]
    correct_index: Mapped[int] = mapped_column(Integer)
    explanation: Mapped[str] = mapped_column(Text, nullable=True)

    assessment: Mapped["Assessment"] = relationship(back_populates="questions")


class AssessmentAttempt(Base, TimestampMixin):
    __tablename__ = "assessment_attempts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    assessment_id: Mapped[str] = mapped_column(String(36), ForeignKey("assessments.id"), index=True)
    score: Mapped[int] = mapped_column(Integer)
    total: Mapped[int] = mapped_column(Integer)
    percent: Mapped[float] = mapped_column(Float)
    previous_skill_level: Mapped[int] = mapped_column(Integer)
    updated_skill_level: Mapped[int] = mapped_column(Integer)
    answers_json: Mapped[str] = mapped_column(Text, nullable=True)


class StudentProgress(Base, TimestampMixin):
    """Canonical per-user per-skill level & verification record."""
    __tablename__ = "student_progress"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    skill_id: Mapped[str] = mapped_column(String(36), ForeignKey("skills.id"), index=True)
    level: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    status: Mapped[str] = mapped_column(String(30), default="self_reported")
    # self_reported -> evidence_found -> assessed -> verified
    has_resume_evidence: Mapped[bool] = mapped_column(Boolean, default=False)
    has_project_evidence: Mapped[bool] = mapped_column(Boolean, default=False)
    has_github_evidence: Mapped[bool] = mapped_column(Boolean, default=False)
    has_certification: Mapped[bool] = mapped_column(Boolean, default=False)
    best_assessment_percent: Mapped[float] = mapped_column(Float, nullable=True)
    has_practical_evidence: Mapped[bool] = mapped_column(Boolean, default=False)
    best_practical_score: Mapped[float] = mapped_column(Float, nullable=True)

    __table_args__ = (UniqueConstraint("user_id", "skill_id", name="uq_user_skill"),)
    skill: Mapped["Skill"] = relationship()


class ReadinessSnapshot(Base, TimestampMixin):
    __tablename__ = "readiness_snapshots"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    career_id: Mapped[str] = mapped_column(String(36), ForeignKey("careers.id"))
    overall_readiness: Mapped[float] = mapped_column(Float)
    technical_skills: Mapped[float] = mapped_column(Float)
    project_evidence: Mapped[float] = mapped_column(Float)
    assessment_performance: Mapped[float] = mapped_column(Float)
    skill_coverage: Mapped[float] = mapped_column(Float)
    verification: Mapped[float] = mapped_column(Float)


class PracticalAssessment(Base, TimestampMixin):
    __tablename__ = "practical_assessments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    skill_id: Mapped[str] = mapped_column(String(36), ForeignKey("skills.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    validation_type: Mapped[str] = mapped_column(String(50))  # e.g., "docker_containerize"

    skill: Mapped["Skill"] = relationship()


class PracticalSubmission(Base, TimestampMixin):
    __tablename__ = "practical_submissions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    assessment_id: Mapped[str] = mapped_column(String(36), ForeignKey("practical_assessments.id"), index=True)
    score: Mapped[float] = mapped_column(Float)
    passed: Mapped[bool] = mapped_column(Boolean)
    feedback: Mapped[str] = mapped_column(Text, nullable=True)  # JSON feedback breakdown
    previous_skill_level: Mapped[int] = mapped_column(Integer)
    updated_skill_level: Mapped[int] = mapped_column(Integer)
