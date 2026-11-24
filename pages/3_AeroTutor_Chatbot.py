"""Lab 3 Page 2: theme-focused Pydantic AI chatbot with session memory, no tools."""

import streamlit as st

from site_theme import apply_theme

st.set_page_config(page_title="AeroBrief | AeroTutor", page_icon="💬", layout="wide")
apply_theme()

st.markdown('<div class="ab-kicker">02 / Aviation ground-school companion</div>', unsafe_allow_html=True)
st.title("AeroTutor")
st.markdown(
    '<p class="ab-lead">An AI study partner for student pilots. Ask about weather terms, '
    'aerodynamics basics, VFR concepts, runway headings, and flight-training vocabulary.</p>',
    unsafe_allow_html=True,
)

st.info(
    "Lab 3 scope: AeroTutor has **no external tools or access to the weather dashboard**. "
    "It cannot retrieve current METARs, forecasts, or regulations. "
    "It is for learning, not operational flight decisions."
)

try:
    api_key = str(st.secrets.get("GOOGLE_API_KEY", "")).strip()
except Exception:
    api_key = ""

if not api_key or api_key.startswith("REPLACE_"):
    st.warning(
        "Gemini API key not configured. Copy `.streamlit/secrets.toml.example` to "
        "`.streamlit/secrets.toml` and insert your own key locally. For a deployed app, "
        "add the key in Streamlit Community Cloud → App settings → Secrets."
    )

if "aerotutor_chat_log" not in st.session_state:
    st.session_state.aerotutor_chat_log = []
if "aerotutor_pydantic_history" not in st.session_state:
    st.session_state.aerotutor_pydantic_history = []

left, right = st.columns([3, 1])
with left:
    st.caption("Try: 'Explain a crosswind to a student pilot' · 'What does VFR mean?' · 'Remember my favorite training aircraft is a C172'")
with right:
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.aerotutor_chat_log = []
        st.session_state.aerotutor_pydantic_history = []
        st.rerun()

for entry in st.session_state.aerotutor_chat_log:
    with st.chat_message(entry["role"]):
        st.markdown(entry["content"])

prompt = st.chat_input("Ask an aviation-training question...")
if prompt:
    st.session_state.aerotutor_chat_log.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if not api_key or api_key.startswith("REPLACE_"):
            answer = "A Gemini API key is required before I can respond. Please configure it in Streamlit Secrets."
            st.warning(answer)
        else:
            with st.spinner("AeroTutor is thinking..."):
                try:
                    from pydantic_ai import Agent
                    from pydantic_ai.models.google import GoogleModel
                    from pydantic_ai.providers.google import GoogleProvider

                    provider = GoogleProvider(api_key=api_key)
                    model = GoogleModel("gemini-3.5-flash-lite", provider=provider)
                    agent = Agent(
                        model,
                        instructions=(
                            "You are AeroTutor, a concise, friendly student-pilot ground-school "
                            "study assistant. Answer questions about aviation vocabulary, "
                            "weather concepts, aerodynamics, and learning to fly. Explain "
                            "terms in approachable language and ask an occasional useful "
                            "study-check question. Remember facts the student shares within "
                            "this conversation, but avoid pretending to remember across sessions. "
                            "You have no tools and NO ACCESS to real-time weather, the app's "
                            "weather data page, airport status, or live FAA regulations. "
                            "Never fabricate current readings or claim a flight is safe. "
                            "If asked for exact live conditions, say you can't look them up; "
                            "point to official aviation weather and their CFI. "
                            "Do not give a personalized operational go/no-go decision. "
                            "If rules or procedures could have changed, say to check the current FAA guidance."
                        ),
                    )
                    result = agent.run_sync(
                        prompt,
                        message_history=st.session_state.aerotutor_pydantic_history,
                    )
                    answer = str(result.output)
                    st.session_state.aerotutor_pydantic_history = result.all_messages()
                    st.markdown(answer)
                except Exception:
                    # Deliberately avoid showing provider errors or credentials to the user.
                    answer = (
                        "Sorry, AeroTutor couldn't respond right now. "
                        "The model may be busy, a quota may have been reached, "
                        "or the API key may need checking. Please try again."
                    )
                    st.error(answer)
        st.session_state.aerotutor_chat_log.append({"role": "assistant", "content": answer})

st.caption("Powered by Pydantic AI + Google Gemini when configured. Answers are educational and may be incorrect; verify important facts with official FAA material.")
