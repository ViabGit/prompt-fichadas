# Sistema de Recolección de Fichadas para Dispositivos ZKTeco

## Descripción General
Necesito crear un sistema completo para gestionar y recolectar fichadas de dispositivos biométricos ZKTeco. El sistema debe tener arquitectura backend/frontend separada, ser dockerizable y manejar múltiples dispositivos de forma automática.

## Arquitectura

### Backend (Python/FastAPI)
- Framework: FastAPI con uvicorn
- Base de datos: PostgreSQL para configuración y SQLite para logs locales
- Scheduler: APScheduler para tareas programadas
- Comunicación con dispositivos: pyzk o zklib2
- WebSockets para actualización en tiempo real del estado
- Docker-ready con requirements.txt y Dockerfile

### Frontend (Angular 17+)
- Angular Material para UI
- RxJS para manejo de estado
- WebSocket client para actualizaciones en tiempo real
- Gráficos con Chart.js para estadísticas
- Responsive design

## Modelos de Datos

### Dispositivo:
```json
{
  "id": "string",
  "nombre": "string",
  "ip": "string",
  "puerto": 4370,
  "modelo": "string",
  "marca": "ZK",
  "activo": boolean,
  "numero_dispositivo": "string",
  "fecha_ultima_consulta": "datetime",
  "alertas_activas": boolean,
  "intentos_fallidos": 0,
  "estado_conexion": "online|offline|error"
}
```

### Configuración Global:
```json
{
  "carpeta_salida": "/data/fichadas/",
  "carpeta_backup": "/data/backup/",
  "frecuencia_minutos": 5,
  "inicio_automatico": true,
  "max_reintentos": 3,
  "smtp_config": {
    "servidor": "string",
    "puerto": 587,
    "usuario": "string",
    "password": "string",
    "desde": "string",
    "para": ["emails"],
    "usar_tls": true
  },
  "sendgrid_config": {
    "api_key": "string",
    "desde": "string",
    "para": ["emails"]
  },
  "tipo_notificacion": "smtp|sendgrid|ninguno"
}
```

### Formato Fichada (archivo .txt):
```
[ID_Usuario] [DD/MM/YYYY] [HH:MM] [Numero_Dispositivo] [Codigo_Adicional]
Ejemplo: 96532 25/09/2024 09:53 33 00
```

## Funcionalidades Backend

### 1. API REST Endpoints:
- `GET /api/dispositivos` - Listar todos los dispositivos
- `POST /api/dispositivos` - Agregar nuevo dispositivo
- `PUT /api/dispositivos/{id}` - Actualizar dispositivo
- `DELETE /api/dispositivos/{id}` - Eliminar dispositivo
- `GET /api/dispositivos/{id}/estado` - Estado actual del dispositivo
- `POST /api/dispositivos/{id}/test-conexion` - Probar conexión
- `POST /api/dispositivos/{id}/descargar-fichadas` - Descarga manual
- `GET /api/configuracion` - Obtener configuración global
- `PUT /api/configuracion` - Actualizar configuración
- `GET /api/logs` - Obtener logs del sistema
- `GET /api/estadisticas` - Dashboard estadísticas
- `WebSocket /ws/monitor` - Monitoreo en tiempo real

### 2. Servicio de Recolección:
```python
class RecolectorService:
    def conectar_dispositivo(self, ip: str, puerto: int) -> conexion:
        """Establece conexión con dispositivo ZK"""
        pass
    
    def descargar_fichadas(self, dispositivo: Dispositivo) -> list:
        """Descarga todas las fichadas del dispositivo"""
        pass
    
    def procesar_fichadas(self, fichadas: list, numero_dispositivo: str) -> str:
        """Procesa fichadas y genera formato de salida"""
        pass
    
    def guardar_fichadas(self, fichadas: str, ruta: str, nombre_archivo: str):
        """Guarda fichadas en archivo txt"""
        pass
    
    def crear_backup(self, archivo_original: str, carpeta_backup: str):
        """Crea backup con timestamp del archivo"""
        pass
    
    def obtener_ultima_fichada(self, dispositivo: Dispositivo) -> datetime:
        """Obtiene fecha/hora de última fichada descargada"""
        pass
    
    def filtrar_fichadas_nuevas(self, fichadas: list, ultima_fecha: datetime) -> list:
        """Filtra solo fichadas posteriores a ultima_fecha"""
        pass
```

### 3. Scheduler de Tareas:
- Ejecutar cada X minutos según configuración
- Para cada dispositivo activo:
  1. Intentar conexión (máx 3 reintentos)
  2. Descargar solo fichadas nuevas desde última consulta
  3. Guardar en archivo [numero_dispositivo].txt
  4. Crear backup con timestamp
  5. Actualizar fecha_ultima_consulta
  6. Si falla después de 3 intentos, enviar alerta

### 4. Sistema de Alertas:
- Enviar email cuando dispositivo no responde
- Notificar recuperación de conexión
- Resumen diario de dispositivos offline
- Alertas configurables por dispositivo

## Funcionalidades Frontend

### 1. Módulos/Páginas:
- **Dashboard**: Vista general con cards de estado
- **Dispositivos**: CRUD completo con tabla y formularios
- **Monitoreo**: Estado en tiempo real con WebSockets
- **Configuración**: Ajustes globales y SMTP/SendGrid
- **Logs**: Visor de logs con filtros
- **Reportes**: Estadísticas y gráficos

### 2. Componentes Principales:
```typescript
// DispositivoListComponent
export class DispositivoListComponent {
  dispositivos$: Observable<Dispositivo[]>;
  // Tabla con acciones CRUD
}

// DispositivoFormComponent
export class DispositivoFormComponent {
  dispositivoForm: FormGroup;
  // Formulario para crear/editar
}

// MonitoreoComponent
export class MonitoreoComponent {
  estadoDispositivos$: Observable<EstadoDispositivo[]>;
  // Auto-refresh cada 5 segundos
  // WebSocket para actualizaciones en tiempo real
}

// ConfiguracionComponent
export class ConfiguracionComponent {
  configuracionForm: FormGroup;
  // Configuración SMTP/SendGrid
  // Configuración de intervalos
}

// EstadoDispositivoComponent
export class EstadoDispositivoComponent {
  @Input() dispositivo: Dispositivo;
  // Card con indicador de estado
  // Verde: online, Rojo: offline, Amarillo: reconectando
}
```

### 3. Servicios Angular:
```typescript
// DispositivoService
@Injectable()
export class DispositivoService {
  getDispositivos(): Observable<Dispositivo[]>
  createDispositivo(dispositivo: Dispositivo): Observable<Dispositivo>
  updateDispositivo(id: string, dispositivo: Dispositivo): Observable<Dispositivo>
  deleteDispositivo(id: string): Observable<void>
  testConexion(id: string): Observable<TestResult>
  descargarManual(id: string): Observable<DescargaResult>
}

// MonitoreoService
@Injectable()
export class MonitoreoService {
  private socket: WebSocket;
  conectar(): Observable<EstadoUpdate>
  desconectar(): void
}

// ConfiguracionService
@Injectable()
export class ConfiguracionService {
  getConfiguracion(): Observable<Configuracion>
  updateConfiguracion(config: Configuracion): Observable<Configuracion>
}
```

## Estructura de Directorios:

```
proyecto-fichadas/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── dispositivo.py
│   │   │   └── configuracion.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── dispositivo.py
│   │   │   └── configuracion.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── recolector.py
│   │   │   ├── scheduler.py
│   │   │   └── notificacion.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── dispositivos.py
│   │   │   ├── configuracion.py
│   │   │   └── monitoreo.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── zk_connector.py
│   │       └── file_manager.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── modules/
│   │   │   │   ├── dashboard/
│   │   │   │   ├── dispositivos/
│   │   │   │   ├── monitoreo/
│   │   │   │   ├── configuracion/
│   │   │   │   └── logs/
│   │   │   ├── services/
│   │   │   │   ├── dispositivo.service.ts
│   │   │   │   ├── monitoreo.service.ts
│   │   │   │   └── configuracion.service.ts
│   │   │   ├── models/
│   │   │   │   ├── dispositivo.model.ts
│   │   │   │   └── configuracion.model.ts
│   │   │   └── shared/
│   │   │       └── components/
│   │   └── environments/
│   │       ├── environment.ts
│   │       └── environment.prod.ts
│   ├── Dockerfile
│   ├── package.json
│   └── angular.json
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Docker Configuration:

### Backend Dockerfile:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### Frontend Dockerfile:
```dockerfile
FROM node:18 as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build --prod

FROM nginx:alpine
COPY --from=build /app/dist/* /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
```

### Docker Compose:
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: fichadas-backend
    ports:
      - "8000:8000"
    volumes:
      - ./data/fichadas:/data/fichadas
      - ./data/backup:/data/backup
      - ./backend/app:/app/app
    environment:
      - DATABASE_URL=postgresql://fichadas_user:fichadas_pass@db:5432/fichadas_db
      - PYTHONUNBUFFERED=1
    depends_on:
      - db
    restart: unless-stopped
  
  frontend:
    build: ./frontend
    container_name: fichadas-frontend
    ports:
      - "4200:80"
    depends_on:
      - backend
    restart: unless-stopped
  
  db:
    image: postgres:15-alpine
    container_name: fichadas-db
    environment:
      - POSTGRES_DB=fichadas_db
      - POSTGRES_USER=fichadas_user
      - POSTGRES_PASSWORD=fichadas_pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

volumes:
  postgres_data:
```

## Librerías y Dependencias:

### Backend (requirements.txt):
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pyzk==0.9
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
apscheduler==3.10.4
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
sendgrid==6.11.0
aiofiles==23.2.1
websockets==12.0
pydantic==2.5.0
pydantic-settings==2.1.0
httpx==0.25.2
redis==5.0.1
celery==5.3.4
```

### Frontend (package.json dependencies):
```json
{
  "dependencies": {
    "@angular/animations": "^17.0.0",
    "@angular/common": "^17.0.0",
    "@angular/compiler": "^17.0.0",
    "@angular/core": "^17.0.0",
    "@angular/forms": "^17.0.0",
    "@angular/material": "^17.0.0",
    "@angular/platform-browser": "^17.0.0",
    "@angular/platform-browser-dynamic": "^17.0.0",
    "@angular/router": "^17.0.0",
    "rxjs": "^7.8.0",
    "chart.js": "^4.4.0",
    "ng2-charts": "^5.0.0",
    "moment": "^2.29.4",
    "socket.io-client": "^4.5.4"
  }
}
```

## Ejemplo de Implementación - Backend main.py:

```python
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from app.database import init_db
from app.services.scheduler import start_scheduler
from app.api import dispositivos, configuracion, monitoreo
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    start_scheduler()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Sistema de Fichadas ZKTeco",
    description="API para gestión de dispositivos ZKTeco y recolección de fichadas",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(dispositivos.router, prefix="/api/dispositivos", tags=["dispositivos"])
app.include_router(configuracion.router, prefix="/api/configuracion", tags=["configuracion"])
app.include_router(monitoreo.router, prefix="/api/monitoreo", tags=["monitoreo"])

@app.get("/")
async def root():
    return {"message": "Sistema de Fichadas ZKTeco API v1.0"}

@app.websocket("/ws/monitor")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Implementar lógica de WebSocket para monitoreo en tiempo real
    pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Ejemplo de Servicio Recolector:

```python
from pyzk import ZK
from datetime import datetime
import os
import shutil
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class RecolectorService:
    def __init__(self):
        self.conn = None
    
    def conectar_dispositivo(self, ip: str, puerto: int = 4370) -> bool:
        """Establece conexión con dispositivo ZK"""
        try:
            self.zk = ZK(ip, port=puerto, timeout=5, password=0, force_udp=False)
            self.conn = self.zk.connect()
            return True
        except Exception as e:
            logger.error(f"Error conectando a {ip}:{puerto} - {str(e)}")
            return False
    
    def descargar_fichadas(self, dispositivo) -> List:
        """Descarga fichadas del dispositivo"""
        try:
            if not self.conn:
                if not self.conectar_dispositivo(dispositivo.ip, dispositivo.puerto):
                    return []
            
            # Obtener fichadas
            fichadas = self.conn.get_attendance()
            return fichadas
        except Exception as e:
            logger.error(f"Error descargando fichadas: {str(e)}")
            return []
        finally:
            if self.conn:
                self.conn.disconnect()
    
    def procesar_fichadas(self, fichadas: List, numero_dispositivo: str, codigo_adicional: str = "00") -> str:
        """Procesa fichadas y genera formato de salida"""
        lineas = []
        for fichada in fichadas:
            # Formato: ID_Usuario DD/MM/YYYY HH:MM Numero_Dispositivo Codigo_Adicional
            fecha = fichada.timestamp.strftime("%d/%m/%Y")
            hora = fichada.timestamp.strftime("%H:%M")
            linea = f"{fichada.user_id} {fecha} {hora} {numero_dispositivo} {codigo_adicional}"
            lineas.append(linea)
        
        return "\n".join(lineas)
    
    def guardar_fichadas(self, contenido: str, carpeta: str, nombre_archivo: str):
        """Guarda fichadas en archivo txt"""
        os.makedirs(carpeta, exist_ok=True)
        archivo_path = os.path.join(carpeta, f"{nombre_archivo}.txt")
        
        with open(archivo_path, 'w') as f:
            f.write(contenido)
        
        logger.info(f"Fichadas guardadas en {archivo_path}")
        return archivo_path
    
    def crear_backup(self, archivo_original: str, carpeta_backup: str):
        """Crea backup con timestamp"""
        if not os.path.exists(archivo_original):
            return
        
        os.makedirs(carpeta_backup, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_base = os.path.basename(archivo_original)
        nombre_sin_ext = os.path.splitext(nombre_base)[0]
        
        archivo_backup = os.path.join(
            carpeta_backup, 
            f"{nombre_sin_ext}_backup_{timestamp}.txt"
        )
        
        shutil.copy2(archivo_original, archivo_backup)
        logger.info(f"Backup creado: {archivo_backup}")
        return archivo_backup
    
    def filtrar_fichadas_nuevas(self, fichadas: List, ultima_fecha: datetime) -> List:
        """Filtra solo fichadas posteriores a ultima_fecha"""
        if not ultima_fecha:
            return fichadas
        
        fichadas_nuevas = [
            f for f in fichadas 
            if f.timestamp > ultima_fecha
        ]
        
        return fichadas_nuevas
```

## Testing:

### Tests Unitarios Backend:
```python
import pytest
from app.services.recolector import RecolectorService

def test_procesar_fichadas():
    service = RecolectorService()
    # Mock de fichadas
    fichadas_mock = [...]
    resultado = service.procesar_fichadas(fichadas_mock, "33", "00")
    assert "33 00" in resultado

def test_crear_backup():
    # Test de creación de backup
    pass
```

### Tests E2E Frontend:
```typescript
describe('DispositivosComponent', () => {
  it('should display dispositivos list', () => {
    // Test implementation
  });
  
  it('should create new dispositivo', () => {
    // Test implementation
  });
});
```

## Consideraciones de Seguridad:
1. Encriptar contraseñas en base de datos usando bcrypt
2. Implementar JWT para autenticación
3. Sanitizar todos los inputs del usuario
4. Rate limiting en API (max 100 requests/minuto)
5. CORS configurado para dominios específicos
6. Variables sensibles en archivo .env (nunca en el código)
7. HTTPS obligatorio en producción
8. Validación de formato de IP antes de conectar
9. Timeout en conexiones a dispositivos
10. Logs de auditoría para todas las acciones

## Funcionalidades Adicionales Recomendadas:
1. **Exportación de Datos**: Excel, CSV, PDF
2. **API REST Documentada**: Con Swagger/OpenAPI
3. **Autenticación Multi-Factor**: Para mayor seguridad
4. **Modo Debug**: Configurable desde variables de entorno
5. **Métricas con Prometheus**: Para monitoreo avanzado
6. **Health Checks**: Para Docker y Kubernetes
7. **Limpieza Automática**: De backups antiguos (>30 días)
8. **Dashboard Analítico**: Fichadas por día, hora pico, etc.
9. **Sincronización de Hora**: Con dispositivos ZK
10. **Multi-idioma**: i18n en frontend

## Comandos de Inicio Rápido:

```bash
# Clonar repositorio
git clone <repository-url>
cd proyecto-fichadas

# Configurar variables de entorno
cp backend/.env.example backend/.env
# Editar backend/.env con tus configuraciones

# Construir y ejecutar con Docker
docker-compose up --build

# O desarrollo local:

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
ng serve

# Acceder a:
# Frontend: http://localhost:4200
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Notas Importantes:
- La librería pyzk puede requerir permisos especiales en algunos sistemas
- Algunos modelos de ZKTeco pueden necesitar configuración específica
- Verificar compatibilidad del SDK con los modelos específicos
- Los puertos de los dispositivos deben estar accesibles desde el servidor
- Considerar uso de VPN si los dispositivos están en diferentes redes

## Troubleshooting Común:
1. **Error de conexión**: Verificar IP, puerto y que el dispositivo esté en la red
2. **Timeout**: Aumentar timeout en configuración o verificar latencia de red
3. **Formato incorrecto**: Algunos modelos pueden devolver datos en formato diferente
4. **Permisos**: El contenedor Docker necesita permisos para escribir en carpetas
5. **Base de datos**: Verificar que PostgreSQL esté corriendo y las credenciales sean correctas
