import json
import re
import time
import random
from typing import Any

from services.llm_service import client, MODEL_NAME


def extract_json(text: str) -> dict:
    """
    Extract a JSON object from Gemini output.
    """

    text = text.strip()

    text = re.sub(
        r"```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"```\s*",
        "",
        text
    )

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError(
            "No JSON object found in Gemini response."
        )

    return json.loads(
        text[start:end + 1]
    )


def _score_label(score: float) -> str:

    if score >= 8:
        return "Strongly demonstrated"

    if score >= 6:
        return "Moderately demonstrated"

    if score >= 4:
        return "Requires further verification"

    return "Weak demonstration"

def _generate_with_retry(
    prompt: str,
    max_retries: int = 3
):
    """
    Call Gemini with retry logic for temporary
    503/429/5xx service errors.
    """

    for attempt in range(max_retries + 1):

        try:
            print(
                f"Gemini evaluation attempt "
                f"{attempt + 1}/{max_retries + 1}"
            )

            return client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

        except Exception as error:

            error_text = str(error)

            is_retryable = any(
                code in error_text
                for code in [
                    "503",
                    "UNAVAILABLE",
                    "429",
                    "RESOURCE_EXHAUSTED",
                    "500",
                    "INTERNAL",
                    "502",
                    "BAD_GATEWAY",
                    "504",
                    "DEADLINE_EXCEEDED"
                ]
            )

            if not is_retryable:
                raise

            if attempt >= max_retries:
                raise

            delay = (2 ** attempt) + random.uniform(0, 1)

            print(
                f"Gemini temporarily unavailable. "
                f"Retrying in {delay:.1f} seconds..."
            )

            time.sleep(delay)


def evaluate_assessment_batch(
    assessments: list[dict[str, Any]]
) -> dict:
    """
    Evaluate all assessment questions in ONE Gemini request.

    This replaces one-API-call-per-question evaluation.
    """

    if not assessments:
        return {
            "skills": [],
            "overall_score": 0,
            "overall_evaluation": "No assessment data"
        }

    assessment_text = []

    question_id = 1

    for assessment in assessments:

        skill = assessment.get("skill", "")
        evidence = assessment.get("evidence", [])
        questions = assessment.get("questions", [])

        evidence_text = "\n".join(
            f"- {item}"
            for item in evidence[:5]
        )

        assessment_text.append(
            f"""
SKILL: {skill}

RESUME EVIDENCE:
{evidence_text}

QUESTIONS AND ANSWERS:
"""
        )

        for item in questions:

            assessment_text.append(
                f"""
QUESTION_ID: {question_id}
QUESTION: {item.get("question", "")}
ANSWER: {item.get("answer", "")}
"""
            )

            question_id += 1

    prompt = f"""
You are an expert technical interviewer evaluating a candidate.

This is a resume-grounded technical skill verification system.

Evaluate ALL questions and answers below in ONE pass.

Do not reward keyword matching alone.

A technically impressive answer must demonstrate actual understanding.

For every question evaluate:

1. Relevance
2. Technical correctness
3. Detail and reasoning
4. Alignment with resume evidence

Each dimension must receive a score from 0 to 10.

Use:

overall_question_score =
(relevance * 0.30) +
(technical_correctness * 0.35) +
(detail * 0.15) +
(evidence_alignment * 0.20)

Round to one decimal place.

Then calculate the skill score as the average of that
skill's question scores.

Evaluation labels:

8.0 - 10.0 = Strongly demonstrated
6.0 - 7.9 = Moderately demonstrated
4.0 - 5.9 = Requires further verification
0.0 - 3.9 = Weak demonstration

IMPORTANT:

An empty answer must receive zero scores.

Do not assume a candidate knows something simply because
the resume lists the skill.

Give concise but useful feedback.

For every skill also provide:

- strengths
- areas_to_verify

Return ONLY valid JSON.

Required structure:

{{
    "skills": [
        {{
            "skill": "Machine Learning",
            "questions": [
                {{
                    "question": "...",
                    "relevance_score": 0,
                    "technical_correctness_score": 0,
                    "detail_score": 0,
                    "evidence_alignment_score": 0,
                    "overall_score": 0,
                    "overall_evaluation": "",
                    "feedback": ""
                }}
            ],
            "overall_score": 0,
            "overall_evaluation": "",
            "strengths": [],
            "areas_to_verify": []
        }}
    ]
}}

Here is the assessment:

{"".join(assessment_text)}
"""

    try:

        response = _generate_with_retry(
            prompt
        )

        result = extract_json(
            response.text
            )

        skills = result.get(
            "skills",
            []
        )

        total_scores = []

        for skill_result in skills:

            score = float(
                skill_result.get(
                    "overall_score",
                    0
                )
            )

            skill_result["overall_score"] = round(
                score,
                1
            )

            skill_result["overall_evaluation"] = (
                skill_result.get(
                    "overall_evaluation"
                )
                or _score_label(score)
            )

            total_scores.append(
                score
            )

        overall_score = (
            round(
                sum(total_scores) /
                len(total_scores),
                1
            )
            if total_scores
            else 0
        )

        return {
            "skills": skills,
            "overall_score": overall_score,
            "overall_evaluation": _score_label(
                overall_score
            )
        }

    except Exception as error:

        print(
            f"Batch AI evaluation error: {error}"
        )

        return {
            "skills": [],
            "overall_score": 0,
            "overall_evaluation": "Evaluation unavailable",
            "error": str(error)
        }


# -----------------------------------------
# Backward-compatible single-answer evaluator
# -----------------------------------------

def evaluate_answer(
    skill: str,
    answer: str,
    question: str = "",
    evidence: list[str] | None = None
) -> dict:
    """
    Compatibility wrapper for the older endpoint.
    """

    if evidence is None:
        evidence = []

    result = evaluate_assessment_batch(
        [
            {
                "skill": skill,
                "evidence": evidence,
                "questions": [
                    {
                        "question": question,
                        "answer": answer
                    }
                ]
            }
        ]
    )

    if not result.get("skills"):
        return {
            "skill": skill,
            "answer": answer,
            "relevance_score": 0,
            "technical_correctness_score": 0,
            "detail_score": 0,
            "evidence_alignment_score": 0,
            "overall_score": 0,
            "overall_evaluation": "Evaluation unavailable",
            "feedback": "AI evaluation could not be completed."
        }

    skill_result = result["skills"][0]

    question_result = (
        skill_result.get("questions", [{}])[0]
    )

    return {
        "skill": skill,
        "answer": answer,
        "relevance_score": question_result.get(
            "relevance_score",
            0
        ),
        "technical_correctness_score": question_result.get(
            "technical_correctness_score",
            0
        ),
        "detail_score": question_result.get(
            "detail_score",
            0
        ),
        "evidence_alignment_score": question_result.get(
            "evidence_alignment_score",
            0
        ),
        "overall_score": question_result.get(
            "overall_score",
            0
        ),
        "overall_evaluation": question_result.get(
            "overall_evaluation",
            "Evaluation unavailable"
        ),
        "feedback": question_result.get(
            "feedback",
            ""
        )
    }