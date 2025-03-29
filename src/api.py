# src/api.py

# Importación de librerías esenciales
import pandas as pd                                  # Manejo de datos en formato DataFrame
from pydantic import BaseModel                       # Validación automática de datos recibidos en la API
from src.modeling import load_model                  # Función para cargar modelo entrenado previamente
import logging                                       # Registro de logs

# Configuración del logger
logging.basicConfig(level=logging.INFO)

# Esquema Pydantic para validación automática de entrada
class DatosEntrada(BaseModel):
    temperatura: float
    vibracion: float
    presion: float
    hora: int
    dia_semana: int

# Cargar modelo al iniciar la API
model = load_model("models/modelo_xgboost.pkl")

def predict(datos: DatosEntrada) -> dict:
    """
    Realiza una predicción de falla usando el modelo entrenado.

    Parámetros:
    datos (DatosEntrada): Datos validados para hacer predicción.

    Retorna:
    dict: Resultado de la predicción (falla o no falla).
    """
    try:
        # Convertir datos recibidos en DataFrame
        datos_df = pd.DataFrame([datos.dict()])

        # Realizar predicción usando el modelo XGBoost cargado
        prediccion = model.predict(datos_df)

        # Formatear resultado legible según predicción
        resultado = "Falla ⚠️" if prediccion[0] == 1 else "Funcionamiento Normal ✅"

        # Registrar predicción exitosa
        logging.info(f"Predicción realizada correctamente: {resultado}")

        # Devolver resultado como diccionario
        return {"prediccion": int(prediccion[0]), "resultado": resultado}

    except Exception as e:
        # Registrar cualquier error durante predicción
        logging.error(f"Error durante predicción: {str(e)}")

        # Retornar error claro al usuario
        return {"error": f"Ocurrió un error durante la predicción: {str(e)}"}
