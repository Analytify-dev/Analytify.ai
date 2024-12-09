import { Injectable } from '@angular/core';
import { RolespriviledgesService } from './rolespriviledges.service';

@Injectable({
  providedIn: 'root'
})
export class ViewTemplateDrivenService {
// viewDashboard = false;
// viewSheets = false;
// viewSavedQueries = false;
// viewDbs = false;

  constructor(private rolesprevilgeService:RolespriviledgesService) { }

viewDtabase(){
return this.rolesprevilgeService.userHasPriviledge(4);
}
viewSheets(){
  return this.rolesprevilgeService.userHasPriviledge(20);
}
viewDashboard(){
  return this.rolesprevilgeService.userHasPriviledge(36);
}
viewCustomSql(){
  return this.rolesprevilgeService.userHasPriviledge(54);
}
editDashboard(){
  return this.rolesprevilgeService.userHasPriviledge(37);
}
ViewRoles(){
  return this.rolesprevilgeService.userHasPriviledge(59);
}
viewUsers(){
  return this.rolesprevilgeService.userHasPriviledge(64);
}
//add
addDatasource(){
  return this.rolesprevilgeService.userHasPriviledge(1);
}
addsheet(){
  return this.rolesprevilgeService.userHasPriviledge(17);
}
//edit
editDatasource(){
  return this.rolesprevilgeService.userHasPriviledge(2);
}
editsheet(){
  return this.rolesprevilgeService.userHasPriviledge(18);
}
}
