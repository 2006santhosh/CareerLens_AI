const TOKEN_KEY = 'careerlens_token';

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}
export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}
export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = { ...(options.headers as Record<string, string>) };
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`/api${path}`, { ...options, headers });
  if (res.status === 401) {
    clearToken();
    if (!path.includes('/auth/')) {
      window.location.href = '/login';
    }
  }
  if (!res.ok) {
    let detail = 'Something went wrong. Please try again.';
    try {
      const data = await res.json();
      detail = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
    } catch {
      /* ignore parse errors */
    }
    throw new ApiError(detail, res.status);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: 'POST', body: body !== undefined ? JSON.stringify(body) : undefined }),
  put: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: 'PUT', body: JSON.stringify(body) }),
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: 'PATCH', body: JSON.stringify(body) }),
  del: <T>(path: string) => request<T>(path, { method: 'DELETE' }),
  upload: <T>(path: string, form: FormData) => request<T>(path, { method: 'POST', body: form }),
};

export { ApiError };

// ---------------- Types ----------------

export interface User {
  id: string;
  full_name: string;
  email: string;
  college?: string;
  degree?: string;
  department?: string;
  graduation_year?: number;
  onboarding_complete: boolean;
}

export interface Skill {
  id: string;
  name: string;
  category: string;
  description?: string;
  difficulty: string;
}

export interface SkillProfileItem {
  skill: Skill;
  level: number;
  status: string;
  band: string;
  has_resume_evidence: boolean;
  has_project_evidence: boolean;
  has_github_evidence: boolean;
  has_certification: boolean;
  best_assessment_percent?: number;
  has_practical_evidence?: boolean;
  best_practical_score?: number;
  latest_evidence_excerpt?: string;
}

export interface Career {
  id: string;
  name: string;
  description: string;
  responsibilities?: string;
}

export interface CareerSkillOut {
  skill: Skill;
  required_level: number;
  importance: string;
  is_required: boolean;
}

export interface CareerDetail extends Career {
  skills: CareerSkillOut[];
  match_percent?: number;
}

export interface GapItem {
  skill: Skill;
  required_level: number;
  current_level: number;
  gap: number;
  importance: string;
  priority_score: number;
  reason: string;
  is_prerequisite_for: string[];
}

export interface GapAnalysis {
  career: Career;
  skill_coverage: number;
  strong_skills: number;
  partial_skills: number;
  critical_gaps: number;
  total_required_skills: number;
  gaps: GapItem[];
}

export interface RoadmapItem {
  id: string;
  skill: Skill;
  sequence: number;
  phase_label: string;
  why: string;
  what_to_learn: string;
  what_to_build: string;
  how_to_prove: string;
  estimated_hours: number;
  status: string;
}

export interface Roadmap {
  id: string;
  career: Career;
  version: number;
  generated_reason?: string;
  items: RoadmapItem[];
  progress_percent: number;
}

export interface AssessmentListItem {
  id: string;
  skill: Skill;
  title: string;
  type: string;
  question_count: number;
  best_percent?: number;
  attempts: number;
}

export interface AssessmentQuestion {
  id: string;
  prompt: string;
  options: string[];
}

export interface AssessmentDetail {
  id: string;
  skill: Skill;
  title: string;
  description?: string;
  type: string;
  questions: AssessmentQuestion[];
}

export interface AssessmentResult {
  score: number;
  total: number;
  percent: number;
  previous_skill_level: number;
  updated_skill_level: number;
  new_status: string;
  correct_answers: Record<string, number>;
  roadmap_updated: boolean;
}

export interface Readiness {
  overall_readiness: number;
  technical_skills: number;
  project_evidence: number;
  assessment_performance: number;
  skill_coverage: number;
  verification: number;
  explanation: Record<string, string>;
}

export interface Dashboard {
  full_name: string;
  target_career?: Career;
  readiness?: Readiness;
  verified_skills_count: number;
  total_profile_skills: number;
  roadmap_progress_percent: number;
  top_gaps: GapItem[];
  next_best_action: string;
  roadmap_weeks: { week: number; skill: string; status: string }[];
  ai_mode: string;
}

export interface Evidence {
  id: string;
  type: string;
  title: string;
  description?: string;
  source_filename?: string;
  created_at: string;
}

export interface ProfileOut {
  user: User;
  target_career_id?: string;
  target_career_name?: string;
  weekly_hours?: string;
  preferred_learning_style?: string;
  career_interests?: string;
  github_username?: string;
}

export interface AnalyticsOut {
  readiness_trend: { date: string; overall_readiness: number }[];
  category_distribution: { category: string; average_level: number; skill_count: number }[];
  verified_vs_unverified: Record<string, number>;
  assessment_scores: { skill: string; percent: number; date: string }[];
  top_remaining_gaps: string[];
}

export interface ExtractedSkill {
  name: string;
  confidence: number;
  evidence: string;
}

export interface ResumeAnalysisOut {
  filename: string;
  ai_mode: string;
  extracted_skills: ExtractedSkill[];
  projects: string[];
  certifications: string[];
  education: string[];
  message: string;
}

export interface JobDescriptionMatchOut {
  match_percent: number;
  matched_skills: string[];
  missing_skills: string[];
  career_id?: string;
}

export interface PracticalAssessmentOut {
  id: string;
  skill: Skill;
  title: string;
  description: string;
  validation_type: string;
}

export interface PracticalAssessmentResult {
  score: number;
  passed: boolean;
  previous_skill_level: number;
  updated_skill_level: number;
  new_status: string;
  feedback: { check: string; status: string }[];
  roadmap_updated: boolean;
}

export interface SimulatorSkillOverride {
  skill_id: string;
  level?: number;
  status?: string;
  has_project_evidence?: boolean;
  has_github_evidence?: boolean;
}

export interface SimulatorResponse {
  readiness: Readiness;
  gap_analysis: GapAnalysis;
}
