# C4 · Nivel 3 — Componentes de la API (Spring Boot)

Generado por la skill `arquitecto-c4` desde el commit `3c4df30`. Cada componente es un paquete de `com.cofeapp.backend` (controller → service → repository); las flechas son dependencias reales entre paquetes (campos inyectados).

```mermaid
flowchart LR
  spa["App web<br/>[Container: Angular]"]
  subgraph API["API · Spring Boot"]
    auth["<b>Autenticación</b><br/>/auth<br/>1C · 3S · 1R"]
    business["<b>Negocios</b><br/>/businesses<br/>1C · 1S · 1R"]
    cash["<b>Caja</b><br/>/cash-sessions<br/>1C · 1S · 3R"]
    category["<b>Categorías</b><br/>/categories<br/>1C · 1S · 1R"]
    crypto["<b>Cifrado</b><br/>1 clase(s) de soporte"]
    dashboard["<b>Panel de inicio</b><br/>/dashboard<br/>1C · 1S · 0R"]
    discount["<b>Descuentos</b><br/>/discounts<br/>1C · 1S · 1R"]
    excel["<b>Exportación Excel</b><br/>1 clase(s) de soporte"]
    location["<b>Locales</b><br/>/locations<br/>1C · 1S · 1R"]
    mail["<b>Mail</b><br/>0C · 1S · 0R"]
    media["<b>Imágenes</b><br/>/media<br/>1C · 1S · 0R"]
    mercadopago["<b>Cobros QR (Mercado Pago)</b><br/>/mercadopago /orders /qr-charges /webhooks<br/>3C · 2S · 2R"]
    option["<b>Variantes y agregados</b><br/>/option-groups /products<br/>1C · 1S · 4R"]
    order["<b>Pedidos</b><br/>/orders<br/>1C · 1S · 4R"]
    product["<b>Productos</b><br/>/products<br/>1C · 1S · 1R"]
    realtime["<b>Tiempo real (STOMP)</b><br/>1 clase(s) de soporte"]
    security["<b>Seguridad y multi-tenant</b><br/>0C · 1S · 0R"]
    stock["<b>Stock</b><br/>/stock<br/>1C · 1S · 6R"]
    table["<b>Mesas</b><br/>/tables<br/>1C · 1S · 1R"]
    user["<b>Usuarios</b><br/>/users<br/>1C · 1S · 1R"]
  end
  db[("MySQL<br/>27 entidades")]
  mp(["Mercado Pago<br/>[Sistema externo]"])
  smtp(["Servidor de mail<br/>[Sistema externo]"])
  spa -->|"REST + JWT"| API
  API -->|"JPA"| db
  auth --> business
  auth --> location
  auth --> mail
  auth --> user
  cash --> location
  cash --> mercadopago
  cash --> order
  cash --> user
  dashboard --> location
  dashboard --> order
  dashboard --> stock
  mercadopago --> cash
  mercadopago --> crypto
  mercadopago --> location
  mercadopago --> order
  option --> product
  option --> stock
  order --> cash
  order --> discount
  order --> location
  order --> mercadopago
  order --> option
  order --> product
  order --> stock
  order --> table
  order --> user
  product --> category
  realtime --> order
  security --> business
  security --> location
  security --> user
  stock --> location
  stock --> product
  stock --> user
  table --> location
  mercadopago -->|"HTTPS"| mp
  mail -->|"SMTP"| smtp
```

Seguridad y multi-tenant es transversal: la usan 8 componentes (Autenticación, Negocios, Caja, Cobros QR (Mercado Pago), Pedidos, Tiempo real (STOMP), Stock, Usuarios); esas flechas no se dibujan para que el diagrama se lea.

C = controllers, S = services, R = repositories. Detalle por paquete:

| Componente | Rutas | Controllers | Services | Repositories |
|---|---|---|---|---|
| Autenticación (`auth`) | /auth | AuthController | AuthService, LoginAttemptService, PasswordResetService | PasswordResetTokenRepository |
| Negocios (`business`) | /businesses | BusinessController | BusinessService | BusinessRepository |
| Caja (`cash`) | /cash-sessions | CashSessionController | CashSessionService | CashMovementRepository, CashSessionDenominationRepository, CashSessionRepository |
| Categorías (`category`) | /categories | CategoryController | CategoryService | CategoryRepository |
| Cifrado (`crypto`) | — | — | — | — |
| Panel de inicio (`dashboard`) | /dashboard | DashboardController | DashboardService | — |
| Descuentos (`discount`) | /discounts | DiscountController | DiscountService | DiscountRepository |
| Exportación Excel (`excel`) | — | — | — | — |
| Locales (`location`) | /locations | LocationController | LocationService | LocationRepository |
| Mail (`mail`) | — | — | MailService | — |
| Imágenes (`media`) | /media | MediaController | FileStorageService | — |
| Cobros QR (Mercado Pago) (`mercadopago`) | /mercadopago, /orders, /qr-charges, /webhooks | MercadoPagoController, MercadoPagoWebhookController, QrChargeController | MercadoPagoAccountService, QrChargeService | MercadoPagoAccountRepository, MpQrChargeRepository |
| Variantes y agregados (`option`) | /option-groups, /products | OptionGroupController | OptionGroupService | OptionGroupRepository, OptionItemRepository, OrderItemOptionRepository, ProductOptionGroupRepository |
| Pedidos (`order`) | /orders | OrderController | OrderService | OrderDiscountRepository, OrderItemRepository, OrderPaymentRepository, OrderRepository |
| Productos (`product`) | /products | ProductController | ProductService | ProductRepository |
| Tiempo real (STOMP) (`realtime`) | — | — | — | — |
| Seguridad y multi-tenant (`security`) | — | — | JwtService | — |
| Stock (`stock`) | /stock | StockController | StockService | IngredientRepository, IngredientStockAdjustmentRepository, IngredientStockRepository, ProductRecipeItemRepository, ProductStockAdjustmentRepository, ProductStockRepository |
| Mesas (`table`) | /tables | TableController | TableService | TableRepository |
| Usuarios (`user`) | /users | UserController | UserService | UserRepository |
