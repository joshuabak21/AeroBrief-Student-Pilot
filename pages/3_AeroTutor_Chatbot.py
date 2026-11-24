"""AeroTutor: aviation study chatbot that remembers the current conversation."""

import streamlit as st

from site_theme import apply_theme

st.set_page_config(page_title="AeroBrief | AeroTutor", page_icon="💬", layout="wide")
apply_theme()

st.markdown('<div class="ab-kicker">02 / Aviation ground-school companion</div>', unsafe_allow_html=True)
st.title("AeroTutor")
st.markdown(
    '<p class="ab-lead">Ask questions about aviation weather, aerodynamics, VFR, and flight training.</p>',
    unsafe_allow_html=True,
)
st.info("AeroTutor is a study helper, not a live weather or FAA regulation lookup. It has no external tools in Lab 3.")

# Instructions tell the AI how to behave. It cannot use the weather API.
INSTRUCTIONS = (
    "You are AeroTutor, a friendly student-pilot study assistant. "
    "Explain aviation terms clearly and keep answers reasonably short. "
    "Remember information shared earlier in this conversation. "
    "You have no tools or access to current weather, live FAA regulations, or the app's weather page. "
    "Never invent live conditions or decide whether someone should fly. "
    "For real flight decisions, recommend official sources and a flight instructor."
)

try:
    api_key = st.secrets.get("GOOGLE_API_KEY", "")
except Exception:
    api_key = ""

# Both the displayed messages and the AI's conversation history are saved.
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "ai_history" not in st.session_state:
    st.session_state.ai_history = []

if st.button("Clear conversation"):
    st.session_state.chat_messages = []
    st.session_state.ai_history = []
    st.rerun()

for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ask an aviation-training question...")
if question:
    st.session_state.chat_messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        if not api_key:
            answer = "Add your Gemini API key in Streamlit Settings → Secrets to use AeroTutor."
            st.warning(answer)
        else:
            try:
                from pydantic_ai import Agent
                from pydantic_ai.models.google import GoogleModel
                from pydantic_ai.providers.google import GoogleProvider

                model = GoogleModel("gemini-3.5-flash-lite", provider=GoogleProvider(api_key=api_key))
                agent = Agent(model, instructions=INSTRUCTIONS)
                with st.spinner("AeroTutor is thinking..."):
                    result = agent.run_sync(question, message_history=st.session_state.ai_history)
                answer = str(result.output)
                st.session_state.ai_history = result.all_messages()
                st.markdown(answer)
            except Exception:
                # An AI error should not crash the web page or reveal secret details.
                answer = "Sorry, AeroTutor could not respond. Check your key or try again later."
                st.error(answer)
        st.session_state.chat_messages.append({"role": "assistant", "content": answer})

st.caption("For educational use only. Verify important aviation information with official FAA guidance and your CFI.")
