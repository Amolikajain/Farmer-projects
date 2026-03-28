# Deployment Guide - Smart AI Farming Assistant Backend

## Quick Start (Local Development)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the backend
python backend.py

# API will be available at: http://localhost:8000
# Interactive docs: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

---

## Deployment Options

### Option 1: Railway (Recommended - Easiest)
1. Push your code to GitHub
2. Go to [railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway auto-detects Python and deploys
6. Get your URL from the Railway dashboard

### Option 2: Render
1. Push to GitHub
2. Go to [render.com](https://render.com)
3. Click "New +" → "Web Service"
4. Connect GitHub repo
5. Set build command: `pip install -r requirements.txt`
6. Set start command: `uvicorn backend:app --host 0.0.0.0 --port $PORT`

### Option 3: Heroku
```bash
heroku login
heroku create your-app-name
git push heroku main
heroku open
```

### Option 4: AWS/Azure/GCP
Deploy as containerized service with:
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "backend.py"]
```

---

## Environment Variables

Create a `.env` file or set these in your deployment platform:

```env
GEMINI_API_KEY=AIzaSyC2XBragMKwKfK8yMBFYadEsKwR_EMHY78
WEATHER_API_KEY=b898b54a25487a86734efde5a7c63da0
```

---

## API Endpoints Documentation

**Base URL:** `http://your-deployed-url.com` or `http://localhost:8000` (local)

### 1. Health Check
```
GET /health
```
**Response:**
```json
{"status": "healthy"}
```

### 2. Get Available Cities
```
GET /cities
```
**Response:**
```json
{
  "cities": [
    {
      "city": "Bhopal",
      "soil": "Medium Black Soil",
      "market_trend": "Soybean demand is increasing"
    },
    {
      "city": "Nashik",
      "soil": "Black Cotton Soil",
      "market_trend": "Onion prices are decreasing"
    },
    {
      "city": "Navi Mumbai",
      "soil": "Laterite Soil",
      "market_trend": "Rice prices are high"
    }
  ]
}
```

### 3. Get Weather for a City
```
GET /weather/{city}
```
**Parameters:**
- `city` (path): City name (e.g., "Bhopal")

**Response:**
```json
{
  "city": "Bhopal",
  "temperature": 28.5,
  "humidity": 65,
  "description": "scattered clouds",
  "unit": "Celsius"
}
```

### 4. Get City Agricultural Info
```
GET /city-info/{city}
```
**Parameters:**
- `city` (path): City name

**Response:**
```json
{
  "city": "Bhopal",
  "soil": "Medium Black Soil",
  "market_trend": "Soybean demand is increasing"
}
```

### 5. Get Farming Advice (Main Endpoint)
```
POST /get-advice
```
**Request Body:**
```json
{
  "question": "When should I plant soybeans this season?",
  "city": "Bhopal"
}
```

**Response:**
```json
{
  "city": "Bhopal",
  "question": "When should I plant soybeans this season?",
  "advice": "Based on the current weather (28.5°C, 65% humidity, scattered clouds) and medium black soil conditions in Bhopal...[AI-generated advice]",
  "weather": {
    "temperature": 28.5,
    "humidity": 65,
    "description": "scattered clouds"
  },
  "soil": "Medium Black Soil",
  "market_trend": "Soybean demand is increasing"
}
```

### 6. List Available Cities
```
GET /available-cities
```
**Response:**
```json
{
  "available_cities": ["Bhopal", "Nashik", "Navi Mumbai"],
  "count": 3
}
```

---

## Frontend Integration Examples

### JavaScript/React Example
```javascript
async function getFarmingAdvice(question, city) {
  const response = await fetch('https://your-backend-url.com/get-advice', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      question: question,
      city: city
    })
  });
  
  const data = await response.json();
  return data.advice;
}

// Usage
const advice = await getFarmingAdvice(
  'When should I plant soybeans?',
  'Bhopal'
);
console.log(advice);
```

### React Component Example
```jsx
import { useState } from 'react';

export function FarmingAdvisor() {
  const [question, setQuestion] = useState('');
  const [city, setCity] = useState('Bhopal');
  const [advice, setAdvice] = useState('');
  const [loading, setLoading] = useState(false);

  const handleGetAdvice = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/get-advice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, city })
      });
      const data = await response.json();
      setAdvice(data.advice);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input value={question} onChange={(e) => setQuestion(e.target.value)} />
      <select value={city} onChange={(e) => setCity(e.target.value)}>
        <option>Bhopal</option>
        <option>Nashik</option>
        <option>Navi Mumbai</option>
      </select>
      <button onClick={handleGetAdvice} disabled={loading}>
        {loading ? 'Generating...' : 'Get Advice'}
      </button>
      {advice && <p>{advice}</p>}
    </div>
  );
}
```

### Python Example
```python
import requests

API_URL = "https://your-backend-url.com"

def get_farming_advice(question, city):
    response = requests.post(
        f"{API_URL}/get-advice",
        json={"question": question, "city": city}
    )
    return response.json()

# Usage
result = get_farming_advice("How do I prevent crop diseases?", "Bhopal")
print(result['advice'])
```

---

## Error Responses

### 400 - Bad Request
```json
{
  "detail": "City 'InvalidCity' not found. Available: Bhopal, Nashik, Navi Mumbai"
}
```

### 404 - Not Found
```json
{
  "detail": "City 'RandomCity' not found"
}
```

### 500 - Server Error
```json
{
  "detail": "AI generation error: [error details]"
}
```

---

## Interactive API Testing

After deployment, visit: `https://your-backend-url.com/docs`

This provides a Swagger UI where you can test all endpoints directly with a web interface.

---

## Support & Debugging

- Check logs: `railway logs app` or dashboard logs
- Test health: `curl https://your-url.com/health`
- Verify CORS: Check browser console for CORS errors
- API docs: `https://your-url.com/docs`

**Share this with your frontend team:**
- Backend URL: `https://your-backend-url.com`
- API Docs: `https://your-backend-url.com/docs`
- Main Endpoint: `POST /get-advice`
