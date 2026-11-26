
# SIRE – Sistema Inteligente de Registro de Enfermería

## Descripción del proyecto

SIRE es una aplicación web desarrollada para facilitar y automatizar el registro de las atenciones de enfermería del Instituto Tecnológico de Matehuala.

El sistema permite sustituir el registro manual en libretas por una plataforma digital, facilitando la consulta de información, el almacenamiento de registros y la generación automática de reportes mensuales.

## Objetivo

Optimizar el proceso de registro y control de las atenciones de enfermería mediante una plataforma web que permita reducir el trabajo administrativo, organizar la información y facilitar la elaboración de reportes.

## Funcionalidades

- Inicio de sesión para el personal de enfermería.
- Búsqueda de estudiantes mediante su número de control.
- Recuperación automática de los datos del estudiante.
- Registro de motivos de visita.
- Registro de signos vitales, procedimientos y observaciones.
- Consulta del historial de atenciones.
- Generación y descarga de reportes mensuales en formato Word.
- Cierre de sesión.
- Acceso a la plataforma desde internet.

## Tecnologías utilizadas

| Tecnología | Función |
|---|---|
| Python | Desarrollo de la lógica del sistema. |
| Flask | Framework para el desarrollo web. |
| HTML5 | Estructura de las interfaces. |
| CSS3 | Diseño y personalización visual. |
| Bootstrap | Diseño adaptable de la plataforma. |
| MySQL | Almacenamiento de información. |
| Flask-Login | Administración de sesiones. |
| Werkzeug | Generación y verificación de contraseñas mediante hash. |
| Python-docx | Generación de reportes en Word. |
| Gunicorn | Servidor de aplicaciones web. |
| Railway | Alojamiento de la aplicación y la base de datos. |
| GitHub | Almacenamiento del código fuente. |
| Visual Studio Code | Entorno de desarrollo. |

## Estructura del proyecto

    SIRE/
    ├── app.py
    ├── database.py
    ├── crear_enfermera.py
    ├── requirements.txt
    ├── .gitignore
    ├── .railwayignore
    ├── README.md
    ├── templates/
    │   ├── login.html
    │   ├── dashboard.html
    │   └── historial.html
    └── static/
        ├── css/
        │   └── estilos.css
        └── img/
            ├── educacion.png
            ├── tecnm.png
            ├── itmh.png
            └── cuidatec.png

## Descripción de los archivos

- **app.py:** archivo principal que contiene las rutas, funciones y lógica de funcionamiento de la aplicación.
- **database.py:** establece la conexión entre Python y la base de datos MySQL.
- **crear_enfermera.py:** permite registrar una cuenta de enfermería con una contraseña protegida mediante hash.
- **requirements.txt:** contiene las dependencias necesarias para ejecutar el sistema.
- **templates:** carpeta que contiene las interfaces HTML utilizadas por Flask.
- **static:** carpeta que almacena los recursos estáticos, como estilos CSS e imágenes.
- **.gitignore:** especifica los archivos que Git debe excluir del repositorio.
- **.railwayignore:** especifica los archivos que deben excluirse durante el despliegue en Railway.
- **README.md:** documentación general del proyecto.

## Base de datos

El sistema utiliza MySQL como gestor de base de datos relacional.

La base de datos está conformada por tres tablas principales:

- **estudiantes:** almacena la información de los estudiantes.
- **enfermeras:** almacena los datos de las cuentas del personal de enfermería.
- **atenciones:** almacena los registros de las consultas y procedimientos realizados.

Las tablas se relacionan mediante llaves primarias y foráneas para mantener la integridad de la información.

## Arquitectura del sistema

El proyecto utiliza una arquitectura cliente-servidor, organizada en tres capas:

- **Capa de presentación:** HTML, CSS y Bootstrap.
- **Capa de lógica de negocio:** Python y Flask.
- **Capa de datos:** MySQL.

Esta separación facilita el mantenimiento, la organización y la actualización del sistema.

## Seguridad

El sistema incorpora mecanismos básicos de seguridad:

- Autenticación de usuarios.
- Administración de sesiones.
- Almacenamiento de contraseñas mediante hash.
- Uso de variables de entorno para las credenciales.
- Exclusión de archivos confidenciales del repositorio.

## Despliegue

La aplicación y la base de datos se encuentran alojadas en Railway, lo que permite acceder al sistema desde diferentes dispositivos mediante una conexión a internet.

## Enlace de la plataforma

[SIRE – Sistema Inteligente de Registro de Enfermería](https://sire-web-production.up.railway.app)

## Estado del proyecto

Prototipo funcional publicado en internet.

Se realizaron pruebas de inicio de sesión, búsqueda de estudiantes, registro de atenciones, consulta del historial, generación de reportes y cierre de sesión.

## Aviso

Este proyecto fue desarrollado con fines académicos. Los datos de estudiantes, personal de enfermería y atenciones son ficticios.

