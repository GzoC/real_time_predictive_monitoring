"""Offline replay with an explicit logical clock; real HTTP UI uses the simulator."""

import argparse
import json
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

from predictive_monitor.inference import Predictor
from predictive_monitor.schema import DraftReview, TelemetryEvent
from predictive_monitor.simulation import measurement
from predictive_monitor.storage import Store


def run(model, output):
    predictor = Predictor(model)
    clock = datetime(2026, 11, 12, tzinfo=UTC)
    observations = []
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "events.db"
        store = Store(path)
        for i, scenario in enumerate(
            ["normal", "alarm", "alarm", "normal", "normal", "alarm", "alarm"]
        ):
            stamp = clock + timedelta(seconds=[0, 1, 2, 9, 10, 11, 12][i])
            event = TelemetryEvent(
                **measurement(i, scenario),
                event_id=f"replay:{i}",
                asset_id="REPLAY-01",
                timestamp=stamp,
                source="synthetic",
            )
            response = store.ingest(event, predictor, stamp)
            if i == 2:
                for _ in range(10):
                    assert Store(path).ingest(event, predictor, stamp)["duplicate"]
                gap = Store(path).snapshot(event.asset_id, stamp + timedelta(seconds=6))
                assert gap["condition"] == "unknown"
                assert gap["alarm"]["active_episode"]
            observations.append(
                {
                    "event_id": event.event_id,
                    "condition": response["condition"],
                    "episode_id": response["episode_id"],
                }
            )
        drafts = store.drafts("REPLAY-01")
        assert len(drafts) == 2 and drafts[1]["closed_at"] is not None
        review = store.review(
            drafts[0]["draft_id"],
            DraftReview(
                status="approved",
                reviewer="offline-demo",
                note="Synthetic evidence inspected",
                expected_revision=0,
            ),
            clock + timedelta(seconds=13),
        )
        reopened = Store(path)
        assert reopened.drafts("REPLAY-01")[0]["status"] == "approved"
        report = {
            "mode": "offline logical-clock replay, synthetic measurements",
            "model_id": predictor.metadata["model_id"],
            "replays": 10,
            "logical_measurements": len(
                reopened.snapshot("REPLAY-01", clock + timedelta(seconds=13))["events"]
            ),
            "drafts": len(drafts),
            "signal_loss_condition": gap["condition"],
            "review": review,
            "events": observations,
        }
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="var/model")
    parser.add_argument("--output", default="reports/metrics/maintenance-replay.json")
    args = parser.parse_args()
    print(json.dumps(run(args.model, args.output), indent=2))
