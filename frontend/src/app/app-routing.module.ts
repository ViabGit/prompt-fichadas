import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { path: 'dashboard', loadChildren: () => import('./modules/dashboard/dashboard.module').then(m => m.DashboardModule) },
  { path: 'dispositivos', loadChildren: () => import('./modules/dispositivos/dispositivos.module').then(m => m.DispositivosModule) },
  { path: 'monitoreo', loadChildren: () => import('./modules/monitoreo/monitoreo.module').then(m => m.MonitoreoModule) },
  { path: 'configuracion', loadChildren: () => import('./modules/configuracion/configuracion.module').then(m => m.ConfiguracionModule) },
  { path: '**', redirectTo: '/dashboard' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }