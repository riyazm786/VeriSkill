import json
import re

from services.llm_service import client, MODEL_NAME


def extract_json(text: str) -> dict:

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
            "No JSON object found."
        )

    return json.loads(
        text[start:end + 1]
    )


def evaluate_round2(
    questions: list[dict]
) -> dict:

    results = []

    for item in questions:

        answer = item.get(
            "answer",
            ""
        )

        question = item.get(
            "question",
            ""
        )

        question_type = item.get(
            "type",
            "technical"
        )

        skill = item.get(
            "skill",
            "Unknown"
        )

        if not answer.strip():

            results.append({
                "id": item.get("id"),
                "type": question_type,
                "skill": skill,
                "question": question,
                "score": 0,
                "feedback": "No answer was provided."
            })

            continue

        prompt = f"""
You are an expert technical interviewer.

Evaluate this candidate's Round 2 technical challenge.

QUESTION TYPE:
{question_type}

SKILL:
{skill}

QUESTION:
{question}

CANDIDATE ANSWER:
{answer}

Evaluate based on the question type.

For CODING evaluate:
- correctness
- logic
- edge cases
- efficiency
- implementation quality

For DEBUGGING evaluate:
- root-cause identification
- technical reasoning
- correctness of proposed fix

For TECHNICAL SCENARIO evaluate:
- diagnosis
- engineering reasoning
- trade-offs
- practicality

For ENGINEERING evaluate:
- architecture
- technical decisions
- scalability
- reliability
- practical implementation

Give a score from 0 to 10.

Do not reward keyword matching.
Do not assume an answer is correct merely because
it sounds technical.

Return ONLY valid JSON:

{{
    "score": 0,
    "correctness": 0,
    "reasoning": 0,
    "practicality": 0,
    "feedback": "",
    "strengths": [],
    "areas_to_improve": []
}}
"""

        try:

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            result = extract_json(
                response.text
            )

            results.append({
                "id": item.get("id"),
                "type": question_type,
                "skill": skill,
                "question": question,
                "score": result.get(
                    "score",
                    0
                ),
                "correctness": result.get(
                    "correctness",
                    0
                ),
                "reasoning": result.get(
                    "reasoning",
                    0
                ),
                "practicality": result.get(
                    "practicality",
                    0
                ),
                "feedback": result.get(
                    "feedback",
                    ""
                ),
                "strengths": result.get(
                    "strengths",
                    []
                ),
                "areas_to_improve": result.get(
                    "areas_to_improve",
                    []
                )
            })

        except Exception as error:

            print(
                f"Round 2 evaluation error: {error}"
            )

            results.append({
                "id": item.get("id"),
                "type": question_type,
                "skill": skill,
                "question": question,
                "score": 0,
                "feedback": (
                    "AI evaluation could not be completed."
                )
            })

    if results:

        overall_score = round(
            sum(
                float(item.get("score", 0))
                for item in results
            ) / len(results),
            1
        )

    else:

        overall_score = 0

    if overall_score >= 8:
        evaluation = "Strong technical performance"

    elif overall_score >= 6:
        evaluation = "Good technical performance"

    elif overall_score >= 4:
        evaluation = "Requires technical verification"

    else:
        evaluation = "Weak technical performance"

    return {
        "overall_score": overall_score,
        "overall_evaluation": evaluation,
        "results": results
    }