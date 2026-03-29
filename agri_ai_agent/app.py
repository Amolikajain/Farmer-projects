import streamlit as st
import requests
import google.generativeai as genai
import os
from voice_location import get_voice_input, get_location
from soil_api import get_soil_ph

# ---------------- API KEYS ----------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# ---------------- GEMINI SETUP ----------------
if not GEMINI_API_KEY:
    st.error("")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-2.5-flash")

# ---------------- MOCK AGRI DATA ----------------
mock_agri_data = {
    "Bhopal": {
        "soil": "Medium Black Soil",
        "price_trend": "Soybean demand is increasing"
    },
    "Nashik": {
        "soil": "Black Cotton Soil",
        "price_trend": "Onion prices are decreasing"
    },
    "Navi Mumbai": {
        "soil": "Laterite Soil",
        "price_trend": "Rice prices are high"
    }
}

# ---------------- WEATHER FUNCTION ----------------
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "main" not in data or "weather" not in data:
            st.error(f"Invalid response from weather API for city: {city}")
            return None, None, None

        temperature = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        description = data["weather"][0]["description"]
        return temperature, humidity, description

    except requests.exceptions.HTTPError as e:
        st.error(f"Weather API error: {e.response.status_code} - {e.response.json().get('message', 'Unknown error')}")
        return None, None, None
    except requests.exceptions.RequestException as e:
        st.error(f"Network error while fetching weather: {str(e)}")
        return None, None, None
    except (KeyError, IndexError) as e:
        st.error(f"Error parsing weather data: {str(e)}")
        return None, None, None

# ---------------- AI RESPONSE ----------------
def generate_ai_response(question, city, weather, soil, market, soil_ph=None):
    soil_ph_text = f"Soil pH: {soil_ph}" if soil_ph else "Soil pH: Not available"

    prompt = f"""
You are an expert Indian agriculture advisor.

A farmer from {city} asks:
"{question}"

Use ONLY this local information:

Weather:
- Temperature: {weather[0]}°C
- Humidity: {weather[1]}%
- Condition: {weather[2]}

Soil:
- Type: {soil}
- {soil_ph_text}

Market Trend:
- {market}

Give clear, practical farming advice in simple steps. Be concise and helpful.
"""
    response = model.generate_content(prompt)
    return response.text

# ---------------- SHOW ADVICE HELPER ----------------
def show_advice(question, city, soil_ph=None):
    if not question:
        st.warning("Please enter or speak a question.")
        return

    if city not in mock_agri_data:
        st.error(f"No local data available for {city}. Please select a supported city.")
        return

    weather = get_weather(city)
    if weather[0] is not None:
        soil = mock_agri_data.get(city, {}).get("soil", "Unknown soil type")
        market = mock_agri_data.get(city, {}).get("price_trend", "No market data available")
        answer = generate_ai_response(question, city, weather, soil, market, soil_ph)
        st.subheader("🌱 AI Recommendations")
        st.write(answer)
    else:
        st.error("Unable to fetch weather data. Please check the city name or try again.")

# ---------------- SESSION STATE INIT ----------------
if "question" not in st.session_state:
    st.session_state.question = ""

if "city" not in st.session_state:
    st.session_state.city = "Bhopal"

if "soil_ph" not in st.session_state:
    st.session_state.soil_ph = None

# ---------------- STREAMLIT UI ----------------
st.title("🌾 FarmMitra - Smart AI Farming Assistant")
st.write("Ask farming questions based on your local conditions.")

# -------- LOCATION --------
if st.button("📍 Detect My Location"):
    try:
        result = get_location()
        # Handle both (city, coords) and (lat, lon) return types safely
        if isinstance(result, tuple) and len(result) == 2:
            first, second = result
            if isinstance(first, str):
                # Returns (city, coords)
                st.session_state.city = first
                coords = second
                if isinstance(coords, (tuple, list)) and len(coords) == 2:
                    lat, lon = coords
                    st.session_state.soil_ph = get_soil_ph(lat, lon)
            elif isinstance(first, (int, float)):
                # Returns (lat, lon)
                lat, lon = first, second
                st.session_state.soil_ph = get_soil_ph(lat, lon)
        st.success(f"📍 Detected Location: {st.session_state.city}")
    except Exception as e:
        st.error(f"Location detection failed: {str(e)}")

city = st.selectbox(
    "Or select your city manually",
    ["Bhopal", "Nashik", "Navi Mumbai"],
    index=["Bhopal", "Nashik", "Navi Mumbai"].index(st.session_state.city)
    if st.session_state.city in ["Bhopal", "Nashik", "Navi Mumbai"] else 0
)
st.session_state.city = city

# Show soil pH if available
if st.session_state.soil_ph:
    st.info(f"🌱 Soil pH for your location: {st.session_state.soil_ph}")

# -------- VOICE INPUT --------
if st.button("🎤 Speak Your Question"):
    try:
        voice_text = get_voice_input()
        if voice_text:
            st.session_state.question = voice_text
            st.success(f"You said: {voice_text}")
        else:
            st.warning("Could not detect voice. Please try again.")
    except Exception as e:
        st.error(f"Voice input failed: {str(e)}")

# -------- QUESTION INPUT --------
question = st.text_input(
    "Enter your farming question",
    value=st.session_state.question,
    key="question_input"
)
# Sync text input back to session state
st.session_state.question = question

# -------- MAIN BUTTON --------
if st.button("🚀 Get AI Advice"):
    show_advice(st.session_state.question, st.session_state.city, st.session_state.soil_ph)
