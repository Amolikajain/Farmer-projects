from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import google.generativeai as genai
import os
from typing import Optional
import reverse_geocoder as rg

# ============ CONFIG ============
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyC2XBragMKwKfK8yMBFYadEsKwR_EMHY78")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "b898b54a25487a86734efde5a7c63da0")

# ============ SETUP ============
app = FastAPI(
    title="Smart AI Farming Assistant API",
    description="Backend API for agricultural recommendations",
    version="1.0.0"
)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-2.5-flash")

# ============ REAL DATA LOOKUP ============
def get_soil_and_market_by_coords(lat, lon):
    # TODO: Replace with real data source or API
    results = rg.search((lat, lon))
    city = results[0]['name'] if results else "Unknown"
    # Dummy logic for soil/market (replace with real lookup)
    if city == "Bhopal":
        soil = "Medium Black Soil"
        market = "Soybean demand is increasing"
    elif city == "Nashik":
        soil = "Black Cotton Soil"
        market = "Onion prices are decreasing"
    elif city == "Navi Mumbai":
        soil = "Laterite Soil"
        market = "Rice prices are high"
    else:
        soil = "Unknown"
        market = "Unknown"
    return city, soil, market

# ============ MODELS ============
class AdviceRequest(BaseModel):
    question: str
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class WeatherResponse(BaseModel):
    temperature: float
    humidity: int
    description: str

class AdviceResponse(BaseModel):
    city: str
    question: str
    advice: str
    weather: WeatherResponse
    soil: str
    market_trend: str

# ============ WEATHER FUNCTION ============
def get_weather(city: str) -> tuple:
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if "main" not in data or "weather" not in data:
            raise HTTPException(status_code=400, detail=f"Invalid API response for city: {city}")
        return (
            data["main"]["temp"],
            data["main"]["humidity"],
            data["weather"][0]["description"]
        )
    except requests.exceptions.HTTPError as e:
        raise HTTPException(status_code=400, detail=f"Weather API error: {e}")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")

# ============ AI RESPONSE ============
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
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation error: {str(e)}")

# ============ ENDPOINTS ============
@app.get("/", tags=["Health"])
def root():
    return {
        "message": "Smart AI Farming Assistant API",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}

@app.post("/get-advice", tags=["Recommendations"], response_model=AdviceResponse)
def get_farming_advice(request: AdviceRequest):
    if not request.question or len(request.question.strip()) == 0:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    if request.latitude is not None and request.longitude is not None:
        city, soil, market_trend = get_soil_and_market_by_coords(request.latitude, request.longitude)
    elif request.city:
        city = request.city
        soil = "Unknown"
        market_trend = "Unknown"
    else:
        raise HTTPException(status_code=400, detail="Either city or coordinates must be provided")
    weather = get_weather(city)
    advice = generate_ai_response(request.question, city, weather, soil, market_trend)
    return AdviceResponse(
        city=city,
        question=request.question,
        advice=advice,
        weather=WeatherResponse(
            temperature=weather[0],
            humidity=weather[1],
            description=weather[2]
        ),
        soil=soil,
        market_trend=market_trend
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
