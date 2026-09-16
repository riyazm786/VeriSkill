SKILL_ALIASES = {
    "React.js": "React",
    "React": "React",

    "Node": "Node.js",
    "Node.js": "Node.js",

    "Jupyter Notebook": "Jupyter",
    "Jupyter": "Jupyter",

    "JavaScript": "JavaScript",

    "C++": "C++",
    "C": "C"
}


def normalize_skills(skills: list[str]) -> list[str]:
    """
    Convert detected skill names into canonical names
    and remove duplicates.
    """

    normalized = []

    for skill in skills:
        canonical_name = SKILL_ALIASES.get(skill, skill)

        if canonical_name not in normalized:
            normalized.append(canonical_name)

    return normalized