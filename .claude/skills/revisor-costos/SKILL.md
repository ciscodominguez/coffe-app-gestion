---
name: revisor-costos
description: Revisa los costos semanales del proyecto del grupo — cuánto le costó a la empresa cada integrante que trabajó esa semana, cuánto de ese costo se convirtió en trabajo terminado y dónde se podría optimizar. Usar cuando se pida revisión, análisis o informe de costos de la semana, del sprint o del proyecto.
---

# Revisor de Costos

Actuás como **controller de costos de un proyecto de software**. Tu trabajo es mirar lo que hizo el grupo durante la semana, traducirlo a plata como lo vería una empresa y señalar con datos dónde se gastó de más y qué se podría hacer distinto. No juzgás personas: juzgás decisiones de trabajo.

## Parámetros de costo

Por defecto (se pueden sobrescribir en `equipo.md`):

| Parámetro | Valor | Cómo sale |
|---|---|---|
| Costo mensual por integrante | **3.000 USD** | costo empresa promedio |
| Horas laborales por mes | 160 h | 40 h × 4 semanas |
| Costo por hora | **18,75 USD** | 3.000 / 160 |
| Costo semanal por integrante | **692,31 USD** | 3.000 × 12 / 52 |

Si `equipo.md` indica una **dedicación** por integrante (ej. 25 %), el costo semanal de esa persona es `692,31 × dedicación` y su capacidad es `40 h × dedicación`. Si no hay dedicación indicada, asumí 100 % y decilo en el informe.

## Datos de entrada

1. **Configuración del grupo:** leé `equipo.md` en la raíz del proyecto (integrantes, dedicación, usuario en el tablero, objetivos, fecha de entrega, costos de infraestructura). Si no existe, pedíselo al alumno antes de seguir.
2. **Tareas de la semana**, en este orden de prioridad:
   - Si ya existe `reportes/semana-AAAA-WW/tareas-normalizadas.json` (lo genera cualquiera de las skills del curso), usalo y no vuelvas a pedir los datos.
   - Si hay un conector de Jira, ClickUp, Plane o Trello disponible, traé las tareas del proyecto con movimiento en la semana.
   - Si no, buscá un export (CSV o JSON) en la carpeta `datos/`.
   - Como complemento, `git log --since --until --author` sirve para validar quién trabajó y cuándo.
3. Normalizá las tareas a este formato y guardalas en `reportes/semana-AAAA-WW/tareas-normalizadas.json` si no existía:

```json
{ "id": "", "titulo": "", "tipo": "historia|tarea|bug|reunion|investigacion",
  "estado": "pendiente|en_curso|en_revision|bloqueada|terminada",
  "asignado": "", "story_points": 0, "estimacion_h": 0, "horas_registradas": 0,
  "creada": "", "iniciada": "", "terminada": "", "ultimo_movimiento": "",
  "reaperturas": 0, "dependencias": [], "etiquetas": [] }
```

**Semana a analizar:** la que pida el alumno; si no dice nada, la última semana cerrada (lunes a domingo). Usá el número de semana ISO para la carpeta.

## Cálculos

Para cada integrante y para el grupo:

- **Costo cargado** = costo semanal × dedicación. Es lo que la empresa paga, se trabaje o no.
- **Costo imputado** = horas registradas × 18,75.
- **Costo entregado** = horas en tareas que pasaron a *terminada* esa semana × 18,75.
- **Costo en curso** = horas en tareas que siguen abiertas.
- **Capacidad no utilizada** = costo cargado − costo imputado.
- **Costo por story point** = costo cargado del grupo / story points terminados.
- **Desvío de estimación** por tarea = (horas registradas − estimación) / estimación.
- **Infraestructura**: sumá aparte lo que figure en `equipo.md` (hosting, dominios, servicios pagos), prorrateado a la semana.

Si una tarea no tiene horas registradas, **no las inventes**: marcala como "sin registro", excluila del costo imputado y contala en un indicador de calidad de datos. Si no hay horas en ninguna tarea, estimá con story points solo si `equipo.md` define una equivalencia (ej. 1 SP = 4 h) y aclaralo como supuesto.

## Dónde buscar optimizaciones

Revisá estos patrones y reportá solo los que aparezcan, con el costo en USD que representan:

1. **Retrabajo**: tareas reabiertas o bugs sobre funcionalidades de la misma semana → costo de las horas repetidas.
2. **Subestimación crónica**: tareas que superaron su estimación en más de 50 %. Si se repite en una persona o tipo de tarea, es un problema de estimación, no de ejecución.
3. **Trabajo bloqueado**: horas cargadas en tareas que quedaron bloqueadas; costo de la espera.
4. **WIP alto**: más de 2 tareas en curso por persona → costo del cambio de contexto (estimá 15 % de las horas de esa persona).
5. **Capacidad ociosa**: integrantes con mucho costo cargado y poco imputado: ¿faltan tareas asignadas, falta registro o hay sobrecarga en otros?
6. **Desbalance**: una persona con más del 40 % de las horas del grupo → riesgo y cuello de botella.
7. **Reuniones y coordinación**: horas en reuniones sobre el total; arriba de 20 % es para revisar.
8. **Trabajo fuera de alcance**: tareas que no se vinculan con ninguna historia del backlog acordado.
9. **Infraestructura**: servicios pagos cuando existe un plan gratuito equivalente (Railway, Vercel, Render, Cloudflare Tunnel, etc.), ambientes prendidos sin uso, duplicados.

Cada recomendación tiene: **qué pasó → cuánto costó → qué hacer → ahorro estimado por semana**.

## Salida

Generá `reportes/semana-AAAA-WW/costos.md` con esta estructura:

```markdown
# Revisión de costos — Semana WW (dd/mm al dd/mm)

## Resumen
- Costo cargado del grupo: USD X
- Costo entregado (trabajo terminado): USD X (Y %)
- Capacidad no utilizada: USD X
- Costo por story point: USD X
- Infraestructura (semana): USD X
- Calidad de datos: N tareas sin horas registradas

## Costo por integrante
| Integrante | Dedicación | Costo cargado | Horas | Costo imputado | Entregado | No utilizado |

## Costo por tarea (top 10 por costo)
| Tarea | Responsable | Estimado | Real | Desvío | Costo USD | Estado |

## Oportunidades de optimización
1. **[Patrón]** — qué pasó, costo USD, recomendación, ahorro estimado/semana

## Supuestos
```

Además, agregá la semana a `reportes/historico-costos.json` (sin pisar las anteriores) con los totales del resumen, para mostrar la evolución en el TP final.

Cerrá con un párrafo corto en lenguaje de negocio: si fueran una empresa, ¿lo que se pagó esta semana se justifica con lo que se entregó?

## Reglas

- Montos en USD con dos decimales; mostrá la cuenta cuando no sea obvia.
- Nunca inventes horas, tareas ni costos. Lo que falta se reporta como faltante.
- Sin juicios personales. Hablá de tareas, procesos y decisiones.
- Si el alumno pide otra moneda u otro costo mensual, recalculá todo con ese valor.
