import smtplib
import sendgrid
from sendgrid.helpers.mail import Mail
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models.dispositivo import ConfiguracionGlobal
from ..config import settings
import logging
import json

logger = logging.getLogger(__name__)


class NotificacionService:
    def __init__(self):
        pass
    
    async def enviar_notificacion(self, asunto: str, mensaje: str) -> bool:
        """
        Envía notificación usando la configuración disponible
        Retorna True si se envió exitosamente
        """
        db = SessionLocal()
        try:
            config = db.query(ConfiguracionGlobal).first()
            
            if not config or config.tipo_notificacion == "none":
                logger.info("Notificaciones deshabilitadas")
                return True
            
            if config.tipo_notificacion == "smtp":
                return await self._enviar_smtp(config, asunto, mensaje)
            elif config.tipo_notificacion == "sendgrid":
                return await self._enviar_sendgrid(config, asunto, mensaje)
            else:
                logger.warning(f"Tipo de notificación no soportado: {config.tipo_notificacion}")
                return False
                
        except Exception as e:
            logger.error(f"Error enviando notificación: {str(e)}")
            return False
        finally:
            db.close()
    
    async def _enviar_smtp(self, config: ConfiguracionGlobal, asunto: str, mensaje: str) -> bool:
        """Envía email usando SMTP"""
        try:
            if not all([config.smtp_servidor, config.smtp_usuario, config.smtp_password, 
                       config.smtp_desde, config.smtp_para]):
                logger.error("Configuración SMTP incompleta")
                return False
            
            # Parsear lista de destinatarios
            destinatarios = json.loads(config.smtp_para) if isinstance(config.smtp_para, str) else config.smtp_para
            
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = config.smtp_desde
            msg['To'] = ', '.join(destinatarios)
            msg['Subject'] = asunto
            
            # Agregar cuerpo del mensaje
            msg.attach(MIMEText(mensaje, 'plain', 'utf-8'))
            
            # Enviar email
            with smtplib.SMTP(config.smtp_servidor, config.smtp_puerto) as server:
                if config.smtp_usar_tls:
                    server.starttls()
                server.login(config.smtp_usuario, config.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email enviado exitosamente a {len(destinatarios)} destinatarios")
            return True
            
        except json.JSONDecodeError:
            logger.error("Error parseando lista de destinatarios SMTP")
            return False
        except Exception as e:
            logger.error(f"Error enviando email SMTP: {str(e)}")
            return False
    
    async def _enviar_sendgrid(self, config: ConfiguracionGlobal, asunto: str, mensaje: str) -> bool:
        """Envía email usando SendGrid"""
        try:
            if not all([config.sendgrid_api_key, config.sendgrid_desde, config.sendgrid_para]):
                logger.error("Configuración SendGrid incompleta")
                return False
            
            # Parsear lista de destinatarios
            destinatarios = json.loads(config.sendgrid_para) if isinstance(config.sendgrid_para, str) else config.sendgrid_para
            
            # Crear cliente SendGrid
            sg = sendgrid.SendGridAPIClient(api_key=config.sendgrid_api_key)
            
            # Enviar a cada destinatario
            for destinatario in destinatarios:
                mail = Mail(
                    from_email=config.sendgrid_desde,
                    to_emails=destinatario,
                    subject=asunto,
                    plain_text_content=mensaje
                )
                
                response = sg.send(mail)
                
                if response.status_code not in [200, 201, 202]:
                    logger.warning(f"SendGrid respondió con código {response.status_code} para {destinatario}")
            
            logger.info(f"Emails enviados via SendGrid a {len(destinatarios)} destinatarios")
            return True
            
        except json.JSONDecodeError:
            logger.error("Error parseando lista de destinatarios SendGrid")
            return False
        except Exception as e:
            logger.error(f"Error enviando email SendGrid: {str(e)}")
            return False
    
    async def test_configuracion(self, tipo: str, config_data: dict) -> dict:
        """
        Prueba la configuración de notificaciones
        Retorna dict con success y mensaje
        """
        try:
            asunto_test = "Test - Sistema de Fichadas"
            mensaje_test = "Este es un mensaje de prueba del sistema de fichadas ZKTeco."
            
            if tipo == "smtp":
                success = await self._test_smtp(config_data, asunto_test, mensaje_test)
            elif tipo == "sendgrid":
                success = await self._test_sendgrid(config_data, asunto_test, mensaje_test)
            else:
                return {"success": False, "mensaje": "Tipo de notificación no soportado"}
            
            if success:
                return {"success": True, "mensaje": "Configuración probada exitosamente"}
            else:
                return {"success": False, "mensaje": "Error en la configuración"}
                
        except Exception as e:
            return {"success": False, "mensaje": f"Error probando configuración: {str(e)}"}
    
    async def _test_smtp(self, config: dict, asunto: str, mensaje: str) -> bool:
        """Prueba configuración SMTP"""
        try:
            msg = MIMEMultipart()
            msg['From'] = config['desde']
            msg['To'] = config['para'][0] if config['para'] else 'test@test.com'
            msg['Subject'] = asunto
            msg.attach(MIMEText(mensaje, 'plain', 'utf-8'))
            
            with smtplib.SMTP(config['servidor'], config['puerto']) as server:
                if config.get('usar_tls', True):
                    server.starttls()
                server.login(config['usuario'], config['password'])
                server.send_message(msg)
            
            return True
        except Exception as e:
            logger.error(f"Error en test SMTP: {str(e)}")
            return False
    
    async def _test_sendgrid(self, config: dict, asunto: str, mensaje: str) -> bool:
        """Prueba configuración SendGrid"""
        try:
            sg = sendgrid.SendGridAPIClient(api_key=config['api_key'])
            
            mail = Mail(
                from_email=config['desde'],
                to_emails=config['para'][0] if config['para'] else 'test@test.com',
                subject=asunto,
                plain_text_content=mensaje
            )
            
            response = sg.send(mail)
            return response.status_code in [200, 201, 202]
            
        except Exception as e:
            logger.error(f"Error en test SendGrid: {str(e)}")
            return False