# Datos y procedencia

La versión actual usa **AI4I 2020 Predictive Maintenance Dataset**, UCI Machine Learning Repository, DOI [10.24432/C5HS5C](https://doi.org/10.24432/C5HS5C). Fuente y descarga: [ficha oficial de UCI](https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset). Consultada el 27 de octubre de 2026. Licencia de los datos: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); el código del repositorio mantiene MIT. El CSV descargado se conserva sin modificaciones.

Son 10.000 observaciones **sintéticas**, con tipo de producto, temperatura ambiente y de proceso en kelvin, velocidad en rpm, par en N·m y desgaste de herramienta en minutos. `Machine failure` describe una condición de fallo en esa observación; no una falla etiquetada a un horizonte futuro.

Los identificadores `UDI` y `Product ID`, la etiqueta principal y las columnas de tipos de fallo `TWF/HDF/PWF/OSF/RNF` nunca entran al modelo. El pipeline obtiene diferencia de temperaturas, potencia mecánica y desgaste × par a partir de las seis características permitidas. Renombres y fórmulas están en el código; el SHA-256 del CSV queda en cada manifiesto de entrenamiento.

Se reservan bloques consecutivos del orden publicado: primeras 6.000 filas para entrenar, siguientes 2.000 para elegir el umbral y últimas 2.000 para evaluar. Aunque UCI describe procesos generadores con dependencia de orden, no hay marcas de tiempo de adquisición ni identificadores verificables de máquinas. Este corte no se presenta como validación temporal de una planta ni como generalización a activos nuevos. Las reglas que generan la simulación facilitan la clasificación y limitan la validez externa de las métricas.

El CSV `sensor_data.csv` de la implementación anterior no tenía una fuente o generador documentado. Una comprobación descriptiva encontró que temperatura >80 o vibración >4 coincidía con 4.997 de sus 5.000 etiquetas. Ese hallazgo no acredita su origen. El archivo anterior, los modelos serializados y los notebooks originales se conservan en el historial Git, commit `fc4f974fa6426c667d593dbc54dca60dc09b29a2`; no se reutilizan como evidencia de esta evaluación.

La telemetría de la demo se genera con una semilla fija y mediciones definidas en `simulation.py`. Sus timestamps y nombres de activo se crean para la demostración; no son metadatos atribuidos a UCI.
