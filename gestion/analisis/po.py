#!/usr/bin/env python3
"""Cálculos y reporte de la skill product-owner (.claude/skills/product-owner/SKILL.md).

Lee reportes/<semana>/tareas-normalizadas.json + equipo.md y, si existen, costos.json, brooks.json
y los históricos. Escribe:
  reportes/<semana>/reporte-po.html   (informe para proyectar; gráficos con Chart.js 4.4.1 de cdnjs)
  reportes/<semana>/reporte-po.md
  reportes/historico-po.json          (agrega la semana sin pisar las anteriores)

Proyección de cierre: SP pendientes ÷ velocidad promedio (grupo del TP, últimas 3 semanas) = semanas
necesarias, contra las semanas que quedan hasta cada entrega de equipo.md.
  🟢 En camino: llega con margen · 🟡 En riesgo: justo o hasta 20 % más de velocidad · 🔴 No llega

Uso: python gestion/analisis/po.py --semana semana-2026-46
"""
import argparse
import html
import json
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import (REPORTES, activos, dias_habiles, guardar_json, leer_equipo, leer_json,  # noqa: E402
                   limites_semana, semana_de, semanas_entre, usd)

CHART_JS = "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"
LUZ = {"verde": ("🟢", "En camino"), "amarillo": ("🟡", "En riesgo"), "rojo": ("🔴", "No llega")}
ESTADOS = ["pendiente", "en_curso", "en_revision", "bloqueada", "terminada"]
NOMBRE_ESTADO = {"pendiente": "Pendiente", "en_curso": "En curso", "en_revision": "En revisión",
                 "bloqueada": "Bloqueada", "terminada": "Terminada"}


def d(x):
    return date.fromisoformat(x[:10]) if x else None


def luz(necesarias, restantes):
    if necesarias is None:
        return "rojo"
    if restantes <= 0:
        return "verde" if necesarias == 0 else "rojo"
    r = necesarias / restantes
    return "verde" if r <= 0.9 else "amarillo" if r <= 1.2 else "rojo"


def analizar(semana):
    eq = leer_equipo()
    prm = eq["params"]
    datos = leer_json(REPORTES / semana / "tareas-normalizadas.json")
    if datos is None:
        sys.exit(f"Falta reportes/{semana}/tareas-normalizadas.json: corré antes gestion/normalizar.py")
    tareas = datos["tareas"]
    desde, hasta, corte = d(datos["desde"]), d(datos["hasta"]), d(datos["corte"])
    inicio = d(prm["fecha_inicio"])
    nombre = {p["clave"]: p["nombre"] for p in eq["integrantes"]}
    tp = [p for p in activos(eq, hasta) if p["rol_tp"] == "integrante"]
    claves_tp = {p["clave"] for p in eq["integrantes"] if p["rol_tp"] == "integrante"}
    comprometidas = [t for t in tareas if t.get("entrega") != "deseable" and t["estado"] != "cancelada"]

    terminadas = [t for t in tareas if t["cerrada_en_semana"]]
    sp_sem = sum(t["story_points"] or 0 for t in terminadas)

    # Velocidad: semanas desde el inicio del proyecto hasta esta.
    semanas = [s for s in semanas_entre(inicio, hasta) if limites_semana(s)[0] <= hasta]
    vel = {s: dict(total=0.0, tp=0.0, tareas=0) for s in semanas}
    for t in tareas:
        if t["estado"] == "terminada":
            s = semana_de(t["terminada"])
            if s in vel:
                vel[s]["total"] += t["story_points"] or 0
                vel[s]["tareas"] += 1
                if t["asignado"] in claves_tp:
                    vel[s]["tp"] += t["story_points"] or 0
    ult3 = semanas[-3:]
    vel_tp = sum(vel[s]["tp"] for s in ult3) / len(ult3)
    vel_total_prom = sum(vel[s]["total"] for s in ult3) / len(ult3)
    vel_proy = vel_total_prom  # la proyección usa la velocidad de todo el equipo que trabajó

    # Proyección por entrega.
    proyecciones = []
    for e in prm["entregas"]:
        fe = d(e)
        if fe < corte:
            continue
        pend = sum(t["story_points"] or 0 for t in comprometidas if t["estado"] != "terminada"
                   and t.get("entrega") and t["entrega"] <= e)
        restantes = max(0.0, (fe - corte).days / 7)
        nec = pend / vel_proy if vel_proy else (0.0 if pend == 0 else None)
        nec_tp = pend / vel_tp if vel_tp else (0.0 if pend == 0 else None)
        proyecciones.append(dict(entrega=e, final=e == prm["fecha_entrega"], pendiente=pend,
                                 semanas_restantes=round(restantes, 1),
                                 semanas_necesarias=round(nec, 1) if nec is not None else None,
                                 semanas_necesarias_tp=round(nec_tp, 1) if nec_tp is not None else None,
                                 velocidad_necesaria=round(pend / restantes, 1) if restantes else None,
                                 luz=luz(nec, restantes)))
    orden = {"verde": 0, "amarillo": 1, "rojo": 2}
    general = max((p["luz"] for p in proyecciones), key=lambda x: orden[x]) if proyecciones else "verde"

    total_sp = sum(t["story_points"] or 0 for t in comprometidas)
    hecho_sp = sum(t["story_points"] or 0 for t in comprometidas if t["estado"] == "terminada")
    avance = hecho_sp / total_sp if total_sp else 0
    pendiente_sp = total_sp - hecho_sp

    por_epica = defaultdict(lambda: [0.0, 0.0])
    for t in comprometidas:
        por_epica[t["historia"]][1] += t["story_points"] or 0
        if t["estado"] == "terminada":
            por_epica[t["historia"]][0] += t["story_points"] or 0

    lead = [(d(t["terminada"]) - d(t["creada"])).days for t in terminadas if t.get("creada")]
    cycle = [(d(t["terminada"]) - d(t["iniciada"])).days for t in terminadas if t.get("iniciada")]
    revision = [dias_habiles(d(t["listo_revision"]), d(t["terminada"])) for t in terminadas if t.get("listo_revision")]

    nuevas = [t for t in tareas if t.get("creada") and desde <= d(t["creada"]) <= hasta]
    scope = sum(t["story_points"] or 0 for t in nuevas)
    del_ciclo = [t for t in tareas if t.get("ciclo") == semana]
    no_terminadas = [t for t in del_ciclo if t["estado"] != "terminada"]

    # Alertas (nivel, evidencia, acción).
    alertas = []

    def alerta(nivel, titulo, evidencia, accion):
        alertas.append(dict(nivel=nivel, titulo=titulo, evidencia=evidencia, accion=accion))

    movs = [d(t["ultimo_movimiento"]) for t in tareas if t.get("ultimo_movimiento")]
    ultimo = max(movs) if movs else None
    if ultimo is None or dias_habiles(ultimo, corte) >= 3:
        alerta("alto", "Tablero quieto",
               f"Ninguna tarea cambió de estado en {dias_habiles(ultimo, corte)} días hábiles (último movimiento "
               f"{ultimo:%d/%m})." if ultimo else "El tablero no tiene movimientos.",
               "Mover los estados el mismo día que cambia el trabajo; crear el ticket antes de codear.")
    for t in tareas:
        if t["estado"] in ("en_curso", "en_revision") and t.get("ultimo_movimiento") and \
                (corte - d(t["ultimo_movimiento"])).days >= 5:
            alerta("medio", "Tarea en curso sin movimiento",
                   f"{t['id']} — {t['titulo']} ({nombre.get(t['asignado'], 'sin asignar')}) sin cambios hace "
                   f"{(corte - d(t['ultimo_movimiento'])).days} días.", "Destrabarla o partirla en partes más chicas.")
    if len(terminadas) < 2:
        alerta("alto", "Pocas tareas terminadas", f"Solo {len(terminadas)} tarea(s) terminada(s) en la semana.",
               "Revisar qué está frenando el ciclo en la daily del lunes.")
    previas = [vel[s]["total"] for s in semanas[:-1][-3:]]
    if previas and sum(previas) / len(previas) and sp_sem < 0.5 * sum(previas) / len(previas):
        prom = sum(previas) / len(previas)
        alerta("alto", "Velocidad en caída",
               f"{sp_sem:.0f} SP esta semana contra {prom:.0f} SP de promedio en las anteriores "
               f"({sp_sem / prom:.0%}).", "Ver si falta trabajo cargado en el tablero o si el equipo frenó.")
    commits_autores = {c["autor"] for c in datos["commits"]}
    movieron = set()
    for t in tareas:
        for campo in ("iniciada", "listo_revision", "terminada"):
            f = d(t.get(campo))
            if f and desde <= f <= hasta:
                movieron.add(t["asignado"])
                if campo == "terminada" and t.get("revisor"):
                    movieron.add(t["revisor"])
    for p in tp:
        if p["clave"] not in movieron | commits_autores:
            alerta("medio", "Integrante sin movimiento", f"{p['nombre']}: ninguna tarea movida ni commits en la semana.",
                   "Asignarle tickets del próximo ciclo.")
    commits_tareas = {t.get("commit") for t in tareas if t.get("commit")}
    sueltos = [c for c in datos["commits"] if c["hash"] not in commits_tareas
               and not any(x in commits_tareas for x in c.get("copias", []))]
    if sueltos:
        alerta("bajo", "Commits sin tarea", f"{len(sueltos)} commit(s) de la semana no están vinculados a ningún ticket "
               f"({', '.join(c['hash'] for c in sueltos[:5])}).", "Poner el ID del issue de Plane en cada commit.")
    if no_terminadas:
        alerta("medio", "Comprometido no terminado",
               f"{len(no_terminadas)} tarea(s) del ciclo de la semana sin terminar: "
               f"{', '.join(t['id'] for t in no_terminadas)}.", "Pasarlas al próximo ciclo y ver por qué no cerraron.")
    if scope > sp_sem and scope > 0:
        alerta("medio", "Crecimiento de alcance", f"Entraron {scope:.0f} SP nuevos y se terminaron {sp_sem:.0f}.",
               "Confirmar con el PO qué entra en la próxima entrega y qué pasa a deseable.")
    for p in proyecciones:
        if p["luz"] != "verde":
            sobra = p["pendiente"] - vel_proy * p["semanas_restantes"]
            alerta("alto" if p["luz"] == "rojo" else "medio", f"Entrega {d(p['entrega']):%d/%m} {LUZ[p['luz']][1].lower()}",
                   f"Con la velocidad actual ({vel_proy:.0f} SP/semana) hacen falta {p['semanas_necesarias']} semanas y "
                   f"quedan {p['semanas_restantes']}.",
                   f"Recortar ~{max(0, sobra):.0f} SP de alcance o subir la velocidad a {p['velocidad_necesaria']} SP/semana.")
    nivel_orden = {"alto": 0, "medio": 1, "bajo": 2}
    alertas.sort(key=lambda a: nivel_orden[a["nivel"]])

    # Próxima semana: lo pendiente de la próxima entrega, primero lo que destraba a otros.
    prox = next((p for p in proyecciones if p["pendiente"] > 0), None)
    pend_prox = [t for t in comprometidas if t["estado"] != "terminada" and prox and t.get("entrega")
                 and t["entrega"] <= prox["entrega"]]
    destraba = defaultdict(int)
    for t in tareas:
        for dep in t.get("dependencias", []):
            destraba[dep] += 1
    pend_prox.sort(key=lambda t: (-destraba[t["id"]], t["entrega"] or "", -(t["story_points"] or 0)))

    # Burndown del alcance comprometido.
    burndown = []
    for s in semanas:
        c = min(limites_semana(s)[1], corte)
        pend = sum(t["story_points"] or 0 for t in comprometidas
                   if (not t.get("creada") or d(t["creada"]) <= c)
                   and not (t["estado"] == "terminada" and d(t["terminada"]) <= c))
        burndown.append(dict(semana=s, pendiente=pend))
    final = d(prm["fecha_entrega"])
    semanas_plan = semanas_entre(inicio, final)
    total_ini = burndown[0]["pendiente"] if burndown else 0
    ideal = [round(total_ini * (1 - i / max(1, len(semanas_plan) - 1)), 1) for i in range(len(semanas_plan))]

    por_persona = defaultdict(lambda: defaultdict(float))
    for t in terminadas:
        por_persona[nombre.get(t["asignado"], t["asignado"] or "sin asignar")][t["tipo"]] += t["story_points"] or 0
    estado_tablero = {e: sum(1 for t in tareas if t["estado"] == e) for e in ESTADOS}

    return dict(
        semana=semana, desde=datos["desde"], hasta=datos["hasta"], corte=datos["corte"], fuente=datos["fuente"],
        proyecto=prm["nombre"], grupo=[nombre[c] for c in sorted(claves_tp)], semaforo=general,
        proyecciones=proyecciones, sp_semana=sp_sem, tareas_semana=len(terminadas),
        velocidad_tp=round(vel_tp, 1), velocidad_total_prom=round(vel_total_prom, 1),
        avance=round(avance, 3), hecho_sp=hecho_sp, total_sp=total_sp, pendiente_sp=pendiente_sp,
        bloqueadas=estado_tablero["bloqueada"],
        epicas={k: dict(hecho=v[0], total=v[1]) for k, v in sorted(por_epica.items())},
        lead_time=round(sum(lead) / len(lead), 1) if lead else None,
        cycle_time=round(sum(cycle) / len(cycle), 1) if cycle else None,
        espera_revision=round(sum(revision) / len(revision), 1) if revision else None,
        scope_creep=scope, logros=[dict(id=t["id"], titulo=t["titulo"], historia=t["historia"],
                                         asignado=nombre.get(t["asignado"], t["asignado"]), sp=t["story_points"])
                                    for t in terminadas],
        alertas=alertas, proxima=[dict(id=t["id"], titulo=t["titulo"], sp=t["story_points"], entrega=t["entrega"],
                                        asignado=nombre.get(t["asignado"], "sin asignar"), destraba=destraba[t["id"]])
                                   for t in pend_prox[:6]],
        velocidad=[dict(semana=s, **vel[s]) for s in semanas], burndown=burndown,
        ideal=[dict(semana=s, sp=v) for s, v in zip(semanas_plan, ideal)],
        por_persona={k: dict(v) for k, v in por_persona.items()}, estado_tablero=estado_tablero,
    )


def etiqueta(s):
    lunes, domingo = limites_semana(s)
    return f"S{s[-2:]} ({lunes:%d/%m})"


CSS = """
:root{--bg:#f6f5f2;--card:#fff;--line:#e4e2dc;--ink:#0b0b0b;--ink2:#52514e;--muted:#7a7974;--main:#2a78d6;
--good:#0ca30c;--warn:#fab219;--bad:#d03b3b}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
main{max-width:1180px;margin:0 auto;padding:40px 24px 64px}section{margin-bottom:28px;break-inside:avoid}
h1{font-size:34px;line-height:1.15;margin:0}h2{font-size:20px;margin:0 0 14px}h3{font-size:15px;margin:16px 0 6px}
.muted{color:var(--muted)}.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px}
.portada{display:flex;gap:28px;align-items:center;justify-content:space-between;flex-wrap:wrap}
.portada .sub{color:var(--ink2);margin-top:6px}.luz{text-align:center;min-width:180px}
.luz .icono{font-size:84px;line-height:1}.luz .txt{font-size:22px;font-weight:700;margin-top:6px}
.aviso{border-left:6px solid var(--bad);background:#fdf0ef}.aviso.amarillo{border-color:var(--warn);background:#fff8e6}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px}
.kpi .n{font-size:30px;font-weight:700;font-variant-numeric:tabular-nums}.kpi .l{color:var(--ink2);font-size:13px}
.kpi .c{color:var(--muted);font-size:12px;margin-top:2px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(460px,1fr));gap:18px}
.chart{position:relative;height:300px}
ul.logros{list-style:none;padding:0;margin:0}ul.logros li{padding:6px 0;border-top:1px solid var(--line)}
ul.logros li:first-child{border-top:0}.chk{color:var(--good);font-weight:700;margin-right:6px}
table{width:100%;border-collapse:collapse;font-size:14px}th,td{text-align:left;padding:7px 8px;border-top:1px solid var(--line);vertical-align:top}
th{color:var(--ink2);border-top:0;font-weight:600}td.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.nivel{font-weight:700;white-space:nowrap}.nivel.alto{color:var(--bad)}.nivel.medio{color:#8a5a00}.nivel.bajo{color:var(--ink2)}
.barra{height:8px;background:var(--line);border-radius:4px;overflow:hidden;min-width:120px}
.barra i{display:block;height:100%;background:var(--main);border-radius:4px}
footer{color:var(--muted);font-size:12px;margin-top:32px}
@media (max-width:640px){.grid{grid-template-columns:1fr}h1{font-size:26px}}
@media print{body{background:#fff}main{padding:0}.card{border-color:#ccc}section{page-break-inside:avoid}
.grid{grid-template-columns:1fr 1fr}.chart{height:260px}}
"""


def escribir_html(r, costos, brooks, hist_costos):
    e = html.escape
    lunes, domingo = limites_semana(r["semana"])
    icono, texto = LUZ[r["semaforo"]]
    final = next((p for p in r["proyecciones"] if p["final"]), None)
    H = [f'<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
         f'<title>{e(r["proyecto"])} — Reporte PO semana {r["semana"][-2:]}</title><style>{CSS}</style>'
         f'<script src="{CHART_JS}"></script></head><body><main>']
    # 1. Portada
    H.append('<section class="card portada"><div>'
             f'<div class="muted">Gestión de Desarrollo de Software · Reporte del Product Owner</div>'
             f'<h1>{e(r["proyecto"])}</h1>'
             f'<div class="sub">Grupo: {e(", ".join(r["grupo"]))}</div>'
             f'<div class="sub">Semana {r["semana"][-2:]} · {lunes:%d/%m} al {domingo:%d/%m/%Y}</div>'
             f'<div class="muted" style="margin-top:8px">Fuente: {e(r["fuente"])}</div></div>'
             f'<div class="luz"><div class="icono" role="img" aria-label="{texto}">{icono}</div><div class="txt">{texto}</div>'
             '<div class="muted">semáforo general</div></div></section>')
    graves = [a for a in r["alertas"] if a["nivel"] == "alto"]
    if r["semaforo"] == "rojo" or any(a["titulo"] == "Tablero quieto" for a in r["alertas"]) or graves:
        clase = "" if r["semaforo"] == "rojo" or any(a["titulo"] == "Tablero quieto" for a in r["alertas"]) else " amarillo"
        H.append(f'<section class="card aviso{clase}"><strong>⚠️ {e(graves[0]["titulo"] if graves else "Atención")}.</strong> '
                 + (f'{e(graves[0]["evidencia"])} <strong>Propuesta:</strong> {e(graves[0]["accion"])}' if graves else "")
                 + "</section>")
    # 2. KPIs
    prom = r["velocidad_total_prom"]
    kpis = [(f"{r['sp_semana']:.0f}", "puntos terminados", f"{r['tareas_semana']} tareas"),
            (f"{prom:.0f}", "velocidad promedio (SP/sem., 3 semanas)", f"esta semana {r['sp_semana']:.0f} · solo el grupo del TP: {r['velocidad_tp']:.0f}"),
            (f"{r['avance']:.0%}", "avance total", f"{r['hecho_sp']:.0f} de {r['total_sp']:.0f} SP comprometidos"),
            (f"{final['semanas_restantes'] if final else '—'} / {final['semanas_necesarias'] if final and final['semanas_necesarias'] is not None else '∞'}",
             "semanas restantes / necesarias", f"entrega final {d(final['entrega']):%d/%m}" if final else ""),
            (str(r["bloqueadas"]), "tareas bloqueadas", f"espera de revisión promedio: {r['espera_revision'] if r['espera_revision'] is not None else '—'} días hábiles")]
    if costos:
        kpis.append((usd(costos["cargado"]), "costo cargado de la semana", f"entregado {usd(costos['entregado'])}"))
    H.append('<section class="kpis">' + "".join(
        f'<div class="card kpi"><div class="n">{n}</div><div class="l">{l}</div><div class="c">{c}</div></div>'
        for n, l, c in kpis) + "</section>")
    # 3. Lo que logramos
    grupos = defaultdict(list)
    for l in r["logros"]:
        grupos[l["historia"]].append(l)
    logros = "".join(f'<h3>{e(h)}</h3><ul class="logros">' + "".join(
        f'<li><span class="chk">✓</span>{e(x["titulo"])} <span class="muted">· {e(x["asignado"] or "")} · {x["sp"]} SP</span></li>'
        for x in xs) + "</ul>" for h, xs in grupos.items())
    epicas = "".join(f'<tr><td>{e(k)}</td><td><div class="barra"><i style="width:{(v["hecho"] / v["total"] * 100) if v["total"] else 0:.0f}%"></i></div></td>'
                     f'<td class="n">{v["hecho"]:.0f}/{v["total"]:.0f} SP</td></tr>' for k, v in r["epicas"].items())
    H.append('<section class="grid"><div class="card"><h2>Lo que logramos</h2>'
             + (logros or '<p class="muted">No se terminó nada esta semana.</p>') + "</div>"
             f'<div class="card"><h2>Avance por épica</h2><table><tr><th>Épica</th><th></th><th>SP</th></tr>{epicas}</table>'
             f'<p class="muted">Lead time promedio {r["lead_time"] if r["lead_time"] is not None else "—"} días · cycle time '
             f'{r["cycle_time"] if r["cycle_time"] is not None else "—"} días · alcance nuevo en la semana {r["scope_creep"]:.0f} SP.</p></div></section>')
    # 4-7. Gráficos
    H.append('<section class="grid">'
             '<div class="card"><h2>Burndown del alcance comprometido</h2><div class="chart"><canvas id="burndown"></canvas></div></div>'
             '<div class="card"><h2>Velocidad por semana</h2><div class="chart"><canvas id="velocidad"></canvas></div></div>'
             '<div class="card"><h2>Trabajo por integrante (SP terminados en la semana)</h2><div class="chart"><canvas id="personas"></canvas></div></div>'
             '<div class="card"><h2>Estado del tablero al cierre</h2><div class="chart"><canvas id="estado"></canvas></div></div>'
             "</section>")
    # Costos y Brooks
    if costos or brooks:
        H.append('<section class="grid">')
        if costos:
            ops = "".join(f'<tr><td><strong>{e(o["patron"])}</strong><br><span class="muted">{e(o["que_hacer"])}</span></td>'
                          f'<td class="n">{usd(o["costo"])}</td><td class="n">{usd(o["ahorro_semana"])}</td></tr>'
                          for o in costos["oportunidades"][:4])
            H.append('<div class="card"><h2>Costo de la semana</h2>'
                     f'<p>Cargado <strong>{usd(costos["cargado"])}</strong> · entregado {usd(costos["entregado"])} · '
                     f'no utilizado {usd(costos["no_utilizado"])} · '
                     f'{(usd(costos["costo_por_sp"]) + " por SP") if costos["costo_por_sp"] else "sin SP terminados"}.</p>'
                     f'<table><tr><th>Oportunidad</th><th>Costó</th><th>Ahorro/sem.</th></tr>{ops}</table>'
                     + ('<div class="chart" style="height:180px;margin-top:12px"><canvas id="costos"></canvas></div>' if hist_costos else "")
                     + "</div>")
        if brooks:
            filas = "".join(f'<tr><td>{"Equipo actual" if x["extra"] == 0 else "+" + str(x["extra"])}</td><td class="n">{x["canales"]}</td>'
                            f'<td>{(d(x["fin"]).strftime("%d/%m") + " (" + str(x["semanas"]) + " sem.)") if x["fin"] else "no termina"}</td>'
                            f'<td>{e(x["vs_hoy"])}</td></tr>' for x in brooks["escenarios"])
            solos = [c for c, v in brooks["bus_factor"].items() if v["bus"] == 1]
            H.append(f'<div class="card"><h2>Riesgo de Brooks: {brooks["diagnostico"]}</h2>'
                     f'<p>Ruta crítica <strong>{" → ".join(brooks["ruta_critica"]) or "—"}</strong> ({brooks["ruta_critica_sp"]:.0f} SP). '
                     f'Bus factor 1 en: {e(", ".join(solos)) or "ninguna carpeta"}.</p>'
                     f'<table><tr><th>Escenario</th><th>Canales</th><th>Fin estimado</th><th>vs. hoy</th></tr>{filas}</table></div>')
        H.append("</section>")
    # 8. Alertas
    filas = "".join(f'<tr><td class="nivel {a["nivel"]}">{"▲" if a["nivel"] == "alto" else "●" if a["nivel"] == "medio" else "·"} {a["nivel"]}</td>'
                    f'<td><strong>{e(a["titulo"])}</strong><br>{e(a["evidencia"])}</td><td>{e(a["accion"])}</td></tr>'
                    for a in r["alertas"])
    proy = "".join(f'<tr><td>{"Final" if p["final"] else "Parcial"} {d(p["entrega"]):%d/%m}</td><td class="n">{p["pendiente"]:.0f}</td>'
                   f'<td class="n">{p["semanas_restantes"]}</td><td class="n">{p["semanas_necesarias"] if p["semanas_necesarias"] is not None else "∞"}</td>'
                   f'<td>{LUZ[p["luz"]][0]} {LUZ[p["luz"]][1]}</td></tr>' for p in r["proyecciones"])
    H.append('<section class="card"><h2>Alertas y desvíos</h2>'
             f'<table><tr><th>Entrega</th><th>SP pendientes</th><th>Semanas que quedan</th><th>Semanas necesarias</th><th>Estado</th></tr>{proy}</table>'
             + (f'<table style="margin-top:14px"><tr><th>Nivel</th><th>Alerta y evidencia</th><th>Acción sugerida</th></tr>{filas}</table>'
                if filas else '<p style="margin-top:14px">✓ Sin alertas esta semana.</p>') + "</section>")
    # 9. Próxima semana
    prox = "".join(f'<tr><td>{e(t["id"])}</td><td>{e(t["titulo"])}</td><td>{e(t["asignado"])}</td><td class="n">{t["sp"]}</td>'
                   f'<td>{d(t["entrega"]).strftime("%d/%m") if t["entrega"] else "—"}</td>'
                   f'<td>{("destraba " + str(t["destraba"])) if t["destraba"] else ""}</td></tr>' for t in r["proxima"])
    H.append('<section class="card"><h2>Próxima semana: prioridades</h2>'
             + (f'<table><tr><th>Id</th><th>Tarea</th><th>Responsable</th><th>SP</th><th>Entrega</th><th></th></tr>{prox}</table>'
                if prox else '<p class="muted">No hay trabajo comprometido pendiente: cargar el backlog de la próxima entrega.</p>')
             + "</section>")
    H.append('<footer>Generado con la skill product-owner (cálculos en gestion/analisis/po.py). Story points según el tamaño '
             'real de cada PR; velocidad = promedio de las últimas 3 semanas de todo el equipo.</footer></main>')
    # Datos de los gráficos
    datos = dict(
        burn_labels=[etiqueta(x["semana"]) for x in r["ideal"]],
        burn_real=[x["pendiente"] for x in r["burndown"]],
        burn_ideal=[x["sp"] for x in r["ideal"]],
        vel_labels=[etiqueta(x["semana"]) for x in r["velocidad"]],
        vel_tp=[x["tp"] for x in r["velocidad"]],
        vel_otros=[x["total"] - x["tp"] for x in r["velocidad"]],
        pers_labels=list(r["por_persona"].keys()),
        pers_historia=[v.get("historia", 0) for v in r["por_persona"].values()],
        pers_tarea=[v.get("tarea", 0) + v.get("bug", 0) for v in r["por_persona"].values()],
        estado_labels=[NOMBRE_ESTADO[k] for k in ESTADOS], estado_vals=[r["estado_tablero"][k] for k in ESTADOS],
        costos_labels=[etiqueta(h["semana"]) for h in hist_costos], costos_cargado=[h["cargado"] for h in hist_costos],
        costos_ocioso=[h["no_utilizado"] for h in hist_costos],
    )
    H.append("<script>const D=" + json.dumps(datos, ensure_ascii=False) + ";" + """
if(window.Chart){
Chart.defaults.font.family='system-ui,-apple-system,"Segoe UI",Roboto,sans-serif';Chart.defaults.color='#52514e';
Chart.defaults.borderColor='#e4e2dc';Chart.defaults.maintainAspectRatio=false;Chart.defaults.plugins.legend.position='bottom';
const AZUL='#2a78d6',NARANJA='#eb6834',GRIS='#a3a29c';
new Chart(document.getElementById('burndown'),{type:'line',data:{labels:D.burn_labels,datasets:[
 {label:'Pendiente real (SP)',data:D.burn_real,borderColor:AZUL,backgroundColor:AZUL,borderWidth:2,pointRadius:4,tension:0},
 {label:'Ideal hasta la entrega final',data:D.burn_ideal,borderColor:GRIS,borderDash:[6,6],borderWidth:2,pointRadius:0}]},
 options:{interaction:{mode:'index',intersect:false},scales:{y:{beginAtZero:true,title:{display:true,text:'SP pendientes'}}}}});
new Chart(document.getElementById('velocidad'),{type:'bar',data:{labels:D.vel_labels,datasets:[
 {label:'Grupo del TP',data:D.vel_tp,backgroundColor:AZUL,borderRadius:4},
 {label:'Colaboradores',data:D.vel_otros,backgroundColor:NARANJA,borderRadius:4}]},
 options:{scales:{x:{stacked:true},y:{stacked:true,beginAtZero:true,title:{display:true,text:'SP terminados'}}}}});
new Chart(document.getElementById('personas'),{type:'bar',data:{labels:D.pers_labels,datasets:[
 {label:'Historias',data:D.pers_historia,backgroundColor:AZUL,borderRadius:4},
 {label:'Tareas técnicas',data:D.pers_tarea,backgroundColor:NARANJA,borderRadius:4}]},
 options:{indexAxis:'y',scales:{x:{stacked:true,beginAtZero:true,title:{display:true,text:'SP'}},y:{stacked:true}}}});
new Chart(document.getElementById('estado'),{type:'doughnut',data:{labels:D.estado_labels,datasets:[{data:D.estado_vals,
 backgroundColor:['#a3a29c','#2a78d6','#6250d6','#d03b3b','#0ca30c'],borderColor:'#fff',borderWidth:2}]},
 options:{cutout:'62%',plugins:{legend:{position:'right'}}}});
const c=document.getElementById('costos');if(c){new Chart(c,{type:'bar',data:{labels:D.costos_labels,datasets:[
 {label:'Cargado (USD)',data:D.costos_cargado,backgroundColor:GRIS,borderRadius:4},
 {label:'No utilizado (USD)',data:D.costos_ocioso,backgroundColor:NARANJA,borderRadius:4}]},
 options:{scales:{y:{beginAtZero:true}}}});}
}else{document.querySelectorAll('.chart').forEach(e=>e.innerHTML='<p class="muted">Los gráficos necesitan internet (Chart.js desde cdnjs).</p>');}
</script></body></html>""")
    return "".join(H)


def escribir_md(r, costos, brooks):
    lunes, domingo = limites_semana(r["semana"])
    icono, texto = LUZ[r["semaforo"]]
    L = [f"# Reporte del Product Owner — {r['proyecto']} — Semana {r['semana'][-2:]} ({lunes:%d/%m} al {domingo:%d/%m})", "",
         f"Grupo: {', '.join(r['grupo'])}. Fuente: {r['fuente']}.", "",
         f"## Resumen: {icono} {texto}", ""]
    graves = [a for a in r["alertas"] if a["nivel"] == "alto"]
    if graves:
        L += [f"> ⚠️ **{graves[0]['titulo']}.** {graves[0]['evidencia']} Propuesta: {graves[0]['accion']}", ""]
    L += ["| Métrica | Valor |", "|---|---|",
          f"| Puntos terminados | {r['sp_semana']:.0f} SP ({r['tareas_semana']} tareas) |",
          f"| Velocidad promedio de todo el equipo (3 semanas, usada en la proyección) | {r['velocidad_total_prom']} SP/semana |",
          f"| Velocidad promedio solo del grupo del TP | {r['velocidad_tp']} SP/semana |",
          f"| Avance total | {r['avance']:.0%} ({r['hecho_sp']:.0f} de {r['total_sp']:.0f} SP comprometidos) |",
          f"| Lead time / cycle time promedio | {r['lead_time'] if r['lead_time'] is not None else '—'} / "
          f"{r['cycle_time'] if r['cycle_time'] is not None else '—'} días |",
          f"| Espera de revisión promedio | {r['espera_revision'] if r['espera_revision'] is not None else '—'} días hábiles |",
          f"| Alcance nuevo en la semana | {r['scope_creep']:.0f} SP |",
          f"| Tareas bloqueadas | {r['bloqueadas']} |", "",
          "## Proyección por entrega", "",
          "| Entrega | SP pendientes | Semanas que quedan | Semanas necesarias | Necesarias solo con el grupo del TP | Estado |",
          "|---|---|---|---|---|---|"]
    for p in r["proyecciones"]:
        L.append(f"| {'Final' if p['final'] else 'Parcial'} {p['entrega']} | {p['pendiente']:.0f} | {p['semanas_restantes']} | "
                 f"{p['semanas_necesarias'] if p['semanas_necesarias'] is not None else '∞'} | "
                 f"{p['semanas_necesarias_tp'] if p['semanas_necesarias_tp'] is not None else '∞'} | {LUZ[p['luz']][0]} {LUZ[p['luz']][1]} |")
    L += ["", "## Lo que logramos", ""]
    grupos = defaultdict(list)
    for l in r["logros"]:
        grupos[l["historia"]].append(l)
    for h, xs in grupos.items():
        L.append(f"**{h}**")
        L += [f"- {x['titulo']} ({x['asignado']}, {x['sp']} SP)" for x in xs]
        L.append("")
    if not grupos:
        L += ["No se terminó nada esta semana.", ""]
    L += ["## Avance por épica", "", "| Épica | Terminado | Total |", "|---|---|---|"]
    L += [f"| {k} | {v['hecho']:.0f} SP | {v['total']:.0f} SP |" for k, v in r["epicas"].items()]
    L += ["", "## Alertas y desvíos", ""]
    L += [f"- **[{a['nivel']}] {a['titulo']}:** {a['evidencia']} → {a['accion']}" for a in r["alertas"]] or ["- Sin alertas."]
    if costos:
        L += ["", "## Costo", "", f"Cargado {usd(costos['cargado'])}, entregado {usd(costos['entregado'])}, no utilizado "
              f"{usd(costos['no_utilizado'])}. Detalle en `costos.md`."]
    if brooks:
        L += ["", "## Riesgo de Brooks", "", f"{brooks['diagnostico']} Ruta crítica {' → '.join(brooks['ruta_critica']) or '—'} "
              f"({brooks['ruta_critica_sp']:.0f} SP). Detalle en `brooks.md`."]
    L += ["", "## Próxima semana", ""]
    L += [f"{i}. {t['id']} — {t['titulo']} ({t['asignado']}, {t['sp']} SP)" for i, t in enumerate(r["proxima"], 1)] or \
         ["- Cargar el backlog de la próxima entrega."]
    L += ["", "## Limitaciones de datos", "",
          "- No hay horas registradas: los costos usan la equivalencia de SP de equipo.md.",
          "- Las semanas 44 a 46 se reconstruyeron desde git (fecha del commit = listo para revisión, merge = terminada); "
          "no hay registro de cuándo empezó cada tarea, así que el cycle time es el tiempo en revisión.",
          "- No hay tareas de reuniones ni bloqueos explícitos en el tablero.",
          "- El lead time de los tickets reconstruidos se mide desde el 26/10 (alcance planificado al arrancar), no desde "
          "una fecha de creación real.", ""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--semana", required=True)
    a = ap.parse_args()
    r = analizar(a.semana)
    carpeta = REPORTES / a.semana
    costos = leer_json(carpeta / "costos.json")
    brooks = leer_json(carpeta / "brooks.json")
    hist_c = [h for h in leer_json(REPORTES / "historico-costos.json", []) if h["semana"] <= a.semana]
    (carpeta / "reporte-po.html").write_text(escribir_html(r, costos, brooks, hist_c), encoding="utf-8")
    (carpeta / "reporte-po.md").write_text(escribir_md(r, costos, brooks), encoding="utf-8")
    hist = leer_json(REPORTES / "historico-po.json", [])
    fila = dict(semana=a.semana, semaforo=r["semaforo"], sp_terminados=r["sp_semana"], velocidad_tp=r["velocidad_tp"],
                avance=r["avance"], pendiente_sp=r["pendiente_sp"], alertas=len(r["alertas"]))
    hist = sorted([h for h in hist if h["semana"] != a.semana] + [fila], key=lambda h: h["semana"])
    guardar_json(REPORTES / "historico-po.json", hist)
    icono, texto = LUZ[r["semaforo"]]
    print(f"po {a.semana}: {icono} {texto} — {r['sp_semana']:.0f} SP en la semana, avance {r['avance']:.0%}, "
          f"{len(r['alertas'])} alertas → {(carpeta / 'reporte-po.html').relative_to(REPORTES.parent)}")


if __name__ == "__main__":
    main()
