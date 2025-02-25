import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, ElementRef, HostListener, QueryList, ViewChild, ViewChildren } from '@angular/core';
import { NgbDropdown, NgbModal, NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { ResizableModule, ResizeEvent } from 'angular-resizable-element';
import {CompactType, GridsterConfig, GridsterItem, GridsterItemComponent, GridsterItemComponentInterface, GridsterModule, GridsterPush, 
  GridType,
  DisplayGrid,
  GridsterComponent,
  GridsterComponentInterface,
 
} from 'angular-gridster2';
import { MatCardModule } from '@angular/material/card';
import { MatGridListModule } from '@angular/material/grid-list';
import { EChartsOption, number } from 'echarts';
import { NgxEchartsModule, NGX_ECHARTS_CONFIG } from 'ngx-echarts';
import { ApexOptions, ChartComponent, ChartType, NgApexchartsModule } from 'ng-apexcharts';
import ApexCharts from 'apexcharts';
import { CdkDrag, CdkDragDrop, CdkDropList, CdkDropListGroup, moveItemInArray, transferArrayItem } from '@angular/cdk/drag-drop';
import { WorkbenchService } from '../workbench.service';
import { SharedModule } from '../../../shared/sharedmodule';
import * as _ from 'lodash';
// import { chartOptions } from '../../../shared/data/dashboard';
import { ChartsStoreComponent } from '../charts-store/charts-store.component';
import { v4 as uuidv4 } from 'uuid';
import { debounceTime, fromEvent, map, Observable } from 'rxjs';
import { ActivatedRoute, Router } from '@angular/router';
import { FormGroup, FormsModule } from '@angular/forms';
import Swal from 'sweetalert2';
import { ScreenshotService } from '../../../shared/services/screenshot.service';
import * as htmlToImage from 'html-to-image';
import { toPng } from 'html-to-image';
import { style } from 'd3';
import { OVERFLOW } from 'html2canvas/dist/types/css/property-descriptors/overflow';
import { LoaderService } from '../../../shared/services/loader.service';
import { arrow } from '@popperjs/core';
import { MatTabsModule } from '@angular/material/tabs';
import { CKEditorModule } from '@ckeditor/ckeditor5-angular';
import { ClassicEditor, Bold, Essentials, Italic, Mention, Paragraph, Undo, Font, Alignment, FontFamily, Underline, Subscript, Superscript, RemoveFormat, SelectAll, Heading } from 'ckeditor5';
import 'ckeditor5/ckeditor5.css';
import { InsightsButtonComponent } from '../insights-button/insights-button.component';
import { NgxPaginationModule } from 'ngx-pagination';
import { ViewTemplateDrivenService } from '../view-template-driven.service';
import { ToastrService } from 'ngx-toastr';
import { DomSanitizer } from '@angular/platform-browser';
import { NgSelectModule } from '@ng-select/ng-select';
import * as echarts from 'echarts';
import { HttpClient } from '@angular/common/http';
import { SharedService } from '../../../shared/services/shared.service';
// import { series } from '../../charts/apexcharts/data';
import { tap } from 'rxjs/operators'; 
import { InsightEchartComponent } from '../insight-echart/insight-echart.component';
import iconsData from '../../../../assets/iconfonts/font-awesome/metadata/icons.json';
import { FilterIconsPipe } from '../../../shared/pipes/iconsFilterPipe';
import 'pivottable';
import { FormatMeasurePipe } from '../../../shared/pipes/format-measure.pipe';

interface TableRow {
  [key: string]: any;
}
export type ChartOptions = {
  series: ApexAxisChartSeries;
  annotations: ApexAnnotations;
  chart: ApexChart;
  xaxis: ApexXAxis;
  dataLabels: ApexDataLabels;
  grid: ApexGrid;
  labels: string[];
  stroke: ApexStroke;
  title: ApexTitleSubtitle;
  plotOptions: ApexPlotOptions;
};
type DashboardItem = GridsterItem & { 
  data?: { title: string, content: string }, 
  chartOptions?: ApexOptions,
  initCallback?: (item: GridsterItem, itemComponent: GridsterItemComponent) => void 
};
interface Dimension {
  name: string;
  values: string[];
}
interface KpiData {
  rows: any[];
  fontSize: string;
  color: string;
  kpiNumber: any;
  kpiPrefix : string;
  kpiSuffix: string;
  kpiDecimalUnit : string;
  kpiDecimalPlaces: number;
}
declare var $:any;

@Component({
  selector: 'app-sheetsdashboard',
  standalone: true,
  providers: [
    {
      provide: NGX_ECHARTS_CONFIG,
      useFactory: () => ({ echarts: echarts }),
    },
  ],
  imports: [NgxEchartsModule,SharedModule,NgbModule,CommonModule,ResizableModule,GridsterModule,
    CommonModule,GridsterItemComponent,GridsterComponent,NgApexchartsModule,CdkDropListGroup, NgSelectModule,
    CdkDropList, CdkDrag,ChartsStoreComponent,FormsModule, MatTabsModule , CKEditorModule , InsightsButtonComponent,
    NgxPaginationModule,NgSelectModule, InsightEchartComponent,SharedModule,FilterIconsPipe,FormatMeasurePipe],
  templateUrl: './sheetsdashboard.component.html',
  styleUrl: './sheetsdashboard.component.scss'
})
export class SheetsdashboardComponent {
 // @HostListener('window:resize', ['$event'])
 itemsPerPage:any;
 pageNo = 1;
 page: number = 1;
 totalItems:any;
 qrySetId:any[] = [];
 databaseId:any[] = [];
 fileId:any[] = [];
 dashboardName = '';
 dashboardTagName = '';
 panelscheckbox=[] as any;
 isSheetsView : boolean = false;
 sheetsIdArray = [] as any;
 dashboardsheetsIdArray = [] as any;
 sheetIdsDataSet = [] as any;
 sheetsNewDashboard=false;
 dashboardView = false;
 chartOptionsBar:any;
 dashboardId:any;
 databaseName:any;
 gridType: string = 'fixed';
 updateDashbpardBoolen= false;
 active=1;
 isOverflowHidden = false;
 imageFile:any;
 imagename:any
 sheetsFilterNames = [] as any;
 sheetsFilterNamesFromEdit = [] as any;
 columnFilterNames = [] as any;
 columnFilterNamesEdit = [] as any;
 querySetNames = [] as any;
 selectedQuerySetId =[] as any;
 selectClmn:any;
 selectClmnEdit:any;
 selectdColmnDtype:any;
 selectedColumnQuerySetId:any;
 selectdColmnDtypeEdit:any;
 filterName = '';
 dashboardFilterId:any;
 DahboardListFilters = [] as any;
 storeSelectedColData = [] as any
 colData = [] as any;
 heightGrid : number = 800;
 widthGrid : number = 800;
 gridItemSize : number = 50;
 dataArray = [] as any;
 keysArray = [] as any;
 excludeFilterIdArray = [] as any;
 tablePreviewRow = [] as any;
 tablePreviewColumn =[] as any;
 filteredColumnData = [] as any;
 filteredRowData = [] as any;
 disableDashboardUpdate: boolean = false;
 sheetTabs : any[] = [];
 selectedTabIndex : number = 0;
 selectedTab : any = {};
 displayTabs : boolean = false;
 editDashboard : boolean = false;
 fromFileId = false;
 editFilters = false;
 querysetNameEdit:any;
  public chartOptions!: Partial<ChartOptions>;
  searchSheets!: string;
  isPublicUrl = false;
  publicHeader = false;
  columnSearch: any;
  rolesForUpdateDashboard:[] = [];
  usersForUpdateDashboard:[] =[];
  tableNameSelectedForFilter:any;
  isPanelHidden: boolean = true;


  tableItemsPerPage:any;
  tablePageNo = 1;
  tablePage: number = 1;
  tableTotalItems:any;
  tableSearch:any;
  isDraggingDisabled = false;
  isSampleDashboard: boolean = false;;

  sourceSheetId : any = 0;
  targetSheetIds : any[] = [];
  drillThroughQuerySetId : any[] = [];
  dashboardActionsList : any[] = [];
  actionName = '';
  sourceSheetList: any[] = [];
  targetSheetList : any[] = [];
  isAllTargetSheetsSelected : boolean = false;
  editActions : boolean = false;
  actionId : any;
  drillThroughActionList : any[] =[];
  drillThroughDatabaseName : any = '';

  calendarTotalHeight : string = '400px';
  @ViewChild('pivotTableContainer', { static: false }) pivotContainer!: ElementRef;

  constructor(private workbechService:WorkbenchService,private route:ActivatedRoute,private router:Router,private screenshotService: ScreenshotService,
    private loaderService:LoaderService,private modalService:NgbModal, private viewTemplateService:ViewTemplateDrivenService,private toasterService:ToastrService,
     private sanitizer: DomSanitizer,private cdr: ChangeDetectorRef, private http: HttpClient,private sharedService:SharedService){
    this.dashboard = [];
    const currentUrl = this.router.url; 
    this.http.get('./assets/maps/world.json').subscribe((geoJson: any) => {
      echarts.registerMap('world', geoJson); 
    });
    if(currentUrl.includes('public/dashboard')){
      this.updateDashbpardBoolen= true;
      this.isPublicUrl = true;
      this.active = 2;
      this.publicHeader = true
      if (route.snapshot.params['id1']) {
      this.dashboardId = +atob(route.snapshot.params['id1'])
      }
    }
    if(!this.isPublicUrl){
      this.editDashboard = this.viewTemplateService.editDashboard();
    }
    if(currentUrl.includes('analytify/sheetscomponent/sheetsdashboard')){
      this.sheetsNewDashboard = true;
      if (route.snapshot.params['id1'] && route.snapshot.params['id2'] ) {
        this.databaseId.push(+atob(route.snapshot.params['id1']));
        this.qrySetId.push(+atob(route.snapshot.params['id2']));
        }
    }
    // else if(currentUrl.includes('insights/sheetscomponent/sheetsdashboard/fileId')){
    //   this.sheetsNewDashboard = true;
    //   if (route.snapshot.params['id1'] && route.snapshot.params['id2'] ) {
    //     this.fileId.push(+atob(route.snapshot.params['id1']));
    //     this.qrySetId.push(+atob(route.snapshot.params['id2']));
    //     this.fromFileId = true;
    //     }
    // }
    else if(currentUrl.includes('analytify/home/sheetsdashboard')){
      this.dashboardView = true;
      this.updateDashbpardBoolen= true
      if (route.snapshot.params['id3']) {
        // this.databaseId = +atob(route.snapshot.params['id1']);
        // this.qrySetId = +atob(route.snapshot.params['id2'])
        this.dashboardId = +atob(route.snapshot.params['id3'])

        } else if(route.snapshot.params['id1']){
          this.dashboardId = +atob(route.snapshot.params['id1'])
        }
      }
        else if(currentUrl.includes('analytify/sheetsdashboard')){
          this.sheetsNewDashboard = true;
    }
    
  }
  options!: GridsterConfig;
  nestedDashboard: Array<GridsterItem & { data?: any,   chartOptions?: ApexOptions,  chartInstance?: ApexCharts,chartData?: any[],tableData?: { headers: any[], rows: any[], banding: any, color1: any, color2: any ,tableItemsPerPage : any, tableTotalItems : any }
}> = [];
  dashboard!: Array<GridsterItem & { sheetId?: number ,data?: any, chartType?: any,   chartOptions?: ApexOptions, echartOptions : any, chartInstance?: ApexCharts,chartData?: any[],tableData?: { headers: any[], rows: any[], banding: any, color1: any, color2: any, tableItemsPerPage : any, tableTotalItems : any ,tablePage : number  }, numberFormat?: {donutDecimalPlaces: any,decimalPlaces: any,displayUnits: any,prefix:any,suffix:any}, pivotData?:any
  }>;
  dashboardTest: Array<GridsterItem & { data?: any, chartType?: any,   chartOptions?: ApexOptions,  chartInstance?: ApexCharts,chartData?: any[],tableData?: { headers: any[], rows: any[], banding: any, color1: any, color2: any, tableItemsPerPage : any, tableTotalItems : any  }
}> = [];
  dashboardNew!: Array<GridsterItem & { data?: any,   chartOptions?: ApexOptions,  chartInstance?: ApexCharts,chartData?: any[],tableData?: { headers: any[], rows: any[], banding: any, color1: any, color2: any, tableItemsPerPage : any, tableTotalItems : any  }
  }>;
  testData!: Array<GridsterItem & { data?: any, chartType?: any,  chartOptions?: ApexOptions,  chartInstance?: ApexCharts,chartData?: any[],tableData?: { headers: any[], rows: any[], banding: any, color1: any, color2: any, tableItemsPerPage : any, tableTotalItems : any  }
}>;
  pushNewSheet =[] as any;
  sheetData = [] as any;
  tableHeader:any;
  tableRows:any;
  rowArray = [] as any;
  colArray = [] as any;
  selectedRows = [];
  isAllSelected: boolean = false;
  selectedRowsEdit = [];
  dashboardFilterIdEdit:any;
  chartOptionsinitialize = false;
  editquerysetId:any;
  //@ViewChild('gridster') gridster!: ElementRef;
  dropdownOptions: any[] = [];
  selectedOption: string | null = null;
  screenshotSrc: string | null = null;

  itemToPush!: GridsterItemComponent;
  @ViewChildren(GridsterItemComponent) GridsterItemComponent!: QueryList<GridsterItemComponent>;
  @ViewChild('gridster') gridster!: ElementRef; // Adjust the type as needed
  @ViewChild('nestedDropdown', { static: true }) nestedDropdown: NgbDropdown | undefined;
  @ViewChild('ImageUploadKPI') ImageUploadKPI!: ElementRef;
  @ViewChild('imageUpload') imageUpload!: ElementRef<HTMLInputElement>;
  // iconList = [
  //   { class: 'fa-solid fa-arrow-trend-up', name: 'Trend Up' },
  //   { class: 'fa-solid fa-arrow-trend-down', name: 'Trend Down' },
  //   { class: 'fa-solid fa-house', name: 'Home' },
  //   { class: 'fa-solid fa-magnifying-glass', name: 'Magnifying Glass' },
  //   { class: 'fa-solid fa-user', name: 'User' },
  //   { class: 'fa-brands fa-facebook', name: 'Facebook' },
  //   { class: 'fa-solid fa-check', name: 'Check' },
  //   { class: 'fa-solid fa-download', name: 'Download' },
  //   { class: 'fa-brands fa-twitter', name: 'Twitter' },
  //   { class: 'fa-brands fa-instagram', name: 'Instagram' },
  //   { class: 'fa-solid fa-envelope', name: 'Envelope' },
  //   { class: 'fa-brands fa-linkedin', name: 'LinkedIn' },
  //   { class: 'fa-solid fa-arrow-up', name: 'Up Arrow' },
  //   { class: 'fa-solid fa-file', name: 'File' },
  //   { class: 'fa-solid fa-calendar-days', name: 'Calendar Days' },
  //   { class: 'fa-solid fa-circle-down', name: 'Circle Down' },
  //   { class: 'fa-solid fa-address-book', name: 'Address Book' },
  //   { class: 'fa-solid fa-handshake', name: 'Hand Shake' },
  //   { class: 'fa-solid fa-layer-group', name: 'Layer Group' },
  //   { class: 'fa-solid fa-users', name: 'Users' },
  //   { class: 'fa-solid fa-link', name: 'Link' },
  //   { class: 'fa-solid fa-sack-dollar', name: 'Sack Dollar' }
  // ];
  iconList: any[] = []
  static itemChange(
    item: GridsterItem,
    itemComponent: GridsterItemComponentInterface,
    compInstance: SheetsdashboardComponent
  ): void {
    console.info('itemChanged', item, itemComponent);
    compInstance.canNavigateToAnotherPage = true;
  }

  static itemResize(
    item: GridsterItem,
    itemComponent: GridsterItemComponentInterface
  ) : void {
    console.info('itemResized', item, itemComponent);
    const resize$ = fromEvent(window, 'resize');
    resize$
      .pipe(
        map((i: any) => i),
        debounceTime(500) // He waits > 0.5s between 2 events emitted before running the next.
      )
      .subscribe((event) => {
        console.log('resize is finished');
        
      });
     window.dispatchEvent(new Event('resize'));
    }

  static itemInit(
    item: GridsterItem,
    itemComponent: GridsterItemComponentInterface
  ): void {
    console.info('itemInitialized', item, itemComponent);
  }

  static itemRemoved(
    item: GridsterItem,
    itemComponent: GridsterItemComponentInterface
  ): void {
    console.info('itemRemoved', item, itemComponent);
  }

  static itemValidate(item: GridsterItem): boolean {
    return item.cols > 0 && item.rows > 0;
  }

  static gridInit(grid: GridsterComponentInterface): void {
    console.info('gridInit', grid);
  }

  static gridDestroy(grid: GridsterComponentInterface): void {
    console.info('gridDestroy', grid);
  }

  static gridSizeChanged(grid: GridsterComponentInterface): void {
    console.info('gridSizeChanged', grid);
  }

  responseData = {
    tables: {
      user_profile: [
        { column_name: 'email_id', column_dtype: 'varchar' },
        { column_name: 'sub_identifier', column_dtype: 'varchar' }
      ],
      user_role: [
        { column_name: 'id', column_dtype: 'integer' },
        { column_name: 'role_id', column_dtype: 'integer' },
        { column_name: 'user_id(user_role)', column_dtype: 'integer' }
      ]
    }
  }
  private mapStyleToClass(style: string): string {
    switch (style) {
      case 'solid':
        return 'fas';
      case 'regular':
        return 'far';
      case 'brands':
        return 'fab';
      default:
        return ''; // Handle unsupported styles
    }
  }
  ngOnInit() {  
    let displayGrid = DisplayGrid.Always;
    this.iconList = Object.entries(iconsData).map(([key, value]: [string, any]) => ({
      name: key,
      styles: value.styles.map((style: string) => this.mapStyleToClass(style)), // Map styles to class prefixes
      label: value.label, 
    }));
    this.updateFilteredIcons(); // Update the initial filtered icons

    if(this.isPublicUrl){
      displayGrid = DisplayGrid.None;
    }
    this.http.get('./assets/maps/world.json').subscribe((geoJson: any) => {
      echarts.registerMap('world', geoJson); 
      this.loaderService.hide(); 
      if(!this.isPublicUrl){
        if(this.fileId.length > 0 || this.databaseId.length > 0){
          this.sheetsDataWithQuerysetIdTest();
        }
      }
      if(this.isPublicUrl){
        // this.dashboardId = 145
        this.getSavedDashboardDataPublic();
        this.getDashboardFilterredListPublic();
        displayGrid = DisplayGrid.None;
      }
        // if(this.sheetsNewDashboard){
        //   this.sheetsDataWithQuerysetId();
        // }
        if(this.dashboardView){
    
          this.getSavedDashboardData();
          // this.sheetsDataWithQuerysetId();
          this.getDashboardFilterredList();
        }
        if(this.dashboardId != undefined || null){
          this.getDrillThroughActionList();
        }

    });    
   
    //this.getSheetData();
    this.options = {
      gridType: GridType.Fit,
      compactType: CompactType.CompactLeftAndUp,
      displayGrid: displayGrid,
      initCallback: SheetsdashboardComponent.gridInit,
      destroyCallback: SheetsdashboardComponent.gridDestroy,
      gridSizeChangedCallback: SheetsdashboardComponent.gridSizeChanged,
      itemChangeCallback: (item, itemComponent) => this.onItemResize(item, itemComponent),
      itemResizeCallback: SheetsdashboardComponent.itemResize,
      itemInitCallback: SheetsdashboardComponent.itemInit,
      itemRemovedCallback: SheetsdashboardComponent.itemRemoved,
      itemValidateCallback: SheetsdashboardComponent.itemValidate,
      fixedColWidth: this.gridItemSize,
      fixedRowHeight: this.gridItemSize,
      // margin : 10,
      // itemChangeCallback: SheetsdashboardComponent.itemChangesss,
      //   // itemResizeCallback: SheetsdashboardComponent.itemResize,
      

      //  itemResizeCallback: (item: GridsterItem, itemComponent: GridsterItemComponentInterface) => {
      //   // this.updateSizeOnServer(item, itemComponent);
      //   // this.updateChartDimensions(item,itemComponent as GridsterItemComponent)
      //   // this.saveItemDimensions(item);
      // },
      pushItems: true,
      draggable: {
        enabled: this.editDashboard && !this.isDraggingDisabled,
        stop: (item: GridsterItem, itemComponent: GridsterItemComponentInterface, event: MouseEvent) => {
          // Optional logic when dragging stops
          console.log('Drag stopped for item', item);
        }
        
      },
      resizable: {
        enabled: this.editDashboard,
      }
    };
    const savedItems = JSON.parse(localStorage.getItem('dashboardItems') || '[]');

    this.sharedService.downloadRequested$.subscribe(() => {
      this.downloadImageInPublic();
    });

    // Subscribe to refresh requests
    this.sharedService.refreshRequested$.subscribe(() => {
      this.getSavedDashboardDataPublic();
    });

  }

  onItemResize(item: GridsterItem, itemComponent: any): void {
    SheetsdashboardComponent.itemChange(item, itemComponent, this);
  }
  changeGridType(gridType : string){
    let displayGrid = DisplayGrid.Always;
    if(this.isPublicUrl){
      displayGrid = DisplayGrid.None;
    }
  if(gridType.toLocaleLowerCase() == 'fixed'){
    this.gridType = 'fixed';
    this.options = {
      gridType: GridType.Fit,
      compactType: CompactType.CompactUpAndLeft,
      displayGrid: displayGrid,
      initCallback: SheetsdashboardComponent.gridInit,
      destroyCallback: SheetsdashboardComponent.gridDestroy,
      gridSizeChangedCallback: SheetsdashboardComponent.gridSizeChanged,
      itemChangeCallback: (item, itemComponent) => this.onItemResize(item, itemComponent),
      itemResizeCallback: SheetsdashboardComponent.itemResize,
      itemInitCallback: SheetsdashboardComponent.itemInit,
      itemRemovedCallback: SheetsdashboardComponent.itemRemoved,
      itemValidateCallback: SheetsdashboardComponent.itemValidate,
      fixedColWidth: this.gridItemSize,
      fixedRowHeight: this.gridItemSize,
      // margin : 10,
      // outerMarginBottom: 20,
      // itemChangeCallback: SheetsdashboardComponent.itemChangesss,
      //   // itemResizeCallback: SheetsdashboardComponent.itemResize,
      

      //  itemResizeCallback: (item: GridsterItem, itemComponent: GridsterItemComponentInterface) => {
      //   // this.updateSizeOnServer(item, itemComponent);
      //   // this.updateChartDimensions(item,itemComponent as GridsterItemComponent)
      //   // this.saveItemDimensions(item);
      // },
      pushItems: true,
      draggable: {
        enabled: this.editDashboard,
        stop: (item: GridsterItem, itemComponent: GridsterItemComponentInterface, event: MouseEvent) => {
          // Optional logic when dragging stops
          console.log('Drag stopped for item', item);
        }
      },
      resizable: {
        enabled: this.editDashboard,
        // stop: this.onResizeStop.bind(this)
      }
    };
  } else {
    this.gridType = 'scroll'
    this.options = {
      gridType: GridType.Fixed,
      compactType: CompactType.CompactUpAndLeft,
      displayGrid: displayGrid,
      initCallback: SheetsdashboardComponent.gridInit,
      destroyCallback: SheetsdashboardComponent.gridDestroy,
      gridSizeChangedCallback: SheetsdashboardComponent.gridSizeChanged,
      itemChangeCallback: (item, itemComponent) => this.onItemResize(item, itemComponent),
      itemResizeCallback: SheetsdashboardComponent.itemResize,
      itemInitCallback: SheetsdashboardComponent.itemInit,
      itemRemovedCallback: SheetsdashboardComponent.itemRemoved,
      itemValidateCallback: SheetsdashboardComponent.itemValidate,
      fixedColWidth: this.gridItemSize,
      fixedRowHeight: this.gridItemSize,
      // margin : 10,
      // itemChangeCallback: SheetsdashboardComponent.itemChangesss,
      //   // itemResizeCallback: SheetsdashboardComponent.itemResize,
      

      //  itemResizeCallback: (item: GridsterItem, itemComponent: GridsterItemComponentInterface) => {
      //   // this.updateSizeOnServer(item, itemComponent);
      //   // this.updateChartDimensions(item,itemComponent as GridsterItemComponent)
      //   // this.saveItemDimensions(item);
      // },
      pushItems: true,
      draggable: {
        enabled: this.editDashboard,
        stop: (item: GridsterItem, itemComponent: GridsterItemComponentInterface, event: MouseEvent) => {
          // Optional logic when dragging stops
          console.log('Drag stopped for item', item);
        }
      },
      resizable: {
        enabled: this.editDashboard,

        // stop: this.onResizeStop.bind(this)
      }
    };
  }
}
  changeGridItemSize(){
    if(this.gridType == 'fixed'){
      this.options = {
        gridType: GridType.Fit,
        compactType: CompactType.CompactUpAndLeft,
        displayGrid: DisplayGrid.Always,
        initCallback: SheetsdashboardComponent.gridInit,
        destroyCallback: SheetsdashboardComponent.gridDestroy,
        gridSizeChangedCallback: SheetsdashboardComponent.gridSizeChanged,
        itemChangeCallback: (item, itemComponent) => this.onItemResize(item, itemComponent),
        itemResizeCallback: SheetsdashboardComponent.itemResize,
        itemInitCallback: SheetsdashboardComponent.itemInit,
        itemRemovedCallback: SheetsdashboardComponent.itemRemoved,
        itemValidateCallback: SheetsdashboardComponent.itemValidate,
        fixedColWidth: this.gridItemSize,
        fixedRowHeight: this.gridItemSize,
        // margin : 10,
        // itemChangeCallback: SheetsdashboardComponent.itemChangesss,
        //   // itemResizeCallback: SheetsdashboardComponent.itemResize,
        
  
        //  itemResizeCallback: (item: GridsterItem, itemComponent: GridsterItemComponentInterface) => {
        //   // this.updateSizeOnServer(item, itemComponent);
        //   // this.updateChartDimensions(item,itemComponent as GridsterItemComponent)
        //   // this.saveItemDimensions(item);
        // },
        pushItems: true,
        draggable: {
          enabled: this.editDashboard,
          stop: (item: GridsterItem, itemComponent: GridsterItemComponentInterface, event: MouseEvent) => {
            // Optional logic when dragging stops
            console.log('Drag stopped for item', item);
          }
        },
        resizable: {
          enabled: this.editDashboard,
        }
      };
    } else {
      this.options = {
        gridType: GridType.Fixed,
        compactType: CompactType.CompactUpAndLeft,
        displayGrid: DisplayGrid.Always,
        initCallback: SheetsdashboardComponent.gridInit,
        destroyCallback: SheetsdashboardComponent.gridDestroy,
        gridSizeChangedCallback: SheetsdashboardComponent.gridSizeChanged,
        itemChangeCallback: (item, itemComponent) => this.onItemResize(item, itemComponent),
        itemResizeCallback: SheetsdashboardComponent.itemResize,
        itemInitCallback: SheetsdashboardComponent.itemInit,
        itemRemovedCallback: SheetsdashboardComponent.itemRemoved,
        itemValidateCallback: SheetsdashboardComponent.itemValidate,
        fixedColWidth: this.gridItemSize,
        fixedRowHeight: this.gridItemSize,
        // margin : 10,
        // itemChangeCallback: SheetsdashboardComponent.itemChangesss,
        //   // itemResizeCallback: SheetsdashboardComponent.itemResize,
        
  
        //  itemResizeCallback: (item: GridsterItem, itemComponent: GridsterItemComponentInterface) => {
        //   // this.updateSizeOnServer(item, itemComponent);
        //   // this.updateChartDimensions(item,itemComponent as GridsterItemComponent)
        //   // this.saveItemDimensions(item);
        // },
        pushItems: true,
        draggable: {
          enabled: this.editDashboard,
          stop: (item: GridsterItem, itemComponent: GridsterItemComponentInterface, event: MouseEvent) => {
            // Optional logic when dragging stops
            console.log('Drag stopped for item', item);
          }
        },
        resizable: {
          enabled: this.editDashboard,
          // stop: this.onResizeStop.bind(this)
        }
      };
    }

    // window.dispatchEvent(new Event('resize'));
  }

  restoreChartOptions(chartType: ChartType,xval:any,yval:any){
    return {
      chart: {
        type: chartType,
        height:300
      },
      series: [{
        name: 'Series 1',
        data: yval
      }],
      xaxis: {
        categories: xval
      }
    };
  }

  fetchSheetsDataBasedOnSheetIds(obj:any){
    this.workbechService.sheetRetrivelBasedOnIds(obj).subscribe({
      next:(data)=>{
        console.log('savedDashboard',data);
      let sheetArray = data.map((sheet:any)=>sheet.sheets[0]);
      this.dashboardNew = sheetArray.map((sheet:any) => ({
        id:uuidv4(),
        cols: 1,
        rows: 1,
        y: 10,
        x: 10,
        // fileId : sheet.file_id,
        sheetType:sheet.sheet_type,
        sheetId:sheet.sheet_id,
        chartType:sheet.chart,
        chartId:sheet.chart_id,
        qrySetId : sheet.queryset_id,
        databaseId: sheet.hierarchy_id,
        isEChart : sheet.sheet_data.isEChart,
        column_Data : sheet.sheet_data.columns_data,
        row_Data : sheet.sheet_data.rows_data,
        drillDownHierarchy : sheet.sheet_data.drillDownHierarchy,
        isDrillDownData : sheet.sheet_data.isDrillDownData,
        data: { title: sheet.sheet_name, content: 'Content of card New', sheetTagName:sheet.sheet_tag_name? sheet.sheet_tag_name:sheet.sheet_name},
        selectedSheet : sheet.selectedSheet,
        kpiData: sheet.sheet_type === 'Chart' && sheet.chart_id === 25
        ? (() => {
            this.kpiData = {
              kpiNumber : sheet.sheet_data?.results?.kpiNumber || 0,
            kpiPrefix : sheet.sheet_data?.results?.kpiPrefix || '',
            kpiSuffix : sheet.sheet_data?.results?.kpiSuffix || '',
            kpiDecimalUnit : sheet.sheet_data?.results?.kpiDecimalUnit || 'none',
            kpiDecimalPlaces : sheet.sheet_data?.results?.kpiDecimalPlaces || 0,
              rows: sheet.sheet_data?.results?.kpiData || [],       // Default to an empty array if not provided
              fontSize: sheet.sheet_data?.results?.kpiFontSize || '16px', // Default font size
              color: sheet.sheet_data?.results?.kpicolor || '#000000',    // Default color (black)
            };
            return this.kpiData; // Return the kpi object to kpiData
          })()
        : undefined,
        chartOptions: sheet.sheet_type === 'Chart' && !sheet.sheet_data.isEchart ? {
          // ...this.getChartOptions(sheet.chart,sheet?.sheet_data.x_values,sheet?.sheet_data.y_values),
          ... this.getChartOptionsBasedOnType(sheet) as unknown as ApexOptions,
          // chart: { type: sheet.chart, height: 300 },
          //chartData:this.getChartData(sheet.sheet_data.results, sheet.chart)
        } : undefined,
        tableData: sheet.sheet_type === 'Table' ? {
         ... this.getTableData(sheet.sheet_data)
  
        }
         : undefined,
        numberFormat: {
          donutDecimalPlaces:this.donutDecimalPlaces,
          decimalPlaces:sheet?.sheet_data?.numberFormat?.decimalPlaces,
          displayUnits:sheet?.sheet_data?.numberFormat?.displayUnits,
          prefix:sheet?.sheet_data?.numberFormat?.prefix,
          suffix:sheet?.sheet_data?.numberFormat?.suffix
        },
        pivotData:{
          pivotMeasureData:sheet?.sheet_data?.pivotMeasure_Data,
          pivotRowData:sheet?.sheet_data?.row,
          pivotColData:sheet?.sheet_data.col
        },
        customizeOptions: sheet?.sheet_data?.customizeOptions
      }));
      this.setSelectedSheetData();
       this.isSheetsView = false;
      },
      error:(error)=>{
        console.log(error)
      }
    })
  }
  sheetTagTitle : any={};
  dashboardTagTitle : any;
  getSavedDashboardData(){
    const obj ={ 
      queryset_id:this.qrySetId,
      server_id:this.databaseId,
      dashboard_id:this.dashboardId
    }
    this.workbechService.getSavedDashboardData(obj).subscribe({
      next:(data)=>{
        console.log('savedDashboard',data);
        this.dashboardName=data.dashboard_name;
        this.isSampleDashboard = data.is_sample;
        this.heightGrid = data.height;
        this.widthGrid = data.width;
        this.gridType = data.grid_type;
        this.changeGridType(this.gridType);
        this.qrySetId = data.queryset_id;
        // if(data.file_id && data.file_id.length){
        //   this.fileId = data.file_id;
        // }
        if(data.hierarchy_id && data.hierarchy_id.length){
          this.databaseId = data.hierarchy_id;
        }
        this.dashboardsheetsIdArray = data.sheet_ids;
        this.dashboard = data.dashboard_data;
        this.sheetIdsDataSet = data.selected_sheet_ids;
        this.usersForUpdateDashboard = data.user_ids;
        this.rolesForUpdateDashboard = data.role_ids;
        let self = this;
        let obj = {sheet_ids: this.sheetIdsDataSet};
        if(!this.isPublicUrl){
        this.fetchSheetsDataBasedOnSheetIds(obj);
        }
        if(!data.dashboard_tag_name){
          this.dashboardTagName = data.dashboard_name;
        }
        else{
          this.dashboardTagName = data.dashboard_tag_name;
        }
        this.dashboardTagTitle = this.sanitizer.bypassSecurityTrustHtml(this.dashboardTagName);
        this.dashboard.forEach((sheet : any)=>{
          console.log('Before sanitization:', sheet.data?.sheetTagName);
          this.sheetTagTitle[sheet.data?.title] = this.sanitizer.bypassSecurityTrustHtml(sheet.data?.sheetTagName);
          if((sheet && sheet.chartOptions && sheet.chartOptions.chart)) {
          sheet.chartOptions.chart.events = {
            markerClick: (event: any, chartContext: any, config: any) => {
              let selectedXValue;
              if(sheet.chartId == 24 || sheet.chartId == 10 || sheet.chartId == 17 || sheet.chartId == 4){
                selectedXValue = sheet.chartOptions.labels[config.dataPointIndex];
              } else {
                selectedXValue = sheet.chartOptions.xaxis.categories[config.dataPointIndex];
              }
              if(self.actionId && sheet.sheetId === self.sourceSheetId){
                self.setDrillThrough(selectedXValue, sheet);  
              }
            },
            dataPointSelection: function (event: any, chartContext: any, config: any) {
              let selectedXValue;
              if(sheet.chartId == 24 || sheet.chartId == 10 || sheet.chartId == 17 || sheet.chartId == 4){
                selectedXValue = sheet.chartOptions.labels[config.dataPointIndex];
              } else {
                selectedXValue = sheet.chartOptions.xaxis.categories[config.dataPointIndex];
              }
              if(self.actionId && sheet.sheetId === self.sourceSheetId){
                self.setDrillThrough(selectedXValue, sheet);  
              }            
              if (sheet.drillDownIndex < sheet.drillDownHierarchy?.length - 1) {
                // const selectedXValue = element.chartOptions.series[0].data[config.dataPointIndex];
                console.log('X-axis value:', selectedXValue);
                let nestedKey = sheet.drillDownHierarchy[sheet.drillDownIndex];
                sheet.drillDownIndex++;
                let obj = { [nestedKey]: selectedXValue };
                sheet.drillDownObject.push(obj);
                self.dataExtraction(sheet);
              }
            },
            mounted: function(chartContext:any, config:any) {
              if (sheet.chartId == 28) {
                let color = sheet?.chartOptions?.plotOptions?.radialBar?.dataLabels?.name?.color;
                const applyStyles = () => {
                  const valueElement = document.querySelector('.apexcharts-datalabel-value') as HTMLElement;
                  if (valueElement) {
                    valueElement.style.fill = color;
                    valueElement.style.setProperty('fill', color, 'important');
                  }
    
                  const nameElement = document.querySelector('.apexcharts-datalabel-label') as HTMLElement;
                  if (nameElement) {
                    nameElement.style.fill = color;
                    nameElement.style.setProperty('fill', color, 'important');
                  }
                };
                // Initial styling
                applyStyles();
    
                // Monitor DOM for changes
                const observer = new MutationObserver(() => {
                  applyStyles();
                });
                const chartContainer = document.querySelector('.apexcharts-inner');
                if (chartContainer) {
                  observer.observe(chartContainer, { childList: true, subtree: true });
                }
              }
            },
            updated: function(chartContext:any, config:any) {
              if (sheet.chartId == 28) {
                let color = sheet?.chartOptions?.plotOptions?.radialBar?.dataLabels?.name?.color;
                const applyStyles = () => {
                  const valueElement = document.querySelector('.apexcharts-datalabel-value') as HTMLElement;
                  if (valueElement) {
                    valueElement.style.fill = color;
                    valueElement.style.setProperty('fill', color, 'important');
                  }
    
                  const nameElement = document.querySelector('.apexcharts-datalabel-label') as HTMLElement;
                  if (nameElement) {
                    nameElement.style.fill = color;
                    nameElement.style.setProperty('fill', color, 'important');
                  }
                };
                // Initial styling
                applyStyles();
    
                // Monitor DOM for changes
                const observer = new MutationObserver(() => {
                  applyStyles();
                });
                const chartContainer = document.querySelector('.apexcharts-inner');
                if (chartContainer) {
                  observer.observe(chartContainer, { childList: true, subtree: true });
                }
              }
            }
          };
          } else if (sheet.chartId == 29) {
            this.chartType = 'map';
            sheet.echartOptions?.series[0]?.data?.forEach((data: any) => {
              this.chartsColumnData.push(data.name);
              this.chartsRowData.push(data.value);
            });
            this.dualAxisColumnData = [{
              name: sheet?.column_Data[0][0],
              values: this.chartsColumnData
            }]
            this.dualAxisRowData = [{
              name: sheet?.row_Data[0][0],
              data: this.chartsRowData
            }]
          sheet.echartOptions.tooltip= {
            formatter: (params: any) => {
              const { name, data } = params;
              if (data) {
                const keys = Object.keys(data);
          const values = Object.values(data);
          let formattedString = '';
          keys.forEach((key, index) => {
            if(key)
            formattedString += `${key}: ${values[index]}<br/>`;
          });
    
          return formattedString;
               
              } else {
                return `${name}: No Data`;
              }
            }
        }
      }
          console.log('After sanitization:', sheet.data.sheetTagName);
          this.donutDecimalPlaces = sheet?.numberFormat?.donutDecimalPlaces;
          if(sheet['chartId'] === 10 && sheet.chartOptions && sheet.chartOptions.plotOptions && sheet.chartOptions.plotOptions.pie && sheet.chartOptions.plotOptions.pie.donut && sheet.chartOptions.plotOptions.pie.donut.labels && sheet.chartOptions.plotOptions.pie.donut.labels.total){
            sheet.chartOptions.plotOptions.pie.donut.labels.total.formatter = (w:any) => {
              return w.globals.seriesTotals.reduce((a:any, b:any) => {
                return +a + b
              }, 0).toFixed(this.donutDecimalPlaces);
            };
          }
          let chartId : number = sheet['chartId'];
          const numberFormat = sheet?.numberFormat;
          const isEcharts = sheet?.isEChart;
          this.updateNumberFormat(sheet, numberFormat, chartId, isEcharts);
          if(chartId == 11){
            sheet.echartOptions.tooltip.formatter =  function (params: any) {
              const date = params.data[0];
              const value = params.data[1];
              return `Date: ${date}<br/>Value: ${value}`;
            };
            this.calendarTotalHeight = ((150 * sheet.echartOptions.calendar.length) + 25) + 'px';
          }
          if(chartId == 9){
            let transformedData :any =[];
            let headers: string[] = [];
  
           let columnKeys = sheet.pivotData?.pivotColData?.map((col: any) => col.column); 
           let rowKeys = sheet.pivotData?.pivotRowData?.map((row: any) => row.col);
          let valueKeys = sheet.pivotData?.pivotMeasureData?.map((col:any) =>col.col)
          sheet.pivotData?.pivotColData?.forEach((colObj: any) => {
            headers.push(colObj.column);
          });
      
          sheet.pivotData?.pivotRowData?.forEach((rowObj: any) => {
            headers.push(rowObj.col);
          });
          sheet.pivotData?.pivotMeasureData?.forEach((colObj: any) => {
            headers.push(colObj.col);
          });
      
          transformedData.push(headers); 
          // let numRows = sheet.pivotData?.pivotColData[0]?.result_data.length;
          let numRows = 0;
          if (sheet.pivotData?.pivotColData?.length > 0) {
              numRows = sheet.pivotData.pivotColData[0]?.result_data?.length || 0;
          } else if (sheet.pivotData?.pivotRowData?.length > 0) {
              numRows = sheet.pivotData.pivotRowData[0]?.result_data?.length || 0;
          } else if (sheet.pivotData?.pivotMeasureData?.length > 0) {
              numRows = sheet.pivotData.pivotMeasureData[0]?.result_data?.length || 0;
          }
          for (let i = 0; i < numRows; i++) {
            let rowArray: any[] = []; 
            sheet.pivotData?.pivotColData.forEach((colObj: any) => {
              rowArray.push(colObj.result_data[i]);
            });
            sheet.pivotData?.pivotRowData.forEach((rowObj: any) => {
              rowArray.push(rowObj.result_data[i]);
            });
            sheet.pivotData?.pivotMeasureData.forEach((rowObj: any) => {
              rowArray.push(rowObj.result_data[i]);
            });
  
            transformedData.push(rowArray);
          }
            setTimeout(() => {
            if (this.pivotContainer && this.pivotContainer.nativeElement) {
                ($(this.pivotContainer.nativeElement) as any).pivot(transformedData, {
                  rows: columnKeys,  
                  cols: valueKeys, 
                  // vals: this.valueKeys, 
                  aggregator:$.pivotUtilities.aggregators["Sum"](rowKeys),
                  rendererName: "Table"
                });
            }        
          }, 1000);
        }
          if(chartId == 1){
            if(sheet?.tableData?.tableItemsPerPage){
              sheet.tableData.tableItemsPerPage = 10;
            }
            if(sheet?.tableData?.tablePage){
              sheet.tableData.tablePage = 1;
            }
          }
        })
        console.log(this.sheetTagTitle);
        console.log(this.dashboard);
      },
      error:(error)=>{
        console.log(error)
      }
    })
  }

  setSelectedSheetData() {
    this.dashboardNew = this.dashboardNew.map(target => {
      const source = this.dashboard.find(source => source['sheetId'] === target['sheetId']);
      if (source) {
        return { ...target, selectedSheet: source['selectedSheet'] };
      }
      return target;
    });
  }

  // saveDashboard(){
  //   // localStorage.setItem('dashboardItems', JSON.stringify(this.dashboard));
  //   this.sheetsIdArray = this.dashboard.map(item => item['sheetId']);
  //   if(this.dashboardName===''){
  //     this.toasterService.info('Please add dashboard Title.','info',{ positionClass: 'toast-top-center'})
  //   }else{
  //     this.takeScreenshot();
  //     this.assignOriginalDataToDashboard();
  //     this.setQuerySetIds()
  //   let obj ={
  //     grid : this.gridType,
  //     height: this.heightGrid,
  //     width: this.widthGrid,
  //     queryset_id:this.qrySetId,
  //     server_id:this.databaseId,
  //     sheet_ids:this.sheetsIdArray,
  //     selected_sheet_ids :this.sheetIdsDataSet,
  //     dashboard_name:this.dashboardName,
  //     dashboard_tag_name:this.dashboardTagName,
  //     data:this.dashboard,
  //     file_id : this.fileId,
  //     donutDecimalPlaces : this.donutDecimalPlaces
  //   }as any;
  //   if(this.fromFileId){
  //     delete obj.server_id;
  //     obj.file_id = this.fileId
  //   }
  //   this.workbechService.saveDashboard(obj).subscribe({
  //     next:(data)=>{
  //       console.log(data);
  //       this.dashboardId=data.dashboard_id;         
  //       this.dashboardTagTitle = this.sanitizer.bypassSecurityTrustHtml(this.dashboardTagName);
  //       this.updateDashbpardBoolen = true;
  //       // Swal.fire({
  //       //   icon: 'success',
  //       //   title: 'Congartualtions!',
  //       //   text: 'Dashboard Saved Successfully',
  //       //   width: '400px',
  //       // })
  //       this.toasterService.success('Dashboard Saved Successfully','success',{ positionClass: 'toast-top-right'});
  //       const encodedDashboardId = btoa(this.dashboardId.toString());
  //       this.router.navigate(['/insights/home/sheetsdashboard/'+encodedDashboardId])
  
  //     },
  //     error:(error)=>{
  //       console.log(error)
  //       Swal.fire({
  //         icon: 'error',
  //         title: 'oops!',
  //         text: error.error.message,
  //         width: '400px',
  //       })
  //     }
  //   })
  // }
  // }
  async saveDashboard() {
    this.canNavigateToAnotherPage = false;
    this.sheetsIdArray = this.dashboard
    .filter(item => item['type'] !== 'image') // Filter out items with type 'image'
    .map(item => item['sheetId']);
  
    if (this.dashboardName === '') {
      this.toasterService.info('Please add dashboard Title.', 'info', { positionClass: 'toast-top-center' });
    } else {
      try {
        // Wait for the screenshot to be taken
        await this.takeScreenshot();
  
        // Assign other data after screenshot
        this.assignOriginalDataToDashboard();
        this.setQuerySetIds();
  
        let obj = {
          grid: this.gridType,
          height: this.heightGrid,
          width: this.widthGrid,
          queryset_id: this.qrySetId,
          server_id: this.databaseId,
          sheet_ids: this.sheetsIdArray,
          selected_sheet_ids: this.sheetIdsDataSet,
          dashboard_name: this.dashboardName,
          dashboard_tag_name: this.dashboardTagName,
          data: this.dashboard,
          // file_id: this.fileId,
          donutDecimalPlaces: this.donutDecimalPlaces
        }
  
        // Save the dashboard data
        const data = await this.workbechService.saveDashboard(obj).toPromise();
        console.log(data);
        this.dashboardId = data.dashboard_id;
        this.dashboardTagTitle = this.sanitizer.bypassSecurityTrustHtml(this.dashboardTagName);
        this.updateDashbpardBoolen = true;
  
        // Call saveDashboardimage after the dashboard is saved
        await this.saveDashboardimage().toPromise(); // Wait for image saving to complete
  
        // After saving image, navigate
        const encodedDashboardId = btoa(this.dashboardId.toString());
        this.router.navigate(['/analytify/home/sheetsdashboard/' + encodedDashboardId]);
  
        // Show success message after navigation
        this.toasterService.success('Dashboard Saved Successfully', 'success', { positionClass: 'toast-top-right' });
  
      } catch (error) {
        console.error(error);
        const errorMessage = (error as { error?: { message?: string } })?.error?.message || 'An unexpected error occurred.';

        Swal.fire({
          icon: 'error',
          title: 'oops!',
          text: errorMessage ,
          width: '400px',
        });
      }
    }
  }
  
  setQuerySetIds() {
    this.qrySetId = [];
    // this.dashboard.forEach((sheet: any) =>{
    //   this.qrySetId.push(sheet.qrySetId);
    // })
    this.dashboard.forEach((sheet: any) => {
      if (sheet['type'] !== 'image') { 
        if (sheet.qrySetId) {
          this.qrySetId.push(sheet.qrySetId);
        }
      }
    });
  }
  takeScreenshot(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.startMethod();
      this.loaderService.show();
  
      setTimeout(() => {
        const element = document.getElementById('capture-element');
        if (element) {
          htmlToImage.toPng(element)
            .then((dataUrl) => {
              this.screenshotSrc = dataUrl;
              console.log('scrnsht', this.screenshotSrc);
              const imageBlob = this.workbechService.base64ToBlob(dataUrl);
              const imageBlob1 = this.workbechService.blobToFile(imageBlob);
  
              this.imageFile = imageBlob;
              this.imagename = imageBlob1;
              console.log('fileblob', this.imageFile);
              this.loaderService.hide();
              resolve(); // Resolve once the screenshot is done
            })
            .catch((error) => {
              console.error('oops, something went wrong!', error);
              reject(error); // Reject in case of error
            });
        } else {
          reject('No element found for screenshot');
        }
      }, 1000);
    });
  }
  
  downloadImageInPublic() {
    this.startMethod();
    this.loaderService.show();
    setTimeout(() => {
      const element = document.getElementById('capture-element');
      if (element) {
        htmlToImage.toPng(element)
          .then((dataUrl) => {
            // Download the image
            const link = document.createElement('a');
            link.href = dataUrl;
            link.download = 'screenshot.png'; // Set the filename
            link.click();
  
            this.loaderService.hide();
            this.endMethod(); 
          })
          .catch((error) => {
            console.error('oops, something went wrong!', error);
          });
      }
    }, 2000);
  }

  startMethod() {
    this.isOverflowHidden = true;
  }

  endMethod() {
    this.isOverflowHidden = false;
  }
  // saveDashboardimage(){
  //   var formData:any = new FormData();
  //   formData.append("dashboard_id",this.dashboardId);
  //   formData.append("imagepath",this.imageFile,this.imagename.name);

  //   this.workbechService.saveDAshboardimage(formData).subscribe({
  //     next:(data)=>{
  //       console.log(data);
  //       // Swal.fire({
  //       //   icon: 'success',
  //       //   title: 'Congartualtions!',
  //       //   text: 'Dashboard Updated Successfully',
  //       //   width: '400px',
  //       // })
  //       this.endMethod(); 
  //     },
  //     error:(error)=>{
  //       console.log(error)
  //     }
  //   })
  // }
  saveDashboardimage(): Observable<any> {
    var formData: any = new FormData();
    formData.append("dashboard_id", this.dashboardId);
    formData.append("imagepath", this.imageFile, this.imagename.name);
  
    return this.workbechService.saveDAshboardimage(formData).pipe(
      tap((data: any) => {
        console.log(data);
        // Call the endMethod after image is saved
        this.endMethod();
      })
    );
  }
  saveDashboardimageUpdate(){
    var formData: any = new FormData();
    formData.append("dashboard_id", this.dashboardId);
    formData.append("imagepath", this.imageFile, this.imagename.name);
  
     this.workbechService.saveDAshboardimage(formData).subscribe({
      next:(data)=>{
        console.log(data)
      },
      error:(error)=>{
        console.log(error);
      }
     })
   
  }
  updateDashboard(isLiveReloadData : boolean){
    if(!isLiveReloadData){
      this.takeScreenshot();
    }
    this.sheetsIdArray = this.dashboard
    .filter(item => item['type'] !== 'image') // Filter out items with type 'image'
    .map(item => item['sheetId']);
     // this.sheetsIdArray = this.dashboard.map(item => item['sheetId']);
    if(this.dashboardName===''){
      Swal.fire({
        icon: 'error',
        title: 'oops!',
        text: 'Please add Name to Dashboard',
        width: '400px',
      })
    }else{
      let dashboardData = this.assignOriginalDataToDashboard();
      this.setQuerySetIds();
      let obj;
      // if(this.fileId && this.fileId.length){
      //   obj ={
      //     grid : this.gridType,
      //     height: this.heightGrid,
      //     width: this.widthGrid,
      //     queryset_id:this.qrySetId,
      //     sheet_ids:this.sheetsIdArray,
      //     dashboard_name:this.dashboardName,
      //     dashboard_tag_name:this.dashboardTagName,
      //     selected_sheet_ids:this.sheetIdsDataSet,
      //     data : dashboardData,
      //     sheetTabs : this.sheetTabs,
      //     file_id : this.fileId,
      //     user_ids:this.usersForUpdateDashboard,
      //     role_ids:this.rolesForUpdateDashboard,
      //     donutDecimalPlaces : this.donutDecimalPlaces
      //   }as any;
      // } else {
        obj ={
          grid : this.gridType,
          height: this.heightGrid,
          width: this.widthGrid,
          queryset_id:this.qrySetId,
          server_id:this.databaseId,
          sheet_ids:this.sheetsIdArray,
          dashboard_name:this.dashboardName,
          dashboard_tag_name:this.dashboardTagName,
          selected_sheet_ids:this.sheetIdsDataSet,
          data : dashboardData,
          sheetTabs : this.sheetTabs,
          user_ids:this.usersForUpdateDashboard,
          role_ids:this.rolesForUpdateDashboard
        }
      // }
    
    // if(this.fromFileId){
    //   delete obj.server_id;
    //   obj['file_id'] = this.fileId;
    // }
    this.workbechService.updateDashboard(obj,this.dashboardId).subscribe({
      next:(data)=>{
        console.log(data);
        // Swal.fire({
        //   icon: 'success',
        //   title: 'Congartualtions!',
        //   text: 'Dashboard Updated Successfully',
        //   width: '400px',
        // })
        this.dashboardsheetsIdArray = this.sheetsIdArray;
        this.canNavigateToAnotherPage = false;
        this.toasterService.success('Dashboard Updated Successfully','success',{ positionClass: 'toast-top-right'});
        if(!isLiveReloadData){
          this.saveDashboardimageUpdate();
        }
        this.endMethod(); 
      },
      error:(error)=>{
        console.log(error);
        Swal.fire({
          icon: 'error',
          title: 'oops!',
          text: error?.error?.message,
          width: '400px',
        });
      }
    })
  }
  }

  assignOriginalDataToDashboard(){
    let dashboardData = _.cloneDeep(this.dashboard);
    dashboardData.forEach((item1:any) => {
      if(item1.drillDownIndex >= 0){
        item1.drillDownIndex = 0;
        item1.drillDownObject = [];
      }
        if(item1.chartId == '6' && item1['originalData']){//bar
          if(item1.isEChart){
            item1.echartOptions = item1['originalData'].chartOptions;
          } else {
            item1.chartOptions = item1['originalData'].chartOptions;
          }
        delete item1['originalData'];
        }if(item1.chartId == '1' && item1['originalData']){//table
          item1['tableData'] = item1['originalData']['tableData'];
          delete item1['originalData'];
          }
          if(item1.chartId == '9' && item1['originalData']){//pivot
            item1['pivotData'] = item1['originalData']['pivotData'];
            delete item1['originalData'];
            }
        if(item1.chartId == '25' && item1['originalData']){//KPI
          item1['kpiData'] = item1['originalData'];
          delete item1['originalData'];
          }
        if(item1.chartId == '24' && item1['originalData']){//pie
          if(item1.isEChart){
            item1.echartOptions = item1['originalData'].chartOptions;
          } else {
            item1.chartOptions = item1['originalData'].chartOptions;
          }
        delete item1['originalData'];
        }
        if(item1.chartId == '13' && item1['originalData']){//line
          if(item1.isEChart){
            item1.echartOptions = item1['originalData'].chartOptions;
          } else {
            item1.chartOptions = item1['originalData'].chartOptions;
          }
        delete item1['originalData'];
        }
        if(item1.chartId == '17' && item1['originalData']){//area
          if(item1.isEChart){
            item1.echartOptions = item1['originalData'].chartOptions;
          } else {
            item1.chartOptions = item1['originalData'].chartOptions;
          }
        delete item1['originalData'];
        }
        if(item1.chartId == '7' && item1['originalData']){//sidebyside
          if(item1.isEChart){
            item1.echartOptions = item1['originalData'].chartOptions;
          } else {
            item1.chartOptions = item1['originalData'].chartOptions;
          }
          delete item1['originalData'];
        }
        if(item1.chartId == '2' && item1['originalData']){//hstacked
          if(item1.isEChart){
            item1.echartOptions = item1['originalData'].chartOptions;
          } else {
            item1.chartOptions = item1['originalData'].chartOptions;
          }
          delete item1['originalData'];
        }
        if(item1.chartId == '5' && item1['originalData']){//stacked
          if(item1.isEChart){
            item1.echartOptions = item1['originalData'].chartOptions;
          } else {
            item1.chartOptions = item1['originalData'].chartOptions;
          }
          delete item1['originalData'];
        }
        if(item1.chartId == '4' && item1['originalData']){//barline
          if(item1.isEChart){
            item1.echartOptions = item1['originalData'].chartOptions;
          } else {
            item1.chartOptions = item1['originalData'].chartOptions;
          }
          delete item1['originalData'];
        }
        if(item1.chartId == '3' && item1['originalData']){//hgrouped
          if(item1.isEChart){
            item1.echartOptions = item1['originalData'].chartOptions;
          } else {
            item1.chartOptions = item1['originalData'].chartOptions;
          }
          delete item1['originalData'];
        }
        if(item1.chartId == '8' && item1['originalData']){//multiline
          if(item1.isEChart){
            item1.echartOptions = item1['originalData'].chartOptions;
          } else {
            item1.chartOptions = item1['originalData'].chartOptions;
          }
          delete item1['originalData'];
        }
        if(item1.chartId == '12' && item1['originalData']){//radar
          if(item1.isEChart){
            item1.echartOptions = item1['originalData'].chartOptions;
          } else {
            item1.chartOptions = item1['originalData'].chartOptions;
          }
          delete item1['originalData'];
        }
        if(item1.chartId == '29' && item1['originalData']){//world map
          if(item1.isEChart){
            item1.echartOptions = item1['originalData'].chartOptions;
          }
          delete item1['originalData'];
        }
        if(item1.chartId == '27' && item1['originalData']){//funnel
          if(item1.isEChart){
            item1.echartOptions = item1['originalData'].chartOptions;
          }
          delete item1['originalData'];
        }
        if(item1.chartId == '26' && item1['originalData']){//heatmap
        if(item1.isEChart){
          item1.echartOptions = item1['originalData'].chartOptions;
        } else {
          item1.chartOptions = item1['originalData'].chartOptions;
        }
        delete item1['originalData'];
      }
        if(item1.chartId == '11' && item1['originalData']){//calendar
          if(item1.isEChart){
            item1.echartOptions = item1['originalData'].chartOptions;
          }
          delete item1['originalData'];
        }
    });
   return  dashboardData;
  }

  sheetsDataWithQuerysetIdTest(){
    let obj ;
      obj ={
      server_id:this.databaseId[0],
      queryset_id:this.qrySetId[0]
      }
  
    this.workbechService.sheetsDataWithQuerysetId(obj)
    .subscribe({next: (data) => {
       console.log('sheetData',data)
       this.databaseName= data[0].database_name;
      //  this.sheetData = [];
      //  data.forEach((sheetData : any ) => {
      //   this.sheetData.push(sheetData.sheets[0]);
      //  })
    this.dashboardNew = data.map((sheet:any) => ({
      id:uuidv4(),
      cols: 1,
      rows: 1,
      y: 0,
      x: 0,
      sheetType:sheet.sheet_type,
      databaseId : sheet.hierarchy_id,
      // fileId : sheet.file_id,
      qrySetId : sheet.queryset_id,
      sheetId:sheet.sheet_id,
      chartType:sheet.chart,
      chartId:sheet.chart_id,
      column_Data : sheet.sheet_data.columns_data,
      row_Data : sheet.sheet_data.rows_data,
      isEChart : sheet.sheet_data.isEChart,
      drillDownHierarchy : sheet.sheet_data.drillDownHierarchy,
      isDrillDownData : sheet.sheet_data.isDrillDownData,
      data: { title: sheet.sheet_name, content: 'Content of card New', sheetTagName:sheet.sheet_tag_name? sheet.sheet_tag_name:sheet.sheet_name },
      kpiData: sheet.sheet_type === 'Chart' && sheet.chart_id === 25
      ? (() => {
          this.kpiData = {
            kpiNumber : sheet.sheet_data?.results?.kpiNumber || 0,
            kpiPrefix : sheet.sheet_data?.results?.kpiPrefix || '',
            kpiSuffix : sheet.sheet_data?.results?.kpiSuffix || '',
            kpiDecimalUnit : sheet.sheet_data?.results?.kpiDecimalUnit || 'none',
            kpiDecimalPlaces : sheet.sheet_data?.results?.kpiDecimalPlaces || 0,
            rows: sheet.sheet_data?.results?.kpiData || [],       // Default to an empty array if not provided
            fontSize: sheet.sheet_data?.results?.kpiFontSize || '16px', // Default font size
            color: sheet.sheet_data?.results?.kpicolor || '#000000',    // Default color (black)
          };
          return this.kpiData; // Return the kpi object to kpiData
        })()
      : undefined,
      chartOptions: sheet.sheet_type === 'Chart' ? {
        // ...this.getChartOptions(sheet.chart,sheet?.sheet_data.x_values,sheet?.sheet_data.y_values),
        ... this.getChartOptionsBasedOnType(sheet) as unknown as ApexOptions,
        // chart: { type: sheet.chart, height: 300 },
        //chartData:this.getChartData(sheet.sheet_data.results, sheet.chart)
      } : undefined,
      tableData: sheet.sheet_type === 'Table' ? {
       ... this.getTableData(sheet.sheet_data)

      }
       : undefined,
       numberFormat: {
        donutDecimalPlaces:this.donutDecimalPlaces,
        decimalPlaces:sheet?.sheet_data?.numberFormat?.decimalPlaces,
        displayUnits:sheet?.sheet_data?.numberFormat?.displayUnits,
        prefix:sheet?.sheet_data?.numberFormat?.prefix,
        suffix:sheet?.sheet_data?.numberFormat?.suffix
      },
      pivotData: sheet.sheet_type === 'PIVOT' ? {
        pivotDataTransformed:sheet?.sheet_data?.pivotTransformedData,
        pivotRowData:sheet?.sheet_data?.row,
        pivotMeasureData:sheet?.sheet_data?.pivotMeasure_Data,
        pivotColData:sheet?.sheet_data?.col
      }
      : undefined,
      customizeOptions: sheet?.sheet_data?.customizeOptions
    }));
    this.sheetIdsDataSet = this.dashboardNew.map(item => item['sheetId']);
    console.log('dashboardNew',this.dashboardNew)
      },
    error:(error)=>{
    console.log(error);
   }
   })
  }
  sheetsDataWithQuerysetId(){
    const obj ={
      sheetIds:this.sheetIdsDataSet,
    }
    this.workbechService.sheetsDataWithQuerysetId(obj)
    .subscribe({next: (data) => {
       console.log('sheetData',data)
       this.sheetData = data.sheets,
       this.databaseName= data.database_name
    this.dashboardNew = this.sheetData.map((sheet:any) => ({
      id:uuidv4(),
      cols: 1,
      rows: 1,
      y: 10,
      x: 10,
      sheetType:sheet.sheet_type,
      sheetId:sheet.sheet_id,
      chartType:sheet.chart,
      chartId:sheet.chart_id,
      databaseId : sheet.hierarchy_id,
      // fileId : sheet.file_id,
      qrySetId : sheet.queryset_id,
      data: { title: sheet.sheet_name, content: 'Content of card  New', sheetTagName: sheet.sheet_tag_name?sheet.sheet_tag_name:sheet.sheet_name },
      selectedSheet : sheet.selectedSheet,
      kpiData: sheet.sheet_type === 'Chart' && sheet.chart_id === 25
      ? (() => {
          this.kpiData = {
            kpiNumber : sheet.sheet_data?.results?.kpiNumber || 0,
            kpiPrefix : sheet.sheet_data?.results?.kpiPrefix || '',
            kpiSuffix : sheet.sheet_data?.results?.kpiSuffix || '',
            kpiDecimalUnit : sheet.sheet_data?.results?.kpiDecimalUnit || 'none',
            kpiDecimalPlaces : sheet.sheet_data?.results?.kpiDecimalPlaces || 0,
            rows: sheet.sheet_data?.results?.kpiData || [],       // Default to an empty array if not provided
            fontSize: sheet.sheet_data?.results?.kpiFontSize || '16px', // Default font size
            color: sheet.sheet_data?.results?.kpicolor || '#000000',    // Default color (black)
          };
          return this.kpiData; // Return the kpi object to kpiData
        })()
      : undefined,
      chartOptions: sheet.sheet_type === 'Chart' ? {
        // ...this.getChartOptions(sheet.chart,sheet?.sheet_data.x_values,sheet?.sheet_data.y_values),
        ... this.getChartOptionsBasedOnType(sheet) as unknown as ApexOptions,
        // chart: { type: sheet.chart, height: 300 },
        //chartData:this.getChartData(sheet.sheet_data.results, sheet.chart)
      } : undefined,
      tableData: sheet.sheet_type === 'Table' ? {
       ... this.getTableData(sheet.sheet_data)

      }
       : undefined,
       numberFormat: {
        donutDecimalPlaces:this.donutDecimalPlaces,
        decimalPlaces:sheet?.sheet_data?.numberFormat?.decimalPlaces,
        displayUnits:sheet?.sheet_data?.numberFormat?.displayUnits,
        prefix:sheet?.sheet_data?.numberFormat?.prefix,
        suffix:sheet?.sheet_data?.numberFormat?.suffix
      },
      customizeOptions: sheet?.sheet_data?.customizeOptions
    }));
      if (this.dashboardView) {
        this.getSavedDashboardData();
      }
    let mapper = [0];
        this.testData = mapper.map((sheet:any) => ({
      id:uuidv4(),
      cols: 1,
      rows: 1,
      y: 10,
      x: 10,
      sheetType:111,
      sheetId:111,
      chartType:'Tags',
      chartId:111,
      data: { title: 'Tags', content: 'Content of card New' },
    }));
    console.log('testData',this.testData)
      },
    error:(error)=>{
    console.log(error);
   }
   })
  }
  // getSheetData(){
  //   this.workbechService.getSheetData()
  //   .subscribe({next: (data) => {
  //      console.log('sheetData',data)
  //      this.sheetData = data
  //   this.dashboardNew = this.sheetData.map((sheet:any) => ({
  //     id:uuidv4(),
  //     cols: 2,
  //     rows: 1,
  //     y: 0,
  //     x: 0,
  //     sheetType:sheet.sheet_type,
  //     data: { title: sheet.sheet_name, content: 'Content of card New' },
  //     chartOptions: sheet.sheet_type === 'Chart' ? {
  //       // ...this.getChartOptions(sheet.chart,sheet?.sheet_data.x_values,sheet?.sheet_data.y_values),
  //       ... this.getChartOptionsBasedOnType(sheet),
  //       chart: { type: sheet.chart, height: 300 },
  //       //chartData:this.getChartData(sheet.sheet_data.results, sheet.chart)
  //     } : undefined,
  //     tableData: sheet.sheet_type === 'Table' ? {
  //      ... this.getTableData(sheet.sheet_data)

  //     }
  //      : undefined
  //   }));
  //   console.log('dashboardNew',this.dashboardNew)
  //     },
  //   error:(error)=>{
  //   console.log(error);
  //  }
  //  })
  // }
  flattenDimensions(dimensions: Dimension[]): string[] {
    const numCategories = Math.max(...dimensions.map(dim => dim.values.length));
    return Array.from({ length: numCategories }, (_, index) => {
      return dimensions.map(dim => dim.values[index] || '').join(',');
    });
  }
  getChartOptionsBasedOnType(sheet:any){
    if(sheet.chart_id === 9){
      let xaxis = sheet.sheet_data?.results?.barXaxis;
      let yaxis = sheet.sheet_data?.results?.barYaxis;
      let savedOptions = sheet.sheet_data.savedChartOptions;
      return this.barChartOptions(xaxis,yaxis,savedOptions,sheet.sheet_data.isEChart) 
    }
    if(sheet.chart_id === 6){
      let xaxis = sheet.sheet_data?.results?.barXaxis;
      let yaxis = sheet.sheet_data?.results?.barYaxis;
      let savedOptions = sheet.sheet_data.savedChartOptions;
      return this.barChartOptions(xaxis,yaxis,savedOptions,sheet.sheet_data.isEChart) 
    }
    if(sheet.chart_id === 29){
      let xaxis = sheet.sheet_data?.results?.mapChartXaxis;
      let yaxis = sheet.sheet_data?.results?.mapChartYaxis;
      let savedOptions = sheet.sheet_data.savedChartOptions;
      return sheet.sheet_data.savedChartOptions;
      // return this.mapChartOptions(xaxis,yaxis,savedOptions) 
    }
    if(sheet.chart_id === 17){
      let xaxis = sheet.sheet_data?.results?.areaXaxis;
      let yaxis = sheet.sheet_data?.results?.areaYaxis;
      let savedOptions = sheet.sheet_data.savedChartOptions;
      return this.areaChartOptions(xaxis,yaxis,savedOptions,sheet.sheet_data.isEChart)
    }
    if(sheet.chart_id === 13){
      let xaxis = sheet.sheet_data?.results?.lineXaxis;
      let yaxis = sheet.sheet_data?.results?.lineYaxis;
      let savedOptions = sheet.sheet_data.savedChartOptions;
      return this.lineChartOptions(xaxis,yaxis,savedOptions,sheet.sheet_data.isEChart)
    }
    if(sheet.chart_id === 24){
      let xaxis = sheet.sheet_data?.results?.pieXaxis;
      let yaxis = sheet.sheet_data?.results?.pieYaxis;
      let savedOptions = sheet.sheet_data.savedChartOptions;
      return this.pieChartOptions(xaxis,yaxis,savedOptions,sheet.sheet_data.isEChart)
    }
    //sidebyside
    if(sheet.chart_id === 7){
      let xaxis = sheet.sheet_data?.results?.sidebysideBarXaxis;
      let yaxis = sheet.sheet_data?.results?.sidebysideBarYaxis;
      let savedOptions = sheet.sheet_data.savedChartOptions;

      const dimensions: Dimension[] =xaxis
      const categories = this.flattenDimensions(dimensions)
      return this.sidebySideBarChartOptions(categories,yaxis,savedOptions,sheet.sheet_data.isEChart)

    }
    if(sheet.chart_id === 12){//radar
      return sheet.sheet_data.savedChartOptions;
      let xaxis = sheet.sheet_data?.results?.sidebysideBarXaxis;
      let yaxis = sheet.sheet_data?.results?.sidebysideBarYaxis;
      let savedOptions = sheet.sheet_data.savedChartOptions;

      const dimensions: Dimension[] =xaxis
      const categories = this.flattenDimensions(dimensions)
      return this.sidebySideBarChartOptions(categories,yaxis,savedOptions,sheet.sheet_data.isEChart)

    }
    if(sheet.chart_id === 5){
      let xaxis = sheet.sheet_data?.results?.stokedBarXaxis;
      let yaxis = sheet.sheet_data?.results?.stokedBarYaxis;
      let savedOptions = sheet.sheet_data.savedChartOptions;

      const dimensions: Dimension[] = xaxis;
      const categories = this.flattenDimensions(dimensions);

      return this.stockedBarChartOptions(categories,yaxis,savedOptions,sheet.sheet_data.isEChart)
    }
    if(sheet.chart_id === 4){
      let xaxis = sheet.sheet_data?.results?.barLineXaxis;
      let yaxis = sheet.sheet_data?.results?.barLineYaxis;
      let savedOptions = sheet.sheet_data.savedChartOptions;
      console.log('barlinexaxis',xaxis)
      const dimensions: Dimension[] = xaxis;
      const categories = this.flattenDimensions(dimensions);
      console.log('barlinecategories',categories)

      return this.barLineChartOptions(categories,yaxis,savedOptions)
    }
    if(sheet.chart_id === 2){
      let xaxis = sheet.sheet_data?.results?.hStockedXaxis;
      let yaxis = sheet.sheet_data?.results?.hStockedYaxis;
      let savedOptions = sheet.sheet_data.savedChartOptions;

      const dimensions: Dimension[] = xaxis;
      const categories = this.flattenDimensions(dimensions);
      return this.hStockedBarChartOptions(categories,yaxis,savedOptions,sheet.sheet_data.isEChart);
    }
    if(sheet.chart_id === 3){
      let xaxis = sheet.sheet_data?.results?.hgroupedXaxis;
      let yaxis = sheet.sheet_data?.results?.hgroupedYaxis;
      let savedOptions = sheet.sheet_data.savedChartOptions;

      const dimensions: Dimension[] = xaxis;
      const categories = this.flattenDimensions(dimensions);

      return this.hGroupedChartOptions(categories,yaxis,savedOptions,sheet.sheet_data.isEChart)
    }
    if(sheet.chart_id === 8){
      let xaxis = sheet.sheet_data?.results?.multiLineXaxis;
      let yaxis = sheet.sheet_data?.results?.multiLineYaxis;
      let savedOptions = sheet.sheet_data.savedChartOptions;

      const dimensions: Dimension[] = xaxis;
      const categories = this.flattenDimensions(dimensions);

      return this.multiLineChartOptions(categories,yaxis,savedOptions)
    }
    if(sheet.chart_id === 10){
      let xaxis = sheet.sheet_data?.results?.donutXaxis;
      let yaxis = sheet.sheet_data?.results?.donutYaxis;
      let savedOptions = sheet.sheet_data.savedChartOptions;
      this.donutDecimalPlaces = sheet.sheet_data?.results?.decimalplaces;
      return this.donutChartOptions(xaxis,yaxis,savedOptions,sheet.sheet_data.isEChart)
    }
    if(sheet.chart_id === 26){
      let savedOptions = sheet.sheet_data.savedChartOptions;
      return savedOptions;
    }
    if(sheet.chart_id === 27){
      let savedOptions = sheet.sheet_data.savedChartOptions;
      return savedOptions;
    }
    if(sheet.chart_id === 28){
      let savedOptions = sheet.sheet_data.savedChartOptions;
      return savedOptions;
    }
    if(sheet.chart_id === 11){
      let savedOptions = sheet.sheet_data.savedChartOptions;
      return savedOptions;
    }
  }

  getChartData(results: any, chartType: string): any[] | undefined{
    switch (chartType) {
      case 'bar':
         return results.bar.map((item: any) => ({ name: item.col, value: item.row }));
         //return results.bar.forEach((item: { col: any; row: any; }) => chartOptions.series[0].data.push(item.col));
      case 'line':
        return [{xAis:results.lineXaxis,yAxis:results.lineYaxis}]
      case 'area':
        return results.areaXaxis+results.areaYaxis
      default:
        return undefined;        
    }
  }
getTableData(tableData: any): { headers: any[], rows: any[],banding: any, color1: any, color2: any ,tableItemsPerPage : any,tableTotalItems : any, tablePage : number } {
    // Example implementation for table data extraction
    // this.tableItemsPerPage=tableData.results.items_per_page
    // this.tableTotalItems = tableData.results.total_items
    return {
      headers: tableData.results.tableColumns,
      rows: tableData.results.tableData,
      banding: tableData.results.banding,
      color1: tableData.results.color1,
      color2: tableData.results.color2,
      tableItemsPerPage : tableData.results.items_per_page,
      tableTotalItems : tableData.results.total_items,
      tablePage : 1
    };
  }
  onDrag(event: any, item: any){
    let data = JSON.stringify(item);
        event.dataTransfer.setData('item', data);
  }

  
  dropToAddIntoNestedGridster(event: { preventDefault: () => void; stopPropagation: () => void; }, parent: any): void {
    event.preventDefault();
    event.stopPropagation();
    // this.setupDesignerItemToAdd(event, parent);
}

allowDrop(ev : any): void {
  ev.preventDefault();
}
  drop(event: any) {
    this.canNavigateToAnotherPage = true;
    if(this.colArray.length >0 && this.rowArray.length>0){
      this.colArray = [];
      this.rowArray = [];
    }
    if (event.previousContainer === event.container) {
      moveItemInArray(event.container.data, event.previousIndex, event.currentIndex);
    } else {
      console.log('Transfering item to new container')
      console.log('Transferring item to new container');
      
      let item: any = event.previousContainer.data[event.previousIndex];
      console.log('Original item:', JSON.stringify(item));
      
      // Creating a deep copy of the item
      let copy: any = JSON.parse(JSON.stringify(item));
      console.log('Copy of item:', JSON.stringify(copy));
      
      // Initialize an empty object to hold the copied attributes
      let element: any = {
        id:copy.id,
        x:10,
        y: 20,
        rows: 1,
        cols:1,
        data: copy.data,
        sheetType:copy.sheetType,
        sheetId:copy.sheetId,
        chartType:copy.chartType,
        databaseId : copy.databaseId,
        qrySetId : copy.qrySetId,
        // fileId : copy.fileId,
        chartId:copy.chartId,
        chartOptions: copy.chartOptions,
        chartInstance: copy.chartInstance,
        tableData:copy.tableData,
        selectedSheet : true,
        chartData:copy.chartOptions?.chartData || [],
        kpiData:copy.kpiData,
        isEChart : copy.isEChart,
        echartOptions :  copy.chartOptions,
        drillDownHierarchy : copy.drillDownHierarchy,
        column_Data : copy.column_Data,
      row_Data : copy.row_Data,
      drillDownObject : [],
      drillDownIndex : 0,
      isDrillDownData : copy.isDrillDownData,
      numberFormat : copy.numberFormat,
      customizeOptions: copy.customizeOptions,
      pivotData:copy.pivotData
      };
      // this.qrySetId.push(copy.qrySetId);
      // if(copy.fileId){
      //   this.fileId.push(copy.fileId);
      // } else {
        this.databaseId.push(copy.databaseId);
      // }
    //   if(element.chartOptions?.chart?.type === 'bar'){
    //      element['chartData'].forEach((item: { name: any; value: any; }) => {
    //       this.colArray.push(item.name);
    //       this.rowArray.push(item.value);        
    //       // this.getChartOptions(element.chartOptions?.chart?.type || 'bar',this.colArray,this.rowArray);

    //     });      
    //   }
    //   if(element.chartOptions?.chart?.type === 'line'){
    //     this.colArray = element['chartData'][0].xAis
    //     this.rowArray = element['chartData'][0].yAxis
    //     console.log('linedata',this.colArray,this.rowArray)
    //     // this.getChartOptions(element.chartOptions?.chart?.type || 'bar',this.colArray,this.rowArray);

    //  }
    //  console.log(this.rowArray);
     //this.getChartOptions(element.chartOptions?.chart?.type || 'bar');
    //  if(event.event.target.offsetParent.id == 'cdk-drop-list-0'){
      const index = this.findSheetIndex(copy.sheetId);
      if (index == -1) {
        this.disableDashboardUpdate = false;
        this.setDashboardNewSheets(copy.sheetId, true);
        
        let self = this;
        if(element.chartOptions && element.chartOptions.chart) {
        element.chartOptions.chart.events = {
          markerClick: (event: any, chartContext: any, config: any) => {
            let selectedXValue;
            if(element.chartId == 24 || element.chartId == 10 || element.chartId == 17 || element.chartId == 4){
              selectedXValue = element.chartOptions.labels[config.dataPointIndex];
            } else {
              selectedXValue = element.chartOptions.xaxis.categories[config.dataPointIndex];
            }
            if(self.actionId && element.sheetId === self.sourceSheetId){
              self.setDrillThrough(selectedXValue, element);  
            }
          },
          dataPointSelection: function (event: any, chartContext: any, config: any) {
            let selectedXValue;
            if(element.chartId == 24 || element.chartId == 10){
              selectedXValue = element.chartOptions.labels[config.dataPointIndex];
            } else {
              selectedXValue = element.chartOptions.xaxis.categories[config.dataPointIndex];
            }
            if(self.actionId && element.sheetId === self.sourceSheetId){
              self.setDrillThrough(selectedXValue, element);  
            }
            if (element.drillDownIndex < element.drillDownHierarchy.length - 1) {
              // const selectedXValue = element.chartOptions.series[0].data[config.dataPointIndex];
              console.log('X-axis value:', selectedXValue);
              let nestedKey = element.drillDownHierarchy[element.drillDownIndex];
              element.drillDownIndex++;
              let obj = { [nestedKey]: selectedXValue };
              element.drillDownObject.push(obj);
              self.dataExtraction(element);
            }
          },
          mounted: function(chartContext:any, config:any) {
            if (element.chartId == 28) {
              let color = element?.chartOptions?.plotOptions?.radialBar?.dataLabels?.name?.color;
              const applyStyles = () => {
                const valueElement = document.querySelector('.apexcharts-datalabel-value') as HTMLElement;
                if (valueElement) {
                  valueElement.style.fill = color;
                  valueElement.style.setProperty('fill', color, 'important');
                }
  
                const nameElement = document.querySelector('.apexcharts-datalabel-label') as HTMLElement;
                if (nameElement) {
                  nameElement.style.fill = color;
                  nameElement.style.setProperty('fill', color, 'important');
                }
              };
              // Initial styling
              applyStyles();
  
              // Monitor DOM for changes
              const observer = new MutationObserver(() => {
                applyStyles();
              });
              const chartContainer = document.querySelector('.apexcharts-inner');
              if (chartContainer) {
                observer.observe(chartContainer, { childList: true, subtree: true });
              }
            }
          },
          updated: function(chartContext:any, config:any) {
            if (element.chartId == 28) {
              let color = element?.chartOptions?.plotOptions?.radialBar?.dataLabels?.name?.color;
              const applyStyles = () => {
                const valueElement = document.querySelector('.apexcharts-datalabel-value') as HTMLElement;
                if (valueElement) {
                  valueElement.style.fill = color;
                  valueElement.style.setProperty('fill', color, 'important');
                }
  
                const nameElement = document.querySelector('.apexcharts-datalabel-label') as HTMLElement;
                if (nameElement) {
                  nameElement.style.fill = color;
                  nameElement.style.setProperty('fill', color, 'important');
                }
              };
              // Initial styling
              applyStyles();
  
              // Monitor DOM for changes
              const observer = new MutationObserver(() => {
                applyStyles();
              });
              const chartContainer = document.querySelector('.apexcharts-inner');
              if (chartContainer) {
                observer.observe(chartContainer, { childList: true, subtree: true });
              }
            }
          }
        };
      }else if(element.chartId == 29 && element.echartOptions){
        this.chartType = 'map';
        element.echartOptions?.series[0]?.data?.forEach((data:any)=>{
          this.chartsColumnData.push(data.name);
          this.chartsRowData.push(data.value);
        });
        this.dualAxisColumnData = [{
          name : element?.column_Data[0][0],
          values : this.chartsColumnData 
        }]
        this.dualAxisRowData = [{
          name : element?.row_Data[0][0],
          data : this.chartsRowData
        }]
        element.echartOptions.tooltip= {
          formatter: (params: any) => {
            const { name, data } = params;
            if (data) {
              const keys = Object.keys(data);
        const values = Object.values(data);
        let formattedString = '';
        keys.forEach((key, index) => {
          if(key)
          formattedString += `${key}: ${values[index]}<br/>`;
        });
  
        return formattedString;
             
            } else {
              return `${name}: No Data`;
            }
          }
      }
    }
    if(element.chartId == 9){
      let transformedData :any =[];
      let headers: string[] = [];

     let columnKeys = element.pivotData?.pivotColData?.map((col: any) => col.column); 
     let rowKeys = element.pivotData?.pivotRowData?.map((row: any) => row.col);
    let valueKeys = element.pivotData?.pivotMeasureData?.map((col:any) =>col.col)
    element.pivotData?.pivotColData?.forEach((colObj: any) => {
      headers.push(colObj.column);
    });

    element.pivotData?.pivotRowData?.forEach((rowObj: any) => {
      headers.push(rowObj.col);
    });
    element.pivotData?.pivotMeasureData?.forEach((colObj: any) => {
      headers.push(colObj.col);
    });

    transformedData.push(headers); 
    let numRows = 0;
    if (element.pivotData?.pivotColData?.length > 0) {
        numRows = element.pivotData.pivotColData[0]?.result_data?.length || 0;
    } else if (element.pivotData?.pivotRowData?.length > 0) {
        numRows = element.pivotData.pivotRowData[0]?.result_data?.length || 0;
    } else if (element.pivotData?.pivotMeasureData?.length > 0) {
        numRows = element.pivotData.pivotMeasureData[0]?.result_data?.length || 0;
    }

    for (let i = 0; i < numRows; i++) {
      let rowArray: any[] = []; 
      element.pivotData?.pivotColData.forEach((colObj: any) => {
        rowArray.push(colObj.result_data[i]);
      });
      element.pivotData?.pivotRowData.forEach((rowObj: any) => {
        rowArray.push(rowObj.result_data[i]);
      });
      element.pivotData?.pivotMeasureData.forEach((rowObj: any) => {
        rowArray.push(rowObj.result_data[i]);
      });

      transformedData.push(rowArray);
    }
      setTimeout(() => {
      if (this.pivotContainer && this.pivotContainer.nativeElement) {
          ($(this.pivotContainer.nativeElement) as any).pivot(transformedData, {
            rows: columnKeys,  
            cols: valueKeys, 
            // vals: this.valueKeys, 
            aggregator:$.pivotUtilities.aggregators["Sum"](rowKeys),
            rendererName: "Table"
          });
      }        
    }, 1000);
  }
        this.dashboard.push(element);
      }
    //  } else {
    //   this.nestedDashboard.push(element);
    //  }
     
    //  this.initializeChartData(element);  // Initialize chart after adding
    this.dashboard.forEach((sheet:any)=>{
      console.log('Before sanitization:', sheet.data.sheetTagName);
      this.sheetTagTitle[sheet.data.title] = this.sanitizer.bypassSecurityTrustHtml(sheet.data.sheetTagName);
      console.log('After sanitization:', sheet.data.sheetTagName);

      if(sheet['chartId'] === 10 && sheet.chartOptions && sheet.chartOptions.plotOptions && sheet.chartOptions.plotOptions.pie && sheet.chartOptions.plotOptions.pie.donut && sheet.chartOptions.plotOptions.pie.donut.labels && sheet.chartOptions.plotOptions.pie.donut.labels.total){
        sheet.chartOptions.plotOptions.pie.donut.labels.total.formatter = (w:any) => {
          return w.globals.seriesTotals.reduce((a:any, b:any) => {
            return +a + b
          }, 0).toFixed(this.donutDecimalPlaces);
        };
      }
      let chartId: number = sheet['chartId'];
      const numberFormat = sheet?.numberFormat;
      const isEcharts = sheet?.isEChart;
      this.updateNumberFormat(sheet, numberFormat, chartId, isEcharts);
      // if (![10, 24].includes(chartId) && (numberFormat?.decimalPlaces || numberFormat?.displayUnits || numberFormat?.prefix || numberFormat?.suffix)) {
      //   if([2,3].includes(chartId)){
      //     if (sheet.chartOptions?.xaxis?.labels && sheet.chartOptions?.dataLabels) {
      //       sheet.chartOptions.xaxis.labels.formatter = (val: number) => {
      //         return this.formatNumber(val, numberFormat?.decimalPlaces, numberFormat?.displayUnits, numberFormat?.prefix, numberFormat?.suffix);
      //       };            
      //       sheet.chartOptions.dataLabels.formatter = (val: number) => {
      //         return this.formatNumber(val, numberFormat?.decimalPlaces, numberFormat?.displayUnits, numberFormat?.prefix, numberFormat?.suffix);
      //       };
      //     }
      //   }
      //   else{
      //     if (sheet.chartOptions?.yaxis?.labels && sheet.chartOptions?.dataLabels) {
      //       sheet.chartOptions.yaxis.labels.formatter = (val: number) => {
      //         return this.formatNumber(val, numberFormat?.decimalPlaces, numberFormat?.displayUnits, numberFormat?.prefix, numberFormat?.suffix);
      //       };
      //       sheet.chartOptions.dataLabels.formatter = (val: number) => {
      //         return this.formatNumber(val, numberFormat?.decimalPlaces, numberFormat?.displayUnits, numberFormat?.prefix, numberFormat?.suffix);
      //       };
      //     }
      //     else if(sheet.chartOptions?.yaxis[0]?.labels && sheet.chartOptions?.dataLabels){
      //       sheet.chartOptions.yaxis[0].labels.formatter = (val: number) => {
      //         return this.formatNumber(val, numberFormat?.decimalPlaces, numberFormat?.displayUnits, numberFormat?.prefix, numberFormat?.suffix);
      //       };
      //       sheet.chartOptions.dataLabels.formatter = (val: number) => {
      //         return this.formatNumber(val, numberFormat?.decimalPlaces, numberFormat?.displayUnits, numberFormat?.prefix, numberFormat?.suffix);
      //       };
      //     }
      //   }
      // }
      // if([26, 27].includes(chartId) && (numberFormat?.decimalPlaces || numberFormat?.displayUnits || numberFormat?.prefix || numberFormat?.suffix)){
      //   if (sheet.chartOptions?.dataLabels) {
      //     sheet.chartOptions.dataLabels.formatter = (val: number) => {
      //       return this.formatNumber(val, numberFormat?.decimalPlaces, numberFormat?.displayUnits, numberFormat?.prefix, numberFormat?.suffix);
      //     };
      //   }
      // }
      if(chartId == 11){
        sheet.echartOptions.tooltip.formatter =  function (params: any) {
          const date = params.data[0];
          const value = params.data[1];
          return `Date: ${date}<br/>Value: ${value}`;
        };
        this.calendarTotalHeight = ((150 * sheet.echartOptions.calendar.length) + 25) + 'px';
      }
      if(chartId == 1){
        if(sheet?.tableData?.tableItemsPerPage){
          sheet.tableData.tableItemsPerPage = 10;
        }
        if(sheet?.tableData?.tablePage){
          sheet.tableData.tablePage = 1;
        }
      }
    });
     console.log('draggedDashboard',this.dashboard)
    }
  }

  setDashboardNewSheets(sheetId: number, selectedSheet: boolean) {
    this.dashboardNew = this.dashboardNew.map(sheet => {
      if (sheet['sheetId'] === sheetId) {
        return { ...sheet, selectedSheet: selectedSheet };
      }
      return sheet;
    });
  }

  dropNested(event: CdkDragDrop<DashboardItem[]>,nestedItem : DashboardItem){
    if(this.colArray.length >0 && this.rowArray.length>0){
      this.colArray = [];
      this.rowArray = [];
    }
    if (event.previousContainer === event.container) {
      moveItemInArray(event.container.data, event.previousIndex, event.currentIndex);
    } else {
      console.log('Transfering item to new container')
      console.log('Transferring item to new container');
      
      let item: any = event.previousContainer.data[event.previousIndex];
      console.log('Original item:', JSON.stringify(item));
      
      // Creating a deep copy of the item
      let copy: any = JSON.parse(JSON.stringify(item));
      console.log('Copy of item:', JSON.stringify(copy));
      
      // Initialize an empty object to hold the copied attributes
      let element: DashboardItem = {
        id:copy.id,
        x: copy.x,
        y: copy.y,
        rows: copy.rows,
        cols: copy.cols,
        data: copy.data,
        sheetType:copy.sheetType,
        sheetId:copy.sheetId,
        chartType:copy.chartType,
        chartId:copy.chartId,
        databaseId : copy.databaseId,
    qrySetId : copy.qrySetId,
        chartOptions: copy.chartOptions,
        chartInstance: copy.chartInstance,
        tableData:copy.tableData,
        chartData:copy.chartOptions?.chartData || [],
      };

     this.nestedDashboard.push(element);
    //  this.initializeChartData(element);  // Initialize chart after adding
     console.log('draggedDashboard',this.dashboard)
  }
}

arraysHaveSameData(arr1: number[], arr2: number[]): boolean {
  // Check if arrays are of the same length
  if (arr1.length !== arr2.length) {
    return false;
  }

  // Sort both arrays and check if every element is the same
  const sortedArr1 = arr1.slice().sort((a, b) => a - b);  // Sort the first array
  const sortedArr2 = arr2.slice().sort((a, b) => a - b);  // Sort the second array

  // Compare each element
  return sortedArr1.every((value, index) => value === sortedArr2[index]);
}


  viewSheet(sheetdata: any) {
    if (this.dashboardId) {
      this.sheetsIdArray = this.dashboard.map(item => item['sheetId']);
      // if (this.sheetsIdArray && this.dashboardsheetsIdArray && !this.arraysHaveSameData(this.sheetsIdArray , this.dashboardsheetsIdArray)) {
      //   this.toasterService.info('Please Update the dashboard.', 'info', { positionClass: 'toast-top-center' })
      // } else {
        let sheetId = sheetdata.sheetId;
        // if (sheetdata.fileId) {
        //   this.fileId = sheetdata.fileId;
        //   this.qrySetId = sheetdata.qrySetId;
        //   const encodedServerId = btoa(this.fileId.toString());
        //   const encodedQuerySetId = btoa(this.qrySetId.toString());
        //   const encodedSheetId = btoa(sheetId.toString());
        //   const encodedDashboardId = btoa(this.dashboardId.toString());

        //   this.router.navigate(['/insights/sheetsdashboard/sheets/fileId/' + encodedServerId + '/' + encodedQuerySetId + '/' + encodedSheetId + '/' + encodedDashboardId])
        // } else {
          let databaseId = sheetdata.databaseId;
          this.qrySetId = sheetdata.qrySetId;
          const encodedServerId = btoa(databaseId.toString());
          const encodedQuerySetId = btoa(this.qrySetId.toString());
          const encodedSheetId = btoa(sheetId.toString());
          const encodedDashboardId = btoa(this.dashboardId.toString());

          this.router.navigate(['/analytify/sheetsdashboard/sheets/' + encodedServerId + '/' + encodedQuerySetId + '/' + encodedSheetId + '/' + encodedDashboardId])
        // }
      // }
    } else {
      this.toasterService.info('Please save the dashboard.', 'info', { positionClass: 'toast-top-center' })
    }

  }
  
  changedOptions() {
    if (this.options.api && this.options.api.optionsChanged && this.options.api.resize) {
      this.options.api.optionsChanged();
      this.options.api.resize(); 
    }
  }

  removeItem($event:any, item:any, tabSheet : boolean) {
    // $event.preventDefault();
    // $event.stopPropagation();
    if(tabSheet){
      this.dashboardTest.splice(this.dashboardTest.indexOf(item), 1);
      this.sheetTabs[this.selectedTabIndex].dashboard = this.dashboardTest;
    } else {
      if(item['type'] ==='image'){
        let removeIndex = this.dashboard.findIndex((sheet:any) => item.id == sheet.id);
        this.dashboard.splice(removeIndex, 1);
      }else{
      let removeIndex = this.dashboard.findIndex((sheet:any) => item.sheetId == sheet.sheetId);
      if(removeIndex >= 0){
        this.dashboard.splice(removeIndex, 1);
        let popqryIndex = this.qrySetId.findIndex((number:any) => number == item.qrySetId);
        // this.qrySetId.splice(popqryIndex, 1);
        if(this.dashboardId){
          this.deleteSheetFilter(item.sheetId);
          this.actionUpdateOnSheetRemove(item.sheetId);
        }
      // if(item.fileId){
      //   let popIndex = this.fileId.findIndex((number:any) => number == item.fileId);
      //   this.fileId.splice(popIndex, 1);
      // } else {
        let popIndex = this.databaseId.findIndex((number:any) => number == item.databaseId);
        this.databaseId.splice(popIndex, 1);
      // }
      }
    }
    this.canNavigateToAnotherPage = true;
    }
    this.setDashboardNewSheets(item.sheetId, false);
  }

  deleteSheetFilter(sheetId: any){
    let reqObj = {
      "dashboard_id": this.dashboardId,
      "sheet_ids": sheetId
    };
    this.loaderService.show();
    this.workbechService.deleteSheetFilter(reqObj).subscribe({
      next:(data)=>{
        console.log(data);
        this.loaderService.hide();
        this.toasterService.info('Filters on Removed Sheet will be deleted.','info',{ positionClass: 'toast-top-center'});
        this.getDashboardFilterredList(true);
    },
      error:(error)=>{
        console.log(error)
        Swal.fire({
          icon: 'error',
          title: 'oops!',
          text: error.error.message,
          width: '400px',
        })
      }
    });
  }
  removeNestedItem($event:any, item:any) {
    $event.preventDefault();
    $event.stopPropagation();
    this.dashboard.splice(this.nestedDashboard.indexOf(item), 1);
  }

  resetDashboard() {
    this.dashboard = [];
    this.loaderService.show();
    this.qrySetId = [];
    this.databaseId = [];
    // this.fileId = [];
    this.disableDashboardUpdate = true;
    const idsArray = this.DahboardListFilters.map((obj:any) => obj.dashboard_filter_id);
    const actionsIds = this.drillThroughActionList.map((Object : any)=> Object.drill_id);
    this.deleteDashboardAction(actionsIds);
    this.workbechService.deleteDashbaordFilter({"filter_id" : idsArray}).subscribe({
      next:(data)=>{
        console.log(data);
        this.DahboardListFilters =  [];
        this.loaderService.hide();
    },
      error:(error)=>{
        console.log(error)
        Swal.fire({
          icon: 'error',
          title: 'oops!',
          text: error.error.message,
          width: '400px',
        })
      }
    });
    this.dashboardNew.forEach(sheet => {
      sheet['selectedSheet'] = false;
    })
  }

  clearDashboard(){
    Swal.fire({
      title: 'Are you sure?',
      text: "Filters on dashboard will be deleted .You won't be able to revert this!",
      icon: 'warning',
      width: '300px',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Yes, Clear it!'
    }).then((result)=>{
      if(result.isConfirmed){
       this.resetDashboard();
       this.canNavigateToAnotherPage = true;
      }})
  }

  clearSheet(event : any , item :any){
    Swal.fire({
      title: 'Are you sure?',
      text: "You won't be able to revert this!",
      icon: 'warning',
      width: '300px',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Yes, Clear it!'
    }).then((result)=>{
      if(result.isConfirmed){
        this.dashboardNew.splice(this.dashboardNew.findIndex((sheet:any) => item.sheetId == sheet.sheetId), 1);
       this.removeItem(event, item, false);
       this.sheetIdsDataSet.splice(this.sheetIdsDataSet.findIndex((sheet:any) => item.sheetId == sheet), 1);
       this.unSelectSheetsFromSheetsPanel(item);
      }})
  }

  unSelectSheetsFromSheetsPanel(sheetData : any){
    this.panelscheckbox.forEach((panel : any)=>{
      if(panel.queryset_id == sheetData.qrySetId){
        panel.sheet_data.forEach((nestedPanel : any) => {
          if(nestedPanel.sheet_id == sheetData.sheetId){
            nestedPanel.is_selected = false;
            panel.is_selected = false;
          }
        })
      }
    })
  }
 
  // addItem() {
  //   this.dashboard.push({x: 0, y: 0, cols: 1, rows: 1,data: { title: 'New Card', content: 'New card content' }, 
  //   chartOptions: this.getChartOptions('bar')});
  // }

  initItem(item: GridsterItem, itemComponent: GridsterItemComponent) {
    this.itemToPush = itemComponent;
  }

  // pushItem() {
  //   const itemToPush = this.dashboard[0]; // Assuming you want to push the first item
  //   const itemComponent = this.getItemComponent(itemToPush); // Retrieve the GridsterItemComponent

  //   if (!itemComponent) return;
  //   const push = new GridsterPush(this.itemToPush); // init the service
  //   this.itemToPush.$item.rows += 4; // move/resize your item
  //   if (push.pushItems(push.fromNorth)) { // push items from a direction
  //     push.checkPushBack(); // check for items can restore to original position
  //     push.setPushedItems(); // save the items pushed
  //     this.itemToPush.setSize();
  //     this.itemToPush.checkItemChanges(this.itemToPush.$item, this.itemToPush.item);
  //     this.updateChartDimensions(itemToPush);
  //     this.updateCardData(itemToPush);
  //     this.updateChartData(itemToPush);
  //   } else {
  //     this.itemToPush.$item.rows -= 4;
  //     push.restoreItems(); // restore to initial state the pushed items
  //   }
  //   push.destroy(); // destroy push instance
  //   // similar for GridsterPushResize and GridsterSwap
  // }

  pushItem() {
    const itemToPush = this.dashboard[0];
    const gridsterItemComponent = this.getItemComponent(itemToPush);

    if (!gridsterItemComponent) return;

    const push = new GridsterPush(gridsterItemComponent);
    gridsterItemComponent.$item.rows += 4;
    if (push.pushItems(push.fromNorth)) {
      push.checkPushBack();
      push.setPushedItems();
      gridsterItemComponent.setSize();
      gridsterItemComponent.checkItemChanges(gridsterItemComponent.$item, gridsterItemComponent.item);
      //this.updateChartDimensions(itemToPush);
    } else {
      gridsterItemComponent.$item.rows -= 4;
      push.restoreItems();
    }
    push.destroy();
  }

  // updateChartDimensions(item: GridsterItem) {
  //   const gridsterItemComponent = this.getItemComponent(item);
  //   if (gridsterItemComponent && item['chartInstance']) {
  //     item['chartOptions'].chart = {
  //       ...item['chartOptions'].chart,
  //       width: gridsterItemComponent.el.clientWidth,
  //       height: gridsterItemComponent.el.clientHeight
  //     };
  //     item['chartInstance'].updateOptions(item['chartOptions']);
  //   }
  // }
  updateCardData(item: DashboardItem) {
    // Example of updating card content based on item properties
    if (item.data) {
      item.data.title = `Card ${item.x + 1}`;
      item.data.content = `Content of card ${item.x + 1}`;
    }
  }
  updateChartData(item: DashboardItem) {
    // Example of updating chart data based on item properties
    if (item.chartOptions) {
      item.chartOptions.series = [{
        name: 'Series 1',
        data: [Math.random() * 100, Math.random() * 100, Math.random() * 100, Math.random() * 100]
      }];
      if (item['chartInstance']) {
        item['chartInstance'].updateOptions(item.chartOptions);
      }
    }
  }
  // saveItemDimensions(item: GridsterItem) {
  //   // Assuming you have a backend service to save dimensions
  //   // this.workbenchService.saveItemDimensions(item)
  //   //   .subscribe({
  //   //     next: (response) => console.log('Item dimensions saved', response),
  //   //     error: (error) => console.error('Error saving item dimensions', error)
  //   //   });
  
  //   // For local storage:
  //   const savedItems = JSON.parse(localStorage.getItem('dashboardItems') || '[]');
  //   const index = savedItems.findIndex((i: any) => i.id === item['id']);
  //   if (index > -1) {
  //     this.dashboard[index] = item;
  //   } else {
  //     this.dashboard.push(item);
  //   }
  //   localStorage.setItem('dashboardItems', JSON.stringify(this.dashboard));
  // }  // onResizeStop(item: GridsterItem, itemComponent: GridsterItemComponent) {
  //   // Handle resize stop event here
  //   //this.updateChartDimensions(item);
  // }
  onResizeStop(item: DashboardItem, gridSterItem : GridsterItemComponentInterface ,event:any): void {
    const itemComponent  = event.itemComponent as GridsterItemComponent;
    if(gridSterItem){
    this.updateChartDimensions(item, itemComponent,gridSterItem);
    }else{
      console.error('item not available')
    }
  }
  updateSizeOnServer(item:any, itemComponent:any){

  }
  updateChartDimensions(item: DashboardItem, itemComponent: GridsterItemComponent , gridSterItem: GridsterItemComponentInterface): void {
    const chartElement = document.getElementById('test344') as any;
    // if (chartElement) {
    //   chartElement.chartObj.updateOptions({
    //     chart: {
    //       height: gridSterItem.el.clientHeight
    //     }
    //   });
    // }
    item.chartOptions!.chart = {
      // ...item.chartOptions!.chart,
      // width: itemComponent.width,
      height: gridSterItem.el.clientHeight,
      type:item.chartOptions?.chart?.type || 'bar'
    };
    if (item['chartOptions'] && itemComponent) {
      item.chartOptions!.chart = {
        ...item.chartOptions!.chart,
        width: itemComponent.width,
        height: gridSterItem.el.clientHeight,
        type:item.chartOptions?.chart?.type || 'bar'
      };
      item['chartInstance'].updateOptions(item.chartOptions, true);
    }
    // this.chartstest.forEach((chart, index) => {
    //   if (index === 0) {
    //     chart.updateOptions(item.chartOptions);
    //   } else if (index === 1) {
    //     chart.updateOptions(item.chartOptions);
    //   }
    // });
  }
  getItemComponent(item: DashboardItem): GridsterItemComponent | undefined {
    return this.GridsterItemComponent.find(cmp => cmp.item === item);
  }
  getChartOptions(chartType: ChartType,xval:any,yval:any ): ApexOptions {
    this.chartOptionsinitialize = true
    return {
      chart: {
        type: chartType,
        height:300
      },
      series: [{
        name: 'Series 1',
        data: yval
      }],
      xaxis: {
        categories: xval
      }
    };
  }
  ngAfterViewInit() {
    this.dashboard.forEach(item => {
      this.initializeChart(item);
    });
    if (this.gridster) {
      console.log('HEllo element initialized:', this.gridster);
    } else {
      console.error('Gridster element not found!');
    }
  }
  initializeChart(item: DashboardItem): void {
    const chartElement = document.querySelector("#chart"); // Adjust selector if necessary

    if (item['chartInstance']) {
        item['chartInstance'].destroy(); // Destroy the existing chart instance
        item['chartInstance'] = null;
    }
    if (item.chartOptions && item.chartOptions.chart && item.chartOptions.series) {
      const options: ApexOptions = {
        ...item.chartOptions,
        chart: {
          ...item.chartOptions.chart,
          type: item.chartOptions.chart.type || 'bar',
          height: 500
        },
        series: item.chartOptions.series,
        xaxis: {
          ...item.chartOptions.xaxis,
          categories: item.chartOptions.xaxis?.categories
        }
      };
      console.log('Chart options before updating/rendering:', options);

    //       item['chartInstance'] = new ApexCharts(document.querySelector("#chart"), options);
    // item['chartInstance'].render();


    // var chartOrigin = document.querySelector("#chart");
    // if(chartOrigin){
    //   var chart = new ApexCharts(document.querySelector("#chart"),options);
    //   // chartOrigin.updateOptions(options);
    //   chart.render();
    // }


    if (item['chartInstance']) {
      // Update the existing chart instance with new options
      item['chartInstance'].updateOptions(options, true);
  } else {
      // Create a new chart instance if it doesn't exist
      const chartOrigin = document.querySelector("#chart");
      if (chartOrigin) {
          item['chartInstance'] = new ApexCharts(chartOrigin, options);
          item['chartInstance'].render();
      }
  }

    // if(this.chartstest){
    //   this.chartstest['_results'][0].updateOptions(options);
    //   // this.chartstest['_results'][0].render();
    //   // this.chartstest./
    // }
    // item['chartInstance'] = new ApexCharts(document.querySelector("#chart-" + item['id']), item.chartOptions);
    // item['chartInstance'].render();
  }  
}

  onChartInit(event: any, item: DashboardItem) {
    item['chartInstance'] = event.chart;
  }

/////chartOptions
barChartOptions(xaxis:any,yaxis:any,savedOptions : any, isEchart : boolean){
  if (isEchart) {
    savedOptions.series[0].data = yaxis;
    savedOptions.xAxis.data = xaxis;
    return savedOptions;
  } else {
    savedOptions.series[0].data = yaxis;
    savedOptions.xaxis.categories = xaxis.map((category : any)  => category === null ? 'null' : category);
    return savedOptions;
  }
}
areaChartOptions(xaxis:any,yaxis:any,savedOptions : any, isEchart : boolean){
  if (isEchart) {
  savedOptions.series.data = yaxis;
  savedOptions.xAxis.data = xaxis;
  return savedOptions;
  } else {
    savedOptions.series.data = yaxis;
    savedOptions.labels = xaxis.map((category : any)  => category === null ? 'null' : category);
    return savedOptions;
  }
}
lineChartOptions(xaxis:any,yaxis:any,savedOptions:any, isEchart : boolean){
  if (isEchart) {
    savedOptions.series.data = yaxis;
    savedOptions.xAxis.data = xaxis;
    return savedOptions;
  } else {
    savedOptions.series.data = yaxis;
    savedOptions.xaxis.categories = xaxis.map((category : any)  => category === null ? 'null' : category);
    return savedOptions;
  }
}
pieChartOptions(xaxis:any,yaxis:any,savedOptions:any, isEchart : boolean){
  if (isEchart) {
    let combinedArray = yaxis.map((value : any, index :number) => ({
      value: value,
      name: xaxis[index]
    }));
    savedOptions.series.data = combinedArray;
    return savedOptions;
  } else {
  savedOptions.series = yaxis;
  savedOptions.labels = xaxis.map((category : any)  => category === null ? 'null' : category);
  return savedOptions;
  }
}
sidebySideBarChartOptions(xaxis:any,yaxis:any,savedOptions:any, isEchart : boolean){
  if (isEchart) {
    yaxis.forEach((bar: any) => {
      bar["type"] = "bar";
    });
    savedOptions.series.data = yaxis.data;
    savedOptions.xAxis.categories = xaxis;
    return savedOptions;
  } else {
  savedOptions.series = yaxis;
  savedOptions.xaxis.categories = xaxis.map((category : any)  => (category === null || category === '') ? 'null' : category);
  return savedOptions;
  }
}

eRadarChartOptions(xaxis:any,yaxis:any,savedOptions:any, isEchart : boolean){
  const dimensions: Dimension[] = xaxis;
      const categories = this.flattenDimensions(dimensions);
      let radarArray = categories.map((value: any, index: number) => ({
        name: categories[index]
      }));
  savedOptions.series.data = yaxis.data;
    savedOptions.radar.indicator = radarArray;
    return savedOptions;
}
stockedBarChartOptions(xaxis:any,yaxis:any,savedOptions:any, isEchart : boolean){
  if (isEchart) {
    yaxis.forEach((bar: any) => {
      bar["type"] = "bar";
      bar["stack"]="total";
    });
    savedOptions.series.data = yaxis.data;
    savedOptions.xAxis.data = xaxis;
    return savedOptions;
  } else {
  savedOptions.series = yaxis;
  savedOptions.xaxis.categories = xaxis.map((category : any)  => (category === null || category === '') ? 'null' : category);
  return savedOptions;
  }
}
barLineChartOptions(xaxis:any,yaxis:any,savedOptions:any){
  // savedOptions.series = [
  //   {
  //     name: yaxis[0]?.name,
  //     type: "column",
  //     data: yaxis[0]?.data
  //   },
  //   {
  //     name: yaxis[1]?.name,
  //     type: "line",
  //     data: yaxis[1]?.data,
  //   }
  // ];
  // savedOptions.labels = xaxis;
  return savedOptions;
}
hStockedBarChartOptions(xaxis:any,yaxis:any,savedOptions:any, isEchart : boolean){
  
  if (isEchart) {
    yaxis.forEach((bar: any) => {
      bar["type"] = "bar";
      bar["stack"]="total";
    });
    savedOptions.series.data = yaxis.data;
    savedOptions.yAxis.data = xaxis;
    return savedOptions;
  } else {
    savedOptions.series = yaxis;
    savedOptions.xaxis.categories = xaxis.map((category : any)  => (category === null || category === '') ? 'null' : category);
    return savedOptions;
  }
}

hGroupedChartOptions(xaxis:any,yaxis:any,savedOptions:any, isEchart : boolean){
  if (isEchart) {
    yaxis.forEach((bar: any) => {
      bar["type"] = "bar";
    });
    savedOptions.series.data = yaxis.data;
    savedOptions.yAxis.data = xaxis;
    return savedOptions;
  } else {
  savedOptions.series = yaxis;
  savedOptions.xaxis.categories = xaxis.map((category : any)  => (category === null || category === '') ? 'null' : category);
  return savedOptions;
  }
}
multiLineChartOptions(xaxis:any,yaxis:any,savedOptions:any){
  // savedOptions.series = yaxis;
  // savedOptions.xaxis.categories = xaxis;
  return savedOptions;
}
donutChartOptions(xaxis:any,yaxis:any,savedOptions:any, isEchart : boolean){
  if (isEchart) {
    let combinedArray = yaxis.map((value : any, index :number) => ({
      value: value,
      name: xaxis[index]
    }));
    savedOptions.series.data = combinedArray;
    return savedOptions;
  } else {
  savedOptions.series = yaxis;
  savedOptions.labels = xaxis.map((category : any)  => category === null ? 'null' : category);
  return savedOptions;
  }
}
heatMapChartOptions(savedOptions:any){
  return savedOptions;
}
addIcon(iconModal:any,item:any){
  this.modalService.open(iconModal, {
    centered: true,
    windowClass: 'animate__animated animate__zoomIn',
  });
  this.KpiIconItem = item;
}

//filters
openSuperScaled(modal: any) {
  this.modalService.open(modal, {
    centered: true,size:'lg',
    windowClass: 'animate__animated animate__zoomIn',
  });
this.editFilters = false;
this.filterName = '';
this.selectedDatabase='';
this.dropdownOptions = [];
this.querySetNames = [];
this.selectedQuerySetId = 0;
this.selectedOption = null;
this.sheetsFilterNames =[];
this.selectedColumnQuerySetId = null;
}
//Actions
openSuperScaleForActions(modal : any){
  this.modalService.open(modal, {
    centered: true,size:'lg',
    windowClass: 'animate__animated animate__zoomIn',
  });
}
databaseNames =[] as any;
selectedDatabase: string = '';
unfilteredQuerySetData =[] as any;
getQuerySetForFilter(){
  const obj ={
    dashboard_id:this.dashboardId
  }
  this.workbechService.getQuerySetInDashboardFilter(obj).subscribe({
    next:(data)=>{
      console.log(data);
       this.unfilteredQuerySetData=data;
      this.databaseNames = Object.keys(data);


    },
    error:(error)=>{
      console.log(error)
      this.toasterService.error(error.error.message,'error',{ positionClass: 'toast-center-center'})

    }
  })
}
selectedDbIdForFilter:any;
onDatabaseChange(){
  this.selectedQuerySetId = null;
  this.querySetNames = [];
  this.selectedOption = null;
  this.dropdownOptions = [];
  this.sheetsFilterNames =[];

  let selectedDatabaseObj;
    // Get the queryset data for the selected database
    if(this.selectedDatabase){
      selectedDatabaseObj = this.unfilteredQuerySetData[this.selectedDatabase];
    }
    if(this.drillThroughDatabaseName){
      selectedDatabaseObj = this.unfilteredQuerySetData[this.drillThroughDatabaseName];
    }
    
    // Update the filtered queryset data based on selected database
    if (selectedDatabaseObj) {
      console.log(selectedDatabaseObj)
      this.querySetNames = [...selectedDatabaseObj];
      this.selectedDbIdForFilter = this.querySetNames[0].hierarchy_id
    }

}


getColumnsForFilter(){
  this.selectedOption = null;
  this.sheetsFilterNames =[];
  if(this.selectedQuerySetId.length > 0){
  const obj ={
    dashboard_id:this.dashboardId,
    queryset_id : this.selectedQuerySetId,
    search : this.columnSearch
  }
  this.workbechService.getColumnsInDashboardFilter(obj).subscribe({
    next:(data)=>{
      console.log(data);
      this.columnFilterNames=data.response_data.tables;
      this.sheetsFilterNames= data.sheets?.map((name: any) => ({ label: name, selected: false }))
      this.buildDropdownOptions(this.columnFilterNames); 
    },
    error:(error)=>{
      console.log(error)
      Swal.fire({
        icon: 'error',
        title: 'oops!',
        text: error.error.message,
        width: '400px',
      })
    }
  })
  this.cdr.detectChanges();
}else{
  this.dropdownOptions = [];

}

}

ColumnsForFilterEdit(){
  this.selectedOption = null;
  this.sheetsFilterNamesFromEdit =[];

  if(this.selectedQuerySetId.length > 0){
  const obj ={
    dashboard_id:this.dashboardId,
    queryset_id : this.selectedQuerySetId,
    search : this.columnSearch
  }
  this.workbechService.getColumnsInDashboardFilter(obj).subscribe({
    next:(data)=>{
      console.log(data);
      this.columnFilterNames=data.response_data.tables;
      this.sheetsFilterNamesFromEdit= data.sheets?.map((obj: any) => ({ ...obj, selected: false }));
      this.buildDropdownOptions(this.columnFilterNames); 
      this.updateSelectedRowsEdit()
    },
    error:(error)=>{
      console.log(error)
      Swal.fire({
        icon: 'error',
        title: 'oops!',
        text: error.error.message,
        width: '400px',
      })
    }
  })
  this.cdr.detectChanges();
}else{
  this.dropdownOptions = [];

}
}
getColumnsForFilterEdit(selectedqryId:any,dashboardId:any){
this.dashboardId= dashboardId,
this.selectedQuerySetId = selectedqryId
this.selectedOption = null;
 this.getColumnsForFilter();
this.loadSelectedForEditing()

}
//get data for filters columns
buildDropdownOptions(tables:any) {
  this.dropdownOptions = [];

  Object.keys(tables).forEach((tableName: string) => {
    const columns = tables[tableName]; 

    const tableOptions = columns.map((column: any) => ({
      id: `${tableName}_${column.query_id}_${column.column_name}`, // Unique identifier for selection   
      group: tableName,  
      value: column.column_name, 
      column_dtype: column.column_dtype,
      selectedQueryId:column.query_id,
      tableNameForColumn:column.table_name,
      searchKey: `${tableName} ${column.column_name}` 
    }));
    this.dropdownOptions = [...this.dropdownOptions, ...tableOptions];
  });
  // this.selectedOption = this.dropdownOptions.find(option => option.selectedQueryId === this. selectedColumnQuerySetId) || null;
  if(this.editFilters){
  // const preSelectedOption = this.dropdownOptions.find(option => option.selectedQueryId === this. selectedColumnQuerySetId);
  const preSelectedOption = this.dropdownOptions.find(
    option => option.selectedQueryId === this.selectedColumnQuerySetId && option.value === this.selectClmn
  );
  this.selectedOption = preSelectedOption ? preSelectedOption.id : null; 
   console.log('Selected option:', preSelectedOption);
  }
  console.log(this.dropdownOptions);
 
}
onOptionSelected(selectedItem: any) {
  if (selectedItem) {
    const selectedColumn = selectedItem.value;  // Column name
    const selectedDataType = selectedItem.column_dtype;  // Column data type
    this.tableNameSelectedForFilter = selectedItem.tableNameForColumn;
    this.selectClmn=selectedColumn,
    this.selectdColmnDtype=selectedDataType,
    this.selectedColumnQuerySetId = selectedItem.selectedQueryId

    console.log('Selected Column:', selectedColumn);
    console.log('Selected Data Type:', selectedDataType);
  }
}
customSearch(term: string, item: any): boolean {
  return item.searchKey.toLowerCase().includes(term.toLowerCase());
}
loadSelectedForEditing() {
  const selectedForEdit = {
    column_name: this.selectClmnEdit,
    column_dtype: this.selectdColmnDtypeEdit,
    group: this.tableNameSelectedForFilter
  };

  // Find the option in the dropdown that matches the selected value
  const selectedOption = this.dropdownOptions.find(option =>
    option.value === selectedForEdit.column_name && option.group === selectedForEdit.group
  );

  if (selectedOption) {
    this.selectedOption = selectedOption;  // Set the selected option
    this.cdr.detectChanges();
  }
}
//get data for filters columns end

ResetDashboard(){
  this.dashboard =[];
}
updateSelectedRows(){
  this.selectedRows = this.sheetsFilterNames
  .filter((row: { selected: any; }) => row.selected)
  .map((row: { label: any; }) => row.label.id);
console.log('selected rows', this.selectedRows);
this.isAllSelected = this.sheetsFilterNames.every((row: { selected: any; }) => row.selected);
}
getColumnSelectionLabel(filterList: any): string {
  // Get the filtered columns using the provided method
  const filteredColumns = this.getFilteredColumns(filterList);
  const selectedColumns = filteredColumns.filter((col: any) => col.selected);
  
  if (selectedColumns.length === 0) {
    return 'Select Data';
  } else if (selectedColumns.length === 1) {
    return selectedColumns[0].label; // Display the label of the single selected column
  } else if (selectedColumns.length === filteredColumns.length) {
    return 'All Selected';
  } else {
    return 'Multiple Values'; // Display 'Multiple Values' if more than one column is selected
  }
}

toggleAllRows(event: Event) {
  const isChecked = (event.target as HTMLInputElement).checked;
  this.sheetsFilterNames.forEach((row: { selected: boolean; }) => row.selected = isChecked);
  this.updateSelectedRows();
}
isAnyRowSelected(): boolean {
  return this.sheetsFilterNames.some((row: { selected: any; }) => row.selected);
}
validateQuerySetSelection(){
  if (this.selectedQuerySetId === 0) {
    this.selectedQuerySetId = null; // Reset to null if no valid option is selected
  }
}
closeColumnsDropdown(colName:any,colDatatype:any, dropdown: NgbDropdown) {
  dropdown.close();
  this.selectClmn=colName,
  this.selectdColmnDtype=colDatatype

}

closeMainDropdown(dropdown: NgbDropdown,colData :any,id: any){
  localStorage.setItem(id, JSON.stringify(colData));
  dropdown.close();
}
clearSelectedData(dropdown: NgbDropdown,colData :any,id: any, filterData: any){
  filterData.isExclude = false;
  let index = this.excludeFilterIdArray.indexOf(id);
  if (index > -1) {
    this.excludeFilterIdArray.splice(index, 1);
  }
  colData.forEach((col: any) => {
    col.selected = false;
  });
  if (this.storeSelectedColData["test"][id]) {
    this.storeSelectedColData["test"][id] = [];
  }
  localStorage.setItem(id, JSON.stringify(colData));
}

getSelectedData(){

if(this.filterName === ''){
  this.toasterService.error('Please Add Filter Name','error',{ positionClass: 'toast-center-center'})

}else{
  const Obj ={
    dashboard_id:this.dashboardId,
    filter_name:this.filterName,
    column:this.selectClmn,
    sheets:this.selectedRows,
    datatype:this.selectdColmnDtype,
    queryset_id:this.selectedQuerySetId,
    table_name:this.tableNameSelectedForFilter,
    selected_query:this.selectedColumnQuerySetId,
    hierarchy_id:this.selectedDbIdForFilter
  }
  this.workbechService.selectedDatafromFilter(Obj).subscribe({
    next:(data)=>{
      console.log(data);
      this.dashboardFilterId = data.dashboard_filter_id
      this.getDashboardFilterredList();
      this.sheetsFilterNames = []
      this.selectClmn = '';
      this.columnFilterNames=[];
      this.dropdownOptions = [];
      this.filterName = '';
      this.isAllSelected = false;
      this.toasterService.success('Filter Added Successfully','success',{ positionClass: 'toast-top-center'})
      this.selectedOption = null;
      this.selectedQuerySetId = 0;
      this.clearAllFilters();
    },
    error:(error)=>{
      console.log(error)
      // Swal.fire({
      //   icon: 'error',
      //   title: 'oops!',
      //   text: error.error.message,
      //   width: '400px',
      // })
      this.toasterService.error(error.error.message,'error',{ positionClass: 'toast-center-center'})
    }
  })
}
}

getDashboardFilterredList(onSheetRemove? : boolean){
  const Obj ={
    dashboard_id:this.dashboardId
  }
  this.workbechService.getDashboardFilterredList(Obj).subscribe({
    next:(data)=>{
      console.log(data);
      this.DahboardListFilters = data
      if(onSheetRemove && data?.length <= 0){
        this.active = 1;
      }
    },
    error:(error)=>{
      console.log(error)
      Swal.fire({
        icon: 'error',
        title: 'oops!',
        text: error.error.message,
        width: '400px',
      })
    }
  })
}
getFilteredColumns(filterList: any) {
  const searchText = filterList?.searchText ? filterList.searchText.toLowerCase() : '';

  if (!searchText) {
    return filterList?.colData || []; 
  }

  const data = (filterList?.colData || []).filter((col: any) => col?.label?.toLowerCase().includes(searchText));
  
  console.log('Filtered Data:', data); 

  return data;

}
getColDataFromFilterId(id:string,colData:any,isFilter : boolean){
  if(localStorage.getItem('filterid')){
    colData['colData']= JSON.parse(localStorage.getItem('filterid')!);
  } else {
  const Obj ={
    id:id,
    search:colData.search
  }
  this.workbechService.getColDataFromFilterId(Obj).subscribe({
    next:(data)=>{
      console.log(data);
      const lookup = new Map<number, boolean>();
      if (colData['colData']) {
        colData['colData'].forEach((item: any) => {
          lookup.set(item.label, item.selected);
        });
        const array3 = [...colData['colData']];
        data.col_data.forEach((label: any) => {
          if (!lookup.has(label)) {
            array3.push({ label, selected: false });
          }
        });
      colData['colData']= array3;
      } else {
        colData['colData']= data.col_data?.map((name: any) => ({ label: name, selected: false }))
      }
      localStorage.setItem(id, JSON.stringify(colData['colData']));
      console.log('coldata',this.colData)
    },
    error:(error)=>{
      console.log(error)
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
updateSelectedColmns(filterList:any,col: any){
  if(!this.storeSelectedColData["test"]){
    this.storeSelectedColData["test"]={};
  } 
  if(!this.storeSelectedColData["test"][filterList.dashboard_filter_id]){
    this.storeSelectedColData["test"][filterList.dashboard_filter_id]=[];
  }
  let array = this.storeSelectedColData["test"][filterList.dashboard_filter_id];
  if(col.selected){
    array.push(col.label);
  } else {
    let indexVar = array.indexOf(col.label);
    array.splice(indexVar,1);
  }

this.storeSelectedColData["test"][filterList.dashboard_filter_id] =array ;
console.log('selected Data', this.storeSelectedColData);
this.isAllSelected = filterList.colData.every((row: { selected: any; }) => row.selected);
}
  toggleAllColumns(event: Event, filterList: any) {
    let array: any[] = [];
    const isChecked = (event.target as HTMLInputElement).checked;

    filterList.colData.forEach((row: { selected: boolean; }) => row.selected = isChecked);
    // this.updateSelectedColmns(filterList,filterList.colData);
    if (isChecked) {
      if (!this.storeSelectedColData["test"]) {
        this.storeSelectedColData["test"] = {};
      }
      if (!this.storeSelectedColData["test"][filterList.dashboard_filter_id]) {
        this.storeSelectedColData["test"][filterList.dashboard_filter_id] = [];
      }
      array = [];
      filterList.colData.forEach((col: any) => {
        if (col.selected) {
          array.push(col.label);
        }
      });
    } else {
      array = [];
    }

    this.storeSelectedColData["test"][filterList.dashboard_filter_id] = array;
    console.log('selected Data', this.storeSelectedColData);
  }
extractKeysAndData(): void {
  if (this.storeSelectedColData && this.storeSelectedColData.test) {
    this.extractKeysAndData1(this.storeSelectedColData.test);
    console.log('Keys Array:', this.keysArray);
    console.log('Data Array:', this.dataArray);
  } else {
    console.error('storeSelectedColData.test is not defined:', this.storeSelectedColData.test);
  }
}
extractKeysAndData1(inputData: any): void {
  const keys = Object.keys(inputData);
  console.log('Extracted Keys:', keys);  // Debug: Log extracted keys

  this.keysArray = keys;
  this.dataArray = keys.map(key => inputData[key]);
  console.log('Extracted Data Array:', this.dataArray);  // Debug: Log extracted data array
}
getFilteredData(){
  this.extractKeysAndData();
  const Obj ={
    id:this.keysArray,
    exclude_ids:this.excludeFilterIdArray,
    input_list:this.dataArray
  }
  if(this.keysArray && this.keysArray.length > 0){
  this.workbechService.getFilteredData(Obj).subscribe({
    next:(data)=>{
      console.log(data);
      // this.tablePreviewColumn = data.columns;
      // this.tablePreviewRow = data.rows;
      // console.log(this.tablePreviewColumn);
      // console.log(this.tablePreviewRow);
      // localStorage.removeItem('filterid')
      this.sheetFilters = data;
      data.forEach((item: any) => {
        this.filteredRowData = [];
        this.filteredColumnData = [];
      this.tablePreviewColumn.push(item.columns);
      this.tablePreviewRow.push(item.rows);
      item.columns.forEach((res:any) => {      
        let obj1={
          name:res.column,
          values: res.result
        }
        this.filteredColumnData.push(obj1);
        console.log('filtercolumn',this.filteredColumnData)
      });
      item.rows.forEach((res:any) => {
        let obj={
          name: res.column,
          data: res.result
        }
        this.filteredRowData.push(obj);
        console.log('filterowData',this.filteredRowData)
      });
      if(item.chart_id === 1){
        this.pageChangeTableDisplay(item,1,false,0)
        // this.tablePageNo =1;
        this.tablePage=1
      }else{
      this.setDashboardSheetData(item, true , true, false, false, '', false,0);
      }
    });
      },
    error:(error)=>{
      console.log(error)
      Swal.fire({
        icon: 'error',
        title: 'oops!',
        text: error.error.message,
        width: '400px',
      })
    }
  });
}
}
clearAllFilters(): void {
  this.DahboardListFilters.forEach((values:any) => {
    values.searchText =''
  });
  if (this.DahboardListFilters && Array.isArray(this.DahboardListFilters)) {
      this.DahboardListFilters.forEach(filterList => {
        filterList.isExclude = false;
          if (filterList && Array.isArray(filterList.colData)) {
              filterList.colData.forEach((col: { selected: boolean }) => {
                  col.selected = false;
              });
          }
          if (this.storeSelectedColData["test"][filterList.dashboard_filter_id]) {
            this.storeSelectedColData["test"][filterList.dashboard_filter_id] = [];
          }
      });
      this.excludeFilterIdArray = [];
      localStorage.removeItem('storeSelectedColData'); 
      console.log('All filters cleared');
      if(this.isPublicUrl){
        this.getFilteredDataPublic()
      }else{
        this.getFilteredData();
      }
  } else {
      console.warn('DahboardListFilters is not defined or not an array');
  }
}


setDashboardSheetData(item:any , isFilter : boolean , onApplyFilterClick : boolean, isDrillDown : boolean, isDrillThrough : boolean, drillThroughSheetId: any, isLiveReloadData : boolean,liveSheetIndex:any){
  this.dashboard.forEach((item1:any) => {
    if((((item1.sheetId == item.sheet_id || item1.sheetId == item.sheetId) && (isFilter || isDrillDown)) || (isDrillThrough && item1.sheetId == drillThroughSheetId))){
      if(item.chart_id == '1'){//table
        if(!item1.originalData && !isLiveReloadData){
          item1['originalData'] = _.cloneDeep({tableData: item1.tableData});
        }
        this.tablePreviewColumn = item.columns;
        this.tablePreviewRow = item.rows;
        let rowCount:any;
       if(this.tablePreviewColumn[0]?.result?.length){
         rowCount = this.tablePreviewColumn[0]?.result?.length;
       }else{
         rowCount = this.tablePreviewRow[0]?.result?.length;
       }
        //const rowCount = this.tablePreviewRow[0]?.result_data?.length;
        // Extract column names
        item1.tableData.headers = this.tablePreviewColumn.map((col:any) => col.column).concat(this.tablePreviewRow.map((row:any) => row.column));
        // Create table data
        item1.tableData.rows = [];
        for (let i = 0; i < rowCount; i++) {
          const row: TableRow = {};
          this.tablePreviewColumn.forEach((col:any) => {
            row[col.column] = col.result[i];
          });
          this.tablePreviewRow.forEach((rowData:any) => {
            row[rowData.column] = rowData.result[i];
          });
          item1.tableData.rows.push(row);
      }
      if(item1?.tableData?.tableTotalItems){
        item1.tableData.tableTotalItems = this.tableTotalItems;
      }
      if(item1?.tableData?.tableItemsPerPage){
        item1.tableData.tableItemsPerPage = this.tableItemsPerPage;
      }
    }
    if(item.chart_id == '9'){
      if(!item1.originalData && !isLiveReloadData){
        item1['originalData'] = _.cloneDeep({pivotData: item1.pivotData});
      }
      let transformedData :any =[];
      let headers: string[] = [];

     let columnKeys = item?.columns?.map((col: any) => col.column); 
     let rowKeys = item?.rows?.map((row: any) => row.column);
    let valueKeys = item?.pivot?.map((col:any) =>col.column)

    item?.columns?.forEach((colObj: any) => {
      headers.push(colObj.column);
    });

    item?.rows?.forEach((rowObj: any) => {
      headers.push(rowObj.column);
    });
    item?.pivot?.forEach((colObj: any) => {
      headers.push(colObj.column);
    });

    transformedData.push(headers); 
    let numRows = 0;
    if (item?.columns?.length > 0) {
        numRows = item.columns[0]?.result?.length || 0;
    } else if (item?.rows?.length > 0) {
        numRows = item.rows[0]?.result?.length || 0;
    } else if (item?.pivot?.length > 0) {
        numRows = item.pivot[0]?.result?.length || 0;
    }
    for (let i = 0; i < numRows; i++) {
      let rowArray: any[] = []; 
      item?.columns?.forEach((colObj: any) => {
        rowArray.push(colObj.result[i]);
      });
      item?.rows?.forEach((rowObj: any) => {
        rowArray.push(rowObj.result[i]);
      });
      item?.pivot?.forEach((rowObj: any) => {
        rowArray.push(rowObj.result[i]);
      });

      transformedData.push(rowArray);
    }
    setTimeout(() => {
      if (this.pivotContainer && this.pivotContainer.nativeElement) {
          ($(this.pivotContainer.nativeElement) as any).pivot(transformedData, {
            rows: columnKeys,  
            cols: valueKeys, 
            // vals: this.valueKeys, 
            aggregator:$.pivotUtilities.aggregators["Sum"](rowKeys),
            rendererName: "Table"
          });
      }        
    }, 1000);
    }


      if((item.chart_id == '6' || item.chartId == '6' && (isFilter || isDrillDown)) || (item1.chartId == '6' && isDrillThrough)){//bar
        if(item1.isEChart){ 
          if(!item1.originalData && !isLiveReloadData){
            item1['originalData'] = _.cloneDeep({chartOptions: item1.echartOptions});
          }
          if(onApplyFilterClick && ((item1.drillDownHierarchy && item1.drillDownHierarchy.length > 0) || item1.drillDownIndex)){
            item1.drillDownIndex = 0;
            item1.drillDownObject = [];
          }
          item1.echartOptions.xAxis.data = this.filteredColumnData[0]?.values;
        item1.echartOptions.series[0].data = this.filteredRowData[0]?.data;
        item1.echartOptions = {
          ...item1.echartOptions,

        };
        } else {
        if(!item1.originalData && !isLiveReloadData){
          item1['originalData'] = _.cloneDeep({chartOptions: item1.chartOptions});
        }
        if(onApplyFilterClick && ((item1.drillDownHierarchy && item1.drillDownHierarchy.length > 0) || item1.drillDownIndex)){
          item1.drillDownIndex = 0;
          item1.drillDownObject = [];
        }
      item1.chartOptions.xaxis.categories = this.filteredColumnData[0]?.values.map((category : any)  => category === null ? 'null' : category);
      item1.chartOptions.series = this.filteredRowData;
      }
    }
      if((item.chart_id == '25' || item.chartId == '25' && (isFilter || isDrillDown)) || (item1.chartId == '25' && isDrillThrough)){//KPI
        if(!item1.originalData && !isLiveReloadData){
          item1['originalData'] = _.cloneDeep(item1['kpiData']);
        }
        let obj = {column : item.rows[0].column , result_data : item.rows[0].result}
        item1['kpiData'].rows = [obj];
        item1.kpiData.kpiNumber = this.formatKPINumber(item.rows[0].result[0], item1.kpiData.kpiDecimalUnit , item1.kpiData.kpiDecimalPlaces, item1.kpiData.kpiPrefix, item1.kpiData.kpiSuffix);
      }
      if((item.chart_id == '24' || item.chartId == '24' && (isFilter || isDrillDown)) || (item1.chartId == '24' && isDrillThrough)){//pie
        if(item1.isEChart){ 
          if(!item1.originalData && !isLiveReloadData){
            item1['originalData'] = _.cloneDeep({chartOptions: item1.echartOptions});
          }
          if(onApplyFilterClick && ((item1.drillDownHierarchy && item1.drillDownHierarchy.length > 0) || item1.drillDownIndex)){
            item1.drillDownIndex = 0;
            item1.drillDownObject = [];
          }
          let combinedArray = this.filteredRowData[0].data.map((value : any, index :number) => ({
            value: value,
            name: this.filteredColumnData[0].values[index]
          }));
        item1.echartOptions.series[0].data = combinedArray;
        item1.echartOptions = {
          ...item1.echartOptions,
        };
        } else {
          if(!item1.originalData && !isLiveReloadData){
            item1['originalData'] = _.cloneDeep({chartOptions: item1.chartOptions});
          }
        if(onApplyFilterClick && ((item1.drillDownHierarchy && item1.drillDownHierarchy.length > 0) || item1.drillDownIndex)){
          item1.drillDownIndex = 0;
          item1.drillDownObject = [];
        }
        item1.chartOptions.labels = this.filteredColumnData[0].values.map((category : any)  => category === null ? 'null' : category);
      item1.chartOptions.series = this.filteredRowData[0].data;
      }
    }
      if((item.chart_id == '10'|| item.chartId == '10' && (isFilter || isDrillDown)) || (item1.chartId == '10' && isDrillThrough)){//donut
        if(item1.isEChart){ 
          if(!item1.originalData && !isLiveReloadData){
            item1['originalData'] = _.cloneDeep({chartOptions: item1.echartOptions});
          }
          if(onApplyFilterClick && ((item1.drillDownHierarchy && item1.drillDownHierarchy.length > 0) || item1.drillDownIndex)){
            item1.drillDownIndex = 0;
            item1.drillDownObject = [];
          }
          let combinedArray = this.filteredRowData[0].data.map((value : any, index :number) => ({
            value: value,
            name: this.filteredColumnData[0].values[index]
          }));
        item1.echartOptions.series[0].data = combinedArray;
        item1.echartOptions = {
          ...item1.echartOptions
        };
        } else {
          if(!item1.originalData && !isLiveReloadData){
            item1['originalData'] = _.cloneDeep({chartOptions: item1.chartOptions});
          }
        if(onApplyFilterClick && ((item1.drillDownHierarchy && item1.drillDownHierarchy.length > 0) || item1.drillDownIndex)){
          item1.drillDownIndex = 0;
          item1.drillDownObject = [];
        }
        item1.chartOptions.labels = this.filteredColumnData[0].values.map((category : any)  => category === null ? 'null' : category);
      item1.chartOptions.series = this.filteredRowData[0].data;
      }
    }
      if((item.chart_id == '13'|| item.chartId == '13' && (isFilter || isDrillDown)) || (item1.chartId == '13' && isDrillThrough)){//line
        if(item1.isEChart){ 
          if(!item1.originalData && !isLiveReloadData){
            item1['originalData'] = _.cloneDeep({chartOptions: item1.echartOptions});
          }
          if(onApplyFilterClick && ((item1.drillDownHierarchy && item1.drillDownHierarchy.length > 0) || item1.drillDownIndex)){
            item1.drillDownIndex = 0;
            item1.drillDownObject = [];
          }
          item1.echartOptions.xAxis.data = this.filteredColumnData[0].values;
        item1.echartOptions.series[0].data = this.filteredRowData[0].data;
        item1.echartOptions = {
          ...item1.echartOptions,

        };
        } else {
          if(!item1.originalData && !isLiveReloadData){
            item1['originalData'] = _.cloneDeep({chartOptions: item1.chartOptions});
          }
        item1.chartOptions.xaxis.categories = this.filteredColumnData[0].values;
      item1.chartOptions.series = this.filteredRowData;
        }
      }
      if((item.chart_id == '17'|| item.chartId == '17' && (isFilter || isDrillDown)) || (item1.chartId == '17' && isDrillThrough)){//area
        if(item1.isEChart){ 
          if(!item1.originalData && !isLiveReloadData){
            item1['originalData'] = _.cloneDeep({chartOptions: item1.echartOptions});
          }
          if(onApplyFilterClick && ((item1.drillDownHierarchy && item1.drillDownHierarchy.length > 0) || item1.drillDownIndex)){
            item1.drillDownIndex = 0;
            item1.drillDownObject = [];
          }
          item1.echartOptions.xAxis.data = this.filteredColumnData[0].values;
        item1.echartOptions.series[0].data = this.filteredRowData[0].data;
        item1.echartOptions = {
          ...item1.echartOptions,

        };
        } else {
          if(!item1.originalData && !isLiveReloadData){
            item1['originalData'] = _.cloneDeep({chartOptions: item1.chartOptions});
          }
        item1.chartOptions.labels = this.filteredColumnData[0].values;
      item1.chartOptions.series = this.filteredRowData;
      }
    }
      if((item.chart_id == '7' && (isFilter || isDrillDown)) || (item1.chartId == '7' && isDrillThrough)){//sidebyside
        const dimensions: Dimension[] = this.filteredColumnData
        const categories = this.flattenDimensions(dimensions)
        if(item1.isEChart){ 
          if(!item1.originalData && !isLiveReloadData){
            item1['originalData'] = _.cloneDeep({chartOptions: item1.echartOptions});
          }
          this.filteredRowData.forEach((bar : any)=>{
            bar["type"]="bar";
                  });
        item1.echartOptions.xAxis.data = _.cloneDeep(categories);
        item1.echartOptions.series = _.cloneDeep(this.filteredRowData);
        item1.echartOptions = {
          ...item1.echartOptions,
        };
        } else {
       
          if(!item1.originalData && !isLiveReloadData){
            item1['originalData'] = _.cloneDeep({chartOptions: item1.chartOptions});
          }
        item1.chartOptions.xaxis.categories = categories;
        item1.chartOptions.series = this.filteredRowData;
      }
      }
      if((item.chart_id == '2' && (isFilter || isDrillDown)) || (item1.chartId == '2' && isDrillThrough)){//hstacked
        const dimensions: Dimension[] = this.filteredColumnData
        const categories = this.flattenDimensions(dimensions)
        if(item1.isEChart){ 
          if(!item1.originalData && !isLiveReloadData){
            item1['originalData'] = _.cloneDeep({chartOptions: item1.echartOptions});
          }
          this.filteredRowData.forEach((bar : any)=>{
            bar["type"]="bar";
            bar["stack"]="total";
                  });
        item1.echartOptions.yAxis.data = _.cloneDeep(categories);
        item1.echartOptions.series = _.cloneDeep(this.filteredRowData);
        item1.echartOptions = {
          ...item1.echartOptions,
        };
        } else {
          if(!item1.originalData && !isLiveReloadData){
            item1['originalData'] = _.cloneDeep({chartOptions: item1.chartOptions});
          }
        item1.chartOptions.xaxis.categories = categories;
        item1.chartOptions.series = this.filteredRowData;
      }
      }
      if((item.chart_id == '5' && (isFilter || isDrillDown)) || (item1.chartId == '5' && isDrillThrough)){//stacked
        const dimensions: Dimension[] = this.filteredColumnData
        const categories = this.flattenDimensions(dimensions)
        if(item1.isEChart){ 
          if(!item1.originalData && !isLiveReloadData){
            item1['originalData'] = _.cloneDeep({chartOptions: item1.echartOptions});
          }
          this.filteredRowData.forEach((bar : any)=>{
            bar["type"]="bar";
            bar["stack"]="total";
                  });
        item1.echartOptions.xAxis.data = _.cloneDeep(categories);
        item1.echartOptions.series = _.cloneDeep(this.filteredRowData);
        item1.echartOptions = {
          ...item1.echartOptions,
        };
        } else {
          if(!item1.originalData && !isLiveReloadData){
            item1['originalData'] = _.cloneDeep({chartOptions: item1.chartOptions});
          }
        item1.chartOptions.xaxis.categories = categories;
        item1.chartOptions.series = this.filteredRowData;
      }
      }
      if((item.chart_id == '4' && (isFilter || isDrillDown)) || (item1.chartId == '4' && isDrillThrough)){//barline
        const dimensions: Dimension[] = this.filteredColumnData
        const categories = this.flattenDimensions(dimensions)
        if(item1.isEChart){ 
          if(!item1.originalData && !isLiveReloadData){
            item1['originalData'] = _.cloneDeep({chartOptions: item1.echartOptions});
          }
          item1.echartOptions.xAxis[0].data = categories;
        item1.echartOptions.series[0].data = this.filteredRowData[0].data;
        item1.echartOptions.series[1].data = this.filteredRowData[1].data;
        item1.echartOptions = {
          ...item1.echartOptions,
        };
        } else {
          if(!item1.originalData && !isLiveReloadData){
            item1['originalData'] = _.cloneDeep({chartOptions: item1.chartOptions});
          }
        item1.chartOptions.labels = categories;
        item1.chartOptions.series[0].data = this.filteredRowData[0].data;
        item1.chartOptions.series[1].data = this.filteredRowData[1].data;
        // item1.chartOptions.series = this.filteredRowData;
      }
      }
      if((item.chart_id == '3' && (isFilter || isDrillDown)) || (item1.chartId == '3' && isDrillThrough)){//hgrouped
        const dimensions: Dimension[] = this.filteredColumnData
        const categories = this.flattenDimensions(dimensions)
        if(item1.isEChart){ 
          if(!item1.originalData && !isLiveReloadData){
            item1['originalData'] = _.cloneDeep({chartOptions: item1.echartOptions});
          }
            this.filteredRowData.forEach((bar : any)=>{
              bar["type"]="bar";
                    });
          item1.echartOptions.yAxis.data = _.cloneDeep(categories);
          item1.echartOptions.series = _.cloneDeep(this.filteredRowData);
          item1.echartOptions = {
            ...item1.echartOptions,
          };
        } else {
          if(!item1.originalData && !isLiveReloadData){
            item1['originalData'] = _.cloneDeep({chartOptions: item1.chartOptions});
          }
        item1.chartOptions.xaxis.categories = categories;
        item1.chartOptions.series = this.filteredRowData;
      }
      }
      if((item.chart_id == '8' && (isFilter || isDrillDown)) || (item1.chartId == '8' && isDrillThrough)){//multiline
        const dimensions: Dimension[] = this.filteredColumnData
        const categories = this.flattenDimensions(dimensions)
        if(item1.isEChart){ 
          if(!item1.originalData && !isLiveReloadData){
            item1['originalData'] = _.cloneDeep({chartOptions: item1.echartOptions});
          }
          this.filteredRowData.forEach((bar : any)=>{
            bar["type"]="line";
            bar["stack"]="total";
                  });
        item1.echartOptions.xAxis.data = _.cloneDeep(categories);
        item1.echartOptions.series = _.cloneDeep(this.filteredRowData);
        item1.echartOptions = {
          ...item1.echartOptions,
        };
        } else {
          if(!item1.originalData && !isLiveReloadData){
            item1['originalData'] = _.cloneDeep({chartOptions: item1.chartOptions});
          }
        item1.chartOptions.xaxis.categories = categories;
        item1.chartOptions.series = this.filteredRowData;
        item1.chartOptions = {
          ...item1.chartOptions,
        };
      }
      }
      if((item.chart_id == '28' && (isFilter || isDrillDown)) || (item1.chartId == '28' && isDrillThrough)){//guage
        if(!item1.originalData && !isLiveReloadData){
          item1['originalData'] = _.cloneDeep({chartOptions: item1.echartOptions});
        }
        let seriesval =[Math.round(( this.filteredRowData[0]?.data[0]/ (item1.chartOptions.plotOptions.radialBar.max-item1.chartOptions.plotOptions.radialBar.min))*100)]
        item1.chartOptions.series = seriesval;
      }
      if((item.chart_id == '12' && (isFilter || isDrillDown)) || (item1.chartId == '12' && isDrillThrough)){//radar
        const dimensions: Dimension[] = this.filteredColumnData;
        const categories = this.flattenDimensions(dimensions);
        let radarArray = categories.map((value: any, index: number) => ({
          name: categories[index]
        }));
        let legendArray = this.filteredRowData.map((data: any) => ({
          name: data.name
        }));
        const transformedArray = this.filteredRowData.map((obj: any) => ({
          name: obj.name,   
          value: obj.data   
        }));
        if(item1.isEChart){ 
          if(!item1.originalData && !isLiveReloadData){
            item1['originalData'] = _.cloneDeep({chartOptions: item1.echartOptions});
          }
        item1.echartOptions.radar.indicator = radarArray;
        item1.echartOptions.legend = legendArray;
        item1.echartOptions.series[0].data = transformedArray;
        item1.echartOptions = {
          ...item1.echartOptions,
        };
        } else {
      }
      }
      if((item.chart_id == '29' && (isFilter || isDrillDown)) || (item1.chartId == '29' && isDrillThrough)){//world MAP
        if(!item1.originalData && !isLiveReloadData){
          item1['originalData'] = _.cloneDeep({chartOptions: item1.echartOptions});
        }
        let minData = 0;
       const maxData = Math.max(...this.filteredRowData[0].data);
       let result:any[] = [];

       // Loop through the countries (assuming both data sets align by index)
       this.filteredColumnData[0].values.forEach((country: string, index: number) => {
         // Create an object for each country
         const countryData: any = { name: country , value : this.filteredRowData[0].data[index]};
     
         // Add each measure to the country object
         this.filteredRowData.forEach((measure:any) => {
           const measureName = measure.name; // e.g., sum(Sales), sum(Quantity)
           const measureValue = measure.data[index]; // Value for that measure
           countryData[measureName] = measureValue;
         });
     
         result.push(countryData);
       });
    if(this.filteredRowData && this.filteredRowData[0]?.length > 1){
    minData = Math.min(...this.filteredRowData[0].data);
    }
    item1.echartOptions.tooltip = {
      formatter: (params: any) => {
        const { name, data } = params;
        if (data) {
          const keys = Object.keys(data);
    const values = Object.values(data);
    let formattedString = '';
    keys.forEach((key, index) => {
      if(key)
      formattedString += `${key}: ${values[index]}<br/>`;
    });

    return formattedString;
         
        } else {
          return `${name}: No Data`;
        }
      },
          trigger: 'item',
          showDelay: 0,
          transitionDuration: 0.2
        };
        item1.echartOptions.visualMap.min = minData;
        item1.echartOptions.visualMap.max = maxData;
        item1.echartOptions.series[0].data = result;
    item1.echartOptions = {
      ...item1.echartOptions,
    };
  }

      if((item.chart_id == '27' && (isFilter || isDrillDown)) || (item1.chartId == '27' && isDrillThrough)){//funnel
        if(item1.isEChart){
          if(!item1.originalData && !isLiveReloadData){
            item1['originalData'] = _.cloneDeep({chartOptions: item1.echartOptions});
          }
            const combinedArray: any[] = [];
            this.filteredColumnData.forEach((item: any) => {
              this.filteredRowData.forEach((categoryObj: any) => {
                item.values.forEach((value: any, index: number) => {
                  combinedArray.push({
                    name: value,
                    value: categoryObj.data[index]
                  });
                });
              });
            });
            item1.echartOptions.series[0].data = combinedArray;
            item1.echartOptions = {
              ...item1.echartOptions,
            };
        } else {
        const dimensions: Dimension[] = this.filteredColumnData
        const categories = this.flattenDimensions(dimensions)
        if(!item1.originalData && !isLiveReloadData){
          item1['originalData'] = {categories: item1.chartOptions.xaxis.categories , data:item1.chartOptions.series };
        }
        if(isDrillThrough){
          item1.chartOptions = {
            ...item1.chartOptions,
            xaxis: {
              ...item1.chartOptions.xaxis,
              categories: categories,
            },
            series: this.filteredRowData,
          };
        }
        else{
          item1.chartOptions.xaxis.categories = categories;
          item1.chartOptions.series = this.filteredRowData;
        }
      }
      }
      if(item.chart_id == '26'){//heatmap
        const dimensions: Dimension[] = this.filteredColumnData
        const categories = this.flattenDimensions(dimensions)
        if(item1.isEChart){
          if(!item1.originalData && !isLiveReloadData){
            item1['originalData'] = _.cloneDeep({chartOptions: item1.echartOptions});
          }
          item1.echartOptions.xAxis.data = _.cloneDeep(categories);
            const heatmapData: any[][] = [];
            this.filteredRowData.forEach((row: { data: (null | undefined)[]; }, rowIndex: any) => {
                row.data.forEach((value: null | undefined, colIndex: any) => { // Assuming each row has a `data` array
                    if (value !== null && value !== undefined) { // Ensure value is valid
                        heatmapData.push([colIndex, rowIndex, value]); // [xIndex, yIndex, value]
                    }
                });
            });          
          item1.echartOptions.series.data = heatmapData;
          item1.echartOptions = {
            ...item1.echartOptions,     
          };
         }
        else{ if(!item1.originalData && !isLiveReloadData){
          item1['originalData'] = {categories: item1.chartOptions.xaxis.categories , data:item1.chartOptions.series };
        }
        item1.chartOptions.xaxis.categories = categories;
        item1.chartOptions.series = this.filteredRowData;
      }
    }
      if((item.chart_id == '11' && (isFilter || isDrillDown)) || (item1.chartId == '11' && isDrillThrough)){//calendar
        if(item1.isEChart){
          if(!item1.originalData && !isLiveReloadData){
            item1['originalData'] = _.cloneDeep({chartOptions: item1.echartOptions});
          }
          let calendarData : any[]= [];
          let years: Set<any> = new Set();
          console.log(this.filteredColumnData);
          console.log(this.filteredRowData);
          this.filteredColumnData.forEach((data: any) => {
            data?.values.forEach((column:any, index: any)=>{
              let arr = [new Date(column).toISOString().split('T')[0], this.filteredRowData[0]?.data[index]];
              calendarData.push(arr);

              const year = new Date(column).getFullYear();
              years.add(year);
            })
        });
        let yearArray = Array.from(years).sort((a: any, b: any) => a - b);
        let series = yearArray.map((year: any) => {
          const yearData = calendarData.filter(d => new Date(d[0]).getFullYear() === year);
          return {
              type: 'heatmap',
              coordinateSystem: 'calendar',
              calendarIndex: yearArray.indexOf(year),
              data: yearData
          };
        });

        const calendarHeight = 100;  // Adjust height for better visibility
        const yearGap = 20;  // Reduced gap between years
        const totalHeight = (calendarHeight + yearGap) * yearArray.length;
    
        // Create multiple calendar instances, one for each year
        let calendars = yearArray.map((year: any, idx: any) => ({
            top: idx === 0 ? 25 : (calendarHeight + yearGap) * idx,
            range: year.toString(),
            cellSize: ['auto', 10],
            splitLine: {
                show: true,
                lineStyle: {
                    color: '#000',
                    width: 1
                }
            },
            yearLabel: {
                margin: 20
            }
        }));

        const minValue = this.filteredRowData[0].data.reduce((a: any, b: any) => (a < b ? a : b), Infinity);
        const maxValue = this.filteredRowData[0].data.reduce((a: any, b: any) => (a > b ? a : b), -Infinity);
        console.log(minValue +' '+maxValue);

          item1.echartOptions.series = series;
          item1.echartOptions.calendar = calendars;
          item1.echartOptions.visualMap.min = minValue;
          item1.echartOptions.visualMap.max = maxValue;
          item1.echartOptions = { ...item1.echartOptions };
          console.log(calendarData);
          console.log(item1.echartOptions);
        }
      }

          // this.initializeChart(item1);
          this.filteredColumnData =[]
          this.filteredRowData=[]

      console.log('filtered dashboard-data',item1)
    }
})
if(isLiveReloadData && liveSheetIndex == this.dashboard.length-1){
  this.updateDashboard(isLiveReloadData);
}
}

formatKPINumber(value : number, KPIDisplayUnits: string, KPIDecimalPlaces : number,KPIPrefix: string,KPISuffix: string  ) {
  let formattedNumber = value+'';
  let KPINumber;
  if (KPIDisplayUnits !== 'none') {
    switch (KPIDisplayUnits) {
      case 'K':
        formattedNumber = (value / 1_000).toFixed(KPIDecimalPlaces) + 'K';
        break;
      case 'M':
        formattedNumber = (value / 1_000_000).toFixed(KPIDecimalPlaces) + 'M';
        break;
      case 'B':
        formattedNumber = (value / 1_000_000_000).toFixed(KPIDecimalPlaces) + 'B';
        break;
      case 'G':
        formattedNumber = (value / 1_000_000_000_000).toFixed(KPIDecimalPlaces) + 'G';
        break;
      case '%':
        let KPIPercentageDivisor = Math.pow(10, Math.floor(Math.log10(value)) + 1); // Get next power of 10
        let percentageValue = (value / KPIPercentageDivisor) * 100; // Convert to percentage
        formattedNumber = percentageValue.toFixed(KPIDecimalPlaces) + ' %'; // Keep decimals
        break;
    }
  } else {
    formattedNumber = (value).toFixed(KPIDecimalPlaces)
  }

  return KPINumber = KPIPrefix + formattedNumber + KPISuffix;
}

closeFilterModal(){
  this.modalService.dismissAll('close')
}

  findSheetIndex(sheetID: number): number {
    return this.dashboard.findIndex(sheet => sheet['sheetId'] === sheetID);
  }

deleteDashboardFilter(id:any){
  const Obj =
    {"filter_id" : [id]
};
  this.workbechService.deleteDashbaordFilter(Obj).subscribe({
    next:(data)=>{
      console.log(data);
      this.DahboardListFilters =  this.DahboardListFilters.filter((obj : any) => obj.dashboard_filter_id !== id);
      // this.colData= data.col_data?.map((name: any) => ({ label: name, selected: false }))
      let deletedFilterSheetsList = data.sheet_ids;
      let reqObj : any = {
        "dashboard_id":this.dashboardId,
        "sheet_ids" : deletedFilterSheetsList
      };
      if(deletedFilterSheetsList && deletedFilterSheetsList.length > 0) {
      this.workbechService.dashboardFilterDeleteFetchSheetData(reqObj).subscribe({
        next:(data : any)=>{
          console.log(data);
          delete this.storeSelectedColData.test[id];
          data.sql_queries.forEach((item: any) => {
            item.columns.forEach((res:any) => {      
              let obj1={
                name:res.column,
                values: res.result
              }
              this.filteredColumnData.push(obj1);
              console.log('filtercolumn',this.filteredColumnData)
            });
            item.rows.forEach((res:any) => {
              let obj={
                name: res.column,
                data: res.result
              }
              this.filteredRowData.push(obj);
              console.log('filterowData',this.filteredRowData)
            });
            this.setDashboardSheetData(item, true, false, false, false, '', false,0);
          });
          this.toasterService.success('Filter Deleted Succesfully','success',{ positionClass: 'toast-top-center'})
          this.getFilteredData();
          // this.colData= data.col_data?.map((name: any) => ({ label: name, selected: false }))

        },
        error:(error)=>{
          console.log(error)
          this.toasterService.error(error.error.message,'error',{ positionClass: 'toast-top-center'})

        }
    });
  } else {
    this.toasterService.success('Filter Deleted Succesfully','success',{ positionClass: 'toast-top-center'})

  }
  this.editFilters = false;
  this.filterName = '';
  this.selectedDatabase='';
  this.dropdownOptions = [];
  this.querySetNames = [];
  this.selectedQuerySetId = 0;
  this.selectedOption = null;
  this.sheetsFilterNames =[];
  this.selectedColumnQuerySetId = null;
  },
    error:(error)=>{
      console.log(error)
      Swal.fire({
        icon: 'error',
        title: 'oops!',
        text: error.error.message,
        width: '400px',
      })
    }
  });
}
  
//edit filter
addfilterOnEdit(){
  this.editFilters = false;
  this.selectedRowsEdit =[];
  this.selectClmnEdit ='';
  this.filterName = '';
  this.isAllSelected = false;
  this.querysetNameEdit = '';
  //new
  this.dropdownOptions = [];
this.selectedQuerySetId = 0;
this.selectedOption ='';
}
dbIdforEditFilter:any;
databaseNameForEditFilter:any;
editFiltersData(id:any){
  this.editFilters=true;
  const obj ={
    filter_id:id
  }
  this.dashboardFilterIdEdit = id;
  this.workbechService.editFilterDataGet(obj).subscribe({
    next:(data)=>{
      console.log(data);
      this.filterName = data.filter_name;
      this.sheetsFilterNamesFromEdit = data.sheets;
      this.querysetNameEdit = data.queryname;
      this.selectClmnEdit = data.selected_column;
      this.selectdColmnDtypeEdit = data.datatype;
      this.editquerysetId = data.query_id;
      this.tableNameSelectedForFilter = data.table_name;
      this.querySetNames=data.unselected_query;
      this.dbIdforEditFilter = data.hierarchy_id;
      this.selectedColumnQuerySetId= data.selected_query;
      // this.selectedOption = data.selected_query;
      this.databaseNameForEditFilter = data.database_name;
      this.selectedQuerySetId = data.selected_query_id.map(
        (item: { queryset_id: any; }) => item.queryset_id
      );
      this.updateSelectedRowsEdit();
      // this.getColumnsFromEdit(data.query_id,data.dashboard_id);
      this.getColumnsForFilterEdit(this.selectedQuerySetId,data.dashboard_id);
      this.selectedOption=data.selected_column;

      this.selectClmn=data.selected_column;
      this.selectdColmnDtype=data.datatype;
    },
    error:(error)=>{
      console.log(error)
      Swal.fire({
        icon: 'error',
        title: 'oops!',
        text: error.error.message,
        width: '400px',
      })
    }
  })
}

// getColumnsFromEdit(qryId:any,dashboardIID:any){
//     const obj ={
//       dashboard_id:dashboardIID,
//       queryset_id : qryId
//     }
//     this.editquerysetId = qryId
//   this.workbechService.getColumnsInDashboardFilter(obj).subscribe({
//     next:(data)=>{
//       console.log(data);
//       this.columnFilterNamesEdit=data.response_data?.columns;

//     },
//     error:(error)=>{
//       console.log(error)
//       Swal.fire({
//         icon: 'error',
//         title: 'oops!',
//         text: error.error.message,
//         width: '400px',
//       })
//     }
//   })
// }
isAnySheetSelected(){
  return this.sheetsFilterNamesFromEdit.some((sheet: { selected: any; }) => sheet.selected);
}
updateSelectedRowsEdit(){
  this.selectedRowsEdit = this.sheetsFilterNamesFromEdit
  .filter((row: { selected: any; }) => row.selected)
  .map((row: { id: any; }) => row.id);
console.log('selected rows', this.selectedRowsEdit);
this.isAllSelected = this.sheetsFilterNamesFromEdit.every((row: { selected: any; }) => row.selected);
}
toggleAllRowsEdit(event: Event) {
  const isChecked = (event.target as HTMLInputElement).checked;
  this.sheetsFilterNamesFromEdit.forEach((row: { selected: boolean; }) => row.selected = isChecked);
  this.updateSelectedRowsEdit();
}
closeColumnsDropdownEdit(colName:any,colDatatype:any, dropdown: NgbDropdown) {
  dropdown.close();
  this.selectClmnEdit=colName,
  this.selectdColmnDtypeEdit=colDatatype

}
updateFilters(){
  if(this.filterName === ''){
    this.toasterService.error('Please Add Filter Name','error',{ positionClass: 'toast-center-center'})
  
  }else{
const obj ={
  dashboard_filter_id:this.dashboardFilterIdEdit,
  dashboard_id:this.dashboardId,
  filter_name:this.filterName,
  column:this.selectClmn,
  sheets:this.selectedRowsEdit,
  datatype:this.selectdColmnDtype,
  queryset_id:this.selectedQuerySetId,
  table_name:this.tableNameSelectedForFilter,
  selected_query:this.selectedColumnQuerySetId,
  hierarchy_id:this.dbIdforEditFilter

}
  this.workbechService.updatesDashboardFilters(obj).subscribe({
    next:(data)=>{
      console.log(data);
      this.modalService.dismissAll('close');
      this.getDashboardFilterredList();
      this.toasterService.success('Filter Updated Successfully','success',{ positionClass: 'toast-top-right'});
      this.selectedOption = null;
      this.clearAllFilters();
    },
    error:(error)=>{
      console.log(error)
      this.toasterService.error(error.error.message, 'error', { positionClass: 'toast-center-center' })
    }
  })
}
}
///
dropTest2(event: any) {
  if(this.colArray.length >0 && this.rowArray.length>0){
    this.colArray = [];
    this.rowArray = [];
  }
  if (event.previousContainer === event.container) {
    moveItemInArray(event.container.data, event.previousIndex, event.currentIndex);
  } else {
    console.log('Transfering item to new container')
    console.log('Transferring item to new container');
    
    let item: any = event.previousContainer.data[event.previousIndex];
    console.log('Original item:', JSON.stringify(item));
    
    // Creating a deep copy of the item
    let copy: any = JSON.parse(JSON.stringify(item));
    console.log('Copy of item:', JSON.stringify(copy));
    
    // Initialize an empty object to hold the copied attributes
    let element: DashboardItem = {
      id:copy.id,
      x:copy.x,
        y: copy.y,
      rows: 1,
      cols:1,
      data: copy.data,
      sheetType:copy.sheetType,
      sheetId:copy.sheetId,
      chartType:copy.chartType,
      chartId:copy.chartId,
      chartOptions: copy.chartOptions,
      chartInstance: copy.chartInstance,
      tableData:copy.tableData,
      chartData:copy.chartOptions?.chartData || [],
    };
    this.dashboardTest.push(element);
    this.sheetTabs[this.selectedTabIndex].dashboard = this.dashboardTest;
  }
 
}

  selectedSheetTab(event: any) {
    this.selectedTabIndex = event.index;
    this.dashboardTest = this.sheetTabs[this.selectedTabIndex].dashboard;
  }

  addTabs() {
    this.displayTabs = true;
    let id = uuidv4();
    this.selectedTab = { id: id };
    this.selectedTabIndex = this.sheetTabs.length;
    let name = this.selectedTabIndex > 0 ? "Sheet Title " + this.selectedTabIndex : "Sheet Title";
    this.sheetTabs.push({ id: id, name: name, dashboard: [] });
    this.dashboardTest = [];
  }
  Editor = ClassicEditor;
  editor : boolean = false;
  editorConfig = {
    fontFamily: {
      options: [
        'default',
        'Arial, Helvetica, sans-serif',
        'Georgia, serif',
        'Impact, Charcoal, sans-serif',
        'Tahoma, Geneva, sans-serif',
        'Times New Roman, Times, serif',
        'Trebuchet MS, Helvetica, sans-serif',
        'Verdana, Geneva, sans-serif',
        'Courier New, Courier, monospace',
        'Lucida Sans Unicode, Lucida Grande, sans-serif',
        'Comic Sans MS, Comic Sans, cursive',
        'Palatino Linotype, Book Antiqua, Palatino, serif',
        'Arial Black, Gadget, sans-serif'
      ],
      supportAllValues: true
    },
    fontSize: {
      options: [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
    },
    toolbar: ['undo', 'redo', '|', 'selectAll', '|', 'heading', '|', 'bold', 'italic', 'underline', 
      '|', 'removeformat', '|', 'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', '|', 'alignment'],
    plugins: [
      Bold, Essentials, Italic, Mention, Paragraph, Undo, Font, Alignment, Underline, RemoveFormat, SelectAll, Heading],
  };
  
  toggleEditor() {
    this.editor = !this.editor;
  }
  updateSheetName() {
    const inputElement = document.getElementById('htmlContent') as HTMLInputElement;
    if (inputElement) {
      inputElement.innerHTML = this.dashboardTagName;
      inputElement.style.paddingTop = '1.5%';
    }
    const parser = new DOMParser();
    const doc = parser.parseFromString(this.dashboardTagName, 'text/html');
    this.dashboardName = doc.body.textContent+'';
}
kpiData?: KpiData;
  loadDashboard(){
    let obj = {sheet_ids: this.sheetIdsDataSet};
    this.workbechService.sheetRetrivelBasedOnIds(obj).subscribe({
      next:(data)=>{
        console.log('savedDashboard',data);
      let sheetArray = data.map((sheet:any)=>sheet.sheets[0]);
      this.dashboardNew = sheetArray.map((sheet:any) => ({
        id:uuidv4(),
        cols: 1,
        rows: 1,
        y: 10,
        x: 10,
        sheetType:sheet.sheet_type,
        sheetId:sheet.sheet_id,
        chartType:sheet.chart,
        chartId:sheet.chart_id,
        databaseId : sheet.hierarchy_id,
        // fileId : sheet.file_id,
        qrySetId : sheet.queryset_id,
        isEChart : sheet.sheet_data.isEChart,
        data: { title: sheet.sheet_name, content: 'Content of card New', sheetTagName:sheet.sheet_tag_name? sheet.sheet_tag_name:sheet.sheet_name },
        selectedSheet: sheet.selectedSheet,
        column_Data: sheet.sheet_data.columns_data,
        row_Data: sheet.sheet_data.rows_data,
        drillDownHierarchy: sheet.sheet_data.drillDownHierarchy,
        isDrillDownData: sheet.sheet_data.isDrillDownData,
        kpiData: sheet.sheet_type === 'Chart' && sheet.chart_id === 25
        ? (() => {
            this.kpiData = {
              kpiNumber : sheet.sheet_data?.results?.kpiNumber || 0,
            kpiPrefix : sheet.sheet_data?.results?.kpiPrefix || '',
            kpiSuffix : sheet.sheet_data?.results?.kpiSuffix || '',
            kpiDecimalUnit : sheet.sheet_data?.results?.kpiDecimalUnit || 'none',
            kpiDecimalPlaces : sheet.sheet_data?.results?.kpiDecimalPlaces || 0,
              rows: sheet.sheet_data?.results?.kpiData || [],       // Default to an empty array if not provided
              fontSize: sheet.sheet_data?.results?.kpiFontSize || '16px', // Default font size
              color: sheet.sheet_data?.results?.kpicolor || '#000000',    // Default color (black)
            };
            return this.kpiData; // Return the kpi object to kpiData
          })()
        : undefined,
        chartOptions: sheet.sheet_type === 'Chart' ? {
          // ...this.getChartOptions(sheet.chart,sheet?.sheet_data.x_values,sheet?.sheet_data.y_values),
          ... this.getChartOptionsBasedOnType(sheet) as unknown as ApexOptions,
          // chart: { type: sheet.chart, height: 300 },
          //chartData:this.getChartData(sheet.sheet_data.results, sheet.chart)
        } : undefined,
        tableData: sheet.sheet_type === 'Table' ? {
         ... this.getTableData(sheet.sheet_data)
  
        }
         : undefined,
         numberFormat: {
          donutDecimalPlaces:this.donutDecimalPlaces,
          decimalPlaces:sheet?.sheet_data?.numberFormat?.decimalPlaces,
          displayUnits:sheet?.sheet_data?.numberFormat?.displayUnits,
          prefix:sheet?.sheet_data?.numberFormat?.prefix,
          suffix:sheet?.sheet_data?.numberFormat?.suffix
        },
        pivotData: sheet.sheet_type === 'PIVOT' ? {
          pivotDataTransformed:sheet?.sheet_data?.pivotTransformedData,
          pivotRowData:sheet?.sheet_data?.row,
          pivotMeasureData:sheet?.sheet_data?.pivotMeasure_Data,
          pivotColData:sheet?.sheet_data?.col
        }
        : undefined,
        customizeOptions: sheet?.sheet_data?.customizeOptions
      }));
      this.setSelectedSheetData();
      this.removeUnSelectedSheetsFromCanvas();
       this.isSheetsView = false;
      },
      error:(error)=>{
        console.log(error)
      }
    })
  }
  removeUnSelectedSheetsFromCanvas(){
    this.dashboard = this.dashboard.filter((item:any) => this.sheetIdsDataSet.includes(item.sheetId));
  }

  pageChangegetUserSheetsList(page:any){
    this.pageNo=page;
    this.fetchSheetsList();
    }
  fetchSheetsListSearch() {
    this.pageNo = 1;
    this.fetchSheetsList();
  }
  fetchSheetsList(){
    let obj;
    if( this.searchSheets && this.searchSheets.trim() != '' && this.searchSheets.length > 0){
      obj ={
        sheet_ids : this.sheetIdsDataSet,
        page_no : this.pageNo,
        search : this.searchSheets,
        page_count:this.itemsPerPage
      }
    } else {
      obj ={
        sheet_ids : this.sheetIdsDataSet,
        page_no : this.pageNo,
        // search : this.searchSheets,
        page_count:this.itemsPerPage

      }
    }

    this.workbechService.fetchSheetsList(obj).subscribe({
      next:(data)=>{
        console.log('savedDashboard',data);
       this.panelscheckbox = data.sheets;
       this.totalItems = data.total_items;
       this.itemsPerPage = data.items_per_page;
      },
      error:(error)=>{
        this.panelscheckbox = [];
        console.log(error)
      }
    })
  }

  addSheetIds(data:any,panel : any){
    data.is_selected = !data.is_selected;
    let dataSet = new Set(this.sheetIdsDataSet);

    if(data.is_selected){
      dataSet.add(data.sheet_id);
      panel.sheet_selected = true;
      const allSheetDataTrue = panel.sheet_data.every((item:any) => item.is_selected == true);
      if(allSheetDataTrue){
        panel.is_selected = true;
      }
    } else {
      dataSet.delete(data.sheet_id);
      panel.is_selected = false;
      panel.sheet_selected = false;

    }
    this.sheetIdsDataSet = Array.from(dataSet);
  }

  checkAllChilds(panel: any){
    panel.is_selected = !panel.is_selected;
    let dataSet = new Set(this.sheetIdsDataSet);
    panel.sheet_data.forEach((sheet : any) =>{
      if(panel.is_selected){
        sheet.is_selected = true;
        panel.sheet_selected = true;
        dataSet.add(sheet.sheet_id);
      } else {
        sheet.is_selected = false;
        panel.sheet_selected = false;
        dataSet.delete(sheet.sheet_id);
      }
    });
    this.sheetIdsDataSet = Array.from(dataSet);
  }
  updatedashboardName(name:any){
    this.dashboardTagName = name;
    this.dashboardTagTitle = this.sanitizer.bypassSecurityTrustHtml(this.dashboardTagName);
    const parser = new DOMParser();
    const doc = parser.parseFromString(this.dashboardTagName, 'text/html');
    this.dashboardName = doc.body.textContent+'';
    if(this.dashboardName !== name){
      this.canNavigateToAnotherPage = true;
    }
  }
  sheetsRoute(){
    this.router.navigate(['/analytify/sheets']);  
  }






  //public apis
  getSavedDashboardDataPublic(){
    const obj ={
      dashboard_id:this.dashboardId
    }
    this.workbechService.getSavedDashboardDataPublic(obj).subscribe({
      next:(data)=>{
        console.log('savedDashboard',data);
        this.dashboardName=data.dashboard_name;
        this.heightGrid = data.height;
        this.widthGrid = data.width;
        this.gridType = data.grid_type;
        this.changeGridType(this.gridType);
        this.qrySetId = data.queryset_id;
        // this.fileId = data.file_id;
        this.databaseId = data.hierarchy_id;
        this.dashboardsheetsIdArray = data.sheet_ids;
        this.dashboard = data.dashboard_data;
        this.sheetIdsDataSet = data.selected_sheet_ids;
        let self = this;
        this.dashboard.forEach((sheet : any)=>{
          console.log('Before sanitization:', sheet.data.sheetTagName);
          this.sheetTagTitle[sheet.data.title] = this.sanitizer.bypassSecurityTrustHtml(sheet.data.sheetTagName);
          if((sheet && sheet.chartOptions && sheet.chartOptions.chart)) {
            sheet.chartOptions.chart.events = {
              markerClick: (event: any, chartContext: any, config: any) => {
                let selectedXValue;
                if(sheet.chartId == 24 || sheet.chartId == 10 || sheet.chartId == 17 || sheet.chartId == 4){
                  selectedXValue = sheet.chartOptions.labels[config.dataPointIndex];
                } else {
                  selectedXValue = sheet.chartOptions.xaxis.categories[config.dataPointIndex];
                }
                if(self.actionId && sheet.sheetId === self.sourceSheetId){
                  self.setDrillThrough(selectedXValue, sheet);  
                }
              },
              dataPointSelection: function (event: any, chartContext: any, config: any) {
                let selectedXValue;
                if(sheet.chartId == 24 || sheet.chartId == 10 ){
                  selectedXValue = sheet.chartOptions.labels[config.dataPointIndex];
                } else {
                  selectedXValue = sheet.chartOptions.xaxis.categories[config.dataPointIndex];
                }
                if(self.actionId && sheet.sheetId === self.sourceSheetId){
                  self.setDrillThrough(selectedXValue, sheet);  
                }               
                if (sheet.drillDownIndex < sheet.drillDownHierarchy.length - 1) {
                  // const selectedXValue = element.chartOptions.series[0].data[config.dataPointIndex];
                  console.log('X-axis value:', selectedXValue);
                  let nestedKey = sheet.drillDownHierarchy[sheet.drillDownIndex];
                  sheet.drillDownIndex++;
                  let obj = { [nestedKey]: selectedXValue };
                  sheet.drillDownObject.push(obj);
                  self.publicDataExtraction(sheet);
                }
              },
              mounted: function(chartContext:any, config:any) {
                if (sheet.chartId == 28) {
                  let color = sheet?.chartOptions?.plotOptions?.radialBar?.dataLabels?.name?.color;
                  const applyStyles = () => {
                    const valueElement = document.querySelector('.apexcharts-datalabel-value') as HTMLElement;
                    if (valueElement) {
                      valueElement.style.fill = color;
                      valueElement.style.setProperty('fill', color, 'important');
                    }
      
                    const nameElement = document.querySelector('.apexcharts-datalabel-label') as HTMLElement;
                    if (nameElement) {
                      nameElement.style.fill = color;
                      nameElement.style.setProperty('fill', color, 'important');
                    }
                  };
                  // Initial styling
                  applyStyles();
      
                  // Monitor DOM for changes
                  const observer = new MutationObserver(() => {
                    applyStyles();
                  });
                  const chartContainer = document.querySelector('.apexcharts-inner');
                  if (chartContainer) {
                    observer.observe(chartContainer, { childList: true, subtree: true });
                  }
                }
              }
            };
          } else if(sheet.chartId == 29){
            this.chartType = 'map';
            sheet.echartOptions?.series[0]?.data?.forEach((data: any) => {
              this.chartsColumnData.push(data.name);
              this.chartsRowData.push(data.value);
            });
            this.dualAxisColumnData = [{
              name: sheet?.column_Data[0][0],
              values: this.chartsColumnData
            }]
            this.dualAxisRowData = [{
              name: sheet?.row_Data[0][0],
              data: this.chartsRowData
            }]
            sheet.echartOptions.tooltip= {
              formatter: (params: any) => {
                const { name, data } = params;
                if (data) {
                  const keys = Object.keys(data);
            const values = Object.values(data);
            let formattedString = '';
            keys.forEach((key, index) => {
              if(key)
              formattedString += `${key}: ${values[index]}<br/>`;
            });
      
            return formattedString;
                 
                } else {
                  return `${name}: No Data`;
                }
              }
          }
          }
          console.log('After sanitization:', sheet.data.sheetTagName);
          this.donutDecimalPlaces = sheet?.numberFormat?.donutDecimalPlaces;
          if(sheet['chartId'] === 10 && sheet.chartOptions && sheet.chartOptions.plotOptions && sheet.chartOptions.plotOptions.pie && sheet.chartOptions.plotOptions.pie.donut && sheet.chartOptions.plotOptions.pie.donut.labels && sheet.chartOptions.plotOptions.pie.donut.labels.total){
            sheet.chartOptions.plotOptions.pie.donut.labels.total.formatter = (w:any) => {
              return w.globals.seriesTotals.reduce((a:any, b:any) => {
                return +a + b
              }, 0).toFixed(this.donutDecimalPlaces);
            };
          }
          let chartId : number = sheet['chartId'];
          const numberFormat = sheet?.numberFormat;
          const isEcharts = sheet?.isEChart;
          this.updateNumberFormat(sheet, numberFormat, chartId, isEcharts);
          if(chartId == 11){
            sheet.echartOptions.tooltip.formatter =  function (params: any) {
              const date = params.data[0];
              const value = params.data[1];
              return `Date: ${date}<br/>Value: ${value}`;
            };
            this.calendarTotalHeight = ((150 * sheet.echartOptions.calendar.length) + 25) + 'px';
          }
          if(chartId == 1){
            if(sheet?.tableData?.tableItemsPerPage){
              sheet.tableData.tableItemsPerPage = 10;
            }
            if(sheet?.tableData?.tablePage){
              sheet.tableData.tablePage = 1;
            }
          }
        })
        console.log(this.sheetTagTitle);
        if(!data.dashboard_tag_name){
          // const inputElement = document.getElementById('htmlContent') as HTMLInputElement;
          // inputElement.innerHTML = data.dashboard_name;
          this.dashboardTagName = data.dashboard_name;
        }
        else{
          // const inputElement = document.getElementById('htmlContent') as HTMLInputElement;
          // inputElement.innerHTML = data.dashboard_tag_name;
          // inputElement.style.paddingTop = '1.5%';
          this.dashboardTagName = data.dashboard_tag_name;
        }
        this.dashboardTagTitle = this.sanitizer.bypassSecurityTrustHtml(this.dashboardTagName);
        console.log(this.dashboard);
        let obj = {sheet_ids: this.sheetIdsDataSet};
      },
      error:(error)=>{
        console.log(error)
      }
    })
  }

  getDashboardFilterredListPublic(){
    const Obj ={
      dashboard_id:this.dashboardId
    }
    this.workbechService.getDashboardFilterredListPublic(Obj).subscribe({
      next:(data)=>{
        console.log(data);
        this.DahboardListFilters = data
      },
      error:(error)=>{
        console.log(error)
        Swal.fire({
          icon: 'error',
          title: 'oops!',
          text: error.error.message,
          width: '400px',
        })
      }
    })
  }
  getFilteredDataPublic(){
    this.extractKeysAndData();
    const Obj ={
      id:this.keysArray,
      exclude_ids:this.excludeFilterIdArray,
      input_list:this.dataArray
    }
    if(this.keysArray && this.keysArray.length > 0){
    this.workbechService.getFilteredDataPublic(Obj).subscribe({
      next:(data)=>{
        console.log(data);
        // this.tablePreviewColumn = data.columns;
        // this.tablePreviewRow = data.rows;
        // console.log(this.tablePreviewColumn);
        // console.log(this.tablePreviewRow);
        // localStorage.removeItem('filterid')
        this.sheetFilters = data;
        data.forEach((item: any) => {
          this.tablePreviewColumn.push(item.columns);
      this.tablePreviewRow.push(item.rows);
        item.columns.forEach((res:any) => {      
          let obj1={
            name:res.column,
            values: res.result
          }
          this.filteredColumnData.push(obj1);
          console.log('filtercolumn',this.filteredColumnData)
        });
        item.rows.forEach((res:any) => {
          let obj={
            name: res.column,
            data: res.result
          }
          this.filteredRowData.push(obj);
          console.log('filterowData',this.filteredRowData)
        });
        // this.setDashboardSheetData(item, true, true);
        if(item.chart_id === 1){
          this.pageChangeTableDisplayPublic(item,1)
        }else{
        this.setDashboardSheetData(item, true , true, false, false, '', false,0);
        }
      });
        },
      error:(error)=>{
        console.log(error)
        Swal.fire({
          icon: 'error',
          title: 'oops!',
          text: error.error.message,
          width: '400px',
        })
      }
    });
  }
  }
  getColDataFromFilterIdPublic(id:string,colData:any){
    if(localStorage.getItem('filterid')){
      colData['colData']= JSON.parse(localStorage.getItem('filterid')!);
    } else {
    const Obj ={
      id:id
    }
    this.workbechService.getColDataFromFilterIdPublic(Obj).subscribe({
      next:(data)=>{
        console.log(data);
        const lookup = new Map<number, boolean>();
        if (colData['colData']) {
          colData['colData'].forEach((item: any) => {
            lookup.set(item.label, item.selected);
          });
          const array3 = [...colData['colData']];
          data.col_data.forEach((label: any) => {
            if (!lookup.has(label)) {
              array3.push({ label, selected: false });
            }
          });
        colData['colData']= array3;
        } else {
          colData['colData']= data.col_data?.map((name: any) => ({ label: name, selected: false }))
        }
        localStorage.setItem(id, JSON.stringify(colData['colData']));
        console.log('coldata',this.colData)
      },
      error:(error)=>{
        console.log(error)
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

  publicDataExtraction(item : any){
    this.extractKeysAndData();
    let Obj : any = {
      "col":item.column_Data,"row":item.row_Data,
      id:this.keysArray,
      input_list:this.dataArray,
      // "id":["766"],"input_list":[["Home Appliances"]],
      "dashboard_id":this.dashboardId,
      "sheet_id":item.sheetId,
      "hierarchy_id":item.databaseId,
      // "file_id": item.fileId,
      "is_date":item.isDrillDownData,
  "drill_down":item.drillDownObject,
  "next_drill_down":item.drillDownHierarchy[item.drillDownIndex],
  "is_exclude":this.excludeFilterIdArray
    }
    this.workbechService.getPublicDashboardDrillDowndata(Obj).subscribe({
      next:(data)=>{
     console.log(data);
      data.data.col.forEach((res:any) => {      
        let obj1={
          name:res.column,
          values: res.result_data
        }
        this.filteredColumnData.push(obj1);
        if (item.chartId == '29') {
          this.dualAxisColumnData = this.filteredColumnData;
          this.chartsColumnData = this.dualAxisColumnData[0].values;
        }
        console.log('filtercolumn',this.filteredColumnData)
      });
      data.data.row.forEach((res:any) => {
        let obj={
          name: res.col,
          data: res.result_data
        }
        this.filteredRowData.push(obj);
        if (item.chartId == '29') {
          this.dualAxisRowData = this.filteredRowData;
          this.chartsRowData = this.dualAxisRowData[0].data;
        }
        console.log('filterowData',this.filteredRowData)
      });
      this.setDashboardSheetData(item, false, false, true, false, '', false,0);
      // if(item.chartId == '29'){
      //   if (item.drillDownIndex != 0) {
      //     this.chartType = 'bar';
      //   }
      //   else {
      //     this.chartType = 'map';
      //   }
      // }
        },
      error:(error)=>{
        console.log(error)
        Swal.fire({
          icon: 'error',
          title: 'oops!',
          text: error.error.message,
          width: '400px',
        })
      }
    });
  }

  dataExtraction(item : any){
    this.extractKeysAndData();
    let draggedColumnsObj;
    if (item.isDrillDownData) {
      draggedColumnsObj = _.cloneDeep(item.column_Data);
      draggedColumnsObj[0][2] = 'year'
    } else {
      draggedColumnsObj = item.column_Data
    }
    let Obj : any = {
      "col":draggedColumnsObj,"row":item.row_Data,
      id:this.keysArray,
      input_list:this.dataArray,
      // "id":["766"],"input_list":[["Home Appliances"]],
      "dashboard_id":this.dashboardId,
      // "file_id": item.fileId,
      "sheet_id":item.sheetId,
      "hierarchy_id":item.databaseId,
      "is_date":item.isDrillDownData,
  "drill_down":item.drillDownObject,
  "next_drill_down":item.drillDownHierarchy[item.drillDownIndex],
  "is_exclude":this.excludeFilterIdArray
    }
    this.workbechService.getDashboardDrillDowndata(Obj).subscribe({
      next:(data)=>{
     console.log(data);
      data.data.col.forEach((res:any) => {      
        let obj1={
          name:res.column,
          values: res.result_data
        }
        this.filteredColumnData.push(obj1);
        if (item.chartId == '29') {
          this.dualAxisColumnData = this.filteredColumnData;
          this.chartsColumnData = this.dualAxisColumnData[0].values;
        }
        console.log('filtercolumn',this.filteredColumnData)
      });
      data.data.row.forEach((res:any) => {
        let obj={
          name: res.col,
          data: res.result_data
        }
        this.filteredRowData.push(obj);
        if (item.chartId == '29') {
          this.dualAxisRowData = this.filteredRowData;
          this.chartsRowData = this.dualAxisRowData[0].data;
        }
        console.log('filterowData',this.filteredRowData)
      });
      this.setDashboardSheetData(item, false, false, true, false, '', false,0);
      // if(item.chartId == '29'){
      //   if (item.drillDownIndex != 0) {
      //     this.chartType = 'bar';
      //   }
      //   else {
      //     this.chartType = 'map';
      //   }
      // }
        },
      error:(error)=>{
        console.log(error)
        Swal.fire({
          icon: 'error',
          title: 'oops!',
          text: error.error.message,
          width: '400px',
        })
      }
    });
  }

  goDrillDownBack(item: any){
    if(item.drillDownIndex > 0) {
      item.drillDownIndex--;
      item.drillDownObject.pop();
      if(this.isPublicUrl){
        this.publicDataExtraction(item);
      } else {
        this.dataExtraction(item);
      }
    }         
  }
  //mobile view filters
 // Initially, panel is hidden

  togglePanel() {
    this.isPanelHidden = !this.isPanelHidden; 
    this.cdr.detectChanges();  // Force change detection

  }
  issheetListPaneOpen : boolean = true;
  toggleSidebar() {
    const sidebar = document.getElementById("sticky-sidebar");
    const dashboardContent = document.getElementById("dashboard-content");
    if (sidebar?.classList.contains("d-none")) {
      sidebar.classList.remove("d-none");
      sidebar.classList.add("col-xl-2");
      sidebar.classList.add("col-lg-2");
      sidebar.classList.add("col-md-2");
      dashboardContent?.classList.remove("col-lg-12");
      dashboardContent?.classList.remove("col-xl-12");
      dashboardContent?.classList.remove("col-md-12");
      dashboardContent?.classList.add("col-lg-10");
      dashboardContent?.classList.add("col-xl-10");
      dashboardContent?.classList.add("col-md-10");
  } else {
      sidebar?.classList.add("d-none");
      sidebar?.classList.remove("col-xl-2");
      sidebar?.classList.remove("col-lg-2");
      sidebar?.classList.remove("col-md-2");
      dashboardContent?.classList.remove("col-lg-10");
      dashboardContent?.classList.remove("col-xl-10");
      dashboardContent?.classList.remove("col-md-10");
      dashboardContent?.classList.add("col-xl-12");
      dashboardContent?.classList.add("col-lg-12");
      dashboardContent?.classList.add("col-md-12");
  }
}
//tablePagination
tableSearchDashboard(item:any,value:any){
  this.tablePageNo=1;
  this.tableSearch = value;
  this.pageChangeTableDisplay(item,1,false,0);
}
pageChangeTableDisplay(item:any,page:any,isLiveReloadData : boolean,liveSheetIndex:any){
  if(item.tableData){
  item.tableData.tablePage = page;
  }
  const obj={
    sheet_id:item.sheetId ?? item.sheet_id,
    id:this.keysArray,
    input_list:this.dataArray,
    hierarchy_id: item.databaseId,
    // file_id: item.fileId,
    page_no: page,
    page_count: this.tableItemsPerPage,
    dashboard_id:this.dashboardId,
    search:this.tableSearch,
    is_exclude:this.excludeFilterIdArray
  }
  if(obj.search === '' || obj.search === null){
    delete obj.search;
  }
  this.workbechService.paginationTableDashboard(obj).subscribe({
    next:(data)=>{
      data.data['chart_id']=1,
      data.data['sheet_id']=item.sheetId ?? item.sheet_id,
      this.tableItemsPerPage = data.items_per_page;
      this.tableTotalItems = data.total_items;
      this.setDashboardSheetData(data.data, true , false, false, false, '', isLiveReloadData,liveSheetIndex);
    },error:(error)=>{
      console.log(error.error.message);
    }
  })  
}
tableSearchDashboardPublic(item:any,value:any){
  this.tablePageNo=1;
  this.tableSearch = value;
  this.pageChangeTableDisplayPublic(item,1);
}
pageChangeTableDisplayPublic(item:any,page:any){
  if(item?.tableData?.tablePage ){
    item.tableData.tablePage = page;
  }
  const obj={
    sheet_id:item.sheetId ?? item.sheet_id,
    id:this.keysArray,
    input_list:this.dataArray,
    hierarchy_id: item.databaseId,
    // file_id: item.fileId,
    page_no: page,
    page_count: this.tableItemsPerPage,
    dashboard_id:this.dashboardId,
    search:this.tableSearch,
    is_exclude:this.excludeFilterIdArray
  }
  if(obj.search === '' || obj.search === null){
    delete obj.search;
  }
  this.workbechService.paginationTableDashboardPublic(obj).subscribe({
    next:(data)=>{
      data.data['chart_id']=1,
      data.data['sheet_id']=item.sheetId ?? item.sheet_id,
      this.tableItemsPerPage = data.items_per_page;
      this.tableTotalItems = data.total_items;
      this.setDashboardSheetData(data.data, true , false, false, false, '', false,0);
    },error:(error)=>{
      console.log(error.error.message);
    }
  }) 
}
disableDragging(event: MouseEvent) {
  event.stopPropagation();
  this.isDraggingDisabled = true;  // Disable dragging
  this.updateGridsterOptions();     // Update Gridster options
}

enableDragging(event: MouseEvent) {
  event.stopPropagation();
  this.isDraggingDisabled = false;  // Re-enable dragging
  this.updateGridsterOptions();      // Update Gridster options
}

updateGridsterOptions() {
  if (this.options && this.options.draggable) {
    this.options.draggable.enabled = this.editDashboard && !this.isDraggingDisabled;
  }
}
stopDragging(event: MouseEvent) {
  event.stopPropagation(); // Prevent the event from triggering dragging
}
donutDecimalPlaces:number = 2;

formatNumber(value: number,decimalPlaces:number,displayUnits:string,prefix:string,suffix:string): string {
  let formattedNumber = value+'';

    switch (displayUnits) {
      case 'K':
        formattedNumber = (value / 1_000).toFixed(decimalPlaces) + 'K';
        break;
      case 'M':
        formattedNumber = (value / 1_000_000).toFixed(decimalPlaces) + 'M';
        break;
      case 'B':
        formattedNumber = (value / 1_000_000_000).toFixed(decimalPlaces) + 'B';
        break;
      case 'G':
        formattedNumber = (value / 1_000_000_000_000).toFixed(decimalPlaces) + 'G';
        break;
      case 'none':
        formattedNumber = (value/1).toFixed(decimalPlaces);
        break;
    }
  return prefix + formattedNumber + suffix;
}

  excludeFilterIdList(filterData: any, event : any) {
    if (filterData && event?.target?.checked) {
      this.excludeFilterIdArray.push(filterData.dashboard_filter_id);
    } else {
      let index = this.excludeFilterIdArray.indexOf(filterData.dashboard_filter_id);
      if (index > -1) {
        this.excludeFilterIdArray.splice(index, 1);
      }
    }
  }

  updateNumberFormat(sheet : any, numberFormat : any, chartId : any, isEcharts : any){
    if(numberFormat?.decimalPlaces || numberFormat?.displayUnits || numberFormat?.prefix || numberFormat?.suffix){
      if(isEcharts){
        if([2,3].includes(chartId)){
          if (sheet.echartOptions?.xAxis?.axisLabel) {
            sheet.echartOptions.xAxis.axisLabel.formatter = (val: any) => {
              return this.formatNumber(val, numberFormat?.decimalPlaces, numberFormat?.displayUnits, numberFormat?.prefix, numberFormat?.suffix);
            };
          }
          if(sheet.echartOptions?.series){
            sheet.echartOptions.series.forEach((data:any)=>{
              if( data?.label){
                data.label.formatter = (val: any) => {
                  return this.formatNumber(val.value, numberFormat?.decimalPlaces, numberFormat?.displayUnits, numberFormat?.prefix, numberFormat?.suffix);
                };
              }
            })
          }
        } else if([26].includes(chartId)){
          if(sheet.echartOptions?.series){
            sheet.echartOptions.series.forEach((data:any)=>{
              if( data?.label){
                data.label.formatter = (val: any) => {
                  return this.formatNumber(val.value[2], numberFormat?.decimalPlaces, numberFormat?.displayUnits, numberFormat?.prefix, numberFormat?.suffix);
                };
              }
            })
          }
        } else if([27].includes(chartId)){
          if(sheet.echartOptions?.series){
            sheet.echartOptions.series.forEach((data:any)=>{
              if( data?.label){
                data.label.formatter = (val: any) => {
                  const formattedValue = this.formatNumber(val.value, numberFormat?.decimalPlaces, numberFormat?.displayUnits, numberFormat?.prefix, numberFormat?.suffix);
                  return `${val.name}: ${formattedValue}`;
                };
              }
            })
          }
        } else if([12].includes(chartId)){
          if(sheet.echartOptions?.series){
            sheet.echartOptions.series.forEach((data : any)=>{
              data.data.forEach((measure:any)=>{
                if( measure?.label){
                  measure.label.formatter = (val: any) => {
                    return this.formatNumber(val.value, numberFormat?.decimalPlaces, numberFormat?.displayUnits, numberFormat?.prefix, numberFormat?.suffix);
                  };
                }
              })
            })
          }
        } else if(![1, 25, 10, 24, 28, 11, 29].includes(chartId)){
          if (sheet.echartOptions?.yAxis?.axisLabel) {
            sheet.echartOptions.yAxis.axisLabel.formatter = (val: any) => {
              return this.formatNumber(val, numberFormat?.decimalPlaces, numberFormat?.displayUnits, numberFormat?.prefix, numberFormat?.suffix);
            };
          }
          if(sheet.echartOptions?.series){
            sheet.echartOptions.series.forEach((data:any)=>{
              if( data?.label){
                data.label.formatter = (val: any) => {
                  return this.formatNumber(val.value, numberFormat?.decimalPlaces, numberFormat?.displayUnits, numberFormat?.prefix, numberFormat?.suffix);
                };
              }
            })
          }
        }
      } else {
        if([2,3].includes(chartId)){
          if (sheet.chartOptions?.xaxis?.labels && sheet.chartOptions?.dataLabels) {
            sheet.chartOptions.xaxis.labels.formatter = (val: number) => {
              return this.formatNumber(val, numberFormat?.decimalPlaces, numberFormat?.displayUnits, numberFormat?.prefix, numberFormat?.suffix);
            };            
            sheet.chartOptions.dataLabels.formatter = (val: number) => {
              return this.formatNumber(val, numberFormat?.decimalPlaces, numberFormat?.displayUnits, numberFormat?.prefix, numberFormat?.suffix);
            };
          }
        } else if([26].includes(chartId)){
          if (sheet.chartOptions?.dataLabels) {
            sheet.chartOptions.dataLabels.formatter = (val: number) => {
              return this.formatNumber(val, numberFormat?.decimalPlaces, numberFormat?.displayUnits, numberFormat?.prefix, numberFormat?.suffix);
            };
          }
        } else if([27].includes(chartId)){
          if (sheet.chartOptions?.dataLabels) {
            sheet.chartOptions.dataLabels.formatter = (val: any, opts: any) => {
              const category = opts.w.config.xaxis.categories[opts.dataPointIndex];
              const formattedValue = this.formatNumber(val, numberFormat?.decimalPlaces, numberFormat?.displayUnits, numberFormat?.prefix, numberFormat?.suffix);
              return `${category}: ${formattedValue}`;
            }
          }
        } else if(![1, 25, 10, 24, 28].includes(chartId)){
          if (sheet.chartOptions?.yaxis?.labels) {
            sheet.chartOptions.yaxis.labels.formatter = (val: number) => {
              return this.formatNumber(val, numberFormat?.decimalPlaces, numberFormat?.displayUnits, numberFormat?.prefix, numberFormat?.suffix);
            };
          }
          else if(sheet.chartOptions?.yaxis[0]?.labels && sheet.chartOptions?.yaxis?.length >= 0){
            sheet.chartOptions.yaxis.forEach((data:any)=>{
              data.labels.formatter = (val: number) => {
                return this.formatNumber(val, numberFormat?.decimalPlaces, numberFormat?.displayUnits, numberFormat?.prefix, numberFormat?.suffix);
              };
            });
          }
          if(sheet.chartOptions?.dataLabels){
            sheet.chartOptions.dataLabels.formatter = (val: number) => {
              return this.formatNumber(val, numberFormat?.decimalPlaces, numberFormat?.displayUnits, numberFormat?.prefix, numberFormat?.suffix);
            };
          }
        }
      }
    }
  }
  getSheetsForActions(){
    this.sourceSheetList = [];
    this.targetSheetList = [];
    this.sourceSheetId = 0;
    this.targetSheetIds = [];
    this.isAllTargetSheetsSelected = false;
    const obj ={
      dashboard_id:this.dashboardId,
      queryset_id : this.drillThroughQuerySetId,
    }
    this.workbechService.getSheetsInDashboardAction(obj).subscribe({
      next:(data)=>{
        console.log(data);
        this.sourceSheetList = data.sheet_data;
      },
      error:(error)=>{
        console.log(error)
        Swal.fire({
          icon: 'error',
          title: 'oops!',
          text: error.error.message,
          width: '400px',
        })
      }
    })
  }
  getTargetSheetsList(){
    this.targetSheetList =this.sourceSheetList.map(sheet => ({
      ...sheet,
      selected: false,
    })).filter(sheet => sheet.id != this.sourceSheetId);
    console.log('source:',this.sourceSheetList, 'target: ',this.targetSheetList);
  }
  updateSelectedSheets() {
    this.targetSheetIds = [];
    const selectedSheets = this.targetSheetList.filter(sheet => sheet.selected);
    selectedSheets.forEach((sheet:any)=>{
      this.targetSheetIds.push(sheet.id);
    });
    this.isAllTargetSheetsSelected = this.targetSheetList.length === selectedSheets.length;
    console.log('Selected Sheets:', selectedSheets,this.targetSheetIds);
    this.disableActionSave();
  }
  toggleAllTargetSheets(event: Event) {
    const isChecked = (event.target as HTMLInputElement).checked;
    this.targetSheetList.forEach((sheet:any)=>{
      sheet.selected = isChecked;
    });
    this.updateSelectedSheets();
    this.isAllTargetSheetsSelected = isChecked;
  }
  disableActionSave(){
    if(this.actionName && this.drillThroughQuerySetId && this.sourceSheetId && this.sourceSheetId != 0 && this.targetSheetIds.length>0){
      return false;
    }
    else{
      return true;
    }
  }
  saveDrillThroughAction() {
    const Obj = {
      action_name: this.actionName,
      queryset_id: this.drillThroughQuerySetId,
      dashboard_id: this.dashboardId,
      main_sheet_id: this.sourceSheetId,
      target_sheet_ids: this.targetSheetIds,
      hierarchy_id: this.selectedDbIdForFilter
    }
    this.workbechService.saveDrillThroughAction(Obj).subscribe({
      next: (data) => {
        console.log(data);
        this.actionId = data.dashboard_drill_thorugh_id;
        this.actionName = '';
        this.drillThroughQuerySetId = [];
        this.sourceSheetId = 0;
        this.isAllTargetSheetsSelected = false;
        this.targetSheetList.forEach((sheet:any)=>{
          sheet.selected = false;
        });
        this.targetSheetIds = [];
        this.clearActionForm();
        this.editActions = false;
        this.getDrillThroughActionList();
        this.toasterService.success('Action Added Successfully', 'success', { positionClass: 'toast-top-center' })
      },
      error: (error) => {
        console.log(error)
        this.toasterService.error(error.error.message, 'error', { positionClass: 'toast-center-center' })
      }
    })
  }
  getDrillThroughActionList(){
    const Object ={
      dashboard_id:this.dashboardId
    }
    this.workbechService.getDrillThroughActionList(Object, this.isPublicUrl).subscribe({
      next:(data)=>{
        console.log(data);
        this.drillThroughActionList = data;
      },
      error:(error)=>{
        console.log(error)
        Swal.fire({
          icon: 'error',
          title: 'oops!',
          text: error.error.message,
          width: '400px',
        })
      }
    });
  }
  getEditActionPreview(actionId : any) {
    this.clearActionForm();
    this.editActions = true;
    const object = {
      id: actionId
    }
    this.workbechService.getDrillThroughActionEditPreview(object).subscribe({
      next: (data) => {
        console.log(data);
        this.actionId = data.action_id;
        this.actionName = data.action_name;
        this.drillThroughQuerySetId = data.query_id;
        this.querySetNames = data.queryname
        this.selectedDbIdForFilter = data.hierarchy_id;
        Object.values(this.unfilteredQuerySetData).forEach((value: any) => {
          if (Array.isArray(value)) {
            value.forEach((db : any)=>{
              if(this.selectedDbIdForFilter == db.hierarchy_id){
                this.drillThroughDatabaseName = db.database_name;
              }
            })
          }
        });
        data.main_sheet_data.forEach((sheet:any)=>{
          let object = {
            id : sheet.sheet_id,
            name : sheet.sheet_name
          }
          this.sourceSheetList.push(object);
          if(sheet.selected){
            this.sourceSheetId = sheet.sheet_id;
          }
        });
        data.target_sheet_data.forEach((sheet:any)=>{
          if(sheet.sheet_id != this.sourceSheetId){
            let object = {
              id : sheet.sheet_id,
              name : sheet.sheet_name,
              selected : sheet.selected
            }
            this.targetSheetList.push(object);
          }
        });
        this.updateSelectedSheets();
        this.onDatabaseChange();
      },
      error: (error) => {
        console.log(error)
        Swal.fire({
          icon: 'error',
          title: 'oops!',
          text: error.error.message,
          width: '400px',
        })
      }
    })
  }
  getActionData(actionId : any){
    if(this.actionId && this.actionId != 0){
      this.setDrillThrough('',[]);
    }
    console.log(actionId);
    this.workbechService.getDrillThroughAction(actionId, this.isPublicUrl).subscribe({
      next:(data)=>{
        console.log(data);
        this.actionId = data.drill_through_id;
        this.sourceSheetId = data.source_sheet_id;
      },
      error:(error)=>{
        console.log(error)
        Swal.fire({
          icon: 'error',
          title: 'oops!',
          text: error.error.message,
          width: '400px',
        })
      }
    });
  }
  updateDrillThroughAction(){
    const Obj = {
      drill_through_id:this.actionId,
      action_name: this.actionName,
      queryset_id: this.drillThroughQuerySetId,
      dashboard_id: this.dashboardId,
      main_sheet_id: this.sourceSheetId,
      target_sheet_ids: this.targetSheetIds,
      hierarchy_id: this.selectedDbIdForFilter
    }
    this.workbechService.updateDrillThroughAction(Obj).subscribe({
      next: (data) => {
        console.log(data);
        this.actionId = data.action_id;
        this.actionName = '';
        this.drillThroughQuerySetId = [];
        this.sourceSheetId = 0;
        this.isAllTargetSheetsSelected = false;
        this.targetSheetList.forEach((sheet:any)=>{
          sheet.selected = false;
        });
        this.targetSheetIds = [];
        this.getDrillThroughActionList();
        this.clearActionForm();
        this.editActions = false;
        this.toasterService.success('Action Updated Successfully', 'success', { positionClass: 'toast-top-center' })
      },
      error: (error) => {
        console.log(error)
        this.toasterService.error(error.error.message, 'error', { positionClass: 'toast-center-center' })
      }
    })
  }
  deleteDashboardAction(actionId : any){
    let object = {
      id : actionId
    }
    this.workbechService.deleteDrillThroughAction(object).subscribe({
      next: (data) => {
        console.log(data);
        this.getDrillThroughActionList();
        this.actionId = '';
        this.clearActionForm();
        this.editActions = false;
        this.toasterService.success('Action Deleted Successfully', 'Success', { positionClass: 'toast-top-center' });
        this.resetDrillThroughOnActionDelete(this.dashboardId, data.sheet_ids);
      },
      error: (error) => {
        console.log(error)
        this.toasterService.error(error.error.message, 'error', { positionClass: 'toast-center-center' })
      }
    });
  }
  clearActionForm(){
    if(this.actionId && this.actionId != 0){
      this.setDrillThrough('',[]);
    }
    this.actionName = '';
    this.drillThroughQuerySetId = [];
    this.sourceSheetId = 0;
    this.isAllTargetSheetsSelected = false;
    this.targetSheetList.forEach((sheet: any) => {
      sheet.selected = false;
    });
    this.targetSheetIds = [];
    this.sourceSheetList = [];
    this.targetSheetList = [];
    this.actionId = '';
    this.drillThroughDatabaseName = '';
  }
  setDrillThrough(selectedValue : any, item : any){
    let selectedXValue;
    let columnNames : any[] = [];
    let dataTypes: any[] = [];
    if(selectedValue == ''){
      selectedXValue = selectedValue.trim() ? selectedValue.split(',').map((item: string) => [item.trim()]) : [];
    }
    else{
      selectedXValue = selectedValue.split(',').map((item : any) => [item]);
      item.column_Data.forEach((col: any) => {
        columnNames.push(col[0]);
        dataTypes.push(col[1]);
      });
    }

    let object = {
      drill_id: this.actionId,
      dashboard_id: this.dashboardId,
      column_name: columnNames,
      column_data: selectedXValue,
      datatype: dataTypes
    }
    console.log(item);
    console.log('payload',object);

    this.workbechService.getDrillThroughData(object, this.isPublicUrl).subscribe({
      next: (data) => {
        console.log(data);
        data.forEach((sheet:any)=>{
          if(sheet.columns.length > 0) {
            sheet.columns.forEach((col:any)=>{
              let colObject = {
                name: col.column,
                values: col.result
              }
              this.filteredColumnData.push(colObject);
              console.log('filtercolumn', this.filteredColumnData);
            });
          } else {
            let colObject = {
              name: '',
              values: []
            }
            this.filteredColumnData.push(colObject)
          }

          if(sheet.rows.length > 0){
            sheet.rows.forEach((row:any)=>{
              let rowObject = {
                name: row.column,
                data: row.result
              }
              this.filteredRowData.push(rowObject);
              console.log('filterowData', this.filteredRowData);
            });
          } else {
            let rowObject = {
              name: '',
              data: []
            }
            this.filteredRowData.push(rowObject);
          }
          this.setDashboardSheetData(item,false,false, false,true,sheet.sheet_id, false,0);
        });
      },
      error: (error) => {
        console.log(error)
        Swal.fire({
          icon: 'error',
          title: 'oops!',
          text: error.error.message,
          width: '400px',
        })
      }
    });
  }
  actionUpdateOnSheetRemove(sheetId : any){
    let object = {
      sheet_id : sheetId,
      dashboard_id : this.dashboardId
    }
    this.workbechService.actionUpdateOnSheetRemove(object).subscribe({
      next: (data) => {
        console.log(data);
        this.getDrillThroughActionList();
        this.toasterService.info(data.message,'info',{ positionClass: 'toast-top-center'})
      },
      error: (error) => {
        console.log(error)
        this.toasterService.error(error.error.message, 'error', { positionClass: 'toast-top-right' })
      }
    });
  }
  resetDrillThroughOnActionDelete(dahboardId : any, sheetIds : any){
    let object = {
      dashboard_id : dahboardId,
      sheets_ids : sheetIds
    }
    this.workbechService.resetDrillThroughOnActionDelete(object).subscribe({
      next: (data) => {
        console.log(data);
        this.getDrillThroughActionList();
        data.forEach((sheet:any)=>{
          sheet.columns.forEach((col:any)=>{
            let colObject = {
              name: col.column,
              values: col.result
            }
            this.filteredColumnData.push(colObject);
            console.log('filtercolumn', this.filteredColumnData);
          });
          sheet.rows.forEach((row:any)=>{
            let rowObject = {
              name: row.column,
              data: row.result
            }
            this.filteredRowData.push(rowObject);
            console.log('filterowData', this.filteredRowData);
          });
          this.setDashboardSheetData([],false,false, false,true,sheet.sheet_id, false,0);
        });
      },
      error: (error) => {
        console.log(error)
        this.toasterService.error(error.error.message, 'error', { positionClass: 'toast-top-right' })
      }
    })
  }
  onEChartClick(event : any, item : any){
    if(this.actionId && item.sheetId === this.sourceSheetId){
      if(item.chartId == '11'){
        this.setDrillThrough(event.value[0], item);
      }
      else if(item.chartId == '12'){
        const clickedValues = event.data.value; // Get the values for the clicked data
        const clickedIndex = clickedValues.indexOf(event.value); // Identify the index
        const clickedIndicatorName = item.chartOptions.radar.indicator[clickedIndex]?.name;
        this.setDrillThrough(clickedIndicatorName, item);
      }
      else{
        this.setDrillThrough(event.name, item);
      }
      // this.setDrillThrough(event.name, item);
      const clickedValue = event.value;  // Value of the clicked data point
      const clickedCategory = event.name;  // X-axis name or category name
      const clickedSeries = event.seriesName;  // Series name (if defined)

      // Log the details
      console.log('Value:', clickedValue);
      console.log('Category:', clickedCategory);
      console.log('Series Name:', clickedSeries);
    }
    if (item.drillDownIndex < item.drillDownHierarchy?.length - 1) {
      // const selectedXValue = element.chartOptions.series[0].data[config.dataPointIndex];
      console.log('X-axis value:', event.name);
      let nestedKey = item.drillDownHierarchy[item.drillDownIndex];
      item.drillDownIndex++;
      let obj = { [nestedKey]: event.name };
      item.drillDownObject.push(obj);
      if(this.isPublicUrl){
        this.publicDataExtraction(item);
      }
      else{
        this.dataExtraction(item);
      }
    }
  }
  chartType : string = '';
  chartsColumnData : any[] = [];
  chartsRowData :  any[] = [];
  dualAxisRowData : any = [];
  dualAxisColumnData : any = [];
  mapchartDrillDown(event: any, item : any) {
    item.drillDownIndex = event.drillDownIndex;
    item.drillDownHierarchy = event.draggedDrillDownColumns;
    item.drillDownObject = event.drillDownObject;
    if(this.isPublicUrl){
      this.publicDataExtraction(item);
    }
    else{
      this.dataExtraction(item);
    }
    
  }


	   
	   // image upload inn sheets
     uploadedImage: any;
     imageTitle:any;
     fileName: string = 'No file chosen';
     triggerFileUpload() {
       const fileInput = document.getElementById('imageUpload') as HTMLElement;
       fileInput.click();
     }
     
     // Handle image selection
     onImageSelected(event: any) {
       const file = event.target.files[0];
       if (file) {
        if (!file.type.startsWith('image/')) {
         this.toasterService.error('Not a supported file format. Please select an image file.','info',{ positionClass: 'toast-top-center'})
          event.target.value = ''; // Reset file input
          this.fileName = 'No file chosen';
          return;
        }else{
         const reader = new FileReader();
         reader.onload = (e: any) => {
           this.uploadedImage = e.target.result; // Image data as Base64
           console.log('Uploaded Image:', this.uploadedImage);
         };
         reader.readAsDataURL(file);
         this.fileName = file.name; 
        }
       }else{
        this.fileName = 'No file chosen'; 
       }
     }
     uploadInJson(){
      if (this.uploadedImage) {
        let element :any= {
          id: uuidv4(), 
          x: 10,
          y: 20,
          rows: 2,
          cols: 2, 
          type: 'image', 
          imageData: this.uploadedImage, // Store Base64 image data
          imageTitle:this.imageTitle
        };
        this.dashboard.push(element);
        console.log('Updated Dashboard:', this.dashboard);
        this.canNavigateToAnotherPage = true;
        const fileInput = document.getElementById('imageUpload') as HTMLInputElement;
        if (fileInput) {
          fileInput.value = '';
          this.imageTitle = '';
          this.uploadedImage = null;
          this.fileName = 'No file chosen'; 
          this.imageUpload.nativeElement.value = '';
      }
      }
     }
     kpiItem:any;
     uploadedKpiImage:any;
     uploadKpiImage(item:any){
      this.ImageUploadKPI.nativeElement.click();
      this.kpiItem=item;
     }
     imageFileSelectEvent(event:any){
      const file = event.target.files[0];
       if (file) {
        if (!file.type.startsWith('image/')) {
          this.toasterService.error('Not a supported file format. Please select an image file.','info',{ positionClass: 'toast-top-center'})
          event.target.value = ''; // Reset file input
          return;
        }else{
         const reader = new FileReader();
         reader.onload = (e: any) => {
           this.uploadedKpiImage = e.target.result; 
           console.log('Uploaded Image:', this.uploadedKpiImage);
           if(this.uploadedKpiImage){
            this.updateKPIImage(this.kpiItem, this.uploadedKpiImage);
            }
         };
         reader.readAsDataURL(file);
        }
       }
     }
     updateKPIImage(item:any,KpiImage:any){
      const itemIndex = this.dashboard.findIndex((d) => d['id'] === item.id);
      if (itemIndex !== -1) {
        // const item1 = this.dashboard[itemIndex];
        if (item['kpiImage']) {
          // Add the kpiImage key to kpiData
          this.dashboard[itemIndex] = {
            ...item,
            kpiImage: KpiImage,
          };
       
        } else {
          this.dashboard[itemIndex] = {
            ...item,
            kpiImage: KpiImage,
          };    
        }
        console.log('addedKpiImage',this.dashboard);
        this.canNavigateToAnotherPage = true;
      } else {
        console.error('Item not found in dashboard:', item);
      } 
     }
     removeKpiImage(item: any): void {
      const itemIndex = this.dashboard.findIndex((d) => d['id'] === item.id);
      if (itemIndex !== -1) {
        const updatedItem = {
          ...this.dashboard[itemIndex],
          kpiImage: { ...this.dashboard[itemIndex]['kpiImage'] },
        };
  
        // Delete kpiImage key if it exists
        delete updatedItem.kpiImage;
  
        // Update the dashboard array
        this.dashboard[itemIndex] = updatedItem;
        this.canNavigateToAnotherPage = true;
      } else {
        console.error('Item not found in dashboard:', item);
      }
    }

    canNavigate(): boolean {
      return this.canNavigateToAnotherPage;
    }
    canNavigateToAnotherPage = false;
    dashboardNotSaveAlert(): Promise<boolean> {
      this.loaderService.hide();
      return Swal.fire({
        position: "center",
        icon: "warning",
        title: "Your work has not been saved, Do you want to continue?",
        showConfirmButton: true,
        showCancelButton: true, // Add a "No" button
        confirmButtonText: 'Yes', // Text for "Yes" button
        cancelButtonText: 'No',   // Text for "No" button
      }).then((result) => {
        if (result.isConfirmed) {
          // User clicked "Yes", allow navigation
          this.loaderService.show();
          return true;
        } else {
          // User clicked "No", prevent navigation
          this.loaderService.hide();
          return false;
        }
      });
    }
    selectedIcon: string | null = null;
    searchText: string = ''; // Search input value
    KpiIconItem:any;
    selectedIconFontSize: string = '24'; // Default size
    selectedIconColor: string = '#888'; // Default color
    selectedIconPosition: string = 'bottom-right';
    selectIcon(icon: any) {
      console.log('Selected Icon:', icon);
      this.selectedIcon = `${icon.styles[0]} fa-${icon.name}`;

    
    }
    changeSize(event:any): void {
      const size = event.target.value;
      this.selectedIconFontSize = `${size}`;
      console.log('kpiSize',this.selectedIconFontSize)
    }
  
    changeColor(event:any): void {
      const color = event.target.value;
      this.selectedIconColor = color;
      console.log('kpiColor',this.selectedIconColor)
    }
    positions = [
      { value: 'top-left', iconClass: 'dollar-top-left' },
      { value: 'top-middle', iconClass: 'dollar-top-center' },
      { value: 'top-right', iconClass: 'dollar-top-right' },
      { value: 'left-middle', iconClass: 'dollar-center-left' },
      { value: 'center', iconClass: '' },
      { value: 'right-middle', iconClass: 'dollar-center-right' },
      { value: 'bottom-left', iconClass: 'dollar-bottom-left' },
      { value: 'bottom-middle', iconClass: 'dollar-bottom-center' },
      { value: 'bottom-right', iconClass: 'dollar-bottom-right' }
    ];
    selectPosition(position: string): void {
      this.selectedIconPosition = position;
      console.log('kpiPosition',this.selectedIconPosition)
    }
    applyIconInKpi(){
      const itemIndex = this.dashboard.findIndex((d) => d['id'] === this.KpiIconItem.id);
      if (itemIndex !== -1) {
        if (!this.KpiIconItem.kpiIconsArray) {
          this.KpiIconItem.kpiIconsArray = {};
        }
            const newIconObject = {
          kpiIcon: this.selectedIcon,
          kpiIconSize: this.selectedIconFontSize,
          kpiIconColor: this.selectedIconColor,
          kpiIconPosition: this.selectedIconPosition
        };
        this.KpiIconItem.kpiIconsArray = newIconObject;
            this.dashboard[itemIndex] = { 
          ...this.KpiIconItem 
        };
    
        this.modalService.dismissAll();
        console.log('Updated kpiIconsArray:', this.dashboard);
        this.canNavigateToAnotherPage = true;
        this.selectedIcon = null;
      } else {
        console.error('Item not found in dashboard:', this.KpiIconItem);
      }
    
    }

    getIconPositionStyles(position: string) {
      let styles = {};
      const offset = '10px'; // Distance from the edges
      switch (position) {
          case 'top-left':
            return { top: offset, left: offset, transform: 'none' };
          case 'top-middle':
            return { top: offset, left: '50%', transform: 'translateX(-50%)' };
          case 'top-right':
            return { top: offset, right: offset, transform: 'none' };
          case 'left-middle':
            return { top: '50%', left: offset, transform: 'translateY(-50%)' };
          case 'center':
            return { top: '50%', left: '50%', transform: 'translate(-50%, -50%)' };
          case 'right-middle':
            return { top: '50%', right: offset, transform: 'translateY(-50%)' };
          case 'bottom-left':
            return { bottom: offset, left: offset, transform: 'none' };
          case 'bottom-middle':
            return { bottom: offset, left: '50%', transform: 'translateX(-50%)' };
          case 'bottom-right':
            return { bottom: offset, right: offset, transform: 'none' };
        default:
          styles = { bottom: '0', right: '0' }; 
          break;
      }
    
      return styles;
    }
    getIconClass(icon: any): string {
      return `${icon.styles[0]} fa-${icon.name}`; 
    }
    priorityIcons: string[] = ['arrow-trend-up','arrow-trend-down','house','magnifying-glass','user','facebook','check','download','twitter','instagram','envelope','linkedin','arrow-up','file','calendar-days','circle-down','address-book','handshake','layer-group','users','link','sack-dollar'
    ];; 
  filteredIcons: any[] = [];
  showAll: boolean = false; 

  updateFilteredIcons(): void {
    const searchFilter = this.iconList.filter(
      (icon) =>
        !this.searchText ||
        icon.name.toLowerCase().includes(this.searchText.toLowerCase()) ||
        icon.label.toLowerCase().includes(this.searchText.toLowerCase())
    );

    this.filteredIcons = this.showAll
      ? searchFilter 
      : searchFilter.filter((icon) => this.priorityIcons.includes(icon.name)); 
  }
  toggleShowAll(): void {
    this.showAll = !this.showAll;
    this.updateFilteredIcons();
  }
  editKpiIcon(iconModal:any,item:any){
    this.modalService.open(iconModal, {
      centered: true,
      windowClass: 'animate__animated animate__zoomIn',
    });
    this.KpiIconItem = item;
    console.log('editKpi',item);
    const kpiIconsArray = item.kpiIconsArray
    this.selectedIconColor = kpiIconsArray.kpiIconColor ?? '#888'
    this.selectedIconFontSize = kpiIconsArray.kpiIconSize ?? '24'
    this.selectedIconPosition = kpiIconsArray.kpiIconPosition ?? 'bottom-right'
    this.selectedIcon = kpiIconsArray.kpiIcon ?? null
 
  }
  removeKpiIcon(item: any): void {
    const itemIndex = this.dashboard.findIndex((d) => d['id'] === item.id);
    if (itemIndex !== -1) {
      const updatedItem = {
        ...this.dashboard[itemIndex],
        kpiIconsArray: { ...this.dashboard[itemIndex]['kpiIconsArray'] },
      };

      // Delete kpiIcon key if it exists
      delete updatedItem.kpiIconsArray.kpiIcon;
      delete updatedItem.kpiIconsArray.kpiIconPosition;
      delete updatedItem.kpiIconsArray.kpiIconColor;
      delete updatedItem.kpiIconsArray.kpiIconSize;
      // Update the dashboard array
      this.dashboard[itemIndex] = updatedItem;
      this.canNavigateToAnotherPage = true;
      this.deselectIconChanges()
    } else {
      console.error('Item not found in dashboard:', item);
    }
  }
  deselectIconChanges(){
    this.selectedIcon = null;
      this.selectedIconColor = '#888';
      this.selectedIconFontSize = '24';
      this.selectedIconPosition = 'bottom-right';
  }
  isCustomizeVisible: boolean = true; // Controls visibility
  toggleCustomize(): void {
    this.isCustomizeVisible = !this.isCustomizeVisible;
  }
    // selectIcon(icon: { class: string; name: string }) {
    //   this.selectedIcon = icon.class;
    //   console.log('Selected Icon:', icon);
    //   // Close the modal or perform other actions here
    // }
    sheetFilters : any[] = [];
    // [{sheet_id:10924,is_filter_applied:true,filter_count:3}];
    refreshDashboard(){
      let object ={
        "dashboard_id": this.dashboardId
      }
      this.workbechService.refreshDashboardData(object).subscribe({
        next:(data)=>{
          console.log(data);
          data.forEach((item: any,index:any) => {
          this.filteredRowData = [];
          this.filteredColumnData = [];
          this.tablePreviewColumn.push(item.columns);
          this.tablePreviewRow.push(item.rows);
          item.columns.forEach((res:any) => {      
            let obj1={
              name:res.column,
              values: res.result
            }
            this.filteredColumnData.push(obj1);
            console.log('filtercolumn',this.filteredColumnData)
          });
          item.rows.forEach((res:any) => {
            let obj={
              name: res.column,
              data: res.result
            }
            this.filteredRowData.push(obj);
            console.log('filterowData',this.filteredRowData)
          });
          if(item.chart_id === 1){
            this.pageChangeTableDisplay(item,1,true,index)
            this.tablePage=1
          }else{
          this.setDashboardSheetData(item, true , true, false, false, '',true,index);
          }
        });
          },
        error:(error)=>{
          console.log(error)
          Swal.fire({
            icon: 'error',
            title: 'oops!',
            text: error.error.message,
            width: '400px',
          })
        }
      });
    }
}
// export interface CustomGridsterItem extends GridsterItem {
//   title: string;
//   content: string;
// }