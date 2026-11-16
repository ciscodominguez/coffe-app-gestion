# Configuración del equipo

> Lo leen las skills `revisor-costos`, `product-owner` y `analista-brooks` (en `.claude/skills/`) y los
> scripts de `gestion/`. Las tablas también se leen por máquina: se pueden cambiar valores y agregar
> filas, pero no renombrar columnas. Lo marcado con ⚠️ hay que confirmarlo.

## Proyecto
- Nombre: COFFE_APP — sistema de gestión para cafés (pedidos, cocina, caja, stock y cobros con QR), multi-tenant, Spring Boot + Angular + MySQL
- Grupo del TP: Francisco Domínguez, Octavio Penacchietti y Agustín Avalos
- Tablero: Plane — https://app.plane.so/gestion-de-desarrollo-de-soft/ (proyecto COFFE_APP)
- Slug de Plane: gestion-de-desarrollo-de-soft
- Proyecto en Plane: COFFE_APP
- Repositorio: https://github.com/ciscodominguez/coffe-app
- Duración del sprint: 1 semana (ciclos de Plane de lunes a domingo)
- Fecha de inicio: 2026-10-26
- Entregas parciales: 2026-11-16, 2026-11-30 ⚠️ tomadas del equipo.md de ejemplo de la cátedra
- Entrega final: 2026-12-14 ⚠️ ídem

### Cómo se armó el tablero
El código lo escribieron **5 personas** para el TP de Programación IV (Fran, Gio, Facu, Nico y Octa),
entre el 29/10 y el 12/11, antes de que existiera el tablero. Las semanas 44, 45 y 46 se
**reconstruyeron desde el historial de git**: un ticket por PR con su autor real, sus fechas reales
(commit = listo para revisión, merge = terminado) y story points según el tamaño del cambio. Desde la
semana 47 el tablero se usa en vivo. Gio, Facu y Nico figuran como **colaboradores**: no son parte del
grupo de este TP, pero su trabajo está en el tablero tal como pasó. Agustín no participó del código:
se suma el 16/11 como **Product Owner / gestión**.

## Integrantes
| Nombre | Rol | Usuario en tablero | Usuario git | Dedicación | Ingreso al proyecto | Clave | Grupo TP |
|---|---|---|---|---|---|---|---|
| Francisco Domínguez | Dev full stack, dueño del repo | ⚠️ mail de Plane | Fran, ciscodominguez | 25 % | 2026-10-26 | fran | integrante |
| Octavio Penacchietti | Dev full stack | openacchietti@gmail.com | Octa, openacchietti-star | 25 % | 2026-10-26 | octa | integrante |
| Agustín Avalos | Product Owner / gestión | ⚠️ mail de Plane | — | 25 % | 2026-11-16 | agus | integrante |
| Giovani Napoli | Dev full stack (Prog IV) | giorgionapoli458@gmail.com | Gio, GioCDJ | 25 % | 2026-10-26 | gio | colaborador |
| Facundo Gregorio | Dev full stack (Prog IV) | gregoriofacundo4@gmail.com | Facu, Facundo Gregorio | 25 % | 2026-10-26 | facu | colaborador |
| Nicolás Spina | Dev full stack (Prog IV) | spinanicolas11@gmail.com | Nicolas, Nicolas Spina, nicolas spina | 25 % | 2026-10-26 | nico | colaborador |

- **Usuario en tablero**: el mail con el que cada uno entró a Plane. El script de carga lo usa para asignar
  los tickets; si alguien no está en el workspace, sus tickets quedan con la etiqueta `autor:<clave>`.
- **Dedicación**: ⚠️ 25 % (≈ 10 h por semana) es una estimación para estudiantes; ajústenla.

## Costos
- Costo mensual por integrante: 3000 USD
- Horas laborales por mes: 160
- Equivalencia de story point (opcional): 1 SP = 4 h
- Horas registradas: no se registran horas en Plane; se usa la equivalencia de SP como supuesto.

## Infraestructura
| Servicio | Plan | Costo mensual USD | Alternativa gratuita |
|---|---|---|---|
| GitHub | Free | 0 | |
| Plane | Free | 0 | |
| VPS 2 GB de RAM (producción, todavía sin alquilar) | Estimado del README: USD 5 a 15 | 10 | Oracle Cloud Always Free: Ampere A1 hasta 2 OCPU / 12 GB (desde jun-2026), con imágenes arm64 |
| Backblaze B2 (backups) | Free (10 GB) | 0 | |
| ntfy (avisos al celular) | Free | 0 | |
| Dominio | ⚠️ a definir | 0 | |

## Objetivos / historias comprometidas
Puntos = suma de story points de los tickets en Plane. Lo que dice "Deseable" está fuera del alcance comprometido.

| Id | Historia | Puntos | Entrega |
|---|---|---|---|
| Épica: Base del proyecto | 2 tickets reconstruidos de git (Plane, módulo «Base del proyecto») | 7 | 2026-11-16 |
| Épica: Caja y cobros | 8 tickets reconstruidos de git (Plane, módulo «Caja y cobros») | 33 | 2026-11-16 |
| Épica: Carta y salón | 6 tickets reconstruidos de git (Plane, módulo «Carta y salón») | 34 | 2026-11-16 |
| Épica: Cuentas y acceso | 5 tickets reconstruidos de git (Plane, módulo «Cuentas y acceso») | 33 | 2026-11-16 |
| Épica: Gestión del negocio | 6 tickets reconstruidos de git (Plane, módulo «Gestión del negocio») | 24 | 2026-11-16 |
| Épica: Pedidos y cocina | 4 tickets reconstruidos de git (Plane, módulo «Pedidos y cocina») | 26 | 2026-11-16 |
| Épica: Plataforma SaaS | 6 tickets reconstruidos de git (Plane, módulo «Plataforma SaaS») | 21 | 2026-11-16 |
| Épica: Salida a producción | 2 tickets reconstruidos de git (Plane, módulo «Salida a producción») | 10 | 2026-11-16 |
| Épica: Stock | 2 tickets reconstruidos de git (Plane, módulo «Stock») | 8 | 2026-11-16 |
| G-1 | El grupo tiene su tablero en Plane con ciclos, módulos y estimaciones | 2 | 2026-11-16 |
| G-2 | El tablero se lee por API: token personal probado con curl | 1 | 2026-11-16 |
| G-3 | Las semanas ya trabajadas quedan cargadas en Plane desde el historial de git | 3 | 2026-11-16 |
| G-4 | equipo.md completo: integrantes, dedicación, objetivos, fechas y costos de infra | 1 | 2026-11-30 |
| G-5 | El PO tiene costos, Brooks y semáforo de cada semana (3 skills corriendo) | 3 | 2026-11-30 |
| G-6 | La arquitectura C4 se mantiene sola con la skill arquitecto-c4 | 3 | 2026-11-30 |
| G-7 | Cada commit lleva el ID del issue de Plane (hook commit-msg) | 1 | 2026-11-30 |
| P-1 | Un café piloto entra a la app desde internet con HTTPS | 5 | 2026-11-30 |
| P-2 | Las copias nocturnas se restauran bien (prueba real de restauración) | 3 | 2026-11-30 |
| P-3 | Nos avisa al celular si la app se cae (monitor sobre /actuator/health) | 1 | 2026-11-30 |
| P-4 | Términos y privacidad con los datos reales del responsable | 2 | 2026-11-30 |
| P-5 | 1 o 2 cafés de Mar del Plata usan la app gratis un mes como piloto | 3 | 2026-12-14 |
| P-6 | Los pedidos de PedidosYa/Rappi llegan solos a cocina (Fase B/C) | 8 | Deseable |
| P-7 | El café que lo necesita factura electrónicamente con ARCA (opcional) | 13 | Deseable |
