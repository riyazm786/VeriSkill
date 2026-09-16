import re


def split_into_sentences(text: str) -> list[str]:
    """
    Split resume text into individual sentences/lines.
    Resumes often don't use normal sentences, so we also
    treat new lines as useful evidence boundaries.
    """

    lines = text.splitlines()

    sentences = []

    for line in lines:
        line = line.strip()

        if line:
            sentences.append(line)

    return sentences


def find_skill_evidence(skill: str, text: str) -> list[str]:
    """
    Find the lines from the resume that mention a particular skill.
    """

    evidence = []

    lines = split_into_sentences(text)

    for line in lines:

        # Special handling for C++
        if skill == "C++":
            pattern = r"(?<!\w)C\+\+(?!\w)"

        # Special handling for C
        elif skill == "C":
            pattern = r"(?<!\w)C(?![\w+])"

        # React.js
        elif skill == "React.js":
            pattern = r"(?<!\w)React\.js(?!\w)"

        # Node.js
        elif skill == "Node.js":
            pattern = r"(?<!\w)Node\.js(?!\w)"

        else:
            pattern = rf"(?<!\w){re.escape(skill)}(?!\w)"

        if re.search(pattern, line, re.IGNORECASE):
            evidence.append(line)

    return evidence