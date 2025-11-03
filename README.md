# Sistema de Fichadas ZKTeco

Sistema completo para la recolección automática de fichadas desde dispositivos biométricos ZKTeco, con interfaz web moderna y arquitectura backend/frontend separada.

## 🚀 Características

- **Backend FastAPI**: API REST completa con documentación automática
- **Frontend Angular 17**: Interfaz moderna con Angular Material
- **Base de datos PostgreSQL**: Para configuración y logs del sistema
- **Scheduler automático**: Recolección programada cada X minutos
- **WebSocket en tiempo real**: Monitoreo del estado de dispositivos
- **Sistema de notificaciones**: SMTP y SendGrid para alertas
- **Docker Ready**: Contenedores para fácil despliegue
- **Migración automática**: Desde configuración TACollector existente

## 📁 Estructura del Proyecto

```
proyecto-fichadas/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── api/            # Endpoints REST
│   │   ├── models/         # Modelos SQLAlchemy
│   │   ├── schemas/        # Schemas Pydantic
│   │   ├── services/       # Lógica de negocio
│   │   └── utils/          # Utilidades
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # App Angular
│   ├── src/app/
│   │   ├── modules/        # Módulos por funcionalidad
│   │   ├── services/       # Servicios Angular
│   │   └── shared/         # Componentes compartidos
│   └── package.json
├── data/                   # Datos persistentes
│   ├── fichadas/          # Archivos .txt generados
│   └── backup/            # Backups automáticos
├── docker-compose.yml      # Configuración Docker
└── migrar_config.py       # Script de migración
```

## 🏃 Inicio Rápido

### Opción 1: Docker (Recomendado)

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd proyecto-fichadas
```

2. **Configurar variables de entorno**
```bash
cp backend/.env.example backend/.env
# Editar backend/.env con tus configuraciones
```

3. **Levantar servicios**
```bash
# Desarrollo (con hot reload)
docker-compose --profile dev up --build

# Producción
docker-compose --profile prod up --build -d
```

4. **Migrar configuración existente** (opcional)
```bash
python migrar_config.py
```

### Opción 2: Desarrollo Local

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
ng serve
```

**Base de datos:**
```bash
# Instalar PostgreSQL y crear base de datos
createdb fichadas_db
```

## 🔧 Configuración

### Variables de Entorno (.env)

```env
# Base de datos
DATABASE_URL=postgresql://fichadas_user:fichadas_pass@localhost:5432/fichadas_db

# Configuración de archivos
CARPETA_SALIDA=/data/fichadas
CARPETA_BACKUP=/data/backup

# Scheduler
FRECUENCIA_MINUTOS=5
INICIO_AUTOMATICO=true
MAX_REINTENTOS=3

# Notificaciones SMTP (opcional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=tu-password
NOTIFICATION_TYPE=smtp
```

### Configuración de Dispositivos

Los dispositivos se configuran a través de la API REST o interfaz web:

```json
{
  "id": "1",
  "nombre": "Dispositivo Principal",
  "ip": "192.168.1.100",
  "puerto": 4370,
  "modelo": "SF300",
  "marca": "ZK",
  "activo": true,
  "numero_dispositivo": "60033"
}
```

## 📊 Funcionalidades

### Backend (FastAPI)

- **`GET /api/dispositivos`** - Listar dispositivos
- **`POST /api/dispositivos`** - Crear dispositivo
- **`PUT /api/dispositivos/{id}`** - Actualizar dispositivo
- **`DELETE /api/dispositivos/{id}`** - Eliminar dispositivo
- **`POST /api/dispositivos/{id}/test-conexion`** - Probar conexión
- **`POST /api/dispositivos/{id}/descargar-fichadas`** - Descarga manual
- **`GET /api/configuracion`** - Configuración global
- **`PUT /api/configuracion`** - Actualizar configuración
- **`GET /api/monitoreo/logs`** - Logs del sistema
- **`GET /api/monitoreo/estadisticas`** - Dashboard estadísticas
- **`WebSocket /api/monitoreo/monitor`** - Monitoreo tiempo real

### Frontend (Angular)

- **Dashboard**: Vista general con estadísticas
- **Dispositivos**: CRUD completo con tabla y formularios
- **Monitoreo**: Estado en tiempo real de dispositivos
- **Configuración**: Ajustes globales y notificaciones
- **Logs**: Visor de logs con filtros
- **Reportes**: Gráficos y estadísticas

### Recolección Automática

El sistema ejecuta automáticamente cada X minutos:

1. Conecta a cada dispositivo activo
2. Descarga solo fichadas nuevas (desde última consulta)
3. Genera archivo `{numero_dispositivo}.txt`
4. Crea backup con timestamp
5. Actualiza estado en base de datos
6. Envía alertas si hay errores

## 📄 Formato de Fichadas

Los archivos generados siguen el formato:
```
ID_Usuario DD/MM/YYYY HH:MM Numero_Dispositivo Codigo_Adicional
Ejemplo: 96532 25/09/2024 09:53 33 00
```

## 🔍 Monitoreo y Logs

- **Logs en tiempo real**: WebSocket para actualizaciones instantáneas
- **Estados de dispositivos**: Online, Offline, Error
- **Alertas automáticas**: Email cuando dispositivo no responde
- **Dashboard estadístico**: Fichadas por día, errores, uptime
- **Exportación de logs**: Descarga en CSV

## 🚨 Sistema de Alertas

- **Fallo de dispositivo**: Email cuando falla 3 veces consecutivas
- **Recuperación**: Notificación cuando dispositivo vuelve online
- **Resumen diario**: Estado general del sistema
- **Configuración flexible**: SMTP o SendGrid

## 🐳 Docker

### Servicios incluidos:

- **backend**: FastAPI con todas las dependencias
- **frontend**: Angular con nginx
- **db**: PostgreSQL 15
- **redis**: Para cache (opcional)

### Perfiles disponibles:

- **dev**: Frontend en modo desarrollo
- **prod**: Frontend optimizado para producción
- **redis**: Incluye Redis para cache

## 📱 URLs de Acceso

- **Frontend**: http://localhost:4200
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔄 Migración desde TACollector

Para migrar desde un sistema TACollector existente:

```bash
# Listar dispositivos actuales
python migrar_config.py list

# Migrar configuración
python migrar_config.py
```

El script:
- Lee `TACollector.config.json`
- Migra los 17 dispositivos configurados
- Preserva fechas de última consulta
- Crea configuración global equivalente

## 🛠️ Desarrollo

### Agregar nuevos endpoints:

1. Crear schema en `backend/app/schemas/`
2. Agregar endpoint en `backend/app/api/`
3. Actualizar servicio Angular en `frontend/src/app/services/`
4. Crear componente en `frontend/src/app/modules/`

### Base de datos:

```bash
# Crear migración
alembic revision --autogenerate -m "descripcion"

# Aplicar migración
alembic upgrade head
```

## 🐛 Troubleshooting

### Problemas comunes:

1. **Error de conexión a dispositivo**: Verificar IP, puerto y conectividad de red
2. **Base de datos no conecta**: Revisar DATABASE_URL y que PostgreSQL esté corriendo
3. **Frontend no carga**: Verificar que el backend esté en puerto 8000
4. **Scheduler no funciona**: Revisar configuración `INICIO_AUTOMATICO=true`

### Logs útiles:

```bash
# Ver logs del backend
docker-compose logs backend

# Ver logs en tiempo real
docker-compose logs -f backend

# Logs específicos
docker-compose logs db
```

## 📋 TODO / Mejoras Futuras

- [ ] Autenticación JWT
- [ ] Reportes avanzados (PDF, Excel)
- [ ] Notificaciones push
- [ ] Multi-tenant
- [ ] API rate limiting
- [ ] Tests unitarios completos
- [ ] Métricas con Prometheus
- [ ] Dashboard administrativo

## 📄 Licencia

Este proyecto está bajo licencia MIT. Ver archivo `LICENSE` para más detalles.

## 🤝 Contribuir

1. Fork del proyecto
2. Crear branch feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request