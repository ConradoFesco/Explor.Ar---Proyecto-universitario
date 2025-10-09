# Sistema de Permisos - Guía de Uso

## 📋 Descripción

Este sistema de permisos permite controlar el acceso a diferentes funcionalidades de la aplicación mediante decoradores. Los usuarios tienen roles, y los roles tienen permisos específicos.

## 🏗️ Arquitectura

```
Usuario → Rol → Permisos
```

- **Usuario**: Tiene uno o más roles
- **Rol**: Tiene uno o más permisos
- **Permiso**: Autoriza una acción específica

## 🚀 Configuración Inicial

### 1. Cargar Permisos y Roles

Ejecuta el script para crear todos los permisos, roles y relaciones:

```bash
cd admin
python scripts/load_permissions.py
```

Este script:
- ✅ Crea todos los permisos necesarios
- ✅ Crea los roles: admin, editor, moderator, viewer
- ✅ Asigna permisos a cada rol
- ✅ Crea un usuario administrador por defecto

### 2. Usuario Administrador

Se crea automáticamente un usuario administrador:
- **Email**: admin@admin.com
- **Contraseña**: admin123
- **Rol**: admin (acceso completo)

⚠️ **IMPORTANTE**: Cambia la contraseña por defecto en producción.

## 🎭 Roles Disponibles

### Admin
- Acceso completo a todas las funcionalidades
- Puede gestionar usuarios, roles y permisos

### Editor
- Puede crear, editar y eliminar contenido
- No puede gestionar usuarios

### Moderator
- Puede moderar contenido de otros usuarios
- No puede crear nuevo contenido

### Viewer
- Solo puede ver contenido
- No puede crear, editar o eliminar

## 🔧 Gestión de Usuarios y Roles

### Asignar Roles a Usuarios

```bash
python scripts/assign_user_roles.py
```

Este script te permite:
- Ver todos los usuarios y roles
- Asignar roles a usuarios
- Remover roles de usuarios
- Ver permisos de cada usuario

### Asignar Rol Programáticamente

```python
from src.core.models.user import User
from src.core.models.rol_user import RolUser
from src.core.models.rol_user_user import RolUserUser

# Obtener usuario y rol
user = User.query.filter_by(mail="usuario@ejemplo.com").first()
role = RolUser.query.filter_by(name="editor").first()

# Asignar rol
user_role = RolUserUser(
    User_id=user.id,
    Rol_User_id=role.id
)
db.session.add(user_role)
db.session.commit()
```

## 🛡️ Uso de Decoradores

### En las Rutas

```python
from src.web.auth.decorators import permission_required

@site_api.route('/HistoricSite_Routes', methods=['POST'])
@permission_required("create_historic_site")
def create_historic_site():
    # Tu código aquí
    pass
```

### Permisos Disponibles

#### Sitios Históricos
- `create_historic_site` - Crear sitio histórico
- `get_historic_site` - Ver sitio específico
- `get_all_historic_sites` - Listar sitios
- `get_all_sites_for_map` - Obtener sitios para mapa
- `update_historic_site` - Actualizar sitio
- `delete_historic_site` - Eliminar sitio
- `add_tags` - Agregar tags
- `update_tags` - Actualizar tags
- `get_filter_options` - Obtener opciones de filtro

#### Usuarios
- `create_user` - Crear usuario
- `get_user` - Ver usuario
- `get_all_users` - Listar usuarios
- `update_user` - Actualizar usuario
- `delete_user` - Eliminar usuario

#### Categorías
- `create_category` - Crear categoría
- `get_category` - Ver categoría
- `get_all_categories` - Listar categorías
- `update_category` - Actualizar categoría
- `delete_category` - Eliminar categoría

#### Tags
- `create_tag` - Crear tag
- `get_tag` - Ver tag
- `get_all_tags` - Listar tags
- `update_tag` - Actualizar tag
- `delete_tag` - Eliminar tag

#### Eventos
- `create_event` - Crear evento
- `get_event` - Ver evento
- `get_all_events` - Listar eventos
- `update_event` - Actualizar evento
- `delete_event` - Eliminar evento

#### Estados
- `create_state` - Crear estado
- `get_state` - Ver estado
- `get_all_states` - Listar estados
- `update_state` - Actualizar estado
- `delete_state` - Eliminar estado

## 🧪 Pruebas

### Probar el Sistema

```bash
python scripts/test_permissions.py
```

Este script:
- ✅ Verifica que todos los permisos estén cargados
- ✅ Prueba los decoradores
- ✅ Verifica acceso a rutas
- ✅ Crea usuario de prueba

### Probar Decoradores en Rutas

1. **Descomenta los decoradores** en `HistoricSite_Routes.py`:

```python
@site_api.route('/HistoricSite_Routes', methods=['POST'])
@permission_required("create_historic_site")  # Descomenta esta línea
def create_historic_site():
    # ...
```

2. **Inicia sesión** con un usuario que tenga permisos

3. **Prueba las rutas** protegidas

### Verificar Permisos de Usuario

```python
# Obtener usuario
user = User.query.filter_by(mail="usuario@ejemplo.com").first()

# Ver permisos
print(user.permissions)  # Lista de permisos

# Ver roles
for user_role in user.user_roles:
    print(user_role.rol_user.name)
```

## 🔍 Solución de Problemas

### Error: "Usuario no autenticado"
- Verifica que el usuario esté logueado
- Revisa que `session['user_id']` esté establecido

### Error: "Usuario no tiene roles asignados"
- Asigna un rol al usuario usando `assign_user_roles.py`

### Error: "Acceso denegado"
- Verifica que el usuario tenga el permiso requerido
- Revisa que el rol tenga el permiso asignado

### Decorador no funciona
- Verifica que el permiso exista en la base de datos
- Confirma que el usuario tenga el rol correcto
- Revisa que el rol tenga el permiso asignado

## 📝 Ejemplo Completo

```python
# 1. Crear usuario
user = User(mail="test@test.com", name="Test", last_name="User")
user.set_password("password123")
db.session.add(user)

# 2. Asignar rol
role = RolUser.query.filter_by(name="editor").first()
user_role = RolUserUser(User_id=user.id, Rol_User_id=role.id)
db.session.add(user_role)

# 3. Usar en ruta
@permission_required("create_historic_site")
def create_site():
    return jsonify({"message": "Sitio creado"})

# 4. Verificar permisos
print(user.permissions)  # ['create_historic_site', 'get_historic_site', ...]
```

## 🚨 Consideraciones de Seguridad

1. **Cambiar contraseña por defecto** del usuario admin
2. **Validar permisos** en el frontend también
3. **Auditar** cambios de roles y permisos
4. **Usar HTTPS** en producción
5. **Implementar rate limiting** para prevenir ataques

## 📞 Soporte

Si tienes problemas con el sistema de permisos:

1. Ejecuta `test_permissions.py` para diagnosticar
2. Verifica que todos los scripts se ejecutaron correctamente
3. Revisa los logs de la aplicación
4. Confirma que la base de datos esté actualizada
