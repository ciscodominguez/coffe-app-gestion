#!/usr/bin/env python3
"""Genera reportes/semana-AAAA-WW/tareas-normalizadas.json con el esquema de las skills de la cátedra.

Fuentes:
  - Tablero: Plane por API (si está PLANE_API_KEY) o gestion/plane/tickets.json (reconstruido desde git).
  - Repo: commits de la semana (git log), para validar quién trabajó y cuándo.

El estado de cada tarea se calcula AL CIERRE de la semana analizada (domingo, o hoy si la semana
está en curso). Una tarea que hoy está terminada pero se mergeó después de ese domingo figura
"en_revision" o "en_curso" en esa semana. Así se puede analizar cualquier semana pasada.

Esquema de cada tarea (el de revisor-costos) + campos extra del grupo:
  id, titulo, tipo, estado, asignado, story_points, estimacion_h, horas_registradas, creada, iniciada,
  terminada, ultimo_movimiento, reaperturas, dependencias, etiquetas
  extra: historia, area, entrega, revisor, pr, commit, listo_revision, origen, codigo_plane,
         estado_actual, cerrada_en_semana

Uso (desde la raíz del repo):
    python gestion/normalizar.py                          # última semana cerrada
    python gestion/normalizar.py --semana semana-2026-45
    python gestion/normalizar.py --fuente tickets         # no llama a Plane
"""
import argparse
import os
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import (RAIZ, REPORTES, autor_a_clave, guardar_json, leer_equipo, leer_json,  # noqa: E402
                   limites_semana, semana_de)

TICKETS = RAIZ / "gestion" / "plane" / "tickets.json"
GRUPO = {"backlog": "Backlog", "unstarted": "Todo", "started": "In Progress", "completed": "Done",
         "cancelled": "Cancelled"}


def d(x):
    return datetime.fromisoformat(x[:10]).date() if x else None


def tareas_de_tickets():
    """tickets.json -> formato intermedio (estado del tablero hoy)."""
    out = []
    for t in leer_json(TICKETS)["tickets"]:
        out.append(dict(
            id=t["clave"], titulo=t["titulo"], tipo=t.get("tipo", "tarea"), estado_tablero=t["estado"],
            asignado=t["responsable"], story_points=t["sp"], creada=t.get("creado"), iniciada=t.get("inicio"),
            terminada=t.get("fin") if t["estado"] == "Done" else None, actualizada=None,
            dependencias=t.get("deps", []), historia=t["historia"], area=t["modulo"], entrega=t.get("entrega"),
            revisor=t.get("revisor"), pr=t.get("pr"), commit=t.get("commit"), listo_revision=t.get("listo_revision"),
            origen=t["origen"], codigo_plane=None, fin_plan=t.get("fin"), ciclo=t.get("ciclo"),
            etiquetas=[t["modulo"].lower(), f"sp:{t['sp']}", f"origen:{t['origen']}"],
        ))
    return out


def tareas_de_plane(eq):
    import requests  # solo en este modo
    prm = eq["params"]
    base = os.environ.get("PLANE_BASE", "https://api.plane.so/api/v1").rstrip("/")
    slug = os.environ.get("PLANE_SLUG", prm["plane_slug"])
    s = requests.Session()
    s.headers["X-API-Key"] = os.environ["PLANE_API_KEY"]

    def lista(ruta, **params):
        out, cursor = [], None
        while True:
            p = dict(params, per_page=100, **({"cursor": cursor} if cursor else {}))
            r = s.get(f"{base}/workspaces/{slug}/{ruta}", params=p, timeout=30)
            r.raise_for_status()
            j = r.json()
            if isinstance(j, list):
                return j
            out += j.get("results", [])
            if not j.get("next_page_results"):
                return out
            cursor = j["next_cursor"]

    proy = next(p for p in lista("projects/") if p["name"].lower() == prm["plane_proyecto"].lower())
    P, ident = f"projects/{proy['id']}", proy.get("identifier", "")
    estados = {e["id"]: GRUPO.get(e["group"], "Todo") for e in lista(f"{P}/states/")}
    etiquetas = {l["id"]: l["name"] for l in lista(f"{P}/labels/")}
    por_mail = {p["email_plane"].lower(): p["clave"] for p in eq["integrantes"] if p["email_plane"]}
    por_nombre = {p["nombre"].split()[0].lower(): p["clave"] for p in eq["integrantes"]}
    miembro = {}
    for m in lista("members/"):
        m = m.get("member", m) if isinstance(m.get("member"), dict) else m
        miembro[m["id"]] = por_mail.get((m.get("email") or "").lower()) or por_nombre.get(
            (m.get("first_name") or m.get("display_name") or "").lower())
    ciclo_de = {}
    for c in lista(f"{P}/cycles/"):
        if c.get("start_date"):
            for i in lista(f"{P}/cycles/{c['id']}/cycle-issues/"):
                ciclo_de[i.get("id") or i.get("issue")] = semana_de(d(c["start_date"]))
    modulo_de = {}
    for m in lista(f"{P}/modules/"):
        for i in lista(f"{P}/modules/{m['id']}/module-issues/"):
            modulo_de[i.get("id") or i.get("issue")] = m["name"]
    base_git = {t["id"]: t for t in tareas_de_tickets()}
    # Los issues cargados desde la sesión web no tienen external_id: se reconocen por gestion/plane/ids-plane.json.
    clave_de_id = {v["id"]: k for k, v in (leer_json(RAIZ / "gestion" / "plane" / "ids-plane.json", {}) or {}).items()}
    out = []
    issues = lista(f"{P}/issues/")
    # Los issues de ejemplo que Plane crea con el proyecto ("Welcome to Plane", etc.) no son del equipo:
    # se ignoran los que no están en el mapeo y se crearon antes que el primer ticket nuestro.
    creados = [i.get("created_at") or "" for i in issues if i["id"] in clave_de_id]
    umbral = min(creados) if creados else ""
    for i in issues:
        if i["id"] not in clave_de_id and not i.get("external_id") and (i.get("created_at") or "") < umbral:
            continue
        nombres = [etiquetas.get(x, "") for x in i.get("labels", [])]
        sp = next((int(n[3:]) for n in nombres if n.startswith("sp:") and n[3:].isdigit()), None)
        codigo = f"{ident}-{i['sequence_id']}"
        clave = i.get("external_id") or clave_de_id.get(i["id"]) or codigo
        previo = base_git.get(clave, {})
        asignado = next((miembro.get(a) for a in (i.get("assignees") or i.get("assignee_ids") or [])
                         if miembro.get(a)), None) or next(
            (n.split(":", 1)[1] for n in nombres if n.startswith("autor:")), None) or previo.get("asignado")
        estado = estados.get(i["state"], "Todo")
        terminada = i.get("target_date") or (i.get("completed_at") or "")[:10] or None
        out.append(dict(
            id=clave, titulo=i["name"], tipo=previo.get("tipo", "tarea"), estado_tablero=estado, asignado=asignado,
            story_points=sp if sp is not None else previo.get("story_points"),
            creada=previo.get("creada") or (i.get("created_at") or "")[:10],
            iniciada=i.get("start_date") or previo.get("iniciada"),
            terminada=terminada if estado == "Done" else None,
            actualizada=(i.get("updated_at") or "")[:10] or None,
            dependencias=previo.get("dependencias", []),
            historia=modulo_de.get(i["id"], previo.get("historia", "Sin módulo")),
            area=previo.get("area") or next((n.capitalize() for n in nombres if n in
                                             {"backend", "frontend", "infra", "calidad", "docs", "gestión"}), None),
            entrega=previo.get("entrega"), revisor=previo.get("revisor"), pr=previo.get("pr"),
            commit=previo.get("commit"), listo_revision=previo.get("listo_revision"),
            origen=previo.get("origen", "plane"), codigo_plane=codigo, fin_plan=i.get("target_date"),
            ciclo=ciclo_de.get(i["id"], previo.get("ciclo")),
            etiquetas=nombres,
        ))
    return out


def estado_al(t, corte):
    """Estado (vocabulario de la skill) que tenía la tarea al final del día `corte`."""
    ini, fin, lr = d(t.get("iniciada")), d(t.get("terminada")), d(t.get("listo_revision"))
    est = t["estado_tablero"]
    if est == "Cancelled":
        return "cancelada"
    if est == "Done":
        if fin and fin <= corte:
            return "terminada"
        if lr and lr <= corte:
            return "en_revision"
        return "en_curso" if ini and ini <= corte else "pendiente"
    if est == "In Progress":
        return "en_curso" if ini and ini <= corte else "pendiente"
    return "pendiente"


def commits_de_semana(eq, desde, hasta):
    m = autor_a_clave(eq)
    salida = subprocess.run(
        ["git", "log", "--all", "--no-merges", f"--since={desde}T00:00:00-03:00",
         f"--until={hasta}T23:59:59-03:00", "--format=@@%h|%an|%aI|%s", "--shortstat"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=RAIZ, check=True).stdout
    vistos, out, actual = {}, [], None
    for linea in salida.splitlines():
        if linea.startswith("@@"):
            h, an, ad, s = linea[2:].split("|", 3)
            autor = m.get(an.lower(), an)
            clave = (autor, ad, s)
            actual = None
            if clave in vistos:
                # Mismo autor, fecha y mensaje con otro hash: el commit se volvió a aplicar
                # (reescritura de historia). Se cuenta una vez y se marca como retrabajo.
                vistos[clave]["copias"].append(h)
                continue
            actual = dict(hash=h, autor=autor, fecha=ad, asunto=s, lineas=0, copias=[])
            vistos[clave] = actual
            out.append(actual)
        elif "insertion" in linea and actual is not None:
            actual["lineas"] = int(linea.split("insertion")[0].split(",")[-1].strip().split()[0])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--semana", help="semana-AAAA-WW (por defecto, la última cerrada)")
    ap.add_argument("--fuente", choices=["auto", "plane", "tickets"], default="auto")
    a = ap.parse_args()
    eq = leer_equipo()
    hoy = date.today()
    semana = a.semana or semana_de(hoy - timedelta(days=7))
    desde, hasta = limites_semana(semana)
    corte = min(hasta, hoy)
    fuente = a.fuente if a.fuente != "auto" else ("plane" if os.environ.get("PLANE_API_KEY") else "tickets")
    crudas = tareas_de_plane(eq) if fuente == "plane" else tareas_de_tickets()

    tareas = []
    for t in crudas:
        if t.get("creada") and d(t["creada"]) > corte:
            continue  # todavía no existía en el tablero
        estado = estado_al(t, corte)
        # Solo cuentan cambios de estado reales: la fecha de inicio de un ticket que sigue "pendiente" es un plan,
        # no un movimiento.
        arranco = estado != "pendiente"
        movs = [d(t.get("iniciada")) if arranco else None, d(t.get("listo_revision")),
                d(t.get("terminada")) if estado == "terminada" else None,
                d(t.get("actualizada")) if arranco else None]
        movs = [m for m in movs if m and m <= corte]
        tareas.append(dict(
            id=t["id"], titulo=t["titulo"], tipo=t["tipo"], estado=estado, asignado=t["asignado"],
            story_points=t["story_points"], estimacion_h=None, horas_registradas=None,
            creada=t.get("creada"),
            iniciada=t["iniciada"] if estado != "pendiente" and d(t.get("iniciada")) and d(t["iniciada"]) <= corte else None,
            terminada=t["terminada"] if estado == "terminada" else None,
            ultimo_movimiento=max(movs).isoformat() if movs else None,
            reaperturas=0, dependencias=t["dependencias"], etiquetas=t["etiquetas"],
            historia=t["historia"], area=t["area"], entrega=t.get("entrega"), revisor=t.get("revisor"),
            pr=t.get("pr"), commit=t.get("commit"), listo_revision=t.get("listo_revision"), origen=t["origen"],
            codigo_plane=t.get("codigo_plane"), estado_actual=t["estado_tablero"], ciclo=t.get("ciclo"),
            cerrada_en_semana=estado == "terminada" and desde <= d(t["terminada"]) <= hasta,
        ))
    salida = dict(
        semana=semana, desde=desde.isoformat(), hasta=hasta.isoformat(), corte=corte.isoformat(),
        generado=datetime.now().isoformat(timespec="seconds"),
        fuente="Plane (API)" if fuente == "plane" else "gestion/plane/tickets.json (tablero reconstruido desde git)",
        supuestos=["No hay horas registradas en el tablero: estimacion_h y horas_registradas quedan en null.",
                   "Estado al cierre de la semana: listo para revisión = fecha del commit, terminada = fecha del merge."],
        tareas=tareas, commits=commits_de_semana(eq, desde.isoformat(), hasta.isoformat()),
    )
    ruta = REPORTES / semana / "tareas-normalizadas.json"
    guardar_json(ruta, salida)
    hechas = [t for t in tareas if t["cerrada_en_semana"]]
    print(f"{ruta.relative_to(RAIZ)}: {len(tareas)} tareas, {len(hechas)} terminadas en la semana "
          f"({sum(t['story_points'] or 0 for t in hechas)} SP), {len(salida['commits'])} commits. Fuente: {salida['fuente']}")


if __name__ == "__main__":
    main()
