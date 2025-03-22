# Dashboard interactivo con Streamlit
import streamlit as st
import requests

# Título del Dashboard
st.title("🔧 Dashboard Predictivo en Tiempo Real")
st.write("Introduce los parámetros para verificar el estado del equipo:")

# Campos de entrada para el usuario
temperatura = st.number_input("🌡️ Temperatura (°C)", value=70.0)
vibracion = st.number_input("📳 Vibración (mm/s)", value=3.0)
presion = st.number_input("📟 Presión (PSI)", value=30.0)
hora = st.slider("🕑 Hora del día", 0, 23, 12)
dia_semana = st.selectbox("📅 Día de la semana", 
                          ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
                          index=0)

# Mapeo del día de la semana a valor numérico
dias_dict = {"Lunes": 0, "Martes": 1, "Miércoles": 2, "Jueves": 3, "Viernes": 4, "Sábado": 5, "Domingo": 6}
dia_num = dias_dict[dia_semana]

# Botón para realizar la predicción
if st.button("🔍 Realizar Predicción"):

    # Enviar datos a la API para predecir
    response = requests.post("http://localhost:8000/predict", json={
        "temperatura": temperatura,
        "vibracion": vibracion,
        "presion": presion,
        "hora": hora,
        "dia_semana": dia_num
    })

    # Mostrar el resultado de la predicción
    if response.status_code == 200:
        resultado = response.json()
        st.write(f"### Resultado: {resultado['resultado']}")
    else:
        st.error("Error en la comunicación con la API.")
