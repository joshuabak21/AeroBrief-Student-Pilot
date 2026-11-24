"""Lab 3 Page 1: data fetched, analyzed and visualized by Python only."""

import altair as alt
import pandas as pd
import requests
import streamlit as st

from aviation_data import AIRPORTS, convert_wind_columns, extract_forecast, get_forecast, search_cities
from site_theme import apply_theme, safety_note

st.set_page_config(page_title="AeroBrief | Weather Explorer", page_icon="📈", layout="wide")
apply_theme()


@st.cache_data(ttl=3600, show_spinner=False)
def cached_search(name):
    return search_cities(name)


@st.cache_data(ttl=900, show_spinner=False)
def cached_forecast(latitude, longitude, temperature_unit):
    return get_forecast(latitude, longitude, temperature_unit)


st.markdown('<div class="ab-kicker">01 / Real-world aviation-related data</div>', unsafe_allow_html=True)
st.title("Flight Weather Explorer")
st.markdown(
    '<p class="ab-lead">Practice reading the weather factors that student pilots think about: '
    'surface wind, gusts, visibility, cloudiness, and runway wind components.</p>',
    unsafe_allow_html=True,
)
safety_note()

st.subheader("Choose a training location")
preset = st.selectbox(
    "Airport preset or city search",
    list(AIRPORTS.keys()) + ["Search for a city..."],
    index=0,
)

if preset == "Search for a city...":
    query = st.text_input("City name", value="Atlanta", help="Try Atlanta, Daytona Beach, Denver, or San Diego.")
    if len(query.strip()) < 2:
        st.info("Enter at least two characters to search for a city.")
        st.stop()
    try:
        places = cached_search(query)
    except (requests.RequestException, ValueError) as exc:
        st.error("City lookup is temporarily unavailable. Try again later.")
        st.caption(f"Technical detail: {exc}")
        st.stop()
    if not places:
        st.warning("No matching cities found. Try a more specific search.")
        st.stop()
    selected = st.selectbox(
        "Select the matching city",
        range(len(places)),
        format_func=lambda i: ", ".join(
            part for part in (places[i]["name"], places[i]["region"], places[i]["country"]) if part
        ),
    )
    location = places[selected]
    location_label = ", ".join(
        part for part in (location["name"], location["region"], location["country"]) if part
    )
else:
    location = AIRPORTS[preset]
    location_label = location["name"]

control1, control2, control3, control4 = st.columns([1.2, 1, 1, 1])
with control1:
    hours = st.slider("Upcoming forecast hours", min_value=6, max_value=48, value=24, step=6)
with control2:
    runway_heading = st.selectbox("Runway direction (° true, approximate)*", [i * 10 for i in range(36)], index=9)
with control3:
    wind_unit = st.selectbox("Wind speed display", ["knots", "mph"])
with control4:
    temperature_display = st.selectbox("Temperature display", ["°F", "°C"])

st.caption("*Enter an approximate TRUE runway direction for a conceptual wind-component exercise. Runway designations are generally magnetic; this exercise does not correct for magnetic variation.")

try:
    temp_api_unit = "fahrenheit" if temperature_display == "°F" else "celsius"
    with st.spinner("Retrieving forecast from Open-Meteo..."):
        payload = cached_forecast(location["lat"], location["lon"], temp_api_unit)
    rows = extract_forecast(payload, hours=hours, runway_heading=runway_heading)
    rows, shown_unit = convert_wind_columns(rows, wind_unit)
except (requests.RequestException, KeyError, TypeError, ValueError) as exc:
    st.error("We couldn't load the weather forecast. Check your connection and try again.")
    st.caption(f"Technical detail: {exc}")
    st.stop()

wind_col = f"Wind ({shown_unit})"
gust_col = f"Gust ({shown_unit})"
headwind_col = f"Headwind ({shown_unit})"
crosswind_col = f"Crosswind ({shown_unit})"
for row in rows:
    for old, new in (
        ("Wind (kt)", wind_col),
        ("Gust (kt)", gust_col),
        ("Headwind (kt)", headwind_col),
        ("Crosswind (kt)", crosswind_col),
    ):
        if old != new:
            row[new] = row.pop(old)

frame = pd.DataFrame(rows)
local_tz = payload.get("timezone", "local")
st.markdown(f"### {location_label}")
st.caption(f"Forecast hours shown in {local_tz} local time. Data are modeled hourly forecasts, not airport observations.")

speed_values = frame[wind_col].dropna()
gust_values = frame[gust_col].dropna()
visibility_values = frame["Visibility (sm)"].dropna()
rain_values = frame["Rain chance (%)"].dropna()

m1, m2, m3, m4 = st.columns(4)
m1.metric("First-hour forecast wind", f"{float(speed_values.iloc[0]):.1f} {shown_unit}" if not speed_values.empty else "N/A")
m2.metric("Peak modeled gust", f"{float(gust_values.max()):.1f} {shown_unit}" if not gust_values.empty else "N/A")
m3.metric("Lowest modeled visibility", f"{float(visibility_values.min()):.1f} sm" if not visibility_values.empty else "N/A")
m4.metric("Highest rain probability", f"{float(rain_values.max()):.0f}%" if not rain_values.empty else "N/A")

st.divider()
st.subheader("Changing weather across the selected forecast window")

COLOR_RANGE = ["#63d5d3", "#f5b66a"]

# Visual 1: dynamically updated with location, wind-unit choice, and time window.
wind_long = frame[["Local time", wind_col, gust_col]].melt(
    id_vars=["Local time"], var_name="Measure", value_name="Speed"
)
wind_chart = (
    alt.Chart(wind_long)
    .mark_line(point=True, strokeWidth=2.5)
    .encode(
        x=alt.X("Local time:T", title=f"Local time ({local_tz})", axis=alt.Axis(format="%a %I %p")),
        y=alt.Y("Speed:Q", title=f"Modeled speed ({shown_unit})", scale=alt.Scale(zero=True)),
        color=alt.Color("Measure:N", scale=alt.Scale(range=COLOR_RANGE)),
        tooltip=[alt.Tooltip("Local time:T", title="Local"), "Measure:N", alt.Tooltip("Speed:Q", format=".1f")],
    )
    .properties(height=300, title="Surface wind vs. gusts")
    .interactive()
)
st.altair_chart(wind_chart, use_container_width=True)
st.caption("Winds and gusts are modeled near-surface values; actual runway winds may differ.")

# Visual 2: dynamically updated probability and cloud forecast.
cloud_long = frame[["Local time", "Cloud cover (%)", "Rain chance (%)"]].melt(
    id_vars=["Local time"], var_name="Measure", value_name="Percent"
)
cloud_chart = (
    alt.Chart(cloud_long)
    .mark_area(opacity=0.24, line={"strokeWidth": 2.5})
    .encode(
        x=alt.X("Local time:T", title=f"Local time ({local_tz})", axis=alt.Axis(format="%a %I %p")),
        y=alt.Y("Percent:Q", title="Percent", scale=alt.Scale(domain=[0, 100])),
        color=alt.Color("Measure:N", scale=alt.Scale(range=["#8ea7ff", "#f5b66a"])),
        tooltip=[alt.Tooltip("Local time:T", title="Local"), "Measure:N", alt.Tooltip("Percent:Q", format=".0f")],
    )
    .properties(height=280, title="Cloud cover and precipitation probability")
    .interactive()
)
st.altair_chart(cloud_chart, use_container_width=True)

# Visual 3: runway-heading selector changes this educational calculation.
st.subheader("Runway wind component practice")
col_chart, col_info = st.columns([2.2, 1], gap="large")
with col_chart:
    components = frame[["Local time", headwind_col, crosswind_col]].melt(
        id_vars=["Local time"], var_name="Measure", value_name="Component"
    )
    components_chart = (
        alt.Chart(components)
        .mark_line(point=True, strokeWidth=2.5)
        .encode(
            x=alt.X("Local time:T", title=f"Local time ({local_tz})", axis=alt.Axis(format="%a %I %p")),
            y=alt.Y("Component:Q", title=f"Wind component ({shown_unit})"),
            color=alt.Color("Measure:N", scale=alt.Scale(range=["#63d5d3", "#f5b66a"])),
            tooltip=[alt.Tooltip("Local time:T", title="Local"), "Measure:N", alt.Tooltip("Component:Q", format=".1f")],
        )
        .properties(height=275, title=f"Estimated components for heading {runway_heading:03d}°")
        .interactive()
    )
    st.altair_chart(components_chart, use_container_width=True)
with col_info:
    st.markdown("**How to interpret the signs**")
    st.write("Positive headwind = wind opposing the aircraft's direction. Negative headwind = tailwind component.")
    st.write("Crosswind is shown as an absolute magnitude and does not indicate left or right.")
    st.info("Educational approximation only: model winds are not a substitute for runway-specific METAR, ATIS, or airport weather.")

with st.expander("View the forecast table and download the data"):
    table = frame.copy()
    table["Local time"] = table["Local time"].dt.strftime("%Y-%m-%d %H:%M")
    table.rename(columns={"Temperature": f"Temperature ({temperature_display})"}, inplace=True)
    st.dataframe(table, use_container_width=True, hide_index=True)
    st.download_button(
        "Download selected forecast as CSV",
        data=table.to_csv(index=False).encode("utf-8"),
        file_name="aerobrief_training_forecast.csv",
        mime="text/csv",
    )

st.markdown("**Learning prompts:** How do gusts differ from sustained wind? What is a crosswind? Why does visibility matter under VFR?")
st.caption("Source: Open-Meteo Forecast API (https://open-meteo.com/en/docs). For real flight weather, consult https://aviationweather.gov/ and https://www.1800wxbrief.com/.")
