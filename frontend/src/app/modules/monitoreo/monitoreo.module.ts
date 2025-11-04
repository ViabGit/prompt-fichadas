import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MonitoreoRoutingModule } from './monitoreo-routing.module';
import { MonitoreoComponent } from './monitoreo.component';

// Angular Material
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTabsModule } from '@angular/material/tabs';
import { MatBadgeModule } from '@angular/material/badge';

@NgModule({
  declarations: [
    MonitoreoComponent
  ],
  imports: [
    CommonModule,
    MonitoreoRoutingModule,
    MatCardModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatProgressSpinnerModule,
    MatTabsModule,
    MatBadgeModule
  ]
})
export class MonitoreoModule { }
