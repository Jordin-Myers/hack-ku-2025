def evaluate_hygiene(seed: str, backed_up: bool, reused: bool) -> int:
    score = 0
    if backed_up:
        score += 1
    if not reused:
        score += 1
    return score