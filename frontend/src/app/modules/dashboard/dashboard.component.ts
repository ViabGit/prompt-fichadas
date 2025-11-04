import { Component, OnInit, OnDestroy } from '@angular/core';
import { DispositivoService } from '../../services/dispositivo.service';
import { MonitoreoService } from '../../services/monitoreo.service';
import { Dispositivo } from '../../models/dispositivo.model';
import { Subscription, interval } from 'rxjs';
import { switchMap } from 'rxjs/operators';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit, OnDestroy {
  dispositivos: Dispositivo[] = [];
  loading = true;
  error: string | null = null;

  // Estadísticas
  totalDispositivos = 0;
  dispositivosOnline = 0;
  dispositivosOffline = 0;
  fichadasHoy = 0;

  // Subscripciones
  private subscriptions: Subscription[] = [];

  displayedColumns: string[] = ['nombre', 'ip', 'estado', 'ultima_consulta', 'acciones'];

  constructor(
    private dispositivoService: DispositivoService,
    private monitoreoService: MonitoreoService
  ) { }

  ngOnInit(): void {
    this.cargarDatos();

    // Auto-refresh cada 30 segundos
    const refreshSub = interval(30000)
      .pipe(switchMap(() => this.dispositivoService.getDispositivos()))
      .subscribe({
        next: (dispositivos) => {
          this.dispositivos = dispositivos;
          this.calcularEstadisticas();
        },
        error: (err) => console.error('Error en auto-refresh:', err)
      });

    this.subscriptions.push(refreshSub);
  }

  ngOnDestroy(): void {
    this.subscriptions.forEach(sub => sub.unsubscribe());
  }

  cargarDatos(): void {
    this.loading = true;
    this.error = null;

    const disp$ = this.dispositivoService.getDispositivos().subscribe({
      next: (dispositivos) => {
        this.dispositivos = dispositivos;
        this.calcularEstadisticas();
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Error al cargar dispositivos';
        this.loading = false;
        console.error('Error:', err);
      }
    });

    this.subscriptions.push(disp$);
  }

  calcularEstadisticas(): void {
    this.totalDispositivos = this.dispositivos.length;
    this.dispositivosOnline = this.dispositivos.filter(d => d.estado_conexion === 'online').length;
    this.dispositivosOffline = this.dispositivos.filter(d => d.estado_conexion === 'offline').length;
    // TODO: Obtener fichadas del día desde el backend
    this.fichadasHoy = 0;
  }

  getEstadoChipColor(estado: string): string {
    switch (estado) {
      case 'online':
        return 'primary';
      case 'offline':
        return 'warn';
      case 'error':
        return 'accent';
      default:
        return '';
    }
  }

  testConexion(id: string): void {
    this.dispositivoService.testConexion(id).subscribe({
      next: (result) => {
        alert(`Conexión: ${result.mensaje}\nTiempo: ${result.tiempo_respuesta?.toFixed(2)}s`);
        this.cargarDatos();
      },
      error: (err) => {
        alert('Error al probar conexión');
        console.error('Error:', err);
      }
    });
  }

  descargarFichadas(id: string): void {
    if (!confirm('¿Descargar fichadas de este dispositivo?')) {
      return;
    }

    this.dispositivoService.descargarManual(id).subscribe({
      next: (result) => {
        alert(`Descarga completada\nFichadas descargadas: ${result.fichadas_descargadas}`);
        this.cargarDatos();
      },
      error: (err) => {
        alert('Error al descargar fichadas');
        console.error('Error:', err);
      }
    });
  }

  formatFecha(fecha: string | null): string {
    if (!fecha) return 'Nunca';
    return new Date(fecha).toLocaleString('es-AR');
  }
}
