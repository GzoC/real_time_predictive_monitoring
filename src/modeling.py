# src/modeling.py

# Importación de librerías esenciales
from xgboost import XGBClassifier                           # Modelo XGBoost para clasificación
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score # Métricas de evaluación
import joblib                                               # Serialización del modelo
import pandas as pd                                         # Manejo de datos
import matplotlib.pyplot as plt                             # Gráficos básicos
import seaborn as sns                                       # Gráficos estadísticos avanzados
import os                                                   # Manejo de archivos y rutas

def train_model(X_train: pd.DataFrame, y_train: pd.Series) -> XGBClassifier:
    """
    Entrena un modelo XGBoost para clasificación binaria.

    Parámetros:
    X_train (DataFrame): Variables predictoras escaladas para entrenar.
    y_train (Series): Variable objetivo para entrenar.

    Retorna:
    XGBClassifier: Modelo entrenado.
    """
    model = XGBClassifier(
        objective='binary:logistic',
        eval_metric='logloss', 
        use_label_encoder=False, 
        random_state=42 
    )
    model.fit(X_train, y_train)
    return model

def evaluate_model(model: XGBClassifier, X_test: pd.DataFrame, y_test: pd.Series):
    """
    Evalúa el desempeño del modelo en un conjunto de prueba.

    Parámetros:
    model (XGBClassifier): Modelo entrenado.
    X_test (DataFrame): Variables predictoras del conjunto de prueba.
    y_test (Series): Variable objetivo del conjunto de prueba.

    Retorna:
    dict: Diccionario con métricas de desempeño (accuracy, matriz de confusión, reporte clasificación).
    """
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    conf_matrix = confusion_matrix(y_test, y_pred)
    class_report = classification_report(y_test, y_pred)

    resultados = {
        'accuracy': accuracy, 
        'confusion_matrix': conf_matrix, 
        'classification_report': class_report 
    }

    return resultados

def plot_confusion_matrix(conf_matrix):
    """
    Grafica la matriz de confusión.

    Parámetros:
    conf_matrix (array): Matriz de confusión generada por el modelo.
    """
    plt.figure(figsize=(6,4))
    sns.heatmap(conf_matrix, annot=True, cmap='Blues', fmt='g')
    plt.xlabel('Predicción')
    plt.ylabel('Valor Real')
    plt.title('Matriz de Confusión')
    plt.show()

def plot_feature_importances(model: XGBClassifier, feature_names: list):
    """
    Visualiza gráficamente la importancia de las características según el modelo.

    Parámetros:
    model (XGBClassifier): Modelo entrenado.
    feature_names (list): Nombres de las variables predictoras.
    """
    plt.figure(figsize=(10,6))
    importancias = pd.Series(model.feature_importances_, index=feature_names)
    importancias.sort_values(ascending=True).plot(kind='barh', color='green')
    plt.xlabel('Importancia')
    plt.ylabel('Variables')
    plt.title('Importancia de las Variables según XGBoost')
    plt.show()

def save_model(model: XGBClassifier, model_path: str):
    """
    Guarda el modelo entrenado en un archivo (.pkl).

    Parámetros:
    model (XGBClassifier): Modelo entrenado.
    model_path (str): Ruta completa donde guardar el modelo.
    """
    directorio = os.path.dirname(model_path)
    os.makedirs(directorio, exist_ok=True)   # Crear directorio si no existe
    joblib.dump(model, model_path)

def load_model(model_path: str) -> XGBClassifier:
    """
    Carga un modelo entrenado desde un archivo (.pkl).

    Parámetros:
    model_path (str): Ruta del archivo del modelo guardado.

    Retorna:
    XGBClassifier: Modelo cargado.
    """
    model = joblib.load(model_path)
    return model
