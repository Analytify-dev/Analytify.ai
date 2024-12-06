import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-page-header',
  templateUrl: './page-header.component.html',
  styleUrls: ['./page-header.component.scss'],
})
export class PageHeaderComponent {
  @Input() title!: string;
  @Input() title1!:string;
  @Input() activeitem!: string;
  @Input() title2!:string;
  @Input() multiLevel = false;
  @Input() title2Route!:string;
  @Input() moduleId:any;

constructor(private route:Router){}

helpRoute(){
  console.log(this.moduleId)
  this.route.navigate([`/insights/help-guide/${this.moduleId}`])
}
  
}
