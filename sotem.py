import requests
from fastapi import APIRouter
import json
import os

sotemapi = APIRouter()

COORDS_FILE = "coords.json"
LOG_FILE = "sotem_output.jsonl"

def fetch_solar_and_temperature(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&hourly=temperature_2m,shortwave_radiation,direct_radiation,diffuse_radiation"
        f"&current_weather=true"
        f"&timezone=auto"
    )

    response = requests.get(url)
    if response.status_code != 200:
        print("Open-Meteo fetch failed:", response.status_code)
        return None

    try:
        data = response.json()
        current = data.get("current_weather", {})
        hourly = data.get("hourly", {})

        current_time = current.get("time")
        hourly_times = hourly.get("time", [])
        try:
            index = hourly_times.index(current_time)
        except ValueError:
            index = 0  # fallback

        result = {
            "lat": lat,
            "lon": lon,
            "temperature": current.get("temperature"),
            "shortwave_radiation": hourly.get("shortwave_radiation", [None])[index],
            "direct_radiation": hourly.get("direct_radiation", [None])[index],
            "diffuse_radiation": hourly.get("diffuse_radiation", [None])[index],
            "timestamp": current_time
        }

        print("Fetched solar/temperature result:", result)
        return result
    except Exception as e:
        print("Error parsing Open-Meteo response:", e)
        return None
    

@sotemapi.get("/sotem")
def get_sotem():
    if not os.path.exists(COORDS_FILE):
        print("Coordinates file missing")
        return {"error": "Coordinates file not found"}

    try:
        with open(COORDS_FILE, "r") as f:
            coords = json.load(f)

        lat = coords.get("lat")
        lon = coords.get("lon")

        if lat is None or lon is None:
            print("Invalid coordinates in file")
            return {"error": "Invalid coordinates"}

        result = fetch_solar_and_temperature(lat, lon)
        if not result:
            print("No result returned from fetch_solar_and_temperature")
            return {"error": "Failed to fetch solar/temperature data"}

        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(result) + "\n")
        print("Wrote to sotem_output.jsonl")

        return result
    except Exception as e:
        print("Error in /sotem route:", e)
        return {"error": f"Failed to process solar/temperature: {str(e)}"}
    
