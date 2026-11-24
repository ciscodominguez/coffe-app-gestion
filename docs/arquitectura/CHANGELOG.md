# Changelog de arquitectura

Lo escribe la skill `arquitecto-c4` en cada corrida (lo más nuevo arriba).

## 2026-11-23 — `03fd585..e007d8b`

- Commit analizado: `e007d8b` (2026-11-23)
- Archivos cambiados desde la corrida anterior: 13 (0 de código o despliegue)
- Diagramas actualizados: ninguno (cambios sin impacto en la arquitectura)


## 2026-11-16 — `13d042b..03fd585`

- Commit analizado: `03fd585` (2026-11-16)
- Archivos cambiados desde la corrida anterior: 50 (0 de código o despliegue)
- Diagramas actualizados: ninguno (cambios sin impacto en la arquitectura)


## 2026-11-16 — `13d042b (regeneración forzada)`

- Commit analizado: `13d042b` (2026-11-12)
- Diagramas actualizados: c4-1-contexto.md, c4-2-contenedores.md, c4-3-componentes-backend.md, c4-3-componentes-frontend.md

- Regeneración forzada: cambió el analizador (no el código); se redibujaron todos los diagramas.

## 2026-11-16 — `174032e..13d042b`

- Commit analizado: `13d042b` (2026-11-12)
- Archivos cambiados desde la corrida anterior: 104 (89 de código o despliegue)
- Diagramas actualizados: c4-1-contexto.md, c4-2-contenedores.md, c4-3-componentes-backend.md, c4-3-componentes-frontend.md

- Componente nuevo en la API: **Plano del salón** (`floor`, rutas /floor).
- Componente nuevo en la API: **Legales** (`legal`, rutas /legal).
- Componente nuevo en la API: **Superadmin** (`platform`, rutas /platform).
- Componente nuevo en la API: **Soporte** (`support`, rutas /support).
- Pedidos: repositories nuevos OrderPaymentItemRepository.
- Dependencia nueva: Autenticación → Legales.
- Dependencia nueva: Autenticación → Superadmin.
- Dependencia nueva: Suscripción → Superadmin.
- Dependencia nueva: Plano del salón → Locales.
- Dependencia nueva: Plano del salón → Mesas.
- Dependencia nueva: Legales → Suscripción.
- Dependencia nueva: Legales → Negocios.
- Dependencia nueva: Legales → Mail.
- Dependencia nueva: Legales → Superadmin.
- Dependencia nueva: Legales → Seguridad y multi-tenant.
- Dependencia nueva: Superadmin → Suscripción.
- Dependencia nueva: Superadmin → Negocios.
- Dependencia nueva: Superadmin → Legales.
- Dependencia nueva: Superadmin → Soporte.
- Dependencia nueva: Seguridad y multi-tenant → Superadmin.
- Dependencia nueva: Soporte → Suscripción.
- Dependencia nueva: Soporte → Negocios.
- Dependencia nueva: Soporte → Mail.
- Dependencia nueva: Soporte → Superadmin.
- Dependencia nueva: Soporte → Seguridad y multi-tenant.
- Dependencia nueva: Soporte → Usuarios.
- Entidades JPA: 30 → 38.
- Despliegue: aparece caddy en deploy/.
- Despliegue: aparece backups en deploy/.
- Despliegue: aparece compose en deploy/.
- Pantalla nueva en la app: **delivery-apps**.
- Pantalla nueva en la app: **subscription**.
- Service nuevo en el front: DiagnosticsService (ui).
- Service nuevo en el front: FloorService (http).
- Service nuevo en el front: SalesChannelService (http).
- Service nuevo en el front: SubscriptionService (http).
- Service nuevo en el front: SupportService (http).
- Service nuevo en el front: TourService (ui).

## 2026-11-16 — `3c4df30..174032e`

- Commit analizado: `174032e` (2026-11-06)
- Archivos cambiados desde la corrida anterior: 58 (54 de código o despliegue)
- Diagramas actualizados: c4-2-contenedores.md, c4-3-componentes-backend.md, c4-3-componentes-frontend.md

- Componente nuevo en la API: **Suscripción** (`billing`, rutas /subscription, /webhooks).
- Componente nuevo en la API: **Canales de venta** (`channel`, rutas /sales-channels).
- Componente nuevo en la API: **Reportes** (`report`, rutas /reports).
- Dependencia nueva: Autenticación → Suscripción.
- Dependencia nueva: Suscripción → Negocios.
- Dependencia nueva: Suscripción → Cobros QR (Mercado Pago).
- Dependencia nueva: Suscripción → Seguridad y multi-tenant.
- Dependencia nueva: Canales de venta → Locales.
- Dependencia nueva: Pedidos → Canales de venta.
- Dependencia nueva: Reportes → Negocios.
- Dependencia nueva: Reportes → Caja.
- Dependencia nueva: Reportes → Locales.
- Dependencia nueva: Reportes → Pedidos.
- Dependencia nueva: Reportes → Seguridad y multi-tenant.
- Dependencia nueva: Reportes → Mesas.
- Dependencia nueva: Reportes → Usuarios.
- Entidades JPA: 27 → 30.
- Pantalla nueva en la app: **legal**.
- Pantalla nueva en la app: **superadmin**.
- Service nuevo en el front: DiscountService (http).
- Service nuevo en el front: LegalService (http).
- Service nuevo en el front: OptionGroupService (http).
- Service nuevo en el front: PlatformService (http).

## 2026-11-16 — `3c4df30`

- Commit analizado: `3c4df30` (2026-11-03)
- Diagramas actualizados: c4-1-contexto.md, c4-2-contenedores.md, c4-3-componentes-backend.md, c4-3-componentes-frontend.md

- Primera versión del modelo C4 (contexto, contenedores y componentes).
