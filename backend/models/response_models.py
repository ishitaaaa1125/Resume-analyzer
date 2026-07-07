from __future__ import annotations

from typing import Any, Union

from pydantic import BaseModel, Field


class RecruiterDecision(BaseModel):
    status: str = ""
    reason: str = ""


class HiringConfidence(BaseModel):
    level: str = ""
    explanation: str = ""


class ScoreReason(BaseModel):
    score: int = Field(default=0, ge=0, le=100)
    reason: str = ""


class SkillAnalysis(BaseModel):
    skill: str = ""
    category: str = ""
    found: bool = False
    match_percentage: int = Field(default=0, ge=0, le=100)
    feedback: str = ""
    recommendation: str = ""


class SkillGroup(BaseModel):
    category: str = ""
    current_skills: list[str] = Field(default_factory=list)
    required_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    outdated_skills: list[str] = Field(default_factory=list)
    repeated_skills: list[str] = Field(default_factory=list)
    feedback: str = ""


class SkillsProfile(BaseModel):
    current_skills: list[str] = Field(default_factory=list)
    strong_skills: list[str] = Field(default_factory=list)
    intermediate_skills: list[str] = Field(default_factory=list)
    beginner_skills: list[str] = Field(default_factory=list)
    missing_skills: list[dict[str, Any]] = Field(default_factory=list)
    outdated_skills: list[str] = Field(default_factory=list)
    industry_trending_skills: list[str] = Field(default_factory=list)
    most_valuable_skills: list[str] = Field(default_factory=list)
    learning_priority: list[dict[str, Any]] = Field(default_factory=list)


class ExperienceAnalysisEntry(BaseModel):
    company: str = ""
    role: str = ""
    ownership: str = ""
    leadership: str = ""
    business_impact: str = ""
    technical_responsibility: str = ""
    code_quality: str = ""
    testing: str = ""
    deployment: str = ""
    collaboration: str = ""
    problem_solving: str = ""
    architecture_knowledge: str = ""
    positive_points: list[str] = Field(default_factory=list)
    negative_points: list[str] = Field(default_factory=list)
    missing_points: list[str] = Field(default_factory=list)
    weak_bullets: list[str] = Field(default_factory=list)
    rewritten_examples: list[str] = Field(default_factory=list)


class ProjectAnalysisEntry(BaseModel):
    project_name: str = ""
    complexity_score: int = Field(default=0, ge=0, le=100)
    architecture_score: int = Field(default=0, ge=0, le=100)
    security_score: int = Field(default=0, ge=0, le=100)
    business_value: str = ""
    technical_depth: str = ""
    architecture_quality: str = ""
    database_design: str = ""
    scalability: str = ""
    difficulty_level: str = ""
    production_readiness: str = ""
    technologies: list[str] = Field(default_factory=list)
    missing_features: list[str] = Field(default_factory=list)
    architecture_improvements: list[str] = Field(default_factory=list)
    suggested_technologies: list[str] = Field(default_factory=list)
    business_impact: str = ""
    real_recruiter_feedback: str = ""
    interview_questions: list[str] = Field(default_factory=list)
    recruiter_impression: str = ""
    industry_relevance: str = ""
    good_points: list[str] = Field(default_factory=list)
    missing_points: list[str] = Field(default_factory=list)
    ats_feedback: str = ""
    recommended_changes: list[str] = Field(default_factory=list)
    rewritten_description: str = ""


class EducationAnalysis(BaseModel):
    summary: str = ""
    recommendations: list[str] = Field(default_factory=list)


class IssueFix(BaseModel):
    issue: str = ""
    reason: str = ""
    fix: str = ""


class FormattingIssue(BaseModel):
    issue: str = ""
    impact: str = ""
    recommendation: str = ""


class ATSBreakdown(BaseModel):
    formatting: int = Field(default=0, ge=0, le=100)
    projects: int = Field(default=0, ge=0, le=100)
    experience: int = Field(default=0, ge=0, le=100)
    skills: int = Field(default=0, ge=0, le=100)
    education: int = Field(default=0, ge=0, le=100)
    keywords: int = Field(default=0, ge=0, le=100)
    impact: int = Field(default=0, ge=0, le=100)
    readability: int = Field(default=0, ge=0, le=100)
    grammar: int = Field(default=0, ge=0, le=100)
    achievements: int = Field(default=0, ge=0, le=100)


class ATSBreakdownReason(BaseModel):
    category: str = ""
    score: int = Field(default=0, ge=0, le=100)
    reason: str = ""


class ImprovementPlanEntry(BaseModel):
    section: str = ""
    current_problem: str = ""
    why_it_matters: str = ""
    recommended_change: str = ""
    example_before: str = ""
    example_after: str = ""
    priority: str = "High"


class ActionPlanEntry(BaseModel):
    step: int = 1
    title: str = ""
    description: str = ""
    expected_result: str = ""


class RecruiterFeedback(BaseModel):
    hr_feedback: str = ""
    technical_lead_feedback: str = ""
    engineering_manager_feedback: str = ""


class ReviewerSimulation(BaseModel):
    reviewer: str = ""
    what_impressed_them: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    questions: list[str] = Field(default_factory=list)
    would_shortlist: str = ""
    would_hire: str = ""


class InterviewQuestion(BaseModel):
    question: str = ""
    why_asked: str = ""
    preparation_hint: str = ""


class SkillGapEntry(BaseModel):
    skill: str = ""
    current_evidence: str = ""
    required_level: str = ""
    learning_priority: str = ""
    recommendation: str = ""


class RoadmapEntry(BaseModel):
    skill: str = ""
    priority: str = ""
    plan: str = ""
    expected_outcome: str = ""


class RoadmapPhases(BaseModel):
    thirty_day: list[str] = Field(default_factory=list)
    sixty_day: list[str] = Field(default_factory=list)
    ninety_day: list[str] = Field(default_factory=list)


class ArchitectureSignal(BaseModel):
    item: str = ""
    detected: str = ""
    missing: str = ""
    recommended: str = ""


class ArchitectureAnalysis(BaseModel):
    detected: list[ArchitectureSignal] = Field(default_factory=list)
    missing: list[ArchitectureSignal] = Field(default_factory=list)
    recommended: list[ArchitectureSignal] = Field(default_factory=list)


class HiringDecisionDetails(BaseModel):
    hiring_probability: str = ""
    interview_probability: str = ""
    expected_role: str = ""
    expected_salary_range: str = ""
    expected_experience_level: str = ""
    confidence_level: str = ""
    reasons: list[str] = Field(default_factory=list)
    major_hiring_risks: list[str] = Field(default_factory=list)
    final_recommendation: str = ""


class AnalysisResponse(BaseModel):
    ats_score: int = Field(ge=0, le=100)
    ats_score_reason: str = ""
    match_percentage: int = Field(default=0, ge=0, le=100)
    resume_match_percentage: int = Field(default=0, ge=0, le=100)
    job_match_percentage: int = Field(default=0, ge=0, le=100)
    resume_match_reason: str = ""
    job_match_reason: str = ""
    hiring_confidence: HiringConfidence = Field(default_factory=HiringConfidence)
    critical_issues_reason: str = ""
    overall_feedback: str = ""
    executive_summary: str = ""
    recruiter_decision: RecruiterDecision = Field(default_factory=RecruiterDecision)
    resume_strengths: list[str] = Field(default_factory=list)
    resume_weaknesses: list[str] = Field(default_factory=list)
    hiring_risks: list[str] = Field(default_factory=list)
    matched_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    extra_skills: list[str] = Field(default_factory=list)
    keyword_analysis: str = ""
    semantic_relevance: str = ""
    skills_analysis: list[SkillAnalysis] = Field(default_factory=list)
    skills_matrix: list[SkillGroup] = Field(default_factory=list)
    skills_profile: SkillsProfile = Field(default_factory=SkillsProfile)
    skill_gap: list[SkillGapEntry] = Field(default_factory=list)
    experience_analysis: list[ExperienceAnalysisEntry] = Field(default_factory=list)
    project_analysis: list[ProjectAnalysisEntry] = Field(default_factory=list)
    education_analysis: EducationAnalysis = Field(default_factory=EducationAnalysis)
    grammar_analysis: list[IssueFix] = Field(default_factory=list)
    formatting_analysis: list[FormattingIssue] = Field(default_factory=list)
    ats_breakdown: ATSBreakdown = Field(default_factory=ATSBreakdown)
    ats_breakdown_details: list[ATSBreakdownReason] = Field(default_factory=list)
    critical_issues: list[str] = Field(default_factory=list)
    high_priority_changes: list[str] = Field(default_factory=list)
    medium_priority_changes: list[str] = Field(default_factory=list)
    minor_improvements: list[str] = Field(default_factory=list)
    missing_sections: list[str] = Field(default_factory=list)
    detailed_improvement_plan: list[ImprovementPlanEntry] = Field(default_factory=list)
    action_plan: list[ActionPlanEntry] = Field(default_factory=list)
    top_recommendations: list[str] = Field(default_factory=list)
    improved_resume_bullets: list[str] = Field(default_factory=list)
    learning_roadmap: list[RoadmapEntry] = Field(default_factory=list)
    learning_roadmap_phases: RoadmapPhases = Field(default_factory=RoadmapPhases)
    interview_questions: list[InterviewQuestion] = Field(default_factory=list)
    recruiter_feedback: RecruiterFeedback = Field(default_factory=RecruiterFeedback)
    recruiter_simulation: list[ReviewerSimulation] = Field(default_factory=list)
    architecture_analysis: ArchitectureAnalysis = Field(default_factory=ArchitectureAnalysis)
    hiring_decision_details: HiringDecisionDetails = Field(default_factory=HiringDecisionDetails)
    final_summary: str = ""

    # Backward-compatible fields for older frontend code.
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    matching_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    keyword_match_percentage: int = 0
    summary: str = ""
    improvement_plan: list[ImprovementPlanEntry] = Field(default_factory=list)
    resume_highlights: list[str] = Field(default_factory=list)
    resume_red_flags: list[str] = Field(default_factory=list)
    final_recommendations: list[str] = Field(default_factory=list)
    experience_analysis_legacy: list[str] = Field(default_factory=list)
    project_analysis_legacy: list[str] = Field(default_factory=list)
    education_analysis_legacy: str = ""
    grammar_issues: list[str] = Field(default_factory=list)
    formatting_issues: list[str] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    detail: Union[str, dict[str, Any]]
