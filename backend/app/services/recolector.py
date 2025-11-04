from pyzk2 import ZK
from datetime import datetime, timedelta
import os
import shutil
from typing import List, Optional, Tuple
import logging
from sqlalchemy.orm import Session
from ..models.dispositivo import Dispositivo, LogSistema
from ..schemas.dispositivo import TestConexionResponse, DescargaManualResponse
from ..config import settings
import time

logger = logging.getLogger(__name__)


class RecolectorService:
    def __init__(self):
        self.conn = None
        self.zk = None
    
    def conectar_dispositivo(self, ip: str, puerto: int = 4370, timeout: int = 5) -> Tuple[bool, Optional[str]]:
        """
        Establece conexión con dispositivo ZK
        Returns: (success, error_message)
        """
        try:
            self.zk = ZK(ip, port=puerto, timeout=timeout, password=0, force_udp=False)
            self.conn = self.zk.connect()
            return True, None
        except Exception as e:
            error_msg = f"Error conectando a {ip}:{puerto} - {str(e)}"
            logger.error(error_msg)
            self.desconectar()
            return False, error_msg
    
    def desconectar(self):
        """Cierra la conexión si existe"""
        try:
            if self.conn:
                self.conn.disconnect()
        except Exception as e:
            logger.warning(f"Error al desconectar: {str(e)}")
        finally:
            self.conn = None
            self.zk = None
    
    def test_conexion(self, ip: str, puerto: int = 4370) -> TestConexionResponse:
        """Prueba la conexión a un dispositivo y mide tiempo de respuesta"""
        start_time = time.time()
        
        try:
            success, error_msg = self.conectar_dispositivo(ip, puerto, timeout=10)
            response_time = time.time() - start_time
            
            if success:
                # Obtener información básica del dispositivo
                try:
                    users_count = len(self.conn.get_users())
                    device_info = f"Dispositivo conectado. Usuarios registrados: {users_count}"
                    self.desconectar()
                    
                    return TestConexionResponse(
                        success=True,
                        mensaje=device_info,
                        tiempo_respuesta=response_time
                    )
                except Exception as e:
                    self.desconectar()
                    return TestConexionResponse(
                        success=True,
                        mensaje="Conexión exitosa pero no se pudo obtener información detallada",
                        tiempo_respuesta=response_time,
                        error_detalle=str(e)
                    )
            else:
                return TestConexionResponse(
                    success=False,
                    mensaje="Fallo en la conexión",
                    tiempo_respuesta=response_time,
                    error_detalle=error_msg
                )
                
        except Exception as e:
            response_time = time.time() - start_time
            return TestConexionResponse(
                success=False,
                mensaje="Error inesperado al probar conexión",
                tiempo_respuesta=response_time,
                error_detalle=str(e)
            )
    
    def descargar_fichadas(self, dispositivo: Dispositivo, solo_nuevas: bool = True) -> List:
        """
        Descarga fichadas del dispositivo
        si solo_nuevas=True, filtra por fecha_ultima_consulta
        """
        try:
            success, error_msg = self.conectar_dispositivo(dispositivo.ip, dispositivo.puerto)
            if not success:
                raise Exception(error_msg)
            
            # Obtener todas las fichadas
            fichadas = self.conn.get_attendance()
            logger.info(f"Descargadas {len(fichadas)} fichadas de dispositivo {dispositivo.nombre}")
            
            # Filtrar solo fichadas nuevas si es necesario
            if solo_nuevas and dispositivo.fecha_ultima_consulta:
                fichadas_filtradas = self.filtrar_fichadas_nuevas(
                    fichadas, 
                    dispositivo.fecha_ultima_consulta
                )
                logger.info(f"Filtradas {len(fichadas_filtradas)} fichadas nuevas")
                return fichadas_filtradas
            
            return fichadas
            
        except Exception as e:
            logger.error(f"Error descargando fichadas de {dispositivo.nombre}: {str(e)}")
            raise
        finally:
            self.desconectar()
    
    def procesar_fichadas(self, fichadas: List, numero_dispositivo: str, codigo_adicional: str = "00") -> str:
        """
        Procesa fichadas y genera formato de salida
        Formato: ID_Usuario DD/MM/YYYY HH:MM Numero_Dispositivo Codigo_Adicional
        """
        if not fichadas:
            return ""
        
        lineas = []
        for fichada in fichadas:
            try:
                # Formato: ID_Usuario DD/MM/YYYY HH:MM Numero_Dispositivo Codigo_Adicional
                fecha = fichada.timestamp.strftime("%d/%m/%Y")
                hora = fichada.timestamp.strftime("%H:%M")
                linea = f"{fichada.user_id} {fecha} {hora} {numero_dispositivo} {codigo_adicional}"
                lineas.append(linea)
            except Exception as e:
                logger.warning(f"Error procesando fichada: {str(e)}")
                continue
        
        return "\n".join(lineas)
    
    def guardar_fichadas(self, contenido: str, carpeta: str, nombre_archivo: str) -> str:
        """Guarda fichadas en archivo txt"""
        if not contenido.strip():
            logger.info("No hay contenido para guardar")
            return ""
        
        try:
            os.makedirs(carpeta, exist_ok=True)
            archivo_path = os.path.join(carpeta, f"{nombre_archivo}.txt")
            
            # Si el archivo existe, agregar al final
            mode = 'a' if os.path.exists(archivo_path) else 'w'
            
            with open(archivo_path, mode, encoding='utf-8') as f:
                if mode == 'a':
                    f.write('\n')  # Nueva línea si agregamos al final
                f.write(contenido)
            
            logger.info(f"Fichadas guardadas en {archivo_path}")
            return archivo_path
            
        except Exception as e:
            logger.error(f"Error guardando fichadas: {str(e)}")
            raise
    
    def crear_backup(self, archivo_original: str, carpeta_backup: str) -> Optional[str]:
        """Crea backup con timestamp"""
        if not os.path.exists(archivo_original):
            logger.warning(f"Archivo original no existe: {archivo_original}")
            return None
        
        try:
            os.makedirs(carpeta_backup, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_base = os.path.basename(archivo_original)
            nombre_sin_ext = os.path.splitext(nombre_base)[0]
            
            archivo_backup = os.path.join(
                carpeta_backup, 
                f"{nombre_sin_ext}_backup_{timestamp}.txt"
            )
            
            shutil.copy2(archivo_original, archivo_backup)
            logger.info(f"Backup creado: {archivo_backup}")
            return archivo_backup
            
        except Exception as e:
            logger.error(f"Error creando backup: {str(e)}")
            return None
    
    def filtrar_fichadas_nuevas(self, fichadas: List, ultima_fecha: datetime) -> List:
        """Filtra solo fichadas posteriores a ultima_fecha"""
        if not ultima_fecha:
            return fichadas
        
        # Usar zona horaria de Buenos Aires
        import pytz
        buenos_aires_tz = pytz.timezone('America/Argentina/Buenos_Aires')
        
        # Asegurar que ultima_fecha tenga timezone
        if ultima_fecha.tzinfo is None:
            ultima_fecha = buenos_aires_tz.localize(ultima_fecha)
        else:
            ultima_fecha = ultima_fecha.astimezone(buenos_aires_tz)
        
        fichadas_nuevas = []
        for f in fichadas:
            # Asegurar que el timestamp de la fichada tenga timezone
            timestamp = f.timestamp
            if timestamp.tzinfo is None:
                timestamp = buenos_aires_tz.localize(timestamp)
            else:
                timestamp = timestamp.astimezone(buenos_aires_tz)
            
            if timestamp > ultima_fecha:
                fichadas_nuevas.append(f)
        
        logger.info(f"Filtradas {len(fichadas_nuevas)} fichadas posteriores a {ultima_fecha}")
        return fichadas_nuevas
    
    def procesar_dispositivo_completo(
        self, 
        dispositivo: Dispositivo, 
        db: Session,
        forzar_descarga: bool = False
    ) -> DescargaManualResponse:
        """
        Proceso completo para un dispositivo:
        1. Conectar
        2. Descargar fichadas
        3. Procesar y guardar
        4. Crear backup
        5. Actualizar base de datos
        """
        try:
            # Descargar fichadas (solo nuevas si forzar_descarga=False)
            fichadas = self.descargar_fichadas(dispositivo, solo_nuevas=not forzar_descarga)
            
            if not fichadas:
                # Actualizar fecha de consulta aunque no haya fichadas nuevas
                dispositivo.fecha_ultima_consulta = datetime.now()
                dispositivo.estado_conexion = "online"
                dispositivo.intentos_fallidos = 0
                db.commit()
                
                return DescargaManualResponse(
                    success=True,
                    mensaje="Conexión exitosa, no hay fichadas nuevas",
                    fichadas_descargadas=0
                )
            
            # Procesar fichadas
            contenido = self.procesar_fichadas(fichadas, dispositivo.numero_dispositivo)
            
            if not contenido:
                return DescargaManualResponse(
                    success=True,
                    mensaje="No se generó contenido válido",
                    fichadas_descargadas=len(fichadas)
                )
            
            # Guardar fichadas
            archivo_path = self.guardar_fichadas(
                contenido,
                settings.carpeta_salida, 
                dispositivo.numero_dispositivo
            )
            
            # Crear backup si se generó archivo
            if archivo_path:
                self.crear_backup(archivo_path, settings.carpeta_backup)
            
            # Actualizar dispositivo en base de datos
            dispositivo.fecha_ultima_consulta = datetime.now()
            dispositivo.estado_conexion = "online"
            dispositivo.intentos_fallidos = 0
            dispositivo.alertas_activas = False
            db.commit()
            
            # Log de éxito
            log_entry = LogSistema(
                nivel="INFO",
                mensaje=f"Descarga exitosa: {len(fichadas)} fichadas",
                dispositivo_id=dispositivo.id,
                componente="recolector"
            )
            db.add(log_entry)
            db.commit()
            
            return DescargaManualResponse(
                success=True,
                mensaje=f"Descarga exitosa de {len(fichadas)} fichadas",
                fichadas_descargadas=len(fichadas),
                archivo_generado=archivo_path
            )
            
        except Exception as e:
            error_msg = f"Error procesando dispositivo {dispositivo.nombre}: {str(e)}"
            logger.error(error_msg)
            
            # Actualizar estado de error
            dispositivo.intentos_fallidos += 1
            dispositivo.estado_conexion = "error"
            if dispositivo.intentos_fallidos >= settings.max_reintentos:
                dispositivo.alertas_activas = True
            db.commit()
            
            # Log de error
            log_entry = LogSistema(
                nivel="ERROR",
                mensaje=error_msg,
                dispositivo_id=dispositivo.id,
                componente="recolector",
                detalles=str(e)
            )
            db.add(log_entry)
            db.commit()
            
            return DescargaManualResponse(
                success=False,
                mensaje=f"Error en descarga: {str(e)}",
                fichadas_descargadas=0,
                error_detalle=str(e)
            )