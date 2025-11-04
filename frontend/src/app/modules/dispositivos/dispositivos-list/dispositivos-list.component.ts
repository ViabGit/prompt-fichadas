import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { DispositivoService } from '../../../services/dispositivo.service';
import { Dispositivo } from '../../../models/dispositivo.model';
import { DispositivoFormComponent } from '../dispositivo-form/dispositivo-form.component';

@Component({
  selector: 'app-dispositivos-list',
  templateUrl: './dispositivos-list.component.html',
  styleUrls: ['./dispositivos-list.component.css']
})
export class DispositivosListComponent implements OnInit {
  dispositivos: Dispositivo[] = [];
  loading = true;
  displayedColumns: string[] = ['nombre', 'ip', 'puerto', 'numero_dispositivo', 'estado', 'activo', 'acciones'];

  constructor(
    private dispositivoService: DispositivoService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) { }

  ngOnInit(): void {
    this.cargarDispositivos();
  }

  cargarDispositivos(): void {
    this.loading = true;
    this.dispositivoService.getDispositivos().subscribe({
      next: (dispositivos) => {
        this.dispositivos = dispositivos;
        this.loading = false;
      },
      error: (err) => {
        this.mostrarError('Error al cargar dispositivos');
        this.loading = false;
        console.error('Error:', err);
      }
    });
  }

  agregarDispositivo(): void {
    const dialogRef = this.dialog.open(DispositivoFormComponent, {
      width: '600px',
      data: { dispositivo: null }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.cargarDispositivos();
      }
    });
  }

  editarDispositivo(dispositivo: Dispositivo): void {
    const dialogRef = this.dialog.open(DispositivoFormComponent, {
      width: '600px',
      data: { dispositivo: { ...dispositivo } }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.cargarDispositivos();
      }
    });
  }

  eliminarDispositivo(id: string, nombre: string): void {
    if (!confirm(`¿Está seguro de eliminar el dispositivo "${nombre}"?`)) {
      return;
    }

    this.dispositivoService.deleteDispositivo(id).subscribe({
      next: () => {
        this.mostrarMensaje('Dispositivo eliminado exitosamente');
        this.cargarDispositivos();
      },
      error: (err) => {
        this.mostrarError('Error al eliminar dispositivo');
        console.error('Error:', err);
      }
    });
  }

  testConexion(id: string, nombre: string): void {
    this.dispositivoService.testConexion(id).subscribe({
      next: (result) => {
        if (result.success) {
          this.mostrarMensaje(`${nombre}: ${result.mensaje}`);
        } else {
          this.mostrarError(`${nombre}: Error de conexión`);
        }
        this.cargarDispositivos();
      },
      error: (err) => {
        this.mostrarError('Error al probar conexión');
        console.error('Error:', err);
      }
    });
  }

  descargarFichadas(id: string, nombre: string): void {
    if (!confirm(`¿Descargar fichadas de "${nombre}"?`)) {
      return;
    }

    this.mostrarMensaje('Descargando fichadas...');

    this.dispositivoService.descargarManual(id).subscribe({
      next: (result) => {
        this.mostrarMensaje(`Descarga completada: ${result.fichadas_descargadas} fichadas`);
        this.cargarDispositivos();
      },
      error: (err) => {
        this.mostrarError('Error al descargar fichadas');
        console.error('Error:', err);
      }
    });
  }

  getEstadoColor(estado: string): string {
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

  mostrarMensaje(mensaje: string): void {
    this.snackBar.open(mensaje, 'Cerrar', {
      duration: 3000
    });
  }

  mostrarError(mensaje: string): void {
    this.snackBar.open(mensaje, 'Cerrar', {
      duration: 5000,
      panelClass: ['error-snackbar']
    });
  }
}
