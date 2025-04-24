import os
import requests

API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

def run(params: dict, context: dict) -> str:
    location = params.get("location", "New York")
    units = params.get("unit", "imperial")  # or "metric"
    print(f"🌦️ [Weather] Fetching real forecast for {location}...")

    url = "https://api.openweathermap.org/data/2.5/weather"
    response = requests.get(url, params={
        "q": location,
        "units": units,
        "appid": API_KEY
    })

    if response.status_code != 200:
        return f"Failed to fetch weather for {location}: {response.text}"

    data = response.json()
    desc = data["weather"][0]["description"].capitalize()
    temp = data["main"]["temp"]
    return f"Current weather in {location}: {desc}, {temp}°{ 'F' if units == 'imperial' else 'C' }"