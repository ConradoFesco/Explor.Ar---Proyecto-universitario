# Guía de Configuración y Comandos

Esta guía explica paso a paso cómo configurar el proyecto, cargar datos y ejecutar las aplicaciones.

## Requisitos Previos

- Python 3.12+
- Poetry instalado
- PostgreSQL configurado y ejecutándose
- Node.js y npm (para el frontend público)
- MinIO (para almacenamiento de imágenes)

## Configuración Inicial

### 1. Variables de Entorno

Crear un archivo `.env` en la carpeta `admin/` con las siguientes variables:

```env
FLASK_ENV=development
SECRET_KEY=dev-secret
SESSION_TYPE=filesystem
DATABASE_URL=postgresql+psycopg2://usuario:password@localhost:5432/nombre_db
MINIO_SERVER=127.0.0.1:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=False
MINIO_USE_HTTPS=True
```

**Explicación de variables:**
- `DATABASE_URL`: URL de conexión a PostgreSQL
- `MINIO_SERVER`: Dirección y puerto del servidor MinIO
- `MINIO_ACCESS_KEY` y `MINIO_SECRET_KEY`: Credenciales de acceso a MinIO
- `MINIO_SECURE`: `False` para conexiones HTTP, `True` para HTTPS (usado para la conexión del cliente MinIO)
- `MINIO_USE_HTTPS`: `True` para forzar URLs públicas HTTPS (útil cuando la app está en HTTPS pero MinIO usa HTTP internamente)

### 2. Instalar Dependencias

```bash
cd admin
poetry install
```

Este comando instalará todas las dependencias definidas en `pyproject.toml`.

### 3. Verificar y Aplicar Migraciones

Verificar si hay migraciones pendientes:

```bash
cd admin
poetry run flask db check
```

Si hay migraciones pendientes, aplicarlas:

```bash
poetry run flask db upgrade
```

## Carga de Datos

Sigue estos pasos en orden para cargar todos los datos necesarios:

### Paso 1: Resetear la Base de Datos

Este comando elimina todas las tablas, las recrea y carga los datos iniciales (permisos, roles, usuarios, categorías, estados, flags):

```bash
cd admin
poetry run flask reset-db --yes
```

**⚠️ ADVERTENCIA**: Este comando elimina TODOS los datos existentes en la base de datos.

**¿Qué hace este comando?**
- Elimina todas las tablas existentes
- Crea todas las tablas desde cero
- Ejecuta los seeds que crean:
  - 39 permisos del sistema
  - 4 roles (admin, editor, moderador, usuario)
  - 89 relaciones permiso-rol
  - 3 categorías de sitios
  - 3 estados de conservación
  - 3 flags del sistema
  - Usuario super administrador (grupo06@gmail.com)
  - 3 usuarios dummy de prueba
  - 3 sitios dummy de prueba (si no hay sitios)
  - 6 reseñas de prueba

### Paso 2: Cargar Sitios Históricos

Este script carga 15 sitios históricos con sus datos completos y crea reseñas asociadas:

```bash
cd admin
poetry run python scripts/load_historic_sites.py
```

**¿Qué hace este script?**
- Crea/verifica provincias, ciudades, categorías y estados
- Carga 15 sitios históricos de Buenos Aires y La Plata
- Genera entre 2 y 5 reseñas por sitio en distintos estados:
  - 40% pendientes
  - 40% aprobadas
  - 20% rechazadas (con motivo de rechazo)

### Paso 3: Cargar Imágenes

Este script carga imágenes de placeholder para todos los sitios históricos que no tengan imágenes:

```bash
cd admin
poetry run python scripts/bulk_load_images.py
```

**Opciones personalizadas:**

```bash
# Cargar entre 5 y 10 imágenes por sitio
poetry run python scripts/bulk_load_images.py --min-images 5 --max-images 10

# Especificar usuario que realiza la carga
poetry run python scripts/bulk_load_images.py --user-id 1
```

**¿Qué hace este script?**
- Busca todos los sitios históricos sin imágenes
- Descarga imágenes de placeholder desde Picsum Photos
- Carga entre 3 y 7 imágenes por sitio (configurable)
- Marca automáticamente la primera imagen como portada
- Genera títulos y descripciones automáticamente

> **Nota**: Este script es provisorio y usa imágenes de placeholder. Para producción, reemplaza las URLs en el script por imágenes reales.

## Ejecución del Proyecto

El proyecto requiere **3 terminales** ejecutándose simultáneamente:

### Terminal 1: Aplicación Privada (Admin)

```bash
cd admin
poetry run flask run
```

La aplicación estará disponible en: `http://localhost:5000`

**Credenciales de acceso:**
- Email: `grupo06@gmail.com`
- Contraseña: `grupo06`

### Terminal 2: Aplicación Pública (Portal)

```bash
cd portal
npm run dev
```

La aplicación estará disponible en: `http://localhost:5173` (o el puerto que Vite asigne)

### Terminal 3: MinIO (Almacenamiento de Imágenes)

**Requisitos previos:**
- Tener una carpeta `minio/` con los ejecutables:
  - `minio.exe` (servidor MinIO)
  - `mc.exe` (cliente MinIO para administración)
- Crear una carpeta interna para almacenar las fotos (ej: `minio/data/`)

**Comando para ejecutar MinIO:**

```bash
# [COMPLETAR CON EL COMANDO CORRECTO]
# Ejemplo (ajustar según tu configuración):
# cd minio
# ./minio.exe server ./data --console-address ":9001"
```

**Configuración recomendada:**
- Puerto del servidor: `9000` (debe coincidir con `MINIO_SERVER` en `.env`)
- Puerto de consola: `9001` (opcional, para interfaz web de administración)
- Carpeta de datos: `./data` o la ruta que prefieras

> **Nota**: Asegúrate de que MinIO esté configurado con las credenciales que coincidan con las variables de entorno en el `.env` (por defecto: `minioadmin` / `minioadmin`).

## Comandos Útiles

### Migraciones

```bash
# Ver migración actual aplicada
poetry run flask db current

# Verificar si hay cambios pendientes en los modelos
poetry run flask db check

# Crear nueva migración (después de modificar modelos)
poetry run flask db migrate -m "descripción del cambio"

# Aplicar todas las migraciones pendientes
poetry run flask db upgrade

# Revertir última migración
poetry run flask db downgrade
```

### Seeds y Datos

```bash
# Cargar datos iniciales (sin resetear)
poetry run flask seed-db

# Resetear base de datos y cargar seeds
poetry run flask reset-db --yes

# Inicializar base de datos (crear tablas sin seeds)
poetry run flask init-db
```

### Scripts de Carga

```bash
# Cargar sitios históricos
poetry run python scripts/load_historic_sites.py

# Cargar imágenes (con opciones)
poetry run python scripts/bulk_load_images.py
poetry run python scripts/bulk_load_images.py --min-images 5 --max-images 10
```

## Troubleshooting

### Error: "No module named 'werkzeug'" o "No module named 'requests'"

**Solución**: Asegúrate de estar ejecutando los comandos dentro del entorno virtual de Poetry:

```bash
poetry run python scripts/nombre_script.py
```

O activa el shell de Poetry:

```bash
poetry shell
python scripts/nombre_script.py
```

### Error: "TemplateNotFound"

**Solución**: Verifica que los templates estén en la ubicación correcta según la estructura del proyecto. Los templates de reviews deben estar en `src/web/templates/features/reviews/`.

### Error: "AttributeError: 'HistoricSiteReview' object has no attribute 'user'"

**Solución**: Verifica que las relaciones estén correctamente definidas en los modelos. Ejecuta las migraciones si es necesario:

```bash
poetry run flask db upgrade
```

### Error: "sqlalchemy.exc.InvalidRequestError: One or more mappers failed to initialize"

**Solución**: Este error indica un conflicto en las relaciones de SQLAlchemy. Verifica que no haya backrefs duplicados en los modelos.

### MinIO no se conecta

**Soluciones**:
1. Verifica que MinIO esté ejecutándose en el puerto configurado (por defecto: 9000)
2. Verifica las credenciales en el archivo `.env`
3. Asegúrate de que el bucket esté creado (se crea automáticamente al subir la primera imagen)
4. Verifica que no haya un firewall bloqueando la conexión

### Error de codificación (emojis) en Windows

**Solución**: Los scripts ya están configurados para evitar emojis y usar texto simple compatible con Windows.

### La búsqueda no funciona correctamente

**Solución**: Verifica que el parámetro de búsqueda sea `user` (para buscar por email de usuario). La búsqueda busca solo al inicio del email, no contiene.

### Los ordenamientos no funcionan

**Solución**: 
1. Verifica que los selects de ordenamiento tengan los IDs correctos (`sort-by` y `sort-order`)
2. Verifica que el JavaScript esté capturando los valores correctamente
3. Revisa la consola del navegador para errores de JavaScript

## Flujo de Trabajo Recomendado

1. **Primera vez**:
   ```bash
   cd admin
   poetry install
   poetry run flask db upgrade
   poetry run flask reset-db --yes
   poetry run python scripts/load_historic_sites.py
   poetry run python scripts/bulk_load_images.py
   ```

2. **Desarrollo diario**:
   - Ejecutar las 3 terminales (admin, portal, minio)
   - Si modificas modelos: `poetry run flask db migrate -m "descripción"` y `poetry run flask db upgrade`

3. **Si necesitas resetear datos**:
   ```bash
   poetry run flask reset-db --yes
   poetry run python scripts/load_historic_sites.py
   poetry run python scripts/bulk_load_images.py
   ```

## Notas Importantes

- **Siempre usa `poetry run`** para ejecutar comandos Flask o scripts Python
- **Las migraciones son importantes**: Si modificas modelos, crea y aplica migraciones
- **MinIO debe estar ejecutándose** antes de subir imágenes
- **Las credenciales por defecto** deben cambiarse en producción
- **Los scripts de carga** son provisorios y usan datos de prueba

