# tests/test_modeling.py

"""
Pruebas unitarias para el módulo modeling.py
"""

import pytest
import pandas as pd
from xgboost import XGBClassifier
from src.modeling import train_model, evaluate_model, save_model, load_model

def test_train_model():
    """Prueba que el entrenamiento devuelve correctamente un modelo XGBClassifier."""
    X = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    y = pd.Series([0, 1])
    model = train_model(X, y)

    assert isinstance(model, XGBClassifier)

def test_evaluate_model():
    """Verifica que la evaluación del modelo devuelve métricas adecuadas."""
    X = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    y = pd.Series([0, 1])
    model = train_model(X, y)
    resultados = evaluate_model(model, X, y)

    assert "accuracy" in resultados
    assert "classification_report" in resultados
    assert "confusion_matrix" in resultados

def test_save_load_model(tmp_path):
    """Prueba guardar y cargar un modelo correctamente."""
    X = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    y = pd.Series([0, 1])
    model = train_model(X, y)

    model_path = tmp_path / "model.pkl"
    save_model(model, str(model_path))
    loaded_model = load_model(str(model_path))

    assert isinstance(loaded_model, XGBClassifier)
