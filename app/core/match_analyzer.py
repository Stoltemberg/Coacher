from __future__ import annotations


def determine_phase(game_time: float) -> str:
    if game_time < 840:
        return "lane"
    if game_time < 1680:
        return "mid_game"
    return "late_game"


def expected_cs(minutes: float, cs_per_minute: float = 6.5) -> float:
    return max(0.0, minutes * cs_per_minute)


def confidence_label(total_entries: int) -> str:
    if total_entries >= 8:
        return "Alta"
    if total_entries >= 4:
        return "Média"
    return "Baixa"


def duration_label(duration_seconds: float | int | None) -> str:
    if not duration_seconds:
        return "--"
    duration_minutes = int(float(duration_seconds) // 60)
    return f"{duration_minutes} min" if duration_minutes else "--"
