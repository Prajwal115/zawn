from fastapi import FastAPI
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from carbonapi import carbonapi
from airqapi import airqapi  # ← Import your new router
from aqiapi2 import aqiapi2
import os
import json
from fastapi.responses import JSONResponse
from sotem import sotemapi
from fastapi import FastAPI, Request

app = FastAPI()
app.include_router(aqiapi2)
app.include_router(carbonapi)
app.include_router(sotemapi)
app.include_router(airqapi)  # ← Integrate it here

app.mount("/res", StaticFiles(directory="res"), name="static")

@app.get("/dash_2")
async def update_coords_from_form(request: Request):
    query_params = dict(request.query_params)
    lat = float(query_params.get("latitude", 0))
    lon = float(query_params.get("longitude", 0))


    # Write to coords.json
    with open("coords.json", "w") as f:
        json.dump({"lat": lat, "lon": lon}, f)

    print(f"Updated coords.json with: {lat}, {lon}")

    # Redirect to dashboard or wherever you want
    return RedirectResponse(url="/home")


@app.post("/update-coordinates")
async def update_coordinates(request: Request):
    payload = await request.json()
    lat = payload.get("lat")
    lon = payload.get("lon")

    if lat is None or lon is None:
        return {"error": "Missing lat/lon"}

    with open("coords.json", "w") as f:
        json.dump({"lat": lat, "lon": lon}, f)

    return {"status": "Coordinates updated"}
@app.get("/services", response_class=FileResponse)
async def serve_services():
    return FileResponse("services.html")

@app.get("/carbon-log")
def get_carbon_log():
    with open("carbon_output.jsonl", "r") as f:
        lines = f.readlines()
    return {"log": lines[-1]}  # return latest entry


@app.get("/aqi2-log")
def get_latest_aqi2_log():
    try:
        with open("aqi2.jsonl", "r") as f:
            lines = f.readlines()
        if not lines:
            return {"error": "No AQI data available"}
        latest = json.loads(lines[-1])
        return JSONResponse(content=latest)
    except Exception as e:
        return {"error": f"Failed to read AQI log: {str(e)}"}


@app.get("/sotem-log")
def get_latest_sotem_log():
    try:
        with open("sotem_output.jsonl", "r") as f:
            lines = f.readlines()
        if not lines:
            return {"error": "No solar/temperature data available"}
        latest = json.loads(lines[-1])
        return JSONResponse(content=latest)
    except Exception as e:
        return {"error": f"Failed to read solar/temperature log: {str(e)}"}
    
@app.get("/airq-log")
def get_latest_airq_log():
    try:
        with open("airq_latest.json", "r") as f:
            latest = json.load(f)
        return JSONResponse(content=latest)
    except Exception as e:
        return {"error": f"Failed to read latest AQI snapshot: {str(e)}"}
    

@app.get("/result", response_class=FileResponse)
async def serve_result():
    return FileResponse("result.html")

@app.get("/", response_class=FileResponse)
async def serve_services():
    return FileResponse("index.html")

@app.get("/login", response_class=FileResponse)
async def serve_services():
    return FileResponse("login.html")

@app.get("/register", response_class=FileResponse)
async def serve_services():
    return FileResponse("register.html")

@app.get("/home", response_class=FileResponse)
async def serve_services():
    return FileResponse("dash.html")

@app.get("/graph", response_class=FileResponse)
async def serve_services():
    return FileResponse("graph.html")


@app.get("/logout", response_class=FileResponse)
async def serve_services():
    return FileResponse("logout.html")

@app.get("/carbon-graph-data")
def carbon_graph_data():
    with open("carbon_output.jsonl") as f:
        lines = f.readlines()[-30:]  # last 30 entries
    data = [json.loads(line) for line in lines]
    return data