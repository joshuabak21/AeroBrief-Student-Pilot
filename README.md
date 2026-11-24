# AeroBrief — CS 1301 Web Development Labs 3 & 4

**Theme:** Student pilots, training-area weather and aviation ground school.  
**Pages:** Home, Flight Weather Explorer (Lab 3 data page), AeroTutor (Lab 3 AI chatbot), and a Lab 4 agent placeholder.

## 1. What this app does

The **Flight Weather Explorer** retrieves external forecast JSON from Open-Meteo. It processes hourly weather values with Python (not an LLM) and displays three interactive visualizations:

1. Modeled 10 m sustained winds versus gusts.
2. Cloud cover versus precipitation probability.
3. Estimated headwind and crosswind components for a user-selected heading.

Inputs include training airport/city selection, forecast length, runway heading, wind units and temperature units. A forecast table and CSV download are available. You can look up a specific city using the Open-Meteo Geocoding API; this supports a later Lab 4 tool.

The **AeroTutor Chatbot** uses a Pydantic AI `Agent` backed by Google Gemini (default model: `gemini-3.5-flash-lite`). The app saves the displayed messages and complete agent history in `st.session_state` and passes `message_history` to subsequent turns. It uses `st.chat_input`, `st.chat_message` and `try/except`. **It has no tools and does not access weather/API data in Lab 3**, as required by the assignment.

## 2. Folder layout

```text
WebDevLabs3_4/
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.example
├── images/
├── pages/
│   ├── 2_Flight_Weather.py
│   ├── 3_AeroTutor_Chatbot.py
│   └── 4_Agent.py              # Lab 4 placeholder only
├── tests/
│   └── test_aviation_data.py
├── Home_Page.py
├── aviation_data.py
├── site_theme.py
├── requirements.txt
├── PROJECT_PLAN.md
├── README.md
└── .gitignore
```

## 3. How to run on your computer

Open the `WebDevLabs3_4` folder in VS Code or Terminal.

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

**Windows PowerShell**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install streamlit
Copy-Item .streamlit\secrets.toml.example .streamlit\secrets.toml
```

Edit `.streamlit/secrets.toml` to contain the real Gemini key you create at <https://aistudio.google.com/apikey>:

```toml
GOOGLE_API_KEY = "PASTE_YOUR_OWN_KEY_HERE"
```

Run:

```bash
streamlit run Home_Page.py
```

The **weather data page works without a Gemini key**. The chatbot needs your own API key and network access. Its model is `gemini-3.5-flash-lite` (verify current model availability and limits in Google AI Studio). A free Gemini key may be subject to rate limits or changes in Google's free-tier availability.

## 4. Test and deploy

- Install `pytest` locally if desired: `pip install pytest`.
- Run `python -m pytest -q tests` from the project root for offline unit tests.
- Test the website: select a second airport, change the time window, change the runway heading, and verify both weather charts and wind components change.
- Test chat memory: say "My favorite trainer is the Cessna 172," then ask "What did I say my favorite trainer was?" Clear the conversation and try again.
- Test error handling: temporarily remove the Gemini key and ensure the chatbot displays a warning rather than crashing.
- Push all files **except** your real `.streamlit/secrets.toml` to GitHub. `.gitignore` already excludes it.
- On Streamlit Community Cloud, connect the repository, choose `Home_Page.py` as the main file, and add your own `GOOGLE_API_KEY` under **App settings → Secrets**.
- For Gradescope, submit the zipped project and the public deployed Streamlit URL. Follow the assignment instructions for team/partner submission and deadlines.

**Before submission:** Add your actual team number, section, and both member names to `Home_Page.py`. If needed, remove or expand the Lab 4 placeholder as instructed by your TA.

## 5. Data source verification

- **Geocoding:** <https://open-meteo.com/en/docs/geocoding-api> — query a city name, receive JSON matching cities and their coordinates.
- **Forecast:** <https://open-meteo.com/en/docs> — request hourly modeled wind speed, gusts, direction, cloud cover, precipitation probability, visibility, and temperature for coordinates.
- Both work without API keys for noncommercial/educational usage, subject to the service's licensing and fair-use terms.
- The responses are JSON, not a file approaching 100 MB; the app requests only a few days of hourly fields.
- **Pydantic AI:** <https://pydantic.dev/docs/ai/models/google/> and <https://pydantic.dev/docs/ai/core-concepts/message-history/>.
- **Streamlit:** <https://docs.streamlit.io/develop/api-reference/chat>.

## 6. Aviation disclaimer

Open-Meteo uses numerical weather model forecasts and **does not provide official airfield METARs or TAFs on this page**. The wind-component calculations use modeled 10 m wind, user-input heading, and no magnetic-variation correction. This project is for education only. It is **not** a flight dispatch tool or an operational go/no-go recommendation. For actual flights, obtain an official briefing from an approved weather source and follow your instructor's guidance.
