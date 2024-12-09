import { Component } from '@angular/core';
import { SharedModule } from '../../../shared/sharedmodule';
import { WorkbenchService } from '../workbench.service';
import Swal from 'sweetalert2';
import { CommonModule } from '@angular/common';
import { NgxPaginationModule } from 'ngx-pagination';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ViewTemplateDrivenService } from '../view-template-driven.service';
import { ToastrService } from 'ngx-toastr';
import { LoaderService } from '../../../shared/services/loader.service';

@Component({
  selector: 'app-saved-queries',
  standalone: true,
  imports: [SharedModule,CommonModule,NgxPaginationModule,NgbModule,FormsModule],
  templateUrl: './saved-queries.component.html',
  styleUrl: './saved-queries.component.scss'
})
export class SavedQueriesComponent {
  itemsPerPage!:number;
  pageNo = 1;
  page: number = 1;
  totalItems:any;
  searchName:any;
  savedQueryList:any[]=[];
  gridView = true;
  viewSavedQueries = false;
constructor(private workbechService:WorkbenchService,private route:Router,private viewTemplateService:ViewTemplateDrivenService, private toasterservice:ToastrService,private loaderService:LoaderService){
  this.viewSavedQueries = this.viewTemplateService.viewCustomSql();
}

  ngOnInit(){
    this.loaderService.hide();
    if(this.viewSavedQueries){
    this.getSavedQueries();
    }
  }
  getSavedQueriesSearch(){
    this.pageNo=1;
    this.getSavedQueries()
  }
  getSavedQueries(){
    const Obj ={
      search : this.searchName,
      page_no : this.pageNo,
      page_count:this.itemsPerPage
    }
    if(Obj.search == '' || Obj.search == null){
      delete Obj.search;
    }
    this.workbechService.getSavedQueryList(Obj).subscribe({
      next:(data)=>{
        console.log(data);
        this.savedQueryList = data.sheets;
        this.itemsPerPage = data.items_per_page;
        this.totalItems = data.total_items
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
  pageChangeSavedQueries(page:any){
    this.pageNo=page;
    this.getSavedQueries();
  }
  gotoSavedQuery(dbId:any,qrySetId:any,fileId:any,isCustomSql:boolean,dsQrySetId:any){
    if(isCustomSql){ 
    if(fileId === null){
    const encodedServerId = btoa(dbId.toString());
    const encodedQuerySetId = btoa(qrySetId.toString());

    this.route.navigate(['insights/database-connection/savedQuery/dbId/'+encodedServerId+'/'+encodedQuerySetId])
    }
    if(dbId === null){
      const encodedFileId = btoa(fileId.toString());
      const encodedQuerySetId = btoa(qrySetId.toString());
  
      this.route.navigate(['insights/database-connection/savedQuery/fileId/'+encodedFileId+'/'+encodedQuerySetId])
    }

  }
  else{
    const encodeddbId = btoa(dbId?.toString());
    const encodedqurysetId = btoa(qrySetId.toString());
    const encodedFileId = btoa(fileId?.toString());
    // this.router.navigate(['/insights/database-connection/sheets/'+encodeddbId+'/'+encodedqurysetId])

    const idToPass = fileId ? encodedFileId : encodeddbId;
    const fromSource = fileId ? 'fileId' : 'dbId';

    const encodedDsQuerySetId = dsQrySetId === null || dsQrySetId === undefined 
  ? btoa('null') 
  : btoa(dsQrySetId.toString()); 
   this.route.navigate(['/insights/database-connection/sheets/'+fromSource+'/'+idToPass+'/'+encodedqurysetId+'/'+encodedDsQuerySetId])

    // if (dsQrySetId === null || dsQrySetId === undefined) {
    //   // Encode 'null' to represent a null value
    //  const encodedDsQuerySetId = btoa('null');
    //  this.route.navigate(['/insights/database-connection/sheets/'+fromSource+'/'+idToPass+'/'+encodedqurysetId+'/'+encodedDsQuerySetId])

    // } else {
    //   // Convert to string and encode
    //  const encodedDsQuerySetId = btoa(dsQrySetId.toString());
    //  this.route.navigate(['/insights/database-connection/sheets/'+fromSource+'/'+idToPass+'/'+encodedqurysetId+'/'+encodedDsQuerySetId])
  
    // }
  }
  }
}
