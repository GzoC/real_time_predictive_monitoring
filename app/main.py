# Importación de librerías necesarias
from fastapi import FastAPI             # Framework para la API
from pydantic import BaseModel          # Validación de datos entrantes
import joblib                           # Para cargar el modelo entrenado
import pandas as pd                     # Para convertir los datos entrantes en DataFrame

# Instancia de la aplicación FastAPI
app = FastAPI(title="API Predictiva para Monitoreo en Tiempo Real",
              description="API para predicción de fallas usando modelo XGBoost")

# Carga del modelo previamente entrenado
model = joblib.load("../models/modelo_xgboost.pkl")

# Esquema de entrada de datos para validación automática (Pydantic)
class DatosEntrada(BaseModel):
    temperatura: float
    vibracion: float
    presion: float
    hora: int
    dia_semana: int

# Endpoint de prueba para verificar que la API funciona correctamente
@app.get("/")
def read_root():
    return {"mensaje": "API activa y lista para predicciones."}

# Endpoint para predicciones
@app.post("/predict")
def predict(datos: DatosEntrada):
    # Convertir los datos recibidos a formato DataFrame
    datos_df = pd.DataFrame([datos.dict()])

    # Realizar la predicción usando el modelo XGBoost
    prediccion = model.predict(datos_df)

    # Determinar resultado en formato legible
    resultado = "Falla ⚠️" if prediccion[0] == 1 else "Funcionamiento Normal ✅"

    # Devolver la respuesta en formato JSON
    return {"prediccion": int(prediccion[0]), "resultado": resultado}
