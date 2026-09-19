from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# ---------- Auth ----------
class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str = Field(min_length=6)
    college: Optional[str] = None
    degree: Optional[str] = None
    department: Optional[str] = None
    graduation_year: Optional[int] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    full_name: str
    email: str
    college: Optional[str] = None
    degree: Optional[str] = None
    department: Optional[str] = None
    graduation_year: Optional[int] = None
    onboarding_complete: bool

    class Config:
        from_attributes = True


# ---------- Profile / onboarding ----------
class OnboardingRequest(BaseModel):
    college: Optional[str] = None
    degree: Optional[str] = None
    department: Optional[str] = None
    graduation_year: Optional[int] = None
    current_skills: list[dict] = Field(default_factory=list)  # [{name, level}]
    career_interests: list[str] = Field(default_factory=list)
    target_career_id: str
    weekly_hours: str
    preferred_learning_style: Optional[str] = "Mixed"


class ProfileOut(BaseModel):
    user: UserOut
    target_career_id: Optional[str] = None
    target_career_name: Optional[str] = None
    weekly_hours: Optional[str] = None
    preferred_learning_style: Optional[str] = None
    career_interests: Optional[str] = None
    github_username: Optional[str] = None


class ProfileUpdateRequest(BaseModel):
    weekly_hours: Optional[str] = None
    preferred_learning_style: Optional[str] = None
    career_interests: Optional[list[str]] = None
    target_career_id: Optional[str] = None
    github_username: Optional[str] = None


# ---------- Skills ----------
class SkillOut(BaseModel):
    id: str
    name: str
    category: str
    description: Optional[str] = None
    difficulty: str

    class Config:
        from_attributes = True


class SkillProfileItem(BaseModel):
    skill: SkillOut
    level: int
    status: str
    band: str
    has_resume_evidence: bool
    has_project_evidence: bool
    has_github_evidence: bool
    has_certification: bool
    best_assessment_percent: Optional[float] = None


# ---------- Careers ----------
class CareerSkillOut(BaseModel):
    skill: SkillOut
    required_level: int
    importance: str
    is_required: bool


class CareerOut(BaseModel):
    id: str
    name: str
    description: str
    responsibilities: Optional[str] = None

    class Config:
        from_attributes = True


class CareerDetailOut(CareerOut):
    skills: list[CareerSkillOut]
    match_percent: Optional[float] = None


# ---------- Evidence ----------
class EvidenceCreateRequest(BaseModel):
    type: str
    title: str
    description: Optional[str] = None
    skill_names: list[str] = Field(default_factory=list)


class EvidenceOut(BaseModel):
    id: str
    type: str
    title: str
    description: Optional[str] = None
    source_filename: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Gap analysis ----------
class GapItem(BaseModel):
    skill: SkillOut
    required_level: int
    current_level: int
    gap: int
    importance: str
    priority_score: float
    reason: str
    is_prerequisite_for: list[str] = Field(default_factory=list)


class GapAnalysisOut(BaseModel):
    career: CareerOut
    skill_coverage: float
    strong_skills: int
    partial_skills: int
    critical_gaps: int
    total_required_skills: int
    gaps: list[GapItem]


# ---------- Roadmap ----------
class RoadmapItemOut(BaseModel):
    id: str
    skill: SkillOut
    sequence: int
    phase_label: str
    why: str
    what_to_learn: str
    what_to_build: str
    how_to_prove: str
    estimated_hours: int
    status: str

    class Config:
        from_attributes = True


class RoadmapOut(BaseModel):
    id: str
    career: CareerOut
    version: int
    generated_reason: Optional[str] = None
    items: list[RoadmapItemOut]
    progress_percent: float


class RoadmapItemStatusUpdate(BaseModel):
    status: str


# ---------- Assessments ----------
class AssessmentQuestionOut(BaseModel):
    id: str
    prompt: str
    options: list[str]

    class Config:
        from_attributes = True


class AssessmentOut(BaseModel):
    id: str
    skill: SkillOut
    title: str
    description: Optional[str] = None
    type: str
    questions: list[AssessmentQuestionOut]

    class Config:
        from_attributes = True


class AssessmentListItem(BaseModel):
    id: str
    skill: SkillOut
    title: str
    type: str
    question_count: int
    best_percent: Optional[float] = None
    attempts: int


class AssessmentSubmitRequest(BaseModel):
    answers: dict[str, int]  # question_id -> selected option index


class AssessmentResultOut(BaseModel):
    score: int
    total: int
    percent: float
    previous_skill_level: int
    updated_skill_level: int
    new_status: str
    correct_answers: dict[str, int]
    roadmap_updated: bool


# ---------- Dashboard / Readiness / Analytics ----------
class ReadinessOut(BaseModel):
    overall_readiness: float
    technical_skills: float
    project_evidence: float
    assessment_performance: float
    skill_coverage: float
    verification: float
    explanation: dict[str, str]


class DashboardOut(BaseModel):
    full_name: str
    target_career: Optional[CareerOut] = None
    readiness: Optional[ReadinessOut] = None
    verified_skills_count: int
    total_profile_skills: int
    roadmap_progress_percent: float
    top_gaps: list[GapItem]
    next_best_action: str
    roadmap_weeks: list[dict]
    ai_mode: str


class ProgressPoint(BaseModel):
    date: str
    overall_readiness: float


class CategoryBreakdown(BaseModel):
    category: str
    average_level: int
    skill_count: int


class AnalyticsOut(BaseModel):
    readiness_trend: list[ProgressPoint]
    category_distribution: list[CategoryBreakdown]
    verified_vs_unverified: dict[str, int]
    assessment_scores: list[dict]
    top_remaining_gaps: list[str]


# ---------- Resume ----------
class ExtractedSkill(BaseModel):
    name: str
    confidence: float
    evidence: str


class ResumeAnalysisOut(BaseModel):
    filename: str
    ai_mode: str
    extracted_skills: list[ExtractedSkill]
    projects: list[str]
    certifications: list[str]
    education: list[str]
    message: str


# ---------- Job description matching ----------
class JobDescriptionRequest(BaseModel):
    text: str


class JobDescriptionMatchOut(BaseModel):
    match_percent: float
    matched_skills: list[str]
    missing_skills: list[str]
