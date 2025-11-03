import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { ConfiguracionGlobal } from '../models/sistema.model';

@Injectable({
  providedIn: 'root'
})
export class ConfiguracionService {
  private apiUrl = `${environment.apiUrl}/configuracion`;

  constructor(private http: HttpClient) {}

  getConfiguracion(): Observable<ConfiguracionGlobal> {
    return this.http.get<ConfiguracionGlobal>(this.apiUrl);
  }

  updateConfiguracion(config: Partial<ConfiguracionGlobal>): Observable<ConfiguracionGlobal> {
    return this.http.put<ConfiguracionGlobal>(this.apiUrl, config);
  }

  testNotificacion(tipo: 'smtp' | 'sendgrid'): Observable<any> {
    return this.http.post(`${this.apiUrl}/test-notificacion?tipo=${tipo}`, {});
  }

  getSchedulerStatus(): Observable<any> {
    return this.http.get(`${this.apiUrl}/scheduler/status`);
  }

  controlarScheduler(action: 'start' | 'stop' | 'restart'): Observable<any> {
    return this.http.post(`${this.apiUrl}/scheduler/${action}`, {});
  }
}