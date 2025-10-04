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
from popapi import popapi
from fastapi import FastAPI, Request

app = FastAPI()
app.include_router(aqiapi2)
app.include_router(carbonapi)
app.include_router(sotemapi)
app.include_router(popapi)
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
    

@app.get("/simulate", response_class=FileResponse)
async def serve_result():
    return FileResponse("simulate.html")

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

@app.get("/population-log")
def get_latest_population_log():
    try:
        with open("population_output.jsonl", "r") as f:
            lines = f.readlines()
        if not lines:
            return {"error": "No population data available"}
        latest = json.loads(lines[-1])
        return JSONResponse(content=latest)
    except Exception as e:
        return {"error": f"Failed to read population log: {str(e)}"}
    
@app.get("/grid-log")
def get_latest_grid_log():
    try:
        with open("grid_output.jsonl", "r") as f:
            lines = f.readlines()
        if not lines:
            return {"error": "No grid load data available"}
        latest = json.loads(lines[-1])
        return JSONResponse(content=latest)
    except Exception as e:
        return {"error": f"Failed to read grid load log: {str(e)}"}
    
from fastapi import Request
from fastapi.responses import JSONResponse
import json
import google.generativeai as genai
GEMINI_API_KEY = "AIzaSyBl_DfGOAeTq81UFNtmd1gNiWZ-EawoBhc"  # Replace with your actual API key
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.0-flash")

@app.post("/gemini-response")
async def gemini_response(request: Request):
    payload = await request.json()
    user_prompt = payload.get("user_prompt", "")
    coordinates = payload.get("coordinates", {})
    parameters = payload.get("parameters", {})

    prompt = f"""
You are a simulation assistant. Based on the following scenario and environmental parameters, suggest updated values and provide a 2-line summary.

Scenario: {user_prompt}
Coordinates: Latitude {coordinates.get('latitude')}, Longitude {coordinates.get('longitude')}
Current Parameters:
{json.dumps(parameters, indent=2)}

Respond ONLY in this JSON format:
{{
  "updated_values": {{
    "aqi-value": "142",
    "grid-load-value": "8.1 GW"
  }},
  "summary": "Heatwave increases grid stress. AQI worsens due to stagnant air."
}}
"""

    try:
        response = gemini_model.generate_content(prompt)
        raw_text = response.text.strip()
        print("Raw Gemini response:", raw_text)

        # Strip Markdown code block if present
        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()

        parsed = json.loads(raw_text)
        updated_values = parsed.get("updated_values", {})
        summary = parsed.get("summary", "No summary returned.")

        return JSONResponse(content={"updated_values": updated_values, "summary": summary})

    except Exception as e:
        print("Gemini SDK error:", str(e))
        return JSONResponse(content={"error": f"Gemini SDK failed: {str(e)}"})
