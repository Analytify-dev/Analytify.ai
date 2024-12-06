import { RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import {  NgModule } from '@angular/core';
// import { ContentLayoutComponent } from './layout-components/layouts/content-layout/content-layout.component';
import { SidebarComponent } from './layout-components/sidebar/sidebar.component';
import { SimplebarAngularModule } from 'simplebar-angular';
import { HeaderComponent } from './layout-components/header/header.component';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { SwitcherComponent } from './layout-components/switcher/switcher.component';
import { HoverEffectSidebarDirective } from './directives/hover-effect-sidebar.directive';
import { PageHeaderComponent } from './layout-components/page-header/page-header.component';
import { ToggleBtnDirective } from './directives/toggle-btn.directive';
import { ToggleThemeDirective } from './directives/toggle-theme.directive';
import { FullscreenDirective } from './directives/fullscreen.directive';
// import { LandingpageLayoutComponent } from './layout-components/layouts/landingpage-layout/landingpage-layout.component';
import { LandingSwitcherComponent } from './landing-switcher/landing-switcher.component';
import { ColorPickerModule } from 'ngx-color-picker';
import { AuthenticationLayoutComponent } from './layout-components/layouts/authentication-layout/authentication-layout.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FooterComponent } from './layout-components/footer/footer.component';
import { TabToTopComponent } from './layout-components/tab-to-top/tab-to-top.component';
import { SheetsdashboardComponent } from '../components/workbench/sheetsdashboard/sheetsdashboard.component';
import { TestPipe } from '../test.pipe';

@NgModule({
  declarations: [
    SidebarComponent,
    // ContentLayoutComponent,
    HeaderComponent,
    SwitcherComponent,
    PageHeaderComponent,
    TabToTopComponent,
    HoverEffectSidebarDirective,
    ToggleBtnDirective,
    ToggleThemeDirective,
    FullscreenDirective,
    // LandingpageLayoutComponent,
    LandingSwitcherComponent,
    AuthenticationLayoutComponent,
    FooterComponent,
    

  ],
  imports: [
    CommonModule,
    RouterModule,
    TestPipe,
    SimplebarAngularModule,
    NgbModule,
  ColorPickerModule,
  FormsModule,ReactiveFormsModule,
  SheetsdashboardComponent
  
   
  ],

  exports: [
    // ContentLayoutComponent,
    // LandingpageLayoutComponent,
    TestPipe,
    SidebarComponent,
    HeaderComponent,
    TabToTopComponent,
    SwitcherComponent,
    PageHeaderComponent,
    HoverEffectSidebarDirective,
    ToggleBtnDirective,
    ToggleThemeDirective,
    FullscreenDirective,
    LandingSwitcherComponent,
    AuthenticationLayoutComponent,
    FooterComponent,
    SheetsdashboardComponent

  ],
})
export class SharedModule {}
