# Revisión de costos — Semana 46 (09/11 al 15/11)

## Resumen
- Costo cargado del grupo: USD 865,40
- Costo entregado (trabajo terminado): USD 1.950,00 (225% del cargado)
- Costo imputado (terminado + en curso): USD 1.950,00
- Capacidad no utilizada: USD 369,24
- Costo por story point: USD 33,28 (USD 865,40 ÷ 26 SP)
- Infraestructura (semana): USD 2,31
- Calidad de datos: 6 tareas sin horas registradas

## Costo por integrante
| Integrante | Grupo | Dedicación | Costo cargado | Horas | Costo imputado | Entregado | No utilizado |
|---|---|---|---|---|---|---|---|
| Francisco Domínguez | integrante | 25 % | USD 173,08 | 0 h* | USD 0,00 | USD 0,00 | USD 173,08 |
| Octavio Penacchietti | integrante | 25 % | USD 173,08 | 0 h* | USD 0,00 | USD 0,00 | USD 173,08 |
| Giovani Napoli | colaborador | 25 % | USD 173,08 | 8 h* | USD 150,00 | USD 150,00 | USD 23,08 |
| Facundo Gregorio | colaborador | 25 % | USD 173,08 | 32 h* | USD 600,00 | USD 600,00 | USD 0,00 |
| Nicolás Spina | colaborador | 25 % | USD 173,08 | 64 h* | USD 1.200,00 | USD 1.200,00 | USD 0,00 |

\* horas estimadas con la equivalencia de story points (no hay horas registradas).

## Costo por tarea (top 10 por costo)
| Tarea | Responsable | Estimado | Real | Desvío | Costo USD | Estado |
|---|---|---|---|---|---|---|
| PR-39 — El dueño dibuja el plano del salón y pide soporte con un botón | Nicolás Spina | 32 h (8 SP) | sin registro | — | USD 600,00 | terminada |
| PR-38 — El salón se organiza por zonas y el café puede pedir soporte | Facundo Gregorio | 20 h (5 SP) | sin registro | — | USD 375,00 | terminada |
| PR-40 — Cualquiera del equipo entiende el proyecto leyendo el README | Nicolás Spina | 20 h (5 SP) | sin registro | — | USD 375,00 | terminada |
| PR-33 — El sistema cumple con términos, privacidad y botón de arrepentimiento/baja | Facundo Gregorio | 12 h (3 SP) | sin registro | — | USD 225,00 | terminada |
| PR-27 — La plataforma administra cafés clientes y planes (superadmin) | Nicolás Spina | 12 h (3 SP) | sin registro | — | USD 225,00 | terminada |
| PR-34 — Un usuario nuevo aprende la app con un tour guiado | Giovani Napoli | 8 h (2 SP) | sin registro | — | USD 150,00 | terminada |

## Oportunidades de optimización
1. **Trabajo bloqueado** — PRs listos que esperaron revisión: PR-27 3 días hábiles; PR-40 3 días hábiles. Costo de la espera = días × costo diario del autor × 15 % (retomar contexto, rebase). Costo: USD 31,15. Acordar que todo PR se revisa en menos de 24 h y nombrar el revisor al abrirlo. Ahorro estimado: USD 31,15/semana.
2. **Capacidad ociosa** — Francisco Domínguez tiene USD 173,08 de costo cargado y USD 0,00 imputado (sin tareas propias ni commits; hizo 3 revisiones de PRs, que no tienen horas cargadas). Costo: USD 173,08. Asignarle tickets del ciclo o revisiones; si trabaja en algo que no está en el tablero, cargarlo; si no va a trabajar, bajar su dedicación en equipo.md. Ahorro estimado: USD 173,08/semana.
3. **Capacidad ociosa** — Octavio Penacchietti tiene USD 173,08 de costo cargado y USD 0,00 imputado (sin tareas propias ni commits; hizo 1 revisiones de PRs, que no tienen horas cargadas). Costo: USD 173,08. Asignarle tickets del ciclo o revisiones; si trabaja en algo que no está en el tablero, cargarlo; si no va a trabajar, bajar su dedicación en equipo.md. Ahorro estimado: USD 173,08/semana.
4. **Desbalance** — Nicolás Spina concentra 62% de las horas del grupo (64 de 104 h estimadas). Costo: USD 0,00. Repartir el próximo ciclo; revisión cruzada para que otro conozca ese código. Ahorro estimado: USD 0,00/semana.
5. **Infraestructura** — VPS 2 GB de RAM (producción, todavía sin alquilar): USD 10,00 por mes. Costo: USD 2,31. Evaluar Oracle Cloud Always Free: Ampere A1 hasta 2 OCPU / 12 GB (desde jun-2026), con imágenes arm64. Ahorro estimado: USD 2,31/semana.

## Supuestos
- Costo: USD 3.000 por mes por integrante → USD 18,75 la hora → USD 692,31 por semana (× 12 ÷ 52), multiplicado por la dedicación de equipo.md.
- Capacidad semanal = 40 h × dedicación.
- Ninguna tarea tiene horas registradas: las horas se estiman con la equivalencia de equipo.md (1 SP = 4 h). Imputado = horas de lo terminado en la semana + de lo que quedó abierto al cierre.
- Fuente: gestion/plane/tickets.json (tablero reconstruido desde git).
- No hay tareas de tipo reunión en el tablero: no se puede medir el tiempo de coordinación.
- Sin horas registradas no se puede medir el desvío de estimación ni la subestimación crónica.
- El costo imputado supera al cargado en: Facundo Gregorio, Nicolás Spina. Con 1 SP = 4 h lo entregado no entra en la dedicación declarada: o trabajaron más horas de las declaradas, o la equivalencia de SP es alta para este equipo. Conviene registrar horas reales.

## Conclusión
Como empresa, la semana se justifica: de USD 865,40 pagados, USD 1.950,00 se convirtieron en trabajo terminado (valuado a la equivalencia de SP). Ojo: lo entregado supera lo que permite la dedicación declarada, así que el resultado real depende de cuántas horas se trabajaron de verdad.
