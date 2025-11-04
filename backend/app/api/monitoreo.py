from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict
from datetime import datetime, timedelta
from ..database import get_db
from ..models.dispositivo import Dispositivo, LogSistema
from ..schemas.sistema import LogSistemaResponse, EstadisticasResponse, MonitoreoUpdate
from ..schemas.dispositivo import EstadoDispositivo
import json
import logging
import os
from functools import lru_cache
from pathlib import Path
import time

logger = logging.getLogger(__name__)
router = APIRouter()

# Cache para resultados de conteo de fichadas (cache de 30 segundos)
_fichadas_cache = {"data": None, "timestamp": 0, "ttl": 30}


def contar_fichadas_rapido(fecha: datetime.date = None) -> Dict:
    """
    Cuenta fichadas con cache para evitar leer archivos constantemente.
    Usa grep para contar líneas de forma más eficiente.
    """
    if fecha is None:
        fecha = datetime.now().date()
    
    # Verificar cache
    current_time = time.time()
    if (_fichadas_cache["data"] is not None and 
        current_time - _fichadas_cache["timestamp"] < _fichadas_cache["ttl"]):
        cached_fecha = _fichadas_cache["data"].get("fecha")
        if cached_fecha == fecha:
            return _fichadas_cache["data"]
    
    # Cache expirado o fecha diferente, recalcular
    fichadas_dir = "/data/fichadas"
    resumen = []
    total_fichadas = 0
    fecha_str = fecha.strftime('%d/%m/%Y')
    
    if os.path.exists(fichadas_dir):
        try:
            archivos = [f for f in os.listdir(fichadas_dir) if f.endswith('.txt')]
            
            # Procesar archivos en paralelo con límite de tiempo
            import concurrent.futures
            
            def contar_fichadas_archivo(archivo):
                archivo_path = os.path.join(fichadas_dir, archivo)
                numero_dispositivo = archivo.replace('.txt', '')
                
                try:
                    # Usar wc y grep en pipeline (más rápido)
                    import subprocess
                    result = subprocess.run(
                        f"grep -c '{fecha_str}' {archivo_path} || echo 0",
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=1
                    )
                    fichadas_count = int(result.stdout.strip())
                except:
                    fichadas_count = 0
                
                return {
                    "numero_dispositivo": numero_dispositivo,
                    "fichadas_hoy": fichadas_count
                }
            
            # Procesar hasta 10 archivos en paralelo
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                results = list(executor.map(contar_fichadas_archivo, archivos, timeout=15))
            
            for result in results:
                total_fichadas += result["fichadas_hoy"]
                resumen.append(result)
                
        except Exception as e:
            logger.error(f"Error contando fichadas: {e}")
    
    # Actualizar cache
    result = {
        "resumen": resumen,
        "total_fichadas": total_fichadas,
        "fecha": fecha
    }
    _fichadas_cache["data"] = result
    _fichadas_cache["timestamp"] = current_time
    
    return result


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
    
    # Usar cache para contar fichadas
    fichadas_data = contar_fichadas_rapido()
    fichadas_hoy = fichadas_data["total_fichadas"]
    
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


@router.get("/fichadas/resumen-diario")
async def obtener_resumen_fichadas_diario(db: Session = Depends(get_db)):
    """Obtener resumen de fichadas por dispositivo del día actual"""
    hoy = datetime.now().date()
    dispositivos = db.query(Dispositivo).filter(Dispositivo.activo == True).all()
    
    # Obtener conteo de fichadas desde cache
    fichadas_data = contar_fichadas_rapido(hoy)
    fichadas_por_numero = {
        item["numero_dispositivo"]: item["fichadas_hoy"] 
        for item in fichadas_data["resumen"]
    }
    
    resumen = []
    for dispositivo in dispositivos:
        fichadas_count = fichadas_por_numero.get(dispositivo.numero_dispositivo, 0)
        
        resumen.append({
            "dispositivo_id": dispositivo.id,
            "nombre": dispositivo.nombre,
            "numero_dispositivo": dispositivo.numero_dispositivo,
            "ip": dispositivo.ip,
            "fichadas_hoy": fichadas_count,
            "ultima_actualizacion": dispositivo.fecha_ultima_consulta,
            "estado_conexion": dispositivo.estado_conexion
        })
    
    return {
        "resumen": resumen,
        "total_fichadas": fichadas_data["total_fichadas"],
        "fecha": hoy.strftime('%Y-%m-%d')
    }