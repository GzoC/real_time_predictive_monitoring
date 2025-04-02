Real-Time Predictive Monitoring

Este repositorio contiene un proyecto de monitoreo predictivo en tiempo real basado en Machine Learning. Incluye:
- Pipelines de preprocesamiento de datos.
- Modelo XGBoost entrenado para detectar fallas.
- Despliegue de una API con FastAPI.
- Dashboard interactivo con Streamlit.
- Contenedorización con Docker.
- Pruebas automatizadas y estructura modular profesional.

1. Descripción General

Este proyecto tiene como objetivo identificar fallas en equipos industriales a partir de sensores que registran variables como temperatura, vibración y presión. El corazón de la solución es un **modelo de Machine Learning** (XGBoost) capaz de predecir en tiempo real la probabilidad de fallo.

Se incluye una **API** con FastAPI para exponer el servicio de predicción y un **dashboard con Streamlit** para la visualización de resultados de manera amigable. Todo puede desplegarse fácilmente usando **Docker**.

---

2. Estructura de Directorios

```bash
real_time_predictive_monitoring/
│
├── data/
│   ├── raw/              # Datos originales
│   ├── processed/        # Datos procesados
│   └── database/         # (Opcional) Archivos de base de datos
│
├── notebooks/
│   ├── 01_exploratory_data_analysis.ipynb
│   ├── 02_data_preprocessing.ipynb
│   ├── 03_model_training_evaluation.ipynb
│   ├── 04_model_deployment.ipynb
│   └── 05_api_testing.ipynb
│
├── src/
│   ├── preprocessing.py
│   ├── modeling.py
│   ├── api.py
│   ├── dashboard.py
│   ├── config.py
│   ├── logger.py
│   └── utils.py
│
├── app/
│   └── main.py           # Archivo principal de la API FastAPI
│
├── models/               # Modelos guardados (XGBoost)
├── reports/              # Informes, gráficas y métricas
│   ├── figures/
│   └── metrics/
├── tests/                # Pruebas automatizadas
│   ├── test_preprocessing.py
│   ├── test_modeling.py
│   ├── test_api.py
│   ├── test_config.py
│   ├── test_logger.py
│   └── test_utils.py
├── logs/                 # Archivos de logs
├── requirements.txt
├── .env
├── .gitignore
├── Dockerfile
├── docker-compose.yml
└── README.md             # <-- Este documento

Descripción de los Módulos en src/
preprocessing.py: Funciones de carga, limpieza y preprocesamiento de datos.

modeling.py: Entrenamiento, evaluación y guardado/carga del modelo XGBoost.

api.py: Lógica de predicción (carga de modelo, validación de datos) integrada con FastAPI.

dashboard.py: Interfaz de usuario con Streamlit para probar predicciones en tiempo real.

config.py: Variables de configuración global (rutas, credenciales) cargadas desde .env.

logger.py: Manejo de registros (logs) para seguimiento de eventos y errores.

utils.py: Funciones auxiliares de validación, timestamps y divisores visuales.

3. Configuración e Instalación
3.1. Prerrequisitos
Python 3.9 (o superior).

Docker Desktop (opcional, pero recomendado).

Git para clonar el repositorio.

pip actualizado.

3.2. Instalación de dependencias
Clonar el repositorio:

git clone https://github.com/GzoC/real_time_predictive_monitoring.git

Entrar al directorio y crear un entorno virtual:
cd real_time_predictive_monitoring
python -m venv venv

Activar el entorno virtual:
En Windows:
venv\Scripts\activate

En Linux/Mac:
source venv/bin/activate

Instalar las dependencias:
pip install --upgrade pip
pip install -r requirements.txt

Nota: En caso de usar Docker, no es obligatorio crear un entorno virtual local. Sin embargo, te servirá para ejecutar y probar en modo desarrollo.

4. Uso de la Aplicación
4.1. Ejecución Local
API:

Para lanzar la API en local, edita app/main.py si deseas cambiar algún puerto.

Ejecuta:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Accede a http://localhost:8000 para ver la respuesta inicial.
Documentación interactiva disponible en http://localhost:8000/docs.

Dashboard (Streamlit):

Ejecuta desde la raíz del proyecto (o dentro de src/):
streamlit run src/dashboard.py
Accede a http://localhost:8501.

4.2. Ejecución con Docker Compose

Construir y lanzar contenedores:
docker-compose up --build

Verifica:

La API en http://localhost:8000.
El Dashboard en http://localhost:8501.

5. Notebooks de Desarrollo
01_exploratory_data_analysis.ipynb: Análisis inicial de datos (EDA).

02_data_preprocessing.ipynb: Preprocesamiento y limpieza.

03_model_training_evaluation.ipynb: Entrenamiento y evaluación del modelo.

04_model_deployment.ipynb: Despliegue con FastAPI y Streamlit.

05_api_testing.ipynb: Pruebas de la API y métricas de rendimiento.

**Todos los notebooks se refactorizaron para usar módulos en la carpeta src/, facilitando la mantenibilidad y buenas prácticas.

6. Pruebas Automatizadas
En la carpeta tests/ se incluyen scripts de prueba unitarias e integradas para cada módulo (preprocessing, modeling, api, config, logger, utils). Se pueden ejecutar con:

pytest tests/

Algunas pruebas requieren la API en ejecución, otras se basan en el modelo entrenado. Asegúrate de haber entrenado o cargado el modelo XGBoost antes de iniciar las pruebas.

7. Buenas Prácticas y Consejos
Control de versiones: Mantén ramas separadas para nuevas funcionalidades y mergea a main tras aprobar y testear.

Documentación: Actualiza este README y docstrings en cada script (src/) con información clara.

Entorno Docker: Facilita la replicación exacta de la aplicación en cualquier sistema operativo.

8. Licencia
Este proyecto se distribuye bajo la licencia MIT, lo que te permite usar, modificar y distribuir libremente el código siempre y cuando incluyas la nota de licencia correspondiente.

9. Autor
Gonzalo A. Cisterna Salinas/cisternasalinasg@gmail.com

¡Gracias por interesarte en este proyecto!

