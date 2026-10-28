"""Forensic experiment on an unverified legacy dataset, never a deployment model."""

import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from predictive_monitor.training import choose_threshold, evaluate

LEGACY_SHA256 = "a44c2233ed82dd3eb07aa6bf6f35e5fb6ec13be78ea52023bb51e6e0346d061d"
FEATURES = ["operating_hours", "temperature", "vibration", "pressure", "humidity"]


def split_inputs(frame):
    """Allow-list excludes identifiers, diagnostic information and the label."""
    x = frame.loc[:, FEATURES].copy()
    y = frame.maintenance_required.copy()
    if x.isna().any().any() or not np.isfinite(x.to_numpy()).all():
        raise ValueError("Features must be finite and complete")
    if not y.isin([0, 1]).all():
        raise ValueError("Target must be binary")
    return x, y.astype(int)


def make_model(classifier):
    return Pipeline([("scale", StandardScaler()), ("classifier", classifier)])


def audit(path):
    data = path.read_bytes()
    source_hash = hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()
    if source_hash != LEGACY_SHA256:
        raise ValueError("The legacy CSV differs from the audited source; review provenance first")
    frame = pd.read_csv(path)
    x, y = split_inputs(frame)
    if len(frame) != 10000 or frame.machine_id.nunique() != len(frame):
        raise ValueError("Unexpected row identifiers or count")
    train_ids, remaining = train_test_split(
        np.arange(len(x)), test_size=0.4, stratify=y, random_state=42
    )
    validation_ids, test_ids = train_test_split(
        remaining, test_size=0.5, stratify=y.iloc[remaining], random_state=42
    )
    models = {
        "logistic_regression": make_model(LogisticRegression(max_iter=2000, random_state=42)),
        "gradient_boosting": make_model(
            GradientBoostingClassifier(
                n_estimators=100, max_depth=2, min_samples_leaf=20, random_state=42
            )
        ),
    }
    metrics = {}
    for name, pipeline in models.items():
        pipeline.fit(x.iloc[train_ids], y.iloc[train_ids])
        threshold = choose_threshold(
            y.iloc[validation_ids], pipeline.predict_proba(x.iloc[validation_ids])[:, 1]
        )
        scores = pipeline.predict_proba(x.iloc[test_ids])[:, 1]
        metrics[name] = evaluate(y.iloc[test_ids], scores, threshold)
        assert pipeline.named_steps["scale"].n_samples_seen_ == len(train_ids)
    metrics["always_normal"] = evaluate(y.iloc[test_ids], np.zeros(len(test_ids)), 0.5)
    metrics["always_alarm"] = evaluate(y.iloc[test_ids], np.ones(len(test_ids)), 0.5)
    for metric in metrics.values():
        tn, fp = metric["confusion_matrix"][0]
        fn, tp = metric["confusion_matrix"][1]
        metric["illustrative_cost_fp1_fn10"] = fp + 10 * fn
        metric["accuracy"] = (tn + tp) / len(test_ids)
    leaked = frame.failure_type.ne("No Failure").astype(int)
    return {
        "scope": "Forensic label classification on unverified legacy data; no future horizon or plant validation",
        "source": {
            "repository": "GzoC/predictive_maintenance_01",
            "commit": "c69f8024fd1f014f7f2de591f5594cc21b14a69d",
            "sha256": source_hash,
            "hash_scope": "CSV bytes with CRLF converted to LF for Git checkout portability; values unchanged",
            "file_bytes_sha256": hashlib.sha256(data).hexdigest(),
            "provenance": "unknown",
            "data_license": "unverified",
            "rows": len(frame),
        },
        "environment": {"python": platform.python_version(), "sklearn": sklearn.__version__},
        "leakage": {
            "rule": "failure_type != No Failure",
            "matches": int((leaked == y).sum()),
            "fraction": float((leaked == y).mean()),
            "cross_tab": pd.crosstab(frame.failure_type, y).to_dict(),
        },
        "features": FEATURES,
        "excluded": ["machine_id", "failure_type", "maintenance_required"],
        "split": {
            "method": "random stratified 60/20/20, seed42; not temporal or grouped",
            **{
                name: {
                    "rows": len(ids),
                    "positives": int(y.iloc[ids].sum()),
                    "indices_sha256": hashlib.sha256(
                        np.asarray(ids, dtype="<i8").tobytes()
                    ).hexdigest(),
                }
                for name, ids in [
                    ("train", train_ids),
                    ("validation", validation_ids),
                    ("test", test_ids),
                ]
            },
        },
        "selection": "Fixed models; threshold maximizes validation F2 on 0.05..0.95 grid. No test tuning.",
        "cost": "Illustration only: FP=1, FN=10 arbitrary units, not measured plant costs; not used for fitting or selection",
        "test": metrics,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--legacy-csv", type=Path, required=True)
    parser.add_argument(
        "--output", type=Path, default=Path("reports/research/legacy_maintenance_audit.json")
    )
    args = parser.parse_args()
    report = audit(args.legacy_csv)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(args.output)
    print(json.dumps({"leakage": report["leakage"]["fraction"], "test": report["test"]}, indent=2))


if __name__ == "__main__":
    main()
