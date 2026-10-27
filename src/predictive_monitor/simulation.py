"""Replays documented example measurements with real arrival times, never training rows."""

import random
import time
import uuid
from datetime import UTC, datetime

import requests


def measurement(index, scenario="cycle", seed=42):
    if scenario not in {"normal", "alarm", "cycle"}:
        raise ValueError("Unknown scenario")
    phase = index % 40
    if scenario == "cycle" and 20 <= phase < 29:
        return None  # Intentional loss of signal; no zeros or fabricated observations.
    alarm = scenario == "alarm" or (scenario == "cycle" and 10 <= phase < 20)
    rng = random.Random(seed + index)
    return {
        "product_type": "L",
        "air_temperature_k": round(300 + rng.uniform(-0.1, 0.1), 2),
        "process_temperature_k": round((307 if alarm else 310) + rng.uniform(-0.1, 0.1), 2),
        "rotational_speed_rpm": (1200 if alarm else 1500) + rng.randint(-10, 10),
        "torque_nm": round((65 if alarm else 40) + rng.uniform(-1, 1), 2),
        "tool_wear_min": 230 if alarm else 50,
    }


def simulate(api_url, asset_id="DEMO-01", steps=80, interval=1.0, scenario="cycle"):
    if steps < 1 or steps > 100000 or interval < 0.05:
        raise ValueError("steps must be 1..100000 and interval at least 0.05 seconds")
    run = uuid.uuid4().hex[:12]
    with requests.Session() as session:
        for i in range(steps):
            sample = measurement(i, scenario)
            if sample is not None:
                event = {
                    **sample,
                    "asset_id": asset_id,
                    "event_id": f"{run}:{i}",
                    "timestamp": datetime.now(UTC).isoformat(),
                    "source": "synthetic",
                }
                # Retry the exact event after uncertain delivery; the server is idempotent.
                for attempt in range(3):
                    try:
                        response = session.post(
                            api_url.rstrip("/") + "/events", json=event, timeout=5
                        )
                        response.raise_for_status()
                        break
                    except requests.RequestException:
                        if attempt == 2:
                            raise
                        time.sleep(0.5 * (attempt + 1))
            if i < steps - 1:
                time.sleep(interval)
