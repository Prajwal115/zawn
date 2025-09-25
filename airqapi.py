from fastapi import APIRouter
import requests
import json
import os

airqapi = APIRouter()
API_KEY = "API_KEY1"
COORDS_FILE = "coords.json"
LATEST_FILE = "airq_latest.json"

def fetch_air_quality(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch from OpenWeatherMap:", response.status_code)
        return None

    try:
        data = response.json()["list"][0]
        return {
            "lat": lat,
            "lon": lon,
            "aqi": data["main"]["aqi"],
            "pm2_5": data["components"]["pm2_5"],
            "pm10": data["components"]["pm10"],
            "no2": data["components"]["no2"],
            "so2": data["components"]["so2"],
            "co": data["components"]["co"],
            "o3": data["components"]["o3"],
            "timestamp": data["dt"]
        }
    except Exception as e:
        print("Error parsing pollution data:", e)
        return None

@airqapi.get("/airq")
def get_air_quality():
    if not os.path.exists(COORDS_FILE):
        print("Coordinates file missing")
        return {"error": "Coordinates file not found"}

    try:
        with open(COORDS_FILE, "r") as f:
            coords = json.load(f)
        lat = coords.get("lat")
        lon = coords.get("lon")
    except Exception as e:
        print("Error reading coordinates:", e)
        return {"error": "Invalid coordinates file"}

    if lat is None or lon is None:
        print("Coordinates missing in file")
        return {"error": "Invalid coordinates"}

    result = fetch_air_quality(lat, lon)
    if result is None:
        return {"error": "Failed to fetch pollution data"}

    try:
        with open(LATEST_FILE, "w") as f:
            json.dump(result, f)
        print("Wrote latest AQI snapshot to file")
    except Exception as e:
        print("Error writing to snapshot file:", e)

    return result
