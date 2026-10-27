"""Load only locally trained, trusted artifacts. A hash detects corruption, not malicious input."""

import hashlib
import json
from pathlib import Path

import joblib
import pandas as pd
import sklearn

from .schema import FEATURES, SCHEMA_VERSION, Observation


class Predictor:
    def __init__(self, directory):
        root = Path(directory)
        self.metadata = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
        if (
            self.metadata["schema_version"] != SCHEMA_VERSION
            or self.metadata["features"] != FEATURES
        ):
            raise ValueError("Artifact feature contract mismatch")
        if self.metadata["versions"]["sklearn"] != sklearn.__version__:
            raise ValueError("Train and serve with the same scikit-learn version")
        payload = (root / "pipeline.joblib").read_bytes()
        if hashlib.sha256(payload).hexdigest() != self.metadata["artifact_sha256"]:
            raise ValueError("Artifact checksum mismatch")
        self.pipeline = joblib.load(root / "pipeline.joblib")

    def predict(self, observation: Observation):
        frame = pd.DataFrame([observation.features()], columns=FEATURES)
        score = float(self.pipeline.predict_proba(frame)[0, 1])
        threshold = self.metadata["threshold"]
        outside = [
            name
            for name, bounds in self.metadata["training_range"].items()
            if not bounds["min"] <= getattr(observation, name) <= bounds["max"]
        ]
        return {
            "condition": "alarm" if score >= threshold else "normal",
            "score": score,
            "threshold": threshold,
            "model_id": self.metadata["model_id"],
            "task": "current_condition_classification",
            "out_of_training_range": outside,
        }
