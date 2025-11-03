"""
Script para migrar dispositivos desde TACollector.config.json al nuevo sistema
"""
import json
import sys
import os
from datetime import datetime

# Agregar el directorio del proyecto al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import SessionLocal, init_db
from app.models.dispositivo import Dispositivo, ConfiguracionGlobal


def migrar_configuracion():
    """Migra la configuración desde TACollector.config.json"""
    
    # Ruta al archivo de configuración original
    config_path = "d:/Downloads/tacollector/Output/TACollector.config.json"
    
    if not os.path.exists(config_path):
        print(f"ERROR: No se encontró el archivo {config_path}")
        return False
    
    try:
        # Leer configuración original
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        print(f"Configuración cargada: {len(config_data['Dispositivos'])} dispositivos")
        
        # Inicializar base de datos
        init_db()
        db = SessionLocal()
        
        try:
            # Crear configuración global si no existe
            config_global = db.query(ConfiguracionGlobal).first()
            if not config_global:
                config_global = ConfiguracionGlobal(
                    carpeta_salida=config_data.get('Carpeta', '/data/fichadas/'),
                    frecuencia_minutos=config_data.get('FrecuenciaMinutos', 5),
                    inicio_automatico=config_data.get('InicioAutomatico', True)
                )
                db.add(config_global)
                print("✓ Configuración global creada")
            
            # Migrar dispositivos
            dispositivos_migrados = 0
            dispositivos_actualizados = 0
            
            for dispositivo_data in config_data['Dispositivos']:
                # Verificar si ya existe
                dispositivo_existente = db.query(Dispositivo).filter(
                    Dispositivo.id == dispositivo_data['Id']
                ).first()
                
                if dispositivo_existente:
                    # Actualizar dispositivo existente
                    dispositivo_existente.nombre = dispositivo_data['Nombre']
                    dispositivo_existente.ip = dispositivo_data['IP']
                    dispositivo_existente.puerto = dispositivo_data['Puerto']
                    dispositivo_existente.modelo = dispositivo_data['Modelo']
                    dispositivo_existente.marca = dispositivo_data['Marca']
                    dispositivo_existente.activo = dispositivo_data['Activo']
                    dispositivo_existente.numero_dispositivo = dispositivo_data['NombreArchivo']
                    
                    # Convertir fecha si existe
                    if 'FechaHoraBaseConsulta' in dispositivo_data:
                        try:
                            fecha_consulta = datetime.fromisoformat(
                                dispositivo_data['FechaHoraBaseConsulta'].replace('T', ' ')
                            )
                            dispositivo_existente.fecha_ultima_consulta = fecha_consulta
                        except:
                            pass
                    
                    dispositivos_actualizados += 1
                    print(f"✓ Actualizado: {dispositivo_data['Nombre']}")
                    
                else:
                    # Crear nuevo dispositivo
                    nuevo_dispositivo = Dispositivo(
                        id=dispositivo_data['Id'],
                        nombre=dispositivo_data['Nombre'],
                        ip=dispositivo_data['IP'],
                        puerto=dispositivo_data['Puerto'],
                        modelo=dispositivo_data['Modelo'],
                        marca=dispositivo_data['Marca'],
                        activo=dispositivo_data['Activo'],
                        numero_dispositivo=dispositivo_data['NombreArchivo'],
                        estado_conexion="offline"
                    )
                    
                    # Convertir fecha si existe
                    if 'FechaHoraBaseConsulta' in dispositivo_data:
                        try:
                            fecha_consulta = datetime.fromisoformat(
                                dispositivo_data['FechaHoraBaseConsulta'].replace('T', ' ')
                            )
                            nuevo_dispositivo.fecha_ultima_consulta = fecha_consulta
                        except:
                            pass
                    
                    db.add(nuevo_dispositivo)
                    dispositivos_migrados += 1
                    print(f"✓ Creado: {dispositivo_data['Nombre']}")
            
            # Commit cambios
            db.commit()
            
            print(f"\n=== MIGRACIÓN COMPLETADA ===")
            print(f"Dispositivos creados: {dispositivos_migrados}")
            print(f"Dispositivos actualizados: {dispositivos_actualizados}")
            print(f"Total procesados: {dispositivos_migrados + dispositivos_actualizados}")
            
            return True
            
        except Exception as e:
            db.rollback()
            print(f"ERROR en base de datos: {str(e)}")
            return False
        finally:
            db.close()
            
    except Exception as e:
        print(f"ERROR leyendo configuración: {str(e)}")
        return False


def listar_dispositivos():
    """Lista todos los dispositivos en la base de datos"""
    try:
        db = SessionLocal()
        dispositivos = db.query(Dispositivo).all()
        
        print(f"\n=== DISPOSITIVOS EN BASE DE DATOS ({len(dispositivos)}) ===")
        for d in dispositivos:
            estado_icon = "🟢" if d.estado_conexion == "online" else "🔴" if d.estado_conexion == "error" else "⚪"
            activo_icon = "✓" if d.activo else "✗"
            print(f"{estado_icon} {d.id:2} | {d.nombre:20} | {d.ip:15} | {d.numero_dispositivo:6} | Activo: {activo_icon}")
        
        db.close()
        
    except Exception as e:
        print(f"ERROR listando dispositivos: {str(e)}")


if __name__ == "__main__":
    print("=== MIGRADOR DE CONFIGURACIÓN ZKTeco ===")
    print("Este script migra dispositivos desde TACollector.config.json")
    
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        listar_dispositivos()
    else:
        # Confirmar migración
        respuesta = input("\n¿Proceder con la migración? (s/N): ").lower().strip()
        
        if respuesta in ['s', 'si', 'y', 'yes']:
            if migrar_configuracion():
                print("\n¡Migración exitosa!")
                listar_dispositivos()
            else:
                print("\n❌ Error en la migración")
                sys.exit(1)
        else:
            print("Migración cancelada")