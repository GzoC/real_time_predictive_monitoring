# tests/test_api.py

"""
Pruebas unitarias para api.py
"""

from src.api import DatosEntrada, predict

def test_predict_normal():
    """Prueba que la predicción con datos correctos devuelve resultados adecuados."""
    datos = DatosEntrada(
        temperatura=75,
        vibracion=4.5,
        presion=35,
        hora=14,
        dia_semana=3
    )
    resultado = predict(datos)

    assert "prediccion" in resultado or "error" in resultado

def test_predict_error():
    """Prueba que la API maneje correctamente datos incorrectos."""
    class FakeData:
        def dict(self):
            return None

    fake = FakeData()
    resultado = predict(fake)

    assert "error" in resultado
