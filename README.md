# Thera-Burn : AI Therapist That Roasts Your Feelings

> Not your therapist. Your brutally honest life coach.

Thera-Burn is an AI-powered mental wellness app that combines empathetic therapy with dark humor and witty roasts. Tired of sterile affirmations? This app listens to your vents, detects your mood, and delivers no-nonsense advice laced with sarcasm—using psychological insights (like CBT techniques) hidden under stand-up comic flair. It's designed to boost engagement through humor while providing real, actionable support.
Perfect for quick venting sessions or tracking emotional patterns over time. Built as an MVP with local-first privacy in mind.

## 🎯 Problem It Solves
Mental wellness apps often feel too serious or bland, leading to low retention. People crave humor + brutal truth over fluffy positivity. Thera-Burn flips the script: It roasts your bad habits lovingly to make you laugh, reflect, and change.

## 💡 How It Works
1. **Vent Input:** Share your thoughts via text (voice support planned for future).
2. **Emotion Detection:** Analyzes tone to tag emotions (e.g., sad, anxious, bored).
3. **Roast Generation:** LLM crafts a response with:
   - Empathy for your feelings.
   - A light-hearted roast (fun, non-malicious).
   - Micro-advice rooted in CBT (e.g., challenging negative thoughts).
   - An uplifting close.
4. **Mood Journal:** Logs sessions for tracking progress (optional viewing).
5. **Output:** Concise, conversational reply to keep it snappy.

## 🧠 Example Dialog
**User:** “I can’t seem to focus on anything lately.” <br>
**Thera-Burn:** “Ah, the classic 'focus fog'—probably because your brain's auditioning for a squirrel role. <br>Empathize: It's tough when everything feels scattered. Roast: Maybe ditch the 47 Chrome tabs and that emotional hoarding habit? <br>Advice: Pick one task, set a 5-min timer (yes, _just_ five—your future self will thank you, unlike your past self who's still binge-watching excuses). You've got this, chaos conductor. 😏” <br><br>
**User:** “Ouch. That’s fair.” <br>
**Thera-Burn:** “Good, truth stings less than regret. Now close those tabs—literal and metaphorical. What's one tiny win today?” 

## ✨ Features
- **Interactive Chat UI:** Built with Streamlit for easy web-based venting.
- **Local-First AI:** Uses Ollama (Llama 3) for privacy and low latency.
- **Fallback to Grok API:** Seamless switch if local model fails (requires API key).
- **Emotion Analysis:** Hugging Face transformers for quick sentiment tagging.
- **Mood Journal:** SQLite-backed history to review recent entries (last 5 shown in sidebar).
- **CBT-Infused Roasts:** Structured prompts ensure advice is psychologically sound yet hilarious.
- **Configurable:** API key via env var or UI; model swapping easy.
- **MVP-Ready:** Deployable locally or to cloud (e.g., Streamlit Sharing).

## 🚀 Quick Start

1. Clone the repo:
```bash
git clone <your-repo-url>
cd thera-burn
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Ollama (local AI):
- Pull model: `ollama pull llama3:8b`.
- Start server: `ollama serve`.

4. (Optional) Grok API Fallback:
- Get key from `x.ai/api`.
- Set env: `export XAI_API_KEY=your_key_here`.

5. Run the app:
```bash
streamlit run app.py
```
Open http://localhost:8501.

6. Vent away! Type in the chat input; view journal in sidebar.

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.10+.
- Git.
- Ollama installed (for local LLM).
- (Optional) Hugging Face account for model caching.

### Step-by-Step Setup

1. **Environment Setup:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Ollama Configuration:**
- Install: Follow Ollama docs.
- Model: `ollama pull llama3:8b` (8B for balanced humor; swap to `llama3:70b` for premium quality).
- Server: Runs on `localhost:11434` by default—ensure it's active.

3. **Grok API (Fallback):**
- Sign up at `x.ai/api`.
- Export key: `export XAI_API_KEY=sk-...` (or enter in app sidebar).

4. **Database:**
- Auto-creates `mood_journal.db` on first run (SQLite—no extra setup).

5. **Launch:**
```bash
streamlit run app.py
```
- Access via browser.


### Troubleshooting

- Ollama Fails: Check if server is running (`curl http://localhost:11434`). Fallback to Grok if key set.
- Transformers Errors: Ensure torch is installed (CPU/GPU variants).
- No Emotion Detection: Model downloads on first run (~500MB).
- High Latency: Use smaller model like `llama3.2:1b` for speed.

## 📱 Usage

### Chat Interface:
- Type your vent in the bottom input.
- App detects emotion (e.g., "Detected mood: Sad 😔").
- Receives roasted response.
- Type `history` for sidebar reminder.

### Mood Journal:
- Sidebar button: "View Recent Entries".
- Shows last 5: Timestamp, emotion, vent snippet, AI response.
- Privacy: Local SQLite file—delete `mood_journal.db` to clear.

### Customization:
- Edit `SYSTEM_PROMPT` in `app.py` for tone tweaks.
- Swap emotion model: Change pipeline in `load_emotion_analyzer()`.
- Add voice: Integrate Streamlit's audio recorder (future enhancement).

## 🏗️ Architecture
```
textUser Input (Streamlit Chat)
          ↓
Emotion Analyzer (Hugging Face Pipeline)
          ↓
Enhanced Prompt (w/ Emotion + System Prompt)
          ↓
LLM Inference: Ollama → Grok Fallback
          ↓
Response Generation + Logging (SQLite)
          ↓
UI Display + Journal Sidebar
```

- **Flow:** Modular for easy extension (e.g., add vector DB for long-term journaling).
- **Scalability:** Local for MVP; deploy to Hugging Face Spaces or Vercel.
- **Security:** No cloud storage by default; API calls encrypted.

## 🔧 Tech Stack
| **Layer** | **Tool(s)** | **Why?** |
|---|---|---|
| **UI/Frontend** | Streamlit | "Rapid prototyping, interactive chat out-of-box." |
| **LLM Backend** | Ollama (Llama 3:8b) / Grok API | "Local privacy + cloud fallback; humor-tuned models." |
| **Emotion Detection** | Hugging Face Transformers (DistilBERT) | "Lightweight, local sentiment analysis." |
| **Persistence** | SQLite | "Simple, file-based journaling." |
| **HTTP/JSON** | Requests | "API calls to Ollama/Grok." |
| **Other** | "Python 3.10+, Torch" | "Core runtime and ML deps." |

- **No External Services:** Runs fully offline except Grok fallback.
- **Model Size:** ~4.7GB for Llama 3:8b (quantized options available).

## 📈 Future Enhancements

- **Voice Input:** Speech-to-text via Whisper (local).
- **Advanced Emotions:** Multi-label detection (anger, joy, fear).
- **Personalization:** Fine-tune on user history.
- **Analytics:** Mood trend charts (Matplotlib integration).
- **Mobile:** PWA via Streamlit extras.
- **Multi-Language:** Prompt translations.

