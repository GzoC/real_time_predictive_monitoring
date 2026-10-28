import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression

spec = importlib.util.spec_from_file_location(
    "legacy_audit", Path(__file__).parents[1] / "scripts/audit_legacy_maintenance.py"
)
study = importlib.util.module_from_spec(spec)
spec.loader.exec_module(study)


def test_research_allowlist_and_train_only_scaler():
    frame = pd.DataFrame({name: [1.0, 2.0, 3.0, 4.0, 99999.0] for name in study.FEATURES})
    frame["machine_id"] = range(5)
    frame["failure_type"] = ["No Failure", "Fault", "No Failure", "Fault", "Fault"]
    frame["maintenance_required"] = [0, 1, 0, 1, 1]
    x, y = study.split_inputs(frame)
    assert x.columns.tolist() == study.FEATURES
    assert y.tolist() == [0, 1, 0, 1, 1]
    model = study.make_model(LogisticRegression()).fit(x.iloc[:4], y.iloc[:4])
    assert model.named_steps["scale"].n_samples_seen_ == 4
    assert np.allclose(model.named_steps["scale"].mean_, 2.5)
    model.predict_proba(x.iloc[4:])
    assert model.named_steps["scale"].n_samples_seen_ == 4


def test_legacy_data_must_match_pinned_source(tmp_path):
    path = tmp_path / "altered.csv"
    path.write_text("unverified replacement")
    with pytest.raises(ValueError, match="differs"):
        study.audit(path)
