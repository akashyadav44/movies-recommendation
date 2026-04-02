import os
import anthropic
import streamlit as st

# Streamlit Cloud secrets ya local env variable dono se kaam karega
_api_key = st.secrets.get("ANTHROPIC_API_KEY") if hasattr(st, "secrets") else None
if not _api_key:
    _api_key = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=_api_key)

SYSTEM_PROMPT = """You are a helpful movie expert chatbot. You help users with:
- Movie recommendations based on their mood, genre, actors they like
- Information about movies (plot, cast, director, release year)
- Comparing movies and explaining why one might be better than another
- Explaining why certain movies are recommended based on content similarity

Keep answers short and friendly. If asked about a specific movie that is currently
being viewed by the user, use that context to give better answers.
Always respond in the same language the user writes in (Hindi/English/Hinglish)."""


def get_chatbot_response(messages: list, current_movie: str = None) -> str:
    system = SYSTEM_PROMPT
    if current_movie:
        system += f"\n\nThe user is currently viewing: '{current_movie}'. Use this as context when relevant."

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=system,
            messages=messages,
        )
        return response.content[0].text
    except anthropic.AuthenticationError:
        return "API key sahi nahi hai. Streamlit Secrets mein ANTHROPIC_API_KEY check karo."
    except anthropic.RateLimitError:
        return "Bahut zyada requests ho gayi. Thodi der baad try karo."
    except Exception as e:
        return f"Error: {str(e)}"


def render_chatbot_sidebar(current_movie: str = None):
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🤖 Movie Chatbot")

    if current_movie:
        st.sidebar.caption(f"Context: {current_movie}")
    else:
        st.sidebar.caption("Koi bhi movie ke baare mein poochho!")

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    if st.sidebar.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_messages = []
        st.rerun()

    # Last 6 messages dikhao
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
        "Ask me anything...",
        placeholder="e.g. Mujhe action movies suggest karo",
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
                with st.spinner("Thinking..."):
                    reply = get_chatbot_response(
                        messages=st.session_state.chat_messages,
                        current_movie=current_movie
                    )

            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": reply
            })

            st.rerun()