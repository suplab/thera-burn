# Thera-Burn 🔥😈
> Not your therapist. Your brutally honest life coach.

Thera-Burn is an AI-powered mental wellness app that combines empathetic therapy with dark humor. It listens to your vents, detects your mood, and delivers no-nonsense CBT-infused advice wrapped in stand-up comedy flair. Built for people who'd rather laugh at their problems than meditate them away.

---

## What it does

1. **Vent** — Type what's bothering you in the chat.
2. **Detect** — A local HuggingFace model classifies your emotion (6 classes: sadness, joy, love, anger, fear, surprise).
3. **Roast** — An LLM delivers empathy + a light roast + a CBT-inspired micro-tip, all under 150 words.
4. **Journal** — Every session is logged to local SQLite. Review, export as CSV, or clear it.
5. **Analyse** — Visualise your emotion distribution and mood timeline across all sessions.

---

## Features

| Feature | Status |
|---|---|
| Chat UI (Gradio, light theme) | ✅ |
| 4 LLM providers: Groq, Grok (xAI), HuggingFace Inference, Ollama | ✅ |
| 6-class emotion detection (local HF model, lazy-loaded) | ✅ |
| Dynamic settings panel per provider | ✅ |
| Input validation + character counter | ✅ |
| Mood journal (SQLite, last 50 entries) | ✅ |
| Analytics tab — emotion distribution + mood timeline charts | ✅ |
| CSV export of full journal | ✅ |
| Voice input (Whisper) | 🔜 |
| Multi-language support | 🔜 |
| Mood trend notifications / weekly report | 🔜 |

---

## Project Structure

```
thera-burn/
├── app.py              # Gradio UI — tabs, event wiring, all UI logic
├── config.py           # Constants: system prompt, model lists, URLs, emoji map
├── requirements.txt
├── .env.example        # Template for API keys
└── core/
    ├── emotion.py      # Lazy-loaded HF pipeline, detect_emotion()
    ├── llm.py          # Groq / Grok / HuggingFace / Ollama + routing
    └── journal.py      # SQLite CRUD: log, read, export, clear
```

---

## Quick Start

```bash
git clone <repo-url>
cd thera-burn
pip install -r requirements.txt
cp .env.example .env   # fill in your keys
python app.py          # opens at http://localhost:7860
```

The emotion model (~250 MB) downloads on first run and is cached locally.

---

## LLM Providers

Pick one in the Settings panel. Keys can be pasted in the UI or set as env vars.

| Provider | Env var | Notes |
|---|---|---|
| **Groq** *(default)* | `GROQ_API_KEY` | Fast cloud inference; free tier available. Models: `llama-3.3-70b-versatile`, `llama3-8b-8192`, `mixtral-8x7b-32768`, `gemma2-9b-it` |
| **Grok (xAI)** | `XAI_API_KEY` | x.ai's `grok-3` model |
| **HuggingFace** | `HF_TOKEN` | Serverless inference via `InferenceClient`. Models: `zephyr-7b-beta`, `Mistral-7B-Instruct-v0.2`, `gemma-2-2b-it` |
| **Ollama (Local)** | — | Self-hosted; runs fully offline. Default model: `llama3:8b`. Install Ollama and run `ollama pull llama3:8b` |

---

## Environment Variables

```bash
# .env
GROQ_API_KEY=gsk_...
XAI_API_KEY=xai-...
HF_TOKEN=hf_...
```

All keys are optional — only the selected provider's key is used. Keys entered in the UI take precedence over env vars.

---

## Architecture

```
User input (Gradio chat)
        │
        ▼
Input validation (3–500 chars)
        │
        ▼
Emotion detection  ◄── local HF model (bhadresh-savani/distilbert-base-uncased-emotion)
        │
        ▼
LLM routing  ◄── Groq │ Grok │ HuggingFace Inference │ Ollama
        │
        ▼
Response display + SQLite logging
        │
        ├── Analytics tab (matplotlib charts)
        └── Journal tab  (table, CSV export, clear)
```

---

## Tech Stack

| Layer | Tool | Why |
|---|---|---|
| UI | Gradio 4 (Soft light theme) | Fast, chat-native, tab layout |
| LLM — cloud fast | Groq API | Low-latency, generous free tier |
| LLM — cloud open | HuggingFace Inference API | Open models, no GPU needed |
| LLM — local | Ollama | Full privacy, no API key |
| Emotion detection | HF Transformers (DistilBERT, 6-class) | Lightweight, runs on CPU |
| Analytics | Matplotlib | Simple, no extra server |
| Persistence | SQLite | File-based, zero setup |
| HTTP | Requests | Groq / Grok API calls |
| HF client | huggingface_hub InferenceClient | HF serverless chat completions |

---

## Customisation

- **System prompt** — edit `SYSTEM_PROMPT` in `config.py` to change the roast tone.
- **Emotion model** — change `EMOTION_MODEL_LOCAL` in `config.py` to any HF text-classification model.
- **Add a provider** — add a function in `core/llm.py` and a branch in `generate_response()`.
- **Port** — change `server_port` in `app.py`'s `demo.launch()` call.

---

## Roadmap

- [ ] Voice input via Whisper (local STT → vent without typing)
- [ ] Weekly mood digest email / push notification
- [ ] Multi-language (auto-detect language, translate prompt)
- [ ] Personalisation (track recurring themes, fine-tune advice over time)
- [ ] Shareable roast cards (PNG export of funniest responses)
