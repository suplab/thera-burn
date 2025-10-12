# app.py
# Thera-Burn: AI Therapist That Roasts You
# Streamlit app with emotion detection, roast generation, and mood journaling.
# Prefers local Ollama (llama3:8b) with fallback to Grok API.

import os
import sqlite3
import streamlit as st
from datetime import datetime
import requests
import json
from typing import Dict, Any, List
from transformers import pipeline

# System prompt for the AI (enhanced with CBT elements)
SYSTEM_PROMPT = """
You are a brutally honest AI life coach disguised as a therapist. 
Your style: Empathetic yet witty, blending dark humor and sarcasm like a stand-up comic who's secretly a CBT expert.
For every user vent:
1. Acknowledge the emotion with empathy.
2. Deliver a light-hearted roast tied to their situation (fun, non-malicious, self-reflective).
3. Provide micro-advice: Use CBT techniques (e.g., challenge distortions, suggest behavioral experiments) hidden in humorous, actionable steps.
4. End on an uplifting note to encourage progress.
Keep responses concise (under 150 words), conversational, and roast-heavy but supportive.
Example: User vents about procrastination → Roast their "future self" myth, advise a 5-min start rule with a funny twist.
"""

# Initialize sentiment pipeline (local HuggingFace model for emotion detection)
@st.cache_resource
def load_emotion_analyzer():
    """Load a local sentiment analysis pipeline for basic emotion tagging."""
    # Using a simple sentiment model; for more emotions, swap to 'bhadresh-savani/distilbert-base-uncased-emotion'
    return pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

emotion_analyzer = load_emotion_analyzer()

def init_db():
    """Initialize SQLite database for mood journal."""
    conn = sqlite3.connect('mood_journal.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            vent TEXT,
            emotion TEXT,
            response TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_mood_entry(vent: str, emotion: str, response: str):
    """Log entry to mood journal."""
    conn = sqlite3.connect('mood_journal.db')
    c = conn.cursor()
    timestamp = datetime.now().isoformat()
    c.execute('INSERT INTO entries (timestamp, vent, emotion, response) VALUES (?, ?, ?, ?)',
              (timestamp, vent, emotion, response))
    conn.commit()
    conn.close()

def get_mood_history() -> List[Dict[str, Any]]:
    """Retrieve recent mood journal entries."""
    conn = sqlite3.connect('mood_journal.db')
    c = conn.cursor()
    c.execute('SELECT timestamp, vent, emotion, response FROM entries ORDER BY timestamp DESC LIMIT 5')
    rows = c.fetchall()
    conn.close()
    return [{'timestamp': row[0], 'vent': row[1], 'emotion': row[2], 'response': row[3]} for row in rows]

def detect_emotion(text: str) -> str:
    """Detect primary emotion using the pipeline."""
    result = emotion_analyzer(text)[0]
    label = result['label'].lower()
    # Map to simple emotions (extend as needed)
    emotion_map = {
        'positive': 'happy',
        'negative': 'sad',
        'neutral': 'bored'
    }
    return emotion_map.get(label, label)

def get_ollama_response(user_input: str, emotion: str, model: str = "llama3:8b") -> str:
    """
    Query local Ollama with emotion context.
    Assumes Ollama running on localhost:11434.
    """
    enhanced_prompt = f"{SYSTEM_PROMPT}\n\nUser's emotion: {emotion}. User vent: {user_input}"
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": enhanced_prompt}
        ],
        "stream": False
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["message"]["content"]
    except requests.exceptions.RequestException:
        return None

def get_grok_response(user_input: str, emotion: str, api_key: str) -> str:
    """
    Fallback to Grok API.
    """
    enhanced_prompt = f"{SYSTEM_PROMPT}\n\nUser's emotion: {emotion}. User vent: {user_input}"
    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "grok-3",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": enhanced_prompt}
        ],
        "temperature": 0.8,  # Slightly higher for humor
        "max_tokens": 300
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException:
        return None

def main():
    st.set_page_config(page_title="Thera-Burn", page_icon="😈")
    st.title("😈 RoastMyFeelings")
    st.markdown("*Not your therapist. Your brutally honest life coach.*")

    # Sidebar for history
    st.sidebar.header("Mood Journal")
    if st.sidebar.button("View Recent Entries"):
        history = get_mood_history()
        for entry in history:
            st.sidebar.write(f"**{entry['timestamp'][:10]}** - {entry['emotion'].title()}: {entry['vent'][:50]}...")
            st.sidebar.write(f"AI: {entry['response'][:100]}...")

    # Check for Grok API key
    api_key = st.sidebar.text_input("Grok API Key (for fallback)", type="password", help="Set XAI_API_KEY env var or enter here.")
    if not api_key:
        api_key = os.getenv("XAI_API_KEY")

    # Main chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Vent here... (or type 'history' for journal)"):
        # Handle special commands
        if prompt.lower() == 'history':
            st.session_state.messages.append({"role": "assistant", "content": "Here's your recent mood history in the sidebar!"})
        else:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Detect emotion
            with st.spinner("Analyzing your vibe..."):
                emotion = detect_emotion(prompt)

            # Generate response
            with st.spinner("Roasting up some truth..."):
                response = get_ollama_response(prompt, emotion)
                if response is None and api_key:
                    response = get_grok_response(prompt, emotion, api_key)
                if response is None:
                    response = "Oof, my circuits are fried. Try again? (Check Ollama/Grok setup.)"

            # Display response
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)

            # Log to journal
            log_mood_entry(prompt, emotion, response)

            # Show detected emotion
            st.info(f"😏 Detected mood: **{emotion.title()}**")

        # Rerun to show new message
        st.rerun()

if __name__ == "__main__":
    init_db()
    main()