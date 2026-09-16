def determine_difficulty(
    evidence_strength: str,
    previous_score: int | None = None
) -> str:

    if previous_score is not None:
        if previous_score >= 8:
            return "advanced"

        if previous_score >= 6:
            return "intermediate"

        return "basic"

    if evidence_strength == "high":
        return "advanced"

    if evidence_strength == "medium":
        return "intermediate"

    return "basic"