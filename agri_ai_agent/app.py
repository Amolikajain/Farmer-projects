import streamlit as st
import requests
import google.generativeai as genai
from voice_location import get_voice_input, get_location

# ---------------- API KEYS ----------------

GEMINI_API_KEY = "AIzaSyCSTod3nH_b86kGys6mzMn4tPf3KipONQ8"
WEATHER_API_KEY = "7b74386e671b790fcc97a070ee8e987e"

# ---------------- GEMINI SETUP ----------------

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("models/gemini-2.5-flash")
import google.generativeai as genai

genai.configure(api_key="AIzaSyCSTod3nH_b86kGys6mzMn4tPf3KipONQ8")

for m in genai.list_models():
    print(m.name)
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

    response = requests.get(url)

    data = response.json()

    temperature = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    description = data["weather"][0]["description"]

    return temperature, humidity, description


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

question = st.text_input("Enter your farming question")

if st.button("🎤 Speak"):
    question = get_voice_input()
    st.write("You said:", question)

if st.button("📍 Detect My Location"):
    city, coords = get_location()
    st.write(f"Detected Location: {city}")
else:
    city = st.selectbox(
        "Or select your city manually",
        ["Bhopal", "Nashik", "Navi Mumbai"]
    )

if st.button("Get AI Advice"):

    weather = get_weather(city)

    soil = mock_agri_data[city]["soil"]
    market = mock_agri_data[city]["price_trend"]

    answer = generate_ai_response(question, city, weather, soil, market)

    st.subheader("🌱 AI Recommendations")

    st.write(answer)