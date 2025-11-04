import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { MonitoreoComponent } from './monitoreo.component';

const routes: Routes = [
  {
    path: '',
    component: MonitoreoComponent
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class MonitoreoRoutingModule { }
