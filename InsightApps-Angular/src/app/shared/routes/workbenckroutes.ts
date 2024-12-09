import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

export const workbench: Routes = [

    {
        path: '',
        loadChildren: () => import('../../components/workbench/workbench.routes').then(r => r.WorkbenchModule)
      },
      {
        path: '',
        loadChildren: () => import('../../components/helpguide/help-guides.routes').then(r => r.HelpGuideModule)
      }

  
];
@NgModule({
  imports: [RouterModule],
    // imports: [RouterModule.forRoot(admin)],
    exports: [RouterModule]
})
export class SaredRoutingModule { }
