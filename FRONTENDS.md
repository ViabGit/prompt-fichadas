# Guía de Frontends - Sistema de Fichadas ZKTeco

Este proyecto incluye **dos opciones de frontend** que puedes usar según tus preferencias:

## 🎨 Opciones Disponibles

### 1. Frontend PHP (Recomendado) ⭐
- **Ruta**: `front-php/`
- **Puerto**: http://localhost:4300
- **Tecnología**: PHP 8.2 + Apache
- **Características**:
  - ✅ Sin compilación necesaria
  - ✅ Listo para usar
  - ✅ Auto-refresh cada 30 segundos
  - ✅ Diseño moderno con gradientes
  - ✅ Totalmente funcional
  - ✅ PHP puro (sin frameworks)

### 2. Frontend Angular (Desarrollo)
- **Ruta**: `frontend/`
- **Puerto**: http://localhost:4200
- **Tecnología**: Angular + Nginx
- **Estado**: En desarrollo
- **Nota**: Requiere compilación y configuración adicional

---

## 🚀 Inicio Rápido

### Opción A: Usar Frontend PHP (Más Simple)

```bash
# Iniciar todos los servicios con el frontend PHP
docker-compose up -d

# O solo el stack completo
docker-compose up -d db backend frontend-php
```

**Acceder**: http://localhost:4300

### Opción B: Usar Frontend Angular

```bash
# Iniciar con el frontend Angular
docker-compose --profile angular up -d

# O específicamente
docker-compose up -d db backend frontend
```

**Acceder**: http://localhost:4200

---

## 📦 Gestión de Servicios

### Ver servicios activos
```bash
docker-compose ps
```

### Detener todos los servicios
```bash
docker-compose down
```

### Detener solo un frontend
```bash
# Detener PHP
docker-compose stop frontend-php

# Detener Angular
docker-compose stop frontend
```

### Ver logs
```bash
# Logs del frontend PHP
docker-compose logs -f frontend-php

# Logs del frontend Angular
docker-compose logs -f frontend

# Logs del backend
docker-compose logs -f backend
```

### Reiniciar un servicio
```bash
# Reiniciar PHP
docker-compose restart frontend-php

# Reiniciar Angular
docker-compose restart frontend
```

---

## 🔧 Configuración

### Frontend PHP

**Archivo principal**: `front-php/index.php`

Para cambiar la URL del backend, edita la constante en el JavaScript:
```javascript
const API_BASE = 'http://localhost:8081/api';
```

**Dockerfile**: `front-php/Dockerfile`
- Imagen base: `php:8.2-apache`
- Puerto expuesto: 80 (mapeado a 4300)
- Sin dependencias externas

### Frontend Angular

**Configuración**: `frontend/nginx.conf`
- Proxy inverso a `/api/*`
- Headers de seguridad CSP
- Puerto expuesto: 80 (mapeado a 4200)

---

## 🎯 Características de los Frontends

### Dashboard Principal (Ambos)
- 📊 Estadísticas en tiempo real
  - Dispositivos activos
  - Total de registros
  - Registros del día
  - Último procesamiento
  
### Acciones Rápidas (Ambos)
- ▶️ Procesar fichadas manualmente
- ⏰ Iniciar scheduler automático
- ⏸️ Detener scheduler
- 🔄 Actualizar datos

### Gestión de Dispositivos (Ambos)
- 📱 Listado completo de dispositivos
- ✅ Estado (Activo/Inactivo)
- 🔍 Detalles: IP, Puerto, Ubicación, ID

---

## 🌐 URLs del Sistema

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Frontend PHP** | http://localhost:4300 | Interfaz principal (PHP) |
| **Frontend Angular** | http://localhost:4200 | Interfaz principal (Angular) |
| **Backend API** | http://localhost:8081 | API REST |
| **API Docs** | http://localhost:8081/docs | Documentación interactiva |
| **Health Check** | http://localhost:8081/health | Estado del backend |
| **PostgreSQL** | localhost:5432 | Base de datos |

---

## 🛠️ Desarrollo

### Frontend PHP

```bash
# Editar archivos
cd front-php
# Modificar index.php

# Reconstruir y reiniciar
docker-compose build frontend-php
docker-compose up -d frontend-php
```

Los cambios se reflejan automáticamente (no requiere rebuild si solo editas PHP).

### Frontend Angular

```bash
# Entrar al contenedor de desarrollo
docker-compose --profile dev up frontend-dev

# O trabajar localmente
cd frontend
npm install
ng serve
```

---

## 🔒 Perfiles de Docker Compose

El archivo `docker-compose.yml` usa perfiles para controlar qué servicios se inician:

```yaml
# Sin perfil (por defecto): Inicia frontend-php
docker-compose up -d

# Perfil 'angular': Inicia frontend angular
docker-compose --profile angular up -d

# Perfil 'dev': Modo desarrollo Angular
docker-compose --profile dev up -d

# Perfil 'redis': Con Redis para Celery
docker-compose --profile redis up -d
```

---

## 📊 Comparación

| Característica | Frontend PHP | Frontend Angular |
|---------------|--------------|------------------|
| **Complejidad** | Baja ⭐ | Alta |
| **Tiempo de inicio** | Instantáneo | Requiere build |
| **Tamaño imagen** | ~200 MB | ~50 MB (nginx) |
| **Tecnología** | PHP + Apache | TypeScript + Angular |
| **Mantenimiento** | Simple | Complejo |
| **Funcionalidad** | Completa ✅ | En desarrollo 🔄 |
| **Recomendado para** | Producción | Desarrollo avanzado |

---

## ❓ Troubleshooting

### Frontend PHP no carga

```bash
# Verificar que el contenedor esté corriendo
docker-compose ps frontend-php

# Ver logs
docker-compose logs frontend-php

# Reiniciar
docker-compose restart frontend-php
```

### Error de conexión con el backend

```bash
# Verificar que el backend esté corriendo
docker-compose ps backend

# Ver logs del backend
docker-compose logs backend

# Probar health check
curl http://localhost:8081/health
```

### Puerto ya en uso

```bash
# Cambiar el puerto en docker-compose.yml
# Buscar "4300:80" y cambiar 4300 por otro puerto
# Por ejemplo: "4500:80"

# Luego reiniciar
docker-compose down
docker-compose up -d
```

---

## 🎨 Personalización

### Cambiar colores del Frontend PHP

Edita `front-php/index.php` en la sección `<style>`:

```css
/* Buscar estas líneas */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Cambiar por tus colores preferidos */
background: linear-gradient(135deg, #tu-color-1 0%, #tu-color-2 100%);
```

### Modificar frecuencia de auto-refresh

En `front-php/index.php`, busca:

```javascript
// Auto-refresh cada 30 segundos
setInterval(cargarDatos, 30000);

// Cambiar 30000 (30 segundos) por el valor deseado en milisegundos
// Ejemplo: 60000 = 1 minuto
```

---

## 📝 Notas Importantes

1. **Frontend PHP** es el recomendado para uso en producción debido a su simplicidad y estabilidad.

2. El **frontend Angular** está disponible para desarrollo avanzado y futuras expansiones.

3. Ambos frontends consumen la misma **API REST** del backend, por lo que tienen las mismas funcionalidades.

4. Puedes tener **ambos frontends corriendo simultáneamente** en diferentes puertos.

5. El auto-refresh está habilitado por defecto en el frontend PHP para mantener los datos actualizados.

---

## 🤝 Contribuir

Si deseas mejorar alguno de los frontends:

1. Haz tus cambios en `front-php/` o `frontend/`
2. Prueba localmente con Docker
3. Actualiza esta documentación si es necesario
4. Crea un commit con tus cambios

---

## 📄 Licencia

Este proyecto es parte del Sistema de Fichadas ZKTeco v1.0.0

---

**¿Dudas?** Consulta la [documentación de la API](http://localhost:8081/docs) o los logs con `docker-compose logs`.
