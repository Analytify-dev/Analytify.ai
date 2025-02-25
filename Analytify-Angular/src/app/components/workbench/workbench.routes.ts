import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from '../../shared/sharedmodule';
// import { PagesService } from '../pages/pages.service';
import { authGuard } from '../../auth.guard';
import { canDeactivateGuard } from '../../can-deactivate.guard';

export const admin: Routes = [

  {
    path: 'analytify', children: [
      {
        path: 'datasources/new-connections',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./workbench/workbench.component').then((m) => m.WorkbenchComponent),
      },
      {
        path: 'datasources/view-connections',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./workbench/workbench.component').then((m) => m.WorkbenchComponent),
      },
      {
        path: 'datasources/google-sheets/:id',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./workbench/workbench.component').then((m) => m.WorkbenchComponent),
      },
      {
        path: 'datasources/google-sheets',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./workbench/workbench.component').then((m) => m.WorkbenchComponent),
      },
      //  {
      //   path: 'database-connection/tables/:id',
      //   canActivate:[authGuard],
      //   loadComponent: () =>
      //     import('./insights/workbench.component').then((m) => m.WorkbenchComponent),
      // },

      {
        path: 'database-connection/tables/:id',
        canActivate: [authGuard],
        canDeactivate: [canDeactivateGuard],
        loadComponent: () =>
          import('./database/database.component').then((m) => m.DatabaseComponent)
      },
      {
        path: 'database-connection/customSql/:id',
        canActivate: [authGuard],
        canDeactivate: [canDeactivateGuard],
        loadComponent: () =>
          import('./database/database.component').then((m) => m.DatabaseComponent)
      },
      //quickbooks
      {
        path: 'database-connection/tables/quickbooks/:id',
        canActivate: [authGuard],
        canDeactivate: [canDeactivateGuard],
        loadComponent: () =>
          import('./database/database.component').then((m) => m.DatabaseComponent)
      },
      //salesforce
      {
        path: 'database-connection/tables/salesforce/:id',
        canActivate: [authGuard],
        canDeactivate: [canDeactivateGuard],
        loadComponent: () =>
          import('./database/database.component').then((m) => m.DatabaseComponent)
      },
      {
        path: 'database-connection/files/tables/:id',
        canActivate: [authGuard],
        canDeactivate: [canDeactivateGuard],
        loadComponent: () =>
          import('./database/database.component').then((m) => m.DatabaseComponent)
      },
      {
        path: 'database-connection/sheets/fileId/:id1/:id2/:id3',
        canActivate: [authGuard],
        canDeactivate: [canDeactivateGuard],
        loadComponent: () =>
          import('./database/database.component').then((m) => m.DatabaseComponent)
      },
      {
        path: 'database-connection/sheets/:id1/:id2/:id3',
        canActivate: [authGuard],
        canDeactivate: [canDeactivateGuard],
        loadComponent: () =>
          import('./database/database.component').then((m) => m.DatabaseComponent)
      },
      {
        path: 'database-connection/savedQuery/fileId/:id1/:id2',
        canActivate: [authGuard],
        canDeactivate: [canDeactivateGuard],
        loadComponent: () =>
          import('./database/database.component').then((m) => m.DatabaseComponent)
      },
      {
        path: 'database-connection/savedQuery/:id1/:id2',
        canActivate: [authGuard],
        canDeactivate: [canDeactivateGuard],
        loadComponent: () =>
          import('./database/database.component').then((m) => m.DatabaseComponent)
      },
      {
        path: 'sheets/fileId/:id1/:id2/:id3',
        canActivate: [authGuard],
        canDeactivate: [canDeactivateGuard],
        loadComponent: () =>
          import('./sheets/sheets.component').then((m) => m.SheetsComponent)
      },
      {
        path: 'sheets/:id1/:id2/:id3',
        canActivate: [authGuard],
        canDeactivate: [canDeactivateGuard],
        loadComponent: () =>
          import('./sheets/sheets.component').then((m) => m.SheetsComponent)
      },
      {
        path: 'sheets',
        canActivate: [authGuard],
        canDeactivate: [canDeactivateGuard],
        loadComponent: () =>
          import('./sheets/sheets.component').then((m) => m.SheetsComponent)
      },
      {
        path: 'sheetsdashboard',
        canActivate: [authGuard],
        canDeactivate: [canDeactivateGuard],
        loadComponent: () =>
          import('./sheetsdashboard/sheetsdashboard.component').then((m) => m.SheetsdashboardComponent)
      },
      {
        path: 'sheetscomponent/sheetsdashboard/fileId/:id1/:id2',
        canActivate: [authGuard],
        canDeactivate: [canDeactivateGuard],
        loadComponent: () =>
          import('./sheetsdashboard/sheetsdashboard.component').then((m) => m.SheetsdashboardComponent),
        pathMatch: 'full',
      },
      {
        path: 'sheetscomponent/sheetsdashboard/:id1/:id2',
        canActivate: [authGuard],
        canDeactivate: [canDeactivateGuard],
        loadComponent: () =>
          import('./sheetsdashboard/sheetsdashboard.component').then((m) => m.SheetsdashboardComponent),
        pathMatch: 'full',
      },
      {
        path: 'home/sheetsdashboard/:id1/:id2/:id3',
        canActivate: [authGuard],
        canDeactivate: [canDeactivateGuard],
        loadComponent: () =>
          import('./sheetsdashboard/sheetsdashboard.component').then((m) => m.SheetsdashboardComponent),
        pathMatch: 'full',
      }, {
        path: 'home/sheetsdashboard/:id1',
        canActivate: [authGuard],
        canDeactivate: [canDeactivateGuard],
        loadComponent: () =>
          import('./sheetsdashboard/sheetsdashboard.component').then((m) => m.SheetsdashboardComponent),
        pathMatch: 'full',
      },
      {
        path: 'home/sheets/:id1/:id2/:id3',
        canActivate: [authGuard],
        canDeactivate: [canDeactivateGuard],
        loadComponent: () =>
          import('./sheets/sheets.component').then((m) => m.SheetsComponent)
      },

      {
        path: 'home/sheets/:id1/:id2/:id3',
        canActivate: [authGuard],
        canDeactivate: [canDeactivateGuard],
        loadComponent: () =>
          import('./sheets/sheets.component').then((m) => m.SheetsComponent)
      },
      {
        path: 'home/fileId/sheets/:id1/:id2/:id3',
        canActivate: [authGuard],
        canDeactivate: [canDeactivateGuard],
        loadComponent: () =>
          import('./sheets/sheets.component').then((m) => m.SheetsComponent)
      },

      {
        path: 'home',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./landingpage/landingpage.component').then((m) => m.LandingpageComponent)
      },
      {
        path: 'dashboards',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./dashboard-page/dashboard-page.component').then((m) => m.DashboardPageComponent)
      },
      {
        path: 'sheets-dashboard',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./sheets-list-page/sheets-list-page.component').then((m) => m.SheetsListPageComponent)
      },
      {
        path: 'saved-queries',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./saved-queries/saved-queries.component').then((m) => m.SavedQueriesComponent)
      },
      {
        path: 'users/users-list',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./users-dashboard/users-dashboard.component').then((m) => m.UsersDashboardComponent)
      },
      {
        path: 'users/add-user',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./users-dashboard/users-dashboard.component').then((m) => m.UsersDashboardComponent)
      },
      {
        path: 'users/edit-user/:id',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./users-dashboard/users-dashboard.component').then((m) => m.UsersDashboardComponent)
      },
      {
        path: 'roles/roles-list',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./roles-dashboard/roles-dashboard.component').then((m) => m.RolesDashboardComponent)
      },
      {
        path: 'roles/add-role',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./roles-dashboard/roles-dashboard.component').then((m) => m.RolesDashboardComponent)
      },
      {
        path: 'dashboard/role-edit/:id1',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./roles-dashboard/roles-dashboard.component').then((m) => m.RolesDashboardComponent)
      },
      {
        path: 'sheetsdashboard/sheets/fileId/:id1/:id2/:id3/:id4',
        canActivate: [authGuard],
        canDeactivate: [canDeactivateGuard],
        loadComponent: () =>
          import('./sheets/sheets.component').then((m) => m.SheetsComponent)
      }, {
        path: 'sheetsdashboard/sheets/:id1/:id2/:id3/:id4',
        canActivate: [authGuard],
        canDeactivate: [canDeactivateGuard],
        loadComponent: () =>
          import('./sheets/sheets.component').then((m) => m.SheetsComponent)
      },
      // {
      //   path: 'home/help-guide',
      //   canActivate:[authGuard],
      //   loadComponent: () =>
      //     import('./help-guide/help-guide.component').then((m) => m.HelpGuideComponent),
      // },




      {
        path: 'public/dashboard/:id1',
        loadComponent: () =>
          import('./sheetsdashboard/sheetsdashboard.component').then((m) => m.SheetsdashboardComponent),
      },
      {
        path: 'configure-page/configure',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./configure/configure.component').then((m) => m.ConfigureComponent),
      },

    ]
  }
 ];

@NgModule({
  declarations: [],
  imports: [
    CommonModule,RouterModule.forChild(admin),
  ],
  exports:[RouterModule]
})
export class WorkbenchModule { 
  static routes = admin;


}
