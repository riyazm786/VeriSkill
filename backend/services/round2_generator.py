import json
import re

from services.llm_service import client, MODEL_NAME


def extract_json(text: str):
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
        raise ValueError("No JSON object found.")

    return json.loads(text[start:end + 1])


def generate_round2_questions(
    skills: list[str],
    evidence: list[str]
) -> list[dict]:
    """
    Generate a completely different second-round
    technical verification assessment.

    Round 2 contains exactly:
    - 1 coding challenge
    - 1 debugging challenge
    - 1 technical scenario
    - 1 engineering/project challenge
    """

    skills_text = ", ".join(skills)

    evidence_text = "\n".join(
        f"- {item}"
        for item in evidence[:10]
    )

    prompt = f"""
You are designing Round 2 of an AI-powered technical
candidate verification system.

The candidate has already completed Round 1.

ROUND 1 tested:
- Resume understanding
- Technical fundamentals
- Project experience
- Explanation ability

ROUND 2 MUST BE COMPLETELY DIFFERENT.

ROUND 2 is a Technical Verification Lab.

Candidate technical skills:
{skills_text}

Resume evidence:
{evidence_text}

Generate exactly FOUR challenges.

Challenge 1:
TYPE = coding

Create one practical coding problem related to the
candidate's strongest technical skills.

Requirements:
- Suitable for a final-year engineering candidate.
- Prefer Python when Python is among the skills.
- The problem should require actual reasoning.
- Do not simply ask the candidate to explain code.
- The candidate must write or describe an implementation.
- Include a concise problem statement.
- Include starter code only when useful.

Challenge 2:
TYPE = debugging

Give a short piece of faulty technical logic or code.
Ask the candidate to identify the problem and explain
how they would fix it.

Challenge 3:
TYPE = technical_scenario

Give a realistic engineering situation involving
performance, accuracy, deployment, data, debugging,
scalability or model behavior.

Ask the candidate what they would investigate and
what solution they would choose.

Challenge 4:
TYPE = engineering

Give a practical project-level problem related to the
candidate's skills.

Test architecture, engineering decisions,
trade-offs and implementation strategy.

IMPORTANT:
Do not repeat normal Round 1 interview questions.

Return ONLY valid JSON.

Use exactly:

{{
    "questions": [
        {{
            "id": "coding-1",
            "type": "coding",
            "skill": "Python",
            "question": "...",
            "starter_code": "..."
        }},
        {{
            "id": "debugging-1",
            "type": "debugging",
            "skill": "...",
            "question": "...",
            "starter_code": "..."
        }},
        {{
            "id": "scenario-1",
            "type": "technical_scenario",
            "skill": "...",
            "question": "...",
            "starter_code": null
        }},
        {{
            "id": "engineering-1",
            "type": "engineering",
            "skill": "...",
            "question": "...",
            "starter_code": null
        }}
    ]
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

        questions = result.get(
            "questions",
            []
        )

        if len(questions) != 4:
            raise ValueError(
                "Round 2 did not return exactly 4 questions."
            )

        return questions

    except Exception as error:

        print(
            f"Round 2 generation error: {error}"
        )

        # Safe fallback if the AI generation fails.
        fallback_skill = skills[0] if skills else "Python"

        return [
            {
                "id": "coding-1",
                "type": "coding",
                "skill": fallback_skill,
                "question": (
                    "Write a function that receives a list "
                    "of numbers and returns the second "
                    "largest unique value."
                ),
                "starter_code": (
                    "def second_largest(numbers):\n"
                    "    # Write your solution here\n"
                    "    pass"
                )
            },
            {
                "id": "debugging-1",
                "type": "debugging",
                "skill": fallback_skill,
                "question": (
                    "A program produces incorrect results "
                    "only for some inputs. Explain how you "
                    "would systematically debug the issue "
                    "and identify the root cause."
                ),
                "starter_code": None
            },
            {
                "id": "scenario-1",
                "type": "technical_scenario",
                "skill": fallback_skill,
                "question": (
                    "Your application works correctly on your "
                    "local machine but becomes significantly "
                    "slower after deployment. What would you "
                    "investigate first and why?"
                ),
                "starter_code": None
            },
            {
                "id": "engineering-1",
                "type": "engineering",
                "skill": fallback_skill,
                "question": (
                    "You need to improve the reliability of "
                    "a technical project before deploying it "
                    "to real users. Describe the engineering "
                    "steps you would take."
                ),
                "starter_code": None
            }
        ]