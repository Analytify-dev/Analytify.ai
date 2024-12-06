import { Route } from '@angular/router';
// import { ContentLayoutComponent } from './shared/layout-components/layouts/content-layout/content-layout.component';
// import { content } from './shared/routes/contentroutes';
import { AuthenticationLayoutComponent } from './shared/layout-components/layouts/authentication-layout/authentication-layout.component';
import { authen } from './shared/routes/authenticationroutes';
// import { LandingpageLayoutComponent } from './shared/layout-components/layouts/landingpage-layout/landingpage-layout.component';
// import { landing } from './shared/routes/landingroutes';
import { workbench } from './shared/routes/workbenckroutes';
import { WorkbenchLayoutsComponent } from './shared/layout-components/layouts/workbench-layouts/workbench-layouts.component';
export const App_Route: Route[] = [
      { path: '', redirectTo: 'authentication/login', pathMatch: 'full' },
      {
        path: '',
        loadComponent: () =>
          import('../app/components/authentication/login/login.component').then((m) => m.LoginComponent),
      },
      {
        path: 'public/dashboard/:id1',
        loadComponent: () =>
          import('../app/components/workbench/sheetsdashboard/sheetsdashboard.component').then((m) => m.SheetsdashboardComponent),
      },
      // { path: '', component: ContentLayoutComponent, children: content },
      { path: '', component: AuthenticationLayoutComponent, children: authen },
      // { path: '', component: LandingpageLayoutComponent, children: landing },
      { path: '', component: WorkbenchLayoutsComponent, children: workbench },


    ]