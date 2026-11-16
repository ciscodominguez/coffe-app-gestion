"""Funciones compartidas por el cargador de Plane, el normalizador y las skills."""
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

# Que los acentos y emojis no rompan la consola de Windows.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

RAIZ = Path(__file__).resolve().parent.parent
EQUIPO_MD = RAIZ / "equipo.md"
REPORTES = RAIZ / "reportes"


def leer_tabla(md, titulo):
    """Devuelve la tabla markdown que sigue al encabezado `## titulo` como lista de dicts."""
    bloque = re.split(r"^## ", md, flags=re.M)
    for b in bloque:
        if b.strip().lower().startswith(titulo.lower()):
            filas = [l.strip() for l in b.splitlines() if l.strip().startswith("|")]
            if len(filas) < 2:
                return []
            cab = [c.strip() for c in filas[0].strip("|").split("|")]
            datos = []
            for f in filas[2:]:
                celdas = [c.strip() for c in f.strip("|").split("|")]
                datos.append(dict(zip(cab, celdas)))
            return datos
    raise ValueError(f"No encontré la sección '## {titulo}' en equipo.md")


def leer_bullets(md, titulo):
    """'- Clave: valor' de una sección, como dict (clave en minúsculas)."""
    for b in re.split(r"^## ", md, flags=re.M):
        if b.strip().lower().startswith(titulo.lower()):
            out = {}
            for l in b.splitlines():
                m = re.match(r"^- ([^:]+):\s*(.*)$", l.strip())
                if m:
                    out[m.group(1).strip().lower()] = m.group(2).strip()
            return out
    return {}


def _fecha(texto):
    m = re.search(r"\d{4}-\d{2}-\d{2}", texto or "")
    return m.group(0) if m else None


def _numero(texto, defecto=0.0):
    m = re.search(r"\d+(?:[.,]\d+)?", texto or "")
    return float(m.group(0).replace(",", ".")) if m else defecto


def leer_equipo(ruta=EQUIPO_MD):
    """Lee equipo.md en el formato de la cátedra (secciones Proyecto, Integrantes, Costos, ...)."""
    md = Path(ruta).read_text(encoding="utf-8")
    proyecto = leer_bullets(md, "Proyecto")
    costos = leer_bullets(md, "Costos")
    integrantes = []
    for f in leer_tabla(md, "Integrantes"):
        usuario = f.get("Usuario en tablero", "")
        integrantes.append(dict(
            clave=f.get("Clave") or f["Nombre"].split()[0].lower(),
            nombre=f["Nombre"], rol=f.get("Rol", ""),
            rol_tp=(f.get("Grupo TP") or "integrante").lower(),
            email_plane=usuario if "@" in usuario else "",
            git_autores=[a.strip() for a in f.get("Usuario git", "").split(",") if a.strip() not in ("", "—", "-")],
            dedicacion_pct=_numero(f.get("Dedicación"), 100.0),
            alta=date.fromisoformat(_fecha(f.get("Ingreso al proyecto")) or "1900-01-01"),
        ))
    entregas = re.findall(r"\d{4}-\d{2}-\d{2}", proyecto.get("entregas parciales", ""))
    final = _fecha(proyecto.get("entrega final"))
    sp_h = re.search(r"1\s*SP\s*=\s*(\d+(?:[.,]\d+)?)\s*h", costos.get("equivalencia de story point (opcional)", ""))
    params = dict(
        nombre=proyecto.get("nombre", "").split("—")[0].strip(),
        costo_mensual_usd=_numero(costos.get("costo mensual por integrante"), 3000.0),
        horas_mes=_numero(costos.get("horas laborales por mes"), 160.0),
        horas_por_sp=float(sp_h.group(1).replace(",", ".")) if sp_h else None,
        fecha_inicio=_fecha(proyecto.get("fecha de inicio")),
        entregas=sorted(set(entregas + ([final] if final else []))),
        fecha_entrega=final,
        plane_slug=proyecto.get("slug de plane", ""),
        plane_proyecto=proyecto.get("proyecto en plane", ""),
        repo=proyecto.get("repositorio", "").split()[0] if proyecto.get("repositorio") else "",
    )
    infra = []
    for f in leer_tabla(md, "Infraestructura"):
        infra.append(dict(servicio=f.get("Servicio", ""), uso=f.get("Plan", ""),
                          costo_mensual_usd=_numero(f.get("Costo mensual USD")),
                          alternativa_gratuita=f.get("Alternativa gratuita", "")))
    objetivos = []
    for f in leer_tabla(md, "Objetivos"):
        objetivos.append(dict(id=f.get("Id"), historia=f.get("Historia"), puntos=_numero(f.get("Puntos")),
                              entrega=f.get("Entrega")))
    return dict(integrantes=integrantes, params=params, infra=infra, objetivos=objetivos)


def activos(equipo, hasta):
    """Integrantes que ya estaban en el tablero al `hasta` (date)."""
    return [p for p in equipo["integrantes"] if p["alta"] <= hasta]


def autor_a_clave(equipo):
    m = {}
    for p in equipo["integrantes"]:
        for a in p["git_autores"]:
            m[a.lower()] = p["clave"]
    return m


def semana_de(fecha):
    if isinstance(fecha, str):
        fecha = datetime.fromisoformat(fecha).date()
    a, s, _ = fecha.isocalendar()
    return f"semana-{a}-{s:02d}"


def limites_semana(clave):
    """'semana-2026-45' -> (lunes, domingo)."""
    _, a, s = clave.split("-")
    lunes = date.fromisocalendar(int(a), int(s), 1)
    return lunes, lunes + timedelta(days=6)


def semanas_entre(desde, hasta):
    out, d = [], desde
    while d <= hasta:
        k = semana_de(d)
        if k not in out:
            out.append(k)
        d += timedelta(days=1)
    return out


def dias_habiles(desde, hasta):
    """Días hábiles (lun-vie) en (desde, hasta]."""
    n, d = 0, desde
    while d < hasta:
        d += timedelta(days=1)
        if d.weekday() < 5:
            n += 1
    return n


def usd(x):
    s = f"{x:,.2f}"
    return "USD " + s.replace(",", "X").replace(".", ",").replace("X", ".")


def guardar_json(ruta, datos):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def leer_json(ruta, defecto=None):
    ruta = Path(ruta)
    if not ruta.exists():
        return defecto
    return json.loads(ruta.read_text(encoding="utf-8"))


def velocidades(tareas, semana, claves=None, n=3, inicio=None):
    """SP cerrados por semana en las `n` semanas que terminan en `semana` (incluida).

    Si se pasan `claves`, solo cuenta las tareas de esos responsables. Si se pasa `inicio`
    (date), no cuenta semanas anteriores al arranque del proyecto."""
    lunes, _ = limites_semana(semana)
    semanas = [semana_de(lunes - timedelta(days=7 * i)) for i in reversed(range(n))]
    if inicio is not None:
        semanas = [s for s in semanas if limites_semana(s)[1] >= inicio] or [semana]
    out = {s: 0.0 for s in semanas}
    for t in tareas:
        if t["estado"] != "Done" or not t.get("fin"):
            continue
        if claves is not None and t.get("responsable") not in claves:
            continue
        s = semana_de(t["fin"][:10])
        if s in out:
            out[s] += t.get("sp") or 0
    return out
