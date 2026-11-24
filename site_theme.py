"""Shared appearance for the Streamlit multipage app."""

import streamlit as st


def apply_theme():
    st.markdown(
        """
        <style>
        .stApp {
            background: radial-gradient(ellipse at 90% 4%, #102e4b 0%, transparent 40%),
                        #081523;
        }
        [data-testid="stSidebar"] {background-color: #0b1c2d;}
        h1, h2, h3 {letter-spacing: -0.035em;}
        h1 {font-weight: 800 !important;}
        [data-testid="stMetric"] {
            background: #10263a;
            border: 1px solid #244357;
            border-radius: 14px;
            padding: 16px 18px;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] > div {border-color: #274357;}
        .ab-kicker {
            color: #62d5d4;
            letter-spacing: .18em;
            font-size: .78rem;
            font-weight: 700;
            text-transform: uppercase;
            margin-bottom: 8px;
        }
        .ab-lead {color: #b5c7d7; font-size: 1.13rem; max-width: 850px;}
        .ab-strip {
            border-left: 3px solid #62d5d4;
            background-color: #10273a;
            padding: 13px 16px;
            border-radius: 0 12px 12px 0;
            margin: 16px 0;
        }
        .ab-tag {
            display:inline-block; border: 1px solid #2e6475;
            border-radius: 99px; color: #9fe2df;
            padding: 5px 11px; margin: 0 6px 6px 0;
            font-size: .8rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def safety_note():
    st.markdown(
        """
        <div class="ab-strip">
          <strong>Training use only.</strong> These are general weather-model forecasts,
          not airport METARs, TAFs, a complete preflight weather briefing, or a
          go/no-go recommendation. Always use official aviation sources and a CFI
          for real flight planning.
        </div>
        """,
        unsafe_allow_html=True,
    )
