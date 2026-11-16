# Reporte del Product Owner — COFFE_APP — Semana 46 (09/11 al 15/11)

Grupo: Agustín Avalos, Francisco Domínguez, Octavio Penacchietti. Fuente: gestion/plane/tickets.json (tablero reconstruido desde git).

## Resumen: 🟢 En camino

> ⚠️ **Velocidad en caída.** 26 SP esta semana contra 85 SP de promedio en las anteriores (31%). Propuesta: Ver si falta trabajo cargado en el tablero o si el equipo frenó.

| Métrica | Valor |
|---|---|
| Puntos terminados | 26 SP (6 tareas) |
| Velocidad promedio de todo el equipo (3 semanas, usada en la proyección) | 65.3 SP/semana |
| Velocidad promedio solo del grupo del TP | 29.3 SP/semana |
| Avance total | 93% (196 de 210 SP comprometidos) |
| Lead time / cycle time promedio | 14.5 / 3.0 días |
| Espera de revisión promedio | 1.7 días hábiles |
| Alcance nuevo en la semana | 0 SP |
| Tareas bloqueadas | 0 |

## Proyección por entrega

| Entrega | SP pendientes | Semanas que quedan | Semanas necesarias | Estado |
|---|---|---|---|---|
| Parcial 2026-11-16 | 0 | 0.1 | 0.0 | 0.0 | 🟢 En camino |
| Parcial 2026-11-30 | 11 | 2.1 | 0.2 | 0.4 | 🟢 En camino |
| Final 2026-12-14 | 14 | 4.1 | 0.2 | 0.5 | 🟢 En camino |

## Lo que logramos

**Gestión del negocio**
- Un usuario nuevo aprende la app con un tour guiado (Giovani Napoli, 2 SP)

**Plataforma SaaS**
- El sistema cumple con términos, privacidad y botón de arrepentimiento/baja (Facundo Gregorio, 3 SP)
- La plataforma administra cafés clientes y planes (superadmin) (Nicolás Spina, 3 SP)

**Carta y salón**
- El dueño dibuja el plano del salón y pide soporte con un botón (Nicolás Spina, 8 SP)
- El salón se organiza por zonas y el café puede pedir soporte (Facundo Gregorio, 5 SP)

**Base del proyecto**
- Cualquiera del equipo entiende el proyecto leyendo el README (Nicolás Spina, 5 SP)

## Avance por épica

| Épica | Terminado | Total |
|---|---|---|
| Base del proyecto | 7 SP | 7 SP |
| Caja y cobros | 33 SP | 33 SP |
| Carta y salón | 34 SP | 34 SP |
| Cuentas y acceso | 33 SP | 33 SP |
| Gestión del negocio | 24 SP | 24 SP |
| Pedidos y cocina | 26 SP | 26 SP |
| Plataforma SaaS | 21 SP | 23 SP |
| Salida a producción | 10 SP | 22 SP |
| Stock | 8 SP | 8 SP |

## Alertas y desvíos

- **[alto] Velocidad en caída:** 26 SP esta semana contra 85 SP de promedio en las anteriores (31%). → Ver si falta trabajo cargado en el tablero o si el equipo frenó.

## Costo

Cargado USD 865,40, entregado USD 1.950,00, no utilizado USD 369,24. Detalle en `costos.md`.

## Riesgo de Brooks

🟡 Ruta crítica P-1 → P-2 → P-5 (11 SP). Detalle en `brooks.md`.

## Próxima semana

1. P-1 — Un café piloto entra a la app desde internet con HTTPS (Francisco Domínguez, 5 SP)
2. P-2 — Las copias nocturnas se restauran bien (prueba real de restauración) (Octavio Penacchietti, 3 SP)
3. P-3 — Nos avisa al celular si la app se cae (monitor sobre /actuator/health) (Octavio Penacchietti, 1 SP)
4. P-4 — Términos y privacidad con los datos reales del responsable (Agustín Avalos, 2 SP)

## Limitaciones de datos

- No hay horas registradas: los costos usan la equivalencia de SP de equipo.md.
- Las semanas 44 a 46 se reconstruyeron desde git (fecha del commit = listo para revisión, merge = terminada); no hay registro de cuándo empezó cada tarea, así que el cycle time es el tiempo en revisión.
- No hay tareas de reuniones ni bloqueos explícitos en el tablero.
- El lead time de los tickets reconstruidos se mide desde el 26/10 (alcance planificado al arrancar), no desde una fecha de creación real.
