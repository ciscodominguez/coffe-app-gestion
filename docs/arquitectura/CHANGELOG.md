# Changelog de arquitectura

Lo escribe la skill `arquitecto-c4` en cada corrida (lo más nuevo arriba).

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
