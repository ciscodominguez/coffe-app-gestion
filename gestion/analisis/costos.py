#!/usr/bin/env python3
"""Cálculos de la skill revisor-costos (.claude/skills/revisor-costos/SKILL.md).

Lee reportes/<semana>/tareas-normalizadas.json + equipo.md y escribe:
  reportes/<semana>/costos.md     (estructura de la skill)
  reportes/<semana>/costos.json   (los números, para product-owner)
  reportes/historico-costos.json  (agrega la semana sin pisar las anteriores)

Uso: python gestion/analisis/costos.py --semana semana-2026-45
"""
import argparse
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import REPORTES, activos, dias_habiles, guardar_json, leer_equipo, leer_json, limites_semana, usd  # noqa: E402

FACTOR_CAMBIO_CONTEXTO = 0.15  # la skill: WIP alto = 15 % de las horas de la persona
UMBRAL_ESPERA = 2              # días hábiles esperando revisión para contar como bloqueo
ABIERTAS = ("en_curso", "en_revision", "bloqueada")


def d(x):
    return date.fromisoformat(x[:10]) if x else None


def analizar(semana):
    eq = leer_equipo()
    prm = eq["params"]
    datos = leer_json(REPORTES / semana / "tareas-normalizadas.json")
    if datos is None:
        sys.exit(f"Falta reportes/{semana}/tareas-normalizadas.json: corré antes gestion/normalizar.py")
    tareas, commits = datos["tareas"], datos["commits"]
    hasta = d(datos["hasta"])
    hora = prm["costo_mensual_usd"] / prm["horas_mes"]
    semanal = prm["costo_mensual_usd"] * 12 / 52
    hsp = prm["horas_por_sp"]
    supuestos = [
        f"Costo: {usd(prm['costo_mensual_usd'])[:-3]} por mes por integrante → {usd(hora)} la hora → {usd(semanal)} por "
        "semana (× 12 ÷ 52), multiplicado por la dedicación de equipo.md.",
        "Capacidad semanal = 40 h × dedicación.",
    ]
    con_horas = [t for t in tareas if t.get("horas_registradas")]
    if not con_horas:
        supuestos.append(f"Ninguna tarea tiene horas registradas: las horas se estiman con la equivalencia de "
                         f"equipo.md (1 SP = {hsp:g} h). Imputado = horas de lo terminado en la semana + de lo que "
                         "quedó abierto al cierre.")
    supuestos.append(f"Fuente: {datos['fuente']}.")

    def horas(t):
        return t["horas_registradas"] if t.get("horas_registradas") else (t["story_points"] or 0) * hsp

    hechas = [t for t in tareas if t["cerrada_en_semana"]]
    abiertas = [t for t in tareas if t["estado"] in ABIERTAS]
    por = defaultdict(lambda: dict(entregado_h=0.0, curso_h=0.0, sp=0.0, tareas=0, wip=[]))
    for t in hechas:
        p = por[t["asignado"]]
        p["entregado_h"] += horas(t)
        p["sp"] += t["story_points"] or 0
        p["tareas"] += 1
    for t in abiertas:
        p = por[t["asignado"]]
        p["curso_h"] += horas(t)
        p["wip"].append(t["id"])

    personas = []
    for i in activos(eq, hasta):
        ded = i["dedicacion_pct"] / 100
        x = por[i["clave"]]
        cargado = semanal * ded
        imputado_h = x["entregado_h"] + x["curso_h"]
        personas.append(dict(
            clave=i["clave"], nombre=i["nombre"], grupo=i["rol_tp"], dedicacion_pct=i["dedicacion_pct"],
            capacidad_h=round(40 * ded, 1), cargado=round(cargado, 2), horas=round(imputado_h, 1),
            imputado=round(imputado_h * hora, 2), entregado=round(x["entregado_h"] * hora, 2),
            en_curso=round(x["curso_h"] * hora, 2), no_utilizado=round(max(0.0, cargado - imputado_h * hora), 2),
            sp=x["sp"], tareas=x["tareas"], wip=x["wip"],
            commits=sum(1 for c in commits if c["autor"] == i["clave"]),
            revisiones=sum(1 for t in hechas if t.get("revisor") == i["clave"]),
        ))
    cargado = sum(p["cargado"] for p in personas)
    entregado = sum(p["entregado"] for p in personas)
    imputado = sum(p["imputado"] for p in personas)
    no_util = sum(p["no_utilizado"] for p in personas)
    sp = sum(p["sp"] for p in personas)
    infra_sem = sum(s["costo_mensual_usd"] for s in eq["infra"]) * 12 / 52
    horas_tot = sum(p["horas"] for p in personas)

    oportunidades = []

    def op(patron, que, costo, hacer, ahorro):
        oportunidades.append(dict(patron=patron, que_paso=que, costo=round(costo, 2), que_hacer=hacer,
                                  ahorro_semana=round(ahorro, 2)))

    # 1. Retrabajo: commits vueltos a aplicar con otro hash (reescritura de main).
    rehechos = [c for c in commits if c.get("copias")]
    if rehechos:
        n = sum(len(c["copias"]) for c in rehechos)
        lineas = sum(c["lineas"] for c in rehechos)
        op("Retrabajo",
           f"{n} commits de la semana están dos veces en el repo con distinto hash ({lineas} líneas): la historia de "
           "main se corrigió y se volvieron a aplicar. No hay horas registradas del arreglo; se toma 1 h por commit "
           "(supuesto).", n * hora,
           "Proteger main en GitHub (solo merge por PR, sin force-push) para no tener que rehacer historia.",
           n * hora)
    # 3. Trabajo bloqueado: PRs que esperaron revisión (terminados en la semana o todavía esperando).
    esperas = []
    for t in tareas:
        lr = d(t.get("listo_revision"))
        if not lr or lr > d(datos["corte"]):
            continue
        if t["estado"] == "terminada" and not t["cerrada_en_semana"]:
            continue
        fin = d(t["terminada"]) if t["estado"] == "terminada" else d(datos["corte"])
        dias = dias_habiles(lr, fin)
        if dias >= UMBRAL_ESPERA:
            esperas.append((t, dias))
    if esperas:
        costo = 0.0
        for t, dias in esperas:
            p = next((x for x in personas if x["clave"] == t["asignado"]), None)
            diario = (p["cargado"] / 5) if p else semanal / 5
            costo += dias * diario * FACTOR_CAMBIO_CONTEXTO
        op("Trabajo bloqueado",
           "PRs listos que esperaron revisión: " + "; ".join(f"{t['id']} {dias} días hábiles" for t, dias in esperas)
           + ". Costo de la espera = días × costo diario del autor × 15 % (retomar contexto, rebase).",
           costo, "Acordar que todo PR se revisa en menos de 24 h y nombrar el revisor al abrirlo.", costo)
    # 4. WIP alto.
    for p in personas:
        if len(p["wip"]) > 2:
            c = p["cargado"] * FACTOR_CAMBIO_CONTEXTO
            op("WIP alto", f"{p['nombre']} terminó la semana con {len(p['wip'])} tareas abiertas ({', '.join(p['wip'])}).",
               c, "Máximo 2 tareas en curso por persona: terminar antes de empezar.", c)
    # 5. Capacidad ociosa.
    for p in personas:
        if p["dedicacion_pct"] and p["no_utilizado"] >= 0.5 * p["cargado"]:
            sin_nada = p["horas"] == 0 and p["commits"] == 0
            op("Capacidad ociosa",
               f"{p['nombre']} tiene {usd(p['cargado'])} de costo cargado y {usd(p['imputado'])} imputado"
               + ((f" (sin tareas propias ni commits; hizo {p['revisiones']} revisiones de PRs, que no tienen horas "
                   "cargadas)." if p["revisiones"] else " (ninguna tarea movida ni commits en la semana).")
                  if sin_nada else "."),
               p["no_utilizado"],
               "Asignarle tickets del ciclo o revisiones; si trabaja en algo que no está en el tablero, cargarlo; "
               "si no va a trabajar, bajar su dedicación en equipo.md.", p["no_utilizado"])
    # 6. Desbalance.
    if horas_tot:
        top = max(personas, key=lambda p: p["horas"])
        if top["horas"] / horas_tot > 0.4:
            op("Desbalance",
               f"{top['nombre']} concentra {top['horas'] / horas_tot:.0%} de las horas del grupo ({top['horas']:.0f} de "
               f"{horas_tot:.0f} h estimadas).", 0.0,
               "Repartir el próximo ciclo; revisión cruzada para que otro conozca ese código.", 0.0)
    # 7. Reuniones: no hay tareas de tipo reunión (va a calidad de datos).
    # 8. Trabajo fuera de alcance.
    fuera = [t for t in hechas if not t.get("historia") or t.get("entrega") == "deseable"]
    if fuera:
        c = sum(horas(t) for t in fuera) * hora
        op("Trabajo fuera de alcance", f"Se terminó trabajo marcado como deseable: {', '.join(t['id'] for t in fuera)}.",
           c, "Priorizar lo comprometido para la próxima entrega antes que lo deseable.", 0.0)
    # 9. Infraestructura.
    for s in eq["infra"]:
        alt = s.get("alternativa_gratuita", "")
        if s["costo_mensual_usd"] > 0 and alt and "⚠️" not in alt:
            c = s["costo_mensual_usd"] * 12 / 52
            op("Infraestructura", f"{s['servicio']}: {usd(s['costo_mensual_usd'])} por mes.", c, f"Evaluar {alt}.", c)

    sobre = [p for p in personas if p["imputado"] > p["cargado"] * 1.2]
    calidad = dict(
        tareas_sin_horas=sum(1 for t in hechas + abiertas if not t.get("horas_registradas")),
        sobrecarga=[p["nombre"] for p in sobre],
        reuniones="No hay tareas de tipo reunión en el tablero: no se puede medir el tiempo de coordinación.",
        estimacion="Sin horas registradas no se puede medir el desvío de estimación ni la subestimación crónica.",
    )
    top10 = sorted(hechas + abiertas, key=lambda t: -horas(t))[:10]
    return dict(
        semana=semana, desde=datos["desde"], hasta=datos["hasta"], fuente=datos["fuente"],
        costo_hora=round(hora, 2), costo_semanal=round(semanal, 2), horas_por_sp=hsp,
        cargado=round(cargado, 2), entregado=round(entregado, 2), imputado=round(imputado, 2),
        no_utilizado=round(no_util, 2), sp_terminados=sp, costo_por_sp=round(cargado / sp, 2) if sp else None,
        infra_semana=round(infra_sem, 2), personas=personas,
        tareas=[dict(id=t["id"], titulo=t["titulo"], asignado=t["asignado"], sp=t["story_points"],
                     estimado_h=horas(t), costo=round(horas(t) * hora, 2), estado=t["estado"]) for t in top10],
        oportunidades=oportunidades, ahorro_semana=round(sum(o["ahorro_semana"] for o in oportunidades), 2),
        calidad=calidad, supuestos=supuestos,
    )


def escribir_md(r, eq):
    nom = {p["clave"]: p["nombre"] for p in eq["integrantes"]}
    lunes, domingo = limites_semana(r["semana"])
    pct = lambda a, b: f"{a / b:.0%}" if b else "—"  # noqa: E731
    L = [f"# Revisión de costos — Semana {r['semana'][-2:]} ({lunes:%d/%m} al {domingo:%d/%m})", "",
         "## Resumen",
         f"- Costo cargado del grupo: {usd(r['cargado'])}",
         f"- Costo entregado (trabajo terminado): {usd(r['entregado'])} ({pct(r['entregado'], r['cargado'])} del cargado)",
         f"- Costo imputado (terminado + en curso): {usd(r['imputado'])}",
         f"- Capacidad no utilizada: {usd(r['no_utilizado'])}",
         f"- Costo por story point: {usd(r['costo_por_sp']) if r['costo_por_sp'] else 'sin SP terminados'}"
         + (f" ({usd(r['cargado'])} ÷ {r['sp_terminados']:.0f} SP)" if r["costo_por_sp"] else ""),
         f"- Infraestructura (semana): {usd(r['infra_semana'])}",
         f"- Calidad de datos: {r['calidad']['tareas_sin_horas']} tareas sin horas registradas", "",
         "## Costo por integrante",
         "| Integrante | Grupo | Dedicación | Costo cargado | Horas | Costo imputado | Entregado | No utilizado |",
         "|---|---|---|---|---|---|---|---|"]
    for p in r["personas"]:
        L.append(f"| {p['nombre']} | {p['grupo']} | {p['dedicacion_pct']:.0f} % | {usd(p['cargado'])} | {p['horas']:.0f} h* | "
                 f"{usd(p['imputado'])} | {usd(p['entregado'])} | {usd(p['no_utilizado'])} |")
    L += ["", "\\* horas estimadas con la equivalencia de story points (no hay horas registradas).", "",
          "## Costo por tarea (top 10 por costo)",
          "| Tarea | Responsable | Estimado | Real | Desvío | Costo USD | Estado |", "|---|---|---|---|---|---|---|"]
    for t in r["tareas"]:
        L.append(f"| {t['id']} — {t['titulo']} | {nom.get(t['asignado'], t['asignado'] or 'sin asignar')} | "
                 f"{t['estimado_h']:.0f} h ({t['sp']} SP) | sin registro | — | {usd(t['costo'])} | {t['estado']} |")
    L += ["", "## Oportunidades de optimización"]
    if not r["oportunidades"]:
        L.append("Sin oportunidades detectadas esta semana.")
    for i, o in enumerate(r["oportunidades"], 1):
        L.append(f"{i}. **{o['patron']}** — {o['que_paso']} Costo: {usd(o['costo'])}. {o['que_hacer']} "
                 f"Ahorro estimado: {usd(o['ahorro_semana'])}/semana.")
    L += ["", "## Supuestos"] + [f"- {s}" for s in r["supuestos"]]
    L += [f"- {r['calidad']['reuniones']}", f"- {r['calidad']['estimacion']}"]
    if r["calidad"]["sobrecarga"]:
        L.append(f"- El costo imputado supera al cargado en: {', '.join(r['calidad']['sobrecarga'])}. Con 1 SP = "
                 f"{r['horas_por_sp']:g} h lo entregado no entra en la dedicación declarada: o trabajaron más horas de "
                 "las declaradas, o la equivalencia de SP es alta para este equipo. Conviene registrar horas reales.")
    ratio = r["entregado"] / r["cargado"] if r["cargado"] else 0
    if ratio >= 0.7:
        neg = (f"Como empresa, la semana se justifica: de {usd(r['cargado'])} pagados, {usd(r['entregado'])} se "
               "convirtieron en trabajo terminado (valuado a la equivalencia de SP).")
    elif ratio >= 0.3:
        neg = (f"Como empresa, la semana se justifica a medias: se pagaron {usd(r['cargado'])} y solo "
               f"{usd(r['entregado'])} terminaron entregados; el resto quedó en curso o sin usar.")
    else:
        neg = (f"Como empresa, la semana no se justifica: se pagaron {usd(r['cargado'])} y se entregaron "
               f"{usd(r['entregado'])}. La plata se fue en capacidad sin usar y trabajo que no cerró.")
    if r["calidad"]["sobrecarga"]:
        neg += (" Ojo: lo entregado supera lo que permite la dedicación declarada, así que el resultado real depende "
                "de cuántas horas se trabajaron de verdad.")
    L += ["", "## Conclusión", neg, ""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--semana", required=True)
    a = ap.parse_args()
    eq = leer_equipo()
    r = analizar(a.semana)
    carpeta = REPORTES / a.semana
    (carpeta / "costos.md").write_text(escribir_md(r, eq), encoding="utf-8")
    guardar_json(carpeta / "costos.json", r)
    hist = leer_json(REPORTES / "historico-costos.json", [])
    fila = {k: r[k] for k in ("semana", "cargado", "entregado", "imputado", "no_utilizado", "sp_terminados",
                              "costo_por_sp", "infra_semana", "ahorro_semana")}
    hist = sorted([h for h in hist if h["semana"] != a.semana] + [fila], key=lambda h: h["semana"])
    guardar_json(REPORTES / "historico-costos.json", hist)
    print(f"costos {a.semana}: cargado {usd(r['cargado'])}, entregado {usd(r['entregado'])}, "
          f"{len(r['oportunidades'])} oportunidades, ahorro {usd(r['ahorro_semana'])}/semana")


if __name__ == "__main__":
    main()
