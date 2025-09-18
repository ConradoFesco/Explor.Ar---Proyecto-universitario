# Modelos SQLAlchemy - Sistema de Sitios Históricos

Este proyecto implementa un sistema de gestión de sitios históricos utilizando Flask-SQLAlchemy y PostgreSQL. Los modelos representan las entidades del sistema de base de datos relacional.

## 📋 Estructura del Proyecto

```
admin/
├── src/web/
│   ├── models/                 # Modelos SQLAlchemy
│   │   ├── __init__.py        # Importaciones de todos los modelos
│   │   ├── user.py            # Modelo de Usuario
│   │   ├── category_site.py   # Modelo de Categoría de Sitio
│   │   ├── province.py        # Modelo de Provincia
│   │   ├── city.py            # Modelo de Ciudad
│   │   ├── state_site.py      # Modelo de Estado de Sitio
│   │   ├── historic_site.py   # Modelo de Sitio Histórico
│   │   ├── tag.py             # Modelo de Tag
│   │   ├── event.py           # Modelo de Evento
│   │   ├── permission.py      # Modelo de Permiso
│   │   ├── rol_user.py        # Modelo de Rol de Usuario
│   │   ├── permission_rol_user.py  # Tabla de relación Permiso-Rol
│   │   ├── rol_user_user.py   # Tabla de relación Rol-Usuario
│   │   └── tag_historic_site.py    # Tabla de relación Tag-Sitio
│   └── __init__.py            # Configuración de la aplicación
├── tests/
│   └── test_models.py         # Pruebas unitarias de los modelos
├── example_usage.py           # Ejemplo de uso de los modelos
├── config.env                 # Archivo de configuración de ejemplo
└── README_MODELS.md           # Este archivo
```

## 🗄️ Modelos de Base de Datos

### Entidades Principales

1. **User** - Usuarios del sistema
2. **CategorySite** - Categorías de sitios históricos
3. **Province** - Provincias
4. **City** - Ciudades
5. **StateSite** - Estados de conservación de sitios
6. **HistoricSite** - Sitios históricos
7. **Tag** - Etiquetas para clasificar sitios
8. **Event** - Eventos/acciones realizadas en sitios

### Entidades de Seguridad

9. **Permission** - Permisos del sistema
10. **RolUser** - Roles de usuario
11. **PermissionRolUser** - Relación Permiso-Rol
12. **RolUserUser** - Relación Rol-Usuario

### Tablas de Relación

13. **TagHistoricSite** - Relación Tag-Sitio Histórico

## 🚀 Configuración Inicial

### 1. Instalar Dependencias

```bash
# Instalar Poetry (si no lo tienes)
curl -sSL https://install.python-poetry.org | python3 -

# Instalar dependencias
poetry install
```

### 2. Configurar Variables de Entorno

Copia el archivo de configuración de ejemplo:

```bash
cp config.env .env
```

Edita el archivo `.env` con tus credenciales de PostgreSQL:

```env
# Configuración de Base de Datos PostgreSQL
DATABASE_URL=postgresql://usuario:contraseña@host:puerto/nombre_db

# Configuración de la aplicación Flask
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=tu_clave_secreta_aqui
```

### 3. Crear Base de Datos

```bash
# Crear la base de datos en PostgreSQL
createdb historic_sites_db

# Inicializar migraciones
flask db init

# Crear migración inicial
flask db migrate -m "Initial migration"

# Aplicar migraciones
flask db upgrade
```

## 📝 Uso de los Modelos

### Ejemplo Básico

```python
from src.web import create_app, db
from src.web.models import User, HistoricSite, CategorySite

app = create_app()

with app.app_context():
    # Crear una categoría
    category = CategorySite(name='Monumento Histórico')
    db.session.add(category)
    db.session.commit()
    
    # Crear un sitio histórico
    site = HistoricSite(
        name='Casa Rosada',
        brief_description='Sede del gobierno argentino',
        latitude='-34.6083',
        longitude='-58.3712',
        id_category=category.id,
        visible=True
    )
    db.session.add(site)
    db.session.commit()
    
    # Consultar sitios
    sites = HistoricSite.query.filter_by(visible=True).all()
    for site in sites:
        print(f"Sitio: {site.name}")
```

### Relaciones

```python
# Obtener un sitio con sus relaciones
site = HistoricSite.query.get(1)
print(f"Sitio: {site.name}")
print(f"Categoría: {site.category.name}")
print(f"Ciudad: {site.city.name}")
print(f"Estado: {site.state_site.state}")

# Obtener eventos de un sitio
events = site.events
for event in events:
    print(f"Evento: {event.type_Action} por {event.user.name}")
```

## 🧪 Ejecutar Pruebas

```bash
# Ejecutar todas las pruebas
python -m pytest tests/

# Ejecutar pruebas con verbose
python -m pytest tests/ -v

# Ejecutar una prueba específica
python -m pytest tests/test_models.py::TestUser::test_create_user -v
```

## 📊 Ejemplo Completo

Ejecuta el script de ejemplo para ver los modelos en acción:

```bash
python example_usage.py
```

Este script:
- Configura la base de datos
- Crea datos de ejemplo
- Demuestra consultas comunes
- Muestra las relaciones entre modelos

## 🔧 Comandos Útiles

### Flask-Migrate

```bash
# Crear nueva migración
flask db migrate -m "Descripción del cambio"

# Aplicar migraciones
flask db upgrade

# Revertir migración
flask db downgrade

# Ver historial de migraciones
flask db history
```

### Consultas Comunes

```python
# Obtener todos los sitios visibles
sites = HistoricSite.query.filter_by(visible=True).all()

# Obtener sitios por categoría
monuments = HistoricSite.query.join(CategorySite).filter(
    CategorySite.name == 'Monumento Histórico'
).all()

# Obtener usuarios activos
active_users = User.query.filter_by(active=True).all()

# Obtener eventos recientes
recent_events = Event.query.order_by(Event.date_time.desc()).limit(10).all()

# Obtener sitios con tags específicos
cultural_sites = HistoricSite.query.join(TagHistoricSite).join(Tag).filter(
    Tag.name == 'Cultura'
).all()
```

## 📚 Métodos Disponibles

Cada modelo incluye:

- **`__repr__()`** - Representación string del objeto
- **`to_dict()`** - Convierte el objeto a diccionario (sin campos sensibles)

### Ejemplo de uso de to_dict()

```python
user = User.query.get(1)
user_data = user.to_dict()
# Retorna: {'id': 1, 'mail': 'user@example.com', 'name': 'Juan', ...}
# Nota: 'password' no está incluido por seguridad
```

## 🛡️ Seguridad

- Las contraseñas no se incluyen en `to_dict()`
- Los campos `deleted` permiten soft delete
- Los permisos y roles están implementados para control de acceso

## 🐛 Solución de Problemas

### Error de Conexión a Base de Datos

1. Verifica que PostgreSQL esté ejecutándose
2. Confirma las credenciales en `.env`
3. Asegúrate de que la base de datos existe

### Error de Importación

```python
# Asegúrate de importar correctamente
from src.web.models import User, HistoricSite
# No uses: from models import User
```

### Error de Migraciones

```bash
# Si hay conflictos, puedes reiniciar las migraciones
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 📞 Soporte

Para problemas o preguntas:

1. Revisa los logs de la aplicación
2. Verifica la configuración de la base de datos
3. Ejecuta las pruebas para identificar problemas
4. Consulta la documentación de Flask-SQLAlchemy

## 🔄 Próximos Pasos

1. Implementar API REST con Flask-RESTful
2. Agregar validaciones de datos
3. Implementar autenticación JWT
4. Crear interfaz web con templates
5. Agregar documentación automática con Swagger
