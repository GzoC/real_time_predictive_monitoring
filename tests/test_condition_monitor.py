import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from predictive_monitor.api import create_app
from predictive_monitor.inference import Predictor
from predictive_monitor.schema import FEATURES, Observation, TelemetryEvent
from predictive_monitor.simulation import measurement
from predictive_monitor.storage import ConflictError, Store
from predictive_monitor.training import read_dataset, train

DATA = Path(__file__).resolve().parents[1] / "data/raw/ai4i2020.csv"


@pytest.fixture(scope="session")
def artifact(tmp_path_factory):
    root = tmp_path_factory.mktemp("trained-model")
    train(DATA, root)
    return root


@pytest.fixture
def client(artifact, tmp_path):
    with TestClient(create_app(artifact, tmp_path / "events.db")) as client:
        yield client


def event(index=0, timestamp=None, **overrides):
    return TelemetryEvent(
        **{
            **measurement(index, "normal"),
            "event_id": f"test:{index}",
            "asset_id": "DEMO-01",
            "source": "synthetic",
            "timestamp": timestamp or datetime.now(UTC),
            **overrides,
        }
    )


def test_exact_physical_input_equivalence_after_reload(artifact, client):
    x, _, _ = read_dataset(DATA)
    predictor = Predictor(artifact)
    # Include held-out normal/failure rows and the two demonstration conditions.
    samples = x.iloc[[0, 50, 8000, 8500, 9000, 9999]].to_dict("records")
    samples += [measurement(0, "normal"), measurement(0, "alarm")]
    for sample in samples:
        direct = predictor.predict(Observation(**sample))
        response = client.post("/predict", json=dict(reversed(list(sample.items()))))
        assert response.status_code == 200, response.text
        assert response.json() == direct
        expected = predictor.pipeline.predict_proba(pd.DataFrame([sample], columns=FEATURES))[0, 1]
        assert direct["score"] == pytest.approx(expected, abs=1e-12)
        assert direct["condition"] in {"normal", "alarm"}


def test_training_transform_fits_only_training_partition(artifact):
    predictor = Predictor(artifact)
    x, _, _ = read_dataset(DATA)
    engineered = predictor.pipeline.named_steps["engineering"].transform(x.iloc[:6000])
    prep = predictor.pipeline.named_steps["preprocessing"]
    columns = prep.transformers_[0][2]
    scaler = prep.named_transformers_["numeric"]
    np.testing.assert_allclose(scaler.mean_, engineered[columns].mean().to_numpy())
    assert scaler.n_samples_seen_ == 6000
    assert predictor.metadata["partitions"]["test"]["udi_first"] == 8001
    assert predictor.pipeline.feature_names_in_.tolist() == FEATURES
    assert not set(FEATURES) & {
        "Machine failure",
        "TWF",
        "HDF",
        "PWF",
        "OSF",
        "RNF",
        "UDI",
        "Product ID",
    }


@pytest.mark.parametrize(
    "field,value",
    [
        ("air_temperature_k", 20),
        ("torque_nm", -1),
        ("torque_nm", "40"),
        ("rotational_speed_rpm", 1500.5),
        ("rotational_speed_rpm", True),
        ("tool_wear_min", -1),
        ("product_type", "unknown"),
        ("Machine failure", 1),
    ],
)
def test_invalid_physical_contract_is_422(client, field, value):
    response = client.post("/predict", json={**measurement(0), field: value})
    assert response.status_code == 422


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_sensor_values_rejected(value):
    with pytest.raises(ValidationError):
        Observation(**{**measurement(0), "torque_nm": value})


def test_missing_artifact_is_unavailable_not_a_prediction(tmp_path):
    with TestClient(create_app(tmp_path / "missing", tmp_path / "db.sqlite")) as client:
        assert client.get("/health").status_code == 503
        response = client.post("/predict", json=measurement(0))
        assert response.status_code == 503
        assert "score" not in response.json()


def test_corrupt_artifact_rejected_before_loading(artifact, tmp_path):
    (tmp_path / "manifest.json").write_bytes((artifact / "manifest.json").read_bytes())
    (tmp_path / "pipeline.joblib").write_bytes(b"not a trusted model")
    with pytest.raises(ValueError, match="checksum"):
        Predictor(tmp_path)


def test_schema_mismatch_rejected(artifact, tmp_path):
    manifest = json.loads((artifact / "manifest.json").read_text())
    manifest["features"] = list(reversed(FEATURES))
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="contract"):
        Predictor(tmp_path)


def test_ingest_is_persistent_idempotent_and_conflicts_are_409(artifact, client, tmp_path):
    first = event()
    response = client.post("/events", json=first.model_dump(mode="json"))
    assert response.status_code == 200
    assert response.json()["duplicate"] is False
    again = client.post("/events", json=first.model_dump(mode="json"))
    assert again.status_code == 200 and again.json()["duplicate"] is True
    conflict = first.model_copy(update={"torque_nm": 44.0})
    assert client.post("/events", json=conflict.model_dump(mode="json")).status_code == 409
    assert client.get("/assets").json() == {"assets": ["DEMO-01"]}
    snap = client.get("/assets/DEMO-01/snapshot").json()
    assert len(snap["events"]) == 1
    assert snap["events"][0]["prediction"]["model_id"] == response.json()["model_id"]


def test_restart_staleness_and_recovery(artifact, tmp_path):
    now = datetime.now(UTC)
    path = tmp_path / "events.db"
    predictor = Predictor(artifact)
    first = event(timestamp=now)
    Store(path).ingest(first, predictor, now)
    reopened = Store(path)
    assert reopened.snapshot(first.asset_id, now)["stale"] is False
    stale = reopened.snapshot(first.asset_id, now + timedelta(seconds=6))
    assert stale["condition"] == "unknown"
    assert len(stale["events"]) == 1
    later = event(1, now + timedelta(seconds=7))
    reopened.ingest(later, predictor, now + timedelta(seconds=7))
    assert reopened.snapshot(first.asset_id, now + timedelta(seconds=7))["stale"] is False


def test_no_data_cannot_be_normal(client):
    snap = client.get("/assets/unknown/snapshot").json()
    assert snap["condition"] == "unknown" and snap["age_seconds"] is None


def test_out_of_order_and_future_events_rejected(artifact, tmp_path):
    now = datetime.now(UTC)
    store = Store(tmp_path / "events.db")
    predictor = Predictor(artifact)
    store.ingest(event(timestamp=now), predictor, now)
    with pytest.raises(ConflictError):
        store.ingest(event(1, now - timedelta(seconds=1)), predictor, now)
    with pytest.raises(ValueError, match="future"):
        store.ingest(event(2, now + timedelta(seconds=6)), predictor, now)


def test_naive_timestamp_rejected(client):
    body = event().model_dump(mode="json")
    body["timestamp"] = "2026-10-27T12:00:00"
    assert client.post("/events", json=body).status_code == 422


def test_outside_training_range_remains_visible(artifact):
    sample = Observation(**{**measurement(0), "air_temperature_k": 340.0})
    assert "air_temperature_k" in Predictor(artifact).predict(sample)["out_of_training_range"]


def test_simulation_has_real_gap_and_reproducible_recovery():
    assert measurement(3) == measurement(3)
    assert measurement(0) != measurement(10)
    assert all(measurement(i) is None for i in range(20, 29))
    assert measurement(29) is not None
