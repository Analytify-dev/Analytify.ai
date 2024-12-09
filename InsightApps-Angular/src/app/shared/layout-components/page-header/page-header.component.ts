import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

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
}
