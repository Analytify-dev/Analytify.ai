import { ChangeDetectorRef, Component, OnInit, ViewChild } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { NgbModal, NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { WorkbenchService } from '../workbench.service';
import Swal from 'sweetalert2';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { InsightsButtonComponent } from '../insights-button/insights-button.component';
import { ViewTemplateDrivenService } from '../view-template-driven.service';
import { NgSelectModule } from '@ng-select/ng-select';
import { ToastrService } from 'ngx-toastr';
import { LoaderService } from '../../../shared/services/loader.service';

@Component({
  selector: 'app-landingpage',
  standalone: true,
  imports: [NgbModule,CommonModule,FormsModule,InsightsButtonComponent,NgSelectModule],
  templateUrl: './landingpage.component.html',
  styleUrl: './landingpage.component.scss'
})

export class LandingpageComponent implements OnInit {
searchDbName:any
userSheetsList :any[] =[];
savedDashboardList: any[] =[];
demoDashboardList: any[] =[];
connectionList:any[]=[];
savedQueryList:any[]=[];
showAllSheets = true;
showAllDasboards = true;
showAllSavedQueries = true;
wholeSearch:any
viewDatabbses = false;
viewSheets = false;
viewDashboardList = false;
viewCustomSql = false;
roleDetails = [] as any;
selectedRoleIds = [] as any;
selectedRoleIdsToNumbers = [] as any;
usersOnSelectedRole =[] as any;
selectedUserIds = [] as any;
selectedUserIdsToNumbers = [] as any;
dashboardPropertyTitle :any;
dashboardPropertyId:any;
dashboardId :any;
createUrl =false;
shareAsPrivate = false;
UrlCopy:string | null = null;
publicUrl:any;
port:any;
host:any;
publishedDashboard = false;
testVariableToChange! : string ;
@ViewChild('propertiesModal') propertiesModal : any;
@ViewChild('sampleDashboardPropertiesModal') sampleDashboardPropertiesModal : any;


constructor(private router:Router,private workbechService:WorkbenchService,private templateService:ViewTemplateDrivenService,public modalService:NgbModal,private cdr: ChangeDetectorRef,private toasterservice:ToastrService,private loaderService : LoaderService){
  localStorage.setItem('QuerySetId', '0');
  localStorage.setItem('customQuerySetId', '0');
  this.viewDatabbses=this.templateService.viewDtabase();
  this.viewSheets = this.templateService.viewSheets();
  this.viewDashboardList = this.templateService.viewDashboard();
  this.viewCustomSql = this.templateService.viewCustomSql();
}

ngOnInit(){
  this.loaderService.hide();
  if(this.viewDatabbses){
    this.getDbConnectionList();
  }if(this.viewSheets){
    this.getuserSheets();
  }if(this.viewDashboardList){
    this.getuserDashboardsList();
  }if(this.viewCustomSql){
  this.getSavedQueries();
  }
  this.getHostAndPort();
}
getHostAndPort(): void {
  const { hostname, port } = window.location;
  this.host = hostname;
  this.port = port;
  console.log('port',this.port,'host',this.host)
}
totalSearch(){
  this.getuserSheets();
  this.getuserDashboardsList();
  this.getSavedQueries();
}
getDbConnectionList(){
  const Obj ={
    search : this.searchDbName
  }
  if(Obj.search === '' || Obj.search === null){
    delete Obj.search;
  }
  this.workbechService.getdatabaseConnectionsList(Obj).subscribe({
    next:(data)=>{
      this.connectionList = data.sheets
      console.log('jdhcvjsh',this.connectionList);

     },
    error:(error)=>{
      console.log(error);
      Swal.fire({
        icon: 'error',
        title: 'oops!',
        text: error.error.message,
        width: '400px',
      })
    }
  })
}
getuserSheets(){
  const Obj ={
    search:this.wholeSearch,
    page_count:'12'
  }
  if(Obj.search === '' || Obj.search === null || Obj.search === ' '){
    delete Obj.search;
  }
  this.workbechService.getUserSheetListPut(Obj).subscribe(
    {
      next:(data:any) =>{
        this.userSheetsList=data?.sheets
        console.log(this.userSheetsList)

      },
      error:(error:any)=>{
      console.log(error);
      Swal.fire({
        icon: 'error',
        title: 'oops!',
        text: error.error.message,
        width: '400px',
      })
    }
    })
}
getuserDashboardsList(){
  const Obj ={
    search:this.wholeSearch,
    page_count:'12'

  }
  if(Obj.search === ' ' || Obj.search === null || Obj.search === ''){
    delete Obj.search;
  }
  this.workbechService.getuserDashboardsListput(Obj).subscribe(
    {
      next:(data:any) =>{
        this.savedDashboardList=data.sheets;
        this.demoDashboardList = data.sample_dashboards;
        console.log(this.savedDashboardList)

      },
      error:(error:any)=>{
      console.log(error);
      Swal.fire({
        icon: 'error',
        title: 'oops!',
        text: error.error.message,
        width: '400px',
      })
    }
    })
}
getSavedQueries(){
  const Obj ={
    search : this.wholeSearch,
    page_count:'12'

  }
  if(Obj.search === ' ' || Obj.search === null || Obj.search === ''){
    delete Obj.search;
  }
  this.workbechService.getSavedQueryList(Obj).subscribe({
    next:(data)=>{
      console.log(data);
      this.savedQueryList = data?.sheets
     },
    error:(error)=>{
      console.log(error);
      Swal.fire({
        icon: 'error',
        title: 'oops!',
        text: error.error.message,
        width: '400px',
      })
    }
  }) 
}
viewDashboard(serverId:any,querysetId:any,dashboardId:any){
  // const encodedServerId = btoa(serverId.toString());
  // const encodedQuerySetId = btoa(querysetId.toString());
  this.loaderService.show();
  const encodedDashboardId = btoa(dashboardId.toString());

  this.router.navigate(['/analytify/home/sheetsdashboard/'+encodedDashboardId])
}
viewSheet(serverId:any,querysetId:any,sheetId:any){
  this.loaderService.show();
  const encodedQuerySetId = btoa(querysetId.toString());
  const encodedSheetId = btoa(sheetId.toString());

  // if (serverId === null || serverId ==='') {
  //   const encodedFileId = btoa(fileId.toString());
  //   this.router.navigate(['/insights/home/fileId/sheets/'+encodedFileId+'/'+encodedQuerySetId+'/'+encodedSheetId])

  // }
  //  if(fileId === null || fileId === ''){
    const encodedServerId = btoa(serverId.toString());
    this.router.navigate(['/analytify/home/sheets/'+encodedServerId+'/'+encodedQuerySetId+'/'+encodedSheetId])

  // }
 
}

 sheetsRoute(){
    this.loaderService.show();
    this.router.navigate(['/analytify/sheets'])  
  }
  newConnections(){
    this.loaderService.show();
    this.router.navigate(['analytify/datasources/new-connections']) 
  }
  goToConnections(){
    this.router.navigate(['analytify/datasources/view-connections']) 

  }
  getTablesFromConnectedDb(dbId:any){
    // const encodedId = btoa(id.toString());
    // this.router.navigate(['/insights/database-connection/tables/'+encodedId]);
    this.loaderService.show();
    // if(dbId === null){
    //   const encodedId = btoa(fileId.toString());
    //   this.router.navigate(['/insights/database-connection/files/tables/'+encodedId]);
    //   }
      // if(fileId === null){
        const encodedId = btoa(dbId.toString());
        this.router.navigate(['/analytify/database-connection/tables/'+encodedId]);
        // }
  }
  deleteDashboard(dashboardId:any){
    Swal.fire({
      title: 'Are you sure?',
      text: "You won't be able to revert this!",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Yes, delete it!'
    }).then((result)=>{
      if(result.isConfirmed){
        this.workbechService.deleteDashboard(dashboardId)
        .subscribe(
          {
            next:(data:any) => {
              console.log(data);      
              if(data){
                // Swal.fire({
                //   icon: 'success',
                //   title: 'Deleted!',
                //   text: 'Dashboard Deleted Successfully',
                //   width: '400px',
                // })
                this.toasterservice.success('Dashboard Deleted Successfullyy','success',{ positionClass: 'toast-top-right'});
              }
              this.getuserDashboardsList();
            },
            error:(error:any)=>{
              Swal.fire({
                icon: 'warning',
                text: error.error.message,
                width: '300px',
              })
              console.log(error)
            }
          } 
        )
      }})
  }
  deleteSheet(serverId:any,qurysetId:any,sheetId:any){
    const obj ={
      sheet_id:sheetId,
    }
    this.workbechService.deleteSheetMessage(obj)
    .subscribe(
      {
        next:(data:any) => {
          console.log(data);      
          if(data){
            Swal.fire({
              title: 'Are you sure?',
              text: data.message,
              icon: 'warning',
              showCancelButton: true,
              confirmButtonColor: '#3085d6',
              cancelButtonColor: '#d33',
              confirmButtonText: 'Yes, delete it!'
            }).then((result)=>{
              if(result.isConfirmed){
                const idToPass =serverId 
                this.workbechService.deleteSheet(idToPass,qurysetId,sheetId)
                .subscribe(
                  {
                    next:(data:any) => {
                      console.log(data);      
                      if(data){
                        // Swal.fire({
                        //   icon: 'success',
                        //   title: 'Deleted!',
                        //   text: 'Sheet Deleted Successfully',
                        //   width: '400px',
                        // })
                        this.toasterservice.success('Sheet Deleted Successfully','success',{ positionClass: 'toast-top-right'});
                      }
                      this.getuserSheets();
                    },
                    error:(error:any)=>{
                      Swal.fire({
                        icon: 'warning',
                        text: error.error.message,
                        width: '300px',
                      })
                      console.log(error)
                    }
                  } 
                )
              }})
          }
        },
        error:(error:any)=>{
          Swal.fire({
            icon: 'warning',
            text: error.error.message,
            width: '300px',
          })
          console.log(error)
        }
      } 
    )
  }


  deleteSavedQuery(qrysetId:any){
    const obj ={
      queryset_id:qrysetId,
    }
    this.workbechService.deleteSavedQueryMessage(obj)
    .subscribe(
      {
        next:(data:any) => {
          console.log(data);      
          if(data){
            Swal.fire({
              title: 'Are you sure?',
              text: data.message,
              icon: 'warning',
              showCancelButton: true,
              confirmButtonColor: '#3085d6',
              cancelButtonColor: '#d33',
              confirmButtonText: 'Yes, delete it!'
            }).then((result)=>{
              if(result.isConfirmed){
                this.workbechService.deleteSavedQuery(qrysetId)
                .subscribe(
                  {
                    next:(data:any) => {
                      console.log(data);      
                      if(data){
                        // Swal.fire({
                        //   icon: 'success',
                        //   title: 'Deleted!',
                        //   text: 'Query Deleted Successfully',
                        //   width: '400px',
                        // })
                        this.toasterservice.success('Query Deleted Successfully','success',{ positionClass: 'toast-top-right'});
                      }
                      this.getSavedQueries();
                    },
                    error:(error:any)=>{
                      Swal.fire({
                        icon: 'warning',
                        text: error.error.message,
                        width: '300px',
                      })
                      console.log(error)
                    }
                  } 
                )
              }})
          }
        },
        error:(error:any)=>{
          Swal.fire({
            icon: 'warning',
            text: error.error.message,
            width: '300px',
          })
          console.log(error)
        }
      } 
    )


  }

  viewAllSheets(){
    this.router.navigate(['/analytify/sheets-dashboard']) 

  }
  viewAllDashboards(){
    this.router.navigate(['/analytify/dashboards']) 

  }
  viewAllSavedQueries(){
    this.router.navigate(['/analytify/saved-queries']) 

  }
  gotoSavedQuery(dbId:any,qrySetId:any,isCustomSql:boolean,dsQrySetId:any){
    if(isCustomSql){ 
    // if(fileId === null){
    const encodedServerId = btoa(dbId.toString());
    const encodedQuerySetId = btoa(qrySetId.toString());

    this.router.navigate(['analytify/database-connection/savedQuery/'+encodedServerId+'/'+encodedQuerySetId])
    // }
    // if(dbId === null){
    //   const encodedFileId = btoa(fileId.toString());
    //   const encodedQuerySetId = btoa(qrySetId.toString());
  
    //   this.router.navigate(['insights/database-connection/savedQuery/fileId/'+encodedFileId+'/'+encodedQuerySetId])
    // }

  }
  else{
    const encodeddbId = btoa(dbId?.toString());
    const encodedqurysetId = btoa(qrySetId.toString());
    // const encodedFileId = btoa(fileId?.toString());
    // this.router.navigate(['/insights/database-connection/sheets/'+encodeddbId+'/'+encodedqurysetId])

    const idToPass = encodeddbId;
    const fromSource = 'dbId';

    const encodedDsQuerySetId = dsQrySetId === null || dsQrySetId === undefined 
  ? btoa('null') 
  : btoa(dsQrySetId.toString()); 
   this.router.navigate(['/analytify/database-connection/sheets/'+idToPass+'/'+encodedqurysetId+'/'+encodedDsQuerySetId])
  }
  }
  // gotoSavedQuery(dbId:any,qrySetId:any,fileId:any){
  //   // const encodedServerId = btoa(dbId.toString());
  //   // const encodedQuerySetId = btoa(qrySetId.toString());

  //   // this.router.navigate(['insights/database-connection/savedQuery/'+encodedServerId+'/'+encodedQuerySetId])
  //   this.loaderService.show();
  //   if(fileId === null){
  //     const encodedServerId = btoa(dbId.toString());
  //     const encodedQuerySetId = btoa(qrySetId.toString());
  
  //     this.router.navigate(['insights/database-connection/savedQuery/dbId/'+encodedServerId+'/'+encodedQuerySetId])
  //     }
  //     if(dbId === null){
  //       const encodedFileId = btoa(fileId.toString());
  //       const encodedQuerySetId = btoa(qrySetId.toString());
    
  //       this.router.navigate(['insights/database-connection/savedQuery/fileId/'+encodedFileId+'/'+encodedQuerySetId])
  //     }
  // }
  loadNewDashboard(){
    this.loaderService.show();
    this.router.navigate(['/analytify/sheetsdashboard'])
    }
  viewSampleDashbaordPropertiesTab(name: any, dashboardId: any) {
    this.modalService.open(this.sampleDashboardPropertiesModal);
    this.dashboardPropertyTitle = name;
    this.dashboardPropertyId = dashboardId;
    this.dashboardId = dashboardId;
    this.publishedDashboard = false;
  }
  viewPropertiesTab(name :any,dashboardId:any){
  this.modalService.open(this.propertiesModal);
  this.getRoleDetailsDshboard();
  this.dashboardPropertyTitle = name;
  this.dashboardPropertyId = dashboardId;
  this.dashboardId = dashboardId;
  this.publishedDashboard = false;
  this.shareAsPrivate = false;
  this.getAddedDashboardProperties();
  }
  getAddedDashboardProperties(){
    this.workbechService.getAddedDashboardProperties(this.dashboardId).subscribe({
      next:(data)=>{
        this.selectedRoleIds = data.roles.map((role: any) => role.role);
        this.selectedUserIds = data.users.map((user:any)=>user.username);
        console.log('savedrolesandusers',data);
        this.selectedRoleIdsToNumbers = data.roles?.map((role:any) => role.id);
        this.selectedUserIdsToNumbers = data.users?.map((user:any) => user.user_id);
       },
      error:(error)=>{
        console.log(error);
        Swal.fire({
          icon: 'error',
          title: 'oops!',
          text: error.error.message,
          width: '400px',
        })
      }
    }) 
  }

getRoleDetailsDshboard(){
  this.workbechService.getRoleDetailsDshboard().subscribe({
    next:(data)=>{
      console.log('dashboardroledetails',data);
      this.roleDetails = data;
      // this.getUsersforRole();
     },
    error:(error)=>{
      console.log(error);
      Swal.fire({
        icon: 'error',
        title: 'oops!',
        text: error.error.message,
        width: '400px',
      })
    }
  }) 
}
getUsersforRole(){
  const obj ={
    role_ids:this.selectedRoleIdsToNumbers
  }
  this.workbechService.getUsersOnRole(obj).subscribe({
    next:(data)=>{
      this.usersOnSelectedRole = data
      console.log('usersOnselecetdRoles',data);
     },
    error:(error)=>{
      console.log(error);
      Swal.fire({
        icon: 'error',
        title: 'oops!',
        text: error.error.message,
        width: '400px',
      })
    }
  })
}
///share publish
sharePublish(value:any){
console.log(value);
this.testVariableToChange = value;
if(value === 'public'){
  this.createUrl = true;
  this.shareAsPrivate = false
  const publicDashboardId = btoa(this.dashboardId.toString());
  this.publicUrl = 'http://'+this.host+':'+this.port+'/public/dashboard/'+publicDashboardId
  this.publishDashboard();
} else if(value === 'private'){
  this.createUrl = false;
  this.shareAsPrivate = true;
  this.publishedDashboard = false;
}
}
// copyUrl(): void {
//   navigator.clipboard.writeText(this.publicUrl).then(() => {
//     console.log(this.publicUrl);
//     this.toasterservice.success('Link Copied','success',{ positionClass: 'toast-center-center'})
//     // setTimeout(() => this.publicUrl = null, 3000); // Clear message after 3 seconds
//   }).catch(err => {
//     console.error('Could not copy text: ', err);
//     this.publicUrl = 'Failed to copy message.';
//   });
// }

copyUrl(): void {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(this.publicUrl).then(() => {
      console.log(this.publicUrl);
      this.toasterservice.success('Link Copied', 'success', { positionClass: 'toast-center-center' });
    }).catch(err => {
      console.error('Could not copy text: ', err);
      this.fallbackCopyTextToClipboard(this.publicUrl);
    });
  } else {
    // Fallback if navigator.clipboard is not available
    this.fallbackCopyTextToClipboard(this.publicUrl);
  }
}

fallbackCopyTextToClipboard(text: string): void {
  const textArea = document.createElement('textarea');
  textArea.value = text;
  textArea.style.position = 'fixed';  // Avoid scrolling to bottom
  textArea.style.opacity = '0';
  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();
  try {
    const successful = document.execCommand('copy');
    if (successful) {
      this.toasterservice.success('Link Copied', 'success', { positionClass: 'toast-center-center' });
    } else {
      console.error('Fallback: Could not copy text');
    }
  } catch (err) {
    console.error('Fallback: Unable to copy', err);
  }
  document.body.removeChild(textArea);
}
onRolesChange(selected: number[]) {
  this.selectedRoleIds = selected
   this.selectedRoleIdsToNumbers = selected.map(value => Number(value));
  console.log(this.selectedRoleIds);

  // You can store or process the selected values here
}
getSelectedUsers(selected: number[]){
  this.selectedUserIds = selected;
  this.selectedUserIdsToNumbers = this.selectedUserIds.map((value: any) => Number(value));
  console.log(this.selectedUserIds)
  
  // this.selectedUserIds = selected
  }

saveDashboardProperties(){
  const obj ={
    dashboard_id:this.dashboardId,
    role_ids:this.selectedRoleIdsToNumbers,
    user_ids:this.selectedUserIdsToNumbers
  }
  this.workbechService.saveDashboardProperties(obj).subscribe({
    next:(data)=>{
      console.log('properties save',data);
      this.modalService.dismissAll();
      // Swal.fire({
      //   icon: 'success',
      //   title: 'Done!',
      //   text: data.message,
      //   width: '400px',
      // })
      this.toasterservice.success(data.message,'success',{ positionClass: 'toast-top-right'});
     },
    error:(error)=>{
      console.log(error);
      Swal.fire({
        icon: 'error',
        title: 'oops!',
        text: error.error.message,
        width: '400px',
      })
    }
  })
}

publishDashboard(){
  this.workbechService.publishDashbord(this.dashboardPropertyId).subscribe({
    next:(data)=>{
      console.log(data);
      this.toasterservice.success('Dashboard Published','success',{ positionClass: 'toast-center-center'})
      this.publishedDashboard = true;
     },
    error:(error)=>{
      console.log(error);
      Swal.fire({
        icon: 'error',
        title: 'oops!',
        text: error.error.message,
        width: '400px',
      })
    }
  })
}
}
