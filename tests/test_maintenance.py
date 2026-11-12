from datetime import UTC, datetime, timedelta

import pytest

from predictive_monitor.schema import DraftReview, TelemetryEvent
from predictive_monitor.simulation import measurement
from predictive_monitor.storage import ConflictError, Store


class Classifier:
    metadata = {"model_id": "test-model"}

    def predict(self, event):
        return {
            "condition": "alarm" if event.torque_nm > 60 else "normal",
            "score": 0.9 if event.torque_nm > 60 else 0.1,
            "threshold": 0.5,
            "model_id": "test-model",
        }


def send(store, index, alarm=True, quality="good", seconds=None):
    now = datetime(2026, 11, 12, tzinfo=UTC) + timedelta(
        seconds=seconds if seconds is not None else index
    )
    event = TelemetryEvent(
        **measurement(index, "alarm" if alarm else "normal"),
        event_id=f"e{index}",
        asset_id="PUMP-01",
        timestamp=now,
        source="synthetic",
        quality=quality,
    )
    return event, store.ingest(event, Classifier(), now)


def test_ten_replays_restart_recovery_and_new_episode(tmp_path):
    path = tmp_path / "db"
    store = Store(path)
    send(store, 0)
    event, result = send(store, 1)
    for _ in range(10):
        store = Store(path)
        assert store.ingest(event, Classifier(), event.timestamp)["duplicate"]
    assert len(store.snapshot("PUMP-01", event.timestamp)["events"]) == 2
    assert len(store.drafts("PUMP-01")) == 1
    assert store.drafts("PUMP-01")[0]["episode_id"] == result["episode_id"]
    stale = store.snapshot("PUMP-01", event.timestamp + timedelta(seconds=8))
    assert stale["condition"] == "unknown"
    assert stale["alarm"]["active_episode"] == result["episode_id"]
    send(store, 2, False)
    assert store.drafts("PUMP-01")[0]["closed_at"] is None
    send(store, 3, False)
    assert store.drafts("PUMP-01")[0]["closed_at"] is not None
    send(store, 4)
    send(store, 5)
    assert len(Store(path).drafts("PUMP-01")) == 2


def test_quality_and_gaps_cannot_confirm_or_recover(tmp_path):
    store = Store(tmp_path / "db")
    send(store, 0)
    _, invalid = send(store, 1, quality="bad")
    assert invalid["condition"] == "invalid" and invalid["score"] is None
    send(store, 2)
    assert not store.drafts("PUMP-01")
    send(store, 3, seconds=9)
    assert not store.drafts("PUMP-01")
    send(store, 4, seconds=10)
    assert len(store.drafts("PUMP-01")) == 1
    send(store, 5, False, seconds=11)
    send(store, 6, False, quality="uncertain", seconds=12)
    send(store, 7, False, seconds=13)
    assert store.drafts("PUMP-01")[0]["closed_at"] is None
    send(store, 8, False, seconds=14)
    assert store.drafts("PUMP-01")[0]["closed_at"] is not None


def test_review_audit_optimistic_lock_and_restart(tmp_path):
    path = tmp_path / "db"
    store = Store(path)
    send(store, 0)
    send(store, 1)
    draft = store.drafts("PUMP-01")[0]
    review = DraftReview(
        status="approved", reviewer="Gonzalo", note="Inspección simulada", expected_revision=0
    )
    assert not store.review(draft["draft_id"], review)["external_dispatch"]
    with pytest.raises(ConflictError):
        store.review(draft["draft_id"], review)
    reopened = Store(path).drafts("PUMP-01")[0]
    assert reopened["status"] == "approved"
    assert reopened["changes"][1]["old_status"] == "draft"
    assert reopened["changes"][1]["reviewer"] == "Gonzalo"
    assert len(reopened["changes"]) == 2
