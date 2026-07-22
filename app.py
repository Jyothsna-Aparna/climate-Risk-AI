import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import pandas as pd

st.set_page_config(
    page_title="Global Climate Risk Radar | Early-Warning AI", 
    page_icon="🌍", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size:2.2rem;
        font-weight:700;
        color:#006699;
        text-align:center;
        margin-bottom:0px;
    }
    .sub-header {
        font-size:1.0rem;
        text-align:center;
        color:#555555;
        margin-bottom:20px;
    }
    </style>
""", unsafe_allow_html=True)

# Multilingual Translations
TRANSLATIONS = {
    "English": {
        "title": "🌍 Global Climate Risk & Early Warning AI Radar",
        "subtitle": "UNDP SDG 13 (Climate Action) | Real-Time Environmental Risk Intelligence",
        "select_loc": "📍 Select Location",
        "enter_city": "Enter City (Global / India):",
        "temp": "Temperature",
        "humidity": "Humidity",
        "rain": "Rainfall",
        "wind": "Wind Speed",
        "threat_level": "🚨 AI Risk Assessment Engine",
        "overall_risk": "Overall Threat Score",
        "flood": "Flood Threat",
        "heat": "Extreme Heat Threat",
        "wildfire": "Wildfire Hazard",
        "action_alert": "💡 AI Emergency Recommendation",
        "high_risk": "🔴 HIGH RISK: Deploy Immediate Climate Emergency Services!",
        "mod_risk": "🟡 MODERATE RISK: Continuous Monitoring & Early Warning Active.",
        "low_risk": "🟢 LOW RISK: Stable Environmental Conditions.",
        "map_title": "🗺️ Live Geo-Spatial Climate Threat Radar"
    },
    "Telugu (తెలుగు)": {
        "title": "🌍 గ్లోబల్ క్లైమేట్ రిస్క్ & ఎర్లీ వార్నింగ్ AI రాడార్",
        "subtitle": "UNDP SDG 13 (వాతావరణ చర్య) | ప్రత్యక్ష పర్యావరణ ముప్పు అంచనా",
        "select_loc": "📍 ప్రాంతాన్ని ఎంచుకోండి",
        "enter_city": "నగరం పేరు టైప్ చేయండి (భారతదేశం / ప్రపంచం):",
        "temp": "ఉష్ణోగ్రత",
        "humidity": "తేమ (Humidity)",
        "rain": "వర్షపాతం",
        "wind": "గాలి వేగం",
        "threat_level": "🚨 AI రిస్క్ అసెస్మెంట్ ఇంజిన్",
        "overall_risk": "మొత్తం ముప్పు స్కోర్",
        "flood": "వరద ప్రమాదం",
        "heat": "తీవ్రమైన వేడి ప్రమాదం",
        "wildfire": "అడవి కార్చిచ్చు ప్రమాదం",
        "action_alert": "💡 AI అత్యవసర సూచనలు",
        "high_risk": "🔴 తీవ్రమైన ప్రమాదం: తక్షణ అత్యవసర చర్యలు చేపట్టండి!",
        "mod_risk": "🟡 మితమైన ప్రమాదం: నిరంతర పర్యవేక్షణ అవసరం.",
        "low_risk": "🟢 సాధారణ ప్రమాదం: పర్యావరణ పరిస్థితులు సాధారణంగా ఉన్నాయి.",
        "map_title": "🗺️ లైవ్ జియో-స్పేషియల్ క్లైమేట్ మ్యాప్"
    },
    "Hindi (हिंदी)": {
        "title": "🌍 वैश्विक जलवायु जोखिम एवं प्रारंभिक चेतावनी AI रडार",
        "subtitle": "UNDP SDG 13 (जलवायु कार्रवाई) | वास्तविक समय पर्यावरण जोखिम मूल्यांकन",
        "select_loc": "📍 स्थान चुनें",
        "enter_city": "शहर का नाम दर्ज करें (भारत / वैश्विक):",
        "temp": "तापमान",
        "humidity": "आर्द्रता",
        "rain": "वर्षा",
        "wind": "हवा की गति",
        "threat_level": "🚨 AI जोखिम मूल्यांकन इंजन",
        "overall_risk": "कुल जोखिम स्कोर",
        "flood": "बाढ़ का खतरा",
        "heat": "अत्यधिक गर्मी का खतरा",
        "wildfire": "दावानल का खतरा",
        "action_alert": "💡 AI अनुशंसित आपातकालीन कार्रवाई",
        "high_risk": "🔴 उच्च जोखिम: तत्काल जलवायु आपातकालीन सेवाएं तैनात करें!",
        "mod_risk": "🟡 मध्यम जोखिम: सतत निगरानी जारी रखें।",
        "low_risk": "🟢 कम जोखिम: सामान्य पर्यावरणीय स्थिति।",
        "map_title": "🗺️ लाइव जियो-स्पेशियल क्लाइमेट मैप"
    }
}

# Sidebar Banner
st.sidebar.markdown("""
    <div style="text-align: center; padding: 12px; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); border-radius: 10px; color: white; margin-bottom: 15px;">
        <h2 style="margin:0; font-size: 26px;">🌍⚡</h2>
        <h3 style="margin:4px 0 0 0; color: #4fc3f7; font-size: 15px;">EARLY-WARNING AI</h3>
        <p style="margin:2px 0 0 0; font-size: 11px; opacity: 0.8;">Global SDG 13 Intelligence Radar</p>
    </div>
""", unsafe_allow_html=True)

lang = st.sidebar.selectbox("🌐 Choose Language / భాష", ["English", "Telugu (తెలుగు)", "Hindi (हिंदी)"])
t = TRANSLATIONS[lang]

st.sidebar.header(t["select_loc"])
city = st.sidebar.text_input(t["enter_city"], "Hyderabad")

def get_coordinates(city_name):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
    res = requests.get(url).json()
    if res.get("results"):
        loc = res["results"][0]
        return loc["latitude"], loc["longitude"], loc["name"], loc.get("country", "")
    return None, None, None, None

lat, lon, name, country = get_coordinates(city)

st.markdown(f"<div class='main-header'>{t['title']}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='sub-header'>{t['subtitle']}</div>", unsafe_allow_html=True)

if lat and lon:
    st.sidebar.success(f"📍 Target: **{name}, {country}**")
    
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m&hourly=temperature_2m,precipitation&forecast_days=1"
    data = requests.get(weather_url).json()
    
    curr = data['current']
    temp = curr['temperature_2m']
    humidity = curr['relative_humidity_2m']
    precip = curr['precipitation']
    wind = curr['wind_speed_10m']

    flood_risk = min(100, int((precip / 15.0) * 100)) if precip > 0 else 5
    heat_risk = min(100, int(((temp - 30) / 15.0) * 100)) if temp > 30 else 8
    fire_risk = min(100, int(((temp / 40.0) * 0.5 + (100 - humidity)/100.0 * 0.5) * 100)) if temp > 32 and humidity < 35 else 12

    overall_score = max(flood_risk, heat_risk, fire_risk)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(t["temp"], f"{temp} °C")
    m2.metric(t["humidity"], f"{humidity} %")
    m3.metric(t["rain"], f"{precip} mm")
    m4.metric(t["wind"], f"{wind} km/h")

    st.markdown("---")

    col_map, col_risk = st.columns([1.8, 1.2])

    with col_risk:
        st.subheader(t["threat_level"])
        st.write(f"### {t['overall_risk']}: `{overall_score}%`")
        
        st.write(f"🌊 **{t['flood']}**")
        st.progress(flood_risk / 100)
        
        st.write(f"☀️ **{t['heat']}**")
        st.progress(heat_risk / 100)
        
        st.write(f"🔥 **{t['wildfire']}**")
        st.progress(fire_risk / 100)

        st.markdown("---")
        st.subheader(t["action_alert"])
        if overall_score > 60:
            st.error(t["high_risk"])
        elif overall_score > 30:
            st.warning(t["mod_risk"])
        else:
            st.success(t["low_risk"])

    with col_map:
        st.subheader(t["map_title"])
        map_color = "red" if overall_score > 60 else ("orange" if overall_score > 30 else "green")
        m = folium.Map(location=[lat, lon], zoom_start=9)
        
        folium.Circle(
            location=[lat, lon],
            radius=15000,
            color=map_color,
            fill=True,
            fill_color=map_color,
            fill_opacity=0.3,
            popup=f"{name}: {overall_score}% Threat Score"
        ).add_to(m)

        st_folium(m, width="100%", height=400)

    st.markdown("---")
    st.subheader("📈 24-Hour Analytics Trend")
    hourly_df = pd.DataFrame({
        "Time": [f"{i}:00" for i in range(24)],
        "Temp (°C)": data['hourly']['temperature_2m'][:24],
        "Rain (mm)": data['hourly']['precipitation'][:24]
    })
    st.line_chart(hourly_df.set_index("Time"))

else:
    st.error("Invalid City Name!")
    