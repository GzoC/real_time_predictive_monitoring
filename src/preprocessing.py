# src/preprocessing.py

# Importación de librerías necesarias
import pandas as pd                                     # Manejo eficiente de datos
from sklearn.model_selection import train_test_split    # División de datos
from sklearn.preprocessing import StandardScaler        # Escalado de variables numéricas

def load_data(data_path: str) -> pd.DataFrame:
    """
    Carga datos desde un archivo CSV.

    Parámetros:
    data_path (str): ruta completa al archivo CSV.

    Retorna:
    pd.DataFrame: DataFrame con los datos cargados.
    """
    df = pd.read_csv(data_path)
    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia el dataset eliminando filas con datos faltantes (si los hubiera).

    Parámetros:
    df (pd.DataFrame): DataFrame original.

    Retorna:
    pd.DataFrame: DataFrame limpio.
    """
    if df.isnull().sum().sum() > 0:
        df = df.dropna().reset_index(drop=True)
    return df

def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """
    Realiza ingeniería de características generando variables nuevas.

    Parámetros:
    df (pd.DataFrame): DataFrame limpio.

    Retorna:
    pd.DataFrame: DataFrame con nuevas características.
    """
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hora'] = df['timestamp'].dt.hour
    df['dia_semana'] = df['timestamp'].dt.dayofweek
    df = df.drop(columns=['timestamp'])
    return df

def scale_and_split(df: pd.DataFrame, target: str):
    """
    Escala variables numéricas y divide el dataset en conjuntos de entrenamiento y prueba.

    Parámetros:
    df (pd.DataFrame): DataFrame tras feature engineering.
    target (str): Nombre de la columna objetivo (ej. 'falla').

    Retorna:
    X_train_scaled, X_test_scaled, y_train, y_test: conjuntos procesados listos para entrenar.
    """
    y = df[target]
    X = df.drop(columns=[target])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)
    X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns)

    return X_train_scaled, X_test_scaled, y_train, y_test
