import re


ACTION_PATTERNS = (
    "faz",
    "joga",
    "usa",
    "procura",
    "segura",
    "reseta",
    "base",
    "compra",
    "prioriza",
    "pressiona",
    "marca",
    "espera",
    "luta",
    "roda",
)

RISK_PATTERNS = (
    "nao",
    "não",
    "evita",
    "cuidado",
    "risco",
    "perde",
    "pune",
    "puni",
    "sem recurso",
    "morrer",
    "entrega",
    "janela ruim",
)


def _sentence_parts(text):
    normalized = re.sub(r"\s+", " ", str(text or "")).strip()
    if not normalized:
        return []
    parts = [part.strip() for part in re.split(r"(?<=[.!?])\s+", normalized) if part.strip()]
    if len(parts) > 1:
        return parts
    if len(normalized) <= 150:
        return [normalized]
    split_at = normalized.rfind(" ", 0, 150)
    if split_at < 90:
        split_at = 150
    return [normalized[:split_at].strip(), normalized[split_at:].strip()]


def build_coach_call_snapshot(text, event_type="normal", category=None):
    parts = _sentence_parts(text)
    headline = parts[0] if parts else "Aguardando leitura do coach."
    payload = {
        "headline": headline,
        "risk": "",
        "action": "",
        "next_step": "",
        "type": event_type or "normal",
        "category": category or "",
    }

    for part in parts[1:4]:
        lower = part.lower()
        if not payload["risk"] and any(token in lower for token in RISK_PATTERNS):
            payload["risk"] = part
        elif not payload["action"] and any(token in lower for token in ACTION_PATTERNS):
            payload["action"] = part
        elif not payload["next_step"]:
            payload["next_step"] = part

    return payload
