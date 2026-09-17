import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from models.assessment import AssessmentRequest

from services.resume_service import extract_text_from_pdf
from services.skill_extractor import extract_skills
from services.skill_normalizer import normalize_skills
from services.section_detector import split_resume_into_sections
from services.evidence_analyzer import analyze_all_skills
from services.candidate_profile import build_candidate_profile
from services.question_generator import (
    generate_assessment_questions,
    generate_technical_lab
)
from services.answer_evaluator import evaluate_answer


app = FastAPI(
    title="VeriSkill API",
    description="AI-powered Resume Skill Verification System",
    version="2.0.0"
)


# ============================================================
# CORS
# ============================================================
FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173"
)

ALLOWED_ORIGINS = [
    FRONTEND_URL,
    "https://veri-skill.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# UPLOADS
# ============================================================

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "Welcome to VeriSkill",
        "status": "API is running",
        "version": "2.0.0"
    }


# ============================================================
# RESUME UPLOAD
# ============================================================

@app.post("/resume/upload")
async def upload_resume(
    file: UploadFile = File(...)
):

    if file.content_type != "application/pdf":

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:

        content = await file.read()

        buffer.write(content)

    # --------------------------------------------------------
    # Extract resume text
    # --------------------------------------------------------

    extracted_text = extract_text_from_pdf(
        str(file_path)
    )

    # --------------------------------------------------------
    # Detect sections
    # --------------------------------------------------------

    sections = split_resume_into_sections(
        extracted_text
    )

    # --------------------------------------------------------
    # Extract skills
    # --------------------------------------------------------

    raw_skills = extract_skills(
        extracted_text
    )

    skills = normalize_skills(
        raw_skills
    )
    candidate_profile = build_candidate_profile(
    sections,
    skills
    )

    # --------------------------------------------------------
    # Analyze evidence
    # --------------------------------------------------------

    skill_evidence = analyze_all_skills(
        skills,
        sections
    )

    # --------------------------------------------------------
    # Rank skills
    # --------------------------------------------------------

    strength_rank = {
        "high": 3,
        "medium": 2,
        "low": 1,
        "none": 0
    }

    ranked_skills = sorted(
        skill_evidence.items(),
        key=lambda item: (
            strength_rank.get(
                item[1].get(
                    "evidence_strength",
                    "none"
                ),
                0
            ),
            item[1].get(
                "evidence_count",
                0
            ),
            len(
                item[1].get(
                    "sources",
                    []
                )
            )
        ),
        reverse=True
    )

    # --------------------------------------------------------
    # Top 5 assessment skills
    # --------------------------------------------------------

    top_skills = ranked_skills[:5]

    assessment_questions = {}

    for skill, evidence_data in top_skills:

        assessment_questions[skill] = (
            generate_assessment_questions(
                skill,
                evidence_data
            )
        )

    # --------------------------------------------------------
    # Return
    # --------------------------------------------------------

    return {

    "filename": file.filename,

    "message": "Resume uploaded successfully",

    "skills": skills,

    "sections": sections,

    "candidate_profile": candidate_profile,

    "skill_evidence": skill_evidence,

    "assessment_questions": assessment_questions,

    "assessment_skills": [
        skill
        for skill, _ in top_skills
    ],

    "extracted_text": extracted_text
}


# ============================================================
# SINGLE ANSWER EVALUATION
# ============================================================

@app.post("/answer/evaluate")
async def evaluate_candidate_answer(
    skill: str,
    answer: str
):

    return evaluate_answer(
        skill,
        answer
    )


# ============================================================
# ROUND 1 EVALUATION
# ============================================================

@app.post("/assessment/evaluate")
async def evaluate_assessment(
    assessment: AssessmentRequest
):

    results = []

    # --------------------------------------------------------
    # Evaluate every question
    # --------------------------------------------------------

    for item in assessment.questions:

        # Empty answers are handled locally.
        # They do NOT stop the assessment.
        if not item.answer.strip():

            result = {
                "skill": assessment.skill,
                "answer": "",
                "relevance_score": 0,
                "technical_correctness_score": 0,
                "detail_score": 0,
                "evidence_alignment_score": 0,
                "overall_score": 0,
                "overall_evaluation": "Weak demonstration",
                "feedback": (
                    "No answer was provided. "
                    "A detailed technical explanation "
                    "would be required for verification."
                )
            }

        else:

            result = evaluate_answer(
                assessment.skill,
                item.answer,
                item.question,
                assessment.evidence
            )

        result["question"] = item.question

        results.append(result)

    # --------------------------------------------------------
    # Overall score
    # --------------------------------------------------------

    if results:

        overall_score = round(
            sum(
                result["overall_score"]
                for result in results
            ) / len(results),
            1
        )

    else:

        overall_score = 0

    # --------------------------------------------------------
    # Evaluation label
    # --------------------------------------------------------

    if overall_score >= 8:

        overall_evaluation = (
            "Strongly demonstrated"
        )

    elif overall_score >= 6:

        overall_evaluation = (
            "Moderately demonstrated"
        )

    elif overall_score >= 4:

        overall_evaluation = (
            "Requires further verification"
        )

    else:

        overall_evaluation = (
            "Weak demonstration"
        )

    # --------------------------------------------------------
    # IMPORTANT:
    # Round 2 is NOT generated here anymore.
    #
    # The frontend will call /technical-lab
    # after Round 1 has completed.
    # --------------------------------------------------------

    return {

        "skill": assessment.skill,

        "questions_evaluated": len(results),

        "overall_score": overall_score,

        "overall_evaluation": overall_evaluation,

        "results": results
    }


# ============================================================
# ROUND 2 — TECHNICAL VERIFICATION LAB
# ============================================================

@app.post("/technical-lab")
async def technical_lab(
    assessment: dict
):

    skills = assessment.get(
        "skills",
        []
    )

    skill_evidence = assessment.get(
        "skill_evidence",
        {}
    )

    questions = generate_technical_lab(
        skills,
        skill_evidence
    )

    return {
        "round": 2,
        "title": "Technical Verification Lab",
        "description": (
            "A practical technical round designed to verify "
            "implementation, coding and problem-solving ability."
        ),
        "questions": questions
    }
