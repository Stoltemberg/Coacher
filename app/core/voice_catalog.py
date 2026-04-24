"""Voice and personality registry for the desktop app."""

from __future__ import annotations

from copy import deepcopy


VOICE_PERSONALITIES = [
    {
        "id": "standard",
        "label": "Padrao",
        "engine": "edge_tts",
        "tier": "free",
        "description": "Voz neural local para uso diario sem custo de ElevenLabs.",
        "provider": "Local neural",
    },
    {
        "id": "minerva",
        "label": "Minerva",
        "engine": "elevenlabs",
        "tier": "premium",
        "description": "Entrega com personalidade forte usando voz premium.",
        "provider": "ElevenLabs",
    },
]


VOICE_PRESETS = [
    {
        "id": "standard",
        "label": "Equilibrado",
        "description": "Mais contexto e cadencia moderada durante a partida.",
    },
    {
        "id": "hardcore",
        "label": "Agressivo",
        "description": "Cobrança mais intensa e menos tolerancia a erro repetido.",
    },
    {
        "id": "minimal",
        "label": "Minimal",
        "description": "Intervencoes mais curtas e so nos momentos importantes.",
    },
]


SUBSCRIPTION_TIERS = [
    {
        "id": "free",
        "label": "Free",
        "monthly_price_brl": 0,
        "highlights": [
            "3 partidas por ciclo com vozes premium ElevenLabs",
            "Partidas ilimitadas com voz padrao neural local",
            "Coach ao vivo, memoria recente e dashboard completo",
        ],
    },
    {
        "id": "pro_monthly",
        "label": "Pro Mensal",
        "monthly_price_brl": 29.9,
        "highlights": [
            "Uso estendido de vozes premium ElevenLabs",
            "Mais personalidades e vozes exclusivas",
            "Historico avancado, insights entre partidas e futuras features premium",
        ],
    },
]


def voice_catalog_snapshot() -> dict:
    return {
        "personalities": deepcopy(VOICE_PERSONALITIES),
        "presets": deepcopy(VOICE_PRESETS),
        "tiers": deepcopy(SUBSCRIPTION_TIERS),
    }


def normalize_voice_personality(personality: str | None) -> str:
    token = str(personality or "standard").strip().lower()
    available = {item["id"] for item in VOICE_PERSONALITIES}
    return token if token in available else "standard"


def normalize_voice_preset(preset: str | None) -> str:
    token = str(preset or "standard").strip().lower()
    available = {item["id"] for item in VOICE_PRESETS}
    return token if token in available else "standard"


def resolve_voice_personality(personality: str | None) -> dict:
    normalized = normalize_voice_personality(personality)
    return next(item for item in VOICE_PERSONALITIES if item["id"] == normalized)
