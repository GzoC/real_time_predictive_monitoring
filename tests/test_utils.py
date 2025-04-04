# tests/test_utils.py

"""
Pruebas unitarias para utils.py
"""

import pytest
import pandas as pd
from src.utils import validar_dataframe, generar_timestamp, mostrar_divisor

def test_validar_dataframe():
    """Verifica validación correcta de dataframe."""
    df = pd.DataFrame({"A": [1, 2]})
    assert validar_dataframe(df) is True

def test_validar_dataframe_empty():
    """Verifica que un DataFrame vacío lance excepción."""
    df_empty = pd.DataFrame()
    with pytest.raises(ValueError):
        validar_dataframe(df_empty)

def test_generar_timestamp():
    """Verifica generación correcta de timestamp."""
    ts = generar_timestamp()
    assert len(ts) > 0

def test_mostrar_divisor(capfd):
    """Verifica que el divisor se imprima correctamente."""
    mostrar_divisor("Test")
    out, err = capfd.readouterr()
    assert "Test" in out
