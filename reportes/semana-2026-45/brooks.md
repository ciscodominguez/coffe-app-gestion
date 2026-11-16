# Análisis de Ley de Brooks — Semana 45

> "Agregar gente a un proyecto atrasado lo atrasa más." — Fred Brooks, *The Mythical Man-Month* (1975)

## Diagnóstico
🟢 **Sin riesgo** — el grupo llega con la velocidad actual y no hay planes de sumar gente.

## Equipo y comunicación
- Integrantes del grupo del TP: 2 (Francisco, Octavio) — canales: 1 — overhead estimado: no medible (no hay tareas de reunión en el tablero)
- Personas que trabajaron en el repo/tablero esta semana: 5 (Facundo, Francisco, Giovani, Nicolás, Octavio) — canales: 10
- Fórmula: canales = n × (n − 1) ÷ 2. Con +1 persona en el grupo del TP: 3 canales; con +2: 6.

## Trabajo pendiente
| Historia | Puntos | Paralelizable / Secuencial / Crítica | Depende de | Quién sabe |
|---|---|---|---|---|
| PR-34 — Un usuario nuevo aprende la app con un tour guiado | 2 | Paralelizable | — | Octavio, Facundo |
| PR-33 — El sistema cumple con términos, privacidad y botón de arrepentimiento/baja | 3 | Paralelizable | — | Nicolás, Facundo |
| PR-39 — El dueño dibuja el plano del salón y pide soporte con un botón | 8 | Secuencial | PR-38 | Octavio, Facundo |
| PR-38 — El salón se organiza por zonas y el café puede pedir soporte | 5 | Paralelizable | — | Nicolás, Facundo |
| PR-27 — La plataforma administra cafés clientes y planes (superadmin) | 3 | Paralelizable | — | Nicolás, Facundo |
| PR-40 — Cualquiera del equipo entiende el proyecto leyendo el README | 5 | Paralelizable | — | Nicolás |
| P-1 — Un café piloto entra a la app desde internet con HTTPS | 5 | Crítica de conocimiento | — | Francisco |
| P-2 — Las copias nocturnas se restauran bien (prueba real de restauración) | 3 | Secuencial | P-1 | Francisco |
| P-3 — Nos avisa al celular si la app se cae (monitor sobre /actuator/health) | 1 | Secuencial | P-1 | Francisco |
| P-4 — Términos y privacidad con los datos reales del responsable | 2 | Paralelizable | — | Agustín |
| P-5 — 1 o 2 cafés de Mar del Plata usan la app gratis un mes como piloto | 3 | Secuencial | P-1, P-2, P-3 | Francisco |

- Pendiente comprometido: **40 SP** — paralelizable 20 SP, secuencial o crítico 20 SP.
- Ruta crítica: PR-38 → PR-39 (13 pts, ~0.6 semanas a 22.0 SP/semana por persona) — piso mínimo del proyecto.
- Dependencias: las del tablero (campo «Depende de» de cada ticket); las de los tickets reconstruidos se infirieron de git y de los títulos.
- Fuera del alcance comprometido (deseable): P-6 (8 SP), P-7 (13 SP).

```mermaid
flowchart LR
    PR_34["PR-34 · 2 SP<br/>Giovani"]
    PR_33["PR-33 · 3 SP<br/>Facundo"]
    PR_39["PR-39 · 8 SP<br/>Nicolás"]
    PR_38["PR-38 · 5 SP<br/>Facundo"]
    PR_27["PR-27 · 3 SP<br/>Nicolás"]
    PR_40["PR-40 · 5 SP<br/>Nicolás"]
    P_1["P-1 · 5 SP<br/>Francisco"]
    P_2["P-2 · 3 SP<br/>Octavio"]
    P_3["P-3 · 1 SP<br/>Octavio"]
    P_4["P-4 · 2 SP<br/>Agustín"]
    P_5["P-5 · 3 SP<br/>Francisco"]
    PR_38 --> PR_39
    P_1 --> P_2
    P_1 --> P_3
    P_1 --> P_5
    P_2 --> P_5
    P_3 --> P_5
    classDef critica fill:#fde2e1,stroke:#d03b3b,stroke-width:2px
    class PR_38,PR_39 critica
```

## Cuellos de botella y bus factor
| Carpeta | Bus factor | Quién la conoce (más de la mitad de las líneas) |
|---|---|---|
| backend/ | 2 | Nicolás, Facundo |
| deploy/ | 1 ⚠️ | Francisco |
| docs/pruebas/ | 1 ⚠️ | Octavio |
| frontend/ | 2 | Octavio, Facundo |

- Revisiones (merges de PR) acumuladas: Francisco 8, Nicolás 8, Giovani 7, Facundo 7, Octavio 4. Francisco mergea el 24%: si falta, los PRs esperan.
- Facundo tiene 1 tarea(s) pendiente(s) que esperan algo suyo.
- Francisco tiene 3 tarea(s) pendiente(s) que esperan algo suyo.
- Octavio tiene 2 tarea(s) pendiente(s) que esperan algo suyo.

## Simulación: ¿sumar gente?
Base: grupo del TP con 2 desarrolladores a 22.0 SP/semana cada uno (velocidad del grupo 44.0 SP/semana, promedio de las semanas 44, 45). Quedan 5.1 semanas hasta la entrega final (2026-12-14).

| Escenario | Personas | Canales | Capacidad efectiva sem 1–4 (SP) | Fin estimado | vs. hoy |
|---|---|---|---|---|---|
| Equipo actual | 2 | 1 | 44.0 | 15/11/2026 (0.9 sem.) | — |
| +1 persona(s) | 3 | 3 | 40.6 | 16/11/2026 (1.0 sem.) | no cambia (+0.1 sem.) |
| +2 persona(s) | 4 | 6 | 34.7 / 38.2 | 17/11/2026 (1.1 sem.) | no cambia (+0.2 sem.) |

## Recomendaciones
- **Reducir bus factor** en deploy/, docs/pruebas/: pair programming o revisión cruzada (que Octavio acompañe a Francisco en el despliegue, por ejemplo).
- **Bajar el cuello de botella de revisión**: que cualquiera del grupo pueda mergear con una aprobación, en vez de depender de una sola persona.
- Si igual hace falta alguien, conviene **un colaborador que ya conoce el código** (Gio, Facu o Nico): no tiene rampa ni necesita mentor, a diferencia de una persona nueva. Solo en tareas paralelizables.

## Supuestos
- Productividad de una persona nueva: 25 % / 50 % / 75 % / 100 % en sus semanas 1 a 4.
- Mentoría: 20 % del tiempo de un integrante durante las primeras 2 semanas.
- Overhead: 5 % menos de productividad del equipo por cada canal nuevo.
- La persona nueva solo toma trabajo paralelizable.
- Velocidad = SP cerrados por el grupo del TP; Agustín (PO) cuenta para la comunicación pero no suma SP de código.
- «Quién sabe» y bus factor salen de las líneas agregadas por autor en cada carpeta (git log de main).
- Fuente: gestion/plane/tickets.json (tablero reconstruido desde git).
