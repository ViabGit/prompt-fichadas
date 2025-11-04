<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Fichadas ZKTeco</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
            text-align: center;
        }

        h1 {
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .subtitle {
            color: #666;
            font-size: 1.1em;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-5px);
        }

        .stat-label {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .stat-value {
            color: #667eea;
            font-size: 2.5em;
            font-weight: bold;
        }

        .actions {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }

        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }

        .btn:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }

        .section {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }

        .section h2 {
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }

        .device-list {
            display: grid;
            gap: 15px;
        }

        .device-item {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }

        .device-name {
            font-weight: bold;
            color: #333;
            font-size: 1.2em;
            margin-bottom: 10px;
        }

        .device-info {
            color: #666;
            font-size: 0.9em;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }

        .status {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
        }

        .status-active {
            background: #d4edda;
            color: #155724;
        }

        .status-error {
            background: #f8d7da;
            color: #721c24;
        }

        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
            font-size: 1.2em;
        }

        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #dc3545;
        }

        .last-update {
            text-align: center;
            color: white;
            margin-top: 20px;
            font-size: 0.9em;
        }

        footer {
            text-align: center;
            color: white;
            padding: 20px;
            margin-top: 40px;
        }

        .links {
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
        }

        .links a {
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            background: rgba(255,255,255,0.2);
            border-radius: 5px;
            transition: background 0.3s ease;
        }

        .links a:hover {
            background: rgba(255,255,255,0.3);
        }

        @media (max-width: 768px) {
            h1 {
                font-size: 1.8em;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .actions {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🕒 Sistema de Fichadas ZKTeco</h1>
            <p class="subtitle">Control y monitoreo de asistencia en tiempo real</p>
        </header>

        <div class="stats-grid" id="statsGrid">
            <div class="stat-card">
                <div class="stat-label">Dispositivos Activos</div>
                <div class="stat-value" id="dispositivosActivos">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Registros</div>
                <div class="stat-value" id="totalRegistros">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Registros Hoy</div>
                <div class="stat-value" id="registrosHoy">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Último Procesamiento</div>
                <div class="stat-value" style="font-size: 1.2em;" id="ultimoProceso">-</div>
            </div>
        </div>

        <div class="section">
            <h2>⚙️ Acciones Rápidas</h2>
            <div class="actions">
                <button class="btn" onclick="procesarFichadas()">▶️ Procesar Fichadas</button>
                <button class="btn" onclick="iniciarScheduler()">⏰ Iniciar Scheduler</button>
                <button class="btn" onclick="detenerScheduler()">⏸️ Detener Scheduler</button>
                <button class="btn" onclick="cargarDatos()">🔄 Actualizar</button>
            </div>
        </div>

        <div class="section">
            <h2>📱 Dispositivos Configurados</h2>
            <div id="deviceList" class="loading">
                Cargando dispositivos...
            </div>
        </div>

        <div class="last-update" id="lastUpdate">
            Última actualización: Cargando...
        </div>

        <footer>
            <div class="links">
                <a href="http://localhost:8081/docs" target="_blank">📚 API Docs</a>
                <a href="http://localhost:8081/health" target="_blank">❤️ Estado Backend</a>
                <a href="#" onclick="cargarDatos(); return false;">🔄 Recargar</a>
            </div>
            <p style="margin-top: 20px;">© 2024 Sistema de Fichadas ZKTeco - v1.0.0</p>
        </footer>
    </div>

    <script>
        const API_BASE = 'http://localhost:8081/api';

        // Cargar datos iniciales
        async function cargarDatos() {
            await Promise.all([
                cargarEstadisticas(),
                cargarDispositivos()
            ]);
            actualizarTimestamp();
        }

        async function cargarEstadisticas() {
            try {
                const response = await fetch(`${API_BASE}/monitoreo/estadisticas`);
                if (!response.ok) throw new Error('Error al cargar estadísticas');
                
                const data = await response.json();
                
                document.getElementById('dispositivosActivos').textContent = data.dispositivos_activos || 0;
                document.getElementById('totalRegistros').textContent = data.total_registros || 0;
                document.getElementById('registrosHoy').textContent = data.registros_hoy || 0;
                
                const ultimoProceso = data.ultimo_procesamiento ? 
                    new Date(data.ultimo_procesamiento).toLocaleTimeString('es-ES') : 
                    'Nunca';
                document.getElementById('ultimoProceso').textContent = ultimoProceso;
                
            } catch (error) {
                console.error('Error:', error);
                mostrarError('No se pudieron cargar las estadísticas');
            }
        }

    async function cargarDispositivos() {
        try {
            // Ruta correcta según backend: /api/dispositivos
            const response = await fetch(`${API_BASE}/dispositivos`);
                if (!response.ok) throw new Error('Error al cargar dispositivos');
                
                const dispositivos = await response.json();
                const container = document.getElementById('deviceList');
                
                if (!dispositivos || dispositivos.length === 0) {
                    container.innerHTML = '<p class="loading">No hay dispositivos configurados</p>';
                    return;
                }
                
                container.innerHTML = dispositivos.map(d => `
                    <div class="device-item">
                        <div class="device-name">
                            ${d.nombre || 'Sin nombre'}
                            <span class="status ${d.activo ? 'status-active' : 'status-error'}">
                                ${d.activo ? 'Activo' : 'Inactivo'}
                            </span>
                        </div>
                        <div class="device-info">
                            <div><strong>IP:</strong> ${d.ip || 'N/A'}</div>
                            <div><strong>Puerto:</strong> ${d.puerto || 4370}</div>
                            <div><strong>Ubicación:</strong> ${d.ubicacion || 'Sin ubicar'}</div>
                            <div><strong>ID:</strong> ${d.id}</div>
                        </div>
                    </div>
                `).join('');
                
        } catch (error) {
            console.error('Error:', error);
            document.getElementById('deviceList').innerHTML =
                '<div class="error-message">Error al cargar dispositivos</div>';
        }
    }

        async function procesarFichadas() {
            if (!confirm('¿Desea procesar las fichadas de todos los dispositivos?')) return;
            
            try {
                const btn = event.target;
                btn.disabled = true;
                btn.textContent = '⏳ Procesando...';
                
                const response = await fetch(`${API_BASE}/monitoreo/procesar`, {
                    method: 'POST'
                });
                
                if (!response.ok) throw new Error('Error al procesar fichadas');
                
                const result = await response.json();
                alert(`Procesamiento exitoso:\n${result.mensaje || 'Completado'}`);
                await cargarDatos();
                
            } catch (error) {
                console.error('Error:', error);
                alert('Error al procesar fichadas: ' + error.message);
            } finally {
                const btn = event.target;
                btn.disabled = false;
                btn.textContent = '▶️ Procesar Fichadas';
            }
        }

        async function iniciarScheduler() {
            try {
                const response = await fetch(`${API_BASE}/configuracion/scheduler/iniciar`, {
                    method: 'POST'
                });
                
                if (!response.ok) throw new Error('Error al iniciar scheduler');
                
                const result = await response.json();
                alert(result.mensaje || 'Scheduler iniciado');
                
            } catch (error) {
                console.error('Error:', error);
                alert('Error al iniciar scheduler: ' + error.message);
            }
        }

        async function detenerScheduler() {
            try {
                const response = await fetch(`${API_BASE}/configuracion/scheduler/detener`, {
                    method: 'POST'
                });
                
                if (!response.ok) throw new Error('Error al detener scheduler');
                
                const result = await response.json();
                alert(result.mensaje || 'Scheduler detenido');
                
            } catch (error) {
                console.error('Error:', error);
                alert('Error al detener scheduler: ' + error.message);
            }
        }

        function mostrarError(mensaje) {
            const container = document.getElementById('statsGrid');
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.textContent = mensaje;
            container.parentElement.insertBefore(errorDiv, container);
            setTimeout(() => errorDiv.remove(), 5000);
        }

        function actualizarTimestamp() {
            const now = new Date();
            document.getElementById('lastUpdate').textContent = 
                `Última actualización: ${now.toLocaleString('es-ES')}`;
        }

        // Auto-refresh cada 30 segundos
        setInterval(cargarDatos, 30000);

        // Cargar datos al iniciar
        cargarDatos();
    </script>
</body>
</html>
