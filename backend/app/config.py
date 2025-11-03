from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # Base de datos
    database_url: str = "postgresql://fichadas_user:fichadas_pass@localhost:5432/fichadas_db"
    secret_key: str = "your-secret-key-here"
    debug: bool = True
    
    # Configuración de archivos
    carpeta_salida: str = "/data/fichadas"
    carpeta_backup: str = "/data/backup"
    
    # Configuración de tareas
    frecuencia_minutos: int = 5
    inicio_automatico: bool = True
    max_reintentos: int = 3
    
    # Configuración SMTP
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from: Optional[str] = None
    smtp_to: Optional[str] = None
    smtp_use_tls: bool = True
    
    # Configuración SendGrid
    sendgrid_api_key: Optional[str] = None
    sendgrid_from: Optional[str] = None
    sendgrid_to: Optional[str] = None
    
    # Tipo de notificación
    notification_type: str = "none"  # smtp, sendgrid, none
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"


settings = Settings()