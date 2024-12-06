import { Component, ElementRef, Renderer2 } from '@angular/core';
import { NavService } from '../../services/navservice';
import * as switcher from '../switcher/switcher'
import { WorkbenchService } from '../../../components/workbench/workbench.service';
@Component({
  selector: 'app-switcher',
  templateUrl: './switcher.component.html',
  styleUrls: ['./switcher.component.scss']
})
export class SwitcherComponent {
  constructor(
    private renderer: Renderer2,
    private elementRef: ElementRef,
    private navServices: NavService,
    private workbenchService: WorkbenchService
  ) {
    
    const htmlElement =
    this.elementRef.nativeElement.ownerDocument.documentElement;
    // this.renderer.setAttribute(htmlElement, 'data-toggled', 'close');
  
  this.renderer.setAttribute(htmlElement, 'data-menu-styles','dark');

  }
  body = document.querySelector('body');

  SwitcherClose(){
  //   if (document.querySelector(".offcanvas-end")?.classList.contains("show")) {
  //     document.querySelector(".offcanvas-end")?.classList.remove("show");
  //     document.querySelector(".switcher-backdrop")?.classList.remove("d-block");
  //     document.querySelector(".switcher-backdrop")?.classList.add("d-none");
  // }
    document.querySelector('.offcanvas-end')?.classList.remove('show')
    document.querySelector("body")!.classList.remove("overflow:hidden");
    document.querySelector("body")!.classList.remove("padding-right:4px");
    document.querySelector(".switcher-backdrop")?.classList.remove("d-block");
    document.querySelector(".switcher-backdrop")?.classList.add("d-none");
  }
  themeChange(type: string, type1: string) {
    const htmlElement =
      this.elementRef.nativeElement.ownerDocument.documentElement;
    this.renderer.setAttribute(htmlElement, 'data-theme-mode', type);
    localStorage.setItem('insightappsdarktheme', type);
    localStorage.removeItem("insightapps-background-mode-body");
    localStorage.removeItem("insightapps-background-mode-dark");
    localStorage.removeItem("insightapps-background-mode-light");
    localStorage.removeItem("insightapps-background-mode-formcontrol");
    localStorage.removeItem("insightapps-background-mode-inputBorder");
    this.elementRef.nativeElement.ownerDocument.documentElement?.removeAttribute(
      'style'
    );
    this.renderer.setAttribute(htmlElement, 'data-header-styles', type1);
    localStorage.setItem('insightappsHeader', type1);
    if (localStorage.getItem('insightappsdarktheme') == 'light') {
      localStorage.removeItem("insightapps-background-mode-body");
      localStorage.removeItem("insightapps-background-mode-dark");
      localStorage.removeItem("insightapps-background-mode-light");
      localStorage.removeItem("insightapps-background-mode-formcontrol");
      localStorage.removeItem("insightapps-background-mode-inputBorder");
      this.elementRef.nativeElement.ownerDocument.documentElement?.removeAttribute(
        'style'
      );

    }
    if (localStorage.getItem('insightappsHeader') == 'light') {
      this.elementRef.nativeElement.ownerDocument.documentElement?.removeAttribute('style');
      this.body = document.querySelector('body');
      this.body?.classList.remove('dark');
    }
  }
  DirectionsChange(type: string) {
    // this.elementRef.nativeElement.ownerDocument.documentElement?.setAttribute('dir', type);
    // localStorage.setItem('insightapps-dir', type);
    const htmlElement =
      this.elementRef.nativeElement.ownerDocument.documentElement;
    this.renderer.setAttribute(htmlElement, 'dir', type);
    localStorage.setItem('insightapps-dir', type);
  }
  NavigationChange(type: string) {
    const htmlElement = this.elementRef.nativeElement.ownerDocument.documentElement;
    this.renderer.setAttribute(htmlElement, 'data-nav-layout', type);
    if(type == 'horizontal'){
      this.renderer.setAttribute(htmlElement, 'data-nav-style', 'menu-click');
      this.renderer.removeAttribute(htmlElement, 'data-vertical-style');

      localStorage.removeItem('insightappsverticalstyles');

      const menuclickclosed = document.getElementById(
        'switcher-menu-click'
      ) as HTMLInputElement;
      menuclickclosed.checked = true;
    
    //     const mainContentElement = document.querySelector(".main-content") as HTMLElement | null;
    //     if (mainContentElement) {
    //         mainContentElement.click();
    
    }else{
    }
    localStorage.setItem('insightapps-nav-mode', type);
  }
  Menustyles(type: string, type1: string) {
    const htmlElement =
      this.elementRef.nativeElement.ownerDocument.documentElement;
    localStorage.setItem('insightappsMenu', type);
    this.renderer.setAttribute(htmlElement, 'data-toggled', type1);
    localStorage.setItem('insightappsMenu-toggled', type1);
    this.renderer.setAttribute(htmlElement, 'data-toggled', type1);
    localStorage.setItem('insightappsMenu-toggled', type1);
  }
  menuItems!: any;
  Menus(type: string, type1: string) {
    this.navServices.items.subscribe((items) => {
      this.menuItems = items;
    });
    const htmlElement =
      this.elementRef.nativeElement.ownerDocument.documentElement;
    this.renderer.setAttribute(htmlElement, 'data-nav-style', type1);
    localStorage.setItem('insightappsMenu', type1);
    localStorage.setItem('insightappsMenu-toggled', type);
    this.renderer.setAttribute(htmlElement, 'data-toggled', type);
    this.renderer.removeAttribute(htmlElement, 'data-vertical-style');
    localStorage.removeItem('insightappsverticalstyles');
    localStorage.removeItem('insightappsverticalstyles-toggled');


  }
  SideMenus(dataToggleClass: string, datatVerticalStyles: string) {
    this.setAttr('data-vertical-style',datatVerticalStyles);
    this.removeAttr('data-nav-style');
    if (datatVerticalStyles == 'doublemenu' && !document.querySelector('.double-menu-active')) {
        this.setAttr('data-toggled','double-menu-close');
    } else {
      this.setAttr('data-toggled', dataToggleClass);
    }
    localStorage.setItem('insightappsverticalstyles', datatVerticalStyles);
    localStorage.setItem('insightappsverticalstyles-toggled', dataToggleClass);
    this.navServices.items.subscribe((items) => {
      this.menuItems = items;
    });

     
   
    
  }
  setAttr(key:string, value:string):void{
    const htmlElement = this.elementRef.nativeElement.ownerDocument.documentElement;
    this.renderer.setAttribute(htmlElement, key, value);
    return;
  }
  removeAttr(key:string):void{
    const htmlElement = this.elementRef.nativeElement.ownerDocument.documentElement;
    this.renderer.removeAttribute(htmlElement, key);
    return;
  }
  PageChange(type: string) {
    const htmlElement =
      this.elementRef.nativeElement.ownerDocument.documentElement;
    this.renderer.setAttribute(htmlElement, 'data-page-style', type);
    localStorage.setItem('insightapps-page-mode', type);
  }
  doubleMenuActive: boolean = false;

  WidthChange(type: string) {
    const htmlElement =
      this.elementRef.nativeElement.ownerDocument.documentElement;
    this.renderer.setAttribute(htmlElement, 'data-width', type);
    localStorage.setItem('insightapps-width-mode', type);
  }
  MenuChange(type: string) {
    const htmlElement =
      this.elementRef.nativeElement.ownerDocument.documentElement;
    this.renderer.setAttribute(htmlElement, 'data-menu-position', type);
    localStorage.setItem('insightapps-menu-position', type);
  }
  menuTheme(type: string) {
    const htmlElement =
      this.elementRef.nativeElement.ownerDocument.documentElement;
    this.renderer.setAttribute(htmlElement, 'data-menu-styles', type);
    localStorage.setItem('insightapps-menu-mode', type); 
    if(type =="dark"){
      const darkMenu = document.getElementById(
        'switcher-menu-dark'
      ) as HTMLInputElement;
      if (darkMenu) {
        darkMenu.checked = true;
      }
    }

  }
  HeaderChange(type: string) {
    const htmlElement =
      this.elementRef.nativeElement.ownerDocument.documentElement;
    this.renderer.setAttribute(htmlElement, 'data-header-position', type);
    localStorage.setItem('insightapps-header-position', type);
  }
  headerTheme(type: string) {
    const htmlElement =
      this.elementRef.nativeElement.ownerDocument.documentElement;
    this.renderer.setAttribute(htmlElement, 'data-header-styles', type);
    localStorage.setItem('insightappsHeader', type);
  }
  closeMenu(type1: any) {
    if (type1 == 'icon-hover' || type1 == 'menu-hover') {
      this.menuItems?.forEach((a: any) => {
        if (this.menuItems) {
          a.active = false;
        }
        a?.children?.forEach((b: any) => {
          if (a.children) {
            b.active = false;
          }
        });
      });
    }
  }

  primary(type: string) {
    this.elementRef.nativeElement.ownerDocument.documentElement?.style.setProperty('--primary-rgb', type);
    localStorage.setItem('insightapps-primary-mode', type);
    // localStorage.removeItem('insightappslight-primary-color');
  }
  background(bodyBg: string, darkBg: string,lightBg:string,inputBorder:string,formControl:string, event: string, type1: string) {
    this.elementRef.nativeElement.ownerDocument.documentElement?.style.setProperty('--body-bg-rgb', bodyBg);
    this.elementRef.nativeElement.ownerDocument.documentElement?.style.setProperty('--body-bg-rgb2', darkBg);
    this.elementRef.nativeElement.ownerDocument.documentElement?.style.setProperty('--light-rgb', lightBg);
    this.elementRef.nativeElement.ownerDocument.documentElement?.style.setProperty('--form-control-bg', formControl);
    this.elementRef.nativeElement.ownerDocument.documentElement?.style.setProperty('--input-border', inputBorder);

    localStorage.setItem('insightapps-background-mode-body', bodyBg);
    localStorage.setItem('insightapps-background-mode-dark', darkBg);
    localStorage.setItem('insightapps-background-mode-light', lightBg);
    localStorage.setItem('insightapps-background-mode-formcontrol', formControl);
    localStorage.setItem('insightapps-background-mode-inputBorder', inputBorder);


    this.elementRef.nativeElement.ownerDocument.documentElement?.setAttribute('data-theme-mode', event);
    localStorage.setItem('insightappsdarktheme', event);

    this.elementRef.nativeElement.ownerDocument.documentElement?.setAttribute('data-header-styles', type1);
    localStorage.setItem('insightappsHeader', type1);

    localStorage.removeItem("bodyBgRGB2");
    localStorage.removeItem("bodyBgRGB");
    localStorage.removeItem("bodylightRGB")
    localStorage.removeItem("insightappslight-background-formcontrol")
    localStorage.removeItem("insightappslight-background-inputBorder")



  }

  //primary theme change
  public dynamicLightPrimary(data: any): void {
    this.color1 = data.color;

    const dynamicPrimaryLight = document.querySelectorAll(
      'button.pcr-button'
    );

    switcher.dynamicLightPrimaryColor(dynamicPrimaryLight, this.color1);

    localStorage.setItem('insightappslight-primary-color', switcher.hexToRgba(this.color1) || '');
    localStorage.setItem('insightappslight-mode', 'true');
    this.body?.classList.remove('transparent-mode');

    // Adding
    this.body?.classList.add('light-mode');

    // Removing
    this.body?.classList.remove('dark');
    this.body?.classList.remove('bg-img1');

    // removing data from session storage

    // switcher.checkOptions();
    localStorage.removeItem('insightapps-primary-mode');
  }

  //background theme change
  public color4 = '#6c5ffc';
  public dynamicTranparentBgPrimary(data: any): void {
    this.color4 = data.color;
    const dynamicPrimaryBgTrasnsparent = document.querySelectorAll(
      'button.pcr-button'
    );

    switcher.dynamicBgTrasnsparentPrimaryColor(
      dynamicPrimaryBgTrasnsparent,
      this.color4
    );

    // Adding
    localStorage.setItem('bodyBgRGB', switcher.hexToRgba(this.color4) || '');
    localStorage.setItem('bodyBgRGB2', switcher.hexToRgba1(this.color4) || '');
    localStorage.setItem('bodylightRGB', switcher.hexToRgba1(this.color4) || '');
    localStorage.setItem('insightappsdarktheme', 'dark');
    localStorage.setItem('insightappsHeader', 'dark');
    localStorage.setItem('insightappslight-background-formcontrol', switcher.hexToRgba1(this.color4) || '');


    // Removing
    const html: any = this.elementRef.nativeElement.ownerDocument.documentElement;
    html.setAttribute('data-header-styles', 'dark');
    html.setAttribute('data-theme-mode', 'dark');

    localStorage.removeItem('insightappsDark');
    localStorage.removeItem('insightappsLight');

    this.elementRef.nativeElement.ownerDocument.documentElement?.classList.add('dark');
    document
      .querySelector('.app-header')
      ?.classList.add(
        'hor-header',
        'fixed-header',
        'visible-title',
        'stickyClass'
      );

    localStorage.removeItem('insightapps-header-styles');
    localStorage.removeItem('insightappslight-primary-hover');
    localStorage.removeItem('insightappslight-primary-border');
    localStorage.removeItem('insightappsdark-primary-color');
    localStorage.removeItem('insightappstransparent-bgImg-primary-color');
    localStorage.removeItem('insightappsBgImage');
    localStorage.removeItem("insightapps-background-mode-body")
    localStorage.removeItem("insightapps-background-mode-dark")
  }

  color1 = '#1457e6';
  color = '#1ae715';

  ImageTheme(type: string) {
    this.elementRef.nativeElement.ownerDocument.documentElement?.setAttribute('data-bg-img', type);
    localStorage.setItem('insightapps-image', type);
  }
  reset() {
    // localStorage.clear();
    const html: any = this.elementRef.nativeElement.ownerDocument.documentElement;
    const body: any = document.querySelector('body');
    html.style = '';
    html.setAttribute('data-theme-mode', 'light');
    html.setAttribute('data-vertical-style', 'overlay');
    html.setAttribute('dir', 'ltr');
    html.setAttribute('data-nav-layout', 'vertical');
    html.removeAttribute('data-page-style', 'regular');
    html.removeAttribute('data-width', 'full-width');
    html.removeAttribute('data-menu-position', 'fixed');
    html.removeAttribute('data-header-position', 'fixed');
    html.setAttribute('data-header-styles', 'light');
    html.setAttribute('data-menu-styles', 'dark');
    html.removeAttribute('data-bg-img', 'dark');
    html.removeAttribute('data-toggled', 'overlay');
    body.removeAttribute('data-theme-mode');
    html.removeAttribute("data-nav-style")
    localStorage.setItem('insightapps-menu-mode', 'dark');
    const darkMenu = document.getElementById(
      'switcher-menu-dark'
    ) as HTMLInputElement;
    if (darkMenu) {
      darkMenu.checked = true;
    }
    const menuclickclosed = document.getElementById(
      'switcher-menu-click'
    ) as HTMLInputElement;
    if (menuclickclosed) {
      menuclickclosed.checked = false;
    }
    const lightclickchecked = document.getElementById(
      'switcher-light-theme'
    ) as HTMLInputElement;
    if (lightclickchecked) {
      lightclickchecked.checked = true;
    }

    const ltrclickchecked = document.getElementById(
      'switcher-ltr'
    ) as HTMLInputElement;
    if (ltrclickchecked) {
      ltrclickchecked.checked = true;
    }

    const verticalclickchecked = document.getElementById(
      'switcher-vertical'
    ) as HTMLInputElement;
    if (verticalclickchecked) {
      verticalclickchecked.checked = true;
    }
    const defaultclickchecked = document.getElementById(
      'switcher-default-menu'
    ) as HTMLInputElement;
    if (defaultclickchecked) {
      defaultclickchecked.checked = true;
    }

    // switcher.checkOptions();
  }
  ngOnInit(): void {
    switcher.localStorageBackUp();
    this.closeMenu(localStorage.getItem('insightappsMenus'));
    this.setChartType();
  }

  public localdata = localStorage;
active=1;

  chartType : any;
  userId : any;
  setChartType(){
    this.chartType = localStorage.getItem('chartType');
    this.userId = localStorage.getItem('userId');
  }

  changeChartType(event : any){
    this.chartType = event.target.value;
    let object = {
      "user_id": this.userId,
      "chart_type": this.chartType
    }
    this.workbenchService.setChartType(object).subscribe({next: (responce:any) => {
      console.log(responce);
      localStorage.removeItem('chartType');
      localStorage.setItem('chartType',this.chartType)
    },
    error: (error) => {
      console.log(error);
    }
  })
  }
}

