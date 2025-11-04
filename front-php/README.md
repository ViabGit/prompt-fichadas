# Frontend PHP - Sistema de Fichadas ZKTeco

Frontend simple en PHP puro para el sistema de fichadas ZKTeco.

## Características

- ✅ PHP 8.2 con Apache
- ✅ Sin dependencias externas
- ✅ Diseño responsive
- ✅ Integración con API FastAPI
- ✅ Auto-refresh cada 30 segundos
- ✅ Interfaz moderna con gradientes

## Estructura

```
front-php/
├── Dockerfile          # Imagen PHP 8.2 + Apache
├── index.php          # Página principal
├── .htaccess          # Configuración Apache
└── README.md          # Este archivo
```

## Uso

### Con Docker Compose

```bash
# Iniciar todos los servicios
docker-compose up -d

# Solo el frontend PHP
docker-compose up -d frontend-php
```

### Acceso

- Frontend: http://localhost:4300
- Backend API: http://localhost:8081
- Documentación API: http://localhost:8081/docs

## Funcionalidades

### Dashboard Principal
- Estadísticas en tiempo real
- Dispositivos activos
- Total de registros
- Registros del día
- Último procesamiento

### Acciones Rápidas
- Procesar fichadas manualmente
- Iniciar/Detener scheduler automático
- Actualizar datos

### Listado de Dispositivos
- Ver todos los dispositivos configurados
- Estado (Activo/Inactivo)
- IP, Puerto, Ubicación
- ID del dispositivo

## Tecnologías

- **PHP 8.2**: Lenguaje backend
- **Apache 2.4**: Servidor web
- **JavaScript Vanilla**: Consumo de API
- **CSS3**: Estilos modernos con gradientes

## Desarrollo

El frontend es un archivo PHP simple que renderiza HTML estático y usa JavaScript para consumir la API REST del backend FastAPI.

No requiere compilación ni build, solo ejecutar el contenedor.

## Configuración API

El frontend se conecta al backend en `http://localhost:8081/api`. Si necesitas cambiar esto, edita la constante `API_BASE` en el archivo `index.php`:

```javascript
const API_BASE = 'http://tu-backend:puerto/api';
```

## Docker

El `Dockerfile` usa la imagen oficial `php:8.2-apache` y configura:

- Extensiones PDO (por si se necesitan en el futuro)
- mod_rewrite habilitado
- Permisos correctos para Apache
- Puerto 80 expuesto

## Notas

- Auto-refresh cada 30 segundos para actualizar estadísticas
- Diseño responsive para móviles y tablets
- Colores corporativos con gradiente púrpura-azul
- Manejo de errores con mensajes amigables
