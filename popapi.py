from fastapi import APIRouter
from fastapi.responses import JSONResponse
import json
import threading
import pathway as pw
from pathway.io.python import ConnectorSubject

popapi = APIRouter()

# ✅ Population schema
class PopulationSchema(pw.Schema):
    city: str
    population: int
    latitude: float
    longitude: float
    timestamp: str

# ✅ Population connector
class PopulationConnector(ConnectorSubject):
    def run(self):
        import time, requests
        from datetime import datetime

        API_KEY = "1S6whAKzdBBdqsDuzIRDjQ==CnEFrfmZuRLnF3Ze"  # ← Replace with your actual API Ninjas key
        headers = {"X-Api-Key": API_KEY}

        while True:
            try:
                with open("coords.json", "r") as f:
                    coords = json.load(f)
                lat = coords.get("lat", 28.6145)
                lon = coords.get("lon", 77.2078)
            except Exception:
                lat, lon = 28.6145, 77.2078

            params = {
                "min_lat": lat - 0.14,
                "max_lat": lat + 0.14,
                "min_lon": lon - 0.14,
                "max_lon": lon + 0.14
            }

            try:
                response = requests.get("https://api.api-ninjas.com/v1/city", headers=headers, params=params)
                cities = response.json()
            except Exception:
                cities = []

            if cities:
                city = cities[0]
                self.next(
                    city=city.get("name", "Unknown"),
                    population=city.get("population", 0),
                    latitude=city.get("latitude", lat),
                    longitude=city.get("longitude", lon),
                    timestamp=datetime.utcnow().isoformat()
                )
            else:
                self.next(
                    city="Unavailable",
                    population=0,
                    latitude=lat,
                    longitude=lon,
                    timestamp=datetime.utcnow().isoformat()
                )

            time.sleep(300)  # every 5 minutes

# ✅ Boot population stream
def start_population_stream():
    pop_stream = pw.io.python.read(PopulationConnector(), schema=PopulationSchema)
    pw.io.jsonlines.write(pop_stream, "population_output.jsonl")
    pw.run()

# ✅ Start connector thread
threading.Thread(target=start_population_stream, daemon=True).start()