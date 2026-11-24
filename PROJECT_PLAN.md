# AeroBrief — Lab 3 Dream Project Plan (GenAI-assisted revised draft)

> **Academic integrity note:** This is an AI-assisted **revised plan** reference. The class requires **Part 1 — Initial Plan (No GenAI)** to be written independently *before* coding or using AI. Do not represent this draft as your no-AI plan or invent a reflection about your own work.

## A. Theme and motivation

**AeroBrief: Student Pilot Flight Weather Explorer + AeroTutor.** The audience is student pilots studying private-pilot ground-school concepts. Aviation uses software to process observations, forecasts, performance data, and operational information; this project explores the weather-literacy part of that field.

## B. Data source checked and chosen

**Provider:** Open-Meteo. The app accesses two related free public services:

- City lookup: `https://geocoding-api.open-meteo.com/v1/search?name=Atlanta&count=8&language=en&format=json`
- Hourly weather: `https://api.open-meteo.com/v1/forecast?latitude=33.64&longitude=-84.43&hourly=temperature_2m,wind_speed_10m,wind_gusts_10m,wind_direction_10m,cloud_cover,precipitation_probability,visibility&forecast_days=4&timezone=auto&wind_speed_unit=kn`

Official source: [Open-Meteo forecast documentation](https://open-meteo.com/en/docs), [geocoding documentation](https://open-meteo.com/en/docs/geocoding-api).

**Why this satisfies the project-data checklist:** API exists, responds in JSON, has no key requirement for the selected educational use, supports specific city lookup by name, exposes meaningful forecast fields, and makes enough hourly records for charts and questions. **Verify access and current service terms yourself before submitting**, as the assignment instructs.

**Limitations:** The data represent model forecasts, not airport official weather reports or regulatory flight minima. Never present them as an operational weather briefing.

## C. Three to five planned data features

1. Choose a training airport or search any city; show the matched location.
2. Select an upcoming 6–48 hour time window; filter the hourly forecast accordingly.
3. Compare sustained wind against modeled gusts on a chart, and display important summary metrics.
4. Compare cloud cover and precipitation probability over the same selected hours.
5. Change a runway heading to see calculated headwind and crosswind components; inspect and export a CSV table.

## D. Lab 3 chatbot goals

AeroTutor is a tool-free Pydantic AI/Gemini learning assistant. It can explain aviation weather terms, review basic student-pilot concepts and remember facts from the current conversation. It does not have live data tools and should say it cannot retrieve exact current conditions.

## E. Example questions for the *Lab 4* future agent

1. "What are the highest modeled gusts around Atlanta in the next 12 hours?"
2. "For Daytona Beach, which hours have the highest forecast cloud cover?"
3. "What is the estimated crosswind for a selected runway heading in Denver?"

These require a tool that calls the **same Open-Meteo data source**, not the no-tools Lab 3 chatbot.

## F. Decision log (suggested entries; verify against your actual process)

| Decision | Considered | Suggested reasoning |
|---|---|---|
| Topic | General weather vs pilot weather literacy | Pilot-focused examples align with interest in aviation training. |
| Data | Weather forecasts vs official airport METAR API | Hourly modeled values make two continuously updating charts practical; label clearly as *not a flight briefing*. |
| Interface | One static plot vs interactive controls | Multiple location/time/heading controls satisfy the lab's dynamic inputs requirement. |
| Chatbot | Tool-free tutor vs data-connected assistant | Lab 3 specifically requires no tools; tools are for Lab 4. |
| Security | Embed API key in code vs Streamlit secrets | Secrets should be stored locally and configured separately in deployment. |

## G. Reflection notes — complete in your own words

- What ideas did you propose independently before using GenAI?
- Which AI suggestions did you accept, reject, or modify, and why?
- What did you personally implement, test, debug or improve?
- What did you learn about testing API response fields, using an LLM safely, and managing secrets?
- How did your teammate contribute, and how did you verify the deployed app worked?
