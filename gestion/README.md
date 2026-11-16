# Gestión del proyecto (TP de Gestión de Desarrollo de Software)

Todo lo que pide la clase "Del tablero a los agentes: Plane + skills de Claude", aplicado a COFFE_APP.

```
equipo.md                          ← datos del grupo (lo leen las skills y los scripts)
.claude/skills/
  revisor-costos/SKILL.md          ← skills de la cátedra (sin cambios)
  analista-brooks/SKILL.md
  product-owner/SKILL.md
  arquitecto-c4/SKILL.md           ← tarea: skill de arquitectura C4
gestion/
  plane/generar_tickets.py         ← reconstruye los tickets desde el historial de git
  plane/tickets.json               ← el tablero reconstruido (55 tickets)
  plane/cargar_plane.py            ← lo carga en Plane por API
  normalizar.py                    ← reportes/<semana>/tareas-normalizadas.json
  analisis/costos.py               ← cálculos de revisor-costos
  analisis/brooks.py               ← cálculos de analista-brooks
  analisis/po.py                   ← cálculos y HTML de product-owner
  c4/arquitecto_c4.py              ← analizador de la skill arquitecto-c4
reportes/                          ← salida de las skills, una carpeta por semana
docs/arquitectura/                 ← diagramas C4 + changelog
```

Requisitos: Python 3.9 o más nuevo y `pip install requests` (solo para hablar con Plane).

## 1. Alta en Plane (una vez)

1. En https://app.plane.so/gestion-de-desarrollo-de-soft/ crear el proyecto **COFFE_APP** e invitar al grupo
   (y, si quieren que los tickets queden asignados, también a Gio, Facu y Nico).
2. En *Project settings → Features* activar **Cycles** y **Modules** (y **Estimates**, aunque el script
   guarda los story points como etiqueta `sp:N` porque la API de Plane no permite cargar estimaciones).
3. Completar en `equipo.md` el mail de Plane de Fran y de Agustín (columna *Usuario en tablero*).

## 2. Token y prueba (paso 2 de la clase)

*Profile Settings → Personal Access Tokens → Add personal access token*. Vencimiento: fin de la cursada.
Es una contraseña: **nunca** va al repo.

```bash
# Linux / macOS / Git Bash
export PLANE_API_KEY="plane_api_..."
export PLANE_SLUG="gestion-de-desarrollo-de-soft"
curl -H "X-API-Key: $PLANE_API_KEY" https://api.plane.so/api/v1/workspaces/$PLANE_SLUG/projects/

# Windows PowerShell
$env:PLANE_API_KEY="plane_api_..."
python gestion/plane/cargar_plane.py --probar
```

## 3. Cargar el tablero

```bash
python gestion/plane/cargar_plane.py --simular   # muestra los 55 tickets, sin tocar Plane
python gestion/plane/cargar_plane.py             # crea ciclos (S44–S48), módulos, etiquetas e issues
```

Se puede correr de nuevo sin duplicar nada (cada issue lleva `external_id`). El mapeo clave → id de Plane
queda en `gestion/plane/ids-plane.json`.

## 4. Correr las skills cada lunes (paso 3 de la clase)

Con Claude Code, desde la raíz del repo:

```
claude "Analizá la última semana cerrada. Leé equipo.md y ejecutá en orden:
  1) revisor-costos
  2) analista-brooks
  3) product-owner, sumando costos y Brooks al reporte-po.html.
Resumime semáforo, costo, ahorro y riesgo, con las rutas."
```

Las skills usan los scripts de `gestion/` para que los números salgan siempre igual (ver `CLAUDE.md`).
A mano, lo mismo es:

```bash
python gestion/normalizar.py --semana semana-2026-47
python gestion/analisis/costos.py --semana semana-2026-47
python gestion/analisis/brooks.py --semana semana-2026-47
python gestion/analisis/po.py --semana semana-2026-47
```

Con `PLANE_API_KEY` definido, `normalizar.py` lee el tablero en vivo; sin el token, usa
`gestion/plane/tickets.json`.

## 5. Arquitectura C4 (tarea)

```bash
python gestion/c4/arquitecto_c4.py     # actualiza docs/arquitectura/ con lo que cambió desde la última corrida
```

## Rutina del grupo (postrequisito)

- Crear el ticket en Plane antes de empezar a codear.
- Mover el estado cuando cambia el trabajo y cerrar lo terminado el mismo día.
- Poner el ID del issue en cada commit (por ejemplo `feat: ... [COFFE-48]`).
- Lunes: las tres skills + `arquitecto-c4`.
