# Análisis de Ley de Brooks — Semana 47

> "Agregar gente a un proyecto atrasado lo atrasa más." — Fred Brooks, *The Mythical Man-Month* (1975)

## Diagnóstico
🟡 **Riesgo** — 68% del trabajo pendiente es secuencial o crítico de conocimiento.

## Equipo y comunicación
- Integrantes del grupo del TP: 3 (Agustín, Francisco, Octavio) — canales: 3 — overhead estimado: no medible (no hay tareas de reunión en el tablero)
- Equipo con trabajo pendiente: 3 (Francisco, Octavio, Agustín) — canales: 3
- Personas que trabajaron en el repo/tablero esta semana: 2 (Agustín, Francisco) — canales: 1
- Fórmula: canales = n × (n − 1) ÷ 2. Con +1 persona en el grupo del TP: 6 canales; con +2: 10.

- Ingresos recientes (últimas 4 semanas): Agustín — entra como gestión (PO), no como desarrollo, así que no consume rampa sobre el código.

## Trabajo pendiente
| Historia | Puntos | Paralelizable / Secuencial / Crítica | Depende de | Quién sabe |
|---|---|---|---|---|
| G-4 — equipo.md completo: integrantes, dedicación, objetivos, fechas y costos de infra | 1 | Paralelizable | — | Agustín |
| G-5 — El PO tiene costos, Brooks y semáforo de cada semana (3 skills corriendo) | 3 | Secuencial | G-4 | Agustín |
| G-6 — La arquitectura C4 se mantiene sola con la skill arquitecto-c4 | 3 | Paralelizable | — | Octavio |
| G-7 — Cada commit lleva el ID del issue de Plane (hook commit-msg) | 1 | Paralelizable | — | Francisco |
| P-1 — Un café piloto entra a la app desde internet con HTTPS | 5 | Crítica de conocimiento | — | Francisco |
| P-2 — Las copias nocturnas se restauran bien (prueba real de restauración) | 3 | Secuencial | P-1 | Francisco |
| P-3 — Nos avisa al celular si la app se cae (monitor sobre /actuator/health) | 1 | Secuencial | P-1 | Francisco |
| P-4 — Términos y privacidad con los datos reales del responsable | 2 | Paralelizable | — | Agustín |
| P-5 — 1 o 2 cafés de Mar del Plata usan la app gratis un mes como piloto | 3 | Secuencial | P-1, P-2, P-3 | Francisco |

- Pendiente comprometido: **22 SP** — paralelizable 7 SP, secuencial o crítico 15 SP.
- Ruta crítica: P-1 → P-2 → P-5 (11 pts, ~0.6 semanas a 18.3 SP/semana por persona) — piso mínimo del proyecto.
- Dependencias: las del tablero (campo «Depende de» de cada ticket); las de los tickets reconstruidos se infirieron de git y de los títulos.
- Fuera del alcance comprometido (deseable): P-6 (8 SP), P-7 (13 SP).

```mermaid
flowchart LR
    G_4["G-4 · 1 SP<br/>Agustín"]
    G_5["G-5 · 3 SP<br/>Agustín"]
    G_6["G-6 · 3 SP<br/>Octavio"]
    G_7["G-7 · 1 SP<br/>Francisco"]
    P_1["P-1 · 5 SP<br/>Francisco"]
    P_2["P-2 · 3 SP<br/>Octavio"]
    P_3["P-3 · 1 SP<br/>Octavio"]
    P_4["P-4 · 2 SP<br/>Agustín"]
    P_5["P-5 · 3 SP<br/>Francisco"]
    G_4 --> G_5
    P_1 --> P_2
    P_1 --> P_3
    P_1 --> P_5
    P_2 --> P_5
    P_3 --> P_5
    classDef critica fill:#fde2e1,stroke:#d03b3b,stroke-width:2px
    class P_1,P_2,P_5 critica
```

## Cuellos de botella y bus factor
| Carpeta | Bus factor | Quién la conoce (más de la mitad de las líneas) |
|---|---|---|
| backend/ | 2 | Nicolás, Facundo |
| deploy/ | 1 ⚠️ | Francisco |
| docs/pruebas/ | 1 ⚠️ | Octavio |
| frontend/ | 2 | Octavio, Facundo |

- Revisiones (merges de PR) acumuladas: Francisco 11, Giovani 9, Nicolás 8, Facundo 7, Octavio 5. Francisco mergea el 28%: si falta, los PRs esperan.
- Agustín tiene 1 tarea(s) pendiente(s) que esperan algo suyo.
- Francisco tiene 3 tarea(s) pendiente(s) que esperan algo suyo.
- Octavio tiene 2 tarea(s) pendiente(s) que esperan algo suyo.

## Simulación: ¿sumar gente?
Base: 2 desarrolladores con trabajo pendiente (Francisco, Octavio) a 18.3 SP/semana cada uno (velocidad del equipo 36.7 SP/semana, promedio de las semanas 45, 46, 47). Quedan 3.1 semanas hasta la entrega final (2026-12-14).

| Escenario | Personas | Canales | Capacidad efectiva sem 1–4 (SP) | Fin estimado | vs. hoy |
|---|---|---|---|---|---|
| Equipo actual | 3 | 3 | 36.7 | 27/11/2026 (0.6 sem.) | — |
| +1 persona(s) | 4 | 6 | 31.9 | 28/11/2026 (0.7 sem.) | no cambia (+0.1 sem.) |
| +2 persona(s) | 5 | 10 | 25.0 | 29/11/2026 (0.9 sem.) | alarga (+0.3 sem.) |

## Recomendaciones
- **Reducir bus factor** en deploy/, docs/pruebas/: pair programming o revisión cruzada (que Octavio acompañe a Francisco en el despliegue, por ejemplo).
- **Bajar el cuello de botella de revisión**: que cualquiera del grupo pueda mergear con una aprobación, en vez de depender de una sola persona.
- Si igual hace falta alguien, conviene **un colaborador que ya conoce el código** (Gio, Facu o Nico): no tiene rampa ni necesita mentor, a diferencia de una persona nueva. Solo en tareas paralelizables.

## Supuestos
- Productividad de una persona nueva: 25 % / 50 % / 75 % / 100 % en sus semanas 1 a 4.
- Mentoría: 20 % del tiempo de un integrante durante las primeras 2 semanas.
- Overhead: 5 % menos de productividad del equipo por cada canal nuevo.
- La persona nueva solo toma trabajo paralelizable.
- Velocidad por desarrollador = SP cerrados ÷ desarrolladores que cerraron algo, promedio de 3 semanas. El equipo de la simulación es el grupo del TP más los colaboradores con tareas pendientes; Agustín (PO) cuenta para la comunicación pero no suma SP de código.
- «Quién sabe» y bus factor salen de las líneas agregadas por autor en cada carpeta (git log de main).
- Fuente: gestion/plane/tickets.json (tablero reconstruido desde git).
