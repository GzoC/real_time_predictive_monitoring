# Migración desde la versión inicial

La base anterior permanece en el [historial Git](https://github.com/GzoC/real_time_predictive_monitoring/tree/fc4f974fa6426c667d593dbc54dca60dc09b29a2). Se retiraron sus tres pickles, CSV preescalados, base del explorador Anaconda y notebooks cuyos pasos dependían de esos artefactos. No se deserializaron los modelos antiguos para esta reconstrucción.

El modelo anterior se entrenaba con un escalador que no se aplicaba en la API. La nueva versión entrena y sirve un único Pipeline. Gradient Boosting de scikit-learn reemplaza XGBoost para reducir dependencias; el resultado se compara con reglas de profundidad limitada y con una referencia trivial. No se conserva el modelo anterior como si sus métricas fueran comparables.

El CSV sin procedencia acreditada se sustituyó por AI4I 2020, con atribución y licencia propias. Por ello cambió el contrato de entrada: los campos anteriores temperatura/vibración/presión/hora/día se reemplazan por seis características documentadas en `CONTRACT.md`. No existe conversión físicamente válida entre ambos conjuntos; los clientes deben adoptar el nuevo contrato.

`condition-monitor train`, `serve`, `dashboard` y `simulate` son las entradas actuales. Un notebook ejecutable invoca el mismo entrenamiento que la CLI y comprueba equivalencia con la API. `API_URL=http://api:8000` resuelve la comunicación del dashboard dentro de Compose. El código se instala en la imagen sin depender de un montaje del checkout.

Referencias: [evitar transformaciones inconsistentes y fuga de información](https://scikit-learn.org/stable/common_pitfalls.html), [persistencia de modelos](https://scikit-learn.org/stable/model_persistence.html).
