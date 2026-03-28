# Smart AI Farming Assistant API — Production Documentation
## POST /get-advice
Request Body:
```
{
  "question": "What is the best way to grow rice this season?",
  "latitude": 19.0760,
  "longitude": 72.8777,
  "land_size": 2.5,
  "irrigation_type": "drip",
  "months_to_harvest": 4,
  "crop_to_plant": "rice"
}
```

Response Body:
```
{
  "city": "Navi Mumbai",
  "question": "What is the best way to grow rice this season?",
  "advice": "Based on your land size, irrigation type, and local conditions, here are the best steps to grow rice...",
  "planner": [
  { "step": "Prepare the field and test soil pH.", "month": 1 },
  { "step": "Sow rice seeds and ensure proper irrigation.", "month": 2 },
  { "step": "Apply fertilizer and monitor for pests.", "month": 3 },
  { "step": "Prepare for harvest and market linkage.", "month": 4 }
  ],
  "weather": {
  "temperature": 30.5,
  "humidity": 80,
  "description": "light rain"
  },
  "soil": "Laterite Soil",
  "market_trend": "Rice price: ₹2500/quintal (as of 2026-03-28)"
}
```

---
## POST /approve-plan

Request Body:
```
{
  "farmer_id": "farmer123",
  "planner": [
  { "step": "Prepare the field and test soil pH.", "month": 1 },
  { "step": "Sow rice seeds and ensure proper irrigation.", "month": 2 },
  { "step": "Apply fertilizer and monitor for pests.", "month": 3 },
  { "step": "Prepare for harvest and market linkage.", "month": 4 }
  ]
}
```

Response Body:
```
{
  "status": "approved",
  "message": "Plan saved and reminders scheduled."
}
```

---
## Other Endpoints

- `GET /` — Health/info endpoint
- `GET /health` — Health check

---
**All fields in /get-advice are required. The planner is a month-wise actionable plan for the farmer. After approval, reminders can be scheduled (extend as needed for production).**
# Smart AI Farming Assistant API Documentation

## POST /get-advice

Request Body (JSON):
```
{
  "question": "What is the best way to grow rice this season?",
  "latitude": 19.0760,
  "longitude": 72.8777,
  "land_size": 2.5,
  "irrigation_type": "drip",
  "months_to_harvest": 4,
  "crop_to_plant": "rice"
}
```

Response Body (JSON):
```
{
  "city": "Navi Mumbai",
  "question": "What is the best way to grow rice this season?",
  "advice": "Based on your land size, irrigation type, and local conditions, here are the best steps to grow rice...",
  "planner": [
    { "step": "Prepare the field and test soil pH.", "month": 1 },
    { "step": "Sow rice seeds and ensure proper irrigation.", "month": 2 },
    { "step": "Apply fertilizer and monitor for pests.", "month": 3 },
    { "step": "Prepare for harvest and market linkage.", "month": 4 }
  ],
  "weather": {
    "temperature": 30.5,
    "humidity": 80,
    "description": "light rain"
  },
  "soil": "Laterite Soil",
  "market_trend": "Rice price: ₹2500/quintal (as of 2026-03-28)"
}
```

---


## POST /approve-plan

Request Body (JSON):
```
{
  "farmer_id": "farmer123",
  "planner": [
    { "step": "Prepare the field and test soil pH.", "month": 1 },
    { "step": "Sow rice seeds and ensure proper irrigation.", "month": 2 },
    { "step": "Apply fertilizer and monitor for pests.", "month": 3 },
    { "step": "Prepare for harvest and market linkage.", "month": 4 }
  ]
}
```

Response Body (JSON):
```
{
  "status": "approved",
  "message": "Plan saved and reminders scheduled."
}
```

---

## Other Endpoints

- `GET /` — Health/info endpoint
- `GET /health` — Health check

---

### Notes
- All fields in /get-advice are required.
- The planner is a month-wise actionable plan for the farmer.
- After approval, reminders can be scheduled (extend as needed for production).
# 🌾 Farming Assistant Backend - Frontend Integration Guide

**Share this with your frontend team!**

---

## Backend API URL

```
https://[your-deployed-url].onrender.com
```

*Replace with your actual Render URL after deployment*

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
