from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text
from sqlalchemy.sql import func
from ..database import Base


class Dispositivo(Base):
    __tablename__ = "dispositivos"
    
    id = Column(String, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    ip = Column(String(15), nullable=False)
    puerto = Column(Integer, default=4370)
    modelo = Column(String(100))
    marca = Column(String(50), default="ZK")
    activo = Column(Boolean, default=True)
    numero_dispositivo = Column(String(50))  # NombreArchivo en el config original
    fecha_ultima_consulta = Column(DateTime(timezone=True), server_default=func.now())
    alertas_activas = Column(Boolean, default=False)
    intentos_fallidos = Column(Integer, default=0)
    estado_conexion = Column(String(20), default="offline")  # online, offline, error
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ConfiguracionGlobal(Base):
    __tablename__ = "configuracion_global"
    
    id = Column(Integer, primary_key=True, index=True)
    carpeta_salida = Column(String(500), default="/data/fichadas/")
    carpeta_backup = Column(String(500), default="/data/backup/")
    frecuencia_minutos = Column(Integer, default=5)
    inicio_automatico = Column(Boolean, default=True)
    max_reintentos = Column(Integer, default=3)
    
    # Configuración SMTP
    smtp_servidor = Column(String(255))
    smtp_puerto = Column(Integer, default=587)
    smtp_usuario = Column(String(255))
    smtp_password = Column(String(255))
    smtp_desde = Column(String(255))
    smtp_para = Column(Text)  # JSON array de emails
    smtp_usar_tls = Column(Boolean, default=True)
    
    # Configuración SendGrid
    sendgrid_api_key = Column(String(255))
    sendgrid_desde = Column(String(255))
    sendgrid_para = Column(Text)  # JSON array de emails
    
    # Tipo de notificación
    tipo_notificacion = Column(String(20), default="none")  # smtp, sendgrid, none
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class LogSistema(Base):
    __tablename__ = "logs_sistema"
    
    id = Column(Integer, primary_key=True, index=True)
    nivel = Column(String(20))  # INFO, WARNING, ERROR
    mensaje = Column(Text)
    dispositivo_id = Column(String, nullable=True)  # FK opcional
    componente = Column(String(100))  # scheduler, recolector, api, etc.
    detalles = Column(Text, nullable=True)  # JSON adicional
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())