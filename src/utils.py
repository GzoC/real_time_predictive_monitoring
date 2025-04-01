# src/utils.py

import pandas as pd                                      # Para validaciones de DataFrames
from datetime import datetime                            # Para generar timestamps
from src.logger import logger                            # Para registrar eventos

def validar_dataframe(df: pd.DataFrame, nombre: str = "Dataset") -> bool:
    """
    Verifica que un DataFrame no esté vacío y no contenga valores nulos.

    Parámetros:
    df (DataFrame): El DataFrame a validar.
    nombre (str): Nombre del DataFrame (opcional, para logs).

    Retorna:
    bool: True si el DataFrame es válido; lanza excepción si no lo es.
    """
    if df.empty:
        logger.error(f"{nombre} está vacío.")
        raise ValueError(f"{nombre} está vacío.")

    if df.isnull().sum().sum() > 0:
        logger.warning(f"{nombre} contiene valores nulos.")
        raise ValueError(f"{nombre} contiene valores nulos.")

    logger.info(f"{nombre} validado correctamente.")
    return True

def generar_timestamp() -> str:
    """
    Genera un timestamp con formato estándar.

    Retorna:
    str: Timestamp en formato YYYY-MM-DD_HH-MM-SS
    """
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def mostrar_divisor(texto: str = ""):
    """
    Muestra un divisor visual útil en notebooks o consola.

    Parámetros:
    texto (str): Texto a mostrar junto al divisor.
    """
    linea = "=" * 60
    if texto:
        print(f"\n{linea}\n🔹 {texto}\n{linea}")
    else:
        print(f"\n{linea}")
