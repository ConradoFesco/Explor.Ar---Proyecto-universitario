# Estructura de la Aplicación Web

Este documento describe la estructura modularizada de la aplicación Flask, siguiendo las mejores prácticas de organización de código.

## 📁 Estructura de Directorios

```
src/web/
├── __init__.py              # Factory de la aplicación (limpio y simple)
├── extensions.py            # Inicialización de extensiones (db, migrate, session)
├── blueprints.py            # Registro centralizado de blueprints
├── hooks.py                 # Hooks de Flask (before_request, context_processor)
├── template_filters.py      # Filtros personalizados de Jinja2
├── STRUCTURE.md            # Este archivo
│
├── commands/
│   └── cli.py              # Comandos CLI personalizados
│
├── handlers/
│   └── error.py            # Manejadores de errores HTTP
│
├── routes/                 # Blueprints con rutas
│   ├── main_routes.py      # Rutas principales (vistas HTML)
│   ├── auth_routes.py      # Autenticación
│   ├── user_routes.py      # API de usuarios
│   ├── profile_routes.py   # Perfil de usuario
│   ├── tag_routes.py       # API de tags
│   ├── HistoricSite_Routes.py  # API de sitios históricos
│   ├── state_routes.py     # API de estados
│   ├── category_routes.py  # API de categorías
│   ├── event_routes.py     # API de eventos
│   └── flag_routes.py      # API de flags
│
└── templates/              # Templates Jinja2
    ├── auth/
    ├── shared/
    ├── sites/
    ├── tags/
    └── users/
```

## 📄 Descripción de Archivos

### `__init__.py`
**Responsabilidad**: Factory de la aplicación Flask.

Es el corazón de la aplicación. Su única función es crear y configurar la instancia de Flask de manera limpia y ordenada.

**Funciones principales**:
- `create_app(env, static_folder)`: Crea la aplicación
- `configure_app(app, env)`: Carga configuración
- `initialize_extensions(app)`: Inicializa db, migrate, session
- `register_blueprints(app)`: Registra todos los blueprints
- `register_hooks(app)`: Registra hooks
- `register_filters(app)`: Registra filtros de templates
- `register_error_handlers(app)`: Registra manejadores de errores
- `register_commands(app)`: Registra comandos CLI

**Ventajas**:
- ✅ Código limpio y legible (130 líneas vs 238 anteriores)
- ✅ Separación de responsabilidades
- ✅ Fácil de mantener y testear

### `extensions.py`
**Responsabilidad**: Inicialización de extensiones de Flask.

Define las instancias de las extensiones (SQLAlchemy, Migrate, Session) para evitar importaciones circulares.

```python
db = SQLAlchemy()
migrate = Migrate()
session_ext = Session()
```

### `blueprints.py`
**Responsabilidad**: Registro centralizado de blueprints.

Una única función `register_blueprints(app)` que importa y registra todos los blueprints de la aplicación. Esto reemplaza las múltiples líneas de `app.register_blueprint()`.

**Blueprints registrados**:
- `main` - Rutas principales (vistas HTML)
- `login_bp` - Autenticación
- `profile_bp` - Perfil
- `tag_api` - API de tags
- `site_api` - API de sitios históricos
- `state_api` - API de estados
- `category_api` - API de categorías
- `event_api` - API de eventos
- `flag_api` - API de flags
- `user_api` - API de usuarios

### `hooks.py`
**Responsabilidad**: Hooks de la aplicación Flask.

Contiene la lógica de `@app.before_request` y `@app.context_processor`:

- **`check_admin_maintenance()`**: Verifica el modo mantenimiento antes de cada request
- **`inject_user()`**: Inyecta información del usuario actual en todos los templates

### `template_filters.py`
**Responsabilidad**: Filtros personalizados para templates Jinja2.

- **`format_date(date_value)`**: Formatea fechas al formato DD/MM/YYYY

### `commands/cli.py`
**Responsabilidad**: Comandos CLI personalizados.

Comandos disponibles:
- `flask init-db`: Inicializa la base de datos (crea tablas)
- `flask seed-db`: Ejecuta seeds (datos iniciales)
- `flask reset-db`: Elimina, recrea y ejecuta seeds (⚠️ elimina datos)

### `handlers/error.py`
**Responsabilidad**: Manejadores de errores HTTP.

Maneja errores:
- **404** - Página no encontrada
- **401** - No autorizado
- **500** - Error interno del servidor

Función `register_error_handlers(app)` registra todos los manejadores.

### `routes/main_routes.py`
**Responsabilidad**: Blueprint con rutas principales (vistas HTML).

**Blueprint**: `main`

**Rutas**:
- `GET /` - Página de login
- `GET /home` - Página principal
- `GET /logout` - Cerrar sesión
- `GET /sitios` - Lista de sitios históricos
- `GET /alta-sitios` - Formulario de alta
- `GET /modificar-sitios` - Formulario de modificación
- `GET /tags` - Lista de tags
- `GET /users` - Lista de usuarios
- `GET /users/<id>/editar` - Editar usuario
- `GET /users/nuevo` - Crear usuario

### `routes/[otros blueprints]`
Cada blueprint tiene su propia responsabilidad y agrupa rutas relacionadas (API REST).

## 🚀 Uso

### Crear la aplicación

```python
from src.web import create_app

app = create_app(env="development")
```

### Comandos CLI

```bash
# Inicializar base de datos
flask init-db

# Ejecutar seeds
flask seed-db

# Resetear base de datos (elimina todo)
flask reset-db
```

### Agregar nuevas rutas

1. Crear o editar el blueprint correspondiente en `routes/`
2. Si es necesario, registrarlo en `blueprints.py`

### Agregar nuevos filtros de template

Editar `template_filters.py` y agregar el filtro a `register_filters()`.

### Agregar nuevos hooks

Editar `hooks.py` y agregar el hook a `register_hooks()`.

## 🎯 Beneficios de esta Estructura

1. **Separación de responsabilidades**: Cada archivo tiene una función clara
2. **Facilidad de testing**: Funciones pequeñas y desacopladas
3. **Legibilidad**: Código limpio y organizado
4. **Mantenibilidad**: Fácil encontrar y modificar código
5. **Escalabilidad**: Simple agregar nuevas funcionalidades
6. **Sin código duplicado**: DRY (Don't Repeat Yourself)

## 📚 Referencias

Esta estructura sigue el patrón **Application Factory** de Flask y las recomendaciones oficiales de organización de código para aplicaciones de tamaño mediano/grande.

