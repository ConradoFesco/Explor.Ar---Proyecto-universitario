## Especificaciones de las APIs a corregir (las que no aparecen en el listado es porque ya están bien implementadas).
Aclaración: es necesario que tengan todos esos parámetros como mínimo y se respeten los nombres de los mismos, pero a su vez pueden agregarse parámetros de ser necesario (aclarar en el docstring)

---------------------------------------------------------
GET/sites{?name,description,city,province,tags,order_by,lat,long,radius,page,per_page}
Obtiene una lista de sitios históricos que coinciden con los criterios de búsqueda.

Información del endpoint
- No requiere autenticación.

Example URL
GET https://admin-grupoXX.proyecto2025.linti.unlp.edu.ar/api/sites?name=fortín&description=siglo&city=Córdoba&province=Córdoba&tags=militar,siglo-xix&order_by=latest&lat=-31.4201&long=-64.1888&radius=50&page=1&per_page=20

URL Parameters
name
string (optional) Example: fortín
Filtra por nombre (búsqueda parcial, case-insensitive).

description
string (optional) Example: siglo
Filtra por descripción (búsqueda parcial, case-insensitive).

city
string (optional) Example: Córdoba
Filtra por ciudad (búsqueda exacta, case-insensitive).

province
string (optional) Example: Córdoba
Filtra por provincia (búsqueda exacta, case-insensitive).

tags
string (optional) Example: militar,siglo-xix
Filtra por etiquetas (múltiples separadas por comas).

order_by
string (optional) Example: latest
Ordena los resultados.

Choices: rating-5-1 rating-1-5 latest oldest

lat
number (optional) Example: -31.4201
Latitud para búsqueda geoespacial.

long
number (optional) Example: -64.1888
Longitud para búsqueda geoespacial.

radius
number (optional) Example: 50
Radio en kilómetros para la búsqueda geoespacial. Requiere lat y long.

page
number (optional) Example: 1
Número de página (mínimo 1).

per_page
number (optional) Example: 20
Cantidad de elementos por página (1 a 100).

Response  200
Headers
Content-Type: application/json
Body
{
  "data": [
    {
      "id": 1,
      "name": "Fortín San Martín",
      "short_description": "Antiguo fortín militar...",
      "description": "Construcción del siglo XIX...",
      "city": "Córdoba",
      "province": "Córdoba",
      "country": "AR",
      "lat": -31.4201,
      "long": -64.1888,
      "tags": [
        "militar",
        "siglo-xix"
      ],
      "state_of_conservation": "excelente",
      "inserted_at": "2024-03-15T14:30:00Z",
      "updated_at": "2024-06-20T09:15:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 57
  }
}
Schema
{
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "data": {
      "type": "array",
      "description": "Lista de sitios históricos."
    },
    "meta": {
      "type": "object",
      "properties": {
        "page": {
          "type": "number",
          "description": "Número de página actual."
        },
        "per_page": {
          "type": "number",
          "description": "Cantidad de elementos por página."
        },
        "total": {
          "type": "number",
          "description": "Total de elementos en la lista."
        }
      },
      "description": "Información de paginación."
    }
  }
}
Response  400
Headers
Content-Type: application/json
Body
{
  "error": {
    "code": "invalid_query",
    "message": "Parameter validation failed",
    "details": {
      "lat": [
        "Must be a valid latitude"
      ],
      "long": [
        "Must be a valid longitude"
      ],
      "per_page": [
        "Must be between 1 and 100"
      ]
    }
  }
}
Response  500
Headers
Content-Type: application/json
Body
{
  "error": {
    "code": "server_error",
    "message": "An unexpected error occurred"
  }
}
-------------------------------------------------------------------

GET/sites/{site_id}
Obtiene detalles de un sitio histórico específico por su ID.

Información del endpoint
- No requiere autenticación.

Example URL
GET https://admin-grupoXX.proyecto2025.linti.unlp.edu.ar/api/sites/10
URL Parameters
site_id
number (required) Example: 10
ID del sitio histórico.
Response  200
Headers
Content-Type: application/json
Body
{
  "id": 1,
  "name": "Fortín San Martín",
  "short_description": "Antiguo fortín militar...",
  "description": "Construcción del siglo XIX...",
  "city": "Córdoba",
  "province": "Córdoba",
  "country": "AR",
  "lat": -31.4201,
  "long": -64.1888,
  "tags": [
    "militar",
    "siglo-xix"
  ],
  "state_of_conservation": "excelente",
  "inserted_at": "2024-03-15T14:30:00Z",
  "updated_at": "2024-06-20T09:15:00Z"
}
Schema
{
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "id": {
      "type": "number",
      "description": "Identificador único del sitio histórico."
    },
    "name": {
      "type": "string",
      "description": "Nombre del sitio histórico."
    },
    "short_description": {
      "type": "string",
      "description": "Descripción corta del sitio histórico."
    },
    "description": {
      "type": "string",
      "description": "Descripción del sitio histórico."
    },
    "city": {
      "type": "string",
      "description": "Ciudad donde se encuentra el sitio histórico."
    },
    "province": {
      "type": "string",
      "description": "Provincia donde se encuentra el sitio histórico."
    },
    "country": {
      "type": "string",
      "description": "Código ISO del país donde se encuentra el sitio histórico."
    },
    "lat": {
      "type": "number",
      "description": "Latitud."
    },
    "long": {
      "type": "number",
      "description": "Longitud."
    },
    "tags": {
      "type": "array",
      "description": "Etiquetas asociadas al sitio histórico."
    },
    "state_of_conservation": {
      "type": "string",
      "enum": [
        "excelente",
        "bueno",
        "regular",
        "malo"
      ],
      "description": "Estado de conservación del sitio histórico."
    },
    "inserted_at": {
      "type": "string",
      "description": "Fecha de creación del registro."
    },
    "updated_at": {
      "type": "string",
      "description": "Fecha de última actualización del registro."
    }
  },
  "required": [
    "name",
    "short_description",
    "description",
    "city",
    "province",
    "country",
    "lat",
    "long",
    "tags",
    "state_of_conservation",
    "inserted_at",
    "updated_at"
  ]
}
Response  404
Headers
Content-Type: application/json
Body
{
  "error": {
    "code": "not_found",
    "message": "Site not found"
  }
}
Response  500
Headers
Content-Type: application/json
Body
{
  "error": {
    "code": "server_error",
    "message": "An unexpected error occurred"
  }
}
--------------------------------------------------------------------

GET/sites/{site_id}/reviews{?page,per_page}
Obtiene una lista paginada de reseñas para un sitio histórico específico.

Información del endpoint
- Requiere autenticación.

Example URL
GET https://admin-grupoXX.proyecto2025.linti.unlp.edu.ar/api/sites/10/reviews?page=1&per_page=10
URL Parameters
site_id
number (required) Example: 10
ID del sitio histórico.

page
number (optional) Example: 1
Número de página (mínimo 1).

per_page
number (optional) Example: 10
Cantidad de elementos por página (1 a 100).

Headers
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9

Response  200
Headers
Content-Type: application/json
Body
{
  "data": [
    {
      "id": 1,
      "site_id": 1,
      "rating": 5,
      "comment": "Imperdible",
      "inserted_at": "2025-01-05T10:20:00Z",
      "updated_at": "2025-06-12T08:00:00Z"
    },
    {
      "id": 2,
      "site_id": 101,
      "rating": 5,
      "comment": "Excelente",
      "inserted_at": "2025-01-05T10:20:00Z",
      "updated_at": "2025-06-12T08:00:00Z"
    },
    {
      "id": 3,
      "site_id": 101,
      "rating": 4,
      "comment": "Muy bueno, pero falta señalización",
      "inserted_at": "2025-01-05T10:20:00Z",
      "updated_at": "2025-06-12T08:00:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "per_page": 10,
    "total": 35
  }
}
Schema
{
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "data": {
      "type": "array",
      "description": "Lista de reseñas."
    },
    "meta": {
      "type": "object",
      "properties": {
        "page": {
          "type": "number",
          "description": "Número de página actual."
        },
        "per_page": {
          "type": "number",
          "description": "Cantidad de elementos por página."
        },
        "total": {
          "type": "number",
          "description": "Total de reseñas."
        }
      },
      "description": "Información de paginación."
    }
  }
}
Response  400
Headers
Content-Type: application/json
Body
{ "error": { "code": "invalid_data", "message": "Invalid input data", "details": { "per_page": ["Must be between 1 and 100"] } } }
Response  401
Headers
Content-Type: application/json
Body
{
  "error": {
    "code": "unauthorized",
    "message": "Authentication required"
  }
}
Response  404
Headers
Content-Type: application/json
Body
{
  "error": {
    "code": "not_found",
    "message": "Site not found"
  }
}
Response  500
Headers
Content-Type: application/json
Body
{
  "error": {
    "code": "server_error",
    "message": "An unexpected error occurred"
  }
}
---------------------------------------------------------------------

POST/sites/{site_id}/reviews
Crea una nueva reseña para un sitio histórico específico.

Información del endpoint

 Requiere autenticación.

Example URL
POST https://admin-grupoXX.proyecto2025.linti.unlp.edu.ar/api/sites/101/reviews
URL Parameters
site_id
number (required) Example: 101
ID del sitio histórico.
Request
Headers
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
Body
{
  "rating": 4,
  "site_id": 101,
  "comment": "Faltan carteles explicativos en el interior."
}
Schema
{
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "rating": {
      "type": "number",
      "description": "Calificación otorgada (1 a 5)."
    },
    "site_id": {
      "type": "number",
      "description": "ID del sitio histórico."
    },
    "comment": {
      "type": "string",
      "description": "Comentario adicional."
    }
  },
  "required": [
    "rating",
    "site_id"
  ]
}
Response  201
Headers
Content-Type: application/json
Body
{
  "id": 5,
  "site_id": 101,
  "rating": 4,
  "comment": "Faltan carteles explicativos en el interior.",
  "inserted_at": "2025-01-05T10:20:00Z",
  "updated_at": "2025-06-12T08:00:00Z"
}
Schema
{
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "id": {
      "type": "number",
      "description": "Identificador único de la reseña."
    },
    "site_id": {
      "type": "number",
      "description": "ID del sitio histórico."
    },
    "rating": {
      "type": "number",
      "description": "Calificación otorgada."
    },
    "comment": {
      "type": "string",
      "description": "Comentario adicional."
    },
    "inserted_at": {
      "type": "string",
      "description": "Fecha de creación de la reseña."
    },
    "updated_at": {
      "type": "string",
      "description": "Fecha de última actualización de la reseña."
    }
  },
  "required": [
    "id",
    "site_id",
    "rating",
    "inserted_at",
    "updated_at"
  ]
}
Response  400
Headers
Content-Type: application/json
Body
{
  "error": {
    "code": "invalid_data",
    "message": "Invalid input data",
    "details": {
      "rating": [
        "Must be between 1 and 5"
      ]
    }
  }
}
Response  401
Headers
Content-Type: application/json
Body
{
  "error": {
    "code": "unauthorized",
    "message": "Authentication required"
  }
}
Response  404
Headers
Content-Type: application/json
Body
{
  "error": {
    "code": "not_found",
    "message": "Site not found"
  }
}
Response  500
Headers
Content-Type: application/json
Body
{
  "error": {
    "code": "server_error",
    "message": "An unexpected error occurred"
  }
}
--------------------------------------------------------

GET/sites/{site_id}/reviews/{review_id}
Obtiene una reseña existente por su ID.

Información del endpoint

 Requiere autenticación.

Example URL
GET https://admin-grupoXX.proyecto2025.linti.unlp.edu.ar/api/sites/10/reviews/5
URL Parameters
site_id
number (required) Example: 10
ID del sitio histórico.

review_id
number (required) Example: 5
ID de la reseña a obtener.

Request
Headers
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9

Response  200
Headers
Content-Type: application/json
Body
{
  "id": 1,
  "site_id": 1,
  "rating": 1,
  "comment": "Imperdible",
  "inserted_at": "2025-01-05T10:20:00Z",
  "updated_at": "2025-06-12T08:00:00Z"
}
Schema
{
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "id": {
      "type": "number",
      "description": "Identificador único de la reseña."
    },
    "site_id": {
      "type": "number",
      "description": "Identificador del sitio histórico asociado."
    },
    "rating": {
      "type": "number",
      "enum": [
        1,
        2,
        3,
        4,
        5
      ],
      "description": "Calificación otorgada."
    },
    "comment": {
      "type": "string",
      "description": "Título de la reseña."
    },
    "inserted_at": {
      "type": "string",
      "description": "Fecha de creación de la reseña."
    },
    "updated_at": {
      "type": "string",
      "description": "Fecha de última actualización de la reseña."
    }
  },
  "required": [
    "id",
    "site_id",
    "rating",
    "comment",
    "inserted_at",
    "updated_at"
  ]
}
Response  400
Headers
Content-Type: application/json
Body
{
  "error": {
    "code": "invalid_data",
    "message": "Invalid input data",
    "details": {
      "review_id": [
        "Must be a positive integer"
      ]
    }
  }
}
Response  401
Headers
Content-Type: application/json
Body
{
  "error": {
    "code": "unauthorized",
    "message": "Authentication required"
  }
}
Response  403
Headers
Content-Type: application/json
Body
{
  "error": {
    "code": "forbidden",
    "message": "You do not have permission to access this review"
  }
}
Response  404
Headers
Content-Type: application/json
Body
{
  "error": {
    "code": "not_found",
    "message": "Site not found"
  }
}
Response  500
Headers
Content-Type: application/json
Body
{
  "error": {
    "code": "server_error",
    "message": "An unexpected error occurred"
  }
}
----------------------------------------------------------------

GET/me/favorites{?page,per_page}
Example URL
GET https://admin-grupoXX.proyecto2025.linti.unlp.edu.ar/api/me/favorites?page=1&per_page=20
URL Parameters
page
number (optional) Example: 1
Mínimo 1.

per_page
number (optional) Example: 20
1…100.

Request
Headers
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9

Response  200
Headers
Content-Type: application/json
Body
{
  "data": [
    {
      "id": 1,
      "name": "Fortín San Martín",
      "short_description": "Antiguo fortín militar...",
      "description": "Construcción del siglo XIX...",
      "city": "Córdoba",
      "province": "Córdoba",
      "country": "AR",
      "lat": -31.4201,
      "long": -64.1888,
      "tags": [
        "militar",
        "siglo-xix"
      ],
      "state_of_conservation": "excelente",
      "inserted_at": "2024-03-15T14:30:00Z",
      "updated_at": "2024-06-20T09:15:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 5
  }
}
Schema
{
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "data": {
      "type": "array",
      "description": "Sitios favoritos (sugerencia: incluir `inserted_at` de la relación)."
    },
    "meta": {
      "type": "object",
      "properties": {
        "page": {
          "type": "number"
        },
        "per_page": {
          "type": "number"
        },
        "total": {
          "type": "number"
        }
      }
    }
  }
}
Response  401
Headers
Content-Type: application/json
Body
{
  "error": {
    "code": "unauthorized",
    "message": "Authentication required"
  }
}
Response  500
Headers
Content-Type: application/json
Body
{
  "error": {
    "code": "server_error",
    "message": "An unexpected error occurred"
  }
}