import speech_recognition as sr

def get_voice_input():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("🎤 बोलिए... Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language="en-IN")
        print("You said:", text)
        return text

    except:
        return "Sorry, could not understand audio"

import requests

def get_location():
    url = "https://ipinfo.io/json"
    response = requests.get(url)
    data = response.json()

    city = data.get("city")
    loc = data.get("loc")  # gives lat,long

    return city, loc