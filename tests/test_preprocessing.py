# tests/test_preprocessing.py

"""
Pruebas unitarias para el módulo preprocessing.py
"""

import pytest
import pandas as pd
from src.preprocessing import load_data, clean_data, feature_engineering, scale_and_split

def test_load_data(tmp_path):
    """Verifica que se carguen correctamente los datos desde CSV."""
    csv_file = tmp_path / "test.csv"
    df_test = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    df_test.to_csv(csv_file, index=False)

    df_loaded = load_data(str(csv_file))

    assert not df_loaded.empty
    assert df_loaded.shape == (2, 2)

def test_clean_data():
    """Verifica eliminación correcta de filas con valores nulos."""
    df = pd.DataFrame({"A": [1, None, 2], "B": [3, 4, None]})
    df_clean = clean_data(df)

    assert df_clean.isnull().sum().sum() == 0
    assert len(df_clean) == 1

def test_feature_engineering():
    """Verifica creación de características nuevas (hora y día de la semana)."""
    df = pd.DataFrame({"timestamp": ["2025-01-01 08:00:00", "2025-01-02 14:00:00"]})
    df_feat = feature_engineering(df)

    assert "hora" in df_feat.columns
    assert "dia_semana" in df_feat.columns
    assert "timestamp" not in df_feat.columns

def test_scale_and_split():
    """Verifica que los datos se escalen y se dividan correctamente."""
    df = pd.DataFrame({"X": [1, 2, 3, 4], "falla": [0, 0, 1, 1]})
    X_train, X_test, y_train, y_test = scale_and_split(df, "falla")

    assert X_train.shape[0] == 3
    assert X_test.shape[0] == 1
    assert y_train.shape[0] == 3
    assert y_test.shape[0] == 1
