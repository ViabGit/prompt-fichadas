import { Component, OnInit, OnDestroy } from '@angular/core';
import { MonitoreoService } from '../../services/monitoreo.service';
import { DispositivoService } from '../../services/dispositivo.service';
import { Subscription, interval } from 'rxjs';
import { switchMap } from 'rxjs/operators';

interface LogItem {
  fecha: Date;
  tipo: string;
  dispositivo: string;
  mensaje: string;
  nivel: 'info' | 'warning' | 'error' | 'success';
}

@Component({
  selector: 'app-monitoreo',
  templateUrl: './monitoreo.component.html',
  styleUrls: ['./monitoreo.component.css']
})
export class MonitoreoComponent implements OnInit, OnDestroy {
  estadisticas: any = null;
  logs: LogItem[] = [];
  loading = true;
  autoRefresh = true;

  private subscriptions: Subscription[] = [];

  displayedColumnsLogs: string[] = ['fecha', 'tipo', 'dispositivo', 'mensaje'];

  constructor(
    private monitoreoService: MonitoreoService,
    private dispositivoService: DispositivoService
  ) { }

  ngOnInit(): void {
    this.cargarDatos();

    // Auto-refresh cada 5 segundos
    const refreshSub = interval(5000)
      .pipe(switchMap(() => this.monitoreoService.getEstadisticas()))
      .subscribe({
        next: (stats) => {
          if (this.autoRefresh) {
            this.estadisticas = stats;
          }
        },
        error: (err) => console.error('Error en auto-refresh:', err)
      });

    this.subscriptions.push(refreshSub);

    // Cargar logs cada 10 segundos
    const logsSub = interval(10000)
      .pipe(switchMap(() => this.monitoreoService.getLogs(50)))
      .subscribe({
        next: (logs) => {
          if (this.autoRefresh) {
            this.logs = this.procesarLogs(logs);
          }
        },
        error: (err) => console.error('Error cargando logs:', err)
      });

    this.subscriptions.push(logsSub);
  }

  ngOnDestroy(): void {
    this.subscriptions.forEach(sub => sub.unsubscribe());
  }

  cargarDatos(): void {
    this.loading = true;

    // Cargar estadísticas
    this.monitoreoService.getEstadisticas().subscribe({
      next: (stats) => {
        this.estadisticas = stats;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error cargando estadísticas:', err);
        this.loading = false;
      }
    });

    // Cargar logs
    this.monitoreoService.getLogs(50).subscribe({
      next: (logs) => {
        this.logs = this.procesarLogs(logs);
      },
      error: (err) => {
        console.error('Error cargando logs:', err);
      }
    });
  }

  procesarLogs(logsData: any[]): LogItem[] {
    return logsData.map(log => ({
      fecha: new Date(log.fecha_hora || log.timestamp),
      tipo: log.tipo || log.tipo_evento,
      dispositivo: log.dispositivo_id || log.dispositivo || 'Sistema',
      mensaje: log.mensaje || log.descripcion,
      nivel: this.determinarNivel(log)
    }));
  }

  determinarNivel(log: any): 'info' | 'warning' | 'error' | 'success' {
    const mensaje = (log.mensaje || log.descripcion || '').toLowerCase();
    const tipo = (log.tipo || log.tipo_evento || '').toLowerCase();

    if (tipo.includes('error') || mensaje.includes('error') || mensaje.includes('fallo')) {
      return 'error';
    }
    if (tipo.includes('warning') || tipo.includes('alerta') || mensaje.includes('reintento')) {
      return 'warning';
    }
    if (tipo.includes('exito') || mensaje.includes('exitosa') || mensaje.includes('conectado')) {
      return 'success';
    }
    return 'info';
  }

  toggleAutoRefresh(): void {
    this.autoRefresh = !this.autoRefresh;
    if (this.autoRefresh) {
      this.cargarDatos();
    }
  }

  getNivelColor(nivel: string): string {
    switch (nivel) {
      case 'success':
        return 'primary';
      case 'warning':
        return 'accent';
      case 'error':
        return 'warn';
      default:
        return '';
    }
  }

  getNivelIcon(nivel: string): string {
    switch (nivel) {
      case 'success':
        return 'check_circle';
      case 'warning':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'info';
    }
  }

  formatFecha(fecha: Date): string {
    return fecha.toLocaleString('es-AR');
  }
}
