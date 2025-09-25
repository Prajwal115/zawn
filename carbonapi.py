from fastapi import FastAPI, APIRouter, Query
from fastapi.responses import JSONResponse
import json
import threading
import pathway as pw
from pathway.io.python import ConnectorSubject

app = FastAPI()
carbonapi = APIRouter()

@carbonapi.get("/carbon")
async def get_combined_data(lat: float = Query(...), lon: float = Query(...)):
    with open("coords.json", "w") as f:
        json.dump({"lat": lat, "lon": lon}, f)

    try:
        with open("carbon_output.jsonl", "r") as f1, open("power_output.jsonl", "r") as f2:
            carbon_data = json.loads(f1.readlines()[-1])
            power_data = json.loads(f2.readlines()[-1])
            combined = {**carbon_data, **power_data}
    except Exception:
        combined = {
            "status_label": "Unavailable",
            "carbon_intensity": 0,
            "recommendation": "No advice",
            "timestamp": "N/A",
            "coal": 0,
            "solar": 0,
            "wind": 0,
            "fossil_gas": 0,
            "hydro": 0,
            "nuclear": 0,
            "biomass": 0
        }

    return JSONResponse(content=combined)

# ✅ Serve power breakdown
@carbonapi.get("/power-breakdown")
async def get_power_breakdown(lat: float = Query(...), lon: float = Query(...)):
    with open("coords.json", "w") as f:
        json.dump({"lat": lat, "lon": lon}, f)

    try:
        with open("power_output.jsonl", "r") as f:
            last_line = f.readlines()[-1]
            data = json.loads(last_line)
    except Exception:
        data = {
            "timestamp": "N/A",
            "coal": 0,
            "solar": 0,
            "wind": 0,
            "fossil_gas": 0,
            "hydro": 0,
            "nuclear": 0,
            "biomass": 0
        }

    return JSONResponse(content=data)

# ✅ Carbon schema
class CarbonSignalSchema(pw.Schema):
    carbon_intensity: float
    status_label: str
    recommendation: str
    timestamp: str

# ✅ Power breakdown schema
class PowerBreakdownSchema(pw.Schema):
    timestamp: str
    coal: float
    solar: float
    wind: float
    fossil_gas: float
    hydro: float
    nuclear: float
    biomass: float

# ✅ Carbon connector
class CarbonConnector(ConnectorSubject):
    def run(self):
        import time, requests
        from datetime import datetime

        while True:
            try:
                with open("coords.json", "r") as f:
                    coords = json.load(f)
                lat = coords.get("lat", 28.6145)
                lon = coords.get("lon", 77.2078)
            except Exception:
                lat, lon = 28.6145, 77.2078

            url = f"https://api.electricitymaps.com/v3/carbon-intensity/latest?lat={lat}&lon={lon}"
            headers = {"auth-token": "AUTH_TOKEN"}

            try:
                response = requests.get(url, headers=headers)
                data = response.json()
            except Exception:
                data = {}

            intensity = data.get("carbonIntensity", 0)
            status = (
                "Heavy" if intensity > 500 else
                "Moderate" if intensity > 300 else
                "Clean"
            )
            recommendation = {
                "Heavy": "Delay charging",
                "Moderate": "Use with caution",
                "Clean": "Good time to consume"
            }[status]

            self.next(
                carbon_intensity=intensity,
                status_label=status,
                recommendation=recommendation,
                timestamp=data.get("datetime", datetime.utcnow().isoformat())
            )
            time.sleep(60)

# ✅ Power breakdown connector
class PowerBreakdownConnector(ConnectorSubject):
    def run(self):
        import time, requests
        from datetime import datetime

        while True:
            try:
                with open("coords.json", "r") as f:
                    coords = json.load(f)
                lat = coords.get("lat", 28.6145)
                lon = coords.get("lon", 77.2078)
            except Exception:
                lat, lon = 28.6145, 77.2078

            url = f"https://api.electricitymaps.com/v3/power-breakdown/latest?lat={lat}&lon={lon}"
            headers = {"auth-token": "GKyP7cMM5TN4fgAzbRUK"}

            try:
                response = requests.get(url, headers=headers)
                data = response.json()
            except Exception:
                data = {}

            production = data.get("powerProduction", {})
            self.next(
                timestamp=data.get("datetime", datetime.utcnow().isoformat()),
                coal=production.get("coal", 0),
                solar=production.get("solar", 0),
                wind=production.get("wind", 0),
                fossil_gas=production.get("fossil_gas", 0),
                hydro=production.get("hydro", 0),
                nuclear=production.get("nuclear", 0),
                biomass=production.get("biomass", 0)
            )
            time.sleep(60)

# ✅ Boot both connectors
def start_connector():
    carbon_stream = pw.io.python.read(CarbonConnector(), schema=CarbonSignalSchema)
    pw.io.jsonlines.write(carbon_stream, "carbon_output.jsonl")

    power_stream = pw.io.python.read(PowerBreakdownConnector(), schema=PowerBreakdownSchema)
    pw.io.jsonlines.write(power_stream, "power_output.jsonl")

    pw.run()

threading.Thread(target=start_connector, daemon=True).start()
app.include_router(carbonapi)
