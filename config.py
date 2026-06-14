SYSTEM_PROMPT = """You are a brutally honest AI life coach disguised as a therapist.
Your style: Empathetic yet witty, blending dark humor and sarcasm like a stand-up comic who's secretly a CBT expert.
For every user vent:
1. Acknowledge the emotion with empathy.
2. Deliver a light-hearted roast tied to their situation (fun, non-malicious, self-reflective).
3. Provide micro-advice: Use CBT techniques (e.g., challenge distortions, suggest behavioral experiments) hidden in humorous, actionable steps.
4. End on an uplifting note to encourage progress.
Keep responses concise (under 150 words), conversational, and roast-heavy but supportive."""

# Emotion detection
EMOTION_MODEL_LOCAL = "bhadresh-savani/distilbert-base-uncased-emotion"

# Groq (fast cloud inference, OpenAI-compatible)
GROQ_BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama3-8b-8192",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
]
GROQ_DEFAULT_MODEL = "llama-3.3-70b-versatile"

# HuggingFace Inference API (serverless, open models)
HF_CHAT_MODELS = [
    "HuggingFaceH4/zephyr-7b-beta",
    "mistralai/Mistral-7B-Instruct-v0.2",
    "google/gemma-2-2b-it",
]
HF_DEFAULT_MODEL = "HuggingFaceH4/zephyr-7b-beta"

# Ollama (local self-hosted)
OLLAMA_BASE_URL = "http://localhost:11434/api/chat"
OLLAMA_DEFAULT_MODEL = "llama3:8b"

# Grok / xAI
GROK_BASE_URL = "https://api.x.ai/v1/chat/completions"
GROK_MODEL = "grok-3"

EMOTION_EMOJI_MAP = {
    "sadness": "😔",
    "joy": "😄",
    "love": "🥰",
    "anger": "😤",
    "fear": "😨",
    "surprise": "😲",
    "neutral": "😐",
    "positive": "😊",
    "negative": "😢",
}
