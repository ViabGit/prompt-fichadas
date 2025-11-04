import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { DispositivoService } from '../../../services/dispositivo.service';
import { Dispositivo, DispositivoCreate } from '../../../models/dispositivo.model';

@Component({
  selector: 'app-dispositivo-form',
  templateUrl: './dispositivo-form.component.html',
  styleUrls: ['./dispositivo-form.component.css']
})
export class DispositivoFormComponent implements OnInit {
  dispositivoForm: FormGroup;
  isEditMode = false;
  loading = false;

  constructor(
    private fb: FormBuilder,
    private dispositivoService: DispositivoService,
    private dialogRef: MatDialogRef<DispositivoFormComponent>,
    private snackBar: MatSnackBar,
    @Inject(MAT_DIALOG_DATA) public data: { dispositivo: Dispositivo | null }
  ) {
    this.dispositivoForm = this.fb.group({
      nombre: ['', [Validators.required, Validators.minLength(3)]],
      ip: ['', [Validators.required, Validators.pattern(/^(\d{1,3}\.){3}\d{1,3}$/)]],
      puerto: [4370, [Validators.required, Validators.min(1), Validators.max(65535)]],
      modelo: ['SF300', Validators.required],
      marca: ['ZK', Validators.required],
      numero_dispositivo: ['', [Validators.required, Validators.pattern(/^\d+$/)]],
      activo: [true]
    });
  }

  ngOnInit(): void {
    if (this.data.dispositivo) {
      this.isEditMode = true;
      this.cargarDatos(this.data.dispositivo);
    }
  }

  cargarDatos(dispositivo: Dispositivo): void {
    this.dispositivoForm.patchValue({
      nombre: dispositivo.nombre,
      ip: dispositivo.ip,
      puerto: dispositivo.puerto,
      modelo: dispositivo.modelo,
      marca: dispositivo.marca,
      numero_dispositivo: dispositivo.numero_dispositivo,
      activo: dispositivo.activo
    });
  }

  guardar(): void {
    if (this.dispositivoForm.invalid) {
      this.marcarCamposInvalidos();
      return;
    }

    this.loading = true;
    const dispositivoData: DispositivoCreate = this.dispositivoForm.value;

    if (this.isEditMode && this.data.dispositivo) {
      // Actualizar
      this.dispositivoService.updateDispositivo(this.data.dispositivo.id, dispositivoData).subscribe({
        next: () => {
          this.mostrarMensaje('Dispositivo actualizado exitosamente');
          this.dialogRef.close(true);
        },
        error: (err) => {
          this.loading = false;
          this.mostrarError('Error al actualizar dispositivo');
          console.error('Error:', err);
        }
      });
    } else {
      // Crear
      this.dispositivoService.createDispositivo(dispositivoData).subscribe({
        next: () => {
          this.mostrarMensaje('Dispositivo creado exitosamente');
          this.dialogRef.close(true);
        },
        error: (err) => {
          this.loading = false;
          this.mostrarError('Error al crear dispositivo');
          console.error('Error:', err);
        }
      });
    }
  }

  cancelar(): void {
    this.dialogRef.close(false);
  }

  marcarCamposInvalidos(): void {
    Object.keys(this.dispositivoForm.controls).forEach(key => {
      const control = this.dispositivoForm.get(key);
      if (control && control.invalid) {
        control.markAsTouched();
      }
    });
  }

  getErrorMessage(fieldName: string): string {
    const field = this.dispositivoForm.get(fieldName);
    if (!field) return '';

    if (field.hasError('required')) {
      return 'Este campo es requerido';
    }
    if (field.hasError('minlength')) {
      return `Mínimo ${field.errors?.['minlength'].requiredLength} caracteres`;
    }
    if (field.hasError('pattern')) {
      if (fieldName === 'ip') {
        return 'Formato de IP inválido (ej: 192.168.1.100)';
      }
      if (fieldName === 'numero_dispositivo') {
        return 'Solo números permitidos';
      }
    }
    if (field.hasError('min') || field.hasError('max')) {
      return 'Valor fuera de rango';
    }

    return '';
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
