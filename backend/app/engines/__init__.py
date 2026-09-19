def level_band(level: int) -> str:
    if level <= 20:
        return "Beginner"
    if level <= 40:
        return "Basic"
    if level <= 60:
        return "Developing"
    if level <= 80:
        return "Proficient"
    return "Advanced"


IMPORTANCE_WEIGHT = {"High": 1.5, "Medium": 1.0, "Low": 0.6}
