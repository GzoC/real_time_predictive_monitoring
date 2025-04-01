# src/logger.py

import logging                         # Módulo estándar para manejo de logs
import os                              # Para manejo de rutas
from datetime import datetime          # Para registrar fecha y hora

# Crear carpeta de logs si no existe
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Nombre dinámico del archivo de log con fecha
log_filename = f"app_{datetime.now().strftime('%Y-%m-%d')}.log"
log_path = os.path.join(LOG_DIR, log_filename)

# Configuración básica del logger
logging.basicConfig(
    level=logging.INFO,                                # Nivel mínimo que se registrará (INFO en adelante)
    format="%(asctime)s [%(levelname)s] %(message)s",  # Formato del mensaje con fecha y nivel
    handlers=[
        logging.FileHandler(log_path),                 # Guardar log en archivo
        logging.StreamHandler()                        # Mostrar log en consola también
    ]
)

# Instancia del logger
logger = logging.getLogger(__name__)
