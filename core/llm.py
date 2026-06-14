import requests
from typing import Optional, Dict
from config import SYSTEM_PROMPT, GROQ_BASE_URL, GROK_BASE_URL, GROK_MODEL, OLLAMA_BASE_URL


def _build_messages(prompt: str, emotion: str) -> list:
    enhanced = f"User's detected emotion: {emotion}. User says: {prompt}"
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": enhanced},
    ]


def get_ollama_response(prompt: str, emotion: str, model: str) -> Optional[str]:
    try:
        resp = requests.post(
            OLLAMA_BASE_URL,
            json={"model": model, "messages": _build_messages(prompt, emotion), "stream": False},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"]
    except Exception:
        return None


def get_groq_response(prompt: str, emotion: str, api_key: str, model: str) -> Optional[str]:
    try:
        resp = requests.post(
            GROQ_BASE_URL,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": _build_messages(prompt, emotion),
                "temperature": 0.8,
                "max_tokens": 300,
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception:
        return None


def get_grok_response(prompt: str, emotion: str, api_key: str) -> Optional[str]:
    try:
        resp = requests.post(
            GROK_BASE_URL,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": GROK_MODEL,
                "messages": _build_messages(prompt, emotion),
                "temperature": 0.8,
                "max_tokens": 300,
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception:
        return None


def get_hf_response(prompt: str, emotion: str, hf_token: str, model: str) -> Optional[str]:
    try:
        from huggingface_hub import InferenceClient
        client = InferenceClient(model=model, token=hf_token)
        response = client.chat_completion(
            messages=_build_messages(prompt, emotion),
            max_tokens=300,
            temperature=0.8,
        )
        return response.choices[0].message.content
    except Exception:
        return None


def generate_response(
    prompt: str,
    emotion: str,
    provider: str,
    api_keys: Dict[str, str],
    models: Dict[str, str],
) -> str:
    response = None

    if provider == "Groq" and api_keys.get("groq"):
        response = get_groq_response(prompt, emotion, api_keys["groq"], models.get("groq", "llama-3.3-70b-versatile"))
    elif provider == "Grok (xAI)" and api_keys.get("grok"):
        response = get_grok_response(prompt, emotion, api_keys["grok"])
    elif provider == "HuggingFace" and api_keys.get("hf"):
        response = get_hf_response(prompt, emotion, api_keys["hf"], models.get("hf", "HuggingFaceH4/zephyr-7b-beta"))
    elif provider == "Ollama (Local)":
        response = get_ollama_response(prompt, emotion, models.get("ollama", "llama3:8b"))

    if response is None:
        return "⚠️ Couldn't reach the AI backend. Check your API key or Ollama setup and try again."

    return response
