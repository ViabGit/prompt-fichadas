from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime


class DispositivoBase(BaseModel):
    nombre: str
    ip: str
    puerto: int = 4370
    modelo: Optional[str] = None
    marca: str = "ZK"
    activo: bool = True
    numero_dispositivo: str
    
    @validator('ip')
    def validate_ip(cls, v):
        import ipaddress
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            raise ValueError('IP address is not valid')


class DispositivoCreate(DispositivoBase):
    id: str


class DispositivoUpdate(BaseModel):
    nombre: Optional[str] = None
    ip: Optional[str] = None
    puerto: Optional[int] = None
    modelo: Optional[str] = None
    marca: Optional[str] = None
    activo: Optional[bool] = None
    numero_dispositivo: Optional[str] = None
    
    @validator('ip')
    def validate_ip(cls, v):
        if v is not None:
            import ipaddress
            try:
                ipaddress.ip_address(v)
                return v
            except ValueError:
                raise ValueError('IP address is not valid')


class DispositivoResponse(DispositivoBase):
    id: str
    fecha_ultima_consulta: Optional[datetime] = None
    alertas_activas: bool = False
    intentos_fallidos: int = 0
    estado_conexion: str = "offline"
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TestConexionResponse(BaseModel):
    success: bool
    mensaje: str
    tiempo_respuesta: Optional[float] = None
    error_detalle: Optional[str] = None


class DescargaManualResponse(BaseModel):
    success: bool
    mensaje: str
    fichadas_descargadas: int = 0
    archivo_generado: Optional[str] = None
    error_detalle: Optional[str] = None


class EstadoDispositivo(BaseModel):
    id: str
    nombre: str
    estado_conexion: str
    fecha_ultima_consulta: Optional[datetime]
    intentos_fallidos: int
    alertas_activas: bool