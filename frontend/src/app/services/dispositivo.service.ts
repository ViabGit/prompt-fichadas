import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { 
  Dispositivo, 
  DispositivoCreate, 
  EstadoDispositivo, 
  TestConexionResponse, 
  DescargaManualResponse 
} from '../models/dispositivo.model';

@Injectable({
  providedIn: 'root'
})
export class DispositivoService {
  private apiUrl = `${environment.apiUrl}/dispositivos`;

  constructor(private http: HttpClient) {}

  getDispositivos(): Observable<Dispositivo[]> {
    return this.http.get<Dispositivo[]>(this.apiUrl);
  }

  getDispositivo(id: string): Observable<Dispositivo> {
    return this.http.get<Dispositivo>(`${this.apiUrl}/${id}`);
  }

  createDispositivo(dispositivo: DispositivoCreate): Observable<Dispositivo> {
    return this.http.post<Dispositivo>(this.apiUrl, dispositivo);
  }

  updateDispositivo(id: string, dispositivo: Partial<Dispositivo>): Observable<Dispositivo> {
    return this.http.put<Dispositivo>(`${this.apiUrl}/${id}`, dispositivo);
  }

  deleteDispositivo(id: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`);
  }

  testConexion(id: string): Observable<TestConexionResponse> {
    return this.http.post<TestConexionResponse>(`${this.apiUrl}/${id}/test-conexion`, {});
  }

  descargarFichadas(id: string, forzar: boolean = false): Observable<DescargaManualResponse> {
    return this.http.post<DescargaManualResponse>(
      `${this.apiUrl}/${id}/descargar-fichadas?forzar=${forzar}`, 
      {}
    );
  }

  getEstadoDispositivo(id: string): Observable<EstadoDispositivo> {
    return this.http.get<EstadoDispositivo>(`${this.apiUrl}/${id}/estado`);
  }
}