# src/api.py

import pandas as pd
from pydantic import BaseModel
from src.modeling import load_model
import os

# Ruta absoluta al modelo entrenado
model_path = os.path.join(os.path.dirname(__file__), "..", "models", "modelo_xgboost.pkl")
model = load_model(model_path)  # Carga el modelo usando función del módulo modeling

# Definición del esquema de datos que la API recibirá
class DatosEntrada(BaseModel):
    temperatura: float
    vibracion: float
    presion: float
    hora: int
    dia_semana: int

# Lógica de predicción reutilizable
def predict(datos: DatosEntrada) -> dict:
    try:
        # Convertir entrada a DataFrame
        datos_df = pd.DataFrame([datos.dict()])

        # Realizar predicción
        prediccion = model.predict(datos_df)

        # Interpretar resultado
        resultado = "Falla ⚠️" if prediccion[0] == 1 else "Funcionamiento Normal ✅"

        return {"prediccion": int(prediccion[0]), "resultado": resultado}

    except Exception as e:
        return {"error": f"Ocurrió un error durante la predicción: {str(e)}"}
