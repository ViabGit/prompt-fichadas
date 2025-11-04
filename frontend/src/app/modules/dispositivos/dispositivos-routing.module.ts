import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { DispositivosListComponent } from './dispositivos-list/dispositivos-list.component';

const routes: Routes = [
  {
    path: '',
    component: DispositivosListComponent
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class DispositivosRoutingModule { }
