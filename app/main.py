# app/main.py

from fastapi import FastAPI
from src.api import DatosEntrada, predict

app = FastAPI(
    title="API Predictiva para Monitoreo en Tiempo Real",
    description="API para predicción de fallas usando modelo XGBoost",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"mensaje": "API activa y lista para predicciones."}

@app.post("/predict")
def realizar_prediccion(datos: DatosEntrada):
    return predict(datos)
