from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import google.generativeai as genai
import os
from typing import Optional

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

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-2.5-flash")

# ============ DATA ============
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

# ============ MODELS ============
class AdviceRequest(BaseModel):
    question: str
    city: str

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

class CityInfo(BaseModel):
    city: str
    soil: str
    market_trend: str

# ============ FUNCTIONS ============
def get_weather(city: str) -> tuple:
    """Fetch weather data from OpenWeatherMap API"""
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

def generate_ai_response(question: str, city: str, weather: tuple, soil: str, market: str) -> str:
    """Generate AI advice using Gemini API"""
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
    """API root endpoint"""
    return {
        "message": "Smart AI Farming Assistant API",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/cities", tags=["Data"])
def get_cities():
    """List all available cities with their info"""
    cities = []
    for city, info in mock_agri_data.items():
        cities.append({
            "city": city,
            "soil": info["soil"],
            "market_trend": info["price_trend"]
        })
    return {"cities": cities}

@app.get("/weather/{city}", tags=["Weather"])
def get_city_weather(city: str):
    """Get weather for a specific city
    
    Args:
        city: City name (e.g., 'Bhopal')
    
    Returns:
        Current weather data (temperature, humidity, description)
    """
    temp, humidity, description = get_weather(city)
    return {
        "city": city,
        "temperature": temp,
        "humidity": humidity,
        "description": description,
        "unit": "Celsius"
    }

@app.get("/city-info/{city}", tags=["Data"])
def get_city_info(city: str):
    """Get agricultural info for a city
    
    Args:
        city: City name (e.g., 'Bhopal')
    
    Returns:
        Soil type and market trends
    """
    if city not in mock_agri_data:
        raise HTTPException(status_code=404, detail=f"City '{city}' not found")
    
    info = mock_agri_data[city]
    return {
        "city": city,
        "soil": info["soil"],
        "market_trend": info["price_trend"]
    }

@app.post("/get-advice", tags=["Recommendations"], response_model=AdviceResponse)
def get_farming_advice(request: AdviceRequest):
    """Get AI farming recommendations
    
    This is the main endpoint. Provide a farming question and city,
    and receive personalized recommendations based on:
    - Current weather
    - Local soil type
    - Market trends
    - AI-powered analysis
    
    Args:
        question: Farming question (e.g., 'When should I plant soybeans?')
        city: City name (e.g., 'Bhopal')
    
    Returns:
        Detailed farming advice with supporting data
    """
    # Validate city
    if request.city not in mock_agri_data:
        raise HTTPException(status_code=404, detail=f"City '{request.city}' not found. Available: {', '.join(mock_agri_data.keys())}")
    
    # Validate question
    if not request.question or len(request.question.strip()) == 0:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    # Get data
    weather = get_weather(request.city)
    soil = mock_agri_data[request.city]["soil"]
    market_trend = mock_agri_data[request.city]["price_trend"]
    
    # Generate advice
    advice = generate_ai_response(request.question, request.city, weather, soil, market_trend)
    
    return AdviceResponse(
        city=request.city,
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

@app.get("/available-cities", tags=["Data"])
def list_available_cities():
    """List available cities for farming advice"""
    return {
        "available_cities": list(mock_agri_data.keys()),
        "count": len(mock_agri_data)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
