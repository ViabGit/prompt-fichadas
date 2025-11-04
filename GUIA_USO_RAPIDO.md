# 🚀 Guía de Uso Rápido - Sistema de Fichadas ZKTeco

## Acceso al Sistema

### URLs Principales
- **Frontend Web**: http://localhost:4200
- **API Backend**: http://localhost:8080
- **Documentación API**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/health

## 🎯 Primeros Pasos

### 1. Verificar Estado del Sistema

```powershell
# Ver contenedores corriendo
docker ps

# Ver logs del backend
docker logs fichadas-backend --tail 50

# Ver logs del scheduler
docker logs fichadas-backend | Select-String -Pattern "scheduler"

# Verificar health
curl http://localhost:8080/health
```

### 2. Acceder al Frontend Web
Abrir navegador en: http://localhost:4200

## 📊 Dashboard - Vista Principal

### Estadísticas que muestra:
- Total dispositivos registrados
- Dispositivos online
- Fichadas recolectadas hoy
- Errores últimas 24 horas

### Actualización automática:
- Cada 30 segundos se refrescan los datos automáticamente

## 🔌 Gestión de Dispositivos

### Ver todos los dispositivos:
1. Click en tab "🔌 Dispositivos"
2. Tabla muestra: Nombre, IP, Modelo, Estado, Última consulta

### Agregar nuevo dispositivo:
1. Click en botón "➕ Agregar Dispositivo"
2. Completar formulario:
   - Nombre del dispositivo (requerido)
   - IP del dispositivo (requerido)
   - Puerto (default: 4370)
   - Modelo (ej: ZK-F22)
   - Marca (default: ZK)
   - Número de dispositivo
   - Marcar "Activo"
3. Click en "💾 Guardar Dispositivo"

### Probar conexión de un dispositivo:
1. En tabla de dispositivos, click "🔍 Test"
2. Ver resultado en popup

### Descargar fichadas manualmente:
1. En tabla de dispositivos, click "📥 Descargar"
2. Ver resultado con cantidad de fichadas descargadas

### Eliminar dispositivo:
1. En tabla de dispositivos, click "🗑️"
2. Confirmar eliminación

## ⏰ Control del Scheduler

### Ver estado del scheduler:
1. Click en tab "⏰ Scheduler"
2. Ver indicador circular:
   - Verde pulsante = Ejecutándose
   - Gris = Detenido
3. Ver próxima ejecución programada

### Iniciar scheduler automático:
1. Si está detenido, click "▶️ Iniciar Scheduler"
2. Confirmación en popup
3. El scheduler ejecutará cada X minutos según configuración

### Detener scheduler:
1. Si está corriendo, click "⏸️ Detener Scheduler"
2. Confirmación en popup
3. No se ejecutarán más recolecciones automáticas

### Ejecutar recolección manual inmediata:
1. Click en "🔄 Recolectar Ahora (Manual)"
2. Confirmar acción
3. Ver resultado con dispositivos exitosos/fallidos
4. Esta acción NO afecta el scheduler automático

### Ver historial de ejecuciones:
- Scroll down en tab Scheduler
- Tabla muestra últimas 20 ejecuciones
- Columnas: Fecha, Nivel (INFO/WARNING/ERROR), Mensaje

## ⚙️ Configuración del Sistema

### Configuración General:
1. Click en tab "⚙️ Configuración"
2. Modificar valores:
   - **Carpeta de Salida**: Donde se guardan fichadas (ej: /data/fichadas)
   - **Carpeta de Backup**: Donde se guardan backups (ej: /data/backup)
   - **Frecuencia**: Minutos entre recolecciones (1-1440)
   - **Inicio Automático**: Si scheduler arranca al iniciar sistema
   - **Máximo Reintentos**: Intentos ante fallo de conexión
3. Click "💾 Guardar Configuración"

### Configurar Notificaciones por Email (SMTP):
1. En selector "Tipo de Notificación", elegir "SMTP (Email)"
2. Completar campos que aparecen:
   - Servidor SMTP (ej: smtp.gmail.com)
   - Puerto (ej: 587)
   - Usuario (tu email)
   - Password (contraseña de aplicación)
   - Email Desde (remitente)
   - Email Para (destinatario que recibe alertas)
   - Marcar "Usar TLS" (recomendado)
3. Click "💾 Guardar Configuración"

### Configurar Notificaciones por SendGrid:
1. En selector "Tipo de Notificación", elegir "SendGrid"
2. Completar:
   - API Key de SendGrid
   - Email Desde (verificado en SendGrid)
   - Email Para (destinatario)
3. Click "💾 Guardar Configuración"

### Desactivar notificaciones:
1. En selector "Tipo de Notificación", elegir "Sin notificaciones"
2. Click "💾 Guardar Configuración"

## 📋 Visualización de Logs

### Ver logs del sistema:
1. Click en tab "📋 Logs"
2. Tabla muestra últimos 50 logs

### Filtrar logs por nivel:
1. Selector "Filtrar por nivel"
2. Opciones: Todos, INFO, WARNING, ERROR
3. Al cambiar selección, se actualiza automáticamente

### Filtrar logs por componente:
1. Selector "Filtrar por componente"
2. Opciones: Todos, Recolector, Scheduler, API, Notificaciones
3. Al cambiar selección, se actualiza automáticamente

### Actualizar logs manualmente:
1. Click en botón "🔄 Actualizar"

## 🔧 Operaciones por Terminal (Alternativa)

### Gestión de contenedores:
```powershell
# Iniciar todos los servicios
docker-compose up -d

# Detener todos los servicios
docker-compose down

# Reiniciar un servicio específico
docker-compose restart backend
docker-compose restart frontend

# Ver logs en tiempo real
docker-compose logs -f backend
docker-compose logs -f frontend

# Reconstruir un contenedor
docker-compose build backend
docker-compose up -d backend
```

### Acceder a base de datos:
```powershell
# Conectar a PostgreSQL
docker exec -it fichadas-db psql -U fichadas_user -d fichadas_db

# Dentro de PostgreSQL:
\dt                 # Listar tablas
SELECT * FROM dispositivos;
SELECT * FROM fichadas LIMIT 10;
SELECT * FROM configuracion;
\q                  # Salir
```

### Ver fichadas descargadas:
```powershell
# Ver contenido de carpeta de salida
docker exec fichadas-backend ls -l /data/fichadas

# Ver contenido de un archivo específico
docker exec fichadas-backend cat /data/fichadas/Oficina_Principal_20231103.csv
```

## 🐛 Solución de Problemas

### Frontend no carga:
```powershell
# Verificar que contenedor está corriendo
docker ps | Select-String "frontend"

# Ver logs del frontend
docker logs fichadas-frontend

# Reiniciar frontend
docker-compose restart frontend
```

### Backend no responde:
```powershell
# Verificar health
curl http://localhost:8080/health

# Ver logs del backend
docker logs fichadas-backend --tail 100

# Reiniciar backend
docker-compose restart backend
```

### Scheduler no ejecuta:
1. Ir a tab "⏰ Scheduler" en frontend
2. Verificar que indicador está verde
3. Si está gris, click "▶️ Iniciar Scheduler"
4. Verificar en logs de ejecución que no hay errores

### Dispositivo no se conecta:
1. Verificar que IP y puerto son correctos
2. Usar botón "🔍 Test" en tabla de dispositivos
3. Verificar que dispositivo está encendido y en red
4. Revisar firewall del dispositivo ZKTeco
5. Verificar que puerto 4370 está abierto

### No llegan notificaciones:
1. Ir a tab "⚙️ Configuración"
2. Verificar que tipo de notificación no es "Sin notificaciones"
3. Verificar que credenciales SMTP/SendGrid son correctas
4. Para Gmail: Usar contraseña de aplicación, no password normal
5. Verificar en logs que no hay errores de envío

## 📈 Mejores Prácticas

### Frecuencia de Recolección:
- **Oficinas**: 15-30 minutos es óptimo
- **Fábricas con muchos empleados**: 5-10 minutos
- **Lugares remotos con conexión lenta**: 60 minutos

### Monitoreo Regular:
- Revisar Dashboard diariamente
- Verificar logs de errores semanalmente
- Probar conexiones de dispositivos mensualmente

### Backups:
- Configurar carpeta de backup diferente a salida
- Hacer backup de base de datos periódicamente:
```powershell
docker exec fichadas-db pg_dump -U fichadas_user fichadas_db > backup_$(Get-Date -Format 'yyyyMMdd').sql
```

### Mantenimiento:
```powershell
# Limpiar logs antiguos (si crecen mucho)
docker exec -it fichadas-db psql -U fichadas_user -d fichadas_db -c "DELETE FROM logs WHERE created_at < NOW() - INTERVAL '30 days';"

# Ver espacio usado por contenedores
docker system df
```

## 🎯 Casos de Uso Comunes

### Caso 1: Agregar nuevo dispositivo y probarlo
1. Tab "🔌 Dispositivos"
2. "➕ Agregar Dispositivo"
3. Completar: Nombre="Oficina Central", IP="192.168.1.100", Puerto=4370
4. Guardar
5. Click "🔍 Test" en el nuevo dispositivo
6. Si test exitoso, dispositivo listo

### Caso 2: Configurar recolección automática cada 15 minutos
1. Tab "⚙️ Configuración"
2. Cambiar "Frecuencia de Recolección" a 15
3. Marcar "Inicio Automático"
4. Guardar
5. Tab "⏰ Scheduler"
6. "▶️ Iniciar Scheduler"

### Caso 3: Descargar fichadas de todos los dispositivos ahora
1. Tab "⏰ Scheduler"
2. "🔄 Recolectar Ahora (Manual)"
3. Confirmar
4. Ver resultado en popup

### Caso 4: Revisar errores del día
1. Tab "📋 Logs"
2. Filtro "Nivel" = ERROR
3. Revisar tabla de errores

---

**¡Sistema listo para usar! 🎉**

Para soporte adicional, consultar:
- FRONTEND_MEJORADO.md - Detalles de funcionalidades
- README.md - Documentación completa del sistema
- /docs en el navegador - Documentación interactiva de la API