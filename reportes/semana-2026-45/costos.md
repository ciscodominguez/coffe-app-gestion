# Revisión de costos — Semana 45 (02/11 al 08/11)

## Resumen
- Costo cargado del grupo: USD 865,40
- Costo entregado (trabajo terminado): USD 6.675,00 (771% del cargado)
- Costo imputado (terminado + en curso): USD 8.250,00
- Capacidad no utilizada: USD 0,00
- Costo por story point: USD 9,72 (USD 865,40 ÷ 89 SP)
- Infraestructura (semana): USD 2,31
- Calidad de datos: 30 tareas sin horas registradas

## Costo por integrante
| Integrante | Grupo | Dedicación | Costo cargado | Horas | Costo imputado | Entregado | No utilizado |
|---|---|---|---|---|---|---|---|
| Francisco Domínguez | integrante | 25 % | USD 173,08 | 120 h* | USD 2.250,00 | USD 2.250,00 | USD 0,00 |
| Octavio Penacchietti | integrante | 25 % | USD 173,08 | 88 h* | USD 1.650,00 | USD 1.650,00 | USD 0,00 |
| Giovani Napoli | colaborador | 25 % | USD 173,08 | 92 h* | USD 1.725,00 | USD 1.575,00 | USD 0,00 |
| Facundo Gregorio | colaborador | 25 % | USD 173,08 | 68 h* | USD 1.275,00 | USD 675,00 | USD 0,00 |
| Nicolás Spina | colaborador | 25 % | USD 173,08 | 72 h* | USD 1.350,00 | USD 525,00 | USD 0,00 |

\* horas estimadas con la equivalencia de story points (no hay horas registradas).

## Costo por tarea (top 10 por costo)
| Tarea | Responsable | Estimado | Real | Desvío | Costo USD | Estado |
|---|---|---|---|---|---|---|
| PR-15 — El cliente paga con QR de Mercado Pago | Francisco Domínguez | 32 h (8 SP) | sin registro | — | USD 600,00 | terminada |
| PR-9 — El cajero cobra un pedido desde la pantalla de caja | Francisco Domínguez | 32 h (8 SP) | sin registro | — | USD 600,00 | terminada |
| PR-39 — El dueño dibuja el plano del salón y pide soporte con un botón | Nicolás Spina | 32 h (8 SP) | sin registro | — | USD 600,00 | en_revision |
| PR-16 — La caja abre, cobra, registra movimientos y cierra con conteo | Octavio Penacchietti | 20 h (5 SP) | sin registro | — | USD 375,00 | terminada |
| PR-20 — Un producto tiene variantes y agregados (tamaño, leche, extra shot) | Giovani Napoli | 20 h (5 SP) | sin registro | — | USD 375,00 | terminada |
| PR-26 — La plataforma ve todos los cafés clientes y los activa o suspende (panel superadmin) | Giovani Napoli | 20 h (5 SP) | sin registro | — | USD 375,00 | terminada |
| PR-24 — El mozo elige variantes y agregados al cargar el pedido | Octavio Penacchietti | 20 h (5 SP) | sin registro | — | USD 375,00 | terminada |
| PR-29 — Cada café paga su suscripción mensual con débito automático | Giovani Napoli | 20 h (5 SP) | sin registro | — | USD 375,00 | terminada |
| PR-35 — La app está lista para instalarse en un servidor (Docker, HTTPS, backups) | Francisco Domínguez | 20 h (5 SP) | sin registro | — | USD 375,00 | terminada |
| PR-36 — Probamos todo antes de salir: barrido de endpoints, carga y concurrencia | Octavio Penacchietti | 20 h (5 SP) | sin registro | — | USD 375,00 | terminada |

## Oportunidades de optimización
1. **Trabajo bloqueado** — PRs listos que esperaron revisión: PR-9 2 días hábiles; PR-11 2 días hábiles; PR-14 2 días hábiles; PR-25 2 días hábiles; PR-27 2 días hábiles. Costo de la espera = días × costo diario del autor × 15 % (retomar contexto, rebase). Costo: USD 51,92. Acordar que todo PR se revisa en menos de 24 h y nombrar el revisor al abrirlo. Ahorro estimado: USD 51,92/semana.
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
Como empresa, la semana se justifica: de USD 865,40 pagados, USD 6.675,00 se convirtieron en trabajo terminado (valuado a la equivalencia de SP). Ojo: lo entregado supera lo que permite la dedicación declarada, así que el resultado real depende de cuántas horas se trabajaron de verdad.
