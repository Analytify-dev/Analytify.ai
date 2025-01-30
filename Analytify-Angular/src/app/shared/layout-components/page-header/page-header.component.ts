import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
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
  @Input() isPublicUrl! : boolean;
  @Output() btnClickEvent: EventEmitter<any>;

constructor(private route:Router){
  this.btnClickEvent = new EventEmitter();
}

helpRoute(){
  console.log(this.moduleId)
  this.route.navigate([`/analytify/help-guide/${this.moduleId}`])
}
routeHome(){
  this.route.navigate(['/analytify/home'])
}

toggleSidebar(){
  this.btnClickEvent.emit();
}
}
