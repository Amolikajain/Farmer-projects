import streamlit as st
import requests
import google.generativeai as genai
import os
from voice_location import get_voice_input, get_location

# ---------------- API KEYS ----------------


# ---------------- GEMINI SETUP ----------------

if not GEMINI_API_KEY:
    st.error("⚠️ GEMINI API key not found. Please set it using environment variables.")

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
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()

        # Check if the response contains required keys
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

def generate_ai_response(question, city, weather, soil, market):

    prompt = f"""
You are an expert Indian agriculture advisor.

A farmer from {city} asks:
"{question}"

Use ONLY this local information:

Weather:
Temperature: {weather[0]}°C
Humidity: {weather[1]}%
Condition: {weather[2]}

Soil:
{soil}

Market Trend:
{market}

Give clear farming advice in simple steps.
"""

    response = model.generate_content(prompt)

    return response.text

# ---------------- STREAMLIT UI ----------------

st.title("🌾 Smart AI Farming Assistant")
st.write("Ask farming questions based on your local conditions.")

# -------- LOCATION --------

city = None

if st.button("📍 Detect My Location"):
    city, coords = get_location()
    st.success(f"Detected Location: {city}")

if not city:
    city = st.selectbox(
        "Or select your city manually",
        ["Bhopal", "Nashik", "Navi Mumbai"]
    )

# -------- QUESTION INPUT --------

question = st.text_input("Enter your farming question", key="question_input")

# -------- VOICE INPUT --------

if st.button("🎤 Speak"):
    question = get_voice_input()
    st.write("You said:", question)

    if question:
        weather = get_weather(city)

        if weather[0] is not None:
            soil = mock_agri_data[city]["soil"]
            market = mock_agri_data[city]["price_trend"]

            answer = generate_ai_response(question, city, weather, soil, market)

            st.subheader("🌱 AI Recommendations")
            st.write(answer)
        else:
            st.error("Unable to fetch weather data. Please check the city name or try again.")

# -------- MAIN BUTTON --------

if st.button("Get AI Advice"):

    if not question:
        st.warning("Please enter or speak a question.")
    else:
        weather = get_weather(city)

        if weather[0] is not None:
            soil = mock_agri_data[city]["soil"]
            market = mock_agri_data[city]["price_trend"]

            answer = generate_ai_response(question, city, weather, soil, market)

            st.subheader("🌱 AI Recommendations")
            st.write(answer)
        else:
            st.error("Unable to fetch weather data. Please check the city name or try again.")