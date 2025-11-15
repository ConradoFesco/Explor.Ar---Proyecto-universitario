# Admin - Sitios Históricos

Panel de administración (Flask) para gestionar usuarios, sitios históricos, tags, eventos y feature flags.

## Requisitos
- Python 3.12+
- Poetry
- PostgreSQL (recomendado)

## Configuración rápida (Windows PowerShell)
1) Variables de entorno mínimas (.env)
```
FLASK_ENV=development
SECRET_KEY=dev-secret
SESSION_TYPE=filesystem
DATABASE_URL=postgresql+psycopg2://usuario:password@localhost:5432/nombre_db
```

2) Instalar dependencias
```
poetry install
```

3) Migraciones de base de datos
```
# Dentro de admin/
$env:FLASK_APP="src.web:create_app"; $env:FLASK_ENV="development"
poetry run flask db upgrade
```

4) Cargar datos iniciales (seeds)
```
poetry run python run_seeds.py
# o bien
poetry run flask seed-db
```

5) Levantar la aplicación
```
poetry run flask run
```

## Credenciales de prueba
- Email: `grupo06@gmail.com`
- Contraseña: `grupo06`
- Super admin: `True`

> Importante: cambiar estas credenciales en producción.

## Estructura del proyecto
```
admin/
├─ README.md
├─ run_seeds.py
├─ migrations/                 # Migraciones Alembic
├─ static/                     # JS/CSS/imagenes
│  └─ js/
│     ├─ layout.js             # utilidades globales
│     ├─ login.js              # login web
│     ├─ home.js               # mapa home (SSR)
│     ├─ flags.js              # gestión de feature flags (SweetAlert)
│     ├─ sites.js              # listado y filtros de sitios
│     ├─ create_site.js        # alta de sitios (SSR)
│     └─ edit_site.js          # edición de sitios (SSR)
└─ src/
   ├─ core/
   │  ├─ models/               # Modelos SQLAlchemy
   │  ├─ services/             # Lógica de negocio (MVC)
   │  │  ├─ usuario_service.py
   │  │  ├─ historic_site_service.py
   │  │  ├─ tag_service.py
   │  │  ├─ event_service.py
   │  │  └─ flag_service.py
   │  └─ validators/           # Validaciones servidor (entrada/listados)
   │     ├─ utils.py
   │     ├─ user_validator.py
   │     ├─ site_validator.py
   │     ├─ tag_validator.py
   │     └─ listing_validator.py
   └─ web/
      ├─ __init__.py           # create_app, registros, hooks
      ├─ blueprints_registry.py
      ├─ extensions.py         # db, migrate, session
      ├─ commands/
      │  ├─ cli.py             # comandos: seed-db, reset-db
      │  └─ seeds.py           # datos iniciales (roles/permisos/flags/super admin)
      ├─ blueprints/
      │  ├─ web/               # Endpoints Web (render/redirect)
      │  │  ├─ main_pages.py
      │  │  ├─ users_pages.py
      │  │  ├─ sites_pages.py
      │  │  ├─ sites_events_pages.py
      │  │  ├─ tags_pages.py
      │  │  └─ flags_pages.py
      │  └─ api/               # Endpoints API (JSON)
      │     ├─ user_routes.py
      │     ├─ historic_site_routes.py
      │     └─ flag_routes.py
      ├─ templates/            # Jinja2 (SSR + macros reutilizables)
      │  ├─ layouts/
      │  ├─ components/
      │  ├─ shared/
      │  ├─ features/
      │  │  └─ sites/
      │  └─ users/ | sites/ | tags/ | flags/
      ├─ auth/
      │  └─ decorators.py      # permisos web
      ├─ hooks.py              # before_request (mantenimiento), context_processor
      └─ template_filters.py
```

## Notas de arquitectura
- Web (blueprints/web) sólo renderiza o redirige; API devuelve JSON.
- JS consume únicamente endpoints Web; datos iniciales por SSR.
- Validaciones del lado servidor centralizadas en `src/core/validators/`.
- Permisos con patrón `modulo_accion` (p.ej. `flag_admin`, `create_user`).
- Mensajería unificada con SweetAlert2 a partir de `flash`.

## Convenciones de plantillas (Jinja)
- Componentes reutilizables de UI en `src/web/templates/components/`.
- `shared/components/` reservado para piezas cross-página no visualmente acopladas a UI (p. ej., `modal.html`, `search_filters.html`).
- Evitar duplicados entre `components/` y `shared/components/`.
  - Paginación consolidada en `components/paginator.html.jinja`.
  - Si se requiere una variante JS, usar el macro `render_pagination_js` en el mismo archivo.
- Importar macros con `{% import 'components/...' as x %}` o `{% from 'components/...' import y %}`.
- Mantener lógica de negocio fuera de las plantillas; sólo presentación.

## Modelos y Servicios
- Los Modelos (SQLAlchemy) no deben depender de Flask; pueden exponer utilidades orientadas al dominio (p. ej., hashing de contraseñas) y `to_dict()` para serialización simple.
- Toda la lógica de negocio/composición de datos debe residir en `src/core/services/`.
- Controladores Web: renderizan plantillas con datos preparados por Services (`render_template('tpl', **data)`).
- Controladores API: serializan respuesta desde Services (por Marshmallow) y devuelven JSON.

## Comandos útiles
```
# Estado de migraciones
poetry run flask db current

# Nueva migración (ej.)
poetry run flask db migrate -m "mensaje"
poetry run flask db upgrade

# Seeds
poetry run flask seed-db
poetry run flask reset-db    # ⚠️ elimina datos
```


