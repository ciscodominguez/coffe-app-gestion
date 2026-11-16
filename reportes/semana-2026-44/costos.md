# Revisión de costos — Semana 44 (26/10 al 01/11)

## Resumen
- Costo cargado del grupo: USD 865,40
- Costo entregado (trabajo terminado): USD 6.075,00 (702% del cargado)
- Costo imputado (terminado + en curso): USD 7.350,00
- Capacidad no utilizada: USD 0,00
- Costo por story point: USD 10,68 (USD 865,40 ÷ 81 SP)
- Infraestructura (semana): USD 2,31
- Calidad de datos: 15 tareas sin horas registradas

## Costo por integrante
| Integrante | Grupo | Dedicación | Costo cargado | Horas | Costo imputado | Entregado | No utilizado |
|---|---|---|---|---|---|---|---|
| Francisco Domínguez | integrante | 25 % | USD 173,08 | 76 h* | USD 1.425,00 | USD 750,00 | USD 0,00 |
| Octavio Penacchietti | integrante | 25 % | USD 173,08 | 104 h* | USD 1.950,00 | USD 1.950,00 | USD 0,00 |
| Giovani Napoli | colaborador | 25 % | USD 173,08 | 56 h* | USD 1.050,00 | USD 825,00 | USD 0,00 |
| Facundo Gregorio | colaborador | 25 % | USD 173,08 | 96 h* | USD 1.800,00 | USD 1.575,00 | USD 0,00 |
| Nicolás Spina | colaborador | 25 % | USD 173,08 | 60 h* | USD 1.125,00 | USD 975,00 | USD 0,00 |

\* horas estimadas con la equivalencia de story points (no hay horas registradas).

## Costo por tarea (top 10 por costo)
| Tarea | Responsable | Estimado | Real | Desvío | Costo USD | Estado |
|---|---|---|---|---|---|---|
| PR-6 — El mozo toma pedidos aunque se corte internet y cocina los ve en su pantalla | Facundo Gregorio | 52 h (13 SP) | sin registro | — | USD 975,00 | terminada |
| PR-7 — Los usuarios entran a la app web: base Angular, menú, login y registro | Octavio Penacchietti | 52 h (13 SP) | sin registro | — | USD 975,00 | terminada |
| PR-10 — El dueño administra su negocio, usuarios y locales desde la web | Octavio Penacchietti | 52 h (13 SP) | sin registro | — | USD 975,00 | terminada |
| PR-1 — Un café se registra solo y entra con su usuario; carga locales y empleados | Giovani Napoli | 32 h (8 SP) | sin registro | — | USD 600,00 | terminada |
| PR-2 — Cada café ve solo sus datos: JWT, aislamiento multi-tenant y errores claros | Nicolás Spina | 32 h (8 SP) | sin registro | — | USD 600,00 | terminada |
| PR-3 — Los pedidos de las mesas llegan a cocina al instante (WebSocket) | Facundo Gregorio | 32 h (8 SP) | sin registro | — | USD 600,00 | terminada |
| PR-5 — El dueño arma la carta y las mesas desde la pantalla | Francisco Domínguez | 32 h (8 SP) | sin registro | — | USD 600,00 | terminada |
| PR-9 — El cajero cobra un pedido desde la pantalla de caja | Francisco Domínguez | 32 h (8 SP) | sin registro | — | USD 600,00 | en_revision |
| PR-8 — El café sabe cuánto stock le queda: insumos, recetas y descuento por venta | Nicolás Spina | 20 h (5 SP) | sin registro | — | USD 375,00 | terminada |
| PR-4 — La carta tiene categorías y productos con foto e ingredientes | Giovani Napoli | 12 h (3 SP) | sin registro | — | USD 225,00 | terminada |

## Oportunidades de optimización
1. **Retrabajo** — 5 commits de la semana están dos veces en el repo con distinto hash (12443 líneas): la historia de main se corrigió y se volvieron a aplicar. No hay horas registradas del arreglo; se toma 1 h por commit (supuesto). Costo: USD 93,75. Proteger main en GitHub (solo merge por PR, sin force-push) para no tener que rehacer historia. Ahorro estimado: USD 93,75/semana.
2. **Infraestructura** — VPS 2 GB de RAM (producción, todavía sin alquilar): USD 10,00 por mes. Costo: USD 2,31. Evaluar Oracle Cloud Always Free: Ampere A1 hasta 2 OCPU / 12 GB (desde jun-2026), con imágenes arm64. Ahorro estimado: USD 2,31/semana.

## Supuestos
- Costo: USD 3.000 por mes por integrante → USD 18,75 la hora → USD 692,31 por semana (× 12 ÷ 52), multiplicado por la dedicación de equipo.md.
- Capacidad semanal = 40 h × dedicación.
- Ninguna tarea tiene horas registradas: las horas se estiman con la equivalencia de equipo.md (1 SP = 4 h). Imputado = horas de lo terminado en la semana + de lo que quedó abierto al cierre.
- Fuente: gestion/plane/tickets.json (tablero reconstruido desde git).
- No hay tareas de tipo reunión en el tablero: no se puede medir el tiempo de coordinación.
- Sin horas registradas no se puede medir el desvío de estimación ni la subestimación crónica.
- El costo imputado supera al cargado en: Francisco Domínguez, Octavio Penacchietti, Giovani Napoli, Facundo Gregorio, Nicolás Spina. Con 1 SP = 4 h lo entregado no entra en la dedicación declarada: o trabajaron más horas de las declaradas, o la equivalencia de SP es alta para este equipo. Conviene registrar horas reales.

## Conclusión
Como empresa, la semana se justifica: de USD 865,40 pagados, USD 6.075,00 se convirtieron en trabajo terminado (valuado a la equivalencia de SP). Ojo: lo entregado supera lo que permite la dedicación declarada, así que el resultado real depende de cuántas horas se trabajaron de verdad.
