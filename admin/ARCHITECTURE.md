# Arquitectura del Proyecto

## Estructura del Proyecto

Este proyecto sigue una arquitectura en capas que separa claramente las responsabilidades:

```
admin/
├── src/
│   ├── core/                    # Capa de lógica de negocio
│   │   ├── models/             # Modelos de datos (entidades)
│   │   │   ├── user.py
│   │   │   ├── historic_site.py
│   │   │   ├── event.py
│   │   │   ├── tag.py
│   │   │   ├── flag.py
│   │   │   └── ...
│   │   └── services/           # Servicios de negocio
│   │       ├── auth_service.py
│   │       ├── usuario_service.py
│   │       ├── HistoricSite_Service.py
│   │       ├── event_service.py
│   │       └── ...
│   │
│   └── web/                    # Capa de presentación
│       ├── routes/             # Controladores (endpoints)
│       │   ├── auth_routes.py
│       │   ├── user_routes.py
│       │   ├── HistoricSite_Routes.py
│       │   └── ...
│       ├── templates/          # Vistas HTML organizadas por entidad
│       │   ├── auth/          # Templates de autenticación
│       │   ├── users/         # Templates de usuarios
│       │   ├── sites/         # Templates de sitios históricos
│       │   ├── tags/          # Templates de tags
│       │   ├── flags/         # Templates de feature flags
│       │   ├── events/        # Templates de eventos
│       │   └── shared/        # Templates compartidos (layouts, errores)
│       ├── auth/              # Decoradores de autenticación
│       ├── handlers/          # Manejadores de errores
│       ├── commands/          # Comandos CLI (seeds)
│       ├── extensions.py      # Extensiones de Flask (db, migrate, etc.)
│       └── exceptions.py      # Excepciones personalizadas
│
├── static/                     # Archivos estáticos (CSS, JS, imágenes)
├── migrations/                 # Migraciones de base de datos
├── scripts/                    # Scripts utilitarios
├── config.py                   # Configuraciones del proyecto
├── main.py                     # Punto de entrada de la aplicación
└── pyproject.toml             # Gestión de dependencias con Poetry

```

## Capas de la Arquitectura

### 1. Core Layer (src/core/)
Contiene la lógica de negocio pura, independiente de la capa de presentación:

- **Models**: Definición de entidades y modelos de datos (ORM)
  - Representan las tablas de la base de datos
  - Contienen métodos de instancia relacionados con la entidad
  - No dependen de Flask directamente

- **Services**: Lógica de negocio
  - Contienen las reglas de negocio de la aplicación
  - Manejan transacciones y operaciones complejas
  - Son llamados por los controladores (routes)

### 2. Web Layer (src/web/)
Capa de presentación y manejo de peticiones HTTP:

- **Routes**: Controladores que manejan peticiones HTTP
  - Definen los endpoints de la API
  - Validan datos de entrada
  - Llaman a los servicios correspondientes
  - Retornan respuestas JSON o renderizan templates

- **Templates**: Vistas HTML organizadas por entidad
  - `auth/`: Login, mantenimiento
  - `users/`: CRUD de usuarios, perfil
  - `sites/`: CRUD de sitios históricos
  - `tags/`: Gestión de etiquetas
  - `flags/`: Feature flags
  - `shared/`: Layouts, errores, home

- **Auth**: Decoradores para autorización y autenticación
- **Handlers**: Manejadores de errores HTTP
- **Commands**: Comandos CLI (seeds, migraciones)
- **Extensions**: Inicialización de extensiones (SQLAlchemy, Flask-Migrate)
- **Exceptions**: Excepciones personalizadas

## Flujo de Peticiones

```
Request → Route → Service → Model → Database
                     ↓
                  Response
```

1. **Request**: Petición HTTP llega a un endpoint
2. **Route**: El controlador valida datos y llama al servicio
3. **Service**: Ejecuta la lógica de negocio y usa los modelos
4. **Model**: Interactúa con la base de datos
5. **Response**: Se retorna la respuesta (JSON o HTML)

## Principios de Diseño

### Separación de Responsabilidades
- **Routes**: Solo manejan HTTP (request/response)
- **Services**: Contienen toda la lógica de negocio
- **Models**: Definen estructura de datos y relaciones

### Organización de Templates
Los templates están organizados por entidad para facilitar el mantenimiento:
- Fácil de encontrar templates relacionados
- Evita conflictos de nombres
- Mejora la escalabilidad

### Gestión de Dependencias
- Se usa **Poetry** para gestión de dependencias
- `pyproject.toml` define todas las dependencias
- No se usa `requirements.txt`

## Comandos Útiles

### Ejecutar la aplicación
```bash
cd admin
poetry run python main.py
```

### Ejecutar migraciones
```bash
cd admin
poetry run flask db upgrade
```

### Ejecutar seeds
```bash
cd admin
poetry run python run_seeds.py
```

## Mejores Prácticas

1. **Imports**: Usar imports absolutos (`from src.core.models.user import User`)
2. **Templates**: Usar rutas relativas a la carpeta templates (`users/list_users.html`)
3. **Services**: Toda la lógica de negocio debe estar en servicios
4. **Routes**: Los controladores deben ser delgados (thin controllers)
5. **Models**: Los modelos solo deben tener métodos relacionados con la entidad

## Convenciones de Código

- **Nombres de archivos**: snake_case (user_routes.py)
- **Nombres de clases**: PascalCase (UserService)
- **Nombres de funciones**: snake_case (get_user_by_id)
- **Templates**: Organizados por entidad en carpetas separadas

