import { Component, OnInit } from '@angular/core';
import { WorkbenchService } from '../workbench.service';
import Swal from 'sweetalert2';
import { SharedModule } from '../../../shared/sharedmodule';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { NgxPaginationModule, PaginatePipe, PaginationControlsComponent } from 'ngx-pagination';
import { Router } from '@angular/router';
import { InsightsButtonComponent } from '../insights-button/insights-button.component';
import { ViewTemplateDrivenService } from '../view-template-driven.service';
import { ToastrService } from 'ngx-toastr';
import { LoaderService } from '../../../shared/services/loader.service';

@Component({
  selector: 'app-sheets-list-page',
  standalone: true,
  imports: [SharedModule,CommonModule,FormsModule,NgbModule,NgxPaginationModule,InsightsButtonComponent],
  templateUrl: './sheets-list-page.component.html',
  styleUrl: './sheets-list-page.component.scss'
})
export class SheetsListPageComponent implements OnInit {
  sheetName:any;
  savedSheetsList:any[]=[];
  sheetsList : any[] = [];
  selectedSheetList=0;
  itemsPerPage:any;
  pageNo = 1;
  page: number = 1;
  totalItems:any;
  gridView = true;
  viewSheetList = false;
  dbId:any;
  fileId:any;
  qrysetId:any;
  datasourceQuerysetId:any;
  selectedSheet = '0';
constructor(private workbechService:WorkbenchService,private router:Router,private viewTemplateService:ViewTemplateDrivenService,private toasterService:ToastrService,private loaderService:LoaderService){
  this.viewSheetList = this.viewTemplateService.viewSheets()
}

  ngOnInit() {
    this.loaderService.hide();
    if (this.viewSheetList) {
      this.fetchSheetsList();
      // this.getUserSheetsList();
    }
  }
  getValuesForSheetRoute(event:Event){
    // const selectedOption = (event.target as HTMLSelectElement).selectedOptions[0];
    // this.dbId = selectedOption.getAttribute('data-server_id');
    // this.fileId = selectedOption.getAttribute('data-file_id');
    // this.datasourceQuerysetId = selectedOption.getAttribute('data-datasource_queryset_id');
    // this.qrysetId = this.selectedSheetList


      const selectedSheet = (event.target as HTMLSelectElement).value;
      // Check if the 'All' option is selected
      if (selectedSheet === '0') {
        this.selectedSheet = selectedSheet;
        console.log('All sheets selected');
      } else {
        // Here, `selectedSheet` is a string representation, convert it back if needed
        this.selectedSheet = selectedSheet;
        const selectedObject = this.sheetsList.find(sheet => sheet.id === +selectedSheet);
    
        if (selectedObject) {
          this.dbId = selectedObject.hierarchy_id;
          // this.fileId = selectedObject.file_id;
          this.datasourceQuerysetId = selectedObject.datasource_queryset_id;
          this.qrysetId = selectedObject.id
        }
      }    
  }
  loadSelectedSheetList(value:any){
    if(this.selectedSheetList >= 0){
      const pageNo = value === 'fromSelect' ? 1 : this.pageNo;

    const Obj ={
      search:this.sheetName,
      page_no:pageNo,
      page_count:this.itemsPerPage,
      queryset_id:this.selectedSheetList
    } as any
    if(Obj.search == '' || Obj.search == null){
      delete Obj.search;
    }
    if(Obj.page_count == undefined || Obj.page_count == null){
      delete Obj.page_count;
    }
    if(Obj.queryset_id == '0'){
      delete Obj.queryset_id
    }
    this.workbechService.getUserSheetListPutTest(Obj).subscribe(
      {
        next:(data:any) =>{
          this.savedSheetsList=data.sheets
          this.itemsPerPage = data.items_per_page;
          this.totalItems = data.total_items
          console.log('sheetsList',data);
          this.page=this.pageNo
  
  
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
    } else {
      this.getUserSheetsList();
    }
  }

  fetchSheetsList(){
    const Obj ={
      search:this.sheetName,
      page_no:this.pageNo,
      page_count:this.itemsPerPage
    }
    if(Obj.search == '' || Obj.search == null){
      delete Obj.search;
    }
    if(Obj.page_count == undefined || Obj.page_count == null){
      delete Obj.page_count;
    }
    this.workbechService.fetchSheetsListData().subscribe(
      {
        next:(data:any) =>{
          this.sheetsList = data;
          this.itemsPerPage = data.items_per_page;
          this.totalItems = data.total_items
          console.log('sheetsList',data)
          this.selectedSheetList = 0;
          this.loadSelectedSheetList('fromPagechange');
  
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

pageChangegetUserSheetsList(page:any){
this.pageNo=page;
if(this.selectedSheetList !== 0)
{
  this.loadSelectedSheetList('fromPagechange');
}else{
this.getUserSheetsList();
}
}
searchUserList(){
  this.pageNo=1
  this.getUserSheetsList();
}
onChangeofPagecount(count:any){

}
getUserSheetsList(){
  if(this.selectedSheetList !== 0)
    {
      this.loadSelectedSheetList('fromPagechange');
    }else{
  const Obj ={
    search:this.sheetName,
    page_no:this.pageNo,
    page_count:this.itemsPerPage
  }
  if(Obj.search == '' || Obj.search == null){
    delete Obj.search;
  }
  if(Obj.page_count == undefined || Obj.page_count == null){
    delete Obj.page_count;
  }
  this.workbechService.getUserSheetListPut(Obj).subscribe(
    {
      next:(data:any) =>{
        this.savedSheetsList=data.sheets
        this.itemsPerPage = data.items_per_page;
        this.totalItems = data.total_items
        console.log('sheetsList',data)


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
}
viewSheet(serverId:any,querysetId:any,sheetId:any){
  // const encodedServerId = btoa(serverId.toString());
  const encodedQuerySetId = btoa(querysetId.toString());
  const encodedSheetId = btoa(sheetId.toString());


  // if (serverId === null || serverId === '') {
  //   const encodedFileId = btoa(fileId.toString());
  //   this.router.navigate(['/insights/home/fileId/sheets/'+encodedFileId+'/'+encodedQuerySetId+'/'+encodedSheetId])

  // }
  // else if(fileId === null || fileId === ''){
    const encodedServerId = btoa(serverId.toString());
    this.router.navigate(['/analytify/home/sheets/'+encodedServerId+'/'+encodedQuerySetId+'/'+encodedSheetId])

  // }

  // this.router.navigate(['/insights/home/sheets/'+encodedServerId+'/'+encodedQuerySetId+'/'+encodedSheetId])
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
              const idToPass = serverId;

              this.workbechService.deleteSheet(idToPass,qurysetId,sheetId)
              .subscribe(
                {
                  next:(data:any) => {
                    console.log(data);      
                    if(data){
                      this.toasterService.success('Sheet Deleted Successfully','success',{ positionClass: 'toast-top-right'});

                    }
                    this.getUserSheetsList();
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
sheetsRoute(){
  if (this.selectedSheet === '0') {
  this.router.navigate(['/analytify/sheets'])  
  }else{
  // if (this.dbId === null || this.dbId === undefined) {
  //   const encodedFileId = btoa(this.fileId.toString());
  //   const encodedQuerySetId = btoa(this.qrysetId.toString());
  //   if (this.datasourceQuerysetId === null || this.datasourceQuerysetId === undefined) {
  //     // Encode 'null' to represent a null value
  //     const encodedDsQuerySetId = btoa('null');
  //     this.router.navigate(['/insights/sheets/fileId' + '/' + encodedFileId + '/' + encodedQuerySetId + '/' + encodedDsQuerySetId])
  //   }
  //    else {
  //     const encodedDsQuerySetId = btoa(this.datasourceQuerysetId.toString());
  //       this.router.navigate(['/insights/sheets/fileId' + '/' + encodedFileId + '/' + encodedQuerySetId + '/' + encodedDsQuerySetId])
  //     }
  //   } 
  //  else if (this.fileId === undefined || this.fileId === null) {
    const encodedDatabaseId = btoa(this.dbId.toString());
    const encodedQuerySetId = btoa(this.qrysetId.toString());
    if (this.datasourceQuerysetId === null || this.datasourceQuerysetId === undefined) {
      // Encode 'null' to represent a null value
      const encodedDsQuerySetId = btoa('null');
      this.router.navigate(['/analytify/sheets' + '/' + encodedDatabaseId + '/' + encodedQuerySetId + '/' + encodedDsQuerySetId])
    }
    else {
      const encodedDsQuerySetId = btoa(this.datasourceQuerysetId.toString());
        this.router.navigate(['/analytify/sheets' + '/' + encodedDatabaseId + '/' + encodedQuerySetId + '/' + encodedDsQuerySetId])
      }
    } 
  // }
}
}