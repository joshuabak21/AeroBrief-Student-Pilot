"""Lab 4 extension placeholder. Lab 3 does not require agent tools."""

import streamlit as st
from site_theme import apply_theme

st.set_page_config(page_title="AeroBrief | Lab 4 Extension", page_icon="🧭", layout="wide")
apply_theme()

st.markdown('<div class="ab-kicker">03 / Future project extension</div>', unsafe_allow_html=True)
st.title("Flight Data Agent · Lab 4")
st.info("Reserved for Lab 4. This page intentionally has no connected data tools yet.")
st.write(
    "Lab 4 can extend AeroTutor with tools that look up a requested city and "
    "summarize forecast values from the same Open-Meteo API used on the data page. "
    "During Lab 3, the chatbot remains a tool-free aviation learning companion."
)
st.write("**Planned example questions:** 'What's the strongest forecast gust in Atlanta tomorrow?', 'Compare cloudiness in Denver and Daytona Beach', and 'What is the predicted crosswind for a heading of 090°?'")
