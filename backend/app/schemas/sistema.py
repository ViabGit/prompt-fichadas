from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class LogSistemaBase(BaseModel):
    nivel: str  # INFO, WARNING, ERROR
    mensaje: str
    dispositivo_id: Optional[str] = None
    componente: str
    detalles: Optional[str] = None


class LogSistemaCreate(LogSistemaBase):
    pass


class LogSistemaResponse(LogSistemaBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class EstadisticasResponse(BaseModel):
    total_dispositivos: int
    dispositivos_online: int
    dispositivos_offline: int
    dispositivos_error: int
    ultima_actualizacion: datetime
    fichadas_hoy: int
    errores_ultimas_24h: int


class MonitoreoUpdate(BaseModel):
    tipo: str  # conexion, fichada, error
    dispositivo_id: str
    mensaje: str
    timestamp: datetime
    datos_adicionales: Optional[dict] = None