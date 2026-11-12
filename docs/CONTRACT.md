# Contrato HTTP y telemetría

`POST /predict` recibe seis campos obligatorios: `product_type` (L/M/H), `air_temperature_k` (270–360 K), `process_temperature_k` (270–400 K), `rotational_speed_rpm` (entero 1–5000), `torque_nm` (0–150 N·m), `tool_wear_min` (entero 0–500 min). Los rangos son límites del demostrador, no límites de seguridad de una máquina. No admite campos extra, booleanos como números, cadenas numéricas, NaN ni infinitos.

La respuesta incluye `condition` (normal/alarm), `score`, `threshold`, `model_id`, `task` y `out_of_training_range`. Este último advierte cuando una medición está dentro del contrato técnico pero fuera del rango visto al entrenar. La consulta es independiente de la telemetría y no cambia el estado del activo.

`POST /events` añade `event_id`, `asset_id`, `timestamp` con zona horaria y `source` (synthetic/external). Cada evento se confirma en SQLite junto con la inferencia y el modelo que la produjo. Repetir el mismo ID y contenido devuelve la respuesta guardada con `duplicate=true`. Reutilizar el ID con otro contenido o retroceder el timestamp de un activo devuelve 409. Un reloj con más de cinco segundos de adelanto devuelve 422.

`GET /assets` lista activos; `GET /assets/{id}/snapshot` devuelve las últimas 120 mediciones y su estado. Después de cinco segundos sin una medición vigente la condición es `unknown`; el historial no se elimina ni se sustituye por cero. Se conservan hasta 1.000 eventos por activo y 20 activos. La idempotencia solo cubre los eventos aún retenidos. La pérdida de conexión de la interfaz se muestra aparte y no produce una clasificación normal.

`GET /health` devuelve 200 cuando el modelo y el almacenamiento están disponibles; de lo contrario 503. `GET /model` devuelve el manifiesto de evaluación. Las entradas inválidas producen 422; un error de inferencia inesperado no se transforma en una respuesta 200 con un supuesto resultado.

La API no requiere autenticación en este demostrador. Los ejemplos y Compose publican puertos en loopback. La fuente synthetic/external es una declaración del emisor, no una identidad autenticada. Existe un adaptador de mantenimiento local simulado; no hay notificación ni envío externo. Para exponer la API en una red hacen falta autenticación, TLS y controles operacionales.


## Calidad, episodios y revisión (12 noviembre 2026)

`POST /events` acepta `quality`: `good` (predeterminado, compatible con eventos previos), `bad`, `uncertain`. Los campos físicos siguen siendo obligatorios. Con calidad no buena se conserva el evento con `condition=invalid`, `score=null`, sin llamar al modelo; no confirma ni recupera episodios. Campos fuera del contrato reciben 422 explícito y no modifican la última medición aceptada. Un rechazo de entrada no equivale a una nueva observación del activo.

La condición instantánea y el estado del episodio son distintos: puede verse `normal` mientras solo ha llegado la primera muestra de recuperación. Confirmación/recuperación requieren dos muestras consecutivas frescas (máximo 5 s de antigüedad y separación). Un hueco temporal reinicia contadores, no cierra episodios. Los borradores copian las dos mediciones de confirmación, resultado, umbral, modelo y unidades del contrato; no dependen de que el historial de mediciones se conserve.

`GET /assets/{asset_id}/drafts` incluye episodio, evidencia y cambios. `POST /drafts/{draft_id}/review` recibe `{ "status": "approved", "reviewer": "Gonzalo", "note": "Motivo de revisión", "expected_revision": 0 }`; estados permitidos: `draft`, `approved`, `rejected`. Respuestas 404 (inexistente), 409 (revisión desactualizada), 422 (entrada inválida). `external_dispatch=false` siempre. La identidad del revisor es declarada; no se acredita autenticación ni cumplimiento de auditoría regulada.

Migración aditiva: las tablas anteriores no se borran; los eventos antiguos se interpretan con calidad `good` al reintentar. No se crean borradores retrospectivos de alarmas históricas.
