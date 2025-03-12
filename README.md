# 🚨 Sistema Automatizado de Monitoreo Predictivo con Machine Learning en Tiempo Real

## 📋 Descripción del Proyecto
Este proyecto tiene como objetivo el desarrollo de un sistema predictivo capaz de identificar posibles fallos en equipos industriales en tiempo real, utilizando técnicas avanzadas de **Machine Learning** e integrando herramientas modernas como **FastAPI**, **Streamlit** y **Docker**.

El proyecto se enfoca en la predicción de fallos mediante el análisis de variables industriales clave como vibración, temperatura y presión.

> **Nota:** Este proyecto forma parte del portafolio de [Gonzalo Cisterna Salinas](https://github.com/GzoC) como parte de su formación en **Data Analytics**.

---

## 🎯 Características Principales
✅ Monitoreo predictivo en tiempo real.  
✅ API desarrollada en **FastAPI** para el consumo de predicciones.  
✅ Dashboard interactivo usando **Streamlit** para visualizar datos y alertas.  
✅ Entrenamiento de modelos avanzados como **Random Forest**, **XGBoost** y **LSTM**.  
✅ Integración con **Docker** para un despliegue seguro y eficiente.  
✅ Estructura modular para facilitar el mantenimiento y escalabilidad.  

---

## ⚙️ Tecnologías Utilizadas
- **Python 3.9**
- **Pandas**, **NumPy** (Manejo y análisis de datos)
- **Scikit-learn**, **XGBoost**, **LSTM** (Modelos de Machine Learning)
- **FastAPI** (API en tiempo real)
- **SQLite** o **PostgreSQL** (Almacenamiento de datos)
- **Streamlit** o **Plotly Dash** (Dashboard interactivo)
- **Docker** y **Docker Compose** (Despliegue y administración de contenedores)
- **pytest** (Pruebas unitarias para asegurar la calidad del código)

---

## 📂 Estructura del Proyecto
```
real_time_predictive_monitoring/
│
├── data/
│   ├── raw/                 # Datos originales capturados desde sensores
│   ├── processed/           # Datos ya procesados y listos para entrenamiento
│   └── database/            # Base de datos para almacenamiento y consulta
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
│   └── app.py
│
├── models/
├── reports/
│   ├── figures/
│   └── metrics/
├── tests/
│
├── requirements.txt
├── .env
├── .gitignore
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🖥️ Instalación y Configuración
### 1️⃣ **Clonar el Repositorio**
```bash
git clone https://github.com/GzoC/real_time_predictive_monitoring_01.git
cd real_time_predictive_monitoring_01
```

### 2️⃣ **Crear y Activar el Entorno Virtual**
```bash
conda create -n monitoreo_predictivo python=3.9 -y
conda activate monitoreo_predictivo
```

### 3️⃣ **Instalar las Dependencias**
```bash
pip install -r requirements.txt
```

### 4️⃣ **Configurar el Archivo `.env`**
1. Crea un archivo `.env` en la raíz del proyecto.
2. Agrega las siguientes variables de entorno:
```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=admin
DB_PASSWORD=tu_contraseña_segura
DB_NAME=mi_base_de_datos
API_KEY=tu_api_key_aqui
ENV=development
DEBUG=True
```

### 5️⃣ **Ejecutar la Aplicación**
Para levantar la API localmente:
```bash
uvicorn app.app:app --reload
```

Para visualizar el dashboard interactivo:
```bash
streamlit run src/dashboard.py
```

### 6️⃣ **Despliegue con Docker (Recomendado para Producción)**
```bash
docker-compose up
```

---

## 🚀 Uso de la API
La API proporciona los siguientes endpoints clave:

| **Método** | **Ruta**            | **Descripción**                      |
|--------------|----------------------|----------------------------------------|
| `POST`        | `/predict`            | Recibe datos y devuelve una predicción |
| `GET`         | `/status`             | Verifica el estado del sistema         |

Ejemplo de request para el endpoint `/predict`:
```json
{
  "vibration": 2.5,
  "temperature": 75.0,
  "pressure": 1.2
}
```

---

## 🔧 Pruebas
Para ejecutar las pruebas unitarias, utiliza el siguiente comando:
```bash
pytest tests/
```

---

## 🧑‍💻 Autor
👨‍💻 **Gonzalo Cisterna Salinas**  
📧 [cisternasalinasg@gmail.com](mailto:cisternasalinasg@gmail.com)  
🌐 [GitHub - GzoC](https://github.com/GzoC)

---

## 📜 Licencia
Este proyecto está bajo la licencia **MIT**, lo que permite su libre uso, modificación y distribución. Consulta el archivo `LICENSE` para más detalles.

