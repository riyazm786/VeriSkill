import re


# Skills are ordered from more specific to more general.
# This prevents things like C being detected inside C++.
SKILL_LIST = [
    "Tailwind CSS",
    "Machine Learning",
    "Deep Learning",
    "Computer Vision",
    "Data Analysis",
    "Jupyter Notebook",
    "JavaScript",
    "React.js",
    "Node.js",
    "OpenCV",
    "TensorFlow",
    "PyTorch",
    "LangChain",
    "FastAPI",
    "MongoDB",
    "MySQL",
    "Python",
    "Java",
    "C++",
    "C",
    "React",
    "Node",
    "HTML",
    "CSS",
    "SQL",
    "NLP",
    "Git",
    "GitHub",
    "RAG",
    "FAISS",
    "Flask",
    "Django",
]


def skill_found(skill: str, text: str) -> bool:
    """
    Check whether a skill is present in the resume text.
    """

    escaped_skill = re.escape(skill)

    # Special handling for C++
    if skill == "C++":
        return re.search(r"(?<!\w)C\+\+(?!\w)", text, re.IGNORECASE) is not None

    # Special handling for C
    if skill == "C":
        return re.search(r"(?<!\w)C(?![\w+])", text, re.IGNORECASE) is not None

    # Special handling for React.js
    if skill == "React.js":
        return re.search(r"(?<!\w)React\.js(?!\w)", text, re.IGNORECASE) is not None

    # Special handling for Node.js
    if skill == "Node.js":
        return re.search(r"(?<!\w)Node\.js(?!\w)", text, re.IGNORECASE) is not None

    pattern = rf"(?<!\w){escaped_skill}(?!\w)"

    return re.search(pattern, text, re.IGNORECASE) is not None

def extract_skills(text: str) -> list[str]:
    """
    Extract technical skills mentioned in the resume.
    """

    found_skills = []

    for skill in SKILL_LIST:
        if skill_found(skill, text):
            found_skills.append(skill)

    return found_skills