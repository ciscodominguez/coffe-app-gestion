# CLAUDE.md — COFFE_APP

## Skills de gestión (TP de Gestión de Desarrollo de Software)

Las skills `revisor-costos`, `analista-brooks` y `product-owner` (en `.claude/skills/`) son las de la
cátedra. En este repo los cálculos ya están implementados en scripts, para que cada corrida dé los mismos
números. Al ejecutar cualquiera de esas skills:

1. Si no existe `reportes/<semana>/tareas-normalizadas.json`, generarlo con
   `python gestion/normalizar.py --semana <semana-AAAA-WW>` (lee Plane si está `PLANE_API_KEY`; si no,
   `gestion/plane/tickets.json`).
2. Correr el script de la skill:
   - revisor-costos → `python gestion/analisis/costos.py --semana <semana>`
   - analista-brooks → `python gestion/analisis/brooks.py --semana <semana>`
   - product-owner → `python gestion/analisis/po.py --semana <semana>` (después de los otros dos, así suma
     costos y Brooks al `reporte-po.html`)
3. Leer el `.md` generado, verificarlo contra lo que pide la SKILL.md y completar lo que el script no
   puede saber (contexto, explicación de una alerta, una recomendación más concreta). No cambiar números
   a mano: si un cálculo está mal, corregir el script.

`equipo.md` en la raíz tiene integrantes, dedicación, fechas de entrega, costos e infraestructura.

## Arquitectura

La skill `arquitecto-c4` mantiene `docs/arquitectura/` con `python gestion/c4/arquitecto_c4.py`.
Los diagramas no se editan a mano.

## Convenciones

- Cada commit lleva el ID del issue de Plane.
- El token de Plane va en la variable de entorno `PLANE_API_KEY`; nunca en el repo.
