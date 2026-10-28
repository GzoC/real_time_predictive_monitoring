import pandas as pd

from predictive_monitor.charts import chart_data, telemetry_chart


def test_missing_signal_breaks_each_series_without_inventing_measurements():
    frame = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                [
                    "2026-10-28T10:00:00Z",
                    "2026-10-28T10:00:01Z",
                    "2026-10-28T10:00:11Z",
                    "2026-10-28T10:00:12Z",
                ]
            ),
            "score": [0.1, 0.9, 0.2, 0.3],
            "threshold": [0.45] * 4,
        }
    )
    long = chart_data(frame, ["score", "threshold"])
    assert len(long) == 8
    for _, series in long.groupby("variable"):
        assert series.segment.tolist() == [0, 0, 1, 1]
        assert series.timestamp.tolist() == frame.timestamp.tolist()
    spec = telemetry_chart(frame, ["score", "threshold"]).to_dict()
    assert spec["encoding"]["detail"]["field"] == "segment"
    assert spec["encoding"]["y"]["scale"]["zero"] is False
    assert spec["encoding"]["x"]["scale"]["type"] == "utc"
    assert long.utc_label.iloc[0] == "2026-10-28 10:00:00 UTC"


def test_short_irregular_intervals_stay_in_one_segment():
    frame = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(["2026-10-28T10:00:00Z", "2026-10-28T10:00:04Z"]),
            "torque_nm": [35.0, 36.0],
        }
    )
    assert chart_data(frame, ["torque_nm"]).segment.tolist() == [0, 0]
