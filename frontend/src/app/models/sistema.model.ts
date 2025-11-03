export interface ConfiguracionGlobal {
  id: number;
  carpeta_salida: string;
  carpeta_backup: string;
  frecuencia_minutos: number;
  inicio_automatico: boolean;
  max_reintentos: number;
  tipo_notificacion: 'smtp' | 'sendgrid' | 'none';
  smtp_config?: SMTPConfig;
  sendgrid_config?: SendGridConfig;
  created_at: Date;
  updated_at?: Date;
}

export interface SMTPConfig {
  servidor: string;
  puerto: number;
  usuario: string;
  password: string;
  desde: string;
  para: string[];
  usar_tls: boolean;
}

export interface SendGridConfig {
  api_key: string;
  desde: string;
  para: string[];
}

export interface Estadisticas {
  total_dispositivos: number;
  dispositivos_online: number;
  dispositivos_offline: number;
  dispositivos_error: number;
  ultima_actualizacion: Date;
  fichadas_hoy: number;
  errores_ultimas_24h: number;
}

export interface LogSistema {
  id: number;
  nivel: 'INFO' | 'WARNING' | 'ERROR';
  mensaje: string;
  dispositivo_id?: string;
  componente: string;
  detalles?: string;
  created_at: Date;
}