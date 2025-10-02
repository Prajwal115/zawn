# ZAWN 🌍  
*A modular tool to understand Carbon Intensity & Grid, Sustainbility and Pollution Impact.*

ZAWN is a region-aware sustainability dashboard that streams carbon intensity, AQI, solar radiation, and temperature data in real time. 
Designed for researchers, responders, and clarity-seekers, ZAWN transforms fragmented environmental signals into actionable insights.

---

## 🔥 Problem

- Real-time carbon and AQI data is scattered across inconsistent APIs.
- Dashboards often ignore regional context, streaming global data instead of local truth.
- Sustainability metrics like carbon-free % and grid demand are abstract and siloed.
- Users lack a unified, transparent view of planetary health.

---

## 🌱 Solution

- **FastAPI backend** with modular routes for each signal.
- **Frontend dashboard** with clarity-first tiles, verdicts, and a carbon intensity graph.
- **Coordinate-aware ingestion** for region-specific insights.
- **Fallback logic** and teardown philosophy for mocked data and API failures.


---

## ⚙️ Process

- Signals streamed to `.jsonl` logs for reproducibility and demo clarity.
- Graphs rendered with Plotly.js (Carbon Intensity vs Time).
- Login/logout system with localStorage for user sessions.
- Deployment via Render with environment variables for secure API key handling.

---

## 🧬 Pathway Integration

ZAWN uses [Pathway](https://pathway.com) as a **streaming data orchestrator** to simulate and process carbon intensity signals in real time. Pathway enables:

- **Live ingestion** of carbon data from ElectricityMap or mocked sources.
- **Chronological ordering** and deduplication of signal entries.
- **Triggering verdict logic** based on carbon thresholds (e.g., “Delay charging” at >500 gCO₂/kWh).

Pathway acts as the backbone for ZAWN’s signal pipeline—ensuring clarity, modularity, and resilience.

---

## 🚀 Deployment

- Hosted on [Render](https://zawn.render.com) (https://zawn.render.com)
- API keys stored securely via Render environment variables
- `requirements.txt` included for dependency management

---

## 🧪 Demo Highlights

- Carbon intensity graph with rising and falling trends
- Region-aware dashboard wired to Delhi
- Sustainability index logic (mocked but modular)
- Honest fallback tiles for unavailable signals
- **[Coming Soon] Simulations** by modifying parameters and then getting simulated results.
---

## 📁 How to run it

1. Clone the repository
```python
git clone https://github.com/your-username/zawn.git
cd zawn
```
2. Install Dependencies. Make sure you have Python 3.9+ installed. Then run -
```python
pip install -r requirements.txt
```
3. Set up environment variables for ```API_KEY1```, ```API_KEY2```, ```AUTH_KEY``` from OpenWeatherMapAPI, WorldAQI, ElectricityMapAPI
4. uvicorn main:app --host 0.0.0.0 --port 10000
5. It will run on your localhost.
6. Test various connections like ```http://localhost:8000/aqi```,  ```http://localhost:8000/airq```

## About
Made by Prajwal - a curious developer and a UI UX designer for a project. Also known as Innovative Challenger.

Signing off,
Prajwal
