# 🌾 Farming Assistant Backend - Frontend Integration Guide

**Share this with your frontend team!**

---

## Backend API URL

```
https://[your-deployed-url].com
```

*After deployment, replace with your actual URL*

---

## Main Endpoint (Primary Use)

### Get Farming Advice
```
POST https://[your-backend-url]/get-advice
```

**Request:**
```json
{
  "question": "When should I plant soybeans?",
  "city": "Bhopal"
}
```

**Response:**
```json
{
  "city": "Bhopal",
  "question": "When should I plant soybeans?",
  "advice": "Based on current weather... [AI-generated recommendations]",
  "weather": {
    "temperature": 28.5,
    "humidity": 65,
    "description": "scattered clouds"
  },
  "soil": "Medium Black Soil",
  "market_trend": "Soybean demand is increasing"
}
```

---

## Available Cities

```
GET https://[your-backend-url]/cities
```

Returns:
```json
{
  "cities": [
    {"city": "Bhopal", "soil": "Medium Black Soil", "market_trend": "..."},
    {"city": "Nashik", "soil": "Black Cotton Soil", "market_trend": "..."},
    {"city": "Navi Mumbai", "soil": "Laterite Soil", "market_trend": "..."}
  ]
}
```

---

## Quick Integration Checklist

- [ ] Update backend URL in your frontend config
- [ ] Set CORS headers if needed (backend supports all origins)
- [ ] Handle error responses (400, 404, 500)
- [ ] Show loading state during API calls
- [ ] Display weather, soil, and market info alongside advice

---

## All Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/cities` | Get all cities with soil & market info |
| GET | `/weather/{city}` | Get current weather for a city |
| GET | `/city-info/{city}` | Get agricultural info for a city |
| POST | `/get-advice` | **Main endpoint - Get farming recommendations** |
| GET | `/available-cities` | List available cities |

---

## Interactive API Documentation

After deployment, visit:
```
https://[your-backend-url]/docs
```

This provides a Swagger UI where you can test all endpoints.

---

## Error Handling

**404 - City Not Found:**
```json
{"detail": "City 'InvalidCity' not found. Available: Bhopal, Nashik, Navi Mumbai"}
```

**400 - Bad Request:**
```json
{"detail": "Question cannot be empty"}
```

**500 - Server Error:**
```json
{"detail": "AI generation error: ..."}
```

---

## Sample Code (React)

```jsx
const API_URL = "https://your-backend-url.com";

async function getFarmingAdvice(question, city) {
  const response = await fetch(`${API_URL}/get-advice`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, city })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }
  
  return await response.json();
}
```

---

## Contact & Support

- Full documentation: See `DEPLOYMENT.md`
- Backend repo: [GitHub link]
- Questions? Contact backend team

**Ready to integrate! 🚀**
