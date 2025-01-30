import { CanDeactivateFn } from '@angular/router';
import { Observable } from 'rxjs';
import { SheetsComponent } from './components/workbench/sheets/sheets.component';
import { DatabaseComponent } from './components/workbench/database/database.component';
import { SheetsdashboardComponent } from './components/workbench/sheetsdashboard/sheetsdashboard.component';

export interface CanComponentDeactivate {
  canDeactivate: () => boolean | Observable<boolean>;
  gotoSheetButtonDisable: boolean;
  canNavigate: () => boolean | Observable<boolean>;
  dataNotSaveAlert: () => Promise<boolean>;
  sheetNotSaveAlert: () => Promise<boolean>;
  dashboardNotSaveAlert: () => Promise<boolean>;

}

export const canDeactivateGuard: CanDeactivateFn<CanComponentDeactivate> = (component) => {
  // If gotoSheetButtonDisable is false, show the alert
  if(component instanceof DatabaseComponent){
    if (!component.gotoSheetButtonDisable) {
      return component.dataNotSaveAlert().then((result) => {
        // If user confirmed, allow navigation
        return result;
      });
    }
  } else if(component instanceof SheetsComponent){
    if(component.canNavigate()){
      return component.sheetNotSaveAlert().then((result) => {
        return result;
      });
    }
  } else if(component instanceof SheetsdashboardComponent){
    if(component.canNavigate()){
      return component.dashboardNotSaveAlert().then((result) => {
        return result;
      });
    }
  }

  // If gotoSheetButtonDisable is true, allow navigation by default
  return true;
};
