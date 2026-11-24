import streamlit as st

from site_theme import apply_theme, safety_note

st.set_page_config(page_title="AeroBrief | Pilot Training", page_icon="✈️", layout="wide")
apply_theme()

st.markdown('<div class="ab-kicker">CS 1301 · Web Development Labs 3 & 4</div>', unsafe_allow_html=True)
st.title("AeroBrief")
st.markdown(
    '<p class="ab-lead">A weather-learning dashboard and AI ground-school companion for '
    'student pilots. Explore forecast trends, practice runway wind-component reasoning, '
    'and ask aviation training questions.</p>', unsafe_allow_html=True,
)

st.markdown(
    '<span class="ab-tag">Real external JSON data</span>'
    '<span class="ab-tag">Interactive charts</span>'
    '<span class="ab-tag">Pilot-focused chatbot</span>',
    unsafe_allow_html=True,
)
st.divider()

left, right = st.columns(2, gap="large")
with left:
    st.subheader("01 / Flight Weather Explorer")
    st.write(
        "Select a training airport or search for a city. Explore predicted surface winds, "
        "gusts, cloud cover, precipitation probabilities, visibility, and estimated "
        "headwind/crosswind components for a chosen runway heading."
    )
    st.page_link("pages/2_Flight_Weather.py", label="Open Flight Weather Explorer", icon="📈")

with right:
    st.subheader("02 / AeroTutor Chatbot")
    st.write(
        "Ask questions about VFR basics, weather vocabulary, runway headings, "
        "flight training, and aviation concepts. AeroTutor uses Gemini through "
        "Pydantic AI and remembers messages during your session. It does not have data tools in Lab 3."
    )
    st.page_link("pages/3_AeroTutor_Chatbot.py", label="Open AeroTutor Chatbot", icon="💬")

st.divider()
st.subheader("About this class project")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Theme:** Student pilots and aviation weather literacy")
    st.markdown("**Data:** [Open-Meteo forecast API](https://open-meteo.com/en/docs) and [geocoding API](https://open-meteo.com/en/docs/geocoding-api)")
with col2:
    st.markdown("**Class:** CS 1301 · Fall 2026")
    st.markdown("**Team:** Team 29, Section D Joshua Bakare, Ryosuke Ebata")

safety_note()
