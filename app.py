import csv
import os

import gradio as gr

from config import (
    EMOTION_EMOJI_MAP,
    GROQ_DEFAULT_MODEL,
    GROQ_MODELS,
    HF_CHAT_MODELS,
    HF_DEFAULT_MODEL,
    OLLAMA_DEFAULT_MODEL,
)
from core.emotion import detect_emotion
from core.journal import clear_history, get_all_entries, get_history, init_db, log_entry
from core.llm import generate_response

MAX_CHARS = 500

init_db()


# ── Chat ──────────────────────────────────────────────────────────────────────

def respond(message, history, provider, groq_key, groq_model, grok_key, hf_token, hf_model, ollama_model):
    msg = message.strip()

    if not msg:
        return history, "", ""

    if len(msg) < 3:
        history = list(history or [])
        history.append({"role": "assistant", "content": "Say a bit more — I need material to work with. 😏"})
        return history, "", ""

    if len(msg) > MAX_CHARS:
        history = list(history or [])
        history.append({"role": "assistant", "content": f"Whoa, that's {len(msg)} characters. Keep it under {MAX_CHARS} — even your problems need an edit. ✂️"})
        return history, message, ""

    emotion = detect_emotion(msg)

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

    response = generate_response(msg, emotion, provider, api_keys, models)
    log_entry(msg, emotion, response)

    history = list(history or [])
    history.append({"role": "user",      "content": msg})
    history.append({"role": "assistant", "content": response})

    emoji = EMOTION_EMOJI_MAP.get(emotion, "🤔")
    return history, "", f"{emoji} Detected mood: **{emotion.title()}**"


def update_char_count(text):
    n = len(text)
    color = "crimson" if n > MAX_CHARS else "darkorange" if n > MAX_CHARS * 0.8 else "gray"
    return f'<p style="color:{color};font-size:0.78em;margin:2px 0">{n}/{MAX_CHARS}</p>'


def toggle_provider(provider):
    return (
        gr.update(visible=provider == "Groq"),
        gr.update(visible=provider == "Grok (xAI)"),
        gr.update(visible=provider == "HuggingFace"),
        gr.update(visible=provider == "Ollama (Local)"),
    )


# ── Analytics ─────────────────────────────────────────────────────────────────

def generate_analytics():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from collections import Counter

    entries = get_all_entries()
    if not entries:
        return None, "No entries yet — start venting and come back here! 😤"

    emotions = [e["emotion"] for e in entries]
    counts   = Counter(emotions)

    COLORS = {
        "sadness": "#64b5f6",
        "joy":     "#ffee58",
        "love":    "#f48fb1",
        "anger":   "#ef9a9a",
        "fear":    "#ce93d8",
        "surprise":"#80cbc4",
        "neutral": "#b0bec5",
    }
    BG = "#fafafa"

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    fig.patch.set_facecolor(BG)

    # Bar — emotion distribution
    labels  = [k.title() for k in counts]
    values  = list(counts.values())
    colors  = [COLORS.get(k, "#90a4ae") for k in counts]
    bars    = axes[0].bar(labels, values, color=colors, edgecolor="white", linewidth=1.2)
    axes[0].set_title("Emotion Distribution", fontsize=13, fontweight="bold", pad=10)
    axes[0].set_ylabel("Sessions")
    axes[0].set_facecolor(BG)
    for sp in ("top", "right"):
        axes[0].spines[sp].set_visible(False)
    for bar, val in zip(bars, values):
        axes[0].text(
            bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.15,
            str(val), ha="center", va="bottom", fontsize=10,
        )

    # Scatter — mood timeline (last 40 sessions)
    EMOTION_ORDER = ["sadness", "fear", "anger", "neutral", "surprise", "love", "joy"]
    e_to_y = {e: i for i, e in enumerate(EMOTION_ORDER)}
    recent  = entries[-40:]
    ys      = [e_to_y.get(e["emotion"], 3) for e in recent]
    dot_colors = [COLORS.get(e["emotion"], "#90a4ae") for e in recent]
    xs = list(range(len(recent)))
    axes[1].plot(xs, ys, color="#ddd", linewidth=1, zorder=2)
    axes[1].scatter(xs, ys, c=dot_colors, s=70, zorder=3)
    axes[1].set_yticks(range(len(EMOTION_ORDER)))
    axes[1].set_yticklabels([e.title() for e in EMOTION_ORDER], fontsize=9)
    axes[1].set_xticks([])
    axes[1].set_title(f"Mood Timeline (last {len(recent)} sessions)", fontsize=13, fontweight="bold", pad=10)
    axes[1].set_facecolor(BG)
    for sp in ("top", "right"):
        axes[1].spines[sp].set_visible(False)

    plt.tight_layout(pad=2.5)

    top_emotion, top_count = counts.most_common(1)[0]
    summary = (
        f"**{len(entries)}** sessions logged &nbsp;·&nbsp; "
        f"Top mood: **{top_emotion.title()}** ({top_count}×) &nbsp;·&nbsp; "
        f"**{len(counts)}** distinct emotions detected"
    )
    return fig, summary


# ── Journal ───────────────────────────────────────────────────────────────────

def _table_rows(entries):
    return [
        [
            e["timestamp"][:16].replace("T", " "),
            e["emotion"].title(),
            (e["vent"][:70]      + "…") if len(e["vent"])      > 70  else e["vent"],
            (e["response"][:120] + "…") if len(e["response"]) > 120 else e["response"],
        ]
        for e in entries
    ]


def refresh_journal():
    return _table_rows(get_history(limit=50)), ""


def export_journal():
    entries = get_all_entries()
    if not entries:
        return gr.update(visible=False), "⚠️ Nothing to export yet."
    path = "journal_export.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "vent", "emotion", "response"])
        writer.writeheader()
        writer.writerows(entries)
    return gr.update(value=path, visible=True), f"✅ Exported {len(entries)} entries."


def clear_journal():
    clear_history()
    return [], "🗑️ Journal cleared."


# ── UI ────────────────────────────────────────────────────────────────────────

with gr.Blocks(theme=gr.themes.Soft(), title="Thera-Burn 😈") as demo:
    gr.Markdown(
        "# 😈 RoastMyFeelings\n"
        "### *Not your therapist. Your brutally honest life coach.*"
    )

    with gr.Tabs():

        # ── Tab 1: Chat ───────────────────────────────────────────────
        with gr.TabItem("💬 Chat"):
            with gr.Row():

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
                    char_count = gr.HTML('<p style="color:gray;font-size:0.78em;margin:2px 0">0/500</p>')
                    clear_btn  = gr.Button("🗑️ Clear Chat", variant="secondary", size="sm")

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

        # ── Tab 2: Analytics ──────────────────────────────────────────
        with gr.TabItem("📊 Analytics"):
            analytics_btn     = gr.Button("Generate Charts", variant="primary", size="sm")
            analytics_summary = gr.Markdown("Click **Generate Charts** to analyze your mood history.")
            analytics_plot    = gr.Plot(label="")

        # ── Tab 3: Journal ────────────────────────────────────────────
        with gr.TabItem("📔 Journal"):
            with gr.Row():
                j_refresh = gr.Button("🔄 Refresh",     variant="secondary", size="sm")
                j_export  = gr.Button("📥 Export CSV",  variant="secondary", size="sm")
                j_clear   = gr.Button("🗑️ Clear All",   variant="stop",      size="sm")
            j_status   = gr.Markdown("")
            j_download = gr.File(label="Download CSV", visible=False)
            j_table    = gr.Dataframe(
                headers=["Date", "Mood", "Vent", "Response"],
                datatype=["str", "str", "str", "str"],
                interactive=False,
                wrap=True,
            )

    # ── Event wiring ──────────────────────────────────────────────────

    chat_inputs  = [msg_input, chatbot, provider, groq_key, groq_model, grok_key, hf_token, hf_model, ollama_model]
    chat_outputs = [chatbot, msg_input, emotion_info]

    send_btn.click(respond,  inputs=chat_inputs,  outputs=chat_outputs)
    msg_input.submit(respond, inputs=chat_inputs, outputs=chat_outputs)
    msg_input.change(update_char_count, inputs=[msg_input], outputs=[char_count])
    clear_btn.click(lambda: ([], "", ""), outputs=[chatbot, msg_input, emotion_info])

    provider.change(
        toggle_provider,
        inputs=[provider],
        outputs=[groq_group, grok_group, hf_group, ollama_group],
    )

    analytics_btn.click(generate_analytics, outputs=[analytics_plot, analytics_summary])

    j_refresh.click(refresh_journal, outputs=[j_table, j_status])
    j_export.click(export_journal,   outputs=[j_download, j_status])
    j_clear.click(clear_journal,     outputs=[j_table,    j_status])


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
