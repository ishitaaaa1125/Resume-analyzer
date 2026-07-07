from services.gemini_service import GeminiService


def test_normalize_response_keeps_recruiter_fields():
    service = GeminiService.__new__(GeminiService)
    payload = {
        "ats_score": 72,
        "overall_feedback": "Strong fit",
        "executive_summary": "Strong backend engineer",
        "matched_keywords": ["python", "fastapi"],
        "missing_keywords": ["docker", "aws"],
        "skills_analysis": [{"skill": "Python", "found": True, "match_percentage": 90, "feedback": "Good"}],
        "experience_analysis": [{"company": "Acme", "role": "Backend Engineer", "strengths": ["Built APIs"], "weaknesses": ["Needs metrics"], "recommendations": ["Add impact"]}],
        "project_analysis": [{"project_name": "Invoice API", "technologies": ["Python", "FastAPI"], "good_points": ["Clear scope"], "missing_points": ["No metrics"], "recommendations": ["Add KPI"]}],
        "education_analysis": {"summary": "BSc CS", "recommendations": ["Keep concise"]},
        "grammar_analysis": {"issues": [], "recommendations": ["Keep bullets concise"]},
        "formatting_analysis": {"issues": ["Needs section headings"], "recommendations": ["Use cleaner layout"]},
        "ats_breakdown": {"skills": 80, "experience": 70, "projects": 75, "education": 60, "keywords": 72, "formatting": 65},
        "missing_sections": ["Certifications"],
        "high_priority_changes": ["Add metrics"],
        "medium_priority_changes": ["Improve project bullets"],
        "low_priority_changes": ["Tighten summary"],
        "resume_strengths": ["Strong backend work"],
        "resume_weaknesses": ["No quantified metrics"],
        "improvement_plan": [{"section": "Projects", "current_problem": "Thin details", "recommended_change": "Add metrics", "example": "Built an API that reduced latency by 30%"}],
        "top_recommendations": ["Quantify achievements"],
        "recruiter_decision": {"status": "review", "reason": "Good fit but needs tailoring"},
        "resume_highlights": ["Built APIs"],
        "resume_red_flags": ["Missing metrics"],
        "final_recommendations": ["Quantify achievements"],
    }

    normalized = service._normalize_response(payload)

    assert normalized["recruiter_decision"]["status"] == "review"
    assert normalized["resume_highlights"] == ["Built APIs"]
    assert normalized["resume_red_flags"] == ["Missing metrics"]
    assert normalized["final_recommendations"] == ["Quantify achievements"]
