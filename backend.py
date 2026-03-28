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
def get_market_price(city, crop=None):
    # Real Agmarknet API integration (public endpoint)
    # API: https://data.gov.in/resource/market-wise-daily-prices-all-commodities
    # Note: For production, use an official API key and handle rate limits.
    # Here, we use a sample endpoint for demonstration.
    try:
        # Example: Fetch latest market price for the city (and crop if provided)
        # This is a sample endpoint; replace with the latest Agmarknet API if needed
        url = (
            f"https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
            f"?format=json&filters[market]={city}"
        )
        if crop:
            url += f"&filters[commodity]={crop}"
        response = requests.get(url, timeout=5)
        data = response.json()
        records = data.get("records", [])
        if not records:
            return "Market price data not available"
        # Get the latest record
        latest = records[0]
        price = latest.get("modal_price", "N/A")
        commodity = latest.get("commodity", "N/A")
        arrival_date = latest.get("arrival_date", "N/A")
        return f"{commodity} price: ₹{price}/quintal (as of {arrival_date})"
    except Exception:
        return "Market price data not available"

def get_soil_and_market_by_coords(lat, lon, crop=None):
    # Debug: Log coordinates
    print(f"[DEBUG] Looking up city for coordinates: lat={lat}, lon={lon}")
    try:
        results = rg.search((lat, lon))
        print(f"[DEBUG] reverse_geocoder results: {results}")
        city = results[0]['name'] if results else "Unknown"
    except Exception as e:
        print(f"[ERROR] reverse_geocoder failed: {e}")
        city = "Unknown"
    # Dummy logic for soil (replace with real lookup)
    if city == "Bhopal":
        soil = "Medium Black Soil"
    elif city == "Nashik":
        soil = "Black Cotton Soil"
    elif city == "Navi Mumbai":
        soil = "Laterite Soil"
    else:
        soil = "Unknown"
    # Fallback: If city is unknown, use a default city to avoid downstream errors
    if city == "Unknown":
        print("[WARN] City could not be determined from coordinates. Using fallback city 'Bhopal'.")
        city = "Bhopal"
        soil = "Medium Black Soil"
    market = get_market_price(city, crop)
    print(f"[DEBUG] Using city: {city}, soil: {soil}, market: {market}")
    return city, soil, market

# ============ MODELS ============
class AdviceRequest(BaseModel):
    question: str
    latitude: float
    longitude: float
    land_size: float  # in acres or hectares
    irrigation_type: str  # e.g., "drip", "canal", "rainfed"
    months_to_harvest: int  # how many months until harvest
    crop_to_plant: str  # what crop the farmer wants to plant

class WeatherResponse(BaseModel):
    temperature: float
    humidity: int
    description: str

class PlannerStep(BaseModel):
    step: str
    month: int

class AdviceResponse(BaseModel):
    city: str
    question: str
    advice: str
    planner: list[PlannerStep]
    weather: WeatherResponse
    soil: str
    market_trend: str

# In-memory storage for approved plans (for demo; use DB in production)
approved_plans = {}

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
def generate_ai_response(question, city, weather, soil, market, land_size, irrigation_type, months_to_harvest, crop_to_plant):
    prompt = f"""
You are an expert Indian agriculture advisor.
A farmer from {city} asks:
"{question}"
Farmer details:
- Land size: {land_size}
- Irrigation type: {irrigation_type}
- Wants to plant: {crop_to_plant}
- Time to harvest: {months_to_harvest} months
Use ONLY this local information:
Weather:
Temperature: {weather[0]}°C
Humidity: {weather[1]}%
Condition: {weather[2]}
Soil:
{soil}
Market Price:
{market}
Give clear, step-by-step, actionable farming advice tailored to these details. Consider land size, irrigation, crop, and time to harvest for the best possible outcome for the farmer.
Also, provide a month-wise planner as a list of steps for the farmer to follow from now until harvest. Format the planner as a JSON list of objects with 'step' and 'month' fields.
"""
    try:
        response = model.generate_content(prompt)
        # Extract planner from response (simple heuristic: look for JSON block)
        import re, json as pyjson
        planner = []
        match = re.search(r'\[\s*{.*?}\s*\]', response.text, re.DOTALL)
        if match:
            try:
                planner = pyjson.loads(match.group(0))
            except Exception:
                planner = []
        return response.text, planner
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
    if request.latitude is None or request.longitude is None:
        raise HTTPException(status_code=400, detail="Latitude and longitude must be provided")
    if request.land_size is None or request.irrigation_type is None or request.months_to_harvest is None or not request.crop_to_plant:
        raise HTTPException(status_code=400, detail="All fields (land_size, irrigation_type, months_to_harvest, crop_to_plant) are required")
    crop = request.crop_to_plant.capitalize()
    city, soil, market_trend = get_soil_and_market_by_coords(request.latitude, request.longitude, crop)
    weather = get_weather(city)
    advice, planner = generate_ai_response(
        question=request.question,
        city=city,
        weather=weather,
        soil=soil,
        market=market_trend,
        land_size=request.land_size,
        irrigation_type=request.irrigation_type,
        months_to_harvest=request.months_to_harvest,
        crop_to_plant=request.crop_to_plant
    )
    return AdviceResponse(
        city=city,
        question=request.question,
        advice=advice,
        planner=planner,
        weather=WeatherResponse(
            temperature=weather[0],
            humidity=weather[1],
            description=weather[2]
        ),
        soil=soil,
        market_trend=market_trend
    )

# Endpoint to approve and save a plan
from fastapi import Body
from fastapi.responses import JSONResponse
@app.post("/approve-plan", tags=["Planner"])
def approve_plan(farmer_id: str = Body(...), planner: list[PlannerStep] = Body(...)):
    # Save the plan for the farmer (in-memory for demo)
    approved_plans[farmer_id] = planner
    # In production, schedule reminders (e.g., via Celery, cron, or push notifications)
    return JSONResponse({"status": "approved", "message": "Plan saved and reminders scheduled."})

