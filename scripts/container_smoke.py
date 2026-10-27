import json
from urllib.request import urlopen

with urlopen("http://127.0.0.1:8000/assets/DEMO-01/snapshot", timeout=5) as response:
    snapshot = json.load(response)
assert len(snapshot["events"]) == 5, snapshot
assert all(event["prediction"]["condition"] == "alarm" for event in snapshot["events"])
assert all(event["observation"]["source"] == "synthetic" for event in snapshot["events"])
with urlopen("http://127.0.0.1:8501/_stcore/health", timeout=5) as response:
    assert response.status == 200
print("Container smoke passed: simulator -> HTTP -> pipeline -> SQLite; dashboard healthy")
