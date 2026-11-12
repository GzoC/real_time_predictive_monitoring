# Demo actual: 2–3 minutos

1. **0:00–0:30:** con modelo entrenado, API y dashboard iniciados según README, ejecuta `uv run --no-sync condition-monitor simulate --steps 80`. Explica que son datos sintéticos y clasificación presente.
2. **0:30–1:00:** observa normal → alarma; el episodio requiere dos muestras y genera un borrador. En Mantenimiento local revisa activo, dos mediciones, unidades, puntuación y modelo.
3. **1:00–1:40:** durante los nueve segundos sin señal, Monitoreo muestra desconocido; el episodio persiste. Dos normales cierran el episodio. La revisión permanece independiente.
4. **1:40–2:20:** registra responsable, decisión y motivo. Recarga y muestra historial. Explica unicidad por evento/episodio y conflicto de revisión 409; no sale ninguna orden del equipo.
5. **2:20–2:50:** abre Evaluación: detectados, omitidos y falsas alarmas frente a reglas. Concluye indicando límites del dataset, retención y ausencia de horizonte futuro.

Prueba rápida sin servicios: `uv run --no-sync python scripts/maintenance_demo.py`. Capturas nuevas: maintenance-alarm, maintenance-gap, maintenance-recovery y maintenance-review en docs/evidence. Capturadas en Chromium; el manifiesto contiene versión y observaciones.

---

## Registro del guion anterior

# Demostración de dos minutos

## Preparación

Sigue el arranque local o Compose del [README](../README.md). La demo usa AI4I 2020 y telemetría sintética; no conecta un PLC ni acciona una máquina. Para ver solo un ciclo local:

```bash
uv run --no-sync condition-monitor simulate --steps 40 --asset DEMO-01
```

El dashboard debe seleccionar el mismo activo. Los timestamps se crean al enviar cada muestra; la duración total también incluye peticiones HTTP. En la grabación se usó `DEMO-02` para mantener independiente una prueba normal anterior.

## Recorrido

1. **0–20 s:** muestra el estado, la antigüedad y el identificador del modelo. Explica que la misma entrada física pasa por las transformaciones persistidas del entrenamiento.
2. **20–50 s:** observa la alarma, la ausencia de señal y la recuperación. La falta de datos produce desconocido y separa los trazos; no añade ceros ni declara normalidad.
3. **50–80 s:** abre Evaluación del modelo. Compara 28 fallos detectados y 2 falsas alarmas con las reglas: 29 detectados y 91 falsas alarmas. Explica los 11 fallos omitidos y el tamaño reducido del holdout positivo.
4. **80–110 s:** consulta una medición manual o exporta el CSV. La consulta manual no escribe telemetría. Cada fila exportada conserva procedencia, unidades y versión.
5. **110–120 s:** explica el siguiente paso hacia una aplicación real: datos y etiquetas del proceso, validación por activo/tiempo y controles de acceso. No atribuyas anticipación a un modelo de condición actual.

## Decisiones que puedes defender en una entrevista

- **Un único pipeline:** evita que entrenamiento e inferencia usen escalas distintas y permite probar igualdad directa/API.
- **Separación antes de transformar:** el escalador y modelo se ajustan con entrenamiento; el umbral se elige con validación. Los tipos de fallo se excluyen de las entradas.
- **SQLite e idempotencia:** una medición confirmada conserva el resultado del modelo y los reenvíos no duplican eventos retenidos. La retención limita almacenamiento y también el alcance de la idempotencia.
- **Calidad de señal visible:** cinco segundos sin datos cambian el estado a desconocido; una caída de API se comunica por separado.
- **Evaluación honesta:** se comparan errores relevantes frente a reglas y una base trivial. El orden UDI no se presenta como cronología de una planta.

Para reproducir la recuperación de conexión, detén únicamente la API de la demo, observa el aviso y vuelve a iniciarla con el mismo `TELEMETRY_DB`. El dashboard reintenta sin recargar la página; nuevos eventos vuelven a establecer una condición vigente.
