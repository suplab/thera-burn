import os
import gradio as gr

from config import (
    GROQ_MODELS, GROQ_DEFAULT_MODEL,
    HF_CHAT_MODELS, HF_DEFAULT_MODEL,
    OLLAMA_DEFAULT_MODEL,
    EMOTION_EMOJI_MAP,
)
from core.emotion import detect_emotion
from core.llm import generate_response
from core.journal import init_db, log_entry, get_history

init_db()


def respond(message, history, provider, groq_key, groq_model, grok_key, hf_token, hf_model, ollama_model):
    if not message.strip():
        return history, "", ""

    emotion = detect_emotion(message)

    api_keys = {
        "groq": groq_key or os.getenv("GROQ_API_KEY", ""),
        "grok": grok_key or os.getenv("XAI_API_KEY", ""),
        "hf":   hf_token or os.getenv("HF_TOKEN", ""),
    }
    models = {
        "groq":   groq_model,
        "hf":     hf_model,
        "ollama": ollama_model,
    }

    response = generate_response(message, emotion, provider, api_keys, models)
    log_entry(message, emotion, response)

    history = list(history or [])
    history.append({"role": "user",      "content": message})
    history.append({"role": "assistant", "content": response})

    emoji = EMOTION_EMOJI_MAP.get(emotion, "🤔")
    return history, "", f"{emoji} Detected mood: **{emotion.title()}**"


def refresh_journal():
    entries = get_history(limit=10)
    return [
        [
            e["timestamp"][:16].replace("T", " "),
            e["emotion"].title(),
            (e["vent"][:70]     + "…") if len(e["vent"])     > 70  else e["vent"],
            (e["response"][:120] + "…") if len(e["response"]) > 120 else e["response"],
        ]
        for e in entries
    ]


def toggle_provider(provider):
    return (
        gr.update(visible=provider == "Groq"),
        gr.update(visible=provider == "Grok (xAI)"),
        gr.update(visible=provider == "HuggingFace"),
        gr.update(visible=provider == "Ollama (Local)"),
    )


with gr.Blocks(theme=gr.themes.Soft(), title="Thera-Burn 😈") as demo:
    gr.Markdown(
        "# 😈 RoastMyFeelings\n"
        "### *Not your therapist. Your brutally honest life coach.*"
    )

    with gr.Row():
        # ── Chat panel ────────────────────────────────────────────────
        with gr.Column(scale=7):
            chatbot = gr.Chatbot(
                label="Chat",
                height=460,
                type="messages",
                bubble_full_width=False,
                show_copy_button=True,
            )
            emotion_info = gr.Markdown("")

            with gr.Row():
                msg_input = gr.Textbox(
                    placeholder="Vent here… What's eating you today?",
                    show_label=False,
                    lines=2,
                    scale=5,
                    container=False,
                )
                send_btn = gr.Button("🔥 Roast Me", variant="primary", scale=1, min_width=130)

            clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary", size="sm")

        # ── Settings + Journal panel ──────────────────────────────────
        with gr.Column(scale=3):
            with gr.Accordion("⚙️ Settings", open=True):
                provider = gr.Radio(
                    choices=["Groq", "Grok (xAI)", "HuggingFace", "Ollama (Local)"],
                    value="Groq",
                    label="LLM Provider",
                )

                with gr.Column(visible=True) as groq_group:
                    groq_key = gr.Textbox(
                        label="Groq API Key",
                        type="password",
                        placeholder="gsk_…",
                        value=os.getenv("GROQ_API_KEY", ""),
                    )
                    groq_model = gr.Dropdown(
                        choices=GROQ_MODELS,
                        value=GROQ_DEFAULT_MODEL,
                        label="Groq Model",
                    )

                with gr.Column(visible=False) as grok_group:
                    grok_key = gr.Textbox(
                        label="Grok API Key (xAI)",
                        type="password",
                        placeholder="xai-…",
                        value=os.getenv("XAI_API_KEY", ""),
                    )

                with gr.Column(visible=False) as hf_group:
                    hf_token = gr.Textbox(
                        label="HuggingFace Token",
                        type="password",
                        placeholder="hf_…",
                        value=os.getenv("HF_TOKEN", ""),
                    )
                    hf_model = gr.Dropdown(
                        choices=HF_CHAT_MODELS,
                        value=HF_DEFAULT_MODEL,
                        label="HF Model",
                    )

                with gr.Column(visible=False) as ollama_group:
                    ollama_model = gr.Textbox(
                        label="Ollama Model",
                        value=OLLAMA_DEFAULT_MODEL,
                    )

            with gr.Accordion("📔 Mood Journal", open=False):
                journal_btn = gr.Button("🔄 Refresh", variant="secondary", size="sm")
                journal_display = gr.Dataframe(
                    headers=["Date", "Mood", "Vent", "Response"],
                    datatype=["str", "str", "str", "str"],
                    interactive=False,
                    wrap=True,
                )

    # ── Event wiring ──────────────────────────────────────────────────
    chat_inputs  = [msg_input, chatbot, provider, groq_key, groq_model, grok_key, hf_token, hf_model, ollama_model]
    chat_outputs = [chatbot, msg_input, emotion_info]

    send_btn.click(respond, inputs=chat_inputs, outputs=chat_outputs)
    msg_input.submit(respond, inputs=chat_inputs, outputs=chat_outputs)
    clear_btn.click(lambda: ([], "", ""), outputs=[chatbot, msg_input, emotion_info])
    journal_btn.click(refresh_journal, outputs=[journal_display])
    provider.change(toggle_provider, inputs=[provider], outputs=[groq_group, grok_group, hf_group, ollama_group])


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
