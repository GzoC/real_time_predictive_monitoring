# tests/test_logger.py

"""
Pruebas unitarias para logger.py
"""

import logging
from src.logger import logger

def test_logger():
    """Verifica que el logger esté configurado correctamente."""
    logger.info("Probando logger.")

    assert isinstance(logger, logging.Logger)
