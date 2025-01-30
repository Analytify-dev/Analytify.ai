import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { authGuard } from '../../auth.guard';
import { HelpGuideQuestionariesComponent } from './help-guide-questionaries/help-guide-questionaries.component';

const routes: Routes = [
    {path:'analytify',children:[ 
    { 
      path: 'help-guide', 
      canActivate:[authGuard],
      loadComponent: () => import('./help-guide/help-guide.component').then((m) => m.HelpGuideComponent)
    },
    { 
      path: 'help-guide/:slug', 
      canActivate:[authGuard],
      loadComponent: () => import('./help-guide/help-guide.component').then((m) => m.HelpGuideComponent)
    },
    { 
      path: 'protocol-conversion/guide', 
      canActivate:[authGuard],
      loadComponent: () => import('./http-protocal-userguide/http-protocal-userguide.component').then((m) => m.HttpProtocalUserguideComponent)
    },

    //   { path: 'search', component: GuideLeftMenuComponent},
    //   { path: 'search/:moduleName', component:GuideLeftMenuComponent},
    //   { path: 'help-guide/:moduleName', component: HelpGuideComponent },
    ]}
  ];


  @NgModule({
    declarations: [],
    imports: [
      CommonModule,RouterModule.forChild(routes),
    ],
    exports:[RouterModule]
  })
  export class HelpGuideModule { 
  }