from typing import Any

from services.adaptive_assessment import determine_difficulty


def generate_assessment_questions(
    skill: str,
    evidence_data: dict[str, Any],
    previous_score: int | None = None
) -> list[str]:

    evidence_strength = evidence_data.get(
        "evidence_strength",
        "none"
    )

    difficulty = determine_difficulty(
        evidence_strength,
        previous_score
    )

    evidence = evidence_data.get(
        "evidence",
        []
    )

    # ---------------------------------------------------------
    # NO EVIDENCE
    # ---------------------------------------------------------

    if evidence_strength == "none":
        return [
            f"What do you understand about {skill}?",
            f"What are the basic concepts of {skill}?",
            f"Where would you use {skill} in a real project?"
        ]

    # ---------------------------------------------------------
    # BASIC
    # ---------------------------------------------------------

    if difficulty == "basic":
        return [
            f"What is {skill}, and what is it mainly used for?",
            f"Can you explain the basic concepts of {skill}?",
            f"Can you give a practical example of using {skill}?"
        ]

    # ---------------------------------------------------------
    # INTERMEDIATE
    # ---------------------------------------------------------

    if difficulty == "intermediate":
        return [
            f"Can you explain the main concepts of {skill}?",
            f"How have you applied {skill} in your projects or experience?",
            f"What practical problem can be solved using {skill}?"
        ]

    # ---------------------------------------------------------
    # ADVANCED
    # ---------------------------------------------------------

    if difficulty == "advanced":

        evidence_hint = ""

        if evidence:
            evidence_hint = evidence[0]

        return [
            f"Explain how you used {skill} in the project or experience mentioned in your resume.",
            f"What technical challenges did you face while using {skill}, and how did you solve them?",
            f"If you redesigned your implementation of {skill}, what would you improve and why?"
        ]

    # ---------------------------------------------------------
    # SAFE FALLBACK
    # ---------------------------------------------------------

    return [
        f"Explain your understanding of {skill}.",
        f"How would you use {skill} in a real project?",
        f"What are some important considerations when working with {skill}?"
    ]


# ============================================================
# ROUND 2 — TECHNICAL VERIFICATION LAB
# ============================================================

def generate_technical_lab(
    skills: list[str],
    skill_evidence: dict[str, Any]
) -> list[dict]:

    """
    Generate a completely different second-round assessment.

    Round 2 contains:
    1. One coding / implementation challenge
    2. One technical / debugging / architecture challenge
    """

    if not skills:
        skills = ["Python"]

    # Choose the strongest skill first.
    strength_rank = {
        "high": 3,
        "medium": 2,
        "low": 1,
        "none": 0
    }

    ranked_skills = sorted(
        skills,
        key=lambda skill: strength_rank.get(
            skill_evidence.get(skill, {}).get(
                "evidence_strength",
                "none"
            ),
            0
        ),
        reverse=True
    )

    primary_skill = ranked_skills[0]

    # ---------------------------------------------------------
    # CODING QUESTION
    # ---------------------------------------------------------

    coding_questions = {

        "Python": (
            "Coding Challenge — Python\n\n"
            "Write a Python function that receives a list of integers "
            "and returns the first duplicate value. Explain the time "
            "and space complexity of your solution."
        ),

        "JavaScript": (
            "Coding Challenge — JavaScript\n\n"
            "Write a JavaScript function that removes duplicate values "
            "from an array while preserving the original order. "
            "Explain the approach you used."
        ),

        "React": (
            "Implementation Challenge — React\n\n"
            "A React component is re-rendering every time the user "
            "types into an unrelated input field. Explain how you "
            "would identify the cause and reduce unnecessary renders. "
            "Include the React concepts or code you would use."
        ),

        "Node.js": (
            "Implementation Challenge — Node.js\n\n"
            "Design a simple Node.js API endpoint that receives a "
            "candidate ID and returns the candidate's assessment "
            "result. Explain the request flow, validation and error "
            "handling."
        ),

        "SQL": (
            "Coding Challenge — SQL\n\n"
            "Assume you have a table named candidates with columns "
            "id, name and score. Write an SQL query that returns "
            "candidates whose score is greater than 8, ordered from "
            "highest score to lowest."
        ),

        "Machine Learning": (
            "Implementation Challenge — Machine Learning\n\n"
            "Suppose your classification model performs very well "
            "on training data but poorly on unseen data. Explain "
            "what is happening and describe two techniques you would "
            "use to improve the model."
        ),

        "Deep Learning": (
            "Implementation Challenge — Deep Learning\n\n"
            "A neural network is showing high training accuracy but "
            "low validation accuracy. Explain the likely problem "
            "and describe practical techniques you would use to "
            "improve generalization."
        ),

        "Computer Vision": (
            "Implementation Challenge — Computer Vision\n\n"
            "You receive a live camera stream and need to detect "
            "objects in real time. Describe the processing pipeline "
            "you would implement and explain how you would maintain "
            "reasonable performance."
        ),

        "OpenCV": (
            "Coding / Implementation Challenge — OpenCV\n\n"
            "Write or describe Python/OpenCV code that reads an image, "
            "converts it to grayscale and applies edge detection. "
            "Explain why each processing step is useful."
        ),

        "NLP": (
            "Implementation Challenge — NLP\n\n"
            "You need to classify text into multiple categories. "
            "Describe how you would preprocess the text, represent "
            "it numerically and build an initial classification model."
        )
    }

    coding_question = coding_questions.get(
        primary_skill,
        (
            f"Technical Coding Challenge — {primary_skill}\n\n"
            f"Describe or write a small implementation demonstrating "
            f"how you would practically use {primary_skill} in a real "
            f"software project. Explain your design decisions."
        )
    )

    # ---------------------------------------------------------
    # TECHNICAL SCENARIO
    # ---------------------------------------------------------

    technical_question = (
        f"Technical Scenario — {primary_skill}\n\n"
        f"You deployed a project using {primary_skill}, but the "
        f"application is producing incorrect or inconsistent results "
        f"in some cases. Explain how you would debug the problem "
        f"systematically. Mention the logs, tests, metrics or "
        f"technical checks you would perform."
    )

    return [
        {
            "type": "coding",
            "skill": primary_skill,
            "question": coding_question
        },
        {
            "type": "technical",
            "skill": primary_skill,
            "question": technical_question
        }
    ]