# Decisiones de mantenimiento y defensa técnica

El objetivo es demostrar integración transaccional y criterio operacional: una clasificación presente pasa a un borrador revisable, sin atribuir predicción futura. El estado seguro informativo ante pérdida de señal es desconocido. No existe salida de control.

**Hechos:** AI4I es sintético; el pipeline y los cortes anteriores se conservaron. **Supuestos de demo:** 5 s de vigencia y dos muestras de confirmación/recuperación. Estos parámetros no provienen de un análisis de riesgo de maquinaria y no son límites de seguridad.

La deduplicación por evento resuelve reintentos de entrega. La unicidad por episodio resuelve múltiples mediciones de la misma condición. Son problemas distintos. La transacción SQLite contiene medición, actualización del contador y creación del borrador: un fallo antes del commit revierte todo; un fallo después se resuelve reenviando el mismo ID. Los datos deben permanecer en disco; no se promete tolerancia a pérdida del volumen ni funcionamiento distribuido.

La alarma activa persiste durante cortes. Cerrar automáticamente durante un corte convertiría falta de información en recuperación. Después de dos normales frescos se cierra, conservando borrador e historial; una nueva alarma puede crear otro borrador. Aprobar/rechazar el borrador no cambia la condición ni cierra el episodio.

La evidencia muestra mediciones, unidades, umbral y modelo. No se presenta una importancia global de características como explicación causal. Tampoco se considera la puntuación como probabilidad calibrada de falla futura. Las muestras fuera del rango de entrenamiento se identifican en el resultado; requieren revisión del dominio.

La revisión usa una revisión numérica esperada para detectar modificaciones concurrentes. Se conserva el antes/después y el motivo. Es una simulación local: el nombre del revisor no está autenticado y la base es editable por su propietario. Para integrar un CMMS real se necesitarían identidad, autorización, mapeo de activos, políticas de envío, retención, respaldos y validación operacional fuera de este alcance.

## Requisitos y evidencia

| Requisito | Estado | Evidencia |
|---|---|---|
| 1 pipeline y test separado | Existente, vuelto a comprobar | test_condition_monitor; train |
| 2 entradas, unidades, activo, tiempo, calidad | Ampliado y comprobado | schema; tests API/quality |
| 3 episodios con confirmación/recuperación | Implementado y comprobado | test_maintenance |
| 4 adaptador local, evidencia y modelo | Implementado y comprobado | storage; maintenance-replay.json |
| 5 revisión e historial | Implementado y comprobado | tests optimistic lock; captura maintenance-review |
| 6 idempotencia y reinicio | Implementado y comprobado | 10 reenvíos, Store reabierto, segundo episodio |
| 7 recorrido visible | Implementado y observado | cuatro capturas maintenance-* y manifest browser |
| 8 explicación verificable | Implementado | dos mediciones, puntuación y umbral; sin causalidad |

Base: `9fc2fb1bbb7777015b1706d39026e47fbebe7cbd`. Diagnóstico inicial: 27 pruebas aprobadas. Ampliación: 31 aprobadas. Advertencia preexistente de deprecación Starlette/httpx; no afecta los resultados. El replay y el navegador son evidencias diferentes: el primero usa reloj lógico, el segundo usa horas y servicios reales.
