# Explor.ar 🗺️

Explor.ar es una plataforma web orientada a la gestión y descubrimiento de sitios históricos. El sistema está dividido en dos grandes módulos: una **aplicación pública** para que los usuarios descubran y exploren eventos y lugares, y una **aplicación privada** destinada a la administración del contenido.

Este proyecto fue desarrollado utilizando **Python y Flask**, con un fuerte enfoque en el manejo de datos geoespaciales, transacciones seguras en la base de datos y buenas prácticas de autenticación.

## 🚀 Características Principales

* **Arquitectura de Doble Aplicación:** Separación lógica y de acceso entre el portal público (exploración) y el panel privado (gestión de la información).
* **Autenticación Segura (OAuth 2.0):** Integración con la API de Google en la aplicación pública, permitiendo un inicio de sesión rápido y estandarizado.
* **Manejo de Datos Geoespaciales:** Uso avanzado de coordenadas (latitud y longitud) para el posicionamiento exacto de los sitios históricos.
* **Geocodificación Inversa:** Integración con la API de **OpenStreetMap** para resolver y autocompletar dinámicamente la Ciudad y Provincia correspondientes a partir de las coordenadas ingresadas.
* **Transacciones Atómicas:** Lógica de base de datos robusta para garantizar que la creación de un sitio histórico y sus eventos asociados se realicen de forma segura (si una falla, se revierte toda la operación).
* **Interfaz Escalable:** Implementación de paginación (bloques de 25 elementos) para garantizar tiempos de carga rápidos al listar grandes volúmenes de sitios.

## 🛠️ Stack Tecnológico

* **Backend:** Python, Flask
* **Base de Datos & ORM:** SQLAlchemy
* **Extensiones Geoespaciales:** GeoAlchemy2, Shapely
* **Autenticación:** Google OAuth 2.0
* **APIs Externas:** OpenStreetMap API

## 🔒 Notas de Seguridad

> **Aviso:** Como buena práctica de seguridad, las credenciales del entorno de desarrollo (como los `Client Secrets` de Google OAuth y las URIs de la base de datos) fueron revocadas y excluidas del historial público de este repositorio mediante `.gitignore`. El código está disponible a modo de demostración técnica y portfolio.
> 
