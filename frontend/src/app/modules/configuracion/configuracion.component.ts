import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ConfiguracionService } from '../../services/configuracion.service';

@Component({
  selector: 'app-configuracion',
  templateUrl: './configuracion.component.html',
  styleUrls: ['./configuracion.component.css']
})
export class ConfiguracionComponent implements OnInit {
  configuracionForm: FormGroup;
  loading = true;
  saving = false;

  constructor(
    private fb: FormBuilder,
    private configuracionService: ConfiguracionService,
    private snackBar: MatSnackBar
  ) {
    this.configuracionForm = this.fb.group({
      // Configuración General
      carpeta_salida: ['/data/fichadas', Validators.required],
      carpeta_backup: ['/data/backup', Validators.required],
      frecuencia_minutos: [5, [Validators.required, Validators.min(1), Validators.max(1440)]],
      inicio_automatico: [true],
      max_reintentos: [3, [Validators.required, Validators.min(1), Validators.max(10)]],

      // Notificaciones
      tipo_notificacion: ['ninguno', Validators.required],

      // SMTP
      smtp_servidor: [''],
      smtp_puerto: [587, [Validators.min(1), Validators.max(65535)]],
      smtp_usuario: [''],
      smtp_password: [''],
      smtp_desde: [''],
      smtp_para: [''],
      smtp_usar_tls: [true],

      // SendGrid
      sendgrid_api_key: [''],
      sendgrid_desde: [''],
      sendgrid_para: ['']
    });
  }

  ngOnInit(): void {
    this.cargarConfiguracion();
  }

  cargarConfiguracion(): void {
    this.loading = true;
    this.configuracionService.getConfiguracion().subscribe({
      next: (config) => {
        this.configuracionForm.patchValue({
          carpeta_salida: config.carpeta_salida,
          carpeta_backup: config.carpeta_backup,
          frecuencia_minutos: config.frecuencia_minutos,
          inicio_automatico: config.inicio_automatico,
          max_reintentos: config.max_reintentos,
          tipo_notificacion: config.tipo_notificacion || 'ninguno',

          smtp_servidor: config.smtp_config?.servidor || '',
          smtp_puerto: config.smtp_config?.puerto || 587,
          smtp_usuario: config.smtp_config?.usuario || '',
          smtp_password: '', // No mostrar password
          smtp_desde: config.smtp_config?.desde || '',
          smtp_para: config.smtp_config?.para?.join(', ') || '',
          smtp_usar_tls: config.smtp_config?.usar_tls !== false,

          sendgrid_api_key: '', // No mostrar API key
          sendgrid_desde: config.sendgrid_config?.desde || '',
          sendgrid_para: config.sendgrid_config?.para?.join(', ') || ''
        });
        this.loading = false;
      },
      error: (err) => {
        this.mostrarError('Error al cargar configuración');
        this.loading = false;
        console.error('Error:', err);
      }
    });
  }

  guardar(): void {
    if (this.configuracionForm.invalid) {
      this.marcarCamposInvalidos();
      return;
    }

    this.saving = true;
    const formValue = this.configuracionForm.value;

    const config = {
      carpeta_salida: formValue.carpeta_salida,
      carpeta_backup: formValue.carpeta_backup,
      frecuencia_minutos: formValue.frecuencia_minutos,
      inicio_automatico: formValue.inicio_automatico,
      max_reintentos: formValue.max_reintentos,
      tipo_notificacion: formValue.tipo_notificacion,

      smtp_config: {
        servidor: formValue.smtp_servidor,
        puerto: formValue.smtp_puerto,
        usuario: formValue.smtp_usuario,
        password: formValue.smtp_password || undefined, // Solo si se ingresó
        desde: formValue.smtp_desde,
        para: formValue.smtp_para ? formValue.smtp_para.split(',').map((e: string) => e.trim()) : [],
        usar_tls: formValue.smtp_usar_tls
      },

      sendgrid_config: {
        api_key: formValue.sendgrid_api_key || undefined, // Solo si se ingresó
        desde: formValue.sendgrid_desde,
        para: formValue.sendgrid_para ? formValue.sendgrid_para.split(',').map((e: string) => e.trim()) : []
      }
    };

    this.configuracionService.updateConfiguracion(config).subscribe({
      next: () => {
        this.mostrarMensaje('Configuración guardada exitosamente');
        this.saving = false;
        this.cargarConfiguracion();
      },
      error: (err) => {
        this.mostrarError('Error al guardar configuración');
        this.saving = false;
        console.error('Error:', err);
      }
    });
  }

  restaurarDefecto(): void {
    if (!confirm('¿Restaurar configuración por defecto?')) {
      return;
    }

    this.configuracionForm.patchValue({
      carpeta_salida: '/data/fichadas',
      carpeta_backup: '/data/backup',
      frecuencia_minutos: 5,
      inicio_automatico: true,
      max_reintentos: 3,
      tipo_notificacion: 'ninguno'
    });
  }

  marcarCamposInvalidos(): void {
    Object.keys(this.configuracionForm.controls).forEach(key => {
      const control = this.configuracionForm.get(key);
      if (control && control.invalid) {
        control.markAsTouched();
      }
    });
    this.mostrarError('Por favor complete los campos requeridos');
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
