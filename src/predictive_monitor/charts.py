"""Charts preserve missing telemetry as disconnected segments, never invented measurements."""

import altair as alt

from .storage import STALE_AFTER_SECONDS

LABELS = {
    "score": "Puntuación",
    "threshold": "Umbral",
    "air_temperature_k": "Ambiente",
    "process_temperature_k": "Proceso",
    "torque_nm": "Par",
}


def chart_data(frame, columns):
    ordered = frame.loc[:, ["timestamp", *columns]].sort_values("timestamp").copy()
    ordered["segment"] = (
        ordered.timestamp.diff().dt.total_seconds().gt(STALE_AFTER_SECONDS).cumsum()
    )
    long = ordered.melt(
        id_vars=["timestamp", "segment"],
        value_vars=columns,
        var_name="variable",
        value_name="value",
    )
    long["variable"] = long.variable.map(LABELS)
    long["utc_label"] = long.timestamp.dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    return long


def telemetry_chart(frame, columns):
    return (
        alt.Chart(chart_data(frame, columns))
        .mark_line(point=True)
        .encode(
            x=alt.X("timestamp:T", title="Hora UTC", scale=alt.Scale(type="utc")),
            y=alt.Y("value:Q", title=None, scale=alt.Scale(zero=False)),
            color=alt.Color(
                "variable:N", title=None, scale=alt.Scale(range=["#147d73", "#bc6b21"])
            ),
            detail=alt.Detail("segment:N"),
            tooltip=[
                alt.Tooltip("utc_label:N", title="Hora UTC"),
                alt.Tooltip("variable:N", title="Señal"),
                alt.Tooltip("value:Q", title="Valor", format=".3f"),
            ],
        )
        .properties(height=230)
    )
