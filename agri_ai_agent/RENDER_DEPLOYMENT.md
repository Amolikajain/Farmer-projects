# Deploy to Render - Step by Step

## Prerequisites
- GitHub account
- Render account (free at https://render.com)
- Your code pushed to GitHub

---

## Step 1: Push to GitHub

If not already done:
```bash
git init
git add .
git commit -m "Initial commit - Farming Assistant API"
git remote add origin https://github.com/YOUR_USERNAME/farming-assistant.git
git branch -M main
git push -u origin main
```

---

## Step 2: Create Render Account & Connect GitHub

1. Go to **https://render.com**
2. Sign up with GitHub (recommended)
3. Click **"Authorize render-oss"**
4. Grant repository access

---

## Step 3: Create Web Service on Render

1. Go to **https://dashboard.render.com**
2. Click **"New +"** → **"Web Service"**
3. Select your GitHub repository (`farming-assistant`)
4. Fill in details:

| Field | Value |
|-------|-------|
| **Name** | farming-assistant-api |
| **Environment** | Python 3 |
| **Region** | Choose closest to you |
| **Branch** | main |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn backend:app --host 0.0.0.0 --port $PORT` |
| **Free Plan** | Available (free tier works great for testing) |

---

## Step 4: Set Environment Variables

1. In Render dashboard, go to **Settings** → **Environment**
2. Add the following variables:

```
GEMINI_API_KEY = AIzaSyC2XBragMKwKfK8yMBFYadEsKwR_EMHY78
WEATHER_API_KEY = b898b54a25487a86734efde5a7c63da0
```

3. Click **"Save Changes"**

---

## Step 5: Deploy

1. Click **"Create Web Service"**
2. Wait for build to complete (3-5 minutes)
3. You'll see a live URL: `https://farming-assistant-api-xxxx.onrender.com`

---

## Step 6: Test Your Deployment

Once deployed, test these URLs:

**Health Check:**
```
https://your-render-url.com/health
```

**Get Cities:**
```
https://your-render-url.com/cities
```

**API Documentation:**
```
https://your-render-url.com/docs
```

**Test Get Advice (in browser or Postman):**
```
POST https://your-render-url.com/get-advice
Content-Type: application/json

{
  "question": "When should I plant soybeans?",
  "city": "Bhopal"
}
```

---

## Your Live Backend URL

```
https://YOUR-APP-NAME-xxxx.onrender.com
```

**Share this with your frontend team!**

---

## Common Issues & Fixes

### "Build failed"
- Check `requirements.txt` has correct versions
- Ensure Python files have no syntax errors
- View logs: Click service > "Logs" tab

### "502 Bad Gateway"
- API might be starting, wait 30-60 seconds
- Check logs for errors
- Verify environment variables are set

### "No module named 'backend'"
- Ensure `backend.py` is in root directory
- Check file name is correct (case-sensitive on Linux)

### API returning errors
- Verify API keys in environment variables
- Check weather API key is valid
- Test city names: "Bhopal", "Nashik", "Navi Mumbai"

---

## Monitor & Manage

**View Logs:**
- Dashboard → Your service → "Logs" tab
- See real-time requests and errors

**Redeploy:**
- Push to GitHub `main` branch
- Render auto-redeploys on commit

**Upgrade Plan:**
- Free plan works great initially
- Upgrade if you need more resources

---

## Next Steps

1. ✅ Get your Render URL
2. 📧 Send to frontend team: **API_URL** + **API Documentation**
3. 🧪 Frontend team tests integration
4. 🚀 Launch!

---

## Quick Reference

| Item | Value |
|------|-------|
| **Render Dashboard** | https://dashboard.render.com |
| **API Docs** | https://your-url.com/docs |
| **Health Check** | https://your-url.com/health |
| **Main Endpoint** | POST https://your-url.com/get-advice |

**Deployed! 🎉**
