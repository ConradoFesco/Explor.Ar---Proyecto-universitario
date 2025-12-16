# Admin - Sitios Históricos

Panel de administración (Flask) para gestionar usuarios, sitios históricos, tags, eventos y feature flags.

## Requisitos
- Python 3.12+
- Poetry
- PostgreSQL (recomendado)
- Node.js y npm (para el frontend público)
- MinIO (para almacenamiento de imágenes)

## Documentación

- **[SETUP.md](SETUP.md)**: Guía completa de configuración, instalación y carga de datos
- Este README: Estructura del proyecto y arquitectura

## Estructura del Proyecto

```
admin/
├─ README.md
├─ SETUP.md                      # Guía de configuración y comandos
├─ scripts/
│  ├─ load_historic_sites.py      # Carga sitios históricos y reseñas
│  ├─ bulk_load_images.py          # Carga masiva de imágenes
│  └─ load_permissions.py
├─ migrations/                     # Migraciones Alembic
├─ static/                         # JS/CSS/imagenes
│  └─ js/
│     ├─ layout.js                 # utilidades globales
│     ├─ login.js                  # login web
│     ├─ home.js                   # mapa home (SSR)
│     ├─ flags.js                  # gestión de feature flags (SweetAlert)
│     ├─ sites.js                  # listado y filtros de sitios
│     ├─ reviews.js                # gestión de reseñas
│     ├─ create_site.js            # alta de sitios (SSR)
│     ├─ edit_site.js               # edición de sitios (SSR)
│     └─ ...
└─ src/
   ├─ core/
   │  ├─ models/                   # Modelos SQLAlchemy
   │  │  ├─ user.py
   │  │  ├─ historic_site.py
   │  │  ├─ review.py
   │  │  ├─ site_image.py
   │  │  ├─ tag.py
   │  │  ├─ event.py
   │  │  └─ ...
   │  ├─ services/                 # Lógica de negocio (MVC)
   │  │  ├─ usuario_service.py
   │  │  ├─ historic_site_service.py
   │  │  ├─ review_service.py
   │  │  ├─ site_image_service.py
   │  │  ├─ tag_service.py
   │  │  ├─ event_service.py
   │  │  └─ flag_service.py
   │  └─ validators/               # Validaciones servidor (entrada/listados)
   │     ├─ utils.py
   │     ├─ user_validator.py
   │     ├─ site_validator.py
   │     ├─ reviews_validator.py
   │     ├─ tag_validator.py
   │     └─ listing_validator.py
   └─ web/
      ├─ __init__.py               # create_app, registros, hooks
      ├─ blueprints_registry.py
      ├─ extensions.py            # db, migrate, session
      ├─ commands/
      │  ├─ cli.py                 # comandos: seed-db, reset-db
      │  └─ seeds.py               # datos iniciales (roles/permisos/flags/super admin)
      ├─ blueprints/
      │  ├─ web/                   # Endpoints Web (render/redirect)
      │  │  ├─ main_pages.py
      │  │  ├─ users_pages.py
      │  │  ├─ sites_pages.py
      │  │  ├─ reviews_pages.py    # moderación de reseñas
      │  │  ├─ sites_events_pages.py
      │  │  ├─ tags_pages.py
      │  │  └─ flags_pages.py
      │  └─ api/                   # Endpoints API (JSON)
      │     ├─ user_routes.py
      │     ├─ historic_site_routes.py
      │     ├─ review_routes.py
      │     └─ flag_routes.py
      ├─ templates/                # Jinja2 (SSR + macros reutilizables)
      │  ├─ layouts/
      │  │  └─ app.html.jinja
      │  ├─ components/
      │  │  ├─ breadcrumbs.html.jinja
      │  │  ├─ page_header.html.jinja
      │  │  └─ paginator.html.jinja
      │  ├─ shared/
      │  │  └─ components/
      │  │     ├─ modal.html
      │  │     └─ search_filters.html
      │  ├─ features/
      │  │  ├─ sites/
      │  │  │  ├─ _list_fragment.html.jinja
      │  │  │  ├─ _item.html.jinja
      │  │  │  └─ ...
      │  │  ├─ reviews/
      │  │  │  ├─ reviews.html.jinja
      │  │  │  ├─ _list_fragment.html.jinja
      │  │  │  └─ _detail_fragment.html.jinja
      │  │  ├─ tags/
      │  │  └─ users/
      │  └─ auth/
      │     └─ login.html
      ├─ auth/
      │  └─ decorators.py          # permisos web
      ├─ hooks.py                  # before_request (mantenimiento), context_processor
      └─ template_filters.py
```

## Notas de Arquitectura

### Separación de Responsabilidades

- **Web (blueprints/web)**: Solo renderiza o redirige; API devuelve JSON.
- **JS**: Consume únicamente endpoints Web; datos iniciales por SSR.
- **Validaciones**: Centralizadas en `src/core/validators/`.
- **Permisos**: Patrón `modulo_accion` (p.ej. `review_index`, `user_new`, `flag_update`).
- **Mensajería**: Unificada con SweetAlert2 a partir de `flash`.

### Modelos y Servicios

- **Modelos (SQLAlchemy)**: No deben depender de Flask; pueden exponer utilidades orientadas al dominio (p. ej., hashing de contraseñas) y `to_dict()` para serialización simple.
- **Servicios**: Toda la lógica de negocio/composición de datos debe residir en `src/core/services/`.
- **Controladores Web**: Renderizan plantillas con datos preparados por Services (`render_template('tpl', **data)`).
- **Controladores API**: Serializan respuesta desde Services y devuelven JSON.

### Convenciones de Plantillas (Jinja)

- **Componentes reutilizables**: En `src/web/templates/components/`.
- **Shared components**: `shared/components/` reservado para piezas cross-página no visualmente acopladas a UI (p. ej., `modal.html`, `search_filters.html`).
- **Evitar duplicados**: Entre `components/` y `shared/components/`.
  - Paginación consolidada en `components/paginator.html.jinja`.
  - Si se requiere una variante JS, usar el macro `render_pagination_js` en el mismo archivo.
- **Importar macros**: Con `{% import 'components/...' as x %}` o `{% from 'components/...' import y %}`.
- **Lógica de negocio**: Mantener fuera de las plantillas; solo presentación.

## Scripts Disponibles

### `load_historic_sites.py`
Carga 15 sitios históricos con datos completos:
- Crea provincias, ciudades, categorías y estados si no existen
- Genera reseñas asociadas en distintos estados (pending, approved, rejected)
- **Ubicación**: `admin/scripts/load_historic_sites.py`

### `bulk_load_images.py`
Carga imágenes de placeholder para sitios sin imágenes:
- Rango configurable de imágenes por sitio (por defecto: 3-7)
- Usa imágenes de placeholder de Picsum Photos (provisorio)
- **Ubicación**: `admin/scripts/bulk_load_images.py`

## Credenciales de Acceso

### Usuario Super Administrador
- **Email**: `grupo06@gmail.com`
- **Contraseña**: `grupo06`
- **Super admin**: `True`

> **⚠️ IMPORTANTE**: Cambiar estas credenciales en producción.
