from __future__ import annotations

import json
import os
import re
from collections import Counter
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import HTTPException
from google import genai
from google.genai import types

BACKEND_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BACKEND_DIR / ".env"

REQUIRED_LIST_FIELDS = {
    "skills_analysis",
    "skills_matrix",
    "skill_gap",
    "experience_analysis",
    "project_analysis",
    "grammar_analysis",
    "formatting_analysis",
    "detailed_improvement_plan",
    "action_plan",
    "top_recommendations",
    "interview_questions",
    "learning_roadmap",
    "ats_breakdown_details",
    "recruiter_simulation",
}

SKILL_CATEGORIES = {
    "Programming": {"python", "java", "javascript", "typescript", "c++", "c#", "go", "golang", "php", "ruby"},
    "Backend": {"fastapi", "django", "flask", "spring", "node", "node.js", "express", "rest", "api", "graphql", "jwt"},
    "Frontend": {"react", "next.js", "nextjs", "html", "css", "tailwind", "redux", "vite"},
    "Database": {"sql", "mysql", "postgres", "postgresql", "mongodb", "redis", "firebase"},
    "Cloud": {"aws", "azure", "gcp", "cloud", "lambda", "s3"},
    "DevOps": {"docker", "kubernetes", "ci/cd", "jenkins", "terraform", "linux"},
    "Tools": {"git", "github", "jira", "postman", "figma"},
    "Soft Skills": {"leadership", "communication", "collaboration", "ownership", "problem-solving", "agile"},
}

STOP_WORDS = {
    "the",
    "and",
    "for",
    "with",
    "this",
    "that",
    "from",
    "role",
    "job",
    "resume",
    "candidate",
    "experience",
    "software",
    "engineer",
    "developer",
    "team",
    "work",
    "working",
    "skills",
    "requirements",
}


def normalize_text(text: str) -> str:
    return " ".join((text or "").split())


def load_environment() -> bool:
    load_dotenv(ENV_PATH, override=True)
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if api_key and api_key != "YOUR_GEMINI_API_KEY":
        print("Gemini API key loaded")
        return True
    print("GEMINI_API_KEY not found")
    return False


class GeminiService:
    def __init__(self) -> None:
        load_environment()
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key or api_key == "YOUR_GEMINI_API_KEY":
            raise HTTPException(
                status_code=500,
                detail="GEMINI_API_KEY is not configured. Add it to backend/.env before starting the server.",
            )
        self.client = genai.Client(api_key=api_key)

    def analyze_resume(self, resume_text: str, job_description: str) -> dict[str, Any]:
        if not resume_text or not resume_text.strip():
            raise HTTPException(status_code=400, detail="Unable to extract text from uploaded resume.")
        if not job_description or not job_description.strip():
            raise HTTPException(status_code=400, detail="Job description cannot be empty.")

        payload = self._call_gemini(resume_text, job_description)
        normalized = self._normalize_response(payload, resume_text, job_description)
        if self._has_empty_required_lists(normalized):
            regenerated = self._call_gemini(resume_text, job_description, repair_payload=normalized)
            normalized = self._normalize_response(regenerated, resume_text, job_description)
        return self._ensure_required_content(normalized, resume_text, job_description)

    def _call_gemini(
        self,
        resume_text: str,
        job_description: str,
        repair_payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        prompt = self._build_prompt(resume_text, job_description, repair_payload)
        try:
            print(f"Resume character count: {len(resume_text)}")
            print(f"Job description character count: {len(job_description)}")
            print("Gemini prompt preview:")
            print(prompt[:2000])
            model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip() or "gemini-2.0-flash"
            response = self.client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.15,
                    response_mime_type="application/json",
                ),
            )
            text = response.text or ""
            if not text:
                raise ValueError("Gemini returned an empty response.")
            print("Gemini response preview:")
            print(text[:4000])
            return self._parse_gemini_payload(text)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=502, detail="Gemini returned invalid JSON.") from exc
        except HTTPException:
            raise
        except Exception as exc:
            detail = str(exc)
            if "429" in detail or "quota" in detail.lower() or "resource_exhausted" in detail.lower():
                raise HTTPException(
                    status_code=429,
                    detail=(
                        "Gemini API quota exceeded for the configured API key/model. "
                        "Check the key's Google AI Studio project, billing, rate limits, or set GEMINI_MODEL in backend/.env. "
                        f"Provider detail: {detail[:800]}"
                    ),
                ) from exc
            raise HTTPException(status_code=502, detail=f"Gemini API request failed. Provider detail: {detail[:500]}") from exc

    def _build_prompt(
        self,
        resume_text: str,
        job_description: str,
        repair_payload: dict[str, Any] | None = None,
    ) -> str:
        repair_instruction = ""
        if repair_payload:
            empty_fields = [field for field in REQUIRED_LIST_FIELDS if not repair_payload.get(field)]
            repair_instruction = (
                "\nThis is a regeneration request. Your previous response left these required arrays empty: "
                f"{', '.join(empty_fields)}. Re-read the resume and job description and return populated, evidence-based values."
            )

        return f"""
You are simultaneously an ATS scanner, senior HR recruiter, technical interviewer, hiring manager,
resume reviewer, resume writer, and career coach.

Analyze the uploaded resume against the uploaded job description. Use semantic reasoning, not keyword
counting only. Every observation must be grounded in the resume text, the job description, or a clearly
identified absence from the resume. Do not invent companies, projects, certifications, metrics, or skills.
Do not provide generic resume advice.

Return JSON only. No markdown. No commentary outside JSON.
{repair_instruction}

Scoring rules:
- Calculate all scores from the resume and job description evidence.
- Explain scoring through feedback fields and recommendations.
- Use 0-100 integers for all score fields.
- Overall ATS score should consider formatting, projects, experience, skills, education, keywords, impact,
  readability, grammar, and achievements.
- Never show a score without a reason.
- Do not combine projects. Create one project_analysis object for every project visible in the resume.
- Interview questions must be unique and distributed as 5 project-based, 5 technology-based, 3 scenario-based, and 2 HR questions.
- The executive_summary must be 2-4 recruiter-quality paragraphs covering candidate profile, strongest technologies, best project, career readiness, hiring risks, and recruiter recommendation.

Required JSON schema:
{{
  "ats_score": 0,
  "ats_score_reason": "",
  "match_percentage": 0,
  "resume_match_percentage": 0,
  "job_match_percentage": 0,
  "resume_match_reason": "",
  "job_match_reason": "",
  "hiring_confidence": {{"level": "Low|Medium|High", "explanation": ""}},
  "critical_issues_reason": "",
  "overall_feedback": "",
  "executive_summary": "",
  "recruiter_decision": {{"status": "Shortlist|Hold|Reject", "reason": ""}},
  "resume_strengths": [],
  "resume_weaknesses": [],
  "hiring_risks": [],
  "matched_keywords": [],
  "missing_keywords": [],
  "extra_skills": [],
  "keyword_analysis": "",
  "semantic_relevance": "",
  "skills_analysis": [
    {{"skill": "", "category": "", "found": true, "match_percentage": 0, "feedback": "", "recommendation": ""}}
  ],
  "skills_matrix": [
    {{"category": "Programming|Backend|Frontend|Database|Cloud|DevOps|Tools|Soft Skills", "current_skills": [], "required_skills": [], "missing_skills": [], "outdated_skills": [], "repeated_skills": [], "feedback": ""}}
  ],
  "skills_profile": {{
    "current_skills": [],
    "strong_skills": [],
    "intermediate_skills": [],
    "beginner_skills": [],
    "missing_skills": [{{"skill": "", "current_evidence": "", "required_level": "", "learning_priority": "High|Medium|Low", "recommendation": ""}}],
    "outdated_skills": [],
    "industry_trending_skills": [],
    "most_valuable_skills": [],
    "learning_priority": [{{"skill": "", "current_evidence": "", "required_level": "", "learning_priority": "High|Medium|Low", "recommendation": ""}}]
  }},
  "skill_gap": [
    {{"skill": "", "current_evidence": "", "required_level": "", "learning_priority": "High|Medium|Low", "recommendation": ""}}
  ],
  "experience_analysis": [
    {{"company": "", "role": "", "ownership": "", "leadership": "", "business_impact": "", "technical_responsibility": "", "code_quality": "", "testing": "", "deployment": "", "collaboration": "", "problem_solving": "", "architecture_knowledge": "", "positive_points": [], "negative_points": [], "missing_points": [], "weak_bullets": [], "rewritten_examples": []}}
  ],
  "project_analysis": [
    {{"project_name": "", "complexity_score": 0, "architecture_score": 0, "security_score": 0, "business_value": "", "technical_depth": "", "architecture_quality": "", "database_design": "", "scalability": "", "difficulty_level": "", "production_readiness": "", "technologies": [], "missing_features": [], "architecture_improvements": [], "suggested_technologies": [], "business_impact": "", "real_recruiter_feedback": "", "interview_questions": [], "recruiter_impression": "", "industry_relevance": "", "good_points": [], "missing_points": [], "ats_feedback": "", "recommended_changes": [], "rewritten_description": ""}}
  ],
  "education_analysis": {{"summary": "", "recommendations": []}},
  "grammar_analysis": [
    {{"issue": "", "reason": "", "fix": ""}}
  ],
  "formatting_analysis": [
    {{"issue": "", "impact": "", "recommendation": ""}}
  ],
  "ats_breakdown": {{"formatting": 0, "projects": 0, "experience": 0, "skills": 0, "education": 0, "keywords": 0, "impact": 0, "readability": 0, "grammar": 0, "achievements": 0}},
  "ats_breakdown_details": [
    {{"category": "formatting", "score": 0, "reason": ""}}
  ],
  "critical_issues": [],
  "high_priority_changes": [],
  "medium_priority_changes": [],
  "minor_improvements": [],
  "missing_sections": [],
  "detailed_improvement_plan": [
    {{"section": "", "current_problem": "", "why_it_matters": "", "recommended_change": "", "example_before": "", "example_after": "", "priority": "Critical|High|Medium|Low"}}
  ],
  "action_plan": [
    {{"step": 1, "title": "", "description": "", "expected_result": ""}}
  ],
  "top_recommendations": [],
  "improved_resume_bullets": [],
  "learning_roadmap": [
    {{"skill": "", "priority": "High|Medium|Low", "plan": "", "expected_outcome": ""}}
  ],
  "learning_roadmap_phases": {{"thirty_day": [], "sixty_day": [], "ninety_day": []}},
  "interview_questions": [
    {{"question": "", "why_asked": "", "preparation_hint": ""}}
  ],
  "recruiter_feedback": {{"hr_feedback": "", "technical_lead_feedback": "", "engineering_manager_feedback": ""}},
  "recruiter_simulation": [
    {{"reviewer": "HR Recruiter|Technical Lead|Engineering Manager", "what_impressed_them": [], "concerns": [], "questions": [], "would_shortlist": "", "would_hire": ""}}
  ],
  "architecture_analysis": {{
    "detected": [{{"item": "", "detected": "", "missing": "", "recommended": ""}}],
    "missing": [{{"item": "", "detected": "", "missing": "", "recommended": ""}}],
    "recommended": [{{"item": "", "detected": "", "missing": "", "recommended": ""}}]
  }},
  "hiring_decision_details": {{"hiring_probability": "", "interview_probability": "", "expected_role": "", "expected_salary_range": "", "expected_experience_level": "", "confidence_level": "", "reasons": [], "major_hiring_risks": [], "final_recommendation": ""}},
  "final_summary": ""
}}

Resume:
{resume_text}

Job Description:
{job_description}
"""

    def _parse_gemini_payload(self, text: str) -> dict[str, Any]:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            cleaned = cleaned[start : end + 1]
        parsed = json.loads(cleaned)
        if not isinstance(parsed, dict):
            raise json.JSONDecodeError("Gemini JSON root must be an object", cleaned, 0)
        return parsed

    def _normalize_response(
        self,
        payload: dict[str, Any],
        resume_text: str = "",
        job_description: str = "",
    ) -> dict[str, Any]:
        ats_breakdown = self._normalize_ats_breakdown(payload.get("ats_breakdown"))
        ats_score = self._clamp_score(payload.get("ats_score"))
        if not ats_score:
            ats_score = round(sum(ats_breakdown.values()) / max(1, len(ats_breakdown)))

        grammar = self._normalize_issue_fix_list(payload.get("grammar_analysis"))
        formatting = self._normalize_formatting_list(payload.get("formatting_analysis"))
        skills_analysis = self._normalize_skills_analysis(payload.get("skills_analysis"))
        experience = self._normalize_experience_analysis(payload.get("experience_analysis"))
        projects = self._normalize_project_analysis(payload.get("project_analysis"))
        detailed_plan = self._normalize_improvement_plan(payload.get("detailed_improvement_plan") or payload.get("improvement_plan"))
        action_plan = self._normalize_action_plan(payload.get("action_plan"))
        matched = self._coerce_string_list(payload.get("matched_keywords") or payload.get("matching_skills"))
        missing = self._coerce_string_list(payload.get("missing_keywords") or payload.get("missing_skills"))
        strengths = self._coerce_string_list(payload.get("resume_strengths") or payload.get("strengths"))
        weaknesses = self._coerce_string_list(payload.get("resume_weaknesses") or payload.get("weaknesses"))

        recruiter_decision = payload.get("recruiter_decision") if isinstance(payload.get("recruiter_decision"), dict) else {}
        confidence = payload.get("hiring_confidence") if isinstance(payload.get("hiring_confidence"), dict) else {}
        recruiter_feedback = payload.get("recruiter_feedback") if isinstance(payload.get("recruiter_feedback"), dict) else {}
        skills_profile = payload.get("skills_profile") if isinstance(payload.get("skills_profile"), dict) else {}

        normalized = {
            "ats_score": ats_score,
            "ats_score_reason": self._coerce_text(payload.get("ats_score_reason")),
            "match_percentage": self._clamp_score(payload.get("match_percentage"), ats_score),
            "resume_match_percentage": self._clamp_score(payload.get("resume_match_percentage"), ats_score),
            "job_match_percentage": self._clamp_score(payload.get("job_match_percentage"), ats_breakdown["keywords"]),
            "resume_match_reason": self._coerce_text(payload.get("resume_match_reason")),
            "job_match_reason": self._coerce_text(payload.get("job_match_reason")),
            "hiring_confidence": {
                "level": self._coerce_text(confidence.get("level")),
                "explanation": self._coerce_text(confidence.get("explanation")),
            },
            "critical_issues_reason": self._coerce_text(payload.get("critical_issues_reason")),
            "overall_feedback": self._coerce_text(payload.get("overall_feedback")),
            "executive_summary": self._coerce_text(payload.get("executive_summary") or payload.get("summary")),
            "recruiter_decision": {
                "status": self._coerce_text(recruiter_decision.get("status")),
                "reason": self._coerce_text(recruiter_decision.get("reason")),
            },
            "resume_strengths": strengths,
            "resume_weaknesses": weaknesses,
            "hiring_risks": self._coerce_string_list(payload.get("hiring_risks")),
            "matched_keywords": matched,
            "missing_keywords": missing,
            "extra_skills": self._coerce_string_list(payload.get("extra_skills")),
            "keyword_analysis": self._coerce_text(payload.get("keyword_analysis")),
            "semantic_relevance": self._coerce_text(payload.get("semantic_relevance")),
            "skills_analysis": skills_analysis,
            "skills_matrix": self._normalize_skills_matrix(payload.get("skills_matrix")),
            "skills_profile": {
                "current_skills": self._coerce_string_list(skills_profile.get("current_skills")),
                "strong_skills": self._coerce_string_list(skills_profile.get("strong_skills")),
                "intermediate_skills": self._coerce_string_list(skills_profile.get("intermediate_skills")),
                "beginner_skills": self._coerce_string_list(skills_profile.get("beginner_skills")),
                "missing_skills": self._normalize_skill_gap(skills_profile.get("missing_skills")),
                "outdated_skills": self._coerce_string_list(skills_profile.get("outdated_skills")),
                "industry_trending_skills": self._coerce_string_list(skills_profile.get("industry_trending_skills")),
                "most_valuable_skills": self._coerce_string_list(skills_profile.get("most_valuable_skills")),
                "learning_priority": self._normalize_skill_gap(skills_profile.get("learning_priority")),
            },
            "skill_gap": self._normalize_skill_gap(payload.get("skill_gap")),
            "experience_analysis": experience,
            "project_analysis": projects,
            "education_analysis": self._normalize_education_analysis(payload.get("education_analysis")),
            "grammar_analysis": grammar,
            "formatting_analysis": formatting,
            "ats_breakdown": ats_breakdown,
            "ats_breakdown_details": self._normalize_ats_breakdown_details(payload.get("ats_breakdown_details")),
            "critical_issues": self._coerce_string_list(payload.get("critical_issues")),
            "high_priority_changes": self._coerce_string_list(payload.get("high_priority_changes")),
            "medium_priority_changes": self._coerce_string_list(payload.get("medium_priority_changes")),
            "minor_improvements": self._coerce_string_list(payload.get("minor_improvements") or payload.get("low_priority_changes")),
            "missing_sections": self._coerce_string_list(payload.get("missing_sections")),
            "detailed_improvement_plan": detailed_plan,
            "action_plan": action_plan,
            "top_recommendations": self._coerce_string_list(payload.get("top_recommendations") or payload.get("recommendations")),
            "improved_resume_bullets": self._coerce_string_list(payload.get("improved_resume_bullets")),
            "learning_roadmap": self._normalize_learning_roadmap(payload.get("learning_roadmap")),
            "interview_questions": self._normalize_interview_questions(payload.get("interview_questions")),
            "recruiter_feedback": {
                "hr_feedback": self._coerce_text(recruiter_feedback.get("hr_feedback")),
                "technical_lead_feedback": self._coerce_text(recruiter_feedback.get("technical_lead_feedback")),
                "engineering_manager_feedback": self._coerce_text(recruiter_feedback.get("engineering_manager_feedback")),
            },
            "recruiter_simulation": self._normalize_recruiter_simulation(payload.get("recruiter_simulation")),
            "architecture_analysis": self._normalize_architecture_analysis(payload.get("architecture_analysis")),
            "hiring_decision_details": self._normalize_hiring_decision_details(payload.get("hiring_decision_details")),
            "learning_roadmap_phases": self._normalize_roadmap_phases(payload.get("learning_roadmap_phases")),
            "final_summary": self._coerce_text(payload.get("final_summary")),
        }

        normalized.update(
            {
                "strengths": normalized["resume_strengths"],
                "weaknesses": normalized["resume_weaknesses"],
                "recommendations": normalized["top_recommendations"],
                "matching_skills": normalized["matched_keywords"],
                "missing_skills": normalized["missing_keywords"],
                "keyword_match_percentage": normalized["ats_breakdown"]["keywords"],
                "summary": normalized["executive_summary"],
                "improvement_plan": normalized["detailed_improvement_plan"],
                "resume_highlights": self._coerce_string_list(payload.get("resume_highlights")) or normalized["resume_strengths"],
                "resume_red_flags": self._coerce_string_list(payload.get("resume_red_flags")) or normalized["hiring_risks"] or normalized["resume_weaknesses"],
                "final_recommendations": self._coerce_string_list(payload.get("final_recommendations")) or normalized["top_recommendations"],
                "experience_analysis_legacy": [
                    f"{entry['company']}: {entry['role']}" for entry in normalized["experience_analysis"]
                ],
                "project_analysis_legacy": [entry["project_name"] for entry in normalized["project_analysis"]],
                "education_analysis_legacy": normalized["education_analysis"]["summary"],
                "grammar_issues": [entry["issue"] for entry in normalized["grammar_analysis"]],
                "formatting_issues": [entry["issue"] for entry in normalized["formatting_analysis"]],
            }
        )
        return normalized

    def _build_resume_specific_analysis(self, resume_text: str, job_description: str) -> dict[str, Any]:
        resume_text = normalize_text(resume_text)
        job_description = normalize_text(job_description)
        resume_lower = resume_text.lower()
        job_keywords = self._extract_keywords(job_description)
        resume_keywords = self._extract_keywords(resume_text)
        matched = [keyword for keyword in job_keywords if keyword.lower() in resume_lower]
        missing = [keyword for keyword in job_keywords if keyword.lower() not in resume_lower]
        extra = [keyword for keyword in resume_keywords if keyword not in job_keywords]

        missing_sections = self._detect_missing_sections(resume_lower)
        has_metrics = bool(re.search(r"\b\d+%|\b\d+\+|\b\d{2,}\b|reduced|improved|increased|optimized", resume_lower))
        keyword_score = round((len(matched) / max(1, len(job_keywords))) * 100)
        skills_score = min(100, 35 + len(matched) * 7)
        projects_score = 72 if "project" in resume_lower else 35
        experience_score = 72 if any(term in resume_lower for term in ["experience", "developer", "engineer", "intern"]) else 38
        impact_score = 76 if has_metrics else 32
        education_score = 75 if not any(section == "Education" for section in missing_sections) else 35
        formatting_score = 78 if len(resume_text) > 1000 else 58
        grammar_score = 82
        readability_score = 72 if len(resume_text.split()) > 250 else 55
        achievements_score = impact_score
        ats_breakdown = {
            "formatting": formatting_score,
            "projects": projects_score,
            "experience": experience_score,
            "skills": skills_score,
            "education": education_score,
            "keywords": keyword_score,
            "impact": impact_score,
            "readability": readability_score,
            "grammar": grammar_score,
            "achievements": achievements_score,
        }
        ats_score = round(sum(ats_breakdown.values()) / len(ats_breakdown))
        confidence_level = "High" if ats_score >= 78 else "Medium" if ats_score >= 55 else "Low"

        skills_analysis = [
            {
                "skill": keyword,
                "category": self._skill_category(keyword),
                "found": keyword in matched,
                "match_percentage": 90 if keyword in matched else 15,
                "feedback": (
                    f"The resume includes {keyword}, which supports the job requirement."
                    if keyword in matched
                    else f"The job description asks for {keyword}, but the resume does not show evidence of it."
                ),
                "recommendation": (
                    f"Keep {keyword} visible in the skills and project sections."
                    if keyword in matched
                    else f"Add {keyword} only if it is a real skill, and connect it to a project or role bullet."
                ),
            }
            for keyword in (matched + missing)[:12]
        ]

        if not skills_analysis:
            skills_analysis.append(
                {
                    "skill": "Role-specific technical skills",
                    "category": "Tools",
                    "found": False,
                    "match_percentage": 0,
                    "feedback": "The job description did not expose clear technical keywords for comparison.",
                    "recommendation": "Paste a complete job description with required skills for a stronger analysis.",
                }
            )

        project_name = self._first_project_name(resume_text)
        return self._normalize_response(
            {
                "ats_score": ats_score,
                "match_percentage": ats_score,
                "resume_match_percentage": ats_score,
                "job_match_percentage": keyword_score,
                "hiring_confidence": {
                    "level": confidence_level,
                    "explanation": f"Confidence is {confidence_level.lower()} because the resume matches {len(matched)} role keywords and misses {len(missing)} important requirements.",
                },
                "overall_feedback": "The resume has relevant signals, but the strongest improvement areas are keyword alignment, measurable impact, and role-specific project evidence.",
                "executive_summary": f"The resume was reviewed against the supplied job description. It matches {', '.join(matched[:5]) or 'limited explicit keywords'} and misses {', '.join(missing[:5]) or 'few obvious keywords'}.",
                "recruiter_decision": {
                    "status": "Shortlist" if ats_score >= 75 else "Hold" if ats_score >= 55 else "Reject",
                    "reason": "The decision is based on the visible alignment between resume evidence, job requirements, quantified achievements, and missing sections.",
                },
                "resume_strengths": self._fallback_strengths(resume_lower, matched),
                "resume_weaknesses": self._fallback_weaknesses(missing, missing_sections, has_metrics),
                "hiring_risks": self._fallback_weaknesses(missing, missing_sections, has_metrics)[:3],
                "matched_keywords": matched[:15],
                "missing_keywords": missing[:15],
                "extra_skills": extra[:10],
                "keyword_analysis": f"The resume matches {len(matched)} extracted job keywords and misses {len(missing)}. Missing terms should be added only where they reflect real experience.",
                "semantic_relevance": "The fallback analysis estimates relevance from extracted skills, project signals, section presence, and measurable impact language.",
                "skills_analysis": skills_analysis,
                "skills_matrix": self._build_skills_matrix(resume_keywords, job_keywords),
                "skill_gap": self._build_skill_gap(missing),
                "experience_analysis": [
                    {
                        "company": "Experience section" if "experience" in resume_lower else "No clear company detected",
                        "role": "Technical candidate profile",
                        "positive_points": ["The resume includes technical evidence relevant to the target role."] if matched else ["The resume provides text that can be reviewed against the job description."],
                        "negative_points": ["Experience bullets need stronger measurable outcomes."],
                        "missing_points": ["Add scope, ownership, users, performance, revenue, or operational impact for each major role."],
                        "weak_bullets": ["Bullets that only list responsibilities without measurable results are weaker for recruiters."],
                        "rewritten_examples": [
                            f"Developed {matched[0] if matched else 'role-relevant'} features for a production system, improving reliability, speed, or user workflow with measurable outcomes."
                        ],
                    }
                ],
                "project_analysis": [
                    {
                        "project_name": project_name,
                        "complexity_score": projects_score,
                        "business_value": "The project section needs clearer business value and user impact." if "project" in resume_lower else "No clear project section was detected.",
                        "technical_depth": f"Technical depth is strongest where the resume mentions {', '.join(matched[:4]) or 'specific implementation details'}.",
                        "architecture_quality": "Architecture details should explain APIs, data model, authentication, deployment, or integrations where relevant.",
                        "technologies": matched[:6],
                        "missing_features": missing[:5],
                        "recruiter_impression": "Recruiters will understand the stack faster if each project states the problem, contribution, and measurable result.",
                        "industry_relevance": "Industry relevance depends on tying the project to the target role responsibilities.",
                        "good_points": ["The project evidence includes role-relevant technology."] if matched else ["The resume has space to build stronger project evidence."],
                        "missing_points": ["Add measurable impact, architecture, users, and deployment details."],
                        "ats_feedback": "Project keywords should mirror the job description where the experience is truthful.",
                        "recommended_changes": ["Rewrite project bullets in problem-action-result format with technologies and outcomes."],
                        "rewritten_description": f"Developed {project_name} using {', '.join(matched[:3]) or 'a role-relevant technical stack'} to solve a clear user problem, implementing core workflows and documenting measurable impact.",
                    }
                ],
                "education_analysis": {
                    "summary": "Education is present." if "education" in resume_lower else "No clear education section was detected in the extracted resume text.",
                    "recommendations": ["Keep education concise and include degree, institution, graduation year, and relevant coursework only if useful for the target role."],
                },
                "grammar_analysis": [
                    {
                        "issue": "Impact wording is not consistently quantified." if not has_metrics else "Grammar appears generally professional from extracted text.",
                        "reason": "Recruiters scan for outcomes, not only responsibilities.",
                        "fix": "Use action verbs followed by scope and measurable results.",
                    }
                ],
                "formatting_analysis": [
                    {
                        "issue": "Missing or unclear sections: " + ", ".join(missing_sections) if missing_sections else "Section structure appears readable from extracted text.",
                        "impact": "ATS and recruiters may miss important evidence if sections are unclear.",
                        "recommendation": "Use standard headings such as Summary, Skills, Experience, Projects, Education, Certifications, and Links.",
                    }
                ],
                "ats_breakdown": ats_breakdown,
                "critical_issues": self._fallback_weaknesses(missing, missing_sections, has_metrics)[:2],
                "high_priority_changes": [f"Add evidence for missing target skills: {', '.join(missing[:5])}."] if missing else ["Make the strongest role-aligned evidence easier to scan."],
                "medium_priority_changes": ["Rewrite project and experience bullets with STAR or problem-action-result structure."],
                "minor_improvements": ["Tighten wording and remove repeated skills or vague phrases."],
                "missing_sections": missing_sections,
                "detailed_improvement_plan": self._fallback_improvement_plan(missing, missing_sections, matched),
                "action_plan": self._fallback_action_plan(missing),
                "top_recommendations": ["Tailor the summary, skills, and projects to the uploaded job description.", "Quantify achievements with numbers, scale, and outcomes.", "Add missing keywords only where they reflect real experience."],
                "improved_resume_bullets": [
                    f"Built and improved {project_name} using {', '.join(matched[:3]) or 'role-relevant technologies'}, with clear ownership, architecture details, and measurable user impact."
                ],
                "learning_roadmap": self._build_learning_roadmap(missing),
                "interview_questions": self._build_interview_questions(matched, missing),
                "recruiter_feedback": {
                    "hr_feedback": "The resume needs a clearer shortlist story: target role, strongest skills, and measurable impact.",
                    "technical_lead_feedback": "Technical evidence should include architecture decisions, tradeoffs, debugging, testing, and deployment details.",
                    "engineering_manager_feedback": "The resume should better show ownership, collaboration, delivery scope, and business outcomes.",
                },
                "final_summary": "This report was generated from the uploaded resume and job description. The next best step is to rewrite the weakest bullets and add evidence for missing role requirements.",
            },
            resume_text,
            job_description,
        )

    def _ensure_required_content(
        self,
        payload: dict[str, Any],
        resume_text: str,
        job_description: str,
    ) -> dict[str, Any]:
        fallback = self._build_resume_specific_analysis(resume_text, job_description) if self._has_empty_required_lists(payload) else {}
        merged = dict(payload)
        for key, value in fallback.items():
            if key in REQUIRED_LIST_FIELDS and not merged.get(key):
                merged[key] = value
        for key in ["overall_feedback", "executive_summary", "final_summary", "keyword_analysis", "semantic_relevance"]:
            if not merged.get(key) and fallback.get(key):
                merged[key] = fallback[key]
        if not merged.get("resume_strengths") and fallback.get("resume_strengths"):
            merged["resume_strengths"] = fallback["resume_strengths"]
        if not merged.get("resume_weaknesses") and fallback.get("resume_weaknesses"):
            merged["resume_weaknesses"] = fallback["resume_weaknesses"]
        if not merged.get("recruiter_feedback", {}).get("hr_feedback") and fallback.get("recruiter_feedback"):
            merged["recruiter_feedback"] = fallback["recruiter_feedback"]
        return self._normalize_response(merged, resume_text, job_description)

    def _has_empty_required_lists(self, payload: dict[str, Any]) -> bool:
        return any(not payload.get(field) for field in REQUIRED_LIST_FIELDS)

    def _extract_keywords(self, text: str) -> list[str]:
        normalized = re.sub(r"[^a-z0-9+/.#-]+", " ", text.lower())
        tokens = [token.strip("./#-") for token in normalized.split() if token.strip("./#-")]
        keywords = []
        known = set().union(*SKILL_CATEGORIES.values())
        for token in tokens:
            if len(token) < 2 or token in STOP_WORDS:
                continue
            if token in known or token.endswith(("js", "sql", "api")):
                keywords.append(token)
        counts = Counter(keywords)
        return [keyword for keyword, _ in counts.most_common(25)]

    def _detect_missing_sections(self, resume_lower: str) -> list[str]:
        checks = {
            "Professional Summary": ["summary", "profile", "objective"],
            "Projects": ["project", "projects"],
            "Experience": ["experience", "employment", "intern", "developer", "engineer"],
            "Education": ["education", "degree", "bachelor", "master", "university", "college"],
            "Achievements": ["achievement", "award", "honor", "accomplishment"],
            "Certifications": ["certification", "certificate", "certified"],
            "Links": ["github", "linkedin", "portfolio"],
        }
        return [section for section, terms in checks.items() if not any(term in resume_lower for term in terms)]

    def _fallback_strengths(self, resume_lower: str, matched: list[str]) -> list[str]:
        strengths = []
        if matched:
            strengths.append(f"The resume includes role-aligned keywords such as {', '.join(matched[:4])}.")
        if any(verb in resume_lower for verb in ["built", "developed", "implemented", "designed", "created"]):
            strengths.append("The resume uses implementation-oriented action verbs.")
        if "project" in resume_lower:
            strengths.append("The resume includes project evidence that can be improved for stronger recruiter impact.")
        return strengths or ["The resume provides enough extracted text for a role-specific review."]

    def _fallback_weaknesses(self, missing: list[str], missing_sections: list[str], has_metrics: bool) -> list[str]:
        weaknesses = []
        if missing:
            weaknesses.append(f"The resume does not clearly show these job requirements: {', '.join(missing[:5])}.")
        if missing_sections:
            weaknesses.append(f"The resume appears to be missing or under-labeling: {', '.join(missing_sections[:4])}.")
        if not has_metrics:
            weaknesses.append("The resume needs more quantified achievements and business impact.")
        return weaknesses or ["The resume can still improve by making role-fit evidence more direct."]

    def _fallback_improvement_plan(self, missing: list[str], missing_sections: list[str], matched: list[str]) -> list[dict[str, str]]:
        missing_text = ", ".join(missing[:4]) or "the most important job-description skills"
        matched_text = ", ".join(matched[:3]) or "the candidate's strongest technical skills"
        return [
            {
                "section": "Professional Summary",
                "current_problem": "The opening summary does not fully connect the resume to the uploaded job description.",
                "why_it_matters": "Recruiters use the first few lines to decide whether the candidate matches the role.",
                "recommended_change": f"Write a 2-3 line summary naming the target role, {matched_text}, and one measurable outcome.",
                "example_before": "Software developer with experience in web development.",
                "example_after": f"Software developer with hands-on experience in {matched_text}, building role-relevant applications and improving reliability, usability, or delivery speed.",
                "priority": "High",
            },
            {
                "section": "Skills",
                "current_problem": f"The resume does not clearly show {missing_text}.",
                "why_it_matters": "ATS systems and recruiters compare the skills section directly against job requirements.",
                "recommended_change": "Add missing skills only where they are truthful, then support them in projects or experience bullets.",
                "example_before": "Skills: Programming, Web Development",
                "example_after": f"Skills: {matched_text}; add {missing_text} only with real project evidence.",
                "priority": "High",
            },
            {
                "section": "Projects",
                "current_problem": "Project descriptions need stronger business value, architecture, and measurable impact.",
                "why_it_matters": "Projects are often the strongest evidence for junior or transition candidates.",
                "recommended_change": "Rewrite each project with problem, stack, architecture, responsibility, and outcome.",
                "example_before": "Built Employee Management System using Spring Boot.",
                "example_after": "Developed a scalable Employee Management System using Spring Boot, REST APIs, authentication, and a relational database to streamline employee records and reduce manual tracking effort.",
                "priority": "High",
            },
            {
                "section": "Missing Sections",
                "current_problem": f"Missing or unclear sections: {', '.join(missing_sections[:5]) or 'none detected'}.",
                "why_it_matters": "Standard headings help ATS parsers and recruiters find evidence quickly.",
                "recommended_change": "Add concise standard sections for missing areas and avoid graphics-heavy formatting.",
                "example_before": "Information scattered across the resume.",
                "example_after": "Summary | Skills | Experience | Projects | Education | Certifications | Links",
                "priority": "Medium",
            },
        ]

    def _fallback_action_plan(self, missing: list[str]) -> list[dict[str, Any]]:
        return [
            {
                "step": 1,
                "title": "Rewrite the first screen of the resume",
                "description": "Update the summary and skills section to mirror the most important job requirements.",
                "expected_result": "Recruiters immediately understand the candidate's role fit.",
            },
            {
                "step": 2,
                "title": "Upgrade project and experience bullets",
                "description": "Use action, technology, scope, and measurable result in each priority bullet.",
                "expected_result": "The resume shows evidence instead of responsibility-only claims.",
            },
            {
                "step": 3,
                "title": "Close the skill gaps",
                "description": f"Build or document evidence for {', '.join(missing[:4]) or 'the missing target skills'}.",
                "expected_result": "ATS keyword coverage and technical interview readiness improve.",
            },
        ]

    def _build_skills_matrix(self, resume_keywords: list[str], job_keywords: list[str]) -> list[dict[str, Any]]:
        rows = []
        for category, skills in SKILL_CATEGORIES.items():
            current = [skill for skill in resume_keywords if skill in skills]
            required = [skill for skill in job_keywords if skill in skills]
            if current or required:
                rows.append(
                    {
                        "category": category,
                        "current_skills": current,
                        "required_skills": required,
                        "missing_skills": [skill for skill in required if skill not in current],
                        "outdated_skills": [],
                        "repeated_skills": [],
                        "feedback": f"{category} alignment is based on the resume and job-description keywords.",
                    }
                )
        return rows or [
            {
                "category": "Tools",
                "current_skills": resume_keywords[:5],
                "required_skills": job_keywords[:5],
                "missing_skills": [skill for skill in job_keywords[:5] if skill not in resume_keywords],
                "outdated_skills": [],
                "repeated_skills": [],
                "feedback": "Skill grouping is limited because few known skills were extracted.",
            }
        ]

    def _build_skill_gap(self, missing: list[str]) -> list[dict[str, str]]:
        gaps = missing[:8] or ["Role-specific skill evidence"]
        return [
            {
                "skill": skill,
                "current_evidence": "Not clearly visible in the extracted resume text.",
                "required_level": "Required or preferred by the uploaded job description.",
                "learning_priority": "High" if index < 3 else "Medium",
                "recommendation": f"Add {skill} to the resume only after building truthful project or work evidence.",
            }
            for index, skill in enumerate(gaps)
        ]

    def _build_learning_roadmap(self, missing: list[str]) -> list[dict[str, str]]:
        roadmap_skills = missing[:5] or ["Missing role-specific skills"]
        return [
            {
                "skill": skill,
                "priority": "High" if index < 2 else "Medium",
                "plan": f"Build a small project or documented feature using {skill}, then add one evidence-based bullet to the resume.",
                "expected_outcome": f"The candidate can discuss {skill} with concrete implementation details in interviews.",
            }
            for index, skill in enumerate(roadmap_skills)
        ]

    def _build_interview_questions(self, matched: list[str], missing: list[str]) -> list[dict[str, str]]:
        focus = (matched + missing)[:8] or ["your most relevant project"]
        questions = [
            {
                "question": f"How have you used {skill} in a real project or work setting?",
                "why_asked": f"The job description or resume analysis surfaced {skill} as a role-relevant topic.",
                "preparation_hint": "Prepare a STAR answer with architecture, tradeoffs, debugging, and measurable outcome.",
            }
            for skill in focus
        ]
        while len(questions) < 15:
            questions.append(
                {
                    "question": "Walk me through the most technically complex project on your resume.",
                    "why_asked": "Hiring teams need to validate ownership, depth, and decision-making.",
                    "preparation_hint": "Explain the problem, design choices, implementation details, testing, deployment, and result.",
                }
            )
        return questions[:15]

    def _first_project_name(self, resume_text: str) -> str:
        for line in resume_text.splitlines():
            if "project" in line.lower() and len(line.strip()) <= 80:
                return line.strip(": -")
        return "Resume project evidence"

    def _skill_category(self, skill: str) -> str:
        lowered = skill.lower()
        for category, skills in SKILL_CATEGORIES.items():
            if lowered in skills:
                return category
        return "Tools"

    def _normalize_skills_analysis(self, value: Any) -> list[dict[str, Any]]:
        rows = []
        for item in self._dict_items(value)[:20]:
            skill = self._coerce_text(item.get("skill"))
            if skill:
                rows.append(
                    {
                        "skill": skill,
                        "category": self._coerce_text(item.get("category")) or self._skill_category(skill),
                        "found": bool(item.get("found")),
                        "match_percentage": self._clamp_score(item.get("match_percentage")),
                        "feedback": self._coerce_text(item.get("feedback")),
                        "recommendation": self._coerce_text(item.get("recommendation")),
                    }
                )
        return rows

    def _normalize_skills_matrix(self, value: Any) -> list[dict[str, Any]]:
        return [
            {
                "category": self._coerce_text(item.get("category")),
                "current_skills": self._coerce_string_list(item.get("current_skills")),
                "required_skills": self._coerce_string_list(item.get("required_skills")),
                "missing_skills": self._coerce_string_list(item.get("missing_skills")),
                "outdated_skills": self._coerce_string_list(item.get("outdated_skills")),
                "repeated_skills": self._coerce_string_list(item.get("repeated_skills")),
                "feedback": self._coerce_text(item.get("feedback")),
            }
            for item in self._dict_items(value)[:10]
        ]

    def _normalize_skill_gap(self, value: Any) -> list[dict[str, str]]:
        return [
            {
                "skill": self._coerce_text(item.get("skill")),
                "current_evidence": self._coerce_text(item.get("current_evidence")),
                "required_level": self._coerce_text(item.get("required_level")),
                "learning_priority": self._coerce_text(item.get("learning_priority")),
                "recommendation": self._coerce_text(item.get("recommendation")),
            }
            for item in self._dict_items(value)[:10]
        ]

    def _normalize_experience_analysis(self, value: Any) -> list[dict[str, Any]]:
        return [
            {
                "company": self._coerce_text(item.get("company")),
                "role": self._coerce_text(item.get("role")),
                "ownership": self._coerce_text(item.get("ownership")),
                "leadership": self._coerce_text(item.get("leadership")),
                "business_impact": self._coerce_text(item.get("business_impact")),
                "technical_responsibility": self._coerce_text(item.get("technical_responsibility")),
                "code_quality": self._coerce_text(item.get("code_quality")),
                "testing": self._coerce_text(item.get("testing")),
                "deployment": self._coerce_text(item.get("deployment")),
                "collaboration": self._coerce_text(item.get("collaboration")),
                "problem_solving": self._coerce_text(item.get("problem_solving")),
                "architecture_knowledge": self._coerce_text(item.get("architecture_knowledge")),
                "positive_points": self._coerce_string_list(item.get("positive_points") or item.get("strengths")),
                "negative_points": self._coerce_string_list(item.get("negative_points") or item.get("weaknesses")),
                "missing_points": self._coerce_string_list(item.get("missing_points")),
                "weak_bullets": self._coerce_string_list(item.get("weak_bullets")),
                "rewritten_examples": self._coerce_string_list(item.get("rewritten_examples") or item.get("recommendations")),
            }
            for item in self._dict_items(value)[:8]
        ]

    def _normalize_project_analysis(self, value: Any) -> list[dict[str, Any]]:
        return [
            {
                "project_name": self._coerce_text(item.get("project_name")),
                "complexity_score": self._clamp_score(item.get("complexity_score")),
                "architecture_score": self._clamp_score(item.get("architecture_score")),
                "security_score": self._clamp_score(item.get("security_score")),
                "business_value": self._coerce_text(item.get("business_value")),
                "technical_depth": self._coerce_text(item.get("technical_depth")),
                "architecture_quality": self._coerce_text(item.get("architecture_quality")),
                "database_design": self._coerce_text(item.get("database_design")),
                "scalability": self._coerce_text(item.get("scalability")),
                "difficulty_level": self._coerce_text(item.get("difficulty_level")),
                "production_readiness": self._coerce_text(item.get("production_readiness")),
                "technologies": self._coerce_string_list(item.get("technologies")),
                "missing_features": self._coerce_string_list(item.get("missing_features")),
                "architecture_improvements": self._coerce_string_list(item.get("architecture_improvements")),
                "suggested_technologies": self._coerce_string_list(item.get("suggested_technologies")),
                "business_impact": self._coerce_text(item.get("business_impact")),
                "real_recruiter_feedback": self._coerce_text(item.get("real_recruiter_feedback")),
                "interview_questions": self._coerce_string_list(item.get("interview_questions"))[:10],
                "recruiter_impression": self._coerce_text(item.get("recruiter_impression")),
                "industry_relevance": self._coerce_text(item.get("industry_relevance")),
                "good_points": self._coerce_string_list(item.get("good_points")),
                "missing_points": self._coerce_string_list(item.get("missing_points")),
                "ats_feedback": self._coerce_text(item.get("ats_feedback")),
                "recommended_changes": self._coerce_string_list(item.get("recommended_changes") or item.get("recommendations")),
                "rewritten_description": self._coerce_text(item.get("rewritten_description")),
            }
            for item in self._dict_items(value)[:8]
        ]

    def _normalize_education_analysis(self, value: Any) -> dict[str, Any]:
        if isinstance(value, dict):
            return {
                "summary": self._coerce_text(value.get("summary")),
                "recommendations": self._coerce_string_list(value.get("recommendations")),
            }
        return {"summary": self._coerce_text(value), "recommendations": []}

    def _normalize_issue_fix_list(self, value: Any) -> list[dict[str, str]]:
        return [
            {
                "issue": self._coerce_text(item.get("issue")),
                "reason": self._coerce_text(item.get("reason")),
                "fix": self._coerce_text(item.get("fix")),
            }
            for item in self._dict_items(value)[:12]
        ]

    def _normalize_formatting_list(self, value: Any) -> list[dict[str, str]]:
        return [
            {
                "issue": self._coerce_text(item.get("issue")),
                "impact": self._coerce_text(item.get("impact")),
                "recommendation": self._coerce_text(item.get("recommendation")),
            }
            for item in self._dict_items(value)[:12]
        ]

    def _normalize_ats_breakdown(self, value: Any) -> dict[str, int]:
        value = value if isinstance(value, dict) else {}
        return {
            "formatting": self._clamp_score(value.get("formatting")),
            "projects": self._clamp_score(value.get("projects")),
            "experience": self._clamp_score(value.get("experience")),
            "skills": self._clamp_score(value.get("skills")),
            "education": self._clamp_score(value.get("education")),
            "keywords": self._clamp_score(value.get("keywords")),
            "impact": self._clamp_score(value.get("impact")),
            "readability": self._clamp_score(value.get("readability")),
            "grammar": self._clamp_score(value.get("grammar")),
            "achievements": self._clamp_score(value.get("achievements")),
        }

    def _normalize_ats_breakdown_details(self, value: Any) -> list[dict[str, Any]]:
        return [
            {
                "category": self._coerce_text(item.get("category")),
                "score": self._clamp_score(item.get("score")),
                "reason": self._coerce_text(item.get("reason")),
            }
            for item in self._dict_items(value)[:12]
        ]

    def _normalize_improvement_plan(self, value: Any) -> list[dict[str, str]]:
        return [
            {
                "section": self._coerce_text(item.get("section")),
                "current_problem": self._coerce_text(item.get("current_problem")),
                "why_it_matters": self._coerce_text(item.get("why_it_matters")),
                "recommended_change": self._coerce_text(item.get("recommended_change")),
                "example_before": self._coerce_text(item.get("example_before")),
                "example_after": self._coerce_text(item.get("example_after") or item.get("example")),
                "priority": self._coerce_text(item.get("priority"), "High"),
            }
            for item in self._dict_items(value)[:12]
        ]

    def _normalize_action_plan(self, value: Any) -> list[dict[str, Any]]:
        return [
            {
                "step": self._coerce_int(item.get("step"), index + 1),
                "title": self._coerce_text(item.get("title")),
                "description": self._coerce_text(item.get("description")),
                "expected_result": self._coerce_text(item.get("expected_result") or item.get("expected_impact")),
            }
            for index, item in enumerate(self._dict_items(value)[:8])
        ]

    def _normalize_learning_roadmap(self, value: Any) -> list[dict[str, str]]:
        return [
            {
                "skill": self._coerce_text(item.get("skill")),
                "priority": self._coerce_text(item.get("priority")),
                "plan": self._coerce_text(item.get("plan")),
                "expected_outcome": self._coerce_text(item.get("expected_outcome")),
            }
            for item in self._dict_items(value)[:10]
        ]

    def _normalize_interview_questions(self, value: Any) -> list[dict[str, str]]:
        questions = [
            {
                "question": self._coerce_text(item.get("question")),
                "why_asked": self._coerce_text(item.get("why_asked")),
                "preparation_hint": self._coerce_text(item.get("preparation_hint")),
            }
            for item in self._dict_items(value)[:15]
        ]
        seen = set()
        unique_questions = []
        for item in questions:
            normalized_question = item["question"].strip().lower()
            if normalized_question and normalized_question not in seen:
                seen.add(normalized_question)
                unique_questions.append(item)
        return unique_questions

    def _normalize_recruiter_simulation(self, value: Any) -> list[dict[str, Any]]:
        return [
            {
                "reviewer": self._coerce_text(item.get("reviewer")),
                "what_impressed_them": self._coerce_string_list(item.get("what_impressed_them")),
                "concerns": self._coerce_string_list(item.get("concerns")),
                "questions": self._coerce_string_list(item.get("questions"))[:6],
                "would_shortlist": self._coerce_text(item.get("would_shortlist")),
                "would_hire": self._coerce_text(item.get("would_hire")),
            }
            for item in self._dict_items(value)[:3]
        ]

    def _normalize_architecture_analysis(self, value: Any) -> dict[str, Any]:
        value = value if isinstance(value, dict) else {}
        return {
            "detected": self._normalize_architecture_signals(value.get("detected")),
            "missing": self._normalize_architecture_signals(value.get("missing")),
            "recommended": self._normalize_architecture_signals(value.get("recommended")),
        }

    def _normalize_architecture_signals(self, value: Any) -> list[dict[str, str]]:
        return [
            {
                "item": self._coerce_text(item.get("item")),
                "detected": self._coerce_text(item.get("detected")),
                "missing": self._coerce_text(item.get("missing")),
                "recommended": self._coerce_text(item.get("recommended")),
            }
            for item in self._dict_items(value)[:12]
        ]

    def _normalize_hiring_decision_details(self, value: Any) -> dict[str, Any]:
        value = value if isinstance(value, dict) else {}
        return {
            "hiring_probability": self._coerce_text(value.get("hiring_probability")),
            "interview_probability": self._coerce_text(value.get("interview_probability")),
            "expected_role": self._coerce_text(value.get("expected_role")),
            "expected_salary_range": self._coerce_text(value.get("expected_salary_range")),
            "expected_experience_level": self._coerce_text(value.get("expected_experience_level")),
            "confidence_level": self._coerce_text(value.get("confidence_level")),
            "reasons": self._coerce_string_list(value.get("reasons")),
            "major_hiring_risks": self._coerce_string_list(value.get("major_hiring_risks")),
            "final_recommendation": self._coerce_text(value.get("final_recommendation")),
        }

    def _normalize_roadmap_phases(self, value: Any) -> dict[str, list[str]]:
        value = value if isinstance(value, dict) else {}
        return {
            "thirty_day": self._coerce_string_list(value.get("thirty_day")),
            "sixty_day": self._coerce_string_list(value.get("sixty_day")),
            "ninety_day": self._coerce_string_list(value.get("ninety_day")),
        }

    def _dict_items(self, value: Any) -> list[dict[str, Any]]:
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        return []

    def _coerce_text(self, value: Any, fallback: str = "") -> str:
        if value is None:
            return fallback
        text = str(value).strip()
        return text or fallback

    def _coerce_int(self, value: Any, fallback: int = 0) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return fallback

    def _clamp_score(self, value: Any, fallback: int = 0) -> int:
        return max(0, min(100, self._coerce_int(value, fallback)))

    def _coerce_string_list(self, value: Any) -> list[str]:
        if isinstance(value, list):
            return [text for text in (self._coerce_text(item) for item in value) if text]
        if isinstance(value, str):
            text = self._coerce_text(value)
            return [text] if text else []
        return []
