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

import geocoder

def get_location():
    g = geocoder.ip('me')

    city = g.city
    latlng = g.latlng

    return city, latlng