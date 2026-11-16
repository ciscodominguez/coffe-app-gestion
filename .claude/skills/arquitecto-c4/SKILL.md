---
name: arquitecto-c4
description: Genera y mantiene actualizado el modelo C4 de COFFE_APP (contexto, contenedores y componentes del back Spring Boot y del front Angular) en docs/arquitectura/, en Mermaid. En cada corrida mira el diff desde el último commit analizado y actualiza solo lo que cambió, con changelog. Usar cuando se pida diagrama C4, documentar o actualizar la arquitectura, o después de mergear PRs que agregan o quitan módulos, pantallas, servicios o integraciones.
---

# Arquitecto C4

Actuás como **arquitecto de software del grupo**. Tu trabajo es que la documentación de arquitectura
diga siempre lo mismo que el código: el modelo C4 se genera desde el repo y se actualiza con cada cambio,
nunca se dibuja a mano.

## Qué se analiza

1. **Back (Spring Boot)** — `backend/src/main/java/com/cofeapp/backend/`. Cada paquete es un componente:
   sus `@RestController` (con la ruta de `@RequestMapping` o, si no hay, el primer tramo de las rutas de
   los métodos), sus services, sus repositories y las dependencias hacia otros paquetes (campos
   `private final` inyectados). `domain/` son las entidades JPA (se cuentan, no se dibujan). Lo de
   `common/` y `config/` se agrupa en componentes transversales (seguridad y multi-tenant, mail, tiempo
   real STOMP, Excel, cifrado).
2. **Front (Angular)** — `frontend/src/app/`. Cada carpeta de `features/` es una pantalla; los
   `*.service.ts` son services: los que llaman a la API (por `ApiService` o `HttpClient`) con sus rutas,
   el de tiempo real (STOMP) y la cola offline. Qué service usa cada pantalla sale de `inject()` o del
   constructor.
3. **Despliegue** — `deploy/`: proxy Caddy, Docker Compose y scripts de backup, si existen.
4. **Sistemas externos** — Mercado Pago (cliente HTTP en `mercadopago/client`), servidor de mail
   (`JavaMailSender`), almacenamiento de backups.

## Salida (en `docs/arquitectura/`)

| Archivo | Contenido |
|---|---|
| `c4-1-contexto.md` | Nivel 1: personas (dueño, mozo, cocina, cajero, superadmin), COFFE_APP y sistemas externos — Mermaid `C4Context` |
| `c4-2-contenedores.md` | Nivel 2: app web Angular, API Spring Boot, MySQL, proxy y backups — Mermaid `C4Container` |
| `c4-3-componentes-backend.md` | Nivel 3 de la API: un nodo por paquete con rutas y conteo C/S/R, y las dependencias entre paquetes; tabla de detalle |
| `c4-3-componentes-frontend.md` | Nivel 3 de la app web: pantallas → services → API; tabla de services con sus rutas |
| `README.md` | Índice, último commit analizado y resumen |
| `modelo.json` | El modelo extraído del código (lo usa la próxima corrida para comparar) |
| `estado.json` | `ultimo_commit` analizado y fecha de la corrida |
| `CHANGELOG.md` | Una entrada por corrida, lo más nuevo arriba |

## Procedimiento

1. Leé `docs/arquitectura/estado.json`. Si no existe, es la **primera corrida**: se genera todo.
2. Corré el analizador desde la raíz del repo:
   ```bash
   python gestion/c4/arquitecto_c4.py              # analiza HEAD
   python gestion/c4/arquitecto_c4.py --commit <sha>   # otro commit (lee de git, sin checkout)
   ```
   El script:
   - calcula `git diff --name-only <ultimo_commit>..<commit>` y cuenta los archivos de código o despliegue;
   - vuelve a extraer el modelo en el commit pedido y lo compara con `modelo.json`;
   - **regenera solo los diagramas cuyo contenido cambió** (si el diff no tocó la arquitectura, no
     regenera ninguno y lo deja dicho en el changelog);
   - agrega al principio de `CHANGELOG.md` la entrada: rango de commits, archivos cambiados, diagramas
     actualizados y la lista de cambios (componentes, rutas, dependencias, pantallas, services, sistemas
     externos y entidades nuevas o quitadas);
   - guarda el nuevo `modelo.json` y el `estado.json` con el último commit.
3. Revisá el resultado:
   - Que los diagramas rendericen (GitHub muestra los bloques ```mermaid```; también https://mermaid.live).
   - Que el changelog explique el cambio en palabras: si el script listó "Componente nuevo: Caja", agregá
     debajo una línea de contexto de negocio si hace falta (por qué entró, qué PR o issue de Plane).
   - Si el código cambió de una forma que el script no detecta (por ejemplo, una integración nueva con un
     sistema externo que no es Mercado Pago ni mail), agregala al analizador en `gestion/c4/arquitecto_c4.py`
     en vez de editar el diagrama a mano, y volvé a correr con `--forzar`.
4. Commiteá `docs/arquitectura/` en un commit propio con el ID del issue de Plane, por ejemplo
   `docs(arquitectura): actualizar C4 a 13d042b [COFFE-12]`.

## Cuándo correrla

- Después de cada merge a `main` que agregue o quite paquetes, controllers, pantallas, services o algo
  de `deploy/`.
- Cada lunes, junto con las skills de gestión (`revisor-costos`, `analista-brooks`, `product-owner`).

## Reglas

- Los diagramas se generan; no se editan a mano. Si algo está mal, se corrige el analizador.
- Una entrada de changelog por corrida, aunque no haya cambios ("sin impacto en la arquitectura").
- Nunca borres entradas viejas del changelog: es la prueba de que el modelo se mantiene vivo.
- Nombres de componentes en castellano y orientados al negocio (Pedidos, Caja, Stock…), con el paquete
  técnico entre paréntesis en la tabla de detalle.
