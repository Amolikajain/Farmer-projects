import os
from typing import Optional, List
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
# Use gemini-2.0-flash as verified in list_models()
model = genai.GenerativeModel("gemini-2.0-flash")

app = FastAPI(title="Smart Agri AI Agent API")

# ---------------- MODELS ----------------

class AdviceRequest(BaseModel):
    question: str
    city: str
    previous_crops: Optional[List[str]] = []

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

# ---------------- HELPERS ----------------

def get_weather(city: str):
    if not WEATHER_API_KEY:
        return None
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return {
            "temp": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"]
        }
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return None

# ---------------- ENDPOINTS ----------------

@app.get("/")
def read_root():
    return {"message": "Welcome to the Smart Agri AI Agent API"}

@app.get("/location")
def get_location_info():
    try:
        url = "https://ipinfo.io/json"
        response = requests.get(url)
        data = response.json()
        return {
            "city": data.get("city"),
            "region": data.get("region"),
            "country": data.get("country"),
            "loc": data.get("loc")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/weather/{city}")
def get_city_weather(city: str):
    weather = get_weather(city)
    if not weather:
        raise HTTPException(status_code=404, detail="City not found or API error")
    return weather

@app.post("/advice")
def get_farming_advice(request: AdviceRequest):
    weather = get_weather(request.city)
    soil = mock_agri_data.get(request.city, {}).get("soil", "Unknown Soil")
    market = mock_agri_data.get(request.city, {}).get("price_trend", "Stable price trends")

    if weather:
        weather_str = f"{weather['temp']}°C, {weather['humidity']}% humidity, {weather['description']}"
    else:
        weather_str = "Weather data unavailable"
    
    # Constructing a prompt that includes crop history for water crisis analysis
    history_str = ", ".join(request.previous_crops) if request.previous_crops else "None mentioned"
    
    prompt = f"""
    You are an expert Indian agriculture advisor (Krishi Sakha).
    
    A farmer from {request.city} asks: "{request.question}"
    
    LOCAL CONTEXT:
    - Weather: {weather_str}
    - Soil Type: {soil}
    - Market Trend: {market}
    - Previous Crops Grown: {history_str}
    
    TASKS:
    1. Answer the farmer's question in simple, actionable steps.
    2. WATER CRISIS ANALYSIS: Analyze if the previous crops (like Sugarcane or Paddy) have depleted soil moisture. 
       If there's a water crisis/shortage indicated by weather or history, suggest low-water alternatives (e.g., Millets, Pulses).
    3. Use a helpful, encouraging tone.
    4. Provide the response in both English and Hindi.
    """

    try:
        response = model.generate_content(prompt)
        return {"advice": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detect-disease")
async def detect_crop_disease(
    file: UploadFile = File(...),
    city: Optional[str] = Form("Unknown")
):
    try:
        contents = await file.read()
        # Use Gemini Vision (multimodal) capability
        image_parts = [{"mime_type": file.content_type, "data": contents}]
        
        prompt = f"""
        Analyze this image of a crop from {city}. 
        Identify if there is any disease or pest infestation.
        If yes:
        1. Name the disease/pest.
        2. Suggest organic and chemical solutions.
        3. Explain how to prevent it in the future.
        If no disease is found, provide tips for healthy growth of this specific crop.
        Provide the response in both English and Hindi.
        """
        
        response = model.generate_content([prompt, image_parts[0]])
        return {"analysis": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
