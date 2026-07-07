from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from models.response_models import AnalysisResponse, ErrorResponse
from services.gemini_service import GeminiService
from services.pdf_service import extract_text_from_resume

router = APIRouter(tags=["analysis"])


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}, 502: {"model": ErrorResponse}},
)
async def analyze_resume(
    resume: UploadFile = File(...),
    jobDescription: str = Form(...),
) -> AnalysisResponse:
    """Analyze a resume document against a job description using Gemini."""
    if not resume:
        raise HTTPException(status_code=400, detail="Resume file is required.")

    if not jobDescription or not jobDescription.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")

    try:
        print(f"Received upload: filename={resume.filename}, content_type={resume.content_type}")
        resume_text = await extract_text_from_resume(resume)
        if not resume_text.strip():
            raise HTTPException(status_code=400, detail="Unable to extract text from the uploaded resume.")
        print(f"Sending extracted resume text to Gemini (characters={len(resume_text)}).")
        gemini_service = GeminiService()
        analysis = gemini_service.analyze_resume(resume_text, jobDescription.strip())
        return AnalysisResponse(**analysis)
    except HTTPException as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unexpected error while analyzing the resume.") from exc
