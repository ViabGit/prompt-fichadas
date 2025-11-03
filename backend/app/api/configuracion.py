from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.dispositivo import ConfiguracionGlobal
from ..schemas.configuracion import (
    ConfiguracionGlobalCreate,
    ConfiguracionGlobalUpdate,
    ConfiguracionGlobalResponse
)
from ..services.scheduler import restart_scheduler
from ..services.notificacion import NotificacionService
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
notificacion_service = NotificacionService()


@router.get("/", response_model=ConfiguracionGlobalResponse)
async def obtener_configuracion(db: Session = Depends(get_db)):
    """Obtener configuración global actual"""
    config = db.query(ConfiguracionGlobal).first()
    
    if not config:
        # Crear configuración por defecto si no existe
        config = ConfiguracionGlobal()
        db.add(config)
        db.commit()
        db.refresh(config)
    
    # Convertir campos JSON a objetos
    response_data = {
        "id": config.id,
        "carpeta_salida": config.carpeta_salida,
        "carpeta_backup": config.carpeta_backup,
        "frecuencia_minutos": config.frecuencia_minutos,
        "inicio_automatico": config.inicio_automatico,
        "max_reintentos": config.max_reintentos,
        "tipo_notificacion": config.tipo_notificacion,
        "created_at": config.created_at,
        "updated_at": config.updated_at
    }
    
    # Configuración SMTP
    if (config.smtp_servidor and config.smtp_usuario and 
        config.smtp_password and config.smtp_desde and config.smtp_para):
        try:
            smtp_para = json.loads(config.smtp_para) if isinstance(config.smtp_para, str) else []
            response_data["smtp_config"] = {
                "servidor": config.smtp_servidor,
                "puerto": config.smtp_puerto,
                "usuario": config.smtp_usuario,
                "password": "***",  # No exponer password
                "desde": config.smtp_desde,
                "para": smtp_para,
                "usar_tls": config.smtp_usar_tls
            }
        except json.JSONDecodeError:
            pass
    
    # Configuración SendGrid
    if config.sendgrid_api_key and config.sendgrid_desde and config.sendgrid_para:
        try:
            sendgrid_para = json.loads(config.sendgrid_para) if isinstance(config.sendgrid_para, str) else []
            response_data["sendgrid_config"] = {
                "api_key": "***",  # No exponer API key
                "desde": config.sendgrid_desde,
                "para": sendgrid_para
            }
        except json.JSONDecodeError:
            pass
    
    return ConfiguracionGlobalResponse(**response_data)


@router.put("/", response_model=ConfiguracionGlobalResponse)
async def actualizar_configuracion(
    config_update: ConfiguracionGlobalUpdate, 
    db: Session = Depends(get_db)
):
    """Actualizar configuración global"""
    config = db.query(ConfiguracionGlobal).first()
    
    if not config:
        config = ConfiguracionGlobal()
        db.add(config)
    
    # Actualizar campos básicos
    update_data = config_update.dict(exclude_unset=True, exclude={'smtp_config', 'sendgrid_config'})
    for field, value in update_data.items():
        setattr(config, field, value)
    
    # Actualizar configuración SMTP
    if config_update.smtp_config:
        smtp_config = config_update.smtp_config
        config.smtp_servidor = smtp_config.servidor
        config.smtp_puerto = smtp_config.puerto
        config.smtp_usuario = smtp_config.usuario
        if smtp_config.password != "***":  # Solo actualizar si no es placeholder
            config.smtp_password = smtp_config.password
        config.smtp_desde = smtp_config.desde
        config.smtp_para = json.dumps(smtp_config.para)
        config.smtp_usar_tls = smtp_config.usar_tls
    
    # Actualizar configuración SendGrid
    if config_update.sendgrid_config:
        sendgrid_config = config_update.sendgrid_config
        if sendgrid_config.api_key != "***":  # Solo actualizar si no es placeholder
            config.sendgrid_api_key = sendgrid_config.api_key
        config.sendgrid_desde = sendgrid_config.desde
        config.sendgrid_para = json.dumps(sendgrid_config.para)
    
    db.commit()
    db.refresh(config)
    
    # Reiniciar scheduler si cambió la frecuencia o inicio automático
    if 'frecuencia_minutos' in update_data or 'inicio_automatico' in update_data:
        restart_scheduler()
        logger.info("Scheduler reiniciado debido a cambios en configuración")
    
    logger.info("Configuración global actualizada")
    
    # Retornar configuración actualizada
    return await obtener_configuracion(db)


@router.post("/test-notificacion")
async def test_notificacion(tipo: str, db: Session = Depends(get_db)):
    """Probar configuración de notificaciones"""
    if tipo not in ['smtp', 'sendgrid']:
        raise HTTPException(status_code=400, detail="Tipo debe ser 'smtp' o 'sendgrid'")
    
    config = db.query(ConfiguracionGlobal).first()
    if not config:
        raise HTTPException(status_code=404, detail="No hay configuración disponible")
    
    # Preparar datos de configuración para test
    if tipo == 'smtp':
        if not all([config.smtp_servidor, config.smtp_usuario, config.smtp_password]):
            raise HTTPException(status_code=400, detail="Configuración SMTP incompleta")
        
        config_data = {
            "servidor": config.smtp_servidor,
            "puerto": config.smtp_puerto,
            "usuario": config.smtp_usuario,
            "password": config.smtp_password,
            "desde": config.smtp_desde,
            "para": json.loads(config.smtp_para) if config.smtp_para else [],
            "usar_tls": config.smtp_usar_tls
        }
    else:  # sendgrid
        if not all([config.sendgrid_api_key, config.sendgrid_desde]):
            raise HTTPException(status_code=400, detail="Configuración SendGrid incompleta")
        
        config_data = {
            "api_key": config.sendgrid_api_key,
            "desde": config.sendgrid_desde,
            "para": json.loads(config.sendgrid_para) if config.sendgrid_para else []
        }
    
    # Ejecutar test
    resultado = await notificacion_service.test_configuracion(tipo, config_data)
    
    if not resultado["success"]:
        raise HTTPException(status_code=500, detail=resultado["mensaje"])
    
    return {"message": "Configuración de notificación probada exitosamente"}


@router.get("/scheduler/status")
async def obtener_estado_scheduler():
    """Obtener estado del scheduler"""
    from ..services.scheduler import get_scheduler_status
    return get_scheduler_status()


@router.post("/scheduler/{action}")
async def controlar_scheduler(action: str):
    """Controlar scheduler (start, stop, restart)"""
    if action not in ['start', 'stop', 'restart']:
        raise HTTPException(status_code=400, detail="Acción debe ser 'start', 'stop' o 'restart'")
    
    try:
        if action == 'start':
            from ..services.scheduler import start_scheduler
            start_scheduler()
        elif action == 'stop':
            from ..services.scheduler import stop_scheduler
            stop_scheduler()
        else:  # restart
            restart_scheduler()
        
        return {"message": f"Scheduler {action} ejecutado exitosamente"}
        
    except Exception as e:
        logger.error(f"Error controlando scheduler: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")