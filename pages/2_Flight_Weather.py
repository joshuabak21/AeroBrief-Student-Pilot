"""Weather explorer: users choose a location and study changing forecasts."""

import altair as alt
import pandas as pd
import requests
import streamlit as st

from aviation_data import AIRPORTS, search_cities, get_forecast, extract_forecast, convert_wind_columns
from site_theme import apply_theme, safety_note

st.set_page_config(page_title="AeroBrief | Weather Explorer", page_icon="📈", layout="wide")
apply_theme()


@st.cache_data(ttl=3600)
def find_cities(name):
    return search_cities(name)


@st.cache_data(ttl=900)
def load_weather(lat, lon, temperature_unit):
    return get_forecast(lat, lon, temperature_unit)


def draw_chart(table, columns, title, units, colors):
    """Draw a line chart using the chosen columns of a table."""
    chart_data = table[["Local time"] + columns].melt(
        id_vars="Local time", var_name="Weather variable", value_name="Value"
    )
    chart = alt.Chart(chart_data).mark_line(point=True).encode(
        x=alt.X("Local time:T", title="Local time"),
        y=alt.Y("Value:Q", title=units),
        color=alt.Color("Weather variable:N", scale=alt.Scale(range=colors)),
        tooltip=["Local time:T", "Weather variable:N", "Value:Q"],
    ).properties(title=title, height=280).interactive()
    st.altair_chart(chart, use_container_width=True)


st.markdown('<div class="ab-kicker">01 / Real-world aviation-related data</div>', unsafe_allow_html=True)
st.title("Flight Weather Explorer")
st.markdown(
    '<p class="ab-lead">Explore winds, gusts, visibility, clouds, and runway wind components.</p>',
    unsafe_allow_html=True,
)
safety_note()

st.subheader("Choose a training location")
choice = st.selectbox("Airport preset or city search", list(AIRPORTS) + ["Search for a city..."])

if choice == "Search for a city...":
    city = st.text_input("City name", "Atlanta")
    if len(city.strip()) < 2:
        st.info("Type at least two characters.")
        st.stop()
    try:
        places = find_cities(city)
    except requests.RequestException:
        st.error("City search is unavailable. Please try again.")
        st.stop()
    if not places:
        st.warning("No matching cities found.")
        st.stop()
    location = st.selectbox(
        "Choose a result",
        places,
        format_func=lambda place: f"{place['name']}, {place['region']}, {place['country']}",
    )
    location_name = f"{location['name']}, {location['country']}"
else:
    location = AIRPORTS[choice]
    location_name = location["name"]

first, second, third, fourth = st.columns(4)
with first:
    hours = st.slider("Upcoming forecast hours", 6, 48, 24, 6)
with second:
    heading = st.selectbox("Runway heading (° true)*", list(range(0, 360, 10)), index=9)
with third:
    wind_unit = st.selectbox("Wind unit", ["knots", "mph"])
with fourth:
    temp_unit = st.selectbox("Temperature", ["°F", "°C"])

st.caption("*Use a TRUE heading for this demonstration. Runway designations are usually magnetic.")

try:
    api_temp = "fahrenheit" if temp_unit == "°F" else "celsius"
    with st.spinner("Loading forecast..."):
        data = load_weather(location["lat"], location["lon"], api_temp)
    rows = extract_forecast(data, hours=hours, runway_heading=heading)
    rows, shown_unit = convert_wind_columns(rows, wind_unit)
except (requests.RequestException, ValueError, KeyError, TypeError):
    st.error("The weather forecast could not be loaded. Please try again.")
    st.stop()

# Rename the wind columns if the visitor chooses miles per hour.
wind_names = ["Wind", "Gust", "Headwind", "Crosswind"]
for row in rows:
    for name in wind_names:
        old = f"{name} (kt)"
        new = f"{name} ({shown_unit})"
        if old != new:
            row[new] = row.pop(old)

weather = pd.DataFrame(rows)
wind = f"Wind ({shown_unit})"
gust = f"Gust ({shown_unit})"
headwind = f"Headwind ({shown_unit})"
crosswind = f"Crosswind ({shown_unit})"

st.subheader(location_name)
st.caption(f"Modeled hourly weather in {data.get('timezone', 'local')} time; not official airport observations.")

m1, m2, m3, m4 = st.columns(4)
m1.metric("First-hour wind", f"{weather[wind].iloc[0]:.1f} {shown_unit}" if pd.notna(weather[wind].iloc[0]) else "N/A")
m2.metric("Peak gust", f"{weather[gust].max():.1f} {shown_unit}" if weather[gust].notna().any() else "N/A")
m3.metric("Lowest visibility", f"{weather['Visibility (sm)'].min():.1f} sm" if weather['Visibility (sm)'].notna().any() else "N/A")
m4.metric("Highest rain chance", f"{weather['Rain chance (%)'].max():.0f}%" if weather['Rain chance (%)'].notna().any() else "N/A")

st.divider()
st.subheader("Weather changes over time")

draw_chart(weather, [wind, gust], "Surface winds and gusts", shown_unit, ["#63d5d3", "#f5b66a"])
draw_chart(weather, ["Cloud cover (%)", "Rain chance (%)"], "Clouds and chance of rain", "Percent", ["#8ea7ff", "#f5b66a"])

st.subheader("Runway wind component practice")
draw_chart(weather, [headwind, crosswind], f"Wind components for heading {heading:03d}°", shown_unit, ["#63d5d3", "#f5b66a"])
st.caption("A negative headwind means tailwind. Crosswind is shown as a magnitude, not left or right.")

with st.expander("View or download the forecast table"):
    table = weather.copy()
    table["Local time"] = table["Local time"].dt.strftime("%Y-%m-%d %H:%M")
    table.rename(columns={"Temperature": f"Temperature ({temp_unit})"}, inplace=True)
    st.dataframe(table, use_container_width=True, hide_index=True)
    st.download_button(
        "Download CSV", table.to_csv(index=False), "aerobrief_training_forecast.csv", "text/csv"
    )

st.caption("Source: Open-Meteo (open-meteo.com). For actual flight planning, use official aviation weather and consult a CFI.")
