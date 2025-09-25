from fastapi import APIRouter
import requests
import json
import os

aqiapi2 = APIRouter()

API_TOKEN = "06a96547b9eea6a06b42b56f1b833e3e8a279f3a"
COORDS_FILE = "coords.json"
LOG_FILE = "aqi2.jsonl"

def fetch_aqi_and_station(lat, lon):
    url = f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={API_TOKEN}"
    response = requests.get(url)

    if response.status_code != 200:
        print("AQICN fetch failed:", response.status_code)
        return None

    data = response.json().get("data", {})
    return {
        "lat": lat,
        "lon": lon,
        "aqi": data.get("aqi", None),
        "station_name": data.get("city", {}).get("name", "Unknown Station")
    }

@aqiapi2.get("/aqi")
def get_aqi_and_station():
    if not os.path.exists(COORDS_FILE):
        return {"error": "Coordinates file not found"}

    with open(COORDS_FILE, "r") as f:
        coords = json.load(f)

    lat = coords.get("lat")
    lon = coords.get("lon")

    if lat is None or lon is None:
        return {"error": "Invalid coordinates"}

    result = fetch_aqi_and_station(lat, lon)
    if result is None:
        return {"error": "Failed to fetch AQI data"}

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(result) + "\n")

    return result