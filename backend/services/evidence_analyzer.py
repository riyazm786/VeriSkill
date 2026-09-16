import re


SKILL_VARIANTS = {
    "React": ["React", "React.js"],
    "Node.js": ["Node.js", "Node"],
    "Python": ["Python"],
    "Java": ["Java"],
    "C": ["C"],
    "C++": ["C++"],
    "JavaScript": ["JavaScript"],
    "HTML": ["HTML"],
    "CSS": ["CSS"],
    "Tailwind CSS": ["Tailwind CSS"],
    "MongoDB": ["MongoDB"],
    "MySQL": ["MySQL"],
    "SQL": ["SQL"],
    "Machine Learning": ["Machine Learning", "machine learning"],
    "Deep Learning": ["Deep Learning", "deep learning"],
    "NLP": ["NLP", "Natural Language Processing"],
    "Computer Vision": ["Computer Vision"],
    "Data Analysis": ["Data Analysis"],
    "Git": ["Git"],
    "Jupyter": ["Jupyter", "Jupyter Notebook"],
    "OpenCV": ["OpenCV"],
    "RAG": ["RAG", "Retrieval Augmented Generation"],
    "FAISS": ["FAISS"],
    "FastAPI": ["FastAPI"],
    "LangChain": ["LangChain"],
    "TensorFlow": ["TensorFlow"],
    "PyTorch": ["PyTorch"],
}


SECTION_WEIGHTS = {
    "skills": 1,
    "summary": 2,
    "education": 1,
    "certifications": 1,
    "projects": 3,
    "experience": 3,
    "other": 0
}


def contains_skill(skill: str, text: str) -> bool:

    variants = SKILL_VARIANTS.get(
        skill,
        [skill]
    )

    for variant in variants:

        if variant == "C++":
            pattern = r"(?<!\w)C\+\+(?!\w)"

        elif variant == "C":
            pattern = r"(?<!\w)C(?![\w+])"

        else:
            pattern = rf"(?<!\w){re.escape(variant)}(?!\w)"

        if re.search(
            pattern,
            text,
            re.IGNORECASE
        ):
            return True

    return False


def get_skill_text(skill: str, text: str) -> str:

    variants = SKILL_VARIANTS.get(
        skill,
        [skill]
    )

    for variant in variants:

        if variant == "C++":
            pattern = r"(?<!\w)C\+\+(?!\w)"

        elif variant == "C":
            pattern = r"(?<!\w)C(?![\w+])"

        else:
            pattern = rf"(?<!\w){re.escape(variant)}(?!\w)"

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(0)

    return skill


def analyze_skill_evidence(
    skill: str,
    sections: dict[str, list[str]]
) -> dict:

    evidence = []
    sources = []
    score = 0

    for section_name, lines in sections.items():

        section_matches = []

        for line in lines:

            if contains_skill(skill, line):

                # In the Skills section, store only
                # the actual skill name instead of
                # the entire skills line.
                if section_name == "skills":
                    section_matches.append(
                        get_skill_text(skill, line)
                    )

                else:
                    # For projects, experience, summary,
                    # etc., keep the complete line because
                    # it provides useful context.
                    section_matches.append(line)

        if section_matches:

            evidence.extend(section_matches)
            sources.append(section_name)

            score += SECTION_WEIGHTS.get(
                section_name,
                0
            )

    # Determine evidence strength
    if "projects" in sources or "experience" in sources:

        if score >= 6:
            strength = "high"
        else:
            strength = "medium"

    elif "summary" in sources:
        strength = "medium"

    elif "skills" in sources:
        strength = "low"

    else:
        strength = "none"

    return {
        "skill": skill,
        "claimed": len(sources) > 0,
        "evidence_count": len(evidence),
        "sources": sources,
        "evidence_strength": strength,
        "evidence": evidence
    }


def analyze_all_skills(
    skills: list[str],
    sections: dict[str, list[str]]
) -> dict:

    results = {}

    for skill in skills:

        results[skill] = analyze_skill_evidence(
            skill,
            sections
        )

    return results