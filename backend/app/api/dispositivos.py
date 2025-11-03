from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.dispositivo import Dispositivo
from ..schemas.dispositivo import (
    DispositivoCreate,
    DispositivoUpdate, 
    DispositivoResponse,
    TestConexionResponse,
    DescargaManualResponse
)
from ..services.recolector import RecolectorService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
recolector_service = RecolectorService()


@router.get("/", response_model=List[DispositivoResponse])
async def listar_dispositivos(db: Session = Depends(get_db)):
    """Obtener todos los dispositivos"""
    dispositivos = db.query(Dispositivo).all()
    return dispositivos


@router.get("/{dispositivo_id}", response_model=DispositivoResponse)
async def obtener_dispositivo(dispositivo_id: str, db: Session = Depends(get_db)):
    """Obtener un dispositivo por ID"""
    dispositivo = db.query(Dispositivo).filter(Dispositivo.id == dispositivo_id).first()
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return dispositivo


@router.post("/", response_model=DispositivoResponse)
async def crear_dispositivo(dispositivo: DispositivoCreate, db: Session = Depends(get_db)):
    """Crear nuevo dispositivo"""
    # Verificar que no exista otro con la misma ID
    existing = db.query(Dispositivo).filter(Dispositivo.id == dispositivo.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un dispositivo con esa ID")
    
    # Verificar que no exista otro con la misma IP
    existing_ip = db.query(Dispositivo).filter(Dispositivo.ip == dispositivo.ip).first()
    if existing_ip:
        raise HTTPException(status_code=400, detail="Ya existe un dispositivo con esa IP")
    
    db_dispositivo = Dispositivo(**dispositivo.dict())
    db.add(db_dispositivo)
    db.commit()
    db.refresh(db_dispositivo)
    
    logger.info(f"Dispositivo creado: {db_dispositivo.nombre} ({db_dispositivo.id})")
    return db_dispositivo


@router.put("/{dispositivo_id}", response_model=DispositivoResponse)
async def actualizar_dispositivo(
    dispositivo_id: str, 
    dispositivo_update: DispositivoUpdate, 
    db: Session = Depends(get_db)
):
    """Actualizar dispositivo existente"""
    dispositivo = db.query(Dispositivo).filter(Dispositivo.id == dispositivo_id).first()
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    
    # Actualizar solo los campos proporcionados
    update_data = dispositivo_update.dict(exclude_unset=True)
    
    # Verificar IP única si se está actualizando
    if 'ip' in update_data:
        existing_ip = db.query(Dispositivo).filter(
            Dispositivo.ip == update_data['ip'],
            Dispositivo.id != dispositivo_id
        ).first()
        if existing_ip:
            raise HTTPException(status_code=400, detail="Ya existe un dispositivo con esa IP")
    
    for field, value in update_data.items():
        setattr(dispositivo, field, value)
    
    db.commit()
    db.refresh(dispositivo)
    
    logger.info(f"Dispositivo actualizado: {dispositivo.nombre} ({dispositivo.id})")
    return dispositivo


@router.delete("/{dispositivo_id}")
async def eliminar_dispositivo(dispositivo_id: str, db: Session = Depends(get_db)):
    """Eliminar dispositivo"""
    dispositivo = db.query(Dispositivo).filter(Dispositivo.id == dispositivo_id).first()
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    
    nombre = dispositivo.nombre
    db.delete(dispositivo)
    db.commit()
    
    logger.info(f"Dispositivo eliminado: {nombre} ({dispositivo_id})")
    return {"message": "Dispositivo eliminado exitosamente"}


@router.post("/{dispositivo_id}/test-conexion", response_model=TestConexionResponse)
async def test_conexion(dispositivo_id: str, db: Session = Depends(get_db)):
    """Probar conexión con dispositivo"""
    dispositivo = db.query(Dispositivo).filter(Dispositivo.id == dispositivo_id).first()
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    
    resultado = recolector_service.test_conexion(dispositivo.ip, dispositivo.puerto)
    
    # Actualizar estado en base de datos
    if resultado.success:
        dispositivo.estado_conexion = "online"
        dispositivo.intentos_fallidos = 0
    else:
        dispositivo.estado_conexion = "error"
        dispositivo.intentos_fallidos += 1
    
    db.commit()
    
    return resultado


@router.post("/{dispositivo_id}/descargar-fichadas", response_model=DescargaManualResponse)
async def descargar_fichadas_manual(
    dispositivo_id: str, 
    forzar: bool = False,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Descargar fichadas manualmente"""
    dispositivo = db.query(Dispositivo).filter(Dispositivo.id == dispositivo_id).first()
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    
    try:
        # Ejecutar descarga
        resultado = recolector_service.procesar_dispositivo_completo(
            dispositivo, db, forzar_descarga=forzar
        )
        
        logger.info(f"Descarga manual completada para {dispositivo.nombre}: {resultado.mensaje}")
        return resultado
        
    except Exception as e:
        logger.error(f"Error en descarga manual de {dispositivo.nombre}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en descarga: {str(e)}")


@router.get("/{dispositivo_id}/estado")
async def obtener_estado_dispositivo(dispositivo_id: str, db: Session = Depends(get_db)):
    """Obtener estado actual del dispositivo"""
    dispositivo = db.query(Dispositivo).filter(Dispositivo.id == dispositivo_id).first()
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    
    return {
        "id": dispositivo.id,
        "nombre": dispositivo.nombre,
        "estado_conexion": dispositivo.estado_conexion,
        "fecha_ultima_consulta": dispositivo.fecha_ultima_consulta,
        "intentos_fallidos": dispositivo.intentos_fallidos,
        "alertas_activas": dispositivo.alertas_activas,
        "activo": dispositivo.activo
    }