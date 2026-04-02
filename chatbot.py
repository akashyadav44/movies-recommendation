import os
import streamlit as st


def _get_key(name):
    key = os.getenv(name)
    if key:
        return key
    try:
        return st.secrets[name]
    except Exception:
        return None


GROQ_API_KEY = _get_key("GROQ_API_KEY")

if GROQ_API_KEY:
    from groq import Groq
    _client = Groq(api_key=GROQ_API_KEY)
    PROVIDER = "groq"
else:
    PROVIDER = None

SYSTEM_PROMPT = """You are a helpful movie expert chatbot. You help users with:
- Movie recommendations based on their mood, genre, actors they like
- Information about movies (plot, cast, director, release year)
- Comparing movies and explaining why one might be better than another
- Explaining why certain movies are recommended based on content similarity

Keep answers short and friendly.
Always respond in English only, regardless of what language the user writes in.)."""


def get_chatbot_response(messages: list, current_movie: str = None) -> str:
    if not PROVIDER:
        return "GROQ_API_KEY set nahi hai."

    try:
        system = SYSTEM_PROMPT
        if current_movie:
            system += f"\n\nUser is currently viewing: '{current_movie}'. Use this as context."

        all_messages = [{"role": "system", "content": system}] + messages

        response = _client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=all_messages,
            max_tokens=1000,
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"


def render_chatbot_sidebar(current_movie: str = None):
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🤖 Movie Chatbot")

    if not PROVIDER:
        st.sidebar.error("GROQ_API_KEY set nahi hai.")
        return

    st.sidebar.caption("Powered by Groq — Llama 3 (Free)")

    if current_movie:
        st.sidebar.info(f"Context: {current_movie}")
    else:
        st.sidebar.caption("Ask me anything about movies!")

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    if st.sidebar.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_messages = []
        st.rerun()

    for msg in st.session_state.chat_messages[-6:]:
        if msg["role"] == "user":
            st.sidebar.markdown(
                f"<div style='background:#e0f2fe;padding:8px 10px;border-radius:10px;"
                f"margin:4px 0;font-size:0.82rem;color:#0c4a6e'>"
                f"<b>You:</b> {msg['content']}</div>",
                unsafe_allow_html=True
            )
        else:
            st.sidebar.markdown(
                f"<div style='background:#f0fdf4;padding:8px 10px;border-radius:10px;"
                f"margin:4px 0;font-size:0.82rem;color:#14532d'>"
                f"<b>Bot:</b> {msg['content']}</div>",
                unsafe_allow_html=True
            )

    user_input = st.sidebar.text_input(
        "Poochho kuch bhi...",
        placeholder="e.g.= 'Ask Anything about movies!'",
        key="chatbot_input",
        label_visibility="collapsed"
    )

    if st.sidebar.button("Send ➤", use_container_width=True, type="primary"):
        if user_input.strip():
            st.session_state.chat_messages.append({
                "role": "user",
                "content": user_input.strip()
            })
            with st.sidebar:
                with st.spinner("Soch raha hoon..."):
                    reply = get_chatbot_response(
                        messages=st.session_state.chat_messages,
                        current_movie=current_movie
                    )
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": reply
            })
            st.rerun()