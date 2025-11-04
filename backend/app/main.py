from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import uvicorn
from .database import init_db
from .services.scheduler import start_scheduler, stop_scheduler
from .api import dispositivos, configuracion, monitoreo
from .config import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager para la aplicación"""
    # Startup
    logger.info("Iniciando Sistema de Fichadas ZKTeco...")
    
    try:
        # Inicializar base de datos
        init_db()
        logger.info("Base de datos inicializada")
        
        # Iniciar scheduler
        start_scheduler()
        logger.info("Scheduler iniciado")
        
        logger.info("Sistema iniciado exitosamente")
        
    except Exception as e:
        logger.error(f"Error durante el startup: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Cerrando Sistema de Fichadas ZKTeco...")
    try:
        stop_scheduler()
        logger.info("Scheduler detenido")
    except Exception as e:
        logger.error(f"Error durante el shutdown: {str(e)}")


# Crear aplicación FastAPI
app = FastAPI(
    title="Sistema de Fichadas ZKTeco",
    description="API para gestión de dispositivos ZKTeco y recolección de fichadas",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    redirect_slashes=False  # Evitar redirecciones automáticas de trailing slash
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:3000", "*"] if settings.debug else ["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(
    dispositivos.router, 
    prefix="/api/dispositivos", 
    tags=["dispositivos"]
)

app.include_router(
    configuracion.router, 
    prefix="/api/configuracion", 
    tags=["configuracion"]
)

app.include_router(
    monitoreo.router, 
    prefix="/api/monitoreo", 
    tags=["monitoreo"]
)


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Sistema de Fichadas ZKTeco API v1.0",
        "docs": "/docs" if settings.debug else "disabled",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check para Docker y monitoring"""
    from .services.scheduler import get_scheduler_status
    from .database import SessionLocal
    from sqlalchemy import text
    
    try:
        # Test database
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Test scheduler
    scheduler_status = get_scheduler_status()
    
    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "database": db_status,
        "scheduler": scheduler_status,
        "version": "1.0.0"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0", 
        port=8000, 
        reload=settings.debug,
        log_level="info"
    )