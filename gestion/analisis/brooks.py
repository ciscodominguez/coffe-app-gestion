#!/usr/bin/env python3
"""Cálculos de la skill analista-brooks (.claude/skills/analista-brooks/SKILL.md).

"Agregar gente a un proyecto atrasado lo atrasa más." — Fred Brooks, The Mythical Man-Month (1975)

Lee reportes/<semana>/tareas-normalizadas.json, equipo.md y el git log completo. Escribe:
  reportes/<semana>/brooks.md   (estructura de la skill, con diagrama Mermaid de dependencias)
  reportes/<semana>/brooks.json

Supuestos de la simulación (los de la skill):
  - productividad de una persona nueva: 25 % / 50 % / 75 % / 100 % en sus semanas 1 a 4;
  - mentoría: 20 % del tiempo de un integrante actual durante las primeras 2 semanas;
  - overhead: 5 % de pérdida de productividad del equipo por cada canal nuevo;
  - la persona nueva solo toma trabajo paralelizable.

Uso: python gestion/analisis/brooks.py --semana semana-2026-46
"""
import argparse
import subprocess
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import (RAIZ, REPORTES, activos, autor_a_clave, guardar_json, leer_equipo,  # noqa: E402
                   leer_json, limites_semana, velocidades)

RAMPA = [0.25, 0.50, 0.75]   # semanas 1-3; desde la 4 rinde 100 %
MENTORIA = 0.20
SEMANAS_MENTORIA = 2
OVERHEAD_CANAL = 0.05
CARPETA_DE_AREA = {"Backend": "backend/", "Frontend": "frontend/", "Infra": "deploy/", "Calidad": "docs/pruebas/"}
CERRADAS = ("terminada", "cancelada")


def canales(n):
    return n * (n - 1) // 2


def d(x):
    return date.fromisoformat(x[:10]) if x else None


def bus_factor(conteo):
    """Mínimo de personas que juntan más de la mitad del trabajo."""
    total = sum(conteo.values())
    if not total:
        return 0, []
    acum, gente = 0, []
    for persona, v in sorted(conteo.items(), key=lambda x: -x[1]):
        acum += v
        gente.append(persona)
        if acum > total / 2:
            break
    return len(gente), gente


def autores_por_carpeta(eq, hasta):
    m = autor_a_clave(eq)
    out = defaultdict(lambda: defaultdict(int))
    salida = subprocess.run(["git", "log", "HEAD", "--no-merges", f"--until={hasta}T23:59:59-03:00",
                             "--format=@@%an", "--numstat"], capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=RAIZ,
                            check=True).stdout
    autor = None
    for l in salida.splitlines():
        if l.startswith("@@"):
            autor = m.get(l[2:].lower(), l[2:])
            continue
        partes = l.split("\t")
        if len(partes) != 3 or partes[0] == "-" or "package-lock" in partes[2]:
            continue
        for carpeta in set(CARPETA_DE_AREA.values()):
            if partes[2].startswith(carpeta):
                out[carpeta][autor] += int(partes[0])
    return out


def ruta_critica(pendientes):
    por = {t["id"]: t for t in pendientes}
    memo = {}

    def largo(c, pila=()):
        if c in memo:
            return memo[c]
        if c in pila:
            return 0, []
        mejor = (0, [])
        for dep in por[c].get("dependencias", []):
            if dep in por:
                mejor = max(mejor, largo(dep, pila + (c,)), key=lambda x: x[0])
        memo[c] = (mejor[0] + (por[c]["story_points"] or 0), mejor[1] + [c])
        return memo[c]

    return max((largo(c) for c in por), key=lambda x: x[0]) if por else (0, [])


def simular(pend_sp, paralelizable_sp, vel_dev, devs, n_equipo, extra, semanas_max=52):
    """Devuelve (semanas con decimales | None, capacidad efectiva por semana)."""
    restante, par_rest, exacto, caps = pend_sp, paralelizable_sp, 0.0, []
    perdida = OVERHEAD_CANAL * (canales(n_equipo + extra) - canales(n_equipo))
    for s in range(semanas_max):
        rinde_nuevo = (RAMPA[s] if s < len(RAMPA) else 1.0) * extra
        mentor = MENTORIA * extra if s < SEMANAS_MENTORIA else 0.0
        base = max(0.0, (devs - mentor) * vel_dev * (1 - perdida))
        nuevo = min(rinde_nuevo * vel_dev * (1 - perdida), par_rest)  # el nuevo solo hace lo paralelizable
        cap = base + nuevo
        caps.append(round(cap, 1))
        if cap <= 0:
            return None, caps
        hecho = min(restante, cap)
        exacto += hecho / cap
        restante -= hecho
        par_rest = max(0.0, par_rest - nuevo)
        if restante <= 1e-9:
            return round(exacto, 1), caps
    return None, caps


def analizar(semana):
    eq = leer_equipo()
    prm = eq["params"]
    datos = leer_json(REPORTES / semana / "tareas-normalizadas.json")
    if datos is None:
        sys.exit(f"Falta reportes/{semana}/tareas-normalizadas.json: corré antes gestion/normalizar.py")
    tareas = datos["tareas"]
    hasta, corte = d(datos["hasta"]), d(datos["corte"])
    nombre = {p["clave"]: p["nombre"].split()[0] for p in eq["integrantes"]}
    gente = activos(eq, hasta)
    tp = [p for p in gente if p["rol_tp"] == "integrante"]
    claves_tp = {p["clave"] for p in tp}
    devs_tp = [p for p in tp if p["rol"].lower().startswith("dev")]

    trabajaron = sorted({t["asignado"] for t in tareas if t["cerrada_en_semana"] and t["asignado"]}
                        | {c["autor"] for c in datos["commits"]}
                        | {t["revisor"] for t in tareas if t["cerrada_en_semana"] and t.get("revisor")})

    # Equipo de la próxima etapa: el grupo del TP más los colaboradores que tienen trabajo pendiente asignado.
    con_pendiente = {t["asignado"] for t in tareas if t["estado"] not in CERRADAS and t.get("entrega") != "deseable"
                     and t.get("asignado")}
    equipo = [p for p in gente if p["rol_tp"] == "integrante" or p["clave"] in con_pendiente]
    devs = [p for p in equipo if p["rol"].lower().startswith("dev")]
    claves_devs = {p["clave"] for p in devs}

    # Velocidad: promedio de las últimas 3 semanas. Por desarrollador = SP cerrados ÷ (devs que cerraron algo esa semana).
    hechas = [dict(t, estado="Done" if t["estado"] == "terminada" else t["estado"], responsable=t["asignado"],
                   fin=t["terminada"], sp=t["story_points"]) for t in tareas]
    vels = velocidades(hechas, semana, claves_devs, 3, d(prm["fecha_inicio"]))
    dev_semanas = 0
    for s_ in vels:
        lun, dom = limites_semana(s_)
        dev_semanas += len({t["asignado"] for t in tareas if t["estado"] == "terminada" and t["asignado"] in claves_devs
                            and lun <= d(t["terminada"]) <= dom})
    vel_dev = sum(vels.values()) / dev_semanas if dev_semanas else 0
    vel_tp = vel_dev * len(devs)

    # Trabajo pendiente comprometido (sin lo "deseable").
    pend = [t for t in tareas if t["estado"] not in CERRADAS and t.get("entrega") != "deseable"]
    deseable = [t for t in tareas if t["estado"] not in CERRADAS and t.get("entrega") == "deseable"]
    ids_pend = {t["id"] for t in pend}
    carpetas = autores_por_carpeta(eq, datos["hasta"])
    bus_carpeta = {c: bus_factor(v) for c, v in sorted(carpetas.items())}
    clasif = []
    for t in pend:
        deps_abiertas = [x for x in t.get("dependencias", []) if x in ids_pend]
        carpeta = CARPETA_DE_AREA.get(t.get("area"))
        conocen = list(carpetas.get(carpeta, {}).keys()) if carpeta else []
        bus = bus_carpeta.get(carpeta, (0, []))[0] if carpeta else None
        if deps_abiertas:
            tipo = "Secuencial"
        elif bus == 1:
            tipo = "Crítica de conocimiento"
        else:
            tipo = "Paralelizable"
        quien = bus_carpeta[carpeta][1] if carpeta in bus_carpeta else []
        clasif.append(dict(id=t["id"], titulo=t["titulo"], sp=t["story_points"] or 0, tipo=tipo,
                           depende_de=deps_abiertas, quien_sabe=quien or ([t["asignado"]] if t["asignado"] else []),
                           asignado=t["asignado"], estado=t["estado"], conocen=len(conocen)))
    pend_sp = sum(c["sp"] for c in clasif)
    par_sp = sum(c["sp"] for c in clasif if c["tipo"] == "Paralelizable")
    seq_sp = pend_sp - par_sp
    rc_sp, rc = ruta_critica(pend)

    entregas = [e for e in prm["entregas"] if d(e) >= corte]
    proxima = entregas[0] if entregas else prm["fecha_entrega"]
    semanas_restantes = max(0.0, (d(prm["fecha_entrega"]) - corte).days / 7)
    pend_final = pend_sp
    semanas_nec = pend_final / vel_tp if vel_tp else None
    atrasado = semanas_nec is None or semanas_nec > semanas_restantes

    # Cuellos de botella: quién bloquea a otros y quién revisa.
    entrantes = defaultdict(int)
    for c in clasif:
        for dep in c["depende_de"]:
            dueño = next((x["asignado"] for x in clasif if x["id"] == dep), None)
            if dueño:
                entrantes[dueño] += 1
    revisiones = defaultdict(int)
    for t in tareas:
        if t["estado"] == "terminada" and t.get("revisor"):
            revisiones[t["revisor"]] += 1
    total_rev = sum(revisiones.values()) or 1

    # Señales de condición de Brooks.
    ingresos = [p for p in gente if (hasta - p["alta"]).days < 28 and p["alta"] > d(prm["fecha_inicio"])]
    nuevos = [p for p in ingresos if p["rol"].lower().startswith("dev")]  # Brooks habla de sumar gente al desarrollo
    señales = []
    if atrasado and nuevos:
        señales.append("El proyecto está atrasado y se sumó gente.")
    vel_semana = list(vels.values())
    if nuevos and len(vel_semana) >= 2 and vel_semana[-1] < vel_semana[-2]:
        señales.append(f"Se sumó {', '.join(nombre[p['clave']] for p in nuevos)} en las últimas 4 semanas y la "
                       "velocidad bajó.")
    if pend_sp and seq_sp / pend_sp > 0.5:
        señales.append(f"{seq_sp / pend_sp:.0%} del trabajo pendiente es secuencial o crítico de conocimiento.")
    diag = "🔴" if (atrasado and nuevos) or len(señales) >= 2 else "🟡" if señales or atrasado else "🟢"

    escenarios = []
    n_eq = len(equipo)
    lunes_sig = limites_semana(semana)[1] + timedelta(days=1)
    for extra in (0, 1, 2):
        sem, caps = simular(pend_sp, par_sp, vel_dev, len(devs), n_eq, extra)
        fin = (lunes_sig + timedelta(days=round(sem * 7)) if sem is not None else None)
        escenarios.append(dict(extra=extra, personas=n_eq + extra, canales=canales(n_eq + extra), semanas=sem,
                               capacidad=caps[:4], fin=fin.isoformat() if fin else None))
    base = escenarios[0]["semanas"]
    for e in escenarios:
        if base is None or e["semanas"] is None:
            e["vs_hoy"] = "—" if e["extra"] == 0 else "no se puede calcular"
        elif e["extra"] == 0:
            e["vs_hoy"] = "—"
        else:
            dif = e["semanas"] - base
            e["vs_hoy"] = ("acorta" if dif <= -0.3 else "alarga" if dif >= 0.3 else "no cambia") + f" ({dif:+.1f} sem.)"
    return dict(
        semana=semana, desde=datos["desde"], hasta=datos["hasta"], fuente=datos["fuente"], diagnostico=diag,
        señales=señales, atrasado=atrasado, equipo_trabajo=trabajaron, canales_trabajo=canales(len(trabajaron)),
        grupo_tp=sorted(claves_tp), canales_tp=canales(len(tp)), devs_tp=[p["clave"] for p in devs],
        equipo=[p["clave"] for p in equipo], canales_equipo=canales(len(equipo)),
        velocidades_tp=vels, velocidad_tp=round(vel_tp, 1), velocidad_dev=round(vel_dev, 1),
        pendientes=clasif, pendiente_sp=pend_sp, paralelizable_sp=par_sp, secuencial_sp=seq_sp,
        deseable=[dict(id=t["id"], titulo=t["titulo"], sp=t["story_points"]) for t in deseable],
        ruta_critica=rc, ruta_critica_sp=rc_sp,
        ruta_critica_semanas=round(rc_sp / vel_dev, 1) if vel_dev else None,
        semanas_restantes=round(semanas_restantes, 1), semanas_necesarias=round(semanas_nec, 1) if semanas_nec else None,
        proxima_entrega=proxima, fecha_entrega=prm["fecha_entrega"],
        bus_factor={c: dict(bus=b, gente=g) for c, (b, g) in bus_carpeta.items()},
        entrantes=dict(entrantes), revisiones={k: v for k, v in sorted(revisiones.items(), key=lambda x: -x[1])},
        revisiones_pct={k: round(v / total_rev, 2) for k, v in revisiones.items()},
        nuevos=[p["clave"] for p in ingresos], escenarios=escenarios, nombres=nombre,
        deps_todas={t["id"]: [x for x in t.get("dependencias", [])] for t in pend},
    )


def mermaid(r):
    nom = r["nombres"]
    L = ["```mermaid", "flowchart LR"]
    ids = {c["id"] for c in r["pendientes"]}
    for c in r["pendientes"]:
        quien = nom.get(c["asignado"], "sin asignar")
        L.append(f'    {c["id"].replace("-", "_")}["{c["id"]} · {c["sp"]} SP<br/>{quien}"]')
    for c in r["pendientes"]:
        for dep in c["depende_de"]:
            if dep in ids:
                L.append(f'    {dep.replace("-", "_")} --> {c["id"].replace("-", "_")}')
    L.append("    classDef critica fill:#fde2e1,stroke:#d03b3b,stroke-width:2px")
    if r["ruta_critica"]:
        L.append("    class " + ",".join(x.replace("-", "_") for x in r["ruta_critica"]) + " critica")
    L.append("```")
    return L


def escribir_md(r):
    nom = lambda c: r["nombres"].get(c, c or "sin asignar")  # noqa: E731
    textos = {"🟢": "Sin riesgo", "🟡": "Riesgo", "🔴": "En condición de Brooks"}
    if r["diagnostico"] == "🟢":
        frase = ("el grupo llega con la velocidad actual y no hay planes de sumar gente.")
    elif r["señales"]:
        frase = " ".join(r["señales"])
    else:
        frase = "con la velocidad actual el trabajo comprometido no entra en el tiempo que queda."
    L = [f"# Análisis de Ley de Brooks — Semana {r['semana'][-2:]}", "",
         "> \"Agregar gente a un proyecto atrasado lo atrasa más.\" — Fred Brooks, *The Mythical Man-Month* (1975)", "",
         "## Diagnóstico", f"{r['diagnostico']} **{textos[r['diagnostico']]}** — {frase}", "",
         "## Equipo y comunicación",
         f"- Integrantes del grupo del TP: {len(r['grupo_tp'])} ({', '.join(nom(c) for c in r['grupo_tp'])}) — "
         f"canales: {r['canales_tp']} — overhead estimado: no medible (no hay tareas de reunión en el tablero)",
         f"- Equipo con trabajo pendiente: {len(r['equipo'])} ({', '.join(nom(c) for c in r['equipo'])}) — canales: "
         f"{r['canales_equipo']}",
         f"- Personas que trabajaron en el repo/tablero esta semana: {len(r['equipo_trabajo'])} "
         f"({', '.join(nom(c) for c in r['equipo_trabajo']) or 'nadie'}) — canales: {r['canales_trabajo']}",
         "- Fórmula: canales = n × (n − 1) ÷ 2. Con +1 persona en el grupo del TP: "
         f"{(len(r['grupo_tp']) + 1) * len(r['grupo_tp']) // 2} canales; con +2: "
         f"{(len(r['grupo_tp']) + 2) * (len(r['grupo_tp']) + 1) // 2}.", ""]
    if r["nuevos"]:
        L += [f"- Ingresos recientes (últimas 4 semanas): {', '.join(nom(c) for c in r['nuevos'])} — entra como gestión "
              "(PO), no como desarrollo, así que no consume rampa sobre el código.", ""]
    L += ["## Trabajo pendiente",
          "| Historia | Puntos | Paralelizable / Secuencial / Crítica | Depende de | Quién sabe |", "|---|---|---|---|---|"]
    for c in r["pendientes"]:
        L.append(f"| {c['id']} — {c['titulo']} | {c['sp']} | {c['tipo']} | {', '.join(c['depende_de']) or '—'} | "
                 f"{', '.join(nom(x) for x in c['quien_sabe']) or '—'} |")
    if not r["pendientes"]:
        L.append("| (sin trabajo comprometido pendiente) | | | | |")
    L += ["",
          f"- Pendiente comprometido: **{r['pendiente_sp']:.0f} SP** — paralelizable {r['paralelizable_sp']:.0f} SP, "
          f"secuencial o crítico {r['secuencial_sp']:.0f} SP.",
          f"- Ruta crítica: {' → '.join(r['ruta_critica']) or '—'} ({r['ruta_critica_sp']:.0f} pts"
          + (f", ~{r['ruta_critica_semanas']} semanas a {r['velocidad_dev']} SP/semana por persona)"
             if r["ruta_critica_semanas"] is not None else ")") + " — piso mínimo del proyecto.",
          f"- Dependencias: las del tablero (campo «Depende de» de cada ticket); las de los tickets reconstruidos "
          "se infirieron de git y de los títulos."]
    if r["deseable"]:
        deseables = ", ".join(f"{x['id']} ({x['sp']} SP)" for x in r["deseable"])
        L.append(f"- Fuera del alcance comprometido (deseable): {deseables}.")
    L += [""] + mermaid(r) + ["", "## Cuellos de botella y bus factor",
                              "| Carpeta | Bus factor | Quién la conoce (más de la mitad de las líneas) |", "|---|---|---|"]
    for c, v in r["bus_factor"].items():
        L.append(f"| {c} | {v['bus']}{' ⚠️' if v['bus'] == 1 else ''} | {', '.join(nom(g) for g in v['gente'])} |")
    if r["revisiones"]:
        top = next(iter(r["revisiones"]))
        L += ["", f"- Revisiones (merges de PR) acumuladas: " + ", ".join(f"{nom(k)} {v}" for k, v in r["revisiones"].items())
              + f". {nom(top)} mergea el {r['revisiones_pct'][top]:.0%}: si falta, los PRs esperan."]
    for k, v in r["entrantes"].items():
        L.append(f"- {nom(k)} tiene {v} tarea(s) pendiente(s) que esperan algo suyo.")
    L += ["", "## Simulación: ¿sumar gente?",
          f"Base: {len(r['devs_tp'])} desarrolladores con trabajo pendiente ({', '.join(nom(c) for c in r['devs_tp'])}) "
          f"a {r['velocidad_dev']} SP/semana cada uno (velocidad del equipo {r['velocidad_tp']} SP/semana, promedio de las semanas "
          f"{', '.join(k[-2:] for k in r['velocidades_tp'])}). Quedan {r['semanas_restantes']} semanas hasta la entrega "
          f"final ({r['fecha_entrega']}).", "",
          "| Escenario | Personas | Canales | Capacidad efectiva sem 1–4 (SP) | Fin estimado | vs. hoy |", "|---|---|---|---|---|---|"]
    for e in r["escenarios"]:
        esc = "Equipo actual" if e["extra"] == 0 else f"+{e['extra']} persona(s)"
        fin = f"{date.fromisoformat(e['fin']):%d/%m/%Y} ({e['semanas']} sem.)" if e["fin"] else "no termina"
        L.append(f"| {esc} | {e['personas']} | {e['canales']} | {' / '.join(str(c) for c in e['capacidad'])} | {fin} | {e['vs_hoy']} |")
    L += ["", "## Recomendaciones"]
    recs = []
    if r["atrasado"]:
        recs.append("**Recortar alcance** antes que sumar gente: lo deseable ya está fuera; si hace falta más, pasar a "
                    "deseable lo que no está en la ruta crítica.")
    crit = [c for c in r["pendientes"] if c["tipo"] == "Crítica de conocimiento"]
    if crit or any(v["bus"] == 1 for v in r["bus_factor"].values()):
        solos = [c for c, v in r["bus_factor"].items() if v["bus"] == 1]
        recs.append(f"**Reducir bus factor** en {', '.join(solos)}: pair programming o revisión cruzada (que Octavio "
                    "acompañe a Francisco en el despliegue, por ejemplo).")
    if r["revisiones"]:
        recs.append("**Bajar el cuello de botella de revisión**: que cualquiera del grupo pueda mergear con una "
                    "aprobación, en vez de depender de una sola persona.")
    recs.append("Si igual hace falta alguien, conviene **un colaborador que ya conoce el código** (Gio, Facu o Nico): "
                "no tiene rampa ni necesita mentor, a diferencia de una persona nueva. Solo en tareas paralelizables.")
    if not recs:
        recs.append("Seguir con el equipo actual.")
    L += [f"- {x}" for x in recs]
    L += ["", "## Supuestos",
          "- Productividad de una persona nueva: 25 % / 50 % / 75 % / 100 % en sus semanas 1 a 4.",
          "- Mentoría: 20 % del tiempo de un integrante durante las primeras 2 semanas.",
          "- Overhead: 5 % menos de productividad del equipo por cada canal nuevo.",
          "- La persona nueva solo toma trabajo paralelizable.",
          "- Velocidad por desarrollador = SP cerrados ÷ desarrolladores que cerraron algo, promedio de 3 semanas. El "
          "equipo de la simulación es el grupo del TP más los colaboradores con tareas pendientes; Agustín (PO) cuenta "
          "para la comunicación pero no suma SP de código.",
          "- «Quién sabe» y bus factor salen de las líneas agregadas por autor en cada carpeta (git log de main).",
          f"- Fuente: {r['fuente']}.", ""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--semana", required=True)
    a = ap.parse_args()
    r = analizar(a.semana)
    (REPORTES / a.semana / "brooks.md").write_text(escribir_md(r), encoding="utf-8")
    guardar_json(REPORTES / a.semana / "brooks.json", r)
    print(f"brooks {a.semana}: {r['diagnostico']} — {r['pendiente_sp']:.0f} SP pendientes, ruta crítica "
          f"{r['ruta_critica_sp']:.0f} SP, base {r['escenarios'][0]['semanas']} semanas de {r['semanas_restantes']}")


if __name__ == "__main__":
    main()
