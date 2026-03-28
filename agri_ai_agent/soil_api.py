import requests

def get_soil_ph(lat, lon):

    url = f"https://api.openlandmap.org/query?lon={lon}&lat={lat}&attribute=phh2o"

    response = requests.get(url)
    data = response.json()

    print(data)  # helps debug response

    try:
        soil_ph = data["value"]
    except:
        soil_ph = "Not available"

    return soil_ph
