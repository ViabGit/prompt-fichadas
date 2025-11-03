import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { ConfiguracionGlobal, Estadisticas, LogSistema } from '../models/sistema.model';

@Injectable({
  providedIn: 'root'
})
export class MonitoreoService {
  private apiUrl = `${environment.apiUrl}/monitoreo`;
  private socket?: WebSocket;

  constructor(private http: HttpClient) {}

  getEstadisticas(): Observable<Estadisticas> {
    return this.http.get<Estadisticas>(`${this.apiUrl}/estadisticas`);
  }

  getLogs(filtros?: {
    nivel?: string;
    componente?: string;
    dispositivo_id?: string;
    limit?: number;
    offset?: number;
  }): Observable<LogSistema[]> {
    const params = new URLSearchParams();
    if (filtros) {
      Object.entries(filtros).forEach(([key, value]) => {
        if (value !== undefined) {
          params.append(key, value.toString());
        }
      });
    }
    
    const url = `${this.apiUrl}/logs${params.toString() ? '?' + params.toString() : ''}`;
    return this.http.get<LogSistema[]>(url);
  }

  conectarWebSocket(): Observable<any> {
    return new Observable(observer => {
      this.socket = new WebSocket(environment.wsUrl);
      
      this.socket.onopen = () => {
        console.log('WebSocket conectado');
        observer.next({ tipo: 'conexion', data: 'conectado' });
      };
      
      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          observer.next(data);
        } catch (error) {
          console.error('Error parseando mensaje WebSocket:', error);
        }
      };
      
      this.socket.onerror = (error) => {
        console.error('Error WebSocket:', error);
        observer.error(error);
      };
      
      this.socket.onclose = () => {
        console.log('WebSocket desconectado');
        observer.complete();
      };
      
      return () => {
        if (this.socket) {
          this.socket.close();
        }
      };
    });
  }

  desconectarWebSocket(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = undefined;
    }
  }

  limpiarLogs(dias: number = 30, nivel?: string): Observable<any> {
    const params = new URLSearchParams();
    params.append('dias', dias.toString());
    if (nivel) {
      params.append('nivel', nivel);
    }
    
    return this.http.delete(`${this.apiUrl}/logs?${params.toString()}`);
  }

  descargarLogs(filtros?: {
    nivel?: string;
    componente?: string;
    fecha_desde?: Date;
    fecha_hasta?: Date;
  }): Observable<Blob> {
    const params = new URLSearchParams();
    if (filtros) {
      Object.entries(filtros).forEach(([key, value]) => {
        if (value !== undefined) {
          if (value instanceof Date) {
            params.append(key, value.toISOString());
          } else {
            params.append(key, value.toString());
          }
        }
      });
    }
    
    const url = `${this.apiUrl}/logs/download${params.toString() ? '?' + params.toString() : ''}`;
    return this.http.get(url, { responseType: 'blob' });
  }
}