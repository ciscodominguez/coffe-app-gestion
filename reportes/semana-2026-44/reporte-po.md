# Reporte del Product Owner — COFFE_APP — Semana 44 (26/10 al 01/11)

Grupo: Agustín Avalos, Francisco Domínguez, Octavio Penacchietti. Fuente: gestion/plane/tickets.json (tablero reconstruido desde git).

## Resumen: 🟢 En camino

| Métrica | Valor |
|---|---|
| Puntos terminados | 81 SP (10 tareas) |
| Velocidad promedio de todo el equipo (3 semanas, usada en la proyección) | 81.0 SP/semana |
| Velocidad promedio solo del grupo del TP | 36.0 SP/semana |
| Avance total | 39% (81 de 210 SP comprometidos) |
| Lead time / cycle time promedio | 3.8 / 0.1 días |
| Espera de revisión promedio | 0.0 días hábiles |
| Alcance nuevo en la semana | 231 SP |
| Tareas bloqueadas | 0 |

## Proyección por entrega

| Entrega | SP pendientes | Semanas que quedan | Semanas necesarias | Estado |
|---|---|---|---|---|
| Parcial 2026-11-16 | 115 | 2.1 | 1.4 | 3.2 | 🟢 En camino |
| Parcial 2026-11-30 | 126 | 4.1 | 1.6 | 3.5 | 🟢 En camino |
| Final 2026-12-14 | 129 | 6.1 | 1.6 | 3.6 | 🟢 En camino |

## Lo que logramos

**Base del proyecto**
- El equipo tiene el repo y el proyecto Spring Boot listos para trabajar (Francisco Domínguez, 2 SP)

**Cuentas y acceso**
- Un café se registra solo y entra con su usuario; carga locales y empleados (Giovani Napoli, 8 SP)
- Cada café ve solo sus datos: JWT, aislamiento multi-tenant y errores claros (Nicolás Spina, 8 SP)
- Los usuarios entran a la app web: base Angular, menú, login y registro (Octavio Penacchietti, 13 SP)

**Pedidos y cocina**
- Los pedidos de las mesas llegan a cocina al instante (WebSocket) (Facundo Gregorio, 8 SP)
- El mozo toma pedidos aunque se corte internet y cocina los ve en su pantalla (Facundo Gregorio, 13 SP)

**Carta y salón**
- El dueño arma la carta y las mesas desde la pantalla (Francisco Domínguez, 8 SP)
- La carta tiene categorías y productos con foto e ingredientes (Giovani Napoli, 3 SP)

**Stock**
- El café sabe cuánto stock le queda: insumos, recetas y descuento por venta (Nicolás Spina, 5 SP)

**Gestión del negocio**
- El dueño administra su negocio, usuarios y locales desde la web (Octavio Penacchietti, 13 SP)

## Avance por épica

| Épica | Terminado | Total |
|---|---|---|
| Base del proyecto | 2 SP | 7 SP |
| Caja y cobros | 0 SP | 33 SP |
| Carta y salón | 11 SP | 34 SP |
| Cuentas y acceso | 29 SP | 33 SP |
| Gestión del negocio | 13 SP | 24 SP |
| Pedidos y cocina | 21 SP | 26 SP |
| Plataforma SaaS | 0 SP | 23 SP |
| Salida a producción | 0 SP | 22 SP |
| Stock | 5 SP | 8 SP |

## Alertas y desvíos

- **[medio] Crecimiento de alcance:** Entraron 231 SP nuevos y se terminaron 81. → Confirmar con el PO qué entra en la próxima entrega y qué pasa a deseable.

## Costo

Cargado USD 865,40, entregado USD 6.075,00, no utilizado USD 0,00. Detalle en `costos.md`.

## Riesgo de Brooks

🟡 Ruta crítica PR-16 → PR-15 → PR-17 (16 SP). Detalle en `brooks.md`.

## Próxima semana

1. PR-16 — La caja abre, cobra, registra movimientos y cierra con conteo (Octavio Penacchietti, 5 SP)
2. PR-9 — El cajero cobra un pedido desde la pantalla de caja (Francisco Domínguez, 8 SP)
3. PR-31 — Los pedidos de apps de delivery se cargan en modo manual (Francisco Domínguez, 3 SP)
4. PR-27 — La plataforma administra cafés clientes y planes (superadmin) (Nicolás Spina, 3 SP)
5. PR-13 — El dueño ve el resumen del día apenas entra (Francisco Domínguez, 1 SP)
6. PR-15 — El cliente paga con QR de Mercado Pago (Francisco Domínguez, 8 SP)

## Limitaciones de datos

- No hay horas registradas: los costos usan la equivalencia de SP de equipo.md.
- Las semanas 44 a 46 se reconstruyeron desde git (fecha del commit = listo para revisión, merge = terminada); no hay registro de cuándo empezó cada tarea, así que el cycle time es el tiempo en revisión.
- No hay tareas de reuniones ni bloqueos explícitos en el tablero.
- El lead time de los tickets reconstruidos se mide desde el 26/10 (alcance planificado al arrancar), no desde una fecha de creación real.
