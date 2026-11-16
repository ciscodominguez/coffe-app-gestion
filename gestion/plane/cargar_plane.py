#!/usr/bin/env python3
"""Carga en Plane el tablero reconstruido (gestion/plane/tickets.json).

Crea (o reutiliza, si ya existen) en el proyecto de Plane:
  - un ciclo por semana (Semana 44, 45, 46, 47, 48),
  - un módulo por historia (Cuentas y acceso, Caja y cobros, ...),
  - etiquetas de área (backend, frontend, ...), de tamaño (sp:1 ... sp:13) y de origen,
  - un issue por ticket, con responsable, estado, fechas de inicio y cierre,
y guarda el mapeo clave -> id de Plane en gestion/plane/ids-plane.json.

Se puede correr varias veces: los issues llevan external_id y no se duplican.

Requisitos: Python 3.9+ y `pip install requests`.

Uso (desde la raíz del repo):
    export PLANE_API_KEY="plane_api_..."        # en Windows PowerShell: $env:PLANE_API_KEY="..."
    python gestion/plane/cargar_plane.py --probar      # solo prueba el token (lista proyectos)
    python gestion/plane/cargar_plane.py --simular     # muestra qué haría, sin tocar Plane
    python gestion/plane/cargar_plane.py               # carga todo
"""
import argparse
import html
import json
import os
import sys
import time
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import RAIZ, leer_equipo, limites_semana, guardar_json, leer_json  # noqa: E402

try:
    import requests
except ImportError:
    sys.exit("Falta la librería requests: pip install requests")

TICKETS = RAIZ / "gestion" / "plane" / "tickets.json"
IDS = RAIZ / "gestion" / "plane" / "ids-plane.json"
FUENTE = "coffe-app-git"
GRUPO_ESTADO = {"Backlog": "backlog", "Todo": "unstarted", "In Progress": "started", "Done": "completed"}
COLOR_AREA = {"Backend": "#2563eb", "Frontend": "#16a34a", "Infra": "#9333ea", "Calidad": "#ea580c",
              "Docs": "#64748b", "Gestión": "#db2777"}


class Plane:
    def __init__(self, base, slug, token, pausa):
        self.base, self.slug, self.pausa = base.rstrip("/"), slug, pausa
        self.s = requests.Session()
        self.s.headers.update({"X-API-Key": token, "Content-Type": "application/json"})

    def url(self, ruta):
        return f"{self.base}/workspaces/{self.slug}/{ruta.lstrip('/')}"

    def req(self, metodo, ruta, ok=(200, 201, 204), **kw):
        for intento in range(6):
            r = self.s.request(metodo, self.url(ruta), timeout=30, **kw)
            time.sleep(self.pausa)
            if r.status_code == 429:
                espera = int(r.headers.get("Retry-After", "0") or 0) or 15 * (intento + 1)
                print(f"   … límite de la API, espero {espera}s")
                time.sleep(espera)
                continue
            if r.status_code in ok:
                return r.json() if r.content else None
            return r  # el llamador decide qué hacer con el error
        sys.exit(f"La API de Plane sigue limitando ({ruta}). Probá de nuevo en unos minutos.")

    def lista(self, ruta, **params):
        out, cursor = [], None
        while True:
            p = dict(params, per_page=100)
            if cursor:
                p["cursor"] = cursor
            r = self.req("GET", ruta, params=p)
            if isinstance(r, requests.Response):
                sys.exit(f"GET {ruta} -> {r.status_code}: {r.text[:300]}")
            if isinstance(r, list):
                return r
            out.extend(r.get("results", []))
            if not r.get("next_page_results"):
                return out
            cursor = r.get("next_cursor")


def fallar(r, que):
    sys.exit(f"No pude {que}: HTTP {r.status_code} — {r.text[:400]}")


def nombre_ciclo(clave):
    lunes, domingo = limites_semana(clave)
    sem = clave.split("-")[-1]
    return f"Semana {sem} ({lunes:%d/%m} al {domingo:%d/%m})"


def descripcion(t, repo):
    filas = [
        ("Clave", t["clave"]),
        ("Historia", t["historia"]),
        ("Área", t["modulo"]),
        ("Story points", t["sp"]),
    ]
    if t.get("pr"):
        filas += [
            ("Pull request", f'<a href="{repo}/pull/{t["pr"]}">#{t["pr"]}</a> (rama {html.escape(t["rama"])})'),
            ("Commit", f'<a href="{repo}/commit/{t["commit"]}">{t["commit"]}</a> — {html.escape(t["asunto_commit"])}'),
            ("Revisó y mergeó", t["revisor"]),
            ("Líneas agregadas", t["lineas"]),
        ]
    elif t.get("commit"):
        filas.append(("Commit", f'<a href="{repo}/commit/{t["commit"]}">{t["commit"]}</a>'))
    if t.get("deps"):
        filas.append(("Depende de", ", ".join(t["deps"])))
    cuerpo = "".join(f"<li><strong>{k}:</strong> {v}</li>" for k, v in filas)
    nota = ("<p><em>Ticket reconstruido desde el historial de git: fechas, responsable y tamaño son los reales "
            "del PR.</em></p>") if t["origen"] == "git" else ""
    return f"<ul>{cuerpo}</ul>{nota}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--probar", action="store_true", help="solo prueba el token listando los proyectos")
    ap.add_argument("--simular", action="store_true", help="muestra lo que haría, sin llamar a Plane")
    ap.add_argument("--proyecto", help="id del proyecto (si no, lo busca por nombre en equipo.md)")
    ap.add_argument("--pausa", type=float, default=1.1, help="segundos entre llamadas (la API permite ~60/min)")
    a = ap.parse_args()

    eq = leer_equipo()
    prm = eq["params"]
    datos = json.loads(TICKETS.read_text(encoding="utf-8"))["tickets"]
    ciclos = sorted({t["ciclo"] for t in datos if t["ciclo"]})
    historias = sorted({t["historia"] for t in datos})

    if a.simular:
        print(f"Workspace: {prm['plane_slug']} · proyecto: {prm['plane_proyecto']}")
        print(f"Ciclos ({len(ciclos)}): " + " | ".join(nombre_ciclo(c) for c in ciclos))
        print(f"Módulos ({len(historias)}): " + ", ".join(historias))
        for t in datos:
            print(f"  {t['clave']:<10} {t['estado']:<12} {t['ciclo'] or 'backlog':<15} "
                  f"{t['sp']:>2} SP  {t['responsable'] or '-':<6} {t['titulo']}")
        print(f"Total: {len(datos)} issues, {sum(t['sp'] for t in datos)} SP")
        return

    token = os.environ.get("PLANE_API_KEY")
    if not token:
        sys.exit("Definí PLANE_API_KEY con tu personal access token (Profile Settings > Personal Access Tokens).")
    slug = os.environ.get("PLANE_SLUG", prm["plane_slug"])
    api = Plane(os.environ.get("PLANE_BASE", "https://api.plane.so/api/v1"), slug, token, a.pausa)

    proyectos = api.lista("projects/")
    if a.probar:
        print(f"Token OK. Proyectos en '{slug}':")
        for p in proyectos:
            print(f"  {p['id']}  {p.get('identifier', ''):<8} {p['name']}")
        return

    if a.proyecto:
        proy = next((p for p in proyectos if p["id"] == a.proyecto), None)
    else:
        proy = next((p for p in proyectos if p["name"].strip().lower() == prm["plane_proyecto"].lower()), None)
        if proy is None and len(proyectos) == 1:
            proy = proyectos[0]
    if proy is None:
        nombres = ", ".join(p["name"] for p in proyectos) or "(ninguno)"
        sys.exit(f"No encontré el proyecto '{prm['plane_proyecto']}'. Proyectos: {nombres}. "
                 "Cambiá plane_proyecto en equipo.md o pasá --proyecto <id>.")
    pid = proy["id"]
    P = f"projects/{pid}"
    print(f"Proyecto: {proy['name']} ({proy.get('identifier', '')})")
    if not proy.get("cycle_view", True):
        print("⚠️  El proyecto tiene los Cycles apagados: activalos en Project settings > Features.")

    # --- Estados ---
    estados = api.lista(f"{P}/states/")
    por_grupo = {}
    for e in sorted(estados, key=lambda e: e.get("sequence", 0)):
        por_grupo.setdefault(e["group"], e["id"])
    faltan = [g for g in GRUPO_ESTADO.values() if g not in por_grupo]
    if faltan:
        sys.exit(f"Al proyecto le faltan estados de los grupos {faltan}.")

    # --- Integrantes -> miembros de Plane ---
    miembros = api.lista("members/")
    por_mail, por_nombre = {}, {}
    for m in miembros:
        m = m.get("member", m) if isinstance(m.get("member"), dict) else m
        if m.get("email"):
            por_mail[m["email"].lower()] = m["id"]
        for campo in ("display_name", "first_name"):
            if m.get(campo):
                por_nombre[m[campo].lower()] = m["id"]
    asignado = {}
    for p in eq["integrantes"]:
        mid = por_mail.get((p.get("email_plane") or "").lower())
        if not mid:
            mid = por_nombre.get(p["nombre"].split()[0].lower()) or por_nombre.get(p["clave"])
        asignado[p["clave"]] = mid
        print(f"  {p['clave']:<5} -> {'miembro de Plane' if mid else 'sin cuenta en Plane (va como etiqueta)'}")

    # --- Etiquetas ---
    existentes = {l["name"]: l["id"] for l in api.lista(f"{P}/labels/")}

    def etiqueta(nombre, color="#94a3b8"):
        if nombre not in existentes:
            r = api.req("POST", f"{P}/labels/", json={"name": nombre, "color": color})
            if isinstance(r, requests.Response):
                if r.status_code == 409:
                    existentes.update({l["name"]: l["id"] for l in api.lista(f"{P}/labels/")})
                else:
                    fallar(r, f"crear la etiqueta {nombre}")
            else:
                existentes[nombre] = r["id"]
        return existentes[nombre]

    # --- Módulos (historias) ---
    mods = {m["name"]: m["id"] for m in api.lista(f"{P}/modules/")}
    for h in historias:
        if h not in mods:
            r = api.req("POST", f"{P}/modules/", json={"name": h})
            if isinstance(r, requests.Response):
                fallar(r, f"crear el módulo {h}")
            mods[h] = r["id"]
            print(f"  módulo creado: {h}")

    # --- Ciclos ---
    hoy = date.today()
    cyc = {c["name"]: c for c in api.lista(f"{P}/cycles/")}
    ciclo_id, a_corregir = {}, []
    for c in ciclos:
        nom = nombre_ciclo(c)
        lunes, domingo = limites_semana(c)
        if nom in cyc:
            ciclo_id[c] = cyc[nom]["id"]
            continue
        # Plane no deja agregar issues a un ciclo ya terminado: lo creo abierto hasta mañana y
        # después de cargarle los issues le pongo la fecha de cierre real.
        fin_temp = max(domingo, hoy + timedelta(days=1))
        cuerpo = {"name": nom, "start_date": lunes.isoformat(), "end_date": fin_temp.isoformat(),
                  "project_id": pid}
        r = api.req("POST", f"{P}/cycles/", json=cuerpo)
        if isinstance(r, requests.Response):
            fallar(r, f"crear el ciclo {nom}")
        ciclo_id[c] = r["id"]
        if fin_temp != domingo:
            a_corregir.append((c, r["id"], domingo))
        print(f"  ciclo creado: {nom}")

    # --- Issues ---
    ids = leer_json(IDS, {})
    repo = prm["repo"].rstrip("/").removesuffix(".git")
    for t in datos:
        if t["clave"] in ids:
            continue
        etiquetas = [etiqueta(t["modulo"].lower(), COLOR_AREA.get(t["modulo"], "#94a3b8")),
                     etiqueta(f"sp:{t['sp']}", "#0ea5e9"),
                     etiqueta("origen:git" if t["origen"] == "git" else "origen:plan", "#a3a3a3")]
        resp = t["responsable"]
        asignados = [asignado[resp]] if resp and asignado.get(resp) else []
        if resp and not asignados:
            etiquetas.append(etiqueta(f"autor:{resp}", "#f59e0b"))
        cuerpo = {
            "name": t["titulo"],
            "description_html": descripcion(t, repo),
            "state": por_grupo[GRUPO_ESTADO[t["estado"]]],
            "priority": "high" if t["clave"].startswith("P-1") else "medium",
            "assignees": asignados,
            "labels": etiquetas,
            "external_id": t["clave"],
            "external_source": FUENTE,
        }
        if t.get("inicio"):
            cuerpo["start_date"] = t["inicio"]
        if t.get("fin"):
            cuerpo["target_date"] = t["fin"]
        r = api.req("POST", f"{P}/issues/", json=cuerpo)
        if isinstance(r, requests.Response):
            if r.status_code == 409:
                ya = api.lista(f"{P}/issues/", external_id=t["clave"], external_source=FUENTE)
                r = ya[0] if ya else fallar(r, f"recuperar el issue {t['clave']}")
            else:
                fallar(r, f"crear el issue {t['clave']}")
        ids[t["clave"]] = {"id": r["id"], "sequence_id": r.get("sequence_id")}
        guardar_json(IDS, ids)
        print(f"  issue {proy.get('identifier', '')}-{r.get('sequence_id')}: [{t['clave']}] {t['titulo'][:60]}")

    # --- Issues a ciclos y módulos ---
    def ya_en(ruta):
        return {i.get("id") or i.get("issue") for i in api.lista(ruta)}

    for c in ciclos:
        ruta = f"{P}/cycles/{ciclo_id[c]}/cycle-issues/"
        lote = [ids[t["clave"]]["id"] for t in datos if t["ciclo"] == c]
        lote = [i for i in lote if i not in ya_en(ruta)]
        if not lote:
            continue
        r = api.req("POST", ruta, json={"issues": lote})
        if isinstance(r, requests.Response):
            print(f"⚠️  No pude agregar {len(lote)} issues a {nombre_ciclo(c)}: {r.status_code} {r.text[:200]}\n"
                  "   (Plane no deja sumar issues a un ciclo terminado: cambiá a mano la fecha de fin a una futura, "
                  "corré el script de nuevo y volvé a poner la fecha real.)")
    for h in historias:
        ruta = f"{P}/modules/{mods[h]}/module-issues/"
        lote = [ids[t["clave"]]["id"] for t in datos if t["historia"] == h]
        lote = [i for i in lote if i not in ya_en(ruta)]
        if not lote:
            continue
        r = api.req("POST", ruta, json={"issues": lote})
        if isinstance(r, requests.Response):
            print(f"⚠️  No pude agregar los issues al módulo {h}: {r.status_code} {r.text[:200]}")

    for c, cid, domingo in a_corregir:
        r = api.req("PATCH", f"{P}/cycles/{cid}/", json={"end_date": domingo.isoformat()})
        if isinstance(r, requests.Response):
            print(f"⚠️  Cambiá a mano la fecha de fin de {nombre_ciclo(c)} a {domingo:%d/%m} "
                  f"(Plane respondió {r.status_code}).")

    print(f"\nListo: {len(ids)} issues en Plane. Mapeo guardado en {IDS.relative_to(RAIZ)}.")
    print("Siguiente paso: python gestion/normalizar.py --semana <semana-AAAA-SS>")


if __name__ == "__main__":
    main()
