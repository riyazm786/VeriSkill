import re


SECTION_ALIASES = {
    "summary": [
        "professional summary",
        "summary",
        "profile",
        "objective"
    ],

    "education": [
        "education",
        "academic background",
        "academic qualifications"
    ],

    "skills": [
        "technical skills",
        "skills",
        "technical expertise",
        "technologies"
    ],

    "projects": [
        "projects",
        "academic projects",
        "personal projects",
        "project experience"
    ],

    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "internship",
        "internships"
    ],

    "certifications": [
        "certifications",
        "certificates",
        "licenses & certifications"
    ]
}


def detect_section(line: str) -> str | None:
    """
    Identify whether a resume line represents a section heading.
    """

    cleaned = line.strip().lower()

    # Remove common formatting characters
    cleaned = re.sub(r"[^a-zA-Z0-9& ]", "", cleaned)
    cleaned = cleaned.strip()

    for section, aliases in SECTION_ALIASES.items():

        for alias in aliases:

            if cleaned == alias:
                return section

    return None


def split_resume_into_sections(text: str) -> dict[str, list[str]]:
    """
    Split the resume into logical sections.
    """

    sections = {}
    current_section = "other"

    sections[current_section] = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        detected_section = detect_section(line)

        if detected_section:
            current_section = detected_section

            if current_section not in sections:
                sections[current_section] = []

        else:
            sections[current_section].append(line)

    return sections