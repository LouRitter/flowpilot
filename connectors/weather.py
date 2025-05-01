# connectors/weather.py

import requests
from core.secrets import SecretsManager

def run(params: dict, context: dict = None) -> str:
    secrets = SecretsManager()
    api_key = secrets.get("OPENWEATHERMAP_API_KEY")

    location = params.get("location")
    if not location:
        raise ValueError("Missing 'location' for weather step.")

    units = params.get("units", "imperial")  # Optional
    lang = params.get("lang", "en")          # Optional

    print(f"🌦️ [Weather] Fetching forecast for {location}...")

    url = "https://api.openweathermap.org/data/2.5/weather"
    response = requests.get(url, params={
        "q": location,
        "units": units,
        "lang": lang,
        "appid": api_key
    })

    if response.status_code != 200:
        print(f"❌ Failed to fetch weather for {location}: {response.text}")
        return f"Failed to fetch weather for {location}"

    data = response.json()
    desc = data["weather"][0]["description"].capitalize()
    temp = data["main"]["temp"]
    return f"Current weather in {location}: {desc}, {temp}°{ 'F' if units == 'imperial' else 'C' }"
