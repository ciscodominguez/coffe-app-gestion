# Reporte del Product Owner — COFFE_APP — Semana 45 (02/11 al 08/11)

Grupo: Agustín Avalos, Francisco Domínguez, Octavio Penacchietti. Fuente: gestion/plane/tickets.json (tablero reconstruido desde git).

## Resumen: 🟢 En camino

| Métrica | Valor |
|---|---|
| Puntos terminados | 89 SP (25 tareas) |
| Velocidad promedio de todo el equipo (3 semanas, usada en la proyección) | 85.0 SP/semana |
| Velocidad promedio solo del grupo del TP | 44.0 SP/semana |
| Avance total | 81% (170 de 210 SP comprometidos) |
| Lead time / cycle time promedio | 9.1 / 0.6 días |
| Espera de revisión promedio | 0.5 días hábiles |
| Alcance nuevo en la semana | 0 SP |
| Tareas bloqueadas | 0 |

## Proyección por entrega

| Entrega | SP pendientes | Semanas que quedan | Semanas necesarias | Estado |
|---|---|---|---|---|
| Parcial 2026-11-16 | 26 | 1.1 | 0.3 | 0.6 | 🟢 En camino |
| Parcial 2026-11-30 | 37 | 3.1 | 0.4 | 0.8 | 🟢 En camino |
| Final 2026-12-14 | 40 | 5.1 | 0.5 | 0.9 | 🟢 En camino |

## Lo que logramos

**Caja y cobros**
- La caja abre, cobra, registra movimientos y cierra con conteo (Octavio Penacchietti, 5 SP)
- El cliente paga con QR de Mercado Pago (Francisco Domínguez, 8 SP)
- El cajero cobra un pedido desde la pantalla de caja (Francisco Domínguez, 8 SP)
- El café aplica descuentos a un ítem o a todo el pedido (Nicolás Spina, 3 SP)
- Se imprimen comanda, ticket y cierre de caja desde el navegador (Nicolás Spina, 2 SP)
- El dueño conecta su cuenta de Mercado Pago para cobrar con QR (Giovani Napoli, 3 SP)
- El cajero aplica descuentos desde una lista armada (Facundo Gregorio, 3 SP)
- La mesa divide la cuenta en partes iguales o por productos (Facundo Gregorio, 1 SP)

**Gestión del negocio**
- El dueño ve el resumen del día apenas entra (Francisco Domínguez, 1 SP)
- Cada rol ve un inicio con sus números clave (KPIs) (Giovani Napoli, 3 SP)
- El dueño consulta reportes de ventas en pantalla (Francisco Domínguez, 2 SP)
- El contador recibe un Excel con ventas y cierres de caja (Octavio Penacchietti, 3 SP)

**Cuentas y acceso**
- El usuario cambia o recupera su contraseña sin pedir ayuda (Facundo Gregorio, 2 SP)
- Las cuentas están protegidas: recuperar contraseña, bloqueo por intentos y cierre de sesiones (Octavio Penacchietti, 2 SP)

**Carta y salón**
- Un producto tiene variantes y agregados (tamaño, leche, extra shot) (Giovani Napoli, 5 SP)
- El mozo elige variantes y agregados al cargar el pedido (Octavio Penacchietti, 5 SP)

**Stock**
- El encargado controla insumos y stock desde la web (Facundo Gregorio, 3 SP)

**Plataforma SaaS**
- La plataforma ve todos los cafés clientes y los activa o suspende (panel superadmin) (Giovani Napoli, 5 SP)
- Términos y política de privacidad visibles para cualquiera (Francisco Domínguez, 3 SP)
- Cada café paga su suscripción mensual con débito automático (Giovani Napoli, 5 SP)
- El café ve el estado de su suscripción y la paga desde la app (Nicolás Spina, 2 SP)

**Pedidos y cocina**
- Los pedidos de apps de delivery se cargan en modo manual (Francisco Domínguez, 3 SP)
- El dueño elige qué apps de delivery usa cada local (Octavio Penacchietti, 2 SP)

**Salida a producción**
- La app está lista para instalarse en un servidor (Docker, HTTPS, backups) (Francisco Domínguez, 5 SP)
- Probamos todo antes de salir: barrido de endpoints, carga y concurrencia (Octavio Penacchietti, 5 SP)

## Avance por épica

| Épica | Terminado | Total |
|---|---|---|
| Base del proyecto | 2 SP | 7 SP |
| Caja y cobros | 33 SP | 33 SP |
| Carta y salón | 21 SP | 34 SP |
| Cuentas y acceso | 33 SP | 33 SP |
| Gestión del negocio | 22 SP | 24 SP |
| Pedidos y cocina | 26 SP | 26 SP |
| Plataforma SaaS | 15 SP | 23 SP |
| Salida a producción | 10 SP | 22 SP |
| Stock | 8 SP | 8 SP |

## Alertas y desvíos

- Sin alertas.

## Costo

Cargado USD 865,40, entregado USD 6.675,00, no utilizado USD 0,00. Detalle en `costos.md`.

## Riesgo de Brooks

🟢 Ruta crítica PR-38 → PR-39 (13 SP). Detalle en `brooks.md`.

## Próxima semana

1. PR-27 — La plataforma administra cafés clientes y planes (superadmin) (Nicolás Spina, 3 SP)
2. PR-38 — El salón se organiza por zonas y el café puede pedir soporte (Facundo Gregorio, 5 SP)
3. PR-33 — El sistema cumple con términos, privacidad y botón de arrepentimiento/baja (Facundo Gregorio, 3 SP)
4. PR-39 — El dueño dibuja el plano del salón y pide soporte con un botón (Nicolás Spina, 8 SP)
5. PR-40 — Cualquiera del equipo entiende el proyecto leyendo el README (Nicolás Spina, 5 SP)
6. PR-34 — Un usuario nuevo aprende la app con un tour guiado (Giovani Napoli, 2 SP)

## Limitaciones de datos

- No hay horas registradas: los costos usan la equivalencia de SP de equipo.md.
- Las semanas 44 a 46 se reconstruyeron desde git (fecha del commit = listo para revisión, merge = terminada); no hay registro de cuándo empezó cada tarea, así que el cycle time es el tiempo en revisión.
- No hay tareas de reuniones ni bloqueos explícitos en el tablero.
- El lead time de los tickets reconstruidos se mide desde el 26/10 (alcance planificado al arrancar), no desde una fecha de creación real.
