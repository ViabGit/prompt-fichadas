from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
from datetime import datetime, timedelta
from ..database import get_db
from ..models.dispositivo import Dispositivo, LogSistema
from ..schemas.sistema import LogSistemaResponse, EstadisticasResponse, MonitoreoUpdate
from ..schemas.dispositivo import EstadoDispositivo
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except:
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)
        
        # Limpiar conexiones desconectadas
        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()


@router.websocket("/monitor")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    """WebSocket para monitoreo en tiempo real"""
    await manager.connect(websocket)
    try:
        # Enviar estado inicial
        dispositivos = db.query(Dispositivo).all()
        estados = [
            EstadoDispositivo(
                id=d.id,
                nombre=d.nombre,
                estado_conexion=d.estado_conexion,
                fecha_ultima_consulta=d.fecha_ultima_consulta,
                intentos_fallidos=d.intentos_fallidos,
                alertas_activas=d.alertas_activas
            ).dict() for d in dispositivos
        ]
        
        await manager.send_personal_message(
            json.dumps({
                "tipo": "estado_inicial",
                "datos": estados,
                "timestamp": datetime.now().isoformat()
            }),
            websocket
        )
        
        # Mantener conexión viva
        while True:
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Error en WebSocket: {str(e)}")
        manager.disconnect(websocket)


async def broadcast_update(update: MonitoreoUpdate):
    """Enviar actualización a todos los clientes WebSocket conectados"""
    message = json.dumps({
        "tipo": "update",
        "datos": update.dict(),
        "timestamp": datetime.now().isoformat()
    })
    await manager.broadcast(message)


@router.get("/dispositivos/estado", response_model=List[EstadoDispositivo])
async def obtener_estado_dispositivos(db: Session = Depends(get_db)):
    """Obtener estado actual de todos los dispositivos"""
    dispositivos = db.query(Dispositivo).all()
    return [
        EstadoDispositivo(
            id=d.id,
            nombre=d.nombre,
            estado_conexion=d.estado_conexion,
            fecha_ultima_consulta=d.fecha_ultima_consulta,
            intentos_fallidos=d.intentos_fallidos,
            alertas_activas=d.alertas_activas
        ) for d in dispositivos
    ]


@router.get("/logs", response_model=List[LogSistemaResponse])
async def obtener_logs(
    nivel: str = None,
    componente: str = None,
    dispositivo_id: str = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Obtener logs del sistema con filtros opcionales"""
    query = db.query(LogSistema)
    
    if nivel:
        query = query.filter(LogSistema.nivel == nivel.upper())
    
    if componente:
        query = query.filter(LogSistema.componente == componente)
    
    if dispositivo_id:
        query = query.filter(LogSistema.dispositivo_id == dispositivo_id)
    
    logs = query.order_by(desc(LogSistema.created_at)).offset(offset).limit(limit).all()
    return logs


@router.get("/estadisticas", response_model=EstadisticasResponse)
async def obtener_estadisticas(db: Session = Depends(get_db)):
    """Obtener estadísticas del dashboard"""
    
    # Contar dispositivos por estado
    dispositivos = db.query(Dispositivo).all()
    total_dispositivos = len(dispositivos)
    dispositivos_online = len([d for d in dispositivos if d.estado_conexion == "online"])
    dispositivos_offline = len([d for d in dispositivos if d.estado_conexion == "offline"])
    dispositivos_error = len([d for d in dispositivos if d.estado_conexion == "error"])
    
    # Contar errores en las últimas 24 horas
    hace_24h = datetime.now() - timedelta(hours=24)
    errores_24h = db.query(LogSistema).filter(
        LogSistema.nivel == "ERROR",
        LogSistema.created_at >= hace_24h
    ).count()
    
    # Contar fichadas de hoy (aproximado basado en logs)
    hoy = datetime.now().date()
    fichadas_hoy = db.query(LogSistema).filter(
        LogSistema.componente == "recolector",
        LogSistema.nivel == "INFO",
        func.date(LogSistema.created_at) == hoy,
        LogSistema.mensaje.contains("fichadas")
    ).count()
    
    return EstadisticasResponse(
        total_dispositivos=total_dispositivos,
        dispositivos_online=dispositivos_online,
        dispositivos_offline=dispositivos_offline,
        dispositivos_error=dispositivos_error,
        ultima_actualizacion=datetime.now(),
        fichadas_hoy=fichadas_hoy,
        errores_ultimas_24h=errores_24h
    )


@router.delete("/logs")
async def limpiar_logs(
    dias: int = 30,
    nivel: str = None,
    db: Session = Depends(get_db)
):
    """Limpiar logs antiguos"""
    fecha_limite = datetime.now() - timedelta(days=dias)
    
    query = db.query(LogSistema).filter(LogSistema.created_at < fecha_limite)
    
    if nivel:
        query = query.filter(LogSistema.nivel == nivel.upper())
    
    count = query.count()
    query.delete()
    db.commit()
    
    logger.info(f"Limpiados {count} logs anteriores a {fecha_limite}")
    return {"message": f"Eliminados {count} logs anteriores a {dias} días"}


@router.get("/logs/download")
async def descargar_logs(
    nivel: str = None,
    componente: str = None,
    fecha_desde: datetime = None,
    fecha_hasta: datetime = None,
    db: Session = Depends(get_db)
):
    """Descargar logs como archivo CSV"""
    from fastapi.responses import StreamingResponse
    from io import StringIO
    import csv
    
    query = db.query(LogSistema)
    
    if nivel:
        query = query.filter(LogSistema.nivel == nivel.upper())
    
    if componente:
        query = query.filter(LogSistema.componente == componente)
    
    if fecha_desde:
        query = query.filter(LogSistema.created_at >= fecha_desde)
    
    if fecha_hasta:
        query = query.filter(LogSistema.created_at <= fecha_hasta)
    
    logs = query.order_by(desc(LogSistema.created_at)).limit(10000).all()
    
    # Crear CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow(['ID', 'Fecha', 'Nivel', 'Mensaje', 'Dispositivo', 'Componente', 'Detalles'])
    
    # Datos
    for log in logs:
        writer.writerow([
            log.id,
            log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            log.nivel,
            log.mensaje,
            log.dispositivo_id or '',
            log.componente,
            log.detalles or ''
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=logs_sistema.csv"}
    )