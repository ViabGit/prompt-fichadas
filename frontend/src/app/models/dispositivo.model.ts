export interface Dispositivo {
  id: string;
  nombre: string;
  ip: string;
  puerto: number;
  modelo?: string;
  marca: string;
  activo: boolean;
  numero_dispositivo: string;
  fecha_ultima_consulta?: Date;
  alertas_activas: boolean;
  intentos_fallidos: number;
  estado_conexion: 'online' | 'offline' | 'error';
  created_at: Date;
  updated_at?: Date;
}

export interface DispositivoCreate {
  id: string;
  nombre: string;
  ip: string;
  puerto: number;
  modelo?: string;
  marca: string;
  activo: boolean;
  numero_dispositivo: string;
}

export interface EstadoDispositivo {
  id: string;
  nombre: string;
  estado_conexion: string;
  fecha_ultima_consulta?: Date;
  intentos_fallidos: number;
  alertas_activas: boolean;
}

export interface TestConexionResponse {
  success: boolean;
  mensaje: string;
  tiempo_respuesta?: number;
  error_detalle?: string;
}

export interface DescargaManualResponse {
  success: boolean;
  mensaje: string;
  fichadas_descargadas: number;
  archivo_generado?: string;
  error_detalle?: string;
}