#!/usr/bin/env python3
"""Reconstruye el tablero de Plane a partir del historial de git.

Cada PR mergeado en main pasa a ser un ticket con:
  - responsable  = autor del commit de la rama
  - revisor      = quien mergeó el PR
  - inicio       = fecha del commit (cuando quedó listo para revisión)
  - fin          = fecha del merge (cuando quedó terminado)
  - story points = según el tamaño real del cambio (líneas agregadas, sin lockfiles)
  - ciclo        = semana ISO del merge (semana-2026-44, 45, 46)

Además agrega los tickets de gestión del TP (los lleva Agustín como PO) y el
backlog de la próxima entrega, que salen de la hoja de ruta del README (sección 16).

Uso (desde la raíz del repo):
    python3 gestion/plane/generar_tickets.py > gestion/plane/tickets.json
"""
import json
import re
import subprocess
import sys
from datetime import datetime, date

# Fecha desde la que se considera planificado el alcance (lunes de la semana del primer commit).
INICIO_PROYECTO = "2026-10-26"

# Entregas de la cursada (equipo.md). "deseable" = fuera del alcance comprometido.
ENTREGA_1, ENTREGA_2, ENTREGA_FINAL = "2026-11-16", "2026-11-30", "2026-12-14"
ENTREGA_DE = {"G-1": ENTREGA_1, "G-2": ENTREGA_1, "G-3": ENTREGA_1, "P-5": ENTREGA_FINAL,
              "P-6": "deseable", "P-7": "deseable"}
TIPO_DE = {"P-6": "historia", "P-7": "historia"}

# Autores de git -> clave de persona en equipo.md
AUTORES = {
    "fran": "fran", "ciscodominguez": "fran",
    "gio": "gio", "giocdj": "gio",
    "facu": "facu", "facundo gregorio": "facu",
    "nicolas": "nico", "nicolas spina": "nico",
    "octa": "octa", "openacchietti-star": "octa",
}

# Catálogo: commit de la rama -> cómo se lee en el tablero.
# titulo: qué valor entrega (no "hice tal clase"); historia: épica/módulo funcional.
CATALOGO = {
    "54cea77": ("El equipo tiene el repo y el proyecto Spring Boot listos para trabajar", "Infra", "Base del proyecto", []),
    "78984ec": ("Un café se registra solo y entra con su usuario; carga locales y empleados", "Backend", "Cuentas y acceso", ["54cea77"]),
    "d205c3f": ("Cada café ve solo sus datos: JWT, aislamiento multi-tenant y errores claros", "Backend", "Cuentas y acceso", ["54cea77"]),
    "07a22fc": ("Los pedidos de las mesas llegan a cocina al instante (WebSocket)", "Backend", "Pedidos y cocina", ["78984ec", "d205c3f"]),
    "8c45f30": ("El dueño arma la carta y las mesas desde la pantalla", "Frontend", "Carta y salón", ["697f718", "dfe4dbe"]),
    "697f718": ("La carta tiene categorías y productos con foto e ingredientes", "Backend", "Carta y salón", ["d205c3f"]),
    "7076e55": ("El mozo toma pedidos aunque se corte internet y cocina los ve en su pantalla", "Frontend", "Pedidos y cocina", ["07a22fc", "dfe4dbe"]),
    "dfe4dbe": ("Los usuarios entran a la app web: base Angular, menú, login y registro", "Frontend", "Cuentas y acceso", ["78984ec"]),
    "fe8ad37": ("El café sabe cuánto stock le queda: insumos, recetas y descuento por venta", "Backend", "Stock", ["697f718"]),
    "c6fdf1c": ("El dueño administra su negocio, usuarios y locales desde la web", "Frontend", "Gestión del negocio", ["dfe4dbe", "78984ec"]),
    "4465d1c": ("La caja abre, cobra, registra movimientos y cierra con conteo", "Backend", "Caja y cobros", ["07a22fc"]),
    "8fcfc58": ("El cliente paga con QR de Mercado Pago", "Backend", "Caja y cobros", ["4465d1c"]),
    "ff3e1fe": ("El dueño ve el resumen del día apenas entra", "Backend", "Gestión del negocio", ["07a22fc"]),
    "0a8a853": ("Cada rol ve un inicio con sus números clave (KPIs)", "Frontend", "Gestión del negocio", ["ff3e1fe", "dfe4dbe"]),
    "f2592d1": ("El usuario cambia o recupera su contraseña sin pedir ayuda", "Frontend", "Cuentas y acceso", ["d431667", "dfe4dbe"]),
    "7916232": ("El dueño consulta reportes de ventas en pantalla", "Frontend", "Gestión del negocio", ["ff3e1fe"]),
    "482f6a4": ("El cajero cobra un pedido desde la pantalla de caja", "Frontend", "Caja y cobros", ["4465d1c", "dfe4dbe"]),
    "8980c0f": ("El café aplica descuentos a un ítem o a todo el pedido", "Backend", "Caja y cobros", ["07a22fc"]),
    "fa5f9a9": ("Se imprimen comanda, ticket y cierre de caja desde el navegador", "Frontend", "Caja y cobros", ["482f6a4"]),
    "d431667": ("Las cuentas están protegidas: recuperar contraseña, bloqueo por intentos y cierre de sesiones", "Backend", "Cuentas y acceso", ["d205c3f"]),
    "e1fb97a": ("Un producto tiene variantes y agregados (tamaño, leche, extra shot)", "Backend", "Carta y salón", ["697f718"]),
    "98a3e49": ("El dueño conecta su cuenta de Mercado Pago para cobrar con QR", "Frontend", "Caja y cobros", ["8fcfc58"]),
    "0b3d785": ("El encargado controla insumos y stock desde la web", "Frontend", "Stock", ["fe8ad37", "dfe4dbe"]),
    "ef1df9b": ("La plataforma ve todos los cafés clientes y los activa o suspende (panel superadmin)", "Frontend", "Plataforma SaaS", ["2066e48"]),
    "041aa8a": ("El mozo elige variantes y agregados al cargar el pedido", "Frontend", "Carta y salón", ["e1fb97a", "7076e55"]),
    "0086018": ("Términos y política de privacidad visibles para cualquiera", "Frontend", "Plataforma SaaS", ["a8a3c53"]),
    "22497bd": ("Cada café paga su suscripción mensual con débito automático", "Backend", "Plataforma SaaS", ["2066e48"]),
    "9b7d18b": ("El contador recibe un Excel con ventas y cierres de caja", "Backend", "Gestión del negocio", ["4465d1c"]),
    "e2cbe86": ("El cajero aplica descuentos desde una lista armada", "Frontend", "Caja y cobros", ["8980c0f", "482f6a4"]),
    "d3e2455": ("Los pedidos de apps de delivery se cargan en modo manual", "Backend", "Pedidos y cocina", ["07a22fc"]),
    "48c8b4f": ("El dueño elige qué apps de delivery usa cada local", "Frontend", "Pedidos y cocina", ["d3e2455"]),
    "845c6bb": ("La mesa divide la cuenta en partes iguales o por productos", "Backend", "Caja y cobros", ["4465d1c"]),
    "ade8b2d": ("La app está lista para instalarse en un servidor (Docker, HTTPS, backups)", "Infra", "Salida a producción", []),
    "c860218": ("El café ve el estado de su suscripción y la paga desde la app", "Frontend", "Plataforma SaaS", ["22497bd"]),
    "81a8013": ("Probamos todo antes de salir: barrido de endpoints, carga y concurrencia", "Calidad", "Salida a producción", []),
    "17c536e": ("Un usuario nuevo aprende la app con un tour guiado", "Frontend", "Gestión del negocio", ["dfe4dbe"]),
    "a8a3c53": ("El sistema cumple con términos, privacidad y botón de arrepentimiento/baja", "Backend", "Plataforma SaaS", ["d205c3f"]),
    "f6c2198": ("El dueño dibuja el plano del salón y pide soporte con un botón", "Frontend", "Carta y salón", ["45584a5"]),
    "45584a5": ("El salón se organiza por zonas y el café puede pedir soporte", "Backend", "Carta y salón", ["07a22fc"]),
    "2066e48": ("La plataforma administra cafés clientes y planes (superadmin)", "Backend", "Plataforma SaaS", ["d205c3f"]),
    "d93117d": ("Cualquiera del equipo entiende el proyecto leyendo el README", "Docs", "Base del proyecto", []),
}

# Gestión del TP (semana actual) y backlog de la próxima entrega.
# estado: Done / In Progress / Todo / Backlog. ciclo None = backlog sin ciclo.
EXTRAS = [
    # --- Gestión del TP de Gestión de Desarrollo de Software (lleva Agustín como PO) ---
    dict(clave="G-1", titulo="El grupo tiene su tablero en Plane con ciclos, módulos y estimaciones",
         modulo="Gestión", historia="Gestión del TP", sp=2, responsable="agus", estado="Done",
         inicio="2026-11-16", fin="2026-11-16", ciclo="semana-2026-47", deps=[]),
    dict(clave="G-2", titulo="El tablero se lee por API: token personal probado con curl",
         modulo="Gestión", historia="Gestión del TP", sp=1, responsable="agus", estado="Done",
         inicio="2026-11-16", fin="2026-11-16", ciclo="semana-2026-47", deps=["G-1"]),
    dict(clave="G-3", titulo="Las semanas ya trabajadas quedan cargadas en Plane desde el historial de git",
         modulo="Gestión", historia="Gestión del TP", sp=3, responsable="fran", estado="Done",
         inicio="2026-11-16", fin="2026-11-16", ciclo="semana-2026-47", deps=["G-2"]),
    dict(clave="G-4", titulo="equipo.md completo: integrantes, dedicación, objetivos, fechas y costos de infra",
         modulo="Gestión", historia="Gestión del TP", sp=1, responsable="agus", estado="In Progress",
         inicio="2026-11-16", fin="2026-11-18", ciclo="semana-2026-47", deps=[]),
    dict(clave="G-5", titulo="El PO tiene costos, Brooks y semáforo de cada semana (3 skills corriendo)",
         modulo="Gestión", historia="Gestión del TP", sp=3, responsable="agus", estado="Todo",
         inicio="2026-11-17", fin="2026-11-18", ciclo="semana-2026-47", deps=["G-3", "G-4"]),
    dict(clave="G-6", titulo="La arquitectura C4 se mantiene sola con la skill arquitecto-c4",
         modulo="Gestión", historia="Gestión del TP", sp=3, responsable="octa", estado="In Progress",
         inicio="2026-11-16", fin="2026-11-20", ciclo="semana-2026-47", deps=[]),
    dict(clave="G-7", titulo="Cada commit lleva el ID del issue de Plane (hook commit-msg)",
         modulo="Gestión", historia="Gestión del TP", sp=1, responsable="fran", estado="Todo",
         inicio="2026-11-18", fin="2026-11-19", ciclo="semana-2026-47", deps=["G-3"]),
    # --- Próxima entrega: salir a producción con un café piloto ---
    dict(clave="P-1", titulo="Un café piloto entra a la app desde internet con HTTPS",
         modulo="Infra", historia="Salida a producción", sp=5, responsable="fran", estado="Todo",
         inicio="2026-11-18", fin="2026-11-22", ciclo="semana-2026-47", deps=["ade8b2d"]),
    dict(clave="P-2", titulo="Las copias nocturnas se restauran bien (prueba real de restauración)",
         modulo="Infra", historia="Salida a producción", sp=3, responsable="octa", estado="Todo",
         inicio="2026-11-23", fin="2026-11-27", ciclo="semana-2026-48", deps=["P-1"]),
    dict(clave="P-3", titulo="Nos avisa al celular si la app se cae (monitor sobre /actuator/health)",
         modulo="Infra", historia="Salida a producción", sp=1, responsable="octa", estado="Todo",
         inicio="2026-11-23", fin="2026-11-24", ciclo="semana-2026-48", deps=["P-1"]),
    dict(clave="P-4", titulo="Términos y privacidad con los datos reales del responsable",
         modulo="Docs", historia="Plataforma SaaS", sp=2, responsable="agus", estado="Todo",
         inicio="2026-11-23", fin="2026-11-26", ciclo="semana-2026-48", deps=[]),
    dict(clave="P-5", titulo="1 o 2 cafés de Mar del Plata usan la app gratis un mes como piloto",
         modulo="Gestión", historia="Salida a producción", sp=3, responsable="fran", estado="Backlog",
         inicio=None, fin=None, ciclo=None, deps=["P-1", "P-2", "P-3"]),
    dict(clave="P-6", titulo="Los pedidos de PedidosYa/Rappi llegan solos a cocina (Fase B/C)",
         modulo="Backend", historia="Pedidos y cocina", sp=8, responsable=None, estado="Backlog",
         inicio=None, fin=None, ciclo=None, deps=["P-1", "d3e2455"]),
    dict(clave="P-7", titulo="El café que lo necesita factura electrónicamente con ARCA (opcional)",
         modulo="Backend", historia="Caja y cobros", sp=13, responsable=None, estado="Backlog",
         inicio=None, fin=None, ciclo=None, deps=["P-1"]),
]

# Plan de la próxima etapa: los 40 commits de la auditoría de la tesis (docs/auditoria), en 5 olas.
# Se cargan como trabajo PLANIFICADO (Todo), no hecho. Puntos de la auditoría: 1 = medio día = 1 SP.
# (clave, ola, título orientado a valor, tipo, área, historia, responsable, SP, depende de, commit planeado)
AUDITORIA = [
    ("C01", 1, "Ningún PR rompe main: CI con tests del back (MySQL 8) y del front", "tarea", "Calidad", "Calidad y CI", "fran", 2, [], "chore(ci): GitHub Actions con mvn verify (MySQL 8) y build + tests del front"),
    ("C02", 1, "La app se llama COFFE_APP en todos lados y sin comentarios viejos", "tarea", "Frontend", "Errores de la auditoría", "fran", 1, ["C01"], "chore: título COFFE_APP y comentarios viejos de descuentos"),
    ("C03", 1, "Nadie puede firmar tokens: JWT_SECRET obligatorio", "bug", "Backend", "Errores de la auditoría", "fran", 1, ["C01"], "fix(backend): JWT_SECRET obligatorio, sin valor por defecto"),
    ("C04", 1, "El Excel de cierres de caja sale con las columnas alineadas", "bug", "Backend", "Errores de la auditoría", "gio", 2, ["C01"], "fix(backend): columnas del Excel \"Cierres de caja\" + test de encabezados"),
    ("C05", 1, "No se puede dar de baja una mesa con un pedido abierto", "bug", "Backend", "Errores de la auditoría", "facu", 2, ["C01"], "fix(backend): no dar de baja una mesa con pedido abierto; sacar status del PATCH"),
    ("C06", 1, "El botón \"Dar de baja\" se deshabilita en mesas ocupadas", "bug", "Frontend", "Errores de la auditoría", "facu", 1, ["C05"], "feat(frontend): deshabilitar \"Dar de baja\" en mesas ocupadas"),
    ("C07", 1, "No se cargan pedidos en mesas inactivas o de otro local", "bug", "Backend", "Errores de la auditoría", "facu", 1, ["C01"], "fix(backend): rechazar pedidos en mesas inactivas o de otro local"),
    ("C08", 1, "Cambiar el rol cierra la sesión y el café nunca queda sin dueño", "bug", "Backend", "Errores de la auditoría", "fran", 2, ["C01"], "fix(backend): cerrar sesión al cambiar rol o local; no cambiarse el rol propio ni dejar el café sin OWNER"),
    ("C09", 1, "Un usuario solo puede quedar en un local válido de su café", "bug", "Backend", "Errores de la auditoría", "fran", 1, ["C08"], "fix(backend): validar el local al crear o editar usuarios"),
    ("C10", 1, "Los productos de categorías dadas de baja no se ven ni se venden", "bug", "Backend", "Errores de la auditoría", "nico", 1, ["C01"], "fix: no mostrar ni vender productos de categorías dadas de baja (back + front)"),
    ("C13", 1, "Cantidades, precios y nombres absurdos se rechazan con un mensaje claro", "bug", "Backend", "Errores de la auditoría", "nico", 2, ["C01"], "fix(backend): topes de cantidad y precio, nombres en blanco, orden y capacidad"),
    ("C14", 1, "El sistema avisa antes de desactivar un insumo que usan recetas", "historia", "Backend", "Mejoras de la auditoría", "octa", 1, ["C01"], "feat(stock): avisar al desactivar un insumo que está en recetas"),
    ("C16", 1, "Dos cierres de caja simultáneos no se pisan", "bug", "Backend", "Errores de la auditoría", "gio", 1, ["C01"], "fix(backend): lock pesimista al cerrar la caja"),
    ("C19", 1, "El encargado encuentra un insumo escribiendo su nombre", "historia", "Frontend", "Mejoras de la auditoría", "octa", 1, ["C01"], "feat(frontend): buscador de insumos"),
    ("C28", 1, "El carrito, la cola offline y los permisos del front tienen tests", "tarea", "Calidad", "Calidad y CI", "octa", 2, ["C01"], "test(frontend): carrito de Meseras, cola offline, roleGuard e interceptor 401"),
    ("C11", 2, "Cada empleado queda identificado por su DNI", "historia", "Backend", "Mejoras de la auditoría", "fran", 2, ["C09"], "feat: DNI del personal (V20), con validación y alta en Equipo"),
    ("C12", 2, "No hay categorías, productos, descuentos ni SKU repetidos", "bug", "Backend", "Mejoras de la auditoría", "nico", 3, ["C13"], "fix(backend): nombres y SKU únicos en categorías, productos y descuentos (V21)"),
    ("C17", 2, "Los listados largos cargan por páginas y se pueden buscar", "historia", "Backend", "Mejoras de la auditoría", "nico", 3, ["C12"], "feat(backend): paginación en productos, categorías, insumos, usuarios y pedidos, con ?q="),
    ("C20", 2, "La API entrega las ventas por día y por hora", "historia", "Backend", "Mejoras de la auditoría", "gio", 2, ["C04"], "feat(backend): endpoint de ventas por día y por hora"),
    ("C24", 2, "El dueño encuentra todo en un menú más corto y una sola Configuración", "tarea", "Frontend", "Mejoras de la auditoría", "facu", 2, ["C06"], "refactor(frontend): menú simplificado y pantalla única de Configuración"),
    ("C25", 2, "Cobro y carga de pedidos partidos en componentes más simples", "tarea", "Frontend", "Mejoras de la auditoría", "facu", 3, ["C28"], "refactor(frontend): partir payment-dialog y waiter-order en subcomponentes"),
    ("C27", 2, "Cobros y descuentos separados del servicio de pedidos", "tarea", "Backend", "Mejoras de la auditoría", "octa", 2, ["C07", "C10"], "refactor(backend): separar OrderPaymentService y OrderDiscountService"),
    ("C15", 3, "El sistema advierte si se cierra la caja con pedidos sin cobrar", "historia", "Backend", "Mejoras de la auditoría", "facu", 1, ["C16"], "feat(cash): advertir al cerrar la caja con pedidos sin cobrar"),
    ("C18", 3, "Todos los listados tienen el mismo paginador", "historia", "Frontend", "Mejoras de la auditoría", "nico", 2, ["C17", "C19"], "feat(frontend): componente app-paginator en los listados"),
    ("C21", 3, "El dueño ve gráficos de ventas por día, horas pico y métodos de pago", "historia", "Frontend", "Mejoras de la auditoría", "gio", 2, ["C20"], "feat(frontend): gráficos de ventas por día, horas pico y métodos de pago"),
    ("C22", 3, "El café arma promos 2x1, combos y happy hour que se aplican solas", "historia", "Backend", "Mejoras de la auditoría", "nico", 3, ["C12", "C27"], "feat(backend): promos automáticas 2x1, combos y happy hour con vigencia (V22)"),
    ("C23", 3, "El dueño carga promos y el carrito las aplica automáticamente", "historia", "Frontend", "Mejoras de la auditoría", "nico", 2, ["C22", "C25"], "feat(frontend): pantalla de promos y aplicación automática en el carrito"),
    ("C26", 3, "El encargado se entera al instante cuando un insumo queda bajo", "historia", "Frontend", "Mejoras de la auditoría", "octa", 2, ["C14", "C24"], "feat: alertas de stock con badge en el menú y aviso en vivo"),
    ("C29", 4, "Queda registrado quién hizo cada acción sensible (bitácora con AOP)", "historia", "Backend", "Bitácora de auditoría", "fran", 3, ["C27"], "feat(backend): bitácora de auditoría con @Audited y AOP (V23)"),
    ("C30", 4, "Anulaciones, descuentos, precios, caja, stock y roles quedan auditados", "historia", "Backend", "Bitácora de auditoría", "fran", 2, ["C29", "C22"], "feat(backend): auditar anulaciones, descuentos, precios, caja, stock y roles"),
    ("C31", 4, "El dueño consulta la actividad con filtros por usuario, acción y fecha", "historia", "Frontend", "Bitácora de auditoría", "fran", 2, ["C29", "C24"], "feat(frontend): pantalla Actividad con filtros"),
    ("C32", 4, "El cliente ve la carta y llama al mozo desde el QR de la mesa (API)", "historia", "Backend", "Carta QR y llamar al mozo", "facu", 3, ["C05", "C10"], "feat(backend): carta pública y llamado al mozo por token de mesa (V24)"),
    ("C33", 4, "Cada mesa tiene su QR impreso y el mozo recibe el llamado en vivo", "historia", "Frontend", "Carta QR y llamar al mozo", "facu", 3, ["C32", "C25"], "feat(frontend): carta /carta/:token, imprimir QR y aviso en Meseras"),
    ("C34", 4, "El café premia a sus clientes frecuentes con sellos por DNI (API)", "historia", "Backend", "Fidelización por DNI", "octa", 3, ["C27"], "feat(backend): clientes y programa de sellos, con el premio como descuento (V25)"),
    ("C35", 4, "El cajero suma sellos con el DNI al cobrar y ve la ficha del cliente", "historia", "Frontend", "Fidelización por DNI", "octa", 3, ["C34", "C25"], "feat(frontend): DNI en el cobro, ficha de cliente y configuración del programa"),
    ("C36", 4, "El sistema calcula cuánto comprar de cada insumo antes de que se termine", "historia", "Backend", "Pronóstico de reposición", "gio", 3, ["C14"], "feat(backend): pronóstico de reposición por día de la semana"),
    ("C37", 4, "El encargado descarga la lista de compras en Excel", "historia", "Frontend", "Pronóstico de reposición", "gio", 2, ["C36", "C04"], "feat(frontend): lista de compras con exportación a Excel"),
    ("C38", 5, "El jurado entiende el proyecto con un README corto y un diagrama", "tarea", "Docs", "Defensa de la tesis", "gio", 2, ["C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37"], "docs: README corto, diagrama de arquitectura e historial aparte"),
    ("C39", 5, "La demo arranca con carta con fotos y dos semanas de ventas", "tarea", "Calidad", "Defensa de la tesis", "gio", 2, ["C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36", "C37"], "chore: datos de demo (carta con fotos y 2 semanas de ventas)"),
    ("C40", 5, "El recorrido completo de la defensa está probado de punta a punta", "tarea", "Calidad", "Defensa de la tesis", "octa", 2, ["C38", "C39"], "test: prueba integral de punta a punta y checklist de la defensa"),
]
# Ola -> ciclo y entrega. Ola 1 cierra para la entrega parcial del 30/11; el resto, para la final del 14/12.
CICLO_DE_OLA = {1: ("semana-2026-48", "2026-11-23", "2026-11-29", "2026-11-30"),
                2: ("semana-2026-49", "2026-11-30", "2026-12-06", "2026-12-14"),
                3: ("semana-2026-49", "2026-11-30", "2026-12-06", "2026-12-14"),
                4: ("semana-2026-50", "2026-12-07", "2026-12-13", "2026-12-14"),
                5: ("semana-2026-50", "2026-12-07", "2026-12-13", "2026-12-14")}
PLAN_CREADO = "2026-11-23"


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8", errors="replace", check=True).stdout


def lineas_sin_lockfiles(commit):
    total = 0
    for linea in git("show", "--numstat", "--format=", commit).splitlines():
        partes = linea.split("\t")
        if len(partes) != 3 or partes[0] == "-":
            continue
        if partes[2].endswith(("package-lock.json", ".lock")):
            continue
        total += int(partes[0])
    return total


def story_points(lineas):
    # Escala Fibonacci según el tamaño real del cambio.
    for tope, sp in ((300, 1), (600, 2), (1000, 3), (1800, 5), (3000, 8)):
        if lineas <= tope:
            return sp
    return 13


def semana(fecha_iso):
    d = datetime.fromisoformat(fecha_iso).date()
    a, s, _ = d.isocalendar()
    return f"semana-{a}-{s:02d}"


def main():
    tickets = []
    vistos = set()
    log = git("log", "main", "--first-parent", "--format=%H|%an|%aI|%s").splitlines()
    for fila in reversed(log):
        h, an, ad, s = fila.split("|", 3)
        m = re.match(r"Merge pull request #(\d+) from [^/]+/(.+)", s)
        if m:
            pr, rama = int(m.group(1)), m.group(2)
            commits = git("rev-list", "--reverse", f"{h}^1..{h}^2").split()
            fin, revisor = ad, AUTORES[an.lower()]
        else:
            pr, rama, commits, fin, revisor = None, "main", [h], ad, None
        for c in commits:
            corto = c[:7]
            if corto not in CATALOGO:
                continue  # merges internos / commits duplicados de la reescritura
            if corto in vistos:
                continue
            vistos.add(corto)
            autor, fecha_c, asunto = git("log", "-1", "--format=%an|%aI|%s", c).strip().split("|", 2)
            titulo, modulo, historia, deps = CATALOGO[corto]
            lineas = lineas_sin_lockfiles(c)
            tickets.append(dict(
                clave=f"PR-{pr}" if pr else f"C-{corto}",
                titulo=titulo,
                modulo=modulo,
                historia=historia,
                sp=story_points(lineas),
                responsable=AUTORES[autor.lower()],
                revisor=revisor,
                estado="Done",
                inicio=fecha_c[:10],
                listo_revision=fecha_c,
                fin=fin[:10],
                merge=fin,
                ciclo=semana(fin),
                commit=corto,
                asunto_commit=asunto,
                rama=rama,
                pr=pr,
                lineas=lineas,
                deps=deps,
                origen="git",
                creado=INICIO_PROYECTO,
                tipo="historia" if asunto.startswith("feat") else "tarea",
                entrega=ENTREGA_1,
            ))
    faltan = set(CATALOGO) - vistos
    if faltan:
        sys.exit(f"Commits del catálogo que no aparecen en main: {sorted(faltan)}")
    # Las dependencias se guardan por clave de ticket, no por commit.
    por_commit = {t["commit"]: t["clave"] for t in tickets}
    for t in tickets:
        t["deps"] = [por_commit.get(d, d) for d in t["deps"]]
    for e in EXTRAS:
        # Los G-* (gestión del TP) nacen con el tablero; los P-* ya estaban en la hoja de ruta del README.
        creado = "2026-11-16" if e["clave"].startswith("G-") else INICIO_PROYECTO
        t = dict(e, revisor=None, commit=None, rama=None, pr=None, lineas=None, origen="plan", creado=creado,
                 tipo=TIPO_DE.get(e["clave"], "tarea"), entrega=ENTREGA_DE.get(e["clave"], ENTREGA_2))
        t["deps"] = [por_commit.get(d, d) for d in t.pop("deps")]
        tickets.append(t)
    for c, ola, titulo, tipo, area, historia, resp, sp, deps, commit_plan in AUDITORIA:
        ciclo, ini, fin, entrega = CICLO_DE_OLA[ola]
        tickets.append(dict(
            clave=c, titulo=titulo, modulo=area, historia=historia, sp=sp, responsable=resp, estado="Todo",
            inicio=ini, fin=fin, ciclo=ciclo, deps=deps, revisor=None, commit=None, rama=None, pr=None, lineas=None,
            origen="plan", creado=PLAN_CREADO, tipo=tipo, entrega=entrega, ola=ola, commit_planeado=commit_plan))
    json.dump(dict(generado=date.today().isoformat(), tickets=tickets), sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
