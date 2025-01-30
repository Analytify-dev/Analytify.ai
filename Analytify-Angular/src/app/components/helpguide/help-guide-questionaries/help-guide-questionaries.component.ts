import { Component, Input } from '@angular/core';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { SharedModule } from '../../../shared/sharedmodule';
import { ActivatedRoute, Router } from '@angular/router';
import { WorkbenchService } from '../../workbench/workbench.service';
import { CommonModule } from '@angular/common';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-help-guide-questionaries',
  standalone: true,
  imports: [SharedModule,NgbModule,CommonModule,FormsModule],
  templateUrl: './help-guide-questionaries.component.html',
  styleUrl: './help-guide-questionaries.component.scss'
})
export class HelpGuideQuestionariesComponent {
  @Input() slug : string = '';
  userGuideData : any[]=[];
  ModulesData : any[] = [];
  questionariesData : any[] = [];
  searchValue : string = '';

  constructor(private router:Router,private route:ActivatedRoute,private workbenchService:WorkbenchService,private sanitizer: DomSanitizer){
    // if (route.snapshot.params['slug']) {
    //    this.slug = route.snapshot.params['slug'];
    // }
  }
  ngOnInit(): void {
    // this.getModulesData();
    this.getQuestionary();
  }

  getQuestionary(){
    let object ={
      "slug": this.slug
    }
    this.workbenchService.getUserHelpGuide(object).subscribe({next: (responce:any) => {
      console.log(responce);
      this.userGuideData = responce.user_guide_data;
      this.userGuideData.forEach((data:any)=>{
        data.link = this.sanitizeUrl(data.link);
      })
      this.getModulesData();
    },
    error: (error) => {
      console.log(error);
    }
  }) 
  }

  sanitizeUrl(url: string): SafeResourceUrl {
    return this.sanitizer.bypassSecurityTrustResourceUrl(url);
  }

  getModulesData(){
    this.workbenchService.getModulesData().subscribe({next: (responce:any) => {
      console.log(responce);
      this.ModulesData = responce.data;
      this.ModulesData.forEach((data)=>{
        if(data.id == this.userGuideData[0].module_id){
          this.getQuestionaries(data.id);
        }
      })
    },
    error: (error) => {
      console.log(error);
    }
  })
  }

  getQuestionaries(moduleId : number){
    let object ={
      "module_id":moduleId
    }
    this.workbenchService.getUserHelpGuide(object).subscribe({next: (responce:any) => {
      console.log(responce);
      this.questionariesData = responce.user_guide_data;
    },
    error: (error) => {
      console.log(error);
    }
  })
  }

  changeQuestionay(slug : string){
    this.slug = slug;
    this.getQuestionary();
  }

  getSearchData(searchValue : string){
    let object = {
       "search": searchValue
    }
    this.workbenchService.getUserHelpGuideSearch(object).subscribe({next: (responce:any) => {
      console.log(responce);
    },
    error: (error) => {
      console.log(error);
    }
  })
  }
}
