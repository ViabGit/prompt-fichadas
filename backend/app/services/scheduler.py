from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models.dispositivo import Dispositivo, ConfiguracionGlobal
from .recolector import RecolectorService
from .notificacion import NotificacionService
import logging
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.recolector = RecolectorService()
        self.notificacion = NotificacionService()
        self.running = False
    
    def start(self):
        """Inicia el scheduler si la configuración lo permite"""
        try:
            db = SessionLocal()
            config = db.query(ConfiguracionGlobal).first()
            db.close()
            
            if config and config.inicio_automatico:
                # Configurar job con la frecuencia especificada
                self.scheduler.add_job(
                    self.ejecutar_recoleccion,
                    trigger=IntervalTrigger(minutes=config.frecuencia_minutos),
                    id='recoleccion_fichadas',
                    name='Recolección de Fichadas Automática',
                    replace_existing=True
                )
                
                self.scheduler.start()
                self.running = True
                logger.info(f"Scheduler iniciado con frecuencia de {config.frecuencia_minutos} minutos")
            else:
                logger.info("Scheduler no iniciado - inicio automático deshabilitado")
                
        except Exception as e:
            logger.error(f"Error iniciando scheduler: {str(e)}")
    
    def stop(self):
        """Detiene el scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                self.running = False
                logger.info("Scheduler detenido")
        except Exception as e:
            logger.error(f"Error deteniendo scheduler: {str(e)}")
    
    def restart(self):
        """Reinicia el scheduler con nueva configuración"""
        self.stop()
        self.start()
    
    async def ejecutar_recoleccion(self):
        """Ejecuta la recolección para todos los dispositivos activos"""
        start_time = datetime.now()
        logger.info("Iniciando recolección automática de fichadas")
        
        db = SessionLocal()
        try:
            # Obtener dispositivos activos
            dispositivos = db.query(Dispositivo).filter(Dispositivo.activo == True).all()
            
            if not dispositivos:
                logger.info("No hay dispositivos activos para procesar")
                return
            
            # Procesar cada dispositivo
            dispositivos_exitosos = 0
            dispositivos_error = 0
            total_fichadas = 0
            
            for dispositivo in dispositivos:
                try:
                    logger.info(f"Procesando dispositivo: {dispositivo.nombre}")
                    
                    resultado = self.recolector.procesar_dispositivo_completo(
                        dispositivo, db, forzar_descarga=False
                    )
                    
                    if resultado.success:
                        dispositivos_exitosos += 1
                        total_fichadas += resultado.fichadas_descargadas
                        logger.info(f"✓ {dispositivo.nombre}: {resultado.fichadas_descargadas} fichadas")
                    else:
                        dispositivos_error += 1
                        logger.warning(f"✗ {dispositivo.nombre}: {resultado.mensaje}")
                        
                        # Verificar si necesita enviar alerta
                        if dispositivo.intentos_fallidos >= 3:
                            await self.enviar_alerta_dispositivo(dispositivo)
                    
                except Exception as e:
                    dispositivos_error += 1
                    logger.error(f"Error procesando {dispositivo.nombre}: {str(e)}")
            
            # Log resumen
            duration = (datetime.now() - start_time).total_seconds()
            resumen = (f"Recolección completada en {duration:.2f}s - "
                      f"Exitosos: {dispositivos_exitosos}, "
                      f"Errores: {dispositivos_error}, "
                      f"Total fichadas: {total_fichadas}")
            
            logger.info(resumen)
            
            # Enviar resumen diario si corresponde
            if start_time.hour == 18 and start_time.minute < 10:  # Resumen a las 6 PM
                await self.enviar_resumen_diario(dispositivos_exitosos, dispositivos_error, total_fichadas)
                
        except Exception as e:
            logger.error(f"Error en recolección automática: {str(e)}")
        finally:
            db.close()
    
    async def enviar_alerta_dispositivo(self, dispositivo: Dispositivo):
        """Envía alerta cuando un dispositivo falla repetidamente"""
        try:
            asunto = f"Alerta: Dispositivo {dispositivo.nombre} no responde"
            mensaje = (f"El dispositivo {dispositivo.nombre} ({dispositivo.ip}) "
                      f"ha fallado {dispositivo.intentos_fallidos} veces consecutivas.\n\n"
                      f"Última consulta exitosa: {dispositivo.fecha_ultima_consulta}\n"
                      f"Estado actual: {dispositivo.estado_conexion}")
            
            await self.notificacion.enviar_notificacion(asunto, mensaje)
            logger.info(f"Alerta enviada para dispositivo {dispositivo.nombre}")
            
        except Exception as e:
            logger.error(f"Error enviando alerta para {dispositivo.nombre}: {str(e)}")
    
    async def enviar_resumen_diario(self, exitosos: int, errores: int, total_fichadas: int):
        """Envía resumen diario del sistema"""
        try:
            asunto = "Resumen diario - Sistema de Fichadas"
            mensaje = (f"Resumen del día {datetime.now().strftime('%d/%m/%Y')}:\n\n"
                      f"• Dispositivos exitosos: {exitosos}\n"
                      f"• Dispositivos con error: {errores}\n"
                      f"• Total fichadas procesadas: {total_fichadas}\n\n"
                      f"Revise el sistema en caso de errores persistentes.")
            
            await self.notificacion.enviar_notificacion(asunto, mensaje)
            logger.info("Resumen diario enviado")
            
        except Exception as e:
            logger.error(f"Error enviando resumen diario: {str(e)}")
    
    def get_status(self) -> dict:
        """Obtiene el estado actual del scheduler"""
        return {
            "running": self.running,
            "scheduler_running": self.scheduler.running if hasattr(self.scheduler, 'running') else False,
            "jobs": len(self.scheduler.get_jobs()) if self.scheduler else 0,
            "next_run": str(self.scheduler.get_jobs()[0].next_run_time) if self.scheduler.get_jobs() else None
        }


# Instancia global del scheduler
scheduler_service = SchedulerService()


def start_scheduler():
    """Función para iniciar el scheduler desde main.py"""
    scheduler_service.start()


def stop_scheduler():
    """Función para detener el scheduler"""
    scheduler_service.stop()


def restart_scheduler():
    """Función para reiniciar el scheduler"""
    scheduler_service.restart()


def get_scheduler_status():
    """Función para obtener estado del scheduler"""
    return scheduler_service.get_status()