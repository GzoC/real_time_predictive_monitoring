# Contrato HTTP y telemetría

`POST /predict` recibe seis campos obligatorios: `product_type` (L/M/H), `air_temperature_k` (270–360 K), `process_temperature_k` (270–400 K), `rotational_speed_rpm` (entero 1–5000), `torque_nm` (0–150 N·m), `tool_wear_min` (entero 0–500 min). Los rangos son límites del demostrador, no límites de seguridad de una máquina. No admite campos extra, booleanos como números, cadenas numéricas, NaN ni infinitos.

La respuesta incluye `condition` (normal/alarm), `score`, `threshold`, `model_id`, `task` y `out_of_training_range`. Este último advierte cuando una medición está dentro del contrato técnico pero fuera del rango visto al entrenar. La consulta es independiente de la telemetría y no cambia el estado del activo.

`POST /events` añade `event_id`, `asset_id`, `timestamp` con zona horaria y `source` (synthetic/external). Cada evento se confirma en SQLite junto con la inferencia y el modelo que la produjo. Repetir el mismo ID y contenido devuelve la respuesta guardada con `duplicate=true`. Reutilizar el ID con otro contenido o retroceder el timestamp de un activo devuelve 409. Un reloj con más de cinco segundos de adelanto devuelve 422.

`GET /assets` lista activos; `GET /assets/{id}/snapshot` devuelve las últimas 120 mediciones y su estado. Después de cinco segundos sin una medición vigente la condición es `unknown`; el historial no se elimina ni se sustituye por cero. Se conservan hasta 1.000 eventos por activo y 20 activos. La idempotencia solo cubre los eventos aún retenidos. La pérdida de conexión de la interfaz se muestra aparte y no produce una clasificación normal.

`GET /health` devuelve 200 cuando el modelo y el almacenamiento están disponibles; de lo contrario 503. `GET /model` devuelve el manifiesto de evaluación. Las entradas inválidas producen 422; un error de inferencia inesperado no se transforma en una respuesta 200 con un supuesto resultado.

La API no requiere autenticación en este demostrador. Los ejemplos y Compose publican puertos en loopback. La fuente synthetic/external es una declaración del emisor, no una identidad autenticada. No hay automatización de mantenimiento ni notificación externa. Para exponer la API en una red hacen falta autenticación, TLS y controles operacionales.
