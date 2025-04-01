# src/config.py

# Librerías para manejo de rutas y variables de entorno
import os                                          # Manejo de rutas en el sistema
from dotenv import load_dotenv                     # Carga variables de entorno desde .env

# Cargar variables desde archivo .env automáticamente
load_dotenv()

# Ruta base absoluta del proyecto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Rutas globales a carpetas del proyecto
RAW_DATA_PATH = os.path.join(BASE_DIR, "data/raw/sensor_data.csv")
PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "data/processed/")
MODEL_PATH = os.path.join(BASE_DIR, "models/modelo_xgboost.pkl")
LOG_PATH = os.path.join(BASE_DIR, "logs/")

# Variables globales desde archivo .env
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

API_KEY = os.getenv("API_KEY")
ENVIRONMENT = os.getenv("ENV")
DEBUG = os.getenv("DEBUG") == 'True'
