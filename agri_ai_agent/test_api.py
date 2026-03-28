import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_root():
    response = requests.get(f"{BASE_URL}/")
    print(f"Root: {response.json()}")

def test_weather(city):
    response = requests.get(f"{BASE_URL}/weather/{city}")
    print(f"Weather for {city}: {response.json()}")

def test_advice(question, city, history):
    payload = {
        "question": question,
        "city": city,
        "previous_crops": history
    }
    response = requests.post(f"{BASE_URL}/advice", json=payload)
    print(f"Advice for {question}:")
    data = response.json()
    if "advice" in data:
        print(data.get("advice")[:500] + "...")
    else:
        print(f"FAILED: {data}")

if __name__ == "__main__":
    try:
        test_root()
        test_weather("Bhopal")
        test_advice(
            "What should I grow next? I have a water crisis.",
            "Bhopal",
            ["Sugarcane", "Paddy"]
        )
    except Exception as e:
        print(f"Error testing API: {e}. Is the server running?")
