# Validación y evidencia

Revisión local: 28 de octubre de 2026, Windows 10, Python 3.12.13, scikit-learn 1.9.1, Streamlit 1.66.1 y Altair 6.3.0. Modelo de la demo: `59d8b050c20f0514`. La telemetría es sintética y viaja realmente por HTTP hacia la API y SQLite.

## Comprobaciones automáticas

Se ejecutaron **25 pruebas** con pytest: equivalencia de entrada física directa/API y recarga del pipeline, escalado ajustado solo sobre entrenamiento, exclusión de etiquetas, validación de unidades/rangos/tipos, artefacto ausente o corrupto, conflictos e idempotencia, persistencia, timestamps, pérdida/recuperación de señal y segmentación de gráficos sin fabricar mediciones. La suite pasó en 19,34 s; cobertura global 60 % (API 88 %, almacenamiento 98 %, entrenamiento 94 %, gráficos 100 %). CLI e interfaz se comprueban además por integración y navegador, no por cobertura pytest.

Ruff (`check` y `format --check`) y construcción de wheel/sdist aprobados. El primer intento de pytest dentro del entorno restringido no accedió a su carpeta temporal; la repetición con acceso autorizado completó las 25 pruebas. Advertencia no bloqueante conocida: Starlette depreca su integración actual con httpx en TestClient.

La [CI del main integrado b77db10](https://github.com/GzoC/real_time_predictive_monitoring/actions/runs/40600566675) aprobó Python 3.11/3.13 y contenedores. Incluye notebook completo, entrenamiento, instalación del wheel fuera del código fuente y Docker Compose real con API, dashboard y simulador. El [workflow](../.github/workflows/ci.yml) repite esos controles para esta continuación; el estado de su commit se consulta en el PR. Docker no se ejecutó en el equipo Windows de esta revisión. La comprobación de contenedores cubre salud e ingestión, no inspección visual de la interfaz dentro del contenedor.

## Navegador real

Edge de escritorio, viewport 1527 × 746; comprobación móvil mediante viewport 390 × 844, no dispositivo físico. Se comprobó:

| Caso | Resultado observado |
|---|---|
| Activo sin datos | Estado sin señal, sin inferir normalidad |
| Flujo normal | Contadores y antigüedad se actualizan con mediciones recibidas |
| Ciclo `DEMO-02`, 40 pasos | 31 eventos, 10 alarmas; los nueve pasos sin señal no crean filas |
| Ausencia de señal | Estado desconocido al vencer 5 s, historial conservado |
| Recuperación del ciclo | Estado normal con datos nuevos; hueco visible en puntuación y umbral |
| Activos independientes | `DEMO-01`: 30 registros, 0 alarmas; `DEMO-02`: 31 registros, 10 alarmas |
| CSV descargado por el botón | 31 filas; activo, hora UTC, puntuación, modelo y entradas físicas presentes |
| Consulta manual | Caso normal: puntuación 0,001292; caso de alarma: 0,999370; umbral 0,45 |
| Evaluación del modelo | Tabla visible coincide con el informe: TP28/FN11/FP2/TN1959 |
| Identificador inválido `BAD/ASSET` | Error claro antes de solicitar datos del activo |
| API detenida | Mensaje explícito de indisponibilidad y reintento automático |
| API reiniciada con la misma SQLite | Recupera los 31 registros; nuevas mediciones elevan el contador, sin perder las 10 alarmas |
| Móvil | Indicadores y formulario apilados; ancho de documento 390 px, sin desbordamiento horizontal global |
| Consola Edge | Sin errores ni advertencias capturados durante la sesión final de revisión |

La captura de recuperación tras reinicio muestra 55 registros mientras seguía el envío. El CSV y video se tomaron antes de esa segunda simulación. Se preserva esa distinción para no presentar contadores de distintas ejecuciones como si fueran una sola.

## Evidencia descargable

- [Video del ciclo](evidence/walkthrough.mp4): 36 capturas reales, intervalo observado de 48,216 s más un segundo final. La codificación repite capturas a 25 fps y conserva sus intervalos de reloj; no es una grabación de 25 capturas nuevas por segundo. Sin interfaz generada ni valores añadidos.
- [Manifiesto de capturas, tiempos y SHA256](evidence/capture-manifest.json).
- [Normal](evidence/normal.png), [alarma](evidence/alarm.png), [señal ausente](evidence/signal-loss.png), [recuperación](evidence/recovery.png).
- [Evaluación](evidence/evaluation.png), [móvil](evidence/mobile.png), [formulario móvil](evidence/mobile-manual.png).
- [API no disponible](evidence/api-unavailable-mobile.png), [API recuperada](evidence/api-recovered.png), [CSV exportado](evidence/DEMO-02.csv).

El video se decodificó completo con FFmpeg sin errores. Las imágenes son capturas de viewport; no se presentan como páginas completas. La captura del navegador integrado no estuvo disponible y se utilizó Edge para obtener la evidencia.

## Límites

No se midieron carga concurrente, SLA, latencia de red ni un circuito de control industrial. La latencia del manifiesto cubre solo `pipeline.predict_proba`. La revisión visual es manual y no reemplaza una auditoría completa de accesibilidad. La puntuación no está calibrada y el modelo omite 11 de 39 fallos del holdout; datos sintéticos y resultado reservado no equivalen a validación de planta. Ver [MODEL_CARD.md](MODEL_CARD.md).
