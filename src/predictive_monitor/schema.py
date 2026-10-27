"""Physical inputs shared by training, direct inference and HTTP inference."""

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

FEATURES = [
    "product_type",
    "air_temperature_k",
    "process_temperature_k",
    "rotational_speed_rpm",
    "torque_nm",
    "tool_wear_min",
]
NUMERIC_FEATURES = FEATURES[1:]
DERIVED_FEATURES = ["temperature_gap_k", "power_w", "wear_torque_min_nm"]
SCHEMA_VERSION = 1


class Observation(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False, frozen=True)
    product_type: Literal["L", "M", "H"]
    air_temperature_k: float = Field(ge=270, le=360, strict=True)
    process_temperature_k: float = Field(ge=270, le=400, strict=True)
    rotational_speed_rpm: int = Field(ge=1, le=5000, strict=True)
    torque_nm: float = Field(ge=0, le=150, strict=True)
    tool_wear_min: int = Field(ge=0, le=500, strict=True)

    def features(self):
        return {name: getattr(self, name) for name in FEATURES}


class TelemetryEvent(Observation):
    event_id: str = Field(min_length=1, max_length=80, pattern=r"^[a-zA-Z0-9_.:-]+$")
    asset_id: str = Field(min_length=1, max_length=40, pattern=r"^[a-zA-Z0-9_-]+$")
    timestamp: datetime
    source: Literal["synthetic", "external"] = "external"

    @field_validator("timestamp")
    @classmethod
    def aware_utc(cls, value):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must include its UTC offset")
        return value.astimezone(UTC)
