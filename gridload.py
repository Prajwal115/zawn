import json
import time
import os

POP_FILE = "population_output.jsonl"
SOTEM_FILE = "sotem_output.jsonl"
GRID_FILE = "grid_output.jsonl"

def estimate_grid_load(population, temperature):
    if temperature is None:
        temperature = 30  # fallback

    base_demand = population * 1.2 / 1000  # MW
    temp_adjusted = base_demand * (1 + max(0, (temperature - 30) * 0.07))
    return round(temp_adjusted, 2), round(base_demand, 2)

def get_latest_jsonl_entry(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r") as f:
        lines = f.readlines()
        if not lines:
            return None
        return json.loads(lines[-1])

def main():
    last_pop_ts = None
    last_temp_ts = None

    while True:
        pop_data = get_latest_jsonl_entry(POP_FILE)
        temp_data = get_latest_jsonl_entry(SOTEM_FILE)

        if not pop_data or not temp_data:
            time.sleep(5)
            continue

        pop_ts = pop_data.get("timestamp")
        temp_ts = temp_data.get("timestamp")

        # Only update if either source has changed
        if pop_ts != last_pop_ts or temp_ts != last_temp_ts:
            population = pop_data.get("population", 0)
            temperature = temp_data.get("temperature", None)
            timestamp = temp_ts or pop_ts

            final, base = estimate_grid_load(population, temperature)

            result = {
                "estimated_load_mw": final,
                "adjusted_for_temperature": final,
                "timestamp": timestamp
            }

            with open(GRID_FILE, "a") as f:
                f.write(json.dumps(result) + "\n")

            print("Updated grid_output.jsonl:", result)

            last_pop_ts = pop_ts
            last_temp_ts = temp_ts

        time.sleep(10)  # check every 10 seconds

if __name__ == "__main__":
    main()