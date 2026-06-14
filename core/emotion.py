from typing import Optional
from config import EMOTION_MODEL_LOCAL

_pipeline = None


def _get_pipeline():
    global _pipeline
    if _pipeline is None:
        from transformers import pipeline
        _pipeline = pipeline("text-classification", model=EMOTION_MODEL_LOCAL)
    return _pipeline


def detect_emotion(text: str) -> str:
    """Detect primary emotion using local HF model (6-class: sadness, joy, love, anger, fear, surprise)."""
    try:
        result = _get_pipeline()(text[:512])
        return result[0]["label"].lower()
    except Exception:
        return "neutral"
