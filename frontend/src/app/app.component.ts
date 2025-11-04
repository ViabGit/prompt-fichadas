import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  template: `
    <mat-toolbar color="primary">
      <mat-toolbar-row>
        <span>Sistema de Fichadas ZKTeco</span>
        <span class="spacer"></span>
        <button mat-button routerLink="/dashboard">
          <mat-icon>dashboard</mat-icon>
          Dashboard
        </button>
        <button mat-button routerLink="/dispositivos">
          <mat-icon>devices</mat-icon>
          Dispositivos
        </button>
        <button mat-button routerLink="/monitoreo">
          <mat-icon>monitor</mat-icon>
          Monitoreo
        </button>
        <button mat-button routerLink="/configuracion">
          <mat-icon>settings</mat-icon>
          Configuración
        </button>
      </mat-toolbar-row>
    </mat-toolbar>

    <main>
      <router-outlet></router-outlet>
    </main>
  `,
  styles: [`
    .spacer {
      flex: 1 1 auto;
    }
    
    main {
      padding: 20px;
      min-height: calc(100vh - 64px);
      background-color: #f5f5f5;
    }
    
    mat-toolbar button {
      margin-left: 8px;
    }
    
    mat-toolbar mat-icon {
      margin-right: 8px;
    }
  `]
})
export class AppComponent {
  title = 'Sistema de Fichadas ZKTeco';
}