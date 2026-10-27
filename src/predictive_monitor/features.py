"""Features use only measurements available at the observation time."""

import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

from .schema import DERIVED_FEATURES, FEATURES, NUMERIC_FEATURES


def engineer_features(frame):
    result = frame.loc[:, FEATURES].copy()
    result["temperature_gap_k"] = result.process_temperature_k - result.air_temperature_k
    result["power_w"] = result.torque_nm * result.rotational_speed_rpm * (2 * np.pi / 60)
    result["wear_torque_min_nm"] = result.tool_wear_min * result.torque_nm
    return result


def make_pipeline(estimator):
    transform = ColumnTransformer(
        [
            ("numeric", StandardScaler(), NUMERIC_FEATURES + DERIVED_FEATURES),
            (
                "product",
                OneHotEncoder(categories=[["L", "M", "H"]], sparse_output=False),
                ["product_type"],
            ),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )
    return Pipeline(
        [
            ("engineering", FunctionTransformer(engineer_features, validate=False)),
            ("preprocessing", transform),
            ("model", estimator),
        ]
    )
