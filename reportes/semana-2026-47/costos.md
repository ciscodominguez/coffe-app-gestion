# Revisión de costos — Semana 47 (16/11 al 22/11)

## Resumen
- Costo cargado del grupo: USD 1.038,48
- Costo entregado (trabajo terminado): USD 450,00 (43% del cargado)
- Costo imputado (terminado + en curso): USD 750,00
- Capacidad no utilizada: USD 519,24
- Costo por story point: USD 173,08 (USD 1.038,48 ÷ 6 SP)
- Infraestructura (semana): USD 2,31
- Calidad de datos: 5 tareas sin horas registradas

## Costo por integrante
| Integrante | Grupo | Dedicación | Costo cargado | Horas | Costo imputado | Entregado | No utilizado |
|---|---|---|---|---|---|---|---|
| Francisco Domínguez | integrante | 25 % | USD 173,08 | 12 h* | USD 225,00 | USD 225,00 | USD 0,00 |
| Octavio Penacchietti | integrante | 25 % | USD 173,08 | 12 h* | USD 225,00 | USD 0,00 | USD 0,00 |
| Agustín Avalos | integrante | 25 % | USD 173,08 | 16 h* | USD 300,00 | USD 225,00 | USD 0,00 |
| Giovani Napoli | colaborador | 25 % | USD 173,08 | 0 h* | USD 0,00 | USD 0,00 | USD 173,08 |
| Facundo Gregorio | colaborador | 25 % | USD 173,08 | 0 h* | USD 0,00 | USD 0,00 | USD 173,08 |
| Nicolás Spina | colaborador | 25 % | USD 173,08 | 0 h* | USD 0,00 | USD 0,00 | USD 173,08 |

\* horas estimadas con la equivalencia de story points (no hay horas registradas).

## Costo por tarea (top 10 por costo)
| Tarea | Responsable | Estimado | Real | Desvío | Costo USD | Estado |
|---|---|---|---|---|---|---|
| G-3 — Las semanas ya trabajadas quedan cargadas en Plane desde el historial de git | Francisco Domínguez | 12 h (3 SP) | sin registro | — | USD 225,00 | terminada |
| G-6 — La arquitectura C4 se mantiene sola con la skill arquitecto-c4 | Octavio Penacchietti | 12 h (3 SP) | sin registro | — | USD 225,00 | en_curso |
| G-1 — El grupo tiene su tablero en Plane con ciclos, módulos y estimaciones | Agustín Avalos | 8 h (2 SP) | sin registro | — | USD 150,00 | terminada |
| G-2 — El tablero se lee por API: token personal probado con curl | Agustín Avalos | 4 h (1 SP) | sin registro | — | USD 75,00 | terminada |
| G-4 — equipo.md completo: integrantes, dedicación, objetivos, fechas y costos de infra | Agustín Avalos | 4 h (1 SP) | sin registro | — | USD 75,00 | en_curso |

## Oportunidades de optimización
1. **Capacidad ociosa** — Giovani Napoli tiene USD 173,08 de costo cargado y USD 0,00 imputado (ninguna tarea movida ni commits en la semana). Costo: USD 173,08. Asignarle tickets del ciclo o revisiones; si trabaja en algo que no está en el tablero, cargarlo; si no va a trabajar, bajar su dedicación en equipo.md. Ahorro estimado: USD 173,08/semana.
2. **Capacidad ociosa** — Facundo Gregorio tiene USD 173,08 de costo cargado y USD 0,00 imputado (ninguna tarea movida ni commits en la semana). Costo: USD 173,08. Asignarle tickets del ciclo o revisiones; si trabaja en algo que no está en el tablero, cargarlo; si no va a trabajar, bajar su dedicación en equipo.md. Ahorro estimado: USD 173,08/semana.
3. **Capacidad ociosa** — Nicolás Spina tiene USD 173,08 de costo cargado y USD 0,00 imputado (ninguna tarea movida ni commits en la semana). Costo: USD 173,08. Asignarle tickets del ciclo o revisiones; si trabaja en algo que no está en el tablero, cargarlo; si no va a trabajar, bajar su dedicación en equipo.md. Ahorro estimado: USD 173,08/semana.
4. **Infraestructura** — VPS 2 GB de RAM (producción, todavía sin alquilar): USD 10,00 por mes. Costo: USD 2,31. Evaluar Oracle Cloud Always Free: Ampere A1 hasta 2 OCPU / 12 GB (desde jun-2026), con imágenes arm64. Ahorro estimado: USD 2,31/semana.

## Supuestos
- Costo: USD 3.000 por mes por integrante → USD 18,75 la hora → USD 692,31 por semana (× 12 ÷ 52), multiplicado por la dedicación de equipo.md.
- Capacidad semanal = 40 h × dedicación.
- Ninguna tarea tiene horas registradas: las horas se estiman con la equivalencia de equipo.md (1 SP = 4 h). Imputado = horas de lo terminado en la semana + de lo que quedó abierto al cierre.
- Fuente: gestion/plane/tickets.json (tablero reconstruido desde git).
- No hay tareas de tipo reunión en el tablero: no se puede medir el tiempo de coordinación.
- Sin horas registradas no se puede medir el desvío de estimación ni la subestimación crónica.
- El costo imputado supera al cargado en: Francisco Domínguez, Octavio Penacchietti, Agustín Avalos. Con 1 SP = 4 h lo entregado no entra en la dedicación declarada: o trabajaron más horas de las declaradas, o la equivalencia de SP es alta para este equipo. Conviene registrar horas reales.

## Conclusión
Como empresa, la semana se justifica a medias: se pagaron USD 1.038,48 y solo USD 450,00 terminaron entregados; el resto quedó en curso o sin usar. Ojo: lo entregado supera lo que permite la dedicación declarada, así que el resultado real depende de cuántas horas se trabajaron de verdad.
