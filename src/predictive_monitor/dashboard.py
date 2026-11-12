"""Streamlit client. API_URL resolves to the API service name inside Compose."""

import os

import pandas as pd
import requests
import streamlit as st

from predictive_monitor.charts import telemetry_chart

API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000").rstrip("/")


def fetch(path):
    response = requests.get(API_URL + path, timeout=4)
    response.raise_for_status()
    return response.json()


def render():
    st.set_page_config(page_title="Industrial Condition Monitor", page_icon="⚙", layout="wide")
    st.markdown("**OT / DATA / MACHINE LEARNING**")
    st.title("Condición del activo, con evidencia")
    st.caption("Telemetría simulada · Clasificación de la condición actual · AI4I 2020 / UCI")
    with st.sidebar:
        st.header("Estación de monitoreo")
        asset = st.text_input("Activo", "DEMO-01", max_chars=40)
        st.caption("La señal se considera vencida después de 5 segundos sin una medición nueva.")
        st.button("Recargar conexión", width="stretch")
        st.divider()
        st.markdown("**Iniciar el ciclo de demostración**")
        st.code("condition-monitor simulate --steps 80", language="bash", wrap_lines=True)
        st.caption(
            "El ciclo envía operación normal, una condición de alarma, 9 s sin señal y recuperación."
        )
    if not asset or any(
        c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in asset
    ):
        st.error("El activo debe usar letras, números, guion o guion bajo.")
        return
    live, maintenance, model_tab, manual = st.tabs(
        ["Monitoreo", "Mantenimiento local", "Evaluación del modelo", "Medición manual"]
    )

    @st.fragment(run_every="1s")
    def live_view():
        try:
            snapshot = fetch(f"/assets/{asset}/snapshot")
        except (requests.RequestException, ValueError):
            st.error("API no disponible. No se puede confirmar la condición actual del activo.")
            st.caption("Se reintentará automáticamente. Comprueba que la API esté iniciada.")
            return
        events = snapshot["events"]
        a, b, c, d = st.columns(4)
        labels = {
            "normal": "Normal",
            "alarm": "Alarma",
            "unknown": "Sin señal",
            "invalid": "Dato no confiable",
        }
        a.metric("Condición actual", labels[snapshot["condition"]])
        b.metric(
            "Antigüedad",
            "Sin datos" if snapshot["age_seconds"] is None else f"{snapshot['age_seconds']:.1f} s",
        )
        c.metric("Muestras en vista", len(events))
        d.metric("Alarmas en vista", sum(e["prediction"]["condition"] == "alarm" for e in events))
        if snapshot["stale"]:
            st.warning(
                "Señal ausente o vencida. El historial se conserva; no se infiere normalidad."
            )
        elif snapshot["condition"] == "alarm":
            st.error("El modelo detecta una condición de alarma en la última medición.")
        elif snapshot["condition"] == "invalid":
            st.error(
                "Calidad de señal inválida o incierta. Medición sin inferencia; no confirma ni recupera alarmas."
            )
        else:
            st.success("Última medición disponible: condición clasificada como normal.")
        alarm = snapshot["alarm"]
        if alarm and alarm["active_episode"]:
            st.warning(
                f"Episodio confirmado: {alarm['active_episode']} · Revisa el borrador en Mantenimiento local. Se conserva hasta dos muestras normales frescas consecutivas."
            )
        else:
            st.caption(
                "Confirmación: 2 muestras de alarma; recuperación: 2 normales. Máximo 5 s entre muestras. La pérdida de señal no cierra episodios."
            )
        if not events:
            st.info(
                "Inicia el simulador para ver cómo cambian la señal, los indicadores y las alarmas."
            )
            return
        records = [{"quality": "good", **e["observation"], **e["prediction"]} for e in events]
        frame = pd.DataFrame(records)
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
        # Do not draw untrusted physical values as process measurements.
        for column in [
            "score",
            "threshold",
            "air_temperature_k",
            "process_temperature_k",
            "torque_nm",
        ]:
            frame.loc[frame.quality != "good", column] = float("nan")
        latest = events[-1]
        if latest["prediction"]["out_of_training_range"]:
            st.warning(
                "Fuera del rango observado en entrenamiento: "
                + ", ".join(latest["prediction"]["out_of_training_range"])
            )
        st.caption(
            f"Origen: {latest['observation']['source']} · Modelo: {latest['prediction']['model_id']} · Horas UTC"
        )
        st.subheader("Puntuación y umbral de alarma")
        st.altair_chart(telemetry_chart(frame, ["score", "threshold"]), width="stretch")
        st.caption("El trazo se interrumpe cuando hay más de 5 segundos entre mediciones.")
        st.caption(
            "Puntuación del clasificador sin calibración probabilística. No expresa probabilidad de fallo futuro."
        )
        left, right = st.columns(2)
        with left:
            st.subheader("Temperaturas · K")
            st.altair_chart(
                telemetry_chart(frame, ["air_temperature_k", "process_temperature_k"]),
                width="stretch",
            )
        with right:
            st.subheader("Par · N·m")
            st.altair_chart(telemetry_chart(frame, ["torque_nm"]), width="stretch")
        st.subheader("Registro de mediciones")
        st.dataframe(
            frame[
                [
                    "timestamp",
                    "condition",
                    "score",
                    "rotational_speed_rpm",
                    "torque_nm",
                    "tool_wear_min",
                    "model_id",
                ]
            ],
            hide_index=True,
            width="stretch",
        )
        st.download_button(
            "Exportar mediciones visibles",
            frame.to_csv(index=False).encode(),
            file_name=f"{asset}.csv",
            mime="text/csv",
        )

    with live:
        live_view()
    with maintenance:
        st.subheader("Medición → alarma confirmada → borrador → revisión")
        st.info(
            "Adaptador local simulado. Aprobar registra una revisión humana declarada; no envía órdenes ni opera equipos. No hay autenticación de revisores."
        )
        try:
            drafts = fetch(f"/assets/{asset}/drafts")["drafts"]
            if not drafts:
                st.write(
                    "Sin borradores para este activo. Ejecuta el simulador y recarga esta pestaña."
                )
            for draft in drafts:
                with st.expander(
                    f"{draft['status'].upper()} · {draft['draft_id']} · revisión {draft['revision']}",
                    expanded=True,
                ):
                    st.write(
                        f"Activo: {draft['asset_id']} · Creado UTC: {draft['created_at']} · Modelo: {draft['model_id']}"
                    )
                    st.write(
                        "Episodio: "
                        + ("cerrado · " + draft["closed_at"] if draft["closed_at"] else "abierto")
                    )
                    st.write(draft["reason"])
                    evidence = draft["evidence"]
                    reading = evidence["measurement"]
                    st.dataframe(
                        pd.DataFrame(
                            [
                                {
                                    "Hora UTC": reading["timestamp"],
                                    "Calidad": reading["quality"],
                                    "Ambiente (K)": reading["air_temperature_k"],
                                    "Proceso (K)": reading["process_temperature_k"],
                                    "Velocidad (rpm)": reading["rotational_speed_rpm"],
                                    "Par (N·m)": reading["torque_nm"],
                                    "Desgaste (min)": reading["tool_wear_min"],
                                    "Puntuación": evidence["prediction"]["score"],
                                    "Umbral": evidence["prediction"]["threshold"],
                                }
                            ]
                        ),
                        hide_index=True,
                        width="stretch",
                    )
                    st.json(evidence, expanded=False)
                    st.caption(
                        "Las mediciones y la puntuación justifican revisar el activo. No demuestran una causa física ni un fallo futuro."
                    )
                    st.dataframe(
                        pd.DataFrame(draft["changes"])[
                            [
                                "timestamp",
                                "reviewer",
                                "old_status",
                                "new_status",
                                "note",
                                "revision",
                            ]
                        ],
                        hide_index=True,
                        width="stretch",
                    )
                    with st.form("review-" + draft["draft_id"]):
                        reviewer = st.text_input("Responsable de revisión")
                        status = st.selectbox("Decisión", ["approved", "rejected", "draft"])
                        note = st.text_area("Evidencia revisada y motivo")
                        submit = st.form_submit_button("Guardar revisión local")
                    if submit:
                        response = requests.post(
                            API_URL + f"/drafts/{draft['draft_id']}/review",
                            timeout=4,
                            json={
                                "status": status,
                                "reviewer": reviewer,
                                "note": note,
                                "expected_revision": draft["revision"],
                            },
                        )
                        if response.ok:
                            st.success("Revisión guardada. No se envió ninguna orden externa.")
                            st.rerun()
                        else:
                            st.error(f"No se guardó: {response.status_code} · {response.text}")
        except (requests.RequestException, ValueError):
            st.error("No fue posible cargar el registro de mantenimiento.")
    with model_tab:
        try:
            metadata = fetch("/model")
            st.subheader("Resultado en datos reservados")
            st.write(
                "Bloques 60 % entrenamiento, 20 % validación y 20 % prueba en el orden publicado. No hay fechas de adquisición ni grupos de activos verificables."
            )
            rows = []
            for name, metric in metadata["evaluation"]["test"].items():
                tn, fp = metric["confusion_matrix"][0]
                fn, tp = metric["confusion_matrix"][1]
                rows.append(
                    {
                        "Modelo": name,
                        "Detectados": tp,
                        "Omitidos": fn,
                        "Falsas alarmas": fp,
                        "Normales correctos": tn,
                        "Recall": metric["recall"],
                        "Precisión": metric["precision"],
                    }
                )
            st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
            st.caption(
                "Umbral seleccionado con F2 en validación. El conjunto de prueba no ajusta el modelo ni el umbral."
            )
            st.json(
                {
                    "dataset": metadata["dataset"],
                    "partitions": metadata["partitions"],
                    "latency": metadata["latency"],
                }
            )
        except (requests.RequestException, ValueError):
            st.info("La evaluación estará disponible cuando la API cargue el modelo entrenado.")
    with manual:
        st.subheader("Consultar una medición")
        st.caption("Esta consulta no agrega telemetría al activo ni cambia su estado.")
        with st.form("observation"):
            left_inputs, right_inputs = st.columns(2)
            with left_inputs:
                product = st.selectbox("Tipo de producto", ["L", "M", "H"])
                air = st.number_input("Temperatura ambiente · K", 270.0, 360.0, 300.0)
                process = st.number_input("Temperatura de proceso · K", 270.0, 400.0, 310.0)
            with right_inputs:
                speed = st.number_input("Velocidad · rpm", 1, 5000, 1500)
                torque = st.number_input("Par · N·m", 0.0, 150.0, 40.0)
                wear = st.number_input("Desgaste de herramienta · min", 0, 500, 50)
            submit = st.form_submit_button("Clasificar medición")
        if submit:
            try:
                response = requests.post(
                    API_URL + "/predict",
                    timeout=4,
                    json={
                        "product_type": product,
                        "air_temperature_k": air,
                        "process_temperature_k": process,
                        "rotational_speed_rpm": speed,
                        "torque_nm": torque,
                        "tool_wear_min": wear,
                    },
                )
                response.raise_for_status()
                st.json(response.json())
            except (requests.RequestException, ValueError):
                st.error("La consulta falló. No se obtuvo una clasificación válida.")


if __name__ == "__main__":
    render()
