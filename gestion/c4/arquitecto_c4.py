#!/usr/bin/env python3
"""arquitecto-c4: genera y mantiene el modelo C4 de COFFE_APP en docs/arquitectura/.

Lee el código directamente de git (no hace falta checkout), así que puede analizar cualquier commit:
  - backend Spring Boot: paquetes de com.cofeapp.backend, sus controllers (@RestController +
    @RequestMapping), services y repositories, y las dependencias entre paquetes (campos `private final`);
  - frontend Angular: features (pantallas), services de core/ que llaman a la API (ApiService) o al
    tiempo real (STOMP), y qué service usa cada pantalla (inject() o constructor);
  - deploy/: proxy Caddy y backups, si existen.

Primera corrida: genera todo. Corridas siguientes: mira el diff entre el último commit analizado
(docs/arquitectura/estado.json) y el commit pedido, recalcula el modelo, regenera SOLO los diagramas
cuyo contenido cambió y agrega una entrada al CHANGELOG.md.

Uso (desde la raíz del repo):
    python gestion/c4/arquitecto_c4.py                 # analiza HEAD
    python gestion/c4/arquitecto_c4.py --commit 3c4df30
    python gestion/c4/arquitecto_c4.py --forzar        # regenera todo aunque no haya cambios
"""
import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DOCS = RAIZ / "docs" / "arquitectura"
ESTADO = DOCS / "estado.json"
MODELO = DOCS / "modelo.json"
CHANGELOG = DOCS / "CHANGELOG.md"
JAVA = "backend/src/main/java/com/cofeapp/backend/"
APP = "frontend/src/app/"
RELEVANTE = ("backend/src/main/", "frontend/src/app/", "deploy/", "backend/pom.xml", "frontend/package.json")

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

NOMBRES = {
    "auth": "Autenticación", "business": "Negocios", "user": "Usuarios", "location": "Locales",
    "category": "Categorías", "product": "Productos", "option": "Variantes y agregados", "table": "Mesas",
    "floor": "Plano del salón", "order": "Pedidos", "cash": "Caja", "discount": "Descuentos", "stock": "Stock",
    "mercadopago": "Cobros QR (Mercado Pago)", "dashboard": "Panel de inicio", "report": "Reportes",
    "billing": "Suscripción", "platform": "Superadmin", "legal": "Legales", "support": "Soporte",
    "media": "Imágenes", "channel": "Canales de venta", "security": "Seguridad y multi-tenant",
    "mail": "Mail", "excel": "Exportación Excel", "realtime": "Tiempo real (STOMP)", "crypto": "Cifrado",
}
DIAGRAMAS = {"contexto": "c4-1-contexto.md", "contenedores": "c4-2-contenedores.md",
             "backend": "c4-3-componentes-backend.md", "frontend": "c4-3-componentes-frontend.md"}


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, cwd=RAIZ, check=True).stdout


def leer(commit, ruta):
    try:
        return git("show", f"{commit}:{ruta}")
    except subprocess.CalledProcessError:
        return ""


def paquete_de(ruta):
    """backend/.../backend/order/dto/X.java -> 'order'; common/mail -> 'mail'; config/WebSocketConfig -> 'realtime'."""
    partes = ruta[len(JAVA):].split("/")
    if len(partes) == 1:
        return None
    p = partes[0]
    if p == "common":
        sub = partes[1] if len(partes) > 2 else "common"
        return {"tenant": "security", "context": "security", "exception": None}.get(sub, sub)
    if p == "config":
        nombre = partes[-1]
        if "WebSocket" in nombre:
            return "realtime"
        if "Security" in nombre:
            return "security"
        return None
    if p in ("domain", "enums"):
        return None
    return p


def analizar_backend(commit, archivos):
    clases = {}  # nombre -> paquete
    info = defaultdict(lambda: dict(controllers=[], services=[], repositories=[], rutas=[], otros=[]))
    fuentes = {}
    entidades = 0
    for f in archivos:
        if not (f.startswith(JAVA) and f.endswith(".java")) or "/dto/" in f:
            continue
        nombre = Path(f).stem
        if f.startswith(JAVA + "domain/"):
            if "/enums/" not in f:
                entidades += 1
            continue
        pkg = paquete_de(f)
        if not pkg:
            continue
        src = leer(commit, f)
        fuentes[nombre] = (pkg, src)
        clases[nombre] = pkg
    for nombre, (pkg, src) in fuentes.items():
        i = info[pkg]
        if re.search(r"^@RestController\s*$", src, re.M):
            i["controllers"].append(nombre)
            m = re.search(r'^@RequestMapping\(\s*(?:value\s*=\s*)?"([^"]+)"', src, re.M)
            prefijos = [m.group(1)] if m else sorted({"/" + x for x in re.findall(
                r'@(?:Get|Post|Put|Patch|Delete)Mapping\(\s*(?:value\s*=\s*)?"/([\w\-]+)', src)})
            for r in prefijos:
                if r not in i["rutas"]:
                    i["rutas"].append(r)
        elif nombre.endswith("Repository") or re.search(r"extends\s+JpaRepository", src):
            i["repositories"].append(nombre)
        elif nombre.endswith("Service") or "@Service" in src:
            i["services"].append(nombre)
        else:
            i["otros"].append(nombre)
    deps = set()
    for nombre, (pkg, src) in fuentes.items():
        for tipo in re.findall(r"private\s+final\s+([A-Z]\w+)\s+\w+\s*;", src):
            destino = clases.get(tipo)
            if destino and destino != pkg:
                deps.add((pkg, destino))
    externos = set()
    for nombre, (pkg, src) in fuentes.items():
        if pkg == "mercadopago" and "Client" in nombre:
            externos.add("mercadopago_api")
        if pkg == "mail" and ("JavaMailSender" in src or "MailSender" in src):
            externos.add("smtp")
    for v in info.values():
        for k in ("controllers", "services", "repositories", "rutas", "otros"):
            v[k].sort()
    return dict(paquetes={k: info[k] for k in sorted(info)}, dependencias=sorted(deps),
                externos=sorted(externos), entidades=entidades)


def analizar_frontend(commit, archivos):
    servicios, pantallas = {}, defaultdict(set)
    ts = [f for f in archivos if f.startswith(APP) and f.endswith(".ts") and not f.endswith(".spec.ts")]
    for f in ts:
        if f.endswith(".service.ts"):
            src = leer(commit, f)
            clase = re.search(r"export class (\w+)", src)
            if not clase:
                continue
            usos = re.findall(r"this\.api\.\w+(?:<[^>]*>)?\(\s*[`'\"](/[\w\-/${}.]+)", src)
            usos += re.findall(r"this\.http\.\w+(?:<[^>]*>)?\(\s*`\$\{[^}]*(?:apiBaseUrl|baseUrl)[^}]*\}(/[\w\-/${}.]+)", src)
            rutas = sorted({"/" + m.split("/")[1] for m in usos if len(m.split("/")) > 1})
            tipo = "http" if rutas else "realtime" if "stomp" in src.lower() else "ui"
            if "offline" in f:
                tipo = "offline"
            if Path(f).name == "api.service.ts":
                tipo = "api"
            servicios[clase.group(1)] = dict(archivo=f[len(APP):], tipo=tipo, rutas=rutas)
    for f in ts:
        if not f.startswith(APP + "features/"):
            continue
        feature = f[len(APP + "features/"):].split("/")[0]
        src = leer(commit, f)
        usados = set(re.findall(r"inject\(\s*(\w+)\s*\)", src)) | set(
            re.findall(r"(?:private|public|protected)\s+(?:readonly\s+)?\w+\s*:\s*(\w+Service)\b", src))
        for u in usados:
            if u in servicios:
                pantallas[feature].add(u)
        pantallas.setdefault(feature, set())
    return dict(servicios=dict(sorted(servicios.items())),
                pantallas={k: sorted(v) for k, v in sorted(pantallas.items())})


def analizar(commit):
    archivos = git("ls-tree", "-r", "--name-only", commit).splitlines()
    back = analizar_backend(commit, archivos)
    front = analizar_frontend(commit, archivos)
    deploy = dict(caddy=any(f.startswith("deploy/") and "Caddyfile" in f for f in archivos),
                  backups=any(f.startswith("deploy/scripts/") and "backup" in f.lower() for f in archivos),
                  compose=any(f.startswith("deploy/") and f.endswith("docker-compose.yml") for f in archivos))
    return dict(commit=git("rev-parse", "--short", commit).strip(),
                fecha_commit=git("log", "-1", "--format=%aI", commit).strip(), backend=back, frontend=front,
                deploy=deploy)


# ------------------------------------------------------------------ Mermaid

def nom(pkg):
    return NOMBRES.get(pkg, pkg.capitalize())


def md_contexto(m):
    ext = m["backend"]["externos"]
    L = ["# C4 · Nivel 1 — Contexto", "", f"Generado por la skill `arquitecto-c4` desde el commit `{m['commit']}`.", "",
         "```mermaid", "C4Context", "  title COFFE_APP — diagrama de contexto",
         '  Person(dueno, "Dueño / encargado", "Arma la carta, controla caja, stock y reportes")',
         '  Person(mozo, "Mozo", "Toma pedidos en las mesas desde el celular")',
         '  Person(cocina, "Cocina / barra", "Ve los pedidos en la pantalla de cocina (KDS)")',
         '  Person(cajero, "Cajero", "Cobra y cierra la caja")']
    if "platform" in m["backend"]["paquetes"]:
        L.append('  Person(superadmin, "Superadmin", "Administra los cafés clientes y sus planes")')
    L.append('  System(coffe, "COFFE_APP", "Sistema de gestión para cafés: pedidos, cocina, caja, stock y cobros")')
    if "mercadopago_api" in ext:
        L.append('  System_Ext(mp, "Mercado Pago", "Cobros con QR y débito de la suscripción")')
    if "smtp" in ext:
        L.append('  System_Ext(smtp, "Servidor de mail", "Recuperar contraseña y avisos")')
    if m["deploy"]["backups"]:
        L.append('  System_Ext(nube, "Almacenamiento externo", "Copias de seguridad nocturnas (rclone)")')
    L += ['  Rel(dueno, coffe, "Gestiona el negocio")', '  Rel(mozo, coffe, "Carga pedidos")',
          '  Rel(cocina, coffe, "Prepara y avanza pedidos")', '  Rel(cajero, coffe, "Cobra")']
    if "platform" in m["backend"]["paquetes"]:
        L.append('  Rel(superadmin, coffe, "Activa y suspende cafés")')
    if "mercadopago_api" in ext:
        L.append('  Rel(coffe, mp, "Crea cobros QR y recibe webhooks", "HTTPS")')
    if "smtp" in ext:
        L.append('  Rel(coffe, smtp, "Envía mails", "SMTP")')
    if m["deploy"]["backups"]:
        L.append('  Rel(coffe, nube, "Sube copias", "rclone")')
    L += ["```", ""]
    return "\n".join(L)


def md_contenedores(m):
    ext = m["backend"]["externos"]
    rt = "realtime" in m["backend"]["paquetes"]
    caddy = m["deploy"]["caddy"]
    L = ["# C4 · Nivel 2 — Contenedores", "", f"Generado por la skill `arquitecto-c4` desde el commit `{m['commit']}`.", "",
         "```mermaid", "C4Container", "  title COFFE_APP — contenedores",
         '  Person(usuario, "Personal del café", "Dueño, mozo, cocina y cajero")',
         '  System_Boundary(sistema, "COFFE_APP") {',
         '    Container(spa, "App web", "Angular", "Pantallas por rol; cola de pedidos sin conexión en el navegador")']
    if caddy:
        L.append('    Container(proxy, "Proxy", "Caddy", "HTTPS automático; sirve la app y reenvía /api")')
    L += [f'    Container(api, "API", "Spring Boot (Java)", "REST multi-tenant con JWT{" y tiempo real STOMP sobre WebSocket" if rt else ""}")',
          f'    ContainerDb(db, "Base de datos", "MySQL + Flyway", "{m["backend"]["entidades"]} entidades; datos separados por café")']
    if m["deploy"]["backups"]:
        L.append('    Container(backup, "Copias de seguridad", "Script + rclone", "Backup nocturno y prueba de restauración")')
    L.append("  }")
    if "mercadopago_api" in ext:
        L.append('  System_Ext(mp, "Mercado Pago", "API de cobros")')
    if "smtp" in ext:
        L.append('  System_Ext(smtp, "Servidor de mail", "SMTP")')
    if caddy:
        L += ['  Rel(usuario, proxy, "Entra a la app", "HTTPS")', '  Rel(proxy, spa, "Sirve los archivos de la app")',
              f'  Rel(spa, proxy, "Llama a /api{" y abre el WebSocket" if rt else ""}", "JSON/HTTPS{", WSS" if rt else ""}")',
              f'  Rel(proxy, api, "Reenvía /api{" y /ws" if rt else ""}", "HTTP")']
        L += ['  UpdateRelStyle(proxy, spa, $offsetY="-40")', '  UpdateRelStyle(spa, proxy, $offsetY="20")']
    else:
        L += ['  Rel(usuario, spa, "Usa", "HTTPS")', '  Rel(spa, api, "Llama", "JSON/HTTPS")']
        if rt:
            L += ['  Rel(api, spa, "Avisa cambios de pedidos", "STOMP/WebSocket")',
                  '  UpdateRelStyle(spa, api, $offsetY="-40")', '  UpdateRelStyle(api, spa, $offsetY="30")']
    L.append('  Rel(api, db, "Lee y escribe", "JPA")')
    if "mercadopago_api" in ext:
        L.append('  Rel(api, mp, "Cobros QR / webhooks", "HTTPS")')
    if "smtp" in ext:
        L.append('  Rel(api, smtp, "Envía mails", "SMTP")')
    if m["deploy"]["backups"]:
        L.append('  Rel(backup, db, "Vuelca la base", "mysqldump")')
    L += ['  UpdateLayoutConfig($c4ShapeInRow="4", $c4BoundaryInRow="1")', "```", ""]
    return "\n".join(L)


def md_backend(m):
    b = m["backend"]
    L = ["# C4 · Nivel 3 — Componentes de la API (Spring Boot)", "",
         f"Generado por la skill `arquitecto-c4` desde el commit `{m['commit']}`. Cada componente es un paquete de "
         "`com.cofeapp.backend` (controller → service → repository); las flechas son dependencias reales entre "
         "paquetes (campos inyectados).", "", "```mermaid", "flowchart LR",
         '  spa["App web<br/>[Container: Angular]"]', '  subgraph API["API · Spring Boot"]']
    for pkg, i in b["paquetes"].items():
        detalle = []
        if i["rutas"]:
            detalle.append(" ".join(i["rutas"]))
        if i["controllers"] or i["services"] or i["repositories"]:
            detalle.append(f'{len(i["controllers"])}C · {len(i["services"])}S · {len(i["repositories"])}R')
        else:
            detalle.append(f'{len(i["otros"])} clase(s) de soporte')
        L.append(f'    {pkg}["<b>{nom(pkg)}</b><br/>{"<br/>".join(detalle)}"]')
    L.append("  end")
    L.append(f'  db[("MySQL<br/>{b["entidades"]} entidades")]')
    if "mercadopago_api" in b["externos"]:
        L.append('  mp(["Mercado Pago<br/>[Sistema externo]"])')
    if "smtp" in b["externos"]:
        L.append('  smtp(["Servidor de mail<br/>[Sistema externo]"])')
    L.append('  spa -->|"REST + JWT"| API')
    L.append('  API -->|"JPA"| db')
    transversales = {"security"}
    usan_seg = sorted({a for a, z in b["dependencias"] if z in transversales})
    for a, z in b["dependencias"]:
        if z not in transversales:
            L.append(f"  {a} --> {z}")
    if "mercadopago_api" in b["externos"]:
        L.append('  mercadopago -->|"HTTPS"| mp')
    if "smtp" in b["externos"]:
        L.append('  mail -->|"SMTP"| smtp')
    L += ["```", ""]
    if usan_seg:
        L += [f"Seguridad y multi-tenant es transversal: la usan {len(usan_seg)} componentes "
              f"({', '.join(nom(x) for x in usan_seg)}); esas flechas no se dibujan para que el diagrama se lea.", ""]
    L += ["C = controllers, S = services, R = repositories. Detalle por paquete:", "",
          "| Componente | Rutas | Controllers | Services | Repositories |", "|---|---|---|---|---|"]
    for pkg, i in b["paquetes"].items():
        L.append(f"| {nom(pkg)} (`{pkg}`) | {', '.join(i['rutas']) or '—'} | {', '.join(i['controllers']) or '—'} | "
                 f"{', '.join(i['services']) or '—'} | {', '.join(i['repositories']) or '—'} |")
    L.append("")
    return "\n".join(L)


def md_frontend(m):
    f = m["frontend"]
    http = {k: v for k, v in f["servicios"].items() if v["tipo"] in ("http", "realtime", "offline")}
    ui = [k for k, v in f["servicios"].items() if v["tipo"] == "ui"]
    L = ["# C4 · Nivel 3 — Componentes de la app web (Angular)", "",
         f"Generado por la skill `arquitecto-c4` desde el commit `{m['commit']}`. Pantallas (features) a la izquierda, "
         "services de `core/` a la derecha; las flechas salen de `inject()` / constructor.", "",
         "```mermaid", "flowchart LR", '  subgraph Pantallas["Pantallas · features/"]']
    for p in f["pantallas"]:
        L.append(f'    f_{p.replace("-", "_")}["{p}"]')
    L += ["  end", '  subgraph Servicios["Services · core/"]']
    for s, v in http.items():
        etiqueta = " ".join(v["rutas"]) if v["rutas"] else {"realtime": "STOMP", "offline": "cola local"}[v["tipo"]]
        L.append(f'    s_{s}["{s}<br/>{etiqueta}"]')
    if ui:
        L.append(f'    s_ui["Servicios de interfaz ({len(ui)})"]')
    L += ["  end", '  api["API<br/>[Container: Spring Boot]"]']
    for p, servs in f["pantallas"].items():
        destinos = sorted({s if s in http else "ui" for s in servs if s in http or s in ui})
        for s in destinos:
            L.append(f'  f_{p.replace("-", "_")} --> s_{s}')
    for s, v in http.items():
        L.append(f'  s_{s} -->|"{"STOMP" if v["tipo"] == "realtime" else "HTTP"}"| api' if v["tipo"] != "offline"
                 else f"  s_{s} -.-> s_OrderService" if "OrderService" in http else f"  s_{s} --> api")
    L += ["```", "", "| Service | Tipo | Rutas de la API |", "|---|---|---|"]
    for s, v in f["servicios"].items():
        L.append(f"| {s} | {v['tipo']} | {', '.join(v['rutas']) or '—'} |")
    L.append("")
    return "\n".join(L)


GENERADORES = {"contexto": md_contexto, "contenedores": md_contenedores, "backend": md_backend, "frontend": md_frontend}


def claves_diagrama(m):
    """Lo que cada diagrama muestra, para saber si cambió."""
    b, f = m["backend"], m["frontend"]
    return {
        "contexto": [sorted(b["externos"]), "platform" in b["paquetes"], m["deploy"]["backups"]],
        "contenedores": [sorted(b["externos"]), "realtime" in b["paquetes"], m["deploy"], b["entidades"]],
        "backend": [b["paquetes"], b["dependencias"], b["externos"], b["entidades"]],
        "frontend": [f["servicios"], f["pantallas"]],
    }


def diferencias(viejo, nuevo):
    cambios = []
    vb, nb = viejo["backend"], nuevo["backend"]
    for p in sorted(set(nb["paquetes"]) - set(vb["paquetes"])):
        cambios.append(f"Componente nuevo en la API: **{nom(p)}** (`{p}`, rutas {', '.join(nb['paquetes'][p]['rutas']) or '—'}).")
    for p in sorted(set(vb["paquetes"]) - set(nb["paquetes"])):
        cambios.append(f"Componente eliminado de la API: **{nom(p)}** (`{p}`).")
    for p in sorted(set(vb["paquetes"]) & set(nb["paquetes"])):
        a, z = vb["paquetes"][p], nb["paquetes"][p]
        for k, txt in (("controllers", "controllers"), ("services", "services"), ("repositories", "repositories"),
                       ("rutas", "rutas")):
            mas, menos = sorted(set(z[k]) - set(a[k])), sorted(set(a[k]) - set(z[k]))
            if mas:
                cambios.append(f"{nom(p)}: {txt} nuevos {', '.join(mas)}.")
            if menos:
                cambios.append(f"{nom(p)}: {txt} quitados {', '.join(menos)}.")
    dv, dn = set(map(tuple, vb["dependencias"])), set(map(tuple, nb["dependencias"]))
    for a, z in sorted(dn - dv):
        cambios.append(f"Dependencia nueva: {nom(a)} → {nom(z)}.")
    for a, z in sorted(dv - dn):
        cambios.append(f"Dependencia quitada: {nom(a)} → {nom(z)}.")
    for e in sorted(set(nb["externos"]) - set(vb["externos"])):
        cambios.append(f"Sistema externo nuevo: {e}.")
    if nb["entidades"] != vb["entidades"]:
        cambios.append(f"Entidades JPA: {vb['entidades']} → {nb['entidades']}.")
    for k in ("caddy", "backups", "compose"):
        if nuevo["deploy"][k] and not viejo["deploy"][k]:
            cambios.append(f"Despliegue: aparece {k} en deploy/.")
    vf, nf = viejo["frontend"], nuevo["frontend"]
    for p in sorted(set(nf["pantallas"]) - set(vf["pantallas"])):
        cambios.append(f"Pantalla nueva en la app: **{p}**.")
    for p in sorted(set(vf["pantallas"]) - set(nf["pantallas"])):
        cambios.append(f"Pantalla quitada de la app: **{p}**.")
    for s in sorted(set(nf["servicios"]) - set(vf["servicios"])):
        cambios.append(f"Service nuevo en el front: {s} ({nf['servicios'][s]['tipo']}).")
    for s in sorted(set(vf["servicios"]) & set(nf["servicios"])):
        mas = sorted(set(nf["servicios"][s]["rutas"]) - set(vf["servicios"][s]["rutas"]))
        if mas:
            cambios.append(f"{s} ahora llama a {', '.join(mas)}.")
    return cambios


def escribir_indice(m, estado):
    L = ["# Arquitectura de COFFE_APP (modelo C4)", "",
         "Diagramas generados y mantenidos por la skill `arquitecto-c4` (`.claude/skills/arquitecto-c4/`). "
         "No se editan a mano: se regeneran desde el código.", "",
         f"- Último commit analizado: `{estado['ultimo_commit']}` ({estado['fecha_commit'][:10]})",
         f"- Última corrida: {estado['corrida']}", "",
         "| Nivel | Diagrama |", "|---|---|",
         f"| 1 · Contexto | [{DIAGRAMAS['contexto']}]({DIAGRAMAS['contexto']}) |",
         f"| 2 · Contenedores | [{DIAGRAMAS['contenedores']}]({DIAGRAMAS['contenedores']}) |",
         f"| 3 · Componentes de la API | [{DIAGRAMAS['backend']}]({DIAGRAMAS['backend']}) |",
         f"| 3 · Componentes de la app web | [{DIAGRAMAS['frontend']}]({DIAGRAMAS['frontend']}) |", "",
         f"Resumen: {len(m['backend']['paquetes'])} componentes en la API, {len(m['frontend']['pantallas'])} pantallas y "
         f"{len(m['frontend']['servicios'])} services en el front, {m['backend']['entidades']} entidades JPA.", "",
         "Historial de cambios: [CHANGELOG.md](CHANGELOG.md). Modelo en crudo: `modelo.json`. Estado: `estado.json`.", ""]
    (DOCS / "README.md").write_text("\n".join(L), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", default="HEAD")
    ap.add_argument("--forzar", action="store_true")
    a = ap.parse_args()
    DOCS.mkdir(parents=True, exist_ok=True)
    commit = git("rev-parse", a.commit).strip()
    estado = json.loads(ESTADO.read_text(encoding="utf-8")) if ESTADO.exists() else None
    viejo = json.loads(MODELO.read_text(encoding="utf-8")) if MODELO.exists() else None
    ahora = datetime.now().isoformat(timespec="seconds")

    if estado and a.forzar:
        cambiados, relevantes, rango = [], [], f"{commit[:7]} (regeneración forzada)"
    elif estado:
        base = estado["ultimo_commit"]
        if git("rev-parse", base).strip() == commit:
            print(f"Sin cambios: {commit[:7]} ya es el último commit analizado.")
            return
        cambiados = [f for f in git("diff", "--name-only", f"{base}..{commit}").splitlines()]
        relevantes = [f for f in cambiados if f.startswith(RELEVANTE)]
        rango = f"{base[:7]}..{commit[:7]}"
    else:
        cambiados, relevantes, rango = [], [], commit[:7]

    nuevo = analizar(commit)
    if viejo and estado and not a.forzar:
        kv, kn = claves_diagrama(viejo), claves_diagrama(nuevo)
        a_regenerar = [k for k in DIAGRAMAS if json.dumps(kv[k], sort_keys=True) != json.dumps(kn[k], sort_keys=True)]
        cambios = diferencias(viejo, nuevo)
    elif viejo and a.forzar:
        a_regenerar = list(DIAGRAMAS)
        cambios = diferencias(viejo, nuevo) or ["Regeneración forzada: cambió el analizador (no el código); "
                                                "se redibujaron todos los diagramas."]
    else:
        a_regenerar, cambios = list(DIAGRAMAS), ["Primera versión del modelo C4 (contexto, contenedores y componentes)."]

    for k in a_regenerar:
        (DOCS / DIAGRAMAS[k]).write_text(GENERADORES[k](nuevo), encoding="utf-8")
    MODELO.write_text(json.dumps(nuevo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    nuevo_estado = dict(ultimo_commit=commit, fecha_commit=nuevo["fecha_commit"], corrida=ahora,
                        diagramas={k: DIAGRAMAS[k] for k in DIAGRAMAS})
    ESTADO.write_text(json.dumps(nuevo_estado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    escribir_indice(nuevo, nuevo_estado)

    entrada = [f"## {ahora[:10]} — `{rango}`", "",
               f"- Commit analizado: `{commit[:7]}` ({nuevo['fecha_commit'][:10]})"]
    if cambiados:
        entrada.append(f"- Archivos cambiados desde la corrida anterior: {len(cambiados)} "
                       f"({len(relevantes)} de código o despliegue)")
    entrada.append(f"- Diagramas actualizados: {', '.join(DIAGRAMAS[k] for k in a_regenerar) or 'ninguno (cambios sin impacto en la arquitectura)'}")
    entrada += [""] + [f"- {c}" for c in cambios] + [""]
    previo = CHANGELOG.read_text(encoding="utf-8") if CHANGELOG.exists() else "# Changelog de arquitectura\n\nLo escribe la skill `arquitecto-c4` en cada corrida (lo más nuevo arriba).\n\n"
    cab, _, resto = previo.partition("\n\n## ")
    if resto:
        previo = cab + "\n\n" + "\n".join(entrada) + "\n## " + resto
    else:
        previo = previo.rstrip("\n") + "\n\n" + "\n".join(entrada)
    CHANGELOG.write_text(previo, encoding="utf-8")
    print(f"C4 {rango}: {len(cambios)} cambios, diagramas actualizados: {', '.join(a_regenerar) or 'ninguno'}")


if __name__ == "__main__":
    main()
