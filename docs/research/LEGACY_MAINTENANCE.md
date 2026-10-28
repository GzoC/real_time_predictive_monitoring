# Del 100 % aparente a una evaluación defendible

El proyecto precursor `predictive_maintenance_01` comunicaba anticipación de mantenimiento con resultados perfectos. Se reexaminó su [versión c69f802](https://github.com/GzoC/predictive_maintenance_01/tree/c69f8024fd1f014f7f2de591f5594cc21b14a69d) y se conserva aquí el experimento corregido. Este estudio forma parte de la misma narrativa de condición industrial del monitor.

## Hallazgo reproducido

En sus 10.000 filas, `failure_type != "No Failure"` reproduce **el 100 % de `maintenance_required`**: 8.474 casos normales y 1.526 positivos. El notebook de modelado conservaba ese diagnóstico como entrada. Si se pretende decidir antes de conocer el fallo, la respuesta ya estaba dentro de las variables disponibles al modelo. El 100 % no mide anticipación.

El preprocesamiento también escalaba la etiqueta y ajustaba transformaciones antes de separar los datos; los codificadores se reajustaban en cada llamada. Las versiones originales permanecen en Git como evidencia histórica, no se ejecutan ni se cargan sus pickles.

## Experimento corregido

Se permite únicamente `operating_hours`, `temperature`, `vibration`, `pressure` y `humidity`. Se excluyen `machine_id`, `failure_type` y la etiqueta. No se inventan unidades ni una cronología: no hay timestamps, órdenes de mantenimiento ni activos con seguimiento verificable. Los identificadores son únicos por fila, por lo que no acreditan una validación por máquina.

Se realiza una partición **aleatoria estratificada 60/20/20, semilla 42**. El pipeline ajusta `StandardScaler` y clasificador solo con las 6.000 filas de entrenamiento. Las 2.000 de validación eligen el umbral F2; las 2.000 de prueba quedan reservadas. Se fijan regresión logística y Gradient Boosting sin búsqueda de hiperparámetros contra el test. La etiqueta solo permite una clasificación exploratoria de la etiqueta histórica; no define un horizonte futuro.

Holdout: 305 positivos y 1.695 negativos. Ejecución Windows/Python 3.12.13/scikit-learn 1.9.1:

| Método | TP | FN | FP | TN | ROC AUC | AP |
|---|---:|---:|---:|---:|---:|---:|
| Regresión logística, umbral 0,10 | 305 | 0 | 1695 | 0 | 0,508 | 0,150 |
| Gradient Boosting, umbral 0,05 | 305 | 0 | 1694 | 1 | 0,471 | 0,144 |
| Siempre normal | 0 | 305 | 0 | 1695 | 0,500 | 0,153 |
| Siempre alarma | 305 | 0 | 1695 | 0 | 0,500 | 0,153 |

F2 favorece aquí clasificar casi todo como alarma. Recall 100 % con 1.694–1.695 falsas alarmas no demuestra utilidad; la estrategia siempre alarma logra prácticamente el mismo resultado. AP no mejora la prevalencia de positivos del holdout (15,25 %) y los ROC AUC observados no muestran una discriminación útil. Una partición no demuestra imposibilidad de aprender, pero estos resultados no justifican una afirmación de capacidad industrial.

Se informa además el costo ilustrativo `FP + 10 × FN`: 1.695 logística, 1.694 Gradient Boosting, 3.050 siempre normal y 1.695 siempre alarma. Son unidades arbitrarias, no costos medidos de una planta ni criterio usado para seleccionar el umbral. Harían falta costos operacionales reales y un presupuesto de alarmas para definir una decisión.

## Procedencia y reproducción

La fuente/generador y licencia del CSV precursor no están verificados. El MIT del código no acredita licencia de datos. Por eso no se redistribuye ese CSV en este sucesor; se consulta el archivo histórico ya publicado exclusivamente para auditoría. No se atribuye a AI4I ni a UCI. SHA256 con finales LF: `a44c2233ed82dd3eb07aa6bf6f35e5fb6ec13be78ea52023bb51e6e0346d061d`. El informe también guarda el hash de bytes locales: Git puede convertir LF a CRLF sin cambiar valores.

Desde este repositorio con las dependencias del README:

```bash
git clone https://github.com/GzoC/predictive_maintenance_01.git ../legacy-maintenance
git -C ../legacy-maintenance switch --detach c69f8024fd1f014f7f2de591f5594cc21b14a69d
uv run --no-sync python scripts/audit_legacy_maintenance.py --legacy-csv ../legacy-maintenance/data/raw/machine_data.csv --output var/legacy-audit.json
```

El script verifica el hash antes de entrenar. No modifica el CSV, no escala la etiqueta y no genera un artefacto desplegable a partir de datos sin procedencia. [Resultado medido](../../reports/research/legacy_maintenance_audit.json), [script](../../scripts/audit_legacy_maintenance.py), [pruebas](../../tests/test_legacy_research.py). CI reproduce el estudio desde la URL fijada al commit y sube el informe sin redistribuir el CSV.

## Continuidad

La versión operativa del monitor usa AI4I 2020, sintético y con atribución verificable: [datos](../../data/README.md), [modelo](../MODEL_CARD.md). Su evaluación de condición actual (28/39 fallos detectados, 2 falsas alarmas) pertenece a otro dataset y protocolo; **no es una mejora numérica comparable** al experimento precursor. Se conserva la investigación válida: demostrar cómo una fuga cambia la interpretación, separar antes de transformar y confrontar modelos con estrategias triviales.

Recomendación para el portafolio: destacar el monitor y este análisis; retirar el precursor de destacados y archivarlo después de integrar esta investigación y su aviso de migración. Primero deben estar disponibles ambos cambios en sus ramas principales.
