# Modelo y decisión operativa

El objetivo es clasificar la condición **actual** `Machine failure` de AI4I 2020. No existe horizonte de anticipación ni una etiqueta futura. La puntuación de Gradient Boosting no se presenta como probabilidad calibrada de una avería futura. La demo no ejecuta órdenes de control sobre equipos.

Pipeline único: selección de seis entradas físicas → tres características derivadas → estandarización de variables numéricas y codificación del tipo de producto → `GradientBoostingClassifier`. La persistencia incluye el pipeline completo, contrato de características, versión de scikit-learn, hash del dataset, hash del artefacto, umbral, particiones y métricas. Se verifican contrato, versión y hash antes de cargar el artefacto. Los archivos joblib solo deben proceder de un entrenamiento local confiable; un hash no convierte una fuente desconocida en confiable.

Se usan 160 árboles, profundidad máxima 3, tasa de aprendizaje 0,07, mínimo de 10 muestras por hoja y semilla 42. Estos parámetros están fijados en código. El umbral maximiza F2 en validación entre 0,05 y 0,95, dando mayor peso a recall. No se selecciona con las muestras de prueba. Las alternativas son un árbol de profundidad 3 que produce reglas inspeccionables y la estrategia de clasificar siempre como normal. Los resultados completos están en `reports/metrics/evaluation.json`; las reglas estandarizadas, en `reports/metrics/baseline-rules.txt`.

En la ejecución local inicial, el modelo detecta 28 de los 39 fallos reservados, omite 11 y genera 2 falsas alarmas. Las reglas detectan 29, omiten 10 y generan 91 falsas alarmas. Este resultado muestra una reducción de falsas alarmas con una detección ligeramente menor; no prueba superioridad para cualquier coste operacional. El conjunto de prueba solo contiene 39 positivos: los porcentajes tienen incertidumbre y no justifican una decisión de mantenimiento de planta.

El orden publicado se conserva en tres bloques 60/20/20. No se afirma validación por fechas o máquinas reales. Los datos son sintéticos y parte de su etiqueta proviene de reglas generadoras conocidas. La distribución de clases varía entre bloques. Revisar [`data/README.md`](../data/README.md) antes de interpretar las métricas.

Las latencias del manifiesto se midieron con 100 inferencias de una fila después de calentamiento, en el entorno identificado. Incluyen el pipeline, pero no HTTP, almacenamiento, interfaz, red ni una carga concurrente. No son un benchmark de capacidad industrial.

Para un uso real faltan datos trazables del proceso, unidades y límites acordados con operación, etiquetas con horizonte cuando se quiera anticipación, validación por tiempo/activo, costes de error, calibración, seguimiento de deriva, autenticación y una revisión de seguridad operacional.
