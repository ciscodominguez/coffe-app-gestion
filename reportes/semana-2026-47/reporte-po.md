# Reporte del Product Owner — COFFE_APP — Semana 47 (16/11 al 22/11)

Grupo: Agustín Avalos, Francisco Domínguez, Octavio Penacchietti. Fuente: Plane (API).

## Resumen: 🟢 En camino

> ⚠️ **Tablero quieto.** Ninguna tarea cambió de estado en 4 días hábiles (último movimiento 16/11). Propuesta: Mover los estados el mismo día que cambia el trabajo; crear el ticket antes de codear.

| Métrica | Valor |
|---|---|
| Puntos terminados | 6 SP (3 tareas) |
| Velocidad promedio de todo el equipo (3 semanas, usada en la proyección) | 40.3 SP/semana |
| Velocidad promedio solo del grupo del TP | 19.3 SP/semana |
| Avance total | 90% (202 de 224 SP comprometidos) |
| Lead time / cycle time promedio | 0.0 / 0.0 días |
| Espera de revisión promedio | — días hábiles |
| Alcance nuevo en la semana | 14 SP |
| Tareas bloqueadas | 0 |

## Proyección por entrega

| Entrega | SP pendientes | Semanas que quedan | Semanas necesarias | Necesarias solo con el grupo del TP | Estado |
|---|---|---|---|---|---|
| Parcial 2026-11-30 | 19 | 1.1 | 0.5 | 1.0 | 🟢 En camino |
| Final 2026-12-14 | 22 | 3.1 | 0.5 | 1.1 | 🟢 En camino |

## Lo que logramos

**Gestión del TP**
- Las semanas ya trabajadas quedan cargadas en Plane desde el historial de git (Francisco Domínguez, 3 SP)
- El tablero se lee por API: token personal probado con curl (Agustín Avalos, 1 SP)
- El grupo tiene su tablero en Plane con ciclos, módulos y estimaciones (Agustín Avalos, 2 SP)

## Avance por épica

| Épica | Terminado | Total |
|---|---|---|
| Base del proyecto | 7 SP | 7 SP |
| Caja y cobros | 33 SP | 33 SP |
| Carta y salón | 34 SP | 34 SP |
| Cuentas y acceso | 33 SP | 33 SP |
| Gestión del TP | 6 SP | 14 SP |
| Gestión del negocio | 24 SP | 24 SP |
| Pedidos y cocina | 26 SP | 26 SP |
| Plataforma SaaS | 21 SP | 23 SP |
| Salida a producción | 10 SP | 22 SP |
| Stock | 8 SP | 8 SP |

## Alertas y desvíos

- **[alto] Tablero quieto:** Ninguna tarea cambió de estado en 4 días hábiles (último movimiento 16/11). → Mover los estados el mismo día que cambia el trabajo; crear el ticket antes de codear.
- **[alto] Velocidad en caída:** 6 SP esta semana contra 65 SP de promedio en las anteriores (9%). → Ver si falta trabajo cargado en el tablero o si el equipo frenó.
- **[medio] Tarea en curso sin movimiento:** G-6 — La arquitectura C4 se mantiene sola con la skill arquitecto-c4 (Octavio Penacchietti) sin cambios hace 6 días. → Destrabarla o partirla en partes más chicas.
- **[medio] Tarea en curso sin movimiento:** G-4 — equipo.md completo: integrantes, dedicación, objetivos, fechas y costos de infra (Agustín Avalos) sin cambios hace 6 días. → Destrabarla o partirla en partes más chicas.
- **[medio] Comprometido no terminado:** 5 tarea(s) del ciclo de la semana sin terminar: P-1, G-7, G-6, G-5, G-4. → Pasarlas al próximo ciclo y ver por qué no cerraron.
- **[medio] Crecimiento de alcance:** Entraron 14 SP nuevos y se terminaron 6. → Confirmar con el PO qué entra en la próxima entrega y qué pasa a deseable.
- **[bajo] Commits sin tarea:** 12 commit(s) de la semana no están vinculados a ningún ticket (11899e1, 03fd585, 47d68c2, a41e5f2, b5a7003). → Poner el ID del issue de Plane en cada commit.

## Costo

Cargado USD 1.038,48, entregado USD 450,00, no utilizado USD 519,24. Detalle en `costos.md`.

## Riesgo de Brooks

🟡 Ruta crítica P-1 → P-2 → P-5 (11 SP). Detalle en `brooks.md`.

## Próxima semana

1. P-1 — Un café piloto entra a la app desde internet con HTTPS (Francisco Domínguez, 5 SP)
2. P-2 — Las copias nocturnas se restauran bien (prueba real de restauración) (Octavio Penacchietti, 3 SP)
3. P-3 — Nos avisa al celular si la app se cae (monitor sobre /actuator/health) (Octavio Penacchietti, 1 SP)
4. G-4 — equipo.md completo: integrantes, dedicación, objetivos, fechas y costos de infra (Agustín Avalos, 1 SP)
5. G-6 — La arquitectura C4 se mantiene sola con la skill arquitecto-c4 (Octavio Penacchietti, 3 SP)
6. G-5 — El PO tiene costos, Brooks y semáforo de cada semana (3 skills corriendo) (Agustín Avalos, 3 SP)

## Limitaciones de datos

- No hay horas registradas: los costos usan la equivalencia de SP de equipo.md.
- Las semanas 44 a 46 se reconstruyeron desde git (fecha del commit = listo para revisión, merge = terminada); no hay registro de cuándo empezó cada tarea, así que el cycle time es el tiempo en revisión.
- No hay tareas de reuniones ni bloqueos explícitos en el tablero.
- El lead time de los tickets reconstruidos se mide desde el 26/10 (alcance planificado al arrancar), no desde una fecha de creación real.
