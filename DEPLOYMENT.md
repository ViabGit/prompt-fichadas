# 🚀 Deployment Guide - Sistema de Fichadas ZKTeco

## ✅ Sistema Desplegado Exitosamente

El sistema está completamente funcional y ejecutándose en Docker con los siguientes servicios:

### 🐳 Servicios Activos

| Servicio | Puerto | Estado | URL |
|----------|--------|--------|-----|
| **Frontend** | 4200 | ✅ Running | http://localhost:4200 |
| **Backend API** | 8080 | ✅ Running | http://localhost:8080 |
| **PostgreSQL** | 5432 | ✅ Healthy | localhost:5432 |

### 📋 Características Implementadas

✅ Backend FastAPI completamente funcional  
✅ Base de datos PostgreSQL configurada  
✅ Frontend web interactivo con estadísticas en tiempo real  
✅ API REST documentada (Swagger/OpenAPI)  
✅ Scheduler automático para recolección de fichadas  
✅ Sistema de notificaciones configurado  
✅ WebSocket para monitoreo en tiempo real  
✅ 17 dispositivos ZKTeco listos para migración  

---

## 🎯 Acceso Rápido

### 🌐 Interfaz Web
Abrir en el navegador: **http://localhost:4200**

La interfaz permite:
- Ver estadísticas del sistema en tiempo real
- Gestionar dispositivos ZKTeco  
- Probar conexiones de dispositivos
- Descargar fichadas manualmente
- Monitorear el estado del sistema

### 📚 Documentación API
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **Health Check**: http://localhost:8080/health

---

## 🛠️ Comandos de Gestión

### Iniciar el Sistema
```powershell
cd "d:\Repos\ficheros\proyecto-fichadas"
docker-compose up -d
```

### Detener el Sistema
```powershell
docker-compose down
```

### Ver Logs
```powershell
# Todos los servicios
docker-compose logs -f

# Solo backend
docker logs -f fichadas-backend

# Solo base de datos
docker logs -f fichadas-db

# Solo frontend
docker logs -f fichadas-frontend
```

### Reiniciar un Servicio
```powershell
docker-compose restart backend
docker-compose restart frontend
docker-compose restart db
```

### Reconstruir Servicios
```powershell
# Reconstruir todo
docker-compose up -d --build

# Reconstruir solo backend
docker-compose build --no-cache backend
docker-compose up -d backend
```

---

## 📊 Migración de Dispositivos

El sistema incluye un script para migrar los 17 dispositivos existentes desde `TACollector.config.json`:

```powershell
# Ejecutar dentro del contenedor backend
docker exec -it fichadas-backend python migration_script.py
```

Los dispositivos disponibles para migración:
- 11 relojes de producción
- 4 relojes de administración  
- 2 relojes de ingreso/recepción

---

## 🔧 Configuración

### Variables de Entorno (backend/.env)

```env
# Base de Datos
DATABASE_URL=postgresql://fichadas_user:fichadas_pass@db:5432/fichadas_db

# Directorios
CARPETA_SALIDA=/data/fichadas
CARPETA_BACKUP=/data/backup

# Scheduler
FRECUENCIA_MINUTOS=5
INICIO_AUTOMATICO=true
MAX_REINTENTOS=3

# Notificaciones
NOTIFICATION_TYPE=none  # opciones: smtp, sendgrid, none
```

### Cambiar Frecuencia de Recolección

Editar `docker-compose.yml`:
```yaml
environment:
  - FRECUENCIA_MINUTOS=10  # Cambiar a minutos deseados
```

Luego reiniciar:
```powershell
docker-compose restart backend
```

---

## 🔗 Endpoints API Principales

### Dispositivos
- `GET /api/dispositivos` - Listar todos los dispositivos
- `POST /api/dispositivos` - Crear nuevo dispositivo
- `GET /api/dispositivos/{id}` - Obtener dispositivo específico
- `PUT /api/dispositivos/{id}` - Actualizar dispositivo
- `DELETE /api/dispositivos/{id}` - Eliminar dispositivo
- `POST /api/dispositivos/{id}/test-conexion` - Probar conexión
- `POST /api/dispositivos/{id}/descargar-fichadas` - Descarga manual

### Monitoreo
- `GET /api/monitoreo/estadisticas` - Estadísticas del sistema
- `GET /api/monitoreo/logs` - Logs del sistema
- `GET /api/monitoreo/dispositivos-offline` - Dispositivos sin conexión

### Configuración
- `GET /api/configuracion` - Obtener configuración global
- `PUT /api/configuracion` - Actualizar configuración

### Fichadas
- `GET /api/fichadas` - Listar fichadas con filtros
- `GET /api/fichadas/{id}` - Obtener fichada específica
- `GET /api/fichadas/export` - Exportar fichadas (CSV/JSON)

---

## 🐛 Troubleshooting

### El backend no inicia
```powershell
# Ver logs para identificar el error
docker logs fichadas-backend

# Verificar conexión a la base de datos
docker exec -it fichadas-db psql -U fichadas_user -d fichadas_db
```

### Puerto en uso
Si el puerto 8080 o 4200 están en uso, editar `docker-compose.yml`:
```yaml
ports:
  - "8081:8000"  # Cambiar puerto externo
```

### Resetear base de datos
```powershell
docker-compose down -v  # Elimina volúmenes
docker-compose up -d    # Recrea todo
```

### Dispositivos no conectan
1. Verificar que los dispositivos estén en la misma red
2. Verificar IP y puerto en la configuración del dispositivo
3. Usar el botón "Test Conexión" en la interfaz web
4. Revisar logs del backend para detalles del error

---

## 📁 Estructura de Archivos Generados

```
data/
├── fichadas/           # Fichadas descargadas en CSV
│   ├── dispositivo_001_YYYYMMDD_HHMMSS.csv
│   └── ...
└── backup/             # Respaldos automáticos
    ├── fichadas_YYYYMMDD.zip
    └── ...
```

---

## 🔒 Seguridad

### Cambiar Credenciales de Base de Datos

Editar `docker-compose.yml`:
```yaml
environment:
  - POSTGRES_USER=nuevo_usuario
  - POSTGRES_PASSWORD=nueva_password_segura
  - POSTGRES_DB=fichadas_db
```

Y actualizar `backend/.env`:
```env
DATABASE_URL=postgresql://nuevo_usuario:nueva_password_segura@db:5432/fichadas_db
```

---

## 🚀 Producción

### Consideraciones para Producción

1. **Usar HTTPS**: Configurar reverse proxy (Nginx/Traefik) con SSL
2. **Credenciales seguras**: Cambiar todas las passwords por defecto
3. **Backups**: Configurar backups automáticos de PostgreSQL
4. **Monitoreo**: Configurar alertas y monitoreo externo
5. **Logs**: Configurar rotación de logs
6. **Firewall**: Restringir acceso solo a IPs autorizadas

### Ejemplo con Nginx como Reverse Proxy

```nginx
server {
    listen 80;
    server_name fichadas.tudominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name fichadas.tudominio.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:4200;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📞 Soporte

Para reportar problemas o solicitar nuevas funcionalidades:
1. Revisar los logs: `docker-compose logs`
2. Verificar el estado: `docker ps`
3. Consultar la documentación API: http://localhost:8080/docs

---

## 📝 Notas

- El sistema usa **pyzk2** para comunicación con dispositivos ZKTeco
- La frecuencia por defecto de recolección es cada 5 minutos
- Los fichadas se guardan en formato CSV en `/data/fichadas`
- El scheduler se puede habilitar/deshabilitar desde la API
- Las notificaciones por email requieren configurar SMTP o SendGrid

---

**✨ Sistema completamente funcional y listo para usar ✨**