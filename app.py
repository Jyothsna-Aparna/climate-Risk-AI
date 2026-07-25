import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium

import db

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Global Climate Risk & Early Warning AI Radar",
    page_icon="🌍",
    layout="wide",
)

db.init_db()

# ============================================================
# STYLING (foreground / background)
# ============================================================
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .risk-box {
        padding: 1.2rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        font-size: 1.05rem;
    }
    .risk-low { background-color: #143d2b; border: 1px solid #2ecc71; }
    .risk-medium { background-color: #4d3b12; border: 1px solid #f1c40f; }
    .risk-high { background-color: #4d1414; border: 1px solid #e74c3c; }
    .target-box {
        background-color: #113322;
        border-left: 4px solid #2ecc71;
        padding: 0.6rem 1rem;
        border-radius: 6px;
        margin-top: 0.5rem;
    }
    .pipeline-note {
        color: #888888;
        font-size: 0.8rem;
        margin-top: -0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# LANGUAGE STRINGS
# ============================================================
LANG = {
    "English": {
        "title": "🌍 Global Climate Risk & Early Warning AI Radar",
        "subtitle": "UNDP SDG 13 (Climate Action) | Real-Time Environmental Risk Intelligence",
        "select_lang": "Choose Language",
        "select_loc": "📍 Select Location",
        "enter_city": "Enter City (Global / India):",
        "target": "Target",
        "fetching": "Fetching live climate data...",
        "current_conditions": "Current Conditions",
        "temp": "Temperature",
        "humidity": "Humidity",
        "wind": "Wind Speed",
        "risk_level": "Overall Risk Level",
        "low": "LOW",
        "medium": "MODERATE",
        "high": "HIGH",
        "city_not_found": "City not found. Try a different spelling or add the country name (e.g. 'Hyderabad, India').",
        "api_error": "Could not fetch live data right now. Please try again in a moment.",
        "history": "Temperature History (from database)",
        "live": "🔴 Live data fetched just now",
        "cached": "🗄️ Served from database (last updated {mins} min ago)",
        "refresh_hours": "Pipeline refresh interval (hours)",
    },
    "తెలుగు": {
        "title": "🌍 గ్లోబల్ క్లైమేట్ రిస్క్ & ఎర్లీ వార్నింగ్ AI రాడార్",
        "subtitle": "UNDP SDG 13 (క్లైమేట్ యాక్షన్) | రియల్-టైమ్ ఎన్విరాన్మెంటల్ రిస్క్ ఇంటెలిజెన్స్",
        "select_lang": "భాష ఎంచుకోండి",
        "select_loc": "📍 ప్రదేశం ఎంచుకోండి",
        "enter_city": "నగరం నమోదు చేయండి (గ్లోబల్ / ఇండియా):",
        "target": "లక్ష్యం",
        "fetching": "లైవ్ క్లైమేట్ డేటా తీసుకుంటోంది...",
        "current_conditions": "ప్రస్తుత పరిస్థితులు",
        "temp": "ఉష్ణోగ్రత",
        "humidity": "తేమ",
        "wind": "గాలి వేగం",
        "risk_level": "మొత్తం రిస్క్ స్థాయి",
        "low": "తక్కువ",
        "medium": "మధ్యస్థం",
        "high": "అధికం",
        "city_not_found": "నగరం కనుగొనబడలేదు. వేరే స్పెల్లింగ్ ప్రయత్నించండి లేదా దేశం పేరు జోడించండి.",
        "api_error": "ప్రస్తుతం లైవ్ డేటా తీసుకోలేకపోయాం. కొద్ది సేపటిలో మళ్ళీ ప్రయత్నించండి.",
        "history": "ఉష్ణోగ్రత చరిత్ర (డేటాబేస్ నుండి)",
        "live": "🔴 ఇప్పుడే లైవ్ డేటా తీసుకోబడింది",
        "cached": "🗄️ డేటాబేస్ నుండి ({mins} నిమిషాల క్రితం అప్డేట్ అయింది)",
        "refresh_hours": "పైప్‌లైన్ రిఫ్రెష్ ఇంటర్వల్ (గంటలు)",
    },
}

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("## 🌍⚡ EARLY-WARNING AI")
    st.caption("Global SDG 13 Intelligence Radar")

    lang_choice = st.selectbox("🌐 " + LANG["English"]["select_lang"], list(LANG.keys()))
    t = LANG[lang_choice]

    st.markdown(f"### {t['select_loc']}")
    city = st.text_input(t["enter_city"], value="Hyderabad")

    refresh_hours = st.slider(t["refresh_hours"], min_value=1, max_value=24, value=3)

# ============================================================
# MAIN TITLE
# ============================================================
st.markdown(f"<h1 style='text-align:center;color:#5dade2;'>{t['title']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center;color:#bbbbbb;'>{t['subtitle']}</p>", unsafe_allow_html=True)


# ============================================================
# EXTERNAL DATA FETCH (no API key needed — Open-Meteo)
# ============================================================
def geocode_city(city_name: str):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    resp = requests.get(url, params={"name": city_name, "count": 1}, timeout=10)
    resp.raise_for_status()
    payload = resp.json()
    results = payload.get("results")
    if not results:
        return None
    place = results[0]
    return {
        "name": place.get("name"),
        "country": place.get("country"),
        "lat": place.get("latitude"),
        "lon": place.get("longitude"),
    }


def fetch_weather(lat: float, lon: float):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation",
        "timezone": "auto",
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    payload = resp.json()
    if "current" not in payload:
        return None
    return payload["current"]


def compute_risk(temp, wind, precip):
    temp = temp or 0
    wind = wind or 0
    precip = precip or 0
    score = 0
    if temp >= 40 or temp <= 2:
        score += 2
    elif temp >= 35 or temp <= 5:
        score += 1
    if wind >= 40:
        score += 2
    elif wind >= 25:
        score += 1
    if precip >= 20:
        score += 2
    elif precip >= 5:
        score += 1
    if score >= 4:
        return "high"
    elif score >= 2:
        return "medium"
    return "low"


# ============================================================
# PIPELINE: reuse DB record if fresh, else fetch + store
# ============================================================
def run_pipeline(city_name: str, max_age_hours: float):
    latest = db.get_latest_reading(city_name)

    if latest is not None and not db.is_stale(latest["fetched_at"], max_age_hours):
        return latest, False  # served from DB, not a fresh fetch

    location = geocode_city(city_name)
    if location is None:
        return None, None

    current = fetch_weather(location["lat"], location["lon"])
    if current is None:
        return None, None

    temp = current.get("temperature_2m")
    humidity = current.get("relative_humidity_2m")
    wind = current.get("wind_speed_10m")
    precip = current.get("precipitation")
    risk = compute_risk(temp, wind, precip)

    db.insert_reading(
        city=city_name,
        country=location["country"],
        lat=location["lat"],
        lon=location["lon"],
        temperature=temp,
        humidity=humidity,
        wind_speed=wind,
        precipitation=precip,
        risk_level=risk,
    )

    fresh = db.get_latest_reading(city_name)
    return fresh, True


# ============================================================
# MAIN FLOW
# ============================================================
if city.strip():
    with st.spinner(t["fetching"]):
        reading, was_fresh_fetch = run_pipeline(city.strip(), refresh_hours)

    if reading is None:
        st.error(t["city_not_found"] + " / " + t["api_error"])
    else:
        st.markdown(
            f"<div class='target-box'>📍 <b>{t['target']}:</b> {reading['city']}, {reading['country']}</div>",
            unsafe_allow_html=True,
        )

        from datetime import datetime
        fetched_dt = datetime.fromisoformat(reading["fetched_at"])
        mins_ago = int((datetime.utcnow() - fetched_dt).total_seconds() // 60)

        if was_fresh_fetch:
            st.caption(t["live"])
        else:
            st.caption(t["cached"].format(mins=mins_ago))

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader(t["current_conditions"])
            m1, m2, m3 = st.columns(3)
            m1.metric(t["temp"], f"{reading['temperature']} °C")
            m2.metric(t["humidity"], f"{reading['humidity']} %")
            m3.metric(t["wind"], f"{reading['wind_speed']} km/h")

            risk = reading["risk_level"]
            st.markdown(
                f"<div class='risk-box risk-{risk}'><b>{t['risk_level']}:</b> {t[risk]}</div>",
                unsafe_allow_html=True,
            )

        with col2:
            fmap = folium.Map(location=[reading["lat"], reading["lon"]], zoom_start=8, tiles="CartoDB dark_matter")
            folium.Marker(
                [reading["lat"], reading["lon"]],
                tooltip=f"{reading['city']}, {reading['country']}",
                icon=folium.Icon(color="red"),
            ).add_to(fmap)
            st_folium(fmap, height=350, width=None)

        # ------------------------------------------------------
        # HISTORY FROM DATABASE
        # ------------------------------------------------------
        history = db.get_history(reading["city"], limit=50)
        if len(history) >= 2:
            st.subheader(t["history"])
            df = pd.DataFrame(history)
            df["fetched_at"] = pd.to_datetime(df["fetched_at"])
            df = df.set_index("fetched_at")
            st.line_chart(df[["temperature"]])
else:
    st.info(t["enter_city"])