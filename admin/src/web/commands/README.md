# Seeds - Datos Iniciales para Producción

Este directorio contiene scripts para inicializar la base de datos con los datos necesarios para que el sistema funcione en producción.

## 📋 Script: seeds.py

Carga los datos iniciales mínimos necesarios para el funcionamiento del sistema.

### Datos que se cargan:

#### 🔐 **Permisos (78 permisos)**
Todos los permisos necesarios para el funcionamiento del sistema, organizados por módulos:
- Sitios históricos
- Usuarios
- Categorías
- Tags
- Eventos
- Estados
- Flags
- Perfil de usuario

#### 👥 **Roles (3 roles)**
- `admin` - Administrador sin acceso a flags
- `editor` - Editor de contenido
- `usuario` - Usuario básico

#### 🏛️ **Categorías (3 categorías)**
- Arquitectura
- Infraestructura
- Sitio arqueologico

#### 📊 **Estados de Conservación (3 estados)**
- Bueno
- Regular
- Malo

#### 🚩 **Flags (3 flags)**
- `admin_maintenance_mode` - Modo mantenimiento del panel admin (desactivado)
- `portal_maintenance_mode` - Modo mantenimiento del portal público (desactivado)
- `reviews_enabled` - Reviews habilitadas (activado)

#### 👤 **Usuario Super Administrador**
- **Email**: grupo06@gmail.com
- **Nombre**: grupo
- **Apellido**: 06
- **Contraseña**: grupo06
- **Super admin**: True

⚠️ **IMPORTANTE**: Cambiar estas credenciales inmediatamente después del despliegue en producción.

## 🚀 Uso

### Opción 1: Ejecutar directamente
```bash
python admin/src/web/commands/seeds.py
```

### Opción 2: Desde el directorio de comandos
```bash
cd admin/src/web/commands
python seeds.py
```

### Opción 3: Usando el intérprete de Python
```bash
cd admin
python -m src.web.commands.seeds
```

## 📝 Notas

- El script verifica si los datos ya existen antes de crearlos (es idempotente)
- No duplicará datos si se ejecuta múltiples veces
- Los datos se crean en una transacción, si algo falla se hace rollback
- Se muestra un resumen detallado al finalizar

## ⚠️ Advertencias

1. **Credenciales por defecto**: El super admin se crea con credenciales básicas. **Cámbialas inmediatamente en producción**.
2. **Base de datos vacía**: Este script está diseñado para ejecutarse en una base de datos recién creada.
3. **Migraciones primero**: Asegúrate de ejecutar las migraciones de la base de datos antes de ejecutar este script.

## 🔄 Flujo recomendado para despliegue

1. Crear la base de datos
2. Ejecutar migraciones: `flask db upgrade`
3. Ejecutar seeds: `python admin/src/web/commands/seeds.py`
4. Cambiar credenciales del super admin
5. Verificar que el sistema funciona correctamente

