import { Component } from '@angular/core';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { SharedModule } from '../../../shared/sharedmodule';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { WorkbenchService } from '../../workbench/workbench.service';
import { FormsModule } from '@angular/forms';
import { HelpGuideQuestionariesComponent } from '../help-guide-questionaries/help-guide-questionaries.component';
import { LoaderService } from '../../../shared/services/loader.service';

@Component({
  selector: 'app-help-guide',
  standalone: true,
  imports: [SharedModule,NgbModule,CommonModule,FormsModule, HelpGuideQuestionariesComponent],
  templateUrl: './help-guide.component.html',
  styleUrl: './help-guide.component.scss'
})
export class HelpGuideComponent {
  defaults = ['Collapse Group Item #1','Collapse Group Item #2','Collapse Group Item #3'];
  isModules : boolean = true;
  userGuideData : any[] = [];
  ModulesData : any[] = [];
  isSearch : boolean = false;
  searchValue : string = '';
  searchData : any[] = [];
  isQuestionary : boolean = false;
  slug : string = '';
  searchErrorMessage : string = '';

  constructor(private router:Router,private route:ActivatedRoute,private workbenchService:WorkbenchService,private loaderService:LoaderService){
    if(this.router.url.includes('/analytify/help-guide/sheets')){
      this.onModule(3);
    }
    if(this.router.url.includes('/analytify/help-guide/datasource')){
      this.onModule(1);
    }
    if(this.router.url.includes('/analytify/help-guide/dashboard')){
      this.onModule(5);
    }
    if(this.router.url.includes('/analytify/help-guide/customSql')){
      this.onModule(2);
    }
    if(this.router.url.includes('/analytify/help-guide/previlages')){
      this.onModule(6);
    }
    }

  ngOnInit(): void {
    // this.router.navigate(['insights/help-guide']);
    this.loaderService.hide();
    this.getModulesData();
  }

  onModule(moduleId:number){
    let object ={
      "module_id":moduleId
    }
    this.workbenchService.getUserHelpGuide(object).subscribe({next: (responce:any) => {
      console.log(responce);
      // window.location.href = window.location.href + '/' + responce.angular_path;
      this.isModules = false;
      this.userGuideData = responce.user_guide_data;
    },
    error: (error) => {
      console.log(error);
    }
  }) 
  }

  getModulesData(){
    this.workbenchService.getModulesData().subscribe({next: (responce:any) => {
      console.log(responce);
      this.ModulesData = responce.data;
    },
    error: (error) => {
      console.log(error);
    }
  })
  }

  goToQuestionary(slug:string){
    this.slug = slug;
    this.isQuestionary = true;
    this.isSearch = false;
    this.isModules = false;
    // this.router.navigate(['/insights/help-guide/'+slug]);
  }

  getSearchData(searchValue : string){
    this.isSearch = true;
    this.isQuestionary = false;
    this.isModules = false;
    let object = {
       "search": searchValue
    }
    this.workbenchService.getUserHelpGuideSearch(object).subscribe({next: (responce:any) => {
      console.log(responce);
      this.searchErrorMessage = '';
      this.searchData = responce.user_guide_data;
    },
    error: (error) => {
      this.searchErrorMessage = error.error.message;
      this.searchData = [];
      console.log(error);
    }
  });
  // this.router.navigate(['insights/help-guide'], { queryParams: { search: searchValue } });
  }
}
