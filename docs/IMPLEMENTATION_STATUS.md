# Entrega de mantenimiento local · 12 noviembre 2026

Base `9fc2fb1`, rama `codex/traceable-maintenance-demo`. Se conservaron modelo, entrenamiento, evaluación, datos, interfaces existentes e historial.

Se añadieron calidad explícita, episodios persistentes, confirmación/recuperación, borradores únicos y revisión con historial y control de concurrencia. README inglés/español enlazados. Matriz por requisito en [MAINTENANCE.md](MAINTENANCE.md).

Comprobaciones de esta sesión: baseline 27 pruebas; ampliación 31 pruebas; Ruff; entrenamiento real con métricas sin cambios; replay de mantenimiento; wheel/sdist; Chromium real en alarma, revisión, ausencia y recuperación. No se atribuye una ejecución local de contenedores ni del notebook en esta ampliación hasta que conste en evidencia adicional. Los workflows conservan esas comprobaciones y añaden el replay.

## Registro histórico preservado

# Estado de implementación

Actualizado el 28 de octubre de 2026. La reconstrucción base fue integrada mediante [PR #8](https://github.com/GzoC/real_time_predictive_monitoring/pull/8), merge `b77db10b22d808a719e4fecf7538cdcf1c17738b`. Se conserva el historial original.

Esta continuación, `codex/predictive-monitoring-validation`, añade cortes de gráficos ante ausencia de señal, etiquetas UTC consistentes, adaptación de la interfaz y evidencia real de navegador. Su integración se entrega en un PR separado; no se afirma que ya esté en main.

Implementado y verificado: dataset trazable, pipeline único, evaluación reservada frente a baselines, contrato físico, almacenamiento idempotente, simulador HTTP, dashboard, notebook reproducible, paquetes, lock, Docker y CI. Se completó la revisión visual en Edge de escritorio y viewport móvil: flujo normal/alarma/ausencia/recuperación, selección de activo, formulario, CSV, caída y reinicio de API. Hay capturas y video reales del demostrador.

Validación local de esta continuación: 25 pruebas aprobadas, Ruff y construcción de wheel/sdist. La cobertura automatizada global es 60 %; la revisión manual de navegador no forma parte de esa cifra. El notebook, instalación fuera del checkout y contenedores se ejecutaron en la CI de la base integrada y se vuelven a comprobar por el workflow de cada PR. Consultar el estado exacto del commit en GitHub antes de integrar.

Resultados, evidencia y limitaciones: [VALIDATION.md](VALIDATION.md). No se atribuye validación en planta, predicción de fallos futuros ni aprobación operacional. Los siguientes trabajos del portafolio se registran por separado.
