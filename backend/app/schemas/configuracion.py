from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime


class SMTPConfig(BaseModel):
    servidor: str
    puerto: int = 587
    usuario: str
    password: str
    desde: str
    para: List[str]
    usar_tls: bool = True


class SendGridConfig(BaseModel):
    api_key: str
    desde: str
    para: List[str]


class ConfiguracionGlobalBase(BaseModel):
    carpeta_salida: str = "/data/fichadas/"
    carpeta_backup: str = "/data/backup/"
    frecuencia_minutos: int = 5
    inicio_automatico: bool = True
    max_reintentos: int = 3
    tipo_notificacion: str = "none"


class ConfiguracionGlobalCreate(ConfiguracionGlobalBase):
    smtp_config: Optional[SMTPConfig] = None
    sendgrid_config: Optional[SendGridConfig] = None


class ConfiguracionGlobalUpdate(BaseModel):
    carpeta_salida: Optional[str] = None
    carpeta_backup: Optional[str] = None
    frecuencia_minutos: Optional[int] = None
    inicio_automatico: Optional[bool] = None
    max_reintentos: Optional[int] = None
    tipo_notificacion: Optional[str] = None
    smtp_config: Optional[SMTPConfig] = None
    sendgrid_config: Optional[SendGridConfig] = None
    
    @validator('tipo_notificacion')
    def validate_notification_type(cls, v):
        if v is not None and v not in ['smtp', 'sendgrid', 'none']:
            raise ValueError('tipo_notificacion must be smtp, sendgrid or none')
        return v


class ConfiguracionGlobalResponse(ConfiguracionGlobalBase):
    id: int
    smtp_config: Optional[SMTPConfig] = None
    sendgrid_config: Optional[SendGridConfig] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True