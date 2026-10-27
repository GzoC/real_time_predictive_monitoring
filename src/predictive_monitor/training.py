"""Deterministic training and an untouched holdout; no notebook-specific transformations."""

import hashlib
import json
import platform
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    fbeta_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.tree import DecisionTreeClassifier, export_text

from .features import make_pipeline
from .schema import FEATURES, NUMERIC_FEATURES, SCHEMA_VERSION, Observation

RENAME = dict(
    zip(
        [
            "Type",
            "Air temperature [K]",
            "Process temperature [K]",
            "Rotational speed [rpm]",
            "Torque [Nm]",
            "Tool wear [min]",
        ],
        FEATURES,
        strict=True,
    )
)


def read_dataset(path):
    raw = pd.read_csv(path)
    required = {*RENAME, "UDI", "Machine failure"}
    if not required.issubset(raw.columns) or raw.empty or raw.isna().any().any():
        raise ValueError("Dataset schema or missing values are invalid")
    if raw.UDI.duplicated().any() or not raw.UDI.is_monotonic_increasing:
        raise ValueError("UDI must be unique and ordered")
    if not raw["Machine failure"].isin([0, 1]).all():
        raise ValueError("Target must be binary")
    features = raw.rename(columns=RENAME).loc[:, FEATURES].copy()
    for record in features.to_dict("records"):
        Observation.model_validate(record)
    return features, raw["Machine failure"].astype(int), raw.UDI


def evaluate(y, scores, threshold):
    predictions = (np.asarray(scores) >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, predictions, labels=[0, 1]).ravel()
    return {
        "samples": len(y),
        "positives": int(np.sum(y)),
        "threshold": float(threshold),
        "confusion_matrix": [[int(tn), int(fp)], [int(fn), int(tp)]],
        "precision": float(precision_score(y, predictions, zero_division=0)),
        "recall": float(recall_score(y, predictions, zero_division=0)),
        "f2": float(fbeta_score(y, predictions, beta=2, zero_division=0)),
        "false_alarm_rate": float(fp / (fp + tn)) if fp + tn else None,
        "miss_rate": float(fn / (fn + tp)) if fn + tp else None,
        "average_precision": float(average_precision_score(y, scores)),
        "roc_auc": float(roc_auc_score(y, scores)),
    }


def choose_threshold(y, scores):
    # Validation only. Ties favor the higher threshold (fewer alarms).
    return max(
        np.linspace(0.05, 0.95, 19),
        key=lambda t: (
            fbeta_score(y, scores >= t, beta=2, zero_division=0),
            t,
        ),
    )


def train(data_path, output_dir):
    x, y, ids = read_dataset(data_path)
    n_train, n_validation = int(len(x) * 0.6), int(len(x) * 0.8)
    partitions = {
        "train": slice(0, n_train),
        "validation": slice(n_train, n_validation),
        "test": slice(n_validation, len(x)),
    }
    if any(len(y.iloc[s]) < 20 or y.iloc[s].nunique() != 2 for s in partitions.values()):
        raise ValueError("Each ordered partition must have at least 20 samples and both classes")
    train_slice, validation_slice = partitions["train"], partitions["validation"]
    model = make_pipeline(
        GradientBoostingClassifier(
            n_estimators=160,
            learning_rate=0.07,
            max_leaf_nodes=15,
            max_depth=3,
            min_samples_leaf=10,
            random_state=42,
        )
    )
    baseline = make_pipeline(
        DecisionTreeClassifier(
            max_depth=3,
            min_samples_leaf=30,
            class_weight="balanced",
            random_state=42,
        )
    )
    model.fit(x.iloc[train_slice], y.iloc[train_slice])
    baseline.fit(x.iloc[train_slice], y.iloc[train_slice])
    threshold = float(
        choose_threshold(
            y.iloc[validation_slice], model.predict_proba(x.iloc[validation_slice])[:, 1]
        )
    )
    baseline_threshold = float(
        choose_threshold(
            y.iloc[validation_slice], baseline.predict_proba(x.iloc[validation_slice])[:, 1]
        )
    )
    data_hash = hashlib.sha256(Path(data_path).read_bytes()).hexdigest()
    report = {
        "task": "current_condition_classification",
        "future_horizon": None,
        "dataset": {
            "name": "AI4I 2020",
            "doi": "10.24432/C5HS5C",
            "synthetic": True,
            "sha256": data_hash,
            "rows": len(x),
        },
        "schema_version": SCHEMA_VERSION,
        "features": FEATURES,
        "excluded": ["UDI", "Product ID", "Machine failure", "TWF", "HDF", "PWF", "OSF", "RNF"],
        "split": "First 60% train, next 20% validation, last 20% test in published UDI order; no actual timestamps or asset groups available.",
        "partitions": {
            name: {
                "rows": len(x.iloc[s]),
                "positives": int(y.iloc[s].sum()),
                "udi_first": int(ids.iloc[s].iloc[0]),
                "udi_last": int(ids.iloc[s].iloc[-1]),
            }
            for name, s in partitions.items()
        },
        "threshold_selection": "Maximum validation F2 on 0.05..0.95, step 0.05; no test tuning",
        "threshold": threshold,
        "versions": {
            "python": platform.python_version(),
            "sklearn": sklearn.__version__,
            "numpy": np.__version__,
            "pandas": pd.__version__,
        },
        "training_range": {
            name: {
                "min": float(x.iloc[train_slice][name].min()),
                "max": float(x.iloc[train_slice][name].max()),
            }
            for name in NUMERIC_FEATURES
        },
        "evaluation": {},
    }
    for name in ("validation", "test"):
        s = partitions[name]
        report["evaluation"][name] = {
            "gradient_boosting": evaluate(
                y.iloc[s], model.predict_proba(x.iloc[s])[:, 1], threshold
            ),
            "depth_3_rules": evaluate(
                y.iloc[s], baseline.predict_proba(x.iloc[s])[:, 1], baseline_threshold
            ),
            "always_normal": evaluate(y.iloc[s], np.zeros(len(y.iloc[s])), 0.5),
        }
    sample = x.iloc[[n_validation]]
    model.predict_proba(sample)  # Warm up outside the timed observations.
    timings = []
    for _ in range(100):
        start = time.perf_counter()
        model.predict_proba(sample)
        timings.append((time.perf_counter() - start) * 1000)
    report["latency"] = {
        "scope": "Single-row pipeline.predict_proba only; excludes HTTP, storage and UI",
        "repetitions": 100,
        "median_ms": float(np.median(timings)),
        "p95_ms": float(np.percentile(timings, 95)),
        "platform": platform.platform(),
    }
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output / "pipeline.joblib")
    report["artifact_sha256"] = hashlib.sha256(
        (output / "pipeline.joblib").read_bytes()
    ).hexdigest()
    report["model_id"] = report["artifact_sha256"][:16]
    (output / "manifest.json").write_text(
        json.dumps(report, indent=2, allow_nan=False), encoding="utf-8"
    )
    rules = export_text(
        baseline.named_steps["model"],
        feature_names=list(baseline.named_steps["preprocessing"].get_feature_names_out()),
    )
    (output / "baseline-rules.txt").write_text(
        "Thresholds below are in standardized feature units; pipeline applies the training scaler.\n"
        + rules,
        encoding="utf-8",
    )
    return report
