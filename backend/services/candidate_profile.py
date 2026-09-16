from typing import Any


PROGRAMMING_LANGUAGES = {
    "Python",
    "Java",
    "C",
    "C++",
    "JavaScript",
    "TypeScript",
    "SQL",
    "Dart",
    "Go",
    "Rust",
    "PHP",
    "Kotlin",
    "Swift"
}


FRAMEWORKS_AND_TOOLS = {
    "React",
    "React.js",
    "Node.js",
    "Express.js",
    "FastAPI",
    "Flask",
    "Django",
    "MongoDB",
    "MySQL",
    "TensorFlow",
    "PyTorch",
    "OpenCV",
    "LangChain",
    "FAISS",
    "Git",
    "GitHub",
    "HTML",
    "CSS",
    "Tailwind CSS",
    "Flutter",
    "Next.js",
    "Streamlit"
}


def clean_lines(lines: list[str]) -> list[str]:
    """
    Remove empty lines and duplicate entries.
    """

    cleaned = []

    for line in lines:

        line = line.strip()

        if not line:
            continue

        if line not in cleaned:
            cleaned.append(line)

    return cleaned


def extract_programming_languages(
    skills: list[str]
) -> list[str]:

    return [
        skill
        for skill in skills
        if skill in PROGRAMMING_LANGUAGES
    ]


def extract_frameworks_and_tools(
    skills: list[str]
) -> list[str]:

    return [
        skill
        for skill in skills
        if skill in FRAMEWORKS_AND_TOOLS
    ]


def build_candidate_profile(
    sections: dict[str, list[str]],
    skills: list[str]
) -> dict[str, Any]:

    education = clean_lines(
        sections.get("education", [])
    )

    projects = clean_lines(
        sections.get("projects", [])
    )

    experience = clean_lines(
        sections.get("experience", [])
    )

    certifications = clean_lines(
        sections.get("certifications", [])
    )

    summary = clean_lines(
        sections.get("summary", [])
    )

    programming_languages = (
        extract_programming_languages(skills)
    )

    frameworks_and_tools = (
        extract_frameworks_and_tools(skills)
    )

    return {
        "summary": summary[:5],
        "education": education[:8],
        "projects": projects[:12],
        "experience": experience[:10],
        "certifications": certifications[:10],
        "programming_languages": programming_languages,
        "frameworks_and_tools": frameworks_and_tools
    }