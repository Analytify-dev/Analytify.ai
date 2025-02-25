import { Component,ViewChild,NgZone, ChangeDetectionStrategy, ChangeDetectorRef, ElementRef,Input } from '@angular/core';
import { NgbModal, NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { NgSelectModule } from '@ng-select/ng-select';
import { SharedModule } from '../../../shared/sharedmodule';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { WorkbenchService } from '../../workbench/workbench.service';
import {
  CdkDragDrop,
  CdkDrag,
  CdkDropList,
  CdkDropListGroup,
  moveItemInArray,
  transferArrayItem,
} from '@angular/cdk/drag-drop';
import * as d3 from 'd3';
import * as _ from 'lodash';
import type { EChartsOption } from 'echarts';
import { NgApexchartsModule,ChartComponent } from 'ng-apexcharts';
import {FormControl} from '@angular/forms';
import {MatTabChangeEvent, MatTabsModule} from '@angular/material/tabs';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { ActivatedRoute, Router } from '@angular/router';
import Swal from 'sweetalert2';
import { NgxColorsModule } from 'ngx-colors';
import { CommonModule } from '@angular/common';
import { CKEditorModule } from '@ckeditor/ckeditor5-angular';
import { ClassicEditor, Bold, Essentials, Italic, Mention, Paragraph, Undo, Font, Alignment, FontFamily, Underline, Subscript, Superscript, RemoveFormat, SelectAll, Heading, FontSize } from 'ckeditor5';
import 'ckeditor5/ckeditor5.css';
import * as echarts from 'echarts';
import { NgxEchartsModule, NGX_ECHARTS_CONFIG } from 'ngx-echarts';
import { InsightsButtonComponent } from '../insights-button/insights-button.component';
import { DomSanitizer } from '@angular/platform-browser';
import { NgxSliderModule } from '@angular-slider/ngx-slider';
import { Options } from '@angular-slider/ngx-slider';
import { ViewTemplateDrivenService } from '../view-template-driven.service';
import { ToastrService } from 'ngx-toastr';
// import { series } from '../../charts/apexcharts/data';
import { NgxPaginationModule } from 'ngx-pagination';
import { LoaderService } from '../../../shared/services/loader.service';
import { HttpClient } from '@angular/common/http';
import { MatTooltipModule } from '@angular/material/tooltip'; // Import the MatTooltipModule
import { fontWeight } from 'html2canvas/dist/types/css/property-descriptors/font-weight';
import { COLOR_PALETTE } from '../../../shared/models/color-palette.model';
import { fontFamily } from 'html2canvas/dist/types/css/property-descriptors/font-family';
import { lastValueFrom, Subscription, timer } from 'rxjs';
import { evaluate, parse } from 'mathjs';
import { InsightApexComponent } from '../insight-apex/insight-apex.component';
import { InsightEchartComponent } from '../insight-echart/insight-echart.component';
import { SharedService } from '../../../shared/services/shared.service';
import { DefaultColorPickerService } from '../../../services/default-color-picker.service';
import { FormatMeasurePipe } from '../../../shared/pipes/format-measure.pipe';
// import $ from 'jquery';
import 'pivottable';
// import * as $ from 'jquery';
import 'jquery-ui/ui/widgets/sortable';
declare type HorizontalAlign = 'left' | 'center' | 'right';
declare type VerticalAlign = 'top' | 'center' | 'bottom';
declare type MixedAlign = 'left' | 'right' | 'top' | 'bottom' | 'center';
interface TableRow {
  [key: string]: any;
}
interface Dimension {
  name: string;
  values: string[];
}
interface RangeSliderModel {
  minValue: number;
  maxValue: number;
  options: Options;
}
declare global {
  interface JQuery {
    sortable(): JQuery;
  }
}

declare var $:any;

@Component({
  selector: 'app-sheets',
  standalone: true,
  // changeDetection: ChangeDetectionStrategy.OnPush,
  providers: [
    {
      provide: NGX_ECHARTS_CONFIG,
      useFactory: () => ({ echarts: echarts }),
    },
  ],
  imports: [SharedModule, NgxEchartsModule, NgSelectModule,NgbModule,FormsModule,ReactiveFormsModule,MatIconModule,NgxColorsModule,
    CdkDropListGroup, CdkDropList,CommonModule, CdkDrag,NgApexchartsModule,MatTabsModule,MatFormFieldModule,MatInputModule,CKEditorModule,
    InsightsButtonComponent,NgxSliderModule,NgxPaginationModule,MatTooltipModule,InsightApexComponent,InsightEchartComponent,FormatMeasurePipe],
  templateUrl: './sheets.component.html',
  styleUrl: './sheets.component.scss'
})
export class SheetsComponent {
  tableColumnsData = [] as any;
  draggedtables = [] as any;
  draggedColumns = [] as any;
  draggedRows = [] as any;
  dimentions = [] as any;
  measurments = [] as any;
  columnData = [] as any;
  isExclude: boolean = false;
  rowData = [] as any;
  tableName: any;
  schemaName: any;
  table_alias: any;
  draggedColumnsData = [] as any;
  mulColData = [] as any;
  mulRowData = [] as any;
  pivotMeasureValues = [] as any;
  draggedRowsData = [] as any;
  tablePreviewColumn = [] as any;
  tablePreviewRow = [] as any;
  tableDataStore: TableRow[] = [];  
  storeTableRow = [] as any;
  storeTableColumn = [] as any;
  displayedColumns: string[] = [];
  chartEnable = true;
  dimensionExpand = false;
  chartSuggestions: any = null;
  errorMessage : any;
  errorMessage1:any;
  userPrompt: string = '';
  selectedChartPlugin : string = '';	
  isApexCharts : boolean = true;
  isEChatrts : boolean = false;
  isZoom : boolean = false;
  xLabelFontSize : number = 12;
  yLabelFontSize : number = 12;
  xLabelFontFamily : string = 'sans-serif';
  yLabelFontFamily : string = 'sans-serif';
  xlabelFontWeight : number = 400;
  ylabelFontWeight : number = 400;
  xLabelColor : string = '#2392c1';
  xGridColor : string = '#2392c1';
  yLabelColor : string = '#2392c1';
  yGridColor : string = '#2392c1';
  filterSearch! : string;
  editFilterSearch! : string;
  tableSearch! : string;
  isMeasureEdit : boolean = false;
  calculatedFieldName! : string
  isEditCalculatedField : boolean = false;
 /* private data = [
    {"Framework": "Vue", "Stars": "166443", "Released": "2014"},
    {"Framework": "React", "Stars": "150793", "Released": "2013"},
    {"Framework": "Angular", "Stars": "62342", "Released": "2016"},
    {"Framework": "Backbone", "Stars": "27647", "Released": "2010"},
    {"Framework": "Ember", "Stars": "21471", "Released": "2011"},
  ];*/

  //Bar
  public svg: any;
  public margin = 50;
  public width = 750 - (this.margin * 2);
  public height = 350 - (this.margin * 2);
  //Pie
  public widthPie = 600;
  public heightPie = 300;
  // The radius of the pie chart is half the smallest side
  public radius = Math.min(this.width, this.height) / 2 - this.margin;
  public colors:any;
  chartsColumnData = [] as any;
  chartsRowData = [] as any;
  public lineChartOptions!: Partial<EChartsOption>;
  chartOptions:any;
  chartOptions1:any;
  sheetNumber: number = 1;
  sheetName = "Sheet 1";
  sheetTitle = "Sheet ";
  sheetTagName = "";
  databaseId:any;
  fileId:any;
  qrySetId:any;
  chartId = 1;
  sheetResponce = [] as any;
  SheetIndex = 0;
  dimetionMeasure = [] as any;
  filterValues:any;
  filterId = [] as any;
  dualAxisRowData = [] as any;
  measureValue:any;
  retriveDataSheet_id: any;
  sheetfilter_querysets_id = null;
  editFilterId: any;
  isValuePresent: any;
  color = '#2392c1';
  database_name: any;
  dualAxisColumnData = [] as any;
  filterQuerySetId: any;
  measureValues = [] as any;
  SheetSavePlusEnabled = ['Sheet 1'];
  oldColumn: any;
  newColumn: any;
  selectedTabIndex: any;
  isAllSelected: boolean = false;
  active=1;
  activeTabId = 1;
  fromFileId=false;
  sheetsDashboard : boolean = false;
  sheetList : any [] = [];
  dashboardId : any;
  selectedDashboardId : any = 0;
  GridColor : any = '#089ffc';
  // apexbBgColor : any = '#fcfcfc';
  dateValue : any = "-Select-";
  Editor = ClassicEditor;
  editor : boolean = false;
  bandingSwitch: boolean = false; 
  legendSwitch: boolean = true;
  xLabelSwitch: boolean = true;
  yLabelSwitch: boolean = true;
  xGridSwitch: boolean = false; 
  yGridSwitch: boolean = false;
  numberPopup : boolean = false;
  decimalPlaces: number = 2;
  displayUnits: string = 'none';
  prefix: string = '';
  suffix: string = '';
  KPIDecimalPlaces: number = 2;
  KPIRoundPlaces: number = 0;
  KPIDisplayUnits: string = 'none';
  KPIPrefix: string = '';
  KPISuffix: string = '';
  KPIPercentageDivisor : number = 100;
  isCustomSql = false;
  canDrop = true;
  createdBy : any;
  calculatedFieldFunction : string = '';
  nestedCalculatedFieldData : string = '';

  radar: boolean = false;
  radarRowData: any = [];
  xlabelAlignment  = 'left';
  ylabelAlignment : VerticalAlign = 'center';
  dataLabelAlignment : MixedAlign = 'top';
  backgroundColor: string = '#fff';
  canEditDb = false;
  draggedDrillDownColumns = [] as any;
  draggedMeasureValues = [] as any;
  drillDownIndex : number = 0;
  originalData : any ;
  dateDrillDownSwitch : boolean = false;
  drillDownObject: any[] = [];
  sheetCustomQuery: any;
  KPINumber: any;

  tableDataDisplay: TableRow[] = [];
  tableColumnsDisplay: string[] = [];
  tableRowDisplayPreview = [] as any;
  tableColumnDisplayPreview = [] as any;

  itemsPerPage!:number;
  pageNo = 1;
  page: number = 1;
  totalItems:any;
  tableChartSearch:any;

  tablePaginationCustomQuery:any;
  tablePaginationColumn =[] as any;
  tablePaginationRows =[] as any;

  guagechartRowData:any;
  minValueGuage: number = 0; // Default minimum value
  maxValueGuage: number = 100; // Default maximum value
  map: boolean = false;

  guageNumber:any;
  eFunnelChartOptions: any;
  valueToDivide:any;

  barColor : any = '#4382f7';
  lineColor : any = '#38ff98';
  dataLabels:boolean = true;
  label : boolean = true;
  isDistributed : boolean = true;
  kpiFontSize: string = '3';
  kpiColor: string = '#000000';

  titleShow : boolean = true;
  legendsAllignment : any = 'bottom'
  donutSize:any = 50;
  color1:any;
  color2:any;

  isBold:boolean = false;
  isItalic:boolean = false;
  isUnderline:boolean = false;
  isXlabelBold:boolean = false;
  isYlabelBold:boolean = false;
  isTableHeaderBold:boolean = false;
  isTableDataBold:boolean = false;

  backgroundColorSwitch : boolean = false;
  chartColorSwitch : boolean = false;
  barColorSwitch : boolean = false;
  lineColorSwitch : boolean = false;
  gridLineColorSwitch : boolean = false;
  xLabelColorSwitch : boolean = false;
  xGridLineColorSwitch : boolean = false;
  yLabelColorSwitch : boolean = false;
  yGridLineColorSwitch : boolean = false;
  bandingColorSwitch : boolean = false;
  kpiColorSwitch : boolean = false;
  funnelColorSwitch : boolean = false;

  dataLabelsFontFamily : string = 'sans-serif';
  dataLabelsFontSize : any = '12px';
  dataLabelsFontPosition : any = 'top';
  dataLabelsBarFontPosition : any = 'top';
  dataLabelsLineFontPosition : any = 'top';
  measureAlignment : any = 'center';
  dimensionAlignment : any = 'center';
  colorPalette = COLOR_PALETTE;
  dimensionColor = '#2392c1';
  measureColor = '#2392c1';
  dataLabelsColor = '#2392c1';  isValidCalculatedField! : boolean;
  validationMessage: string = '';
  calculatedFieldId: any;
  calculatedFieldLogic! : string ;
  columnMapping: { [key: string]: string } = {};
  filterCalculatedFieldLogic: any = '';

  tableDataFontFamily : string = 'sans-serif';
  tableDataFontSize : any = '12px';
  tableDataFontWeight : any = 400;
  tableDataFontStyle : any = 'normal';
  tableDataFontDecoration : any = 'none';
  tableDataFontColor : any = '#000000';
  tableDataFontAlignment : any = 'left';

  headerFontFamily : any = "'Arial', sans-serif";
  headerFontSize : any = '16px';
  headerFontWeight : any = 700;
  headerFontStyle : any = 'normal';
  headerFontDecoration : any = 'none';
  headerFontColor : any = '#000000'
  headerFontAlignment : any = 'left';
  topLegend:any = null;
  leftLegend:any = 'center';
  legendOrient:any = 'horizontal'
  bottomLegend:any = '0%'
  rightLegend:any = null;
  sortType : any = 0;

  locationDrillDownSwitch: boolean = false;
  locationHeirarchyFieldList: string[] = ['country', 'state', 'city'];
  locationHeirarchyList: string[] = ['country', 'state', 'city'];
  isLocationFeild: boolean = false;
  @ViewChild('pivotTableContainer', { static: false }) pivotContainer!: ElementRef;
  transformedData: any[] = [];
  columnKeys: string[] = [];
  rowKeys: string[] = [];
  valueKeys: string[] = [];
  rawData: any = {};
  
  colorSchemes = [
    ['#00d1c1', '#30e0cf', '#48efde', '#5dfeee', '#fee74f', '#feda40', '#fecd31', '#fec01e', '#feb300'], // Example gradient 1
    ['#67001F', '#B2182B', '#D6604D', '#F4A582', '#FDDBC7', '#D1E5F0', '#92C5DE', '#4393C3', '#2166AC'], // Example gradient 2
    ['#FFFF19', '#FFFF13', '#FFFF0A', '##FFFF00', '#FFC100', '#FF7D00', '#FF0000', '#C30000', '#8A0000'], // Example gradient 3
    ['#FFFFFF', '#DFDFDF', '#C0C0C0', '#A2A2A2', '#858585', '#4E4E4E', '#353535', '#1E1E1E', '#000000'], // Example gradient 4
    ['#E70B81', '#F1609A', '#F890B5', '#FCBCD0', '#FCE5EC', '#C6C6C6', '#A5A5A5', '#858585', '#666666'], // Example gradient 4
  ];
  selectedColorScheme=[] as  any;
  heirarchyColumnData : any [] = [];

  constructor(private workbechService:WorkbenchService,private route:ActivatedRoute,private modalService: NgbModal,private router:Router,private zone: NgZone, private sanitizer: DomSanitizer,private cdr: ChangeDetectorRef,
    private templateService:ViewTemplateDrivenService,private toasterService:ToastrService,private loaderService:LoaderService, private http: HttpClient, private colorService : DefaultColorPickerService,private sharedService: SharedService){   
    if(this.router.url.includes('/analytify/sheets')){
      if (route.snapshot.params['id1'] && route.snapshot.params['id2']&& route.snapshot.params['id3'] ) {
        this.databaseId = +atob(route.snapshot.params['id1']);
        this.qrySetId = +atob(route.snapshot.params['id2']);
        this.filterQuerySetId = atob(route.snapshot.params['id3'])
          // this.tabs[0] = this.sheetName;
          this.sheetTagName = this.sheetName;
        if(this.filterQuerySetId==='null'){
          console.log('filterqrysetid',this.filterQuerySetId)
          this.filterQuerySetId = null
        }
        else{
            parseInt(this.filterQuerySetId)
            console.log(this.filterQuerySetId)
          }
        }
     }
  //    if(this.router.url.includes('/analytify/sheets/fileId')){
  //     if (route.snapshot.params['id1'] && route.snapshot.params['id2']&& route.snapshot.params['id3'] ) {
  //       this.fileId = +atob(route.snapshot.params['id1']);
  //       this.qrySetId = +atob(route.snapshot.params['id2']);
  //       this.filterQuerySetId = atob(route.snapshot.params['id3']);
  //       // this.tabs[0] = this.sheetName;
  //       this.sheetTagName = this.sheetName;
  //       this.fromFileId = true;
  //       if(this.filterQuerySetId==='null'){
  //         console.log('filterqrysetid',this.filterQuerySetId)
  //         this.filterQuerySetId = null
  //       }
  //       else{
  //           parseInt(this.filterQuerySetId)
  //           console.log(this.filterQuerySetId)
  //         }
  //       }      
  // }
  // if(this.router.url.includes('/insights/home/sheets/')){ //old landing page to sheet 
  //   console.log("landing page")
  //   if (route.snapshot.params['id1'] && route.snapshot.params['id2'] && route.snapshot.params['id3']) {
  //     this.databaseId = +atob(route.snapshot.params['id1']);
  //     this.qrySetId = +atob(route.snapshot.params['id2'])
  //     this.retriveDataSheet_id = +atob(route.snapshot.params['id3'])
  //     console.log(this.retriveDataSheet_id);
  //     //this.tabs[0] = this.sheetName;
  //     // this.sheetRetrive();
  //     }
  //  }
  if(this.router.url.includes('/analytify/home/sheets/')){
    if (route.snapshot.params['id1'] && route.snapshot.params['id2'] && route.snapshot.params['id3']) {
      this.databaseId = +atob(route.snapshot.params['id1']);
      this.qrySetId = +atob(route.snapshot.params['id2'])
      this.retriveDataSheet_id = +atob(route.snapshot.params['id3'])
      console.log(this.retriveDataSheet_id);
      //this.tabs[0] = this.sheetName;
      // this.sheetRetrive();
      }
   }
  //  if(this.router.url.includes('/analytify/home/fileId/sheets/')){
  //   this.fromFileId = true;
  //   if (route.snapshot.params['id1'] && route.snapshot.params['id2'] && route.snapshot.params['id3']) {
  //     this.fileId = +atob(route.snapshot.params['id1']);
  //     this.qrySetId = +atob(route.snapshot.params['id2'])
  //     this.retriveDataSheet_id = +atob(route.snapshot.params['id3'])
  //     console.log(this.retriveDataSheet_id);
  //     //this.tabs[0] = this.sheetName;
  //     // this.sheetRetrive();
  //     }
  //  }


  //  if(this.router.url.includes('/analytify/sheetsdashboard/sheets/fileId/')){
  //   this.sheetsDashboard = true;
  //   this.fromFileId = true;
  //   console.log("landing page")
  //   if (route.snapshot.params['id1'] && route.snapshot.params['id2'] && route.snapshot.params['id3'] && route.snapshot.params['id4']) {
  //     this.fileId = +atob(route.snapshot.params['id1']);
  //     this.qrySetId = +atob(route.snapshot.params['id2']);
  //     this.retriveDataSheet_id = +atob(route.snapshot.params['id3']);
  //     this.dashboardId = +atob(route.snapshot.params['id4']);
  //     console.log(this.retriveDataSheet_id)
  //     // this.sheetRetrive();
  //     }
  //  } 
   if(this.router.url.includes('/analytify/sheetsdashboard/sheets/')){
    this.sheetsDashboard = true;
    this.fromFileId = false;
    console.log("landing page")
    if (route.snapshot.params['id1'] && route.snapshot.params['id2'] && route.snapshot.params['id3'] && route.snapshot.params['id4']) {
      this.databaseId = +atob(route.snapshot.params['id1']);
      this.qrySetId = +atob(route.snapshot.params['id2']);
      this.retriveDataSheet_id = +atob(route.snapshot.params['id3']);
      this.dashboardId = +atob(route.snapshot.params['id4']);
      console.log(this.retriveDataSheet_id)
      this.filterQuerySetId = null;
      // this.sheetRetrive();
      }
   } 
   this.canEditDb = this.templateService.addDatasource();
   this.canDrop = !this.canEditDb
  }

  rgbStringToHex(rgb: string): string {
    // Split the input string by commas, remove extra spaces, and convert to numbers
    const [r, g, b] = rgb.split(',').map((value) => parseInt(value.trim(), 10));
  
    // Ensure RGB values are within the valid range [0, 255]
    const clamp = (value: number) => Math.max(0, Math.min(255, value));
  
    // Convert RGB to HEX
    return (
      '#' +
      [clamp(r), clamp(g), clamp(b)]
        .map((x) => x.toString(16).padStart(2, '0')) // Convert to hex and pad
        .join('')
        .toUpperCase()
    );
  }

  ngOnInit(): void {
    this.loaderService.hide();
    this.columnsData();
    this.sheetTitle = this.sheetTitle +this.sheetNumber;
    this.getSheetNames();
    this.getDashboardsList();
    this.setChartType();
    // this.colorService.color$.subscribe((color) => {
    //   this.color = this.rgbStringToHex(color);
    // });
    // this.sheetRetrive();
    // this.sheetRetrive();
    const storedValue = localStorage.getItem('myValue');
    console.log('Value on init from localStorage:', storedValue);
    this.changeChartPlugin(storedValue);
  
    this.sharedService.localStorageValue$.subscribe((value: any) => {
      console.log('Value changed in Comp2:', value);
      this.changeChartPlugin(value);
    });
  }
  isColorSchemeDropdownOpen = false;
  toggleDropdownColorScheme() {
    this.isColorSchemeDropdownOpen = !this.isColorSchemeDropdownOpen;
  }
  selectColorScheme(scheme: string[]) {
    this.selectedColorScheme = scheme.slice(0, 9);
    console.log('color pallete', this.selectedColorScheme)
  }
  getGradient(colors: string[]): string {
    return `linear-gradient(to right, ${colors.join(', ')})`;
  }


 async getSheetNames():Promise<void>{
  //this.tabs = [];
  const obj={
    "server_id":this.databaseId,
    "queryset_id":this.qrySetId,
}
try {
  const response: any = await lastValueFrom(this.workbechService.getSheetNames(obj));
  console.log(response);

  if (response.data.length > 0) {
    this.sheetList = response.data;
    this.sheetNumber = this.sheetList.length + 1;
    response.data.forEach((sheet: any, index: number) => {
      this.tabs.push(sheet);
      if (sheet.id === this.retriveDataSheet_id) {
        this.selectedTabIndex = index;
      }
    });
    console.log(this.tabs);

    this.SheetSavePlusEnabled.splice(0, 1);
    console.log(this.SheetSavePlusEnabled);
  } else {
    this.SheetSavePlusEnabled.splice(0, 1);
    this.sheetNumber = 1;
    this.addSheet(false);
  }
} catch (error) {
  console.error('Error fetching sheet names:', error);
  throw error;
}
}

    

  goToDataSource(){

    if(this.isCustomSql){
      const encodeddbId = btoa(this.databaseId?.toString());
      const encodedqurysetId = btoa(this.qrySetId.toString());
      // const encodedFileId = btoa(this.fileId?.toString());

      const fromSource = 'dbId'
      const idToPass =  encodeddbId;

      if (this.filterQuerySetId === null || this.filterQuerySetId === undefined) {
        // Encode 'null' to represent a null value
       const encodedDsQuerySetId = btoa('null');
       this.router.navigate(['/analytify/database-connection/savedQuery'+'/'+idToPass+'/'+encodedqurysetId])
  
      } else {
        // Convert to string and encode
       const encodedDsQuerySetId = btoa(this.filterQuerySetId.toString());
       this.router.navigate(['/analytify/database-connection/savedQuery'+'/'+idToPass+'/'+encodedqurysetId])
    
      } 
     }
    else{
    const encodeddbId = btoa(this.databaseId?.toString());
    const encodedqurysetId = btoa(this.qrySetId.toString());
    // const encodedFileId = btoa(this.fileId?.toString());
    // this.router.navigate(['/insights/database-connection/sheets/'+encodeddbId+'/'+encodedqurysetId])

    const idToPass = encodeddbId;
    const fromSource ='dbId'
  
    if (this.filterQuerySetId === null || this.filterQuerySetId === undefined) {
      // Encode 'null' to represent a null value
     const encodedDsQuerySetId = btoa('null');
     this.router.navigate(['/analytify/database-connection/sheets'+'/'+idToPass+'/'+encodedqurysetId+'/'+encodedDsQuerySetId])

    } else {
      // Convert to string and encode
     const encodedDsQuerySetId = btoa(this.filterQuerySetId.toString());
     this.router.navigate(['/analytify/database-connection/sheets'+'/'+idToPass+'/'+encodedqurysetId+'/'+encodedDsQuerySetId])
  
    }
  }

  }
  goToConnections(){
    this.router.navigate(['/analytify/datasources/view-connections'])
  }
  toggleSubMenu(menu: any) {
    menu.expanded = !menu.expanded;
  }

 
      tableDimentions = [] as any;
      tableMeasures = [] as any;
      columnsData(){
        const obj = {
          "db_id": this.databaseId,
          "queryset_id": this.qrySetId,
          "search": this.tableSearch
        }
        this.workbechService.getColumnsData(obj).subscribe({
          next: (responce: any) => {
            console.log(responce);
            this.tableColumnsData = responce;
            this.database_name = responce[0].database_name;
            this.isCustomSql = responce[0].is_custom_sql;
            this.tableDimentions = responce.dimensions;
            this.tableMeasures = responce.measures;
          },
          error: (error) => {
            console.log(error);
          }
        }
        )
      }

      dataExtraction(){
        this.dualAxisColumnData = [];
        this.tablePreviewColumn = [];
        this.tablePreviewRow = [];
        this.storeTableRow = [];
        this.storeTableColumn = [];
        this.tableDataStore = [];
        this.displayedColumns = [];
        this.chartsColumnData = [];
        this.chartsRowData = [];
        this.dualAxisRowData = [];
        this.radarRowData = [];
        this.sortedData = [];
        let draggedColumnsObj;
        if (this.dateDrillDownSwitch && this.draggedColumnsData && this.draggedColumnsData.length > 0) {
          draggedColumnsObj = _.cloneDeep(this.draggedColumnsData);
          draggedColumnsObj[0][2] = 'year'
        } else {
          draggedColumnsObj = this.draggedColumnsData
        }
        if(!this.isTopFilter){
          this.sortColumn = 'select';
          this.sortType = 0;
        }
        if(this.draggedDrillDownColumns.length > 0 && this.heirarchyColumnData.length > 0 && this.drillDownIndex >=0 && this.selectedSortColumnData && this.selectedSortColumnData.length > 0){
          let columnsData = JSON.parse(JSON.stringify(this.heirarchyColumnData[this.drillDownIndex]));
          if(this.selectedSortColumnData[0] === this.draggedColumnsData[0][0] && this.dateDrillDownSwitch){
            this.selectedSortColumnData[0] = columnsData[0];
            this.selectedSortColumnData[1] = columnsData[1];
            this.selectedSortColumnData[2] = columnsData[2];
          }
          this.selectedSortColumnData[0] = columnsData[0];
          this.selectedSortColumnData[1] = columnsData[1];
        }
        const obj = {
          "hierarchy_id": this.databaseId,
          "queryset_id": this.qrySetId,
          "col": draggedColumnsObj,
          "row": this.draggedRowsData,
          "filter_id": this.filterId,
          "pivot_measure":this.draggedMeasureValuesData,
          "datasource_querysetid": this.filterQuerySetId,
          "sheetfilter_querysets_id": this.sheetfilter_querysets_id,
          "hierarchy": this.draggedDrillDownColumns,
          "is_date": this.dateDrillDownSwitch,
          "drill_down": this.drillDownObject,
          "next_drill_down": this.draggedDrillDownColumns[this.drillDownIndex],
          "parent_user":this.createdBy,
          "order_column":(!this.isTopFilter) ? null : this.selectedSortColumnData
        }
        this.workbechService.getDataExtraction(obj).subscribe({
          next: (responce: any) => {
            this.tablePaginationRows=responce.rows;
            this.tablePaginationColumn=responce.columns;
            this.tablePaginationCustomQuery=responce.custom_query;
            this.chartsDataSet(responce);
            this.mulColData = responce.columns;
            this.mulRowData = responce.rows;
            this.pivotMeasureValues = responce.pivot_measure;
            this.pivotColumnData = responce?.data?.col;
            this.pivotRowData = responce?.data?.row;
            this.pivotMeasureData = responce?.data?.pivot_measure;
            if (this.chartsRowData.length > 0) {
              // this.enableDisableCharts();
              // this.chartsOptionsSet();
              if (this.retriveDataSheet_id && !this.isEChatrts) {
                const dimensions: Dimension[] = this.dualAxisColumnData;
                // const categories = this.flattenDimensions(dimensions);
                // this.updateChart();
              }
              else{
                // this.chartsOptionsSet();
              }
            }
            this.chartsOptionsSet();
            this.getDimensionAndMeasures();
            this.changeSelectedColumn();
            if (((this.kpi || this.guage) && (this.draggedColumns.length > 0 || this.draggedRows.length !== 1)) || (!(this.kpi || this.guage || this.pivotTable) &&(this.draggedColumns.length < 1 || this.draggedRows.length < 1)) || (this.map && (this.draggedRows.length < 1 || this.draggedColumns.length != 1)) || (this.barLine && this.draggedRows.length !== 2) || (this.calendar && this.draggedColumnsData[0]?.[2] !== '')) {
              if(!this.table){
                this.toasterService.info('Changed to Table Chart','Info',{ positionClass: 'toast-top-right'});
              }
              this.table = true;
              this.pivotTable = false;
              this.bar = false;
              this.area = false;
              this.line = false;
              this.pie = false;
              this.sidebyside = false;
              this.stocked = false;
              this.barLine = false;
              this.horizentalStocked = false;
              this.grouped = false;
              this.multiLine = false;
              this.donut = false;
              this.chartId = 1;
              this.radar = false;
              this.kpi = false;
              this.heatMap = false;
              this.guage = false;
              this.funnel = false;
              this.calendar = false;
              this.map=false;
              // this.tableDisplayPagination();
            } else if(((this.pie || this.bar || this.area || this.line || this.donut || this.funnel || this.calendar) && (this.draggedColumns.length > 1 || this.draggedRows.length > 1))) {
              this.table = false;
              this.pivotTable = false;
              this.bar = false;
              this.area = false;
              this.line = false;
              this.pie = false;
              this.sidebyside = true;
              this.stocked = false;
              this.barLine = false;
              this.horizentalStocked = false;
              this.grouped = false;
              this.multiLine = false;
              this.donut = false;
              this.chartId = 7;
              this.radar = false;
              this.kpi = false;
              this.heatMap = false;
              this.funnel = false;
              this.guage = false;
              this.calendar = false;
              this.map = false;
              // this.sidebysideBar();
              this.resetCustomizations();
              this.chartType = 'sidebyside';
              this.toasterService.info('Changed to Dual Axis Chart','Info',{ positionClass: 'toast-top-right'});
              this.chartType = 'sidebyside'
            }
            if(this.pivotTable){
              this.pivotTableDatatransform();
            }
            if(this.table){
              this.page = 1;
              this.pageNo = 1;
              this.tableDisplayPagination();
            }
          },
          error: (error) => {
            console.log(error);
          }
        }
        )
      }

      pageChangeTableDisplay(page:any){
        this.sortedData = [];
        this.pageNo=page;
        this.tableDisplayPagination();
      }
      tableDisplayPaginationSearch(){
        this.pageNo = 1;
        this.page = 1;
        this.tableDisplayPagination();
      }
      tableDisplayPagination() {
        if (this.draggedRows.length > 0 || this.draggedColumns.length > 0) {
          const obj = {
            hierarchy_id: this.databaseId,
            sheetqueryset_id: this.sheetfilter_querysets_id,
            queryset_id: this.qrySetId,
            page_no: this.pageNo,
            page_count: this.itemsPerPage,
            search: this.tableChartSearch,
            rows: this.tablePaginationRows,
            columns: this.tablePaginationColumn,
            custom_query: this.tablePaginationCustomQuery
          }
          if (obj.search === '' || obj.search === null) {
            delete obj.search;
          }
          this.tableDataDisplay = []
          this.tableColumnsDisplay = []
          this.workbechService.tablePaginationSearch(obj).subscribe(
            {
              next: (data: any) => {
                console.log(data);
                this.itemsPerPage = data.items_per_page;
                this.totalItems = data.total_items;
                this.tableColumnDisplayPreview = data.data?.col
                this.tableRowDisplayPreview = data.data?.row

                let rowCountData: any;
                if (this.tableColumnDisplayPreview[0]?.result_data?.length) {
                  rowCountData = this.tableColumnDisplayPreview[0]?.result_data?.length;
                } else {
                  rowCountData = this.tableRowDisplayPreview[0]?.result_data?.length;
                }
                this.tableColumnsDisplay = this.tableColumnDisplayPreview.map((col: any) => col.column).concat(this.tableRowDisplayPreview.map((row: any) => row.col));

                for (let i = 0; i < rowCountData; i++) {
                  const tableRow: TableRow = {};
                  this.tableColumnDisplayPreview?.forEach((col: any) => {
                    tableRow[col.column] = col.result_data[i];
                  });
                  this.tableRowDisplayPreview?.forEach((rowData: any) => {
                    tableRow[rowData.col] = rowData.result_data[i];
                  });
                  this.tableDataDisplay.push(tableRow);
                 // console.log('display row data ', this.tableDataDisplay)
                }
              },
              error: (error) => {
                console.log(error);
              }
            }
          )
        } else {
          this.tableDataDisplay = []
          this.tableColumnsDisplay = []
          this.totalItems = 0
        }
      }

      pivotRowData = [] as any;
      pivotColumnData = [] as any;
      pivotMeasureData = [] as any;
        pivotTableDatatransform() {
          if (this.draggedRows.length > 0 || this.draggedColumns.length > 0) {
            this.transformedData =[];
          let headers: string[] = [];

          this.columnKeys = this.pivotColumnData?.map((col: any) => col.column); 
          this.rowKeys = this.pivotRowData?.map((row: any) => row.col);
          this.valueKeys = this.pivotMeasureData?.map((col:any) =>col.col)
          this.pivotColumnData.forEach((colObj: any) => {
            headers.push(colObj.column);
          });
      
          this.pivotRowData.forEach((rowObj: any) => {
            headers.push(rowObj.col);
          });
          this.pivotMeasureData.forEach((colObj: any) => {
            headers.push(colObj.col);
          });
      
          this.transformedData.push(headers); 
          let numRows = 0;
          if (this.pivotColumnData.length > 0) {
            numRows = this.pivotColumnData[0].result_data.length;
            } else if (this.pivotRowData.length > 0) {
            numRows = this.pivotRowData[0].result_data.length;
            } else if (this.pivotMeasureData.length > 0) {
            numRows = this.pivotMeasureData[0].result_data.length;
            }
      
          for (let i = 0; i < numRows; i++) {
            let rowArray: any[] = []; 
            this.pivotColumnData.forEach((colObj: any) => {
              rowArray.push(colObj.result_data[i]);
            });
                  this.pivotRowData.forEach((rowObj: any) => {
              rowArray.push(rowObj.result_data[i]);
            });
            this.pivotMeasureData.forEach((rowObj: any) => {
              rowArray.push(rowObj.result_data[i]);
            });

            this.transformedData.push(rowArray);
          }
          this.renderPivotTable();        
        }
        }

        renderPivotTable() {
          setTimeout(() => {

          if (this.pivotContainer && this.pivotContainer.nativeElement) {
              ($(this.pivotContainer.nativeElement) as any).pivot(this.transformedData, {
                rows: this.columnKeys,  
                cols: this.valueKeys, 
                // vals: this.valueKeys, 
                aggregator:$.pivotUtilities.aggregators["Sum"](this.rowKeys),
                rendererName: "Table"
              });
            // }, 1000);
          }        
                      }, 1000);

        }


      chartsDataSet(data: any) {
        let sidebysideBarColumnData = [];
        this.sheetCustomQuery = data.custom_query;
        // this.sheetfilter_querysets_id = data.sheetfilter_querysets_id || data.sheet_filter_quereyset_ids;
        this.tablePreviewColumn = data.data?.col ? data.data.col : data.sheet_data?.col ? data.sheet_data.col : [];
        this.tablePreviewRow = data.data?.row ? data.data.row : data.sheet_data?.row ? data.sheet_data.row : [];
        this.pivotMeasureData = data.data?.pivotMeasure_Data ? data.data.pivotMeasure_Data : data.sheet_data?.pivotMeasure_Data ? data.sheet_data?.pivotMeasure_Data : [];
        
        this.storeTableColumn = data?.table_data?.col ? data.table_data.col : data.sheet_data?.col ? data.sheet_data.col : [];
        this.storeTableRow = data?.table_data?.row ? data.table_data.row : data.sheet_data?.row ? data.sheet_data.row : [];
        // if(this.table){
        //   this.tableDisplayPagination();
        // }
        console.log(this.tablePreviewColumn);
        console.log(this.tablePreviewRow);
        if (this.tablePreviewColumn && this.tablePreviewRow) {
          this.tablePreviewColumn.forEach((res: any) => {
            // let obj = {
            //   data: res.result_data
            // }
            sidebysideBarColumnData.push(res.result_data);
            let obj1 = {
              name: res.column,
              values: res.result_data
            }
            this.dualAxisColumnData.push(obj1);
          });
          this.tablePreviewRow.forEach((res: any) => {
            let obj = {
              name: res.col,
              data: res.result_data
            }
            this.dualAxisRowData.push(obj);
          });
          this.tablePreviewRow.forEach((res: any) => {
            let obj = {
              name: res.col,
              value: res.result_data
            }
            this.radarRowData.push(obj);
          });
          console.log('dualAxisColumnDatathis', this.dualAxisColumnData)
          console.log(this.dualAxisRowData);
          this.cdr.detectChanges();
          let rowCount: any;
          if (this.tablePreviewColumn[0]?.result_data?.length) {
            rowCount = this.tablePreviewColumn[0]?.result_data?.length;
          } else {
            rowCount = this.tablePreviewRow[0]?.result_data?.length;
            this.guagechartRowData = rowCount
            console.log('guage length',this.guagechartRowData)
          }
          //const rowCount = this.tablePreviewRow[0]?.result_data?.length;
          // Extract column names
          this.displayedColumns = this.tablePreviewColumn.map((col: any) => col.column).concat(this.tablePreviewRow.map((row: any) => row.col));
          // Create table data
          console.log(this.displayedColumns)
          // for (let i = 0; i < rowCount; i++) {
          //   const row: TableRow = {};
          //   this.tablePreviewColumn.forEach((col: any) => {
          //     row[col.column] = col.result_data[i];
          //   });
          //   this.tablePreviewRow.forEach((rowData: any) => {
          //     row[rowData.col] = rowData.result_data[i];
          //   });
          //   this.tableData.push(row);

          // }
          //storing table
          let rowCountStore: any;
          if (this.storeTableColumn[0]?.result_data?.length) {
            rowCountStore = this.storeTableColumn[0]?.result_data?.length;
          } else {
            rowCountStore = this.storeTableRow[0]?.result_data?.length;
          }
          rowCountStore = rowCountStore > 10 ? 10:rowCountStore;
          for (let i = 0; i < rowCountStore; i++) {
            const row: TableRow = {};
            this.storeTableColumn.forEach((col: any) => {
              row[col.column] = col.result_data[i];
            });
            this.storeTableRow.forEach((rowData: any) => {
              row[rowData.col] = rowData.result_data[i];
            });
            this.tableDataStore.push(row);
          }
          console.log('only table store',this.tableDataStore);
          //store table data close

          this.tablePreviewColumn.forEach((col: any) => {
            this.chartsColumnData = col.result_data;
          });
          this.tablePreviewRow.forEach((rowData: any) => {
            this.chartsRowData = rowData.result_data;
          });
          console.log(this.chartsColumnData)
          console.log(this.chartsRowData)
          // const length = Math.min(this.chartsColumnData.length, this.chartsRowData.length);
          // for (let i = 0; i < length; i++) {
          //   const aa = { col: this.chartsColumnData[i], row: this.chartsRowData[i] };
          //   this.chartsData.push(aa);
          // }
        }

      }
      chartType : string ='';
      chartsOptionsSet(){
        if (this.bar) {
          this.chartType = 'bar';
        }
        else if(this.pivotTable){
          this.chartType = 'pivotTable'
        } else if (this.area) {
          this.chartType = 'area';
        } else if (this.line) {
          this.chartType = 'line';
        } else if (this.pie) {
          this.chartType = 'pie';
        } else if (this.sidebyside) {
          this.chartType = 'sidebyside';
        } else if (this.stocked) {
          this.chartType = 'stocked';
        } else if (this.barLine) {
          this.chartType = 'barline';
        } else if (this.horizentalStocked) {
          this.chartType = 'hstocked';
        } else if (this.grouped) {
          this.chartType = 'hgrouped';
        } else if (this.multiLine) {
          this.chartType = 'multiline';
        } else if (this.donut) {
          this.chartType = 'donut';
        } else if (this.radar) {
          this.chartType = 'radar';
        } else if (this.heatMap) {
          this.chartType = 'heatmap';
        } else if (this.kpi){
          this.KPIChart();
        } else if (this.funnel){
          this.chartType = 'funnel';
        }else if(this.guage){
          this.chartType = 'guage';
        } else if(this.map){
          this.chartType = 'map';
          this.http.get('./assets/maps/world.json').subscribe((geoJson: any) => {
            echarts.registerMap('world', geoJson);  // Register the map data
          });
        } else if(this.calendar){
          this.chartType = 'calendar';
        }

      }

      KPIChart(){
        this.KPINumber = _.cloneDeep(this.tablePreviewRow[0].result_data[0]);
        this.formatKPINumber();
      }
      tableNameMethod(schemaname: any, tablename: any, tableAlias: any){
        this.schemaName = '';
        this.tableName = '';
        this.table_alias = '';
        this.schemaName = schemaname;
        this.tableName = tablename;
        this.table_alias = tableAlias;
      }
      storeColumnData = [] as any;
      storeRowData = [] as any;
      columndrop(event: CdkDragDrop<string[]>){
        // if (event.previousContainer === event.container) {
        //   moveItemInArray(event.container.data, event.previousIndex, event.currentIndex);
        // } else {
        //   transferArrayItem(
        //     event.previousContainer.data,
        //     event.container.data,
        //     event.previousIndex,
        //     event.currentIndex,
        //   );
        // }
        this.sortedData = [];
        console.log(event)
    let item: any = event.previousContainer.data[event.previousIndex];
        this.storeColumnData.push(event.previousContainer.data);
        // this.storeColumnData[0].forEach((element:any) => {
        // if(element.column === item.column){
        let copy: any = JSON.parse(JSON.stringify(item));
        let element: any = {};
        for(let attr in copy) {
        if (attr == 'title') {
          element[attr] = copy[attr];
        } else {
          element[attr] = copy[attr];
        }
      }
      this.draggedColumns.splice(event.currentIndex, 0, element);
      event.currentIndex = this.draggedColumns.indexOf(element);
      console.log('New element index:', event.currentIndex);
      const columnIndexMap = new Map((this.draggedColumns as any[]).map((col, index) => [col.column, index]));
      //this.draggedColumnsData.push([this.schemaName,this.tableName,this.table_alias,element.column,element.data_type,""])
      if(element.data_type == 'calculated') {
        this.draggedColumnsData.splice(event.currentIndex, 0,[element.column, element.data_type, "", element.field_name]);
      } else {
      this.draggedColumnsData.splice(event.currentIndex, 0,[element.column, element.data_type, "", ""]);
      }
      // this.draggedColumnsData = (this.draggedColumnsData as any[]).sort((a, b) => {
      //   const indexA = columnIndexMap.get(a[0]) ?? -1;
      //   const indexB = columnIndexMap.get(b[0]) ?? -1;
      //   return indexA - indexB;
      // });
      // this.draggedColumns.forEach((column: any, index: number) => {
      //   if (column.column === element.column) {
      //     if (event.currentIndex !== index) {
      //       event.currentIndex = index;
      //     }
      //   }
      // });
      console.log(this.draggedColumnsData);
      this.draggedDrillDownColumns = [];
      if(this.draggedColumns.length === 1){
        const startIndex = this.locationHeirarchyFieldList.findIndex(
          (location) => location.toLowerCase() === this.draggedColumns[0]?.column?.toLowerCase()
        );
        if(startIndex >= 0){
          this.isLocationFeild = true;
          this.locationHeirarchyList = this.locationHeirarchyFieldList.splice(startIndex);
          this.locationHeirarchyFieldList = ['country', 'state', 'city'];
        } else {
          this.isLocationFeild = false;
        }
      } else {
        this.drillDownObject = [];
      }
      if (this.dateList.includes(element.data_type)) {
        this.dateFormat(element, event.currentIndex, 'year');
      } else {
        this.dataExtraction();
      }
    }
    //dateList=['date','time','datetime','timestamp','timestamp with time zone','timestamp without time zone','timezone','time zone','timestamptz','nullable(date)', 'nullable(time)', 'nullable(datetime)','nullable(timestamp)','nullable(timestamp with time zone)', 'nullable(timestamp without time zone)', 'nullable(timezone)', 'nullable(time zone)', 'nullable(timestamptz)', 'nullable(datetime)','datetime64','datetime32','date32'];
    // integerList = ['numeric','int','float','number','double precision','smallint','integer','bigint','decimal','numeric','real','smallserial','serial','bigserial','binary_float','binary_double','int64','int32','float64','float32','nullable(int64)','nullable(int32)','nullable(uint8)','nullable(flaot(64))'];
    // boolList = ['bool', 'boolean'];
    //stringList = ['varchar','bp char','text','varchar2','NVchar2','long','char','Nchar','character varying','string','str','nullable(string)'];
    
  integerList = ['numeric', 'int', 'float', 'number', 'double precision', 'smallint', 'integer', 'bigint', 'decimal', 'numeric', 'real', 'smallserial', 'serial', 'bigserial', 'binary_float', 'binary_double', 'int64', 'int32', 'float64', 'float32', 'nullable(int64)', 'nullable(int32)', 'nullable(uint8)',
    'nullable(float(64))', 'int8', 'int16', 'int32', 'int64', 'float32', 'float16', 'float64', 'decimal(38,10)', 'decimal(12,2)', 'uuid', 'nullable(int8)', 'nullable(int16)', 'nullable(int32)', 'nullable(int64)', 'nullable(float32)', 'nullable(float16)', 'nullable(float64)', 'nullable(decimal(38,10)', 'nullable(decimal(12,2)']
  stringList = ['varchar', 'bp char', 'text', 'varchar2', 'NVchar2', 'long', 'char', 'Nchar', 'character varying', 'string', 'str', 'nullable(varchar)', 'nullable(bp char)', 'nullable(text)',
    'nullable(varchar2)', 'nullable(NVchar2)',
    'nullable(long)', 'nullable(char)', 'nullable(Nchar)',
    'nullable(character varying)', 'nullable(string)', 'string', 'nullable(string)', 'array(string)', 'nullable(array(string))']
  boolList = ['bool', 'boolean', 'nullable(bool)', 'nullable(boolean)', 'uint8']
  dateList = ['date', 'time', 'datetime', 'timestamp', 'timestamp with time zone', 'timestamp without time zone', 'timezone', 'time zone', 'timestamptz', 'nullable(date)', 'nullable(time)', 'nullable(datetime)',
    'nullable(timestamp)',
    'nullable(timestamp with time zone)',
    'nullable(timestamp without time zone)',
    'nullable(timezone)', 'nullable(time zone)', 'nullable(timestamptz)',
    'nullable(datetime)', 'datetime64', 'datetime32', 'date32', 'nullable(date32)', 'nullable(datetime64)', 'nullable(datetime32)', 'date', 'datetime', 'time', 'datetime64', 'datetime32', 'date32', 'nullable(date)', 'nullable(time)', 'nullable(datetime64)', 'nullable(datetime32)', 'nullable(date32)']

    rowdrop(event: CdkDragDrop<string[]>){
      // if (event.previousContainer === event.container) {
      //   moveItemInArray(event.container.data, event.previousIndex, event.currentIndex);
      // } else {
      //   transferArrayItem(
      //     event.previousContainer.data,
      //     event.container.data,
      //     event.previousIndex,
      //     event.currentIndex,
      //   );
      // }
      this.sortedData = [];
      console.log(event)
    let item: any = event.previousContainer.data[event.previousIndex];
      // this.storeRowData.push(event.previousContainer.data); 
      //this.storeRowData[0].forEach((element:any) => {
      //  if(element.column === item.column){
      let copy: any = JSON.parse(JSON.stringify(item));
      let element: any = {};
      for(let attr in copy) {
      if (attr == 'title') {
        element[attr] = copy[attr];
      } else {
        element[attr] = copy[attr];
      }
    }
    this.draggedRows.splice(event.currentIndex, 0, element);
    event.currentIndex = this.draggedRows.indexOf(element);
    const rowIndexMap = new Map((this.draggedRows as any[]).map((row, index) => [row.column, index]));
    //this.draggedRowsData.push([this.schemaName,this.tableName,this.table_alias,element.column,element.data_type,""])
    if(element.data_type == 'calculated') {
      this.draggedRowsData.splice(event.currentIndex, 0,[element.column, element.data_type, "", element.field_name]);
    } else {
    this.draggedRowsData.splice(event.currentIndex, 0,[element.column, element.data_type, "", ""]);
    }
    // this.draggedRowsData = (this.draggedRowsData as any[]).sort((a, b) => {
    //   const indexA = rowIndexMap.get(a[0]) ?? -1;
    //   const indexB = rowIndexMap.get(b[0]) ?? -1;
    //   return indexA - indexB;
    // });
    // this.draggedRows.forEach((row: any, index: number) => {
    //   if (row.column === element.column) {
    //     if (event.currentIndex !== index) {
    //       event.currentIndex = index;
    //     }
    //   }
    // });
    console.log(this.draggedRowsData);
    if (this.integerList.includes(element.data_type)) {
      this.rowMeasuresCount(element, event.currentIndex, 'sum');
    } else {
      this.dataExtraction();
    }

  }
  isDropdownVisible = false;

  toggleDropdown() {
    this.isDropdownVisible = !this.isDropdownVisible;
  }
  rowMeasuresCount(rows:any,index:any,type:any){
    if(this.selectedSortColumnData && this.selectedSortColumnData.length > 0 && this.selectedSortColumnData[0] === rows.column && this.selectedSortColumnData[2] === this.draggedRowsData[index][2]){
      this.selectedSortColumnData[2] = type;
    }
      this.measureValues = [];
      if(type){
        this.measureValues = [rows.column,"aggregate",type,rows.alias ? rows.alias : ""];
      }
      else{
        this.measureValues = [rows.column,rows.data_type,'',rows.alias ? rows.alias : ""];
      }
     if(type === ''){
      this.draggedRowsData[index] = [rows.column,rows.data_type,type,rows.alias ? rows.alias : ""];
      this.draggedRows[index] = {column:rows.column,data_type:rows.data_type,type:type,alias:rows.alias};
      this.dataExtraction();
     }else if(type === '-Select-'){
      this.draggedRowsData[index] = [rows.column,rows.data_type,'',rows.alias ? rows.alias : ""];
      this.draggedRows[index] = {column:rows.column,data_type:rows.data_type,type:'',alias:rows.alias};
      this.dataExtraction();
     }else{
    this.draggedRowsData[index] = this.measureValues;
    console.log(this.draggedRowsData);
    this.draggedRows[index] = {column:rows.column,data_type:rows.data_type,type:type,alias:rows.alias};
    console.log(this.draggedRows)
    if(type === 'count' || type === 'count_distinct'){
      this.KPIDecimalPlaces = 0;
      this.decimalPlaces = 0;
      this.donutDecimalPlaces = 0;
    } else {
      this.KPIDecimalPlaces = 2;
      this.decimalPlaces = 2;
      this.donutDecimalPlaces = 2;
    }
    this.dataExtraction();
     }
  }

  onAliasChange(rows : any , index : any){
    this.isMeasureEdit = false;
    this.rowMeasuresCount(rows, index, rows.type);
  }
   drop(event: CdkDragDrop<string[]>) {
    if (event.previousContainer === event.container) {
      moveItemInArray(event.container.data, event.previousIndex, event.currentIndex);
    } else {
      transferArrayItem(
        event.previousContainer.data,
        event.container.data,
        event.previousIndex,
        event.currentIndex,
      );
    }
  }
  dragStartedColumn(index:any,column:any){
    this.sortedData = [];
    console.log(this.draggedColumns);
    console.log(this.draggedColumnsData);
    console.log(index);
    // this.draggedColumns.splice(index, 1);
    // (this.draggedColumnsData as any[]).forEach((data,index1)=>{
    //   if(this.dateList.includes(data[1])){
    //     if(this.draggedColumns[index].column === data[0] && this.draggedColumns[index].data_type === data[1] 
    //       && this.draggedColumns[index].type === data[2]){
    //         this.draggedColumnsData.splice(index, 1);
    //     }
    //   }
    //   else{
    //     (data as any[]).forEach((aa)=>{ 
    //       if(column === aa){
    //         console.log(aa);
    //         this.draggedColumnsData.splice(index1, 1);
    //       }
    //     } );
    //   }
    // });
    if(this.draggedDrillDownColumns && this.draggedDrillDownColumns.length > 0) {
      this.draggedDrillDownColumns = [];
    }
    if(this.drillDownObject && this.drillDownObject.length > 0) {
      this.drillDownObject = [];
    }
    this.draggedColumns.splice(index, 1);   
    this.draggedColumnsData.splice(index, 1);
    this.dateDrillDownSwitch = false;
    this.locationDrillDownSwitch = false;
    this.getDimensionAndMeasures();
    if (this.selectedSortColumnData) {
      let sortcolumn = JSON.parse(JSON.stringify(this.selectedSortColumnData));
      sortcolumn?.splice(4, 1);
      if (!this.columnsDataForSort.some(column => JSON.stringify(column) === JSON.stringify(sortcolumn))) {
        this.selectedSortColumnData = null;
        this.sortColumn = 'select';
        this.sortType = 0;
      }
    }
    if(this.draggedColumns.length === 1){
      const startIndex = this.locationHeirarchyFieldList.findIndex(
        (location) => location.toLowerCase() === this.draggedColumns[0]?.column?.toLowerCase()
      );
      if(startIndex >= 0){
        this.isLocationFeild = true;
        this.locationHeirarchyList = this.locationHeirarchyFieldList.splice(startIndex);
        this.locationHeirarchyFieldList = ['country', 'state', 'city'];
        this.toggleLocationSwitch(false);
      } else {
        this.isLocationFeild = false;
      }
      
    }
   this.dataExtraction();
  }
  dragStartedRow(index:any,column:any){
    this.sortedData = [];
    this.draggedRows.splice(index, 1);
    this.draggedRowsData.splice(index, 1);
    if(this.draggedDrillDownColumns && this.draggedDrillDownColumns.length > 0) {
      this.draggedDrillDownColumns = [];
    }
    this.dateDrillDownSwitch = false;
    this.locationDrillDownSwitch = false;
  //   (this.draggedRowsData as any[]).forEach((data,index)=>{
  //    (data as any[]).forEach((aa)=>{ 
  //      if(column === aa){
  //        console.log(aa);
  //        this.draggedRowsData.splice(index, 1);
  //      }
  //    } );
  //  });  
  this.getDimensionAndMeasures(); 
  if (this.selectedSortColumnData) {
    let sortcolumn = JSON.parse(JSON.stringify(this.selectedSortColumnData));
    sortcolumn?.splice(4, 1);
    if (!this.columnsDataForSort.some(column => JSON.stringify(column) === JSON.stringify(sortcolumn))) {
      this.selectedSortColumnData = null;
      this.sortColumn = 'select';
      this.sortType = 0;
    }
  }
   this.dataExtraction();
  }
  rightArrow(){
    console.log(this.draggedColumns.length)
    if(this.draggedColumns.length == 6){

    }else{
   const columnNext =  this.draggedColumns.length;
    for (let i = 7; i < columnNext; i++) {
      this.draggedColumns[i];
    }
    console.log(this.draggedColumns)
  }
  }
  table = true;
  pivotTable = false;
  bar = false;
  sidebyside = false;
  area = false;
  line = false;
  pie = false;
  stocked = false;
  barLine = false;
  horizentalStocked = false;
  grouped = false;
  multiLine = false;
  donut = false;
  kpi = false;
  heatMap = false;
  funnel = false;
  guage = false;
  calendar = false;
  chartDisplay(table:boolean,bar:boolean,area:boolean,line:boolean,pie:boolean,sidebysideBar:boolean,stocked:boolean,barLine:boolean,
    horizentalStocked:boolean,grouped:boolean,multiLine:boolean,donut:boolean,radar:boolean,kpi:any,heatMap:any,funnel:any,guage:boolean,map:boolean,calendar:boolean,pivotTable:boolean,chartId:any){
    this.table = table;
    this.pivotTable = pivotTable;
    this.bar=bar;
    this.area=area;
    this.line=line;
    this.pie=pie;
    this.sidebyside = sidebysideBar;
    this.stocked = stocked;
    this.barLine = barLine;
    this.horizentalStocked = horizentalStocked;
    this.grouped = grouped;
    this.multiLine = multiLine;
    this.donut = donut;
    this.chartId = chartId;
    this.radar = radar;
    this.kpi = kpi;
    this.heatMap = heatMap;
    this.funnel = funnel;
    this.guage = guage;
    this.map = map;
    this.calendar = calendar;
    // this.dataExtraction();
    if(!(this.bar|| this.pie || this.donut)){
      this.draggedDrillDownColumns = [];
      this.drillDownObject = [];
      this.drillDownIndex = 0;
      this.dateDrillDownSwitch = false;
    }
    this.resetCustomizations();
    this.chartsOptionsSet(); 
  }
  // enableDisableCharts(){
  //   console.log(this.draggedColumnsData);
  //   console.log(this.draggedRowsData);
  //   const obj={
  //       "db_id":this.databaseId,
  //       "col":this.draggedColumnsData,
  //       "row":this.draggedRowsData,
  // }
  //   this.workbechService.getChartsEnableDisable(obj).subscribe({next: (responce:any) => {
  //         console.log(responce);
  //         this.chartsEnableDisable = responce;
  //       },
  //       error: (error) => {
  //         console.log(error);
  //       }
  //     }
  //   )
  // }
  tabs : any [] = [];
  selected = new FormControl(0);
  addSheet(isDuplicate : boolean) {
    this.columnsData();
    if (this.active !== 3){
      this.active = 1;
    }
    this.retriveDataSheet_id = '';
    this.draggedDrillDownColumns = [];
    this.drillDownObject = [];
    this.drillDownIndex = 0;
    this.dateDrillDownSwitch = false;
    delete this.originalData;
    this.sheetName = ''; this.sheetTitle = '';
    this.KPIDecimalPlaces = 2;
    this.KPIRoundPlaces = 0;
    this.KPIDisplayUnits = 'none';
    this.KPIPrefix = '';
    this.KPISuffix = '';
    this.KPIPercentageDivisor = 100;
    if(this.sheetName != ''){
       this.tabs.push(this.sheetName);
    }else{
      this.getChartData();
      this.sheetNumber = this.tabs.length+1;
       this.tabs.push('Sheet ' +this.sheetNumber);
       this.SheetSavePlusEnabled.push('Sheet ' +this.sheetNumber);
       this.selectedTabIndex = this.tabs.length - 1;
       this.sheetTagName = 'Sheet ' +this.sheetNumber;
       this.setChartType();
    }
    this.kpi=false;
    this.resetCustomizations();
  }

  sheetDuplicate(){
    this.sheetNumber = this.tabs.length+1;
    this.sheetTagName = 'Sheet ' +this.sheetNumber;
    // this.setChartType();
    if(this.filterId?.length > 0){
    this.workbechService.sheetFiltersDuplicate(this.retriveDataSheet_id).subscribe(
      {
        next: (data: any) => {
          this.tabs.push('Sheet ' +this.sheetNumber);
          this.SheetSavePlusEnabled.push('Sheet ' +this.sheetNumber);
          this.selectedTabIndex = this.tabs.length - 1;
          this.sheetRetrive(true,data.filters_list);
          
        },
        error: (error: any) => {
          Swal.fire({
            icon: 'warning',
            text: error.error.message,
            width: '300px',
          })
          console.log(error)
        }
      }
    )
    } else {
      this.tabs.push('Sheet ' +this.sheetNumber);
      this.SheetSavePlusEnabled.push('Sheet ' +this.sheetNumber);
      this.selectedTabIndex = this.tabs.length - 1;
      this.sheetRetrive(true);
    }
  }

  sheetNameChange(name:any,event:any){
    console.log(this.SheetIndex)
    // if (event.keyCode === 13) {
    //   this.tabs[this.SheetIndex] = name;
    // }
    this.sheetTagName = name;
  }
  removeTab() {
    console.log(this.SheetIndex)
    const obj = {
      sheet_id: this.retriveDataSheet_id,
    }
    this.workbechService.deleteSheetMessage(obj)
      .subscribe(
        {
          next: (data: any) => {
            console.log(data);
            Swal.fire({
              title: 'Are you sure?',
              text: data.message,
              icon: 'warning',
              showCancelButton: true,
              confirmButtonColor: '#3085d6',
              cancelButtonColor: '#d33',
              confirmButtonText: 'Yes, delete it!'
            }).then((result) => {
              if (result.isConfirmed) {
                const idToPass = this.databaseId;
                this.workbechService.deleteSheet(idToPass,this.qrySetId,this.retriveDataSheet_id).subscribe({next: (data:any) => {
                // this.workbechService.deleteSheet(this.databaseId, this.qrySetId, this.retriveDataSheet_id).subscribe({
                //   next: (data: any) => {
                    console.log(data);
                    if (data) {
                      this.tabs.splice(this.SheetIndex, 1);
                      // Swal.fire({
                      //   icon: 'success',
                      //   title: 'Deleted!',
                      //   text: 'Deleted Successfully',
                      //   width: '200px',
                      // })
                      this.toasterService.success('Deleted Successfully','success',{ positionClass: 'toast-top-right'});
                      this.getChartData();
                      this.retriveDataSheet_id = '';
                    }
                  },
                  error: (error: any) => {
                    Swal.fire({
                      icon: 'warning',
                      text: error.error.message,
                      width: '200px',
                    })
                    console.log(error)
                  }
                }
                )
              }
            })
          },
          error: (error: any) => {
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
  onChange(event:MatTabChangeEvent){
    console.log('tabs',event);
    this.selectedTabIndex =  event.index;
    const selectedTab = this.tabs[event.index]; // Get the selected tab using the index
    const selectedSheetId = selectedTab.id; // Access the sheet_id
  
    this.draggedDrillDownColumns = [];
    this.drillDownObject = [];
    this.drillDownIndex = 0;
    this.sheetName = '';
    this.dateDrillDownSwitch = false;
    this.locationDrillDownSwitch = false;
    delete this.originalData;
    console.log(event)
    if(event.index === -1){
     this.retriveDataSheet_id = 1;
    }
    this.SheetIndex = event.index;
    this.sheetName = selectedTab.sheet_name ? selectedTab.sheet_name : selectedTab;
    this.sheetTitle = this.sheetName;

    this.sheetTagName = this.sheetName;
    this.sheetTagTitle = this.sheetName;
    this.draggedColumns = [];
    this.draggedColumnsData = [];
    this.draggedRows = [];
    this.draggedRowsData = [];
    this.displayedColumns = [];
    this.retriveDataSheet_id = '';
    this.getChartData();
    if(selectedSheetId){
      this.retriveDataSheet_id = selectedSheetId;
      this.sheetRetrive(false);
    }

    // const obj = {
    //   "server_id": this.databaseId,
    //   "queryset_id": this.qrySetId,
    // } as any;
    // if (this.fromFileId) {
    //   delete obj.server_id;
    //   obj.file_id = this.fileId;
    // }
    // this.workbechService.getSheetNames(obj).subscribe({
    //   next: (responce: any) => {
    //     this.sheetList = responce.data;
    //     if (!this.sheetList.some(sheet => sheet.sheet_name === this.sheetName)) {
    //       this.retriveDataSheet_id = '';
    //     } else {
    //       this.sheetList.forEach(sheet => {
    //         if (sheet.sheet_name === this.sheetName) {
    //           this.retriveDataSheet_id = sheet.id;
    //         }
    //       });
    //     }
    //     // const inputElement = document.getElementById('htmlContent') as HTMLInputElement;
    //     // inputElement.innerHTML = event.tab?.textLabel;
    //     this.sheetTagName = event.tab?.textLabel;
    //     console.log(this.sheetName)
    //     console.log(this.retriveDataSheet_id);
    //     this.draggedColumns = [];
    //     this.draggedColumnsData = [];
    //     this.draggedRows = [];
    //     this.draggedRowsData = [];
    //     this.displayedColumns = [];
    //     this.getChartData();
    //    if(this.retriveDataSheet_id){
    //       this.sheetRetrive();
    //    }
    //   },
    //   error: (error) => {
    //     console.log(error);
    //   }
    // }
    // )
    this.kpi = false;
  }
  getChartData(){
   // if(this.draggedColumns && this.draggedRows && !this.retriveDataSheet_id){
   //alert("pls save your changes")
   // }else{
    this.filterData = [];
    this.filterId = [];
    this.draggedColumns =[];
    this.draggedColumnsData =[];
    this.draggedRows = [];
    this.draggedRowsData = [];
    this.draggedMeasureValues = [];
    this.draggedMeasureValuesData = [];
    // this.retriveDataSheet_id = '';
    this.dimetionMeasure = [];
    this.dualAxisColumnData = [];
    this.dualAxisRowData = [];
    this.sheetfilter_querysets_id = null;
      this.saveTableData = [] ;
      this.savedisplayedColumns = [];
      this.saveBar = [];
      this.savePie = [];
      this.lineYaxis = [];
      this.lineXaxis = [];
      this.areaYaxis = [];
      this.areaXaxis = [];
      this.draggedColumns = [];
      this.draggedRows = [];
      this.tablePreviewColumn = [];
      this.tablePreviewRow = [];
      this.storeTableRow = [];
      this.storeTableColumn = [];
      this.tableDataStore = [];
      this.totalItems = 0;
      this.tableDataDisplay = [];
      this.tableColumnsDisplay = [];
      this.displayedColumns = [];
      this.chartsRowData = [];
      this.chartsColumnData = [];
      this.draggedColumnsData = [];
      this.draggedRowsData = [];
      this.sidebysideBarYaxis = [];
      this.sidebysideBarXaxis = [];
      this.stokedBarYaxis = [];
      this.stokedBarXaxis = [];
      this.barLineYaxis = [];
      this.barLineXaxis = [];
      this.hStockedYaxis = [];
      this.hStockedXaxis = [];
      this.hgroupedYaxis = [];
      this.hgroupedXaxis = [];
      this.multiLineYaxis = [];
      this.multiLineXaxis = [];
      this.donutYaxis = [];
      this.donutXaxis = [];
      this.sortedData = [];
      this.table = true;
      this.pivotTable = false;
      this.bar = false;
      this.pie = false;
      this.line = false;
      this.area = false;
      this.sidebyside = false;
      this.stocked = false;
      this.barLine = false;
      this.horizentalStocked = false;
      this.grouped = false;
      this.multiLine = false;
      this.donut = false;
      this.radar = false;
      this.kpi = false;
      this.map = false;
      this.heatMap = false;
      this.funnel = false;
      this.calendar = false;
      this.guage = false;
      this.banding = false;
      this.barOptions = undefined;
      this.lineOptions = undefined;
      this.areaOptions = undefined;
      this.pieOptions = undefined;
      this.sidebysideBarOptions = undefined;
      this.stokedOptions = undefined;
      this.barLineOptions = undefined;
      this.hStockedOptions = undefined;
      this.hgroupedOptions = undefined;
      this.multiLineOptions = undefined;
      this.donutOptions = undefined;
      this.kpiFontSize = '3';
      this.kpiColor = '#000000';
      this.GridColor = '#089ffc';
      this.backgroundColor = '#fcfcfc';
      this.color = '#2392c1';
      this.bandingSwitch = false;
      this.xLabelSwitch = true;
      this.yLabelSwitch = true;
      this.xGridSwitch = false;
      this.yGridSwitch = false;
      this.color1 = undefined;
      this.color2 = undefined;
      this.displayUnits = 'none';
      this.suffix = '';
      this.prefix = '';
      this.tableSearch = '';
      this.legendsAllignment = 'bottom';
      this.dataLabels = true;
      this.legendSwitch = true;
      this.label = true;
      this.donutSize = 50;
      this.donutDecimalPlaces = 2;
      this.decimalPlaces = 2;
      this.barColor = '#4382f7';
      this.lineColor = '#38ff98';
      this.heirarchyColumnData = [];
      this.selectedSortColumnData = null;
   // }
  }
  saveTableData = [] as any;
  savedisplayedColumns = [] as any;
  banding : boolean = false;
  saveBar = [] as any;
  savePie = [] as any;
  lineYaxis = [] as any;
  lineXaxis = [] as any;
  lineOptions : any = undefined;
  areaYaxis = [] as any;
  areaXaxis = [] as any;
  areaOptions : any = undefined;
  barXaxis = [] as any;
  barOptions : any = undefined;
  pieXaxis = [] as any;
  pieOptions : any = undefined;
  sidebysideBarYaxis = [] as any;
  sidebysideBarXaxis = [] as any;
  sidebysideBarOptions : any = undefined;
  stokedBarYaxis = [] as any;
  stokedBarXaxis = [] as any;
  stokedOptions : any = undefined;
  barLineYaxis = [] as any;
  barLineXaxis = [] as any;
  barLineOptions : any = undefined;
  hStockedYaxis = [] as any;
  hStockedXaxis = [] as any;
  hStockedOptions : any = undefined;
  hgroupedYaxis = [] as any;
  hgroupedXaxis = [] as any;
  hgroupedOptions : any = undefined;
  multiLineYaxis = [] as any;
  multiLineXaxis = [] as any;
  multiLineOptions : any = undefined;
  donutYaxis = [] as any;
  donutXaxis = [] as any;
  donutOptions : any = undefined;
  eMapChartOptions : any;

sheetSave(){
  let savedChartOptions ;
  let kpiData;
  let kpiColor;
  let kpiFontSize;
  let bandColor1;
  let bandColor2;
  let tablePreviewRow = this.tablePreviewRow;
  let tablePreviewCol = this.tablePreviewColumn;
  if(this.table && this.chartId == 1){
  //  this.saveTableData =  this.tableData;
   this.saveTableData =  this.tableDataStore;
   this.savedisplayedColumns = this.displayedColumns;
   this.banding = this.bandingSwitch;
   bandColor1 = this.color1;
   bandColor2 = this.color2;
  }
  if(this.pivotTable && this.chartId == 9){
    //  this.saveTableData =  this.tableDataStore;
    //  this.savedisplayedColumns = this.displayedColumns;
    //  this.banding = this.bandingSwitch;
    //  bandColor1 = this.color1;
    //  bandColor2 = this.color2;
    }
  if(this.bar && this.chartId == 6){
    this.saveBar = this.chartsRowData;
    this.barXaxis = this.chartsColumnData.map((category : any)  => category === null ? 'null' : category);
    if (this.originalData) {
      this.saveBar = this.originalData.data;
      this.barXaxis = this.originalData.categories;
      tablePreviewRow = _.cloneDeep(this.tablePreviewRow);
      tablePreviewRow[0].result_data = this.originalData.data;
      tablePreviewCol = _.cloneDeep(this.tablePreviewColumn);
      tablePreviewCol[0].result_data = this.originalData.categories;
      delete this.originalData;
    }
  }
  if(this.pie && this.chartId == 24){
    this.savePie = this.chartsRowData;
    this.pieXaxis = this.chartsColumnData.map((category : any)  => category === null ? 'null' : category);
    if (this.originalData) {
      this.savePie = this.originalData.data;
      this.pieXaxis = this.originalData.categories;
      // savedChartOptions.labels = this.originalData.categories;
      // savedChartOptions.series = this.originalData.data;
      tablePreviewRow = _.cloneDeep(this.tablePreviewRow);
      tablePreviewRow[0].result_data = this.originalData.data;
      tablePreviewCol = _.cloneDeep(this.tablePreviewColumn);
      tablePreviewCol[0].result_data = this.originalData.categories;
      delete this.originalData;
    }
  }
  if(this.line && this.chartId == 13){
    this.lineYaxis = this.chartsRowData;
    this.lineXaxis = this.chartsColumnData;
  }
  if(this.area && this.chartId == 17){
    this.areaYaxis = this.chartsRowData;
    this.areaXaxis = this.chartsColumnData;
  }
  if(this.sidebyside && this.chartId == 7){
    this.sidebysideBarYaxis = this.dualAxisRowData;
    this.sidebysideBarXaxis = this.dualAxisColumnData;
  }
  if(this.stocked && this.chartId == 5){
    this.stokedBarYaxis = this.dualAxisRowData;
    this.stokedBarXaxis = this.dualAxisColumnData;
  }
  if(this.barLine && this.chartId == 4){
    this.barLineYaxis = this.dualAxisRowData;
    this.barLineXaxis = this.dualAxisColumnData;
  }
  if(this.horizentalStocked && this.chartId == 2){
    this.hStockedYaxis = this.dualAxisRowData;
    this.hStockedXaxis = this.dualAxisColumnData;
  }
  if(this.grouped && this.chartId == 3){
    this.hgroupedYaxis = this.dualAxisRowData;
    this.hgroupedXaxis = this.dualAxisColumnData;    
  }
  if(this.multiLine && this.chartId == 8){
    this.multiLineYaxis = this.dualAxisRowData;
    this.multiLineXaxis = this.dualAxisColumnData;    
  }
  if(this.donut && this.chartId == 10){
    
    this.donutYaxis = this.chartsRowData;
    this.donutXaxis = this.chartsColumnData.map((category : any)  => category === null ? 'null' : category);
    
    if (this.originalData) {
      this.donutYaxis = this.originalData.data;
      this.donutXaxis = this.originalData.categories;
      // savedChartOptions.labels = this.originalData.categories;
      // savedChartOptions.series = this.originalData.data;
      tablePreviewRow = _.cloneDeep(this.tablePreviewRow);
      tablePreviewRow[0].result_data = this.originalData.data;
      tablePreviewCol = _.cloneDeep(this.tablePreviewColumn);
      tablePreviewCol[0].result_data = this.originalData.categories;
      delete this.originalData;
    }
  }
  if(this.kpi && this.chartId == 25){
    kpiData = this.tablePreviewRow;
    kpiColor = this.kpiColor;
    kpiFontSize = this.kpiFontSize;
  }
  if(this.map && this.chartId == 29){
    if(this.originalData){
      if(this.draggedDrillDownColumns.length > 0){
        this.originalData.categories.forEach((column:any,index:any)=>{
          tablePreviewCol[index].column = column.name;
          tablePreviewCol[index].result_data = column.values;
        });
        this.originalData.data.forEach((column:any,index:any)=>{
          tablePreviewRow[index].column = column.name;
          tablePreviewRow[index].result_data = column.data;
        });
        this.drillDownIndex = 0;
      }
      delete this.originalData;
    }
  }
  savedChartOptions = this.chartOptionsSet;
  let customizeObject = {
    isZoom : this.isZoom,
    xGridColor : this.xGridColor,
    xGridSwitch : this.xGridSwitch,
    xLabelSwitch : this.xLabelSwitch,
    xLabelColor : this.xLabelColor,
    yLabelSwitch : this.yLabelSwitch,
    yGridColor : this.yGridColor,
    yGridSwitch : this.yGridSwitch,
    yLabelColor : this.yLabelColor,
    xLabelFontFamily : this.xLabelFontFamily,
    xLabelFontSize : this.xLabelFontSize,
    xlabelFontWeight : this.xlabelFontWeight,
    labelAlignment : this.xlabelAlignment,
    backgroundColor : this.backgroundColor,
    color : this.color,
    selectedColorScheme:this.selectedColorScheme,
    ylabelFontWeight : this.ylabelFontWeight,
    isBold : this.isBold,
    isTableHeaderBold:this.isTableHeaderBold,
    isTableDataBold:this.isTableDataBold,
    isYlabelBold:this.isYlabelBold,
    isXlabelBold:this.isXlabelBold,
    yLabelFontFamily : this.yLabelFontFamily,
    yLabelFontSize : this.yLabelFontSize,
    bandingSwitch : this.bandingSwitch,
    backgroundColorSwitch : this.backgroundColorSwitch,
    chartColorSwitch : this.chartColorSwitch,
    barColorSwitch : this.barColorSwitch,
    lineColorSwitch : this.lineColorSwitch,
    gridLineColorSwitch : this.gridLineColorSwitch,
    xLabelColorSwitch : this.xLabelColorSwitch,
    xGridLineColorSwitch : this.xGridLineColorSwitch,
    yLabelColorSwitch : this.yLabelColorSwitch,
    yGridLineColorSwitch : this.yGridLineColorSwitch,
    bandingColorSwitch : this.bandingColorSwitch,
    kpiColorSwitch : this.kpiColorSwitch,
    funnelColorSwitch : this.funnelColorSwitch,
    color1 : this.color1,
    color2 : this.color2,
    kpiColor : this.kpiColor,
    barColor : this.barColor,
    lineColor : this.lineColor,
    GridColor : this.GridColor,
    legendSwitch : this.legendSwitch,
    dataLabels : this.dataLabels,
    label : this.label,
    donutSize : this.donutSize,
    isDistributed : this.isDistributed,
    kpiFontSize : this.kpiFontSize,
    minValueGuage : this.minValueGuage,
    maxValueGuage : this.maxValueGuage,
    donutDecimalPlaces : this.donutDecimalPlaces,
    decimalPlaces : this.decimalPlaces,
    legendsAllignment : this.legendsAllignment,
    displayUnits : this.displayUnits,
    suffix : this.suffix,
    prefix : this.prefix,
    dataLabelsFontFamily : this.dataLabelsFontFamily,
    dataLabelsFontSize: this.dataLabelsFontSize,
    dataLabelsFontPosition: this.dataLabelsFontPosition,
    measureAlignment: this.measureAlignment,
    dimensionAlignment: this.dimensionAlignment,
    tableDataFontFamily: this.tableDataFontFamily,
    tableDataFontSize: this.tableDataFontSize,
    tableDataFontWeight: this.tableDataFontWeight,
    tableDataFontStyle: this.tableDataFontStyle,
    tableDataFontDecoration: this.tableDataFontDecoration,
    tableDataFontColor: this.tableDataFontColor,
    tableDataFontAlignment: this.tableDataFontAlignment,
    headerFontFamily: this.headerFontFamily,
    headerFontSize: this.headerFontSize,
    headerFontWeight: this.headerFontWeight,
    headerFontStyle: this.headerFontStyle,
    headerFontDecoration: this.headerFontDecoration,
    headerFontColor: this.headerFontColor,
    headerFontAlignment: this.headerFontAlignment,
    dimensionColor:this.dimensionColor,
    measureColor:this.measureColor,
    dataLabelsColor:this.dataLabelsColor,
    sortType : this.sortType,
    rightLegend:this.rightLegend,
    bottomLegend:this.bottomLegend,
    legendOrient:this.legendOrient,
    leftLegend:this.leftLegend,
    topLegend:this.topLegend,
    sortColumn:this.sortColumn,
    locationDrillDownSwitch:this.locationDrillDownSwitch,
    isLocationField : this.isLocationFeild,
    KPIDecimalPlaces : this.KPIDecimalPlaces,
    KPIDisplayUnits : this.KPIDisplayUnits,
    KPIPrefix : this.KPIPrefix,
    KPISuffix : this.KPISuffix
  }
  // this.sheetTagName = this.sheetTitle;
  let draggedColumnsObj;
  if (this.dateDrillDownSwitch && this.draggedColumnsData && this.draggedColumnsData.length > 0) {
    draggedColumnsObj = _.cloneDeep(this.draggedColumnsData);
    draggedColumnsObj[0][2] = 'year'
  } else if(this.locationDrillDownSwitch && this.draggedColumnsData && this.draggedColumnsData.length > 0){
    draggedColumnsObj = _.cloneDeep(this.draggedColumnsData);
    draggedColumnsObj[0][0] = this.draggedDrillDownColumns[0];
  } else {
    draggedColumnsObj = this.draggedColumnsData
  }
const obj={
  "chart_id": this.chartId,
  "queryset_id":this.qrySetId,
  "server_id": this.databaseId,
  "sheet_name": this.sheetTitle,
  "sheet_tag_name": this.sheetTagName,
  "filter_id":this.filterId,
  "sheetfilter_querysets_id":this.sheetfilter_querysets_id,
  "filter_data": this.dimetionMeasure,
  "datasource_querysetid": this.filterQuerySetId,
  "col": this.mulColData,
  "row": this.mulRowData,
  "pivot_measure":this.pivotMeasureValues,
  "custom_query":this.sheetCustomQuery,
  "data":{
    "drillDownHierarchy":this.draggedDrillDownColumns,
    "isDrillDownData" : this.dateDrillDownSwitch,
    "heirarchyColumnData" : this.heirarchyColumnData,
    "selectedSortColumnData" : this.selectedSortColumnData,
  "columns": this.draggedColumns,
  "columns_data":draggedColumnsObj,
  "rows": this.draggedRows,
  "rows_data":this.draggedRowsData,
  "pivotMeasure":this.draggedMeasureValues,
  "pivotMeasure_Data":this.pivotMeasureData,
  "pivotMeasureValuesData":this.draggedMeasureValuesData,
  "pivotTransformedData":this.transformedData,
  "col":tablePreviewCol,
  "row":tablePreviewRow,
  "results": {
    "tableData":this.saveTableData,
    "tableColumns":this.savedisplayedColumns,
    "banding":this.banding,
    "color1":bandColor1,
    "color2":bandColor2,
    "items_per_page":this.itemsPerPage,
    "total_items":this.totalItems,

    "barYaxis":this.saveBar,
    "barXaxis":this.barXaxis,
  //  "barOptions":this.barOptions,

    "pieYaxis":this.savePie,
    "pieXaxis":this.pieXaxis,
  //   "pieOptions":this.pieOptions,

    "lineYaxis":this.lineYaxis,
    "lineXaxis": this.lineXaxis,
  //   "lineOptions":this.lineOptions,

    "areaYaxis":this.areaYaxis,
    "areaXaxis":this.areaXaxis,
  //   "areaOptions":this.areaOptions,

      "sidebysideBarYaxis": this.sidebysideBarYaxis,
      "sidebysideBarXaxis": this.sidebysideBarXaxis,
  //     "sidebysideBarOptions":this.sidebysideBarOptions,
   
      "stokedBarYaxis": this.stokedBarYaxis,
      "stokedBarXaxis": this.stokedBarXaxis,
  //     "stokedOptions":this.stokedOptions,
  
      "barLineYaxis":this.barLineYaxis,
      "barLineXaxis":this.barLineXaxis,
  //     "barLineOptions":this.barLineOptions,

      "hStockedYaxis": this.hStockedYaxis,
      "hStockedXaxis": this.hStockedXaxis,
  //     "hStockedOptions":this.hStockedOptions,

      "hgroupedYaxis": this.hgroupedYaxis,
      "hgroupedXaxis": this.hgroupedXaxis,
  //     "hgroupedOptions":this.hgroupedOptions,

      "multiLineYaxis":this.multiLineYaxis,
      "multiLineXaxis": this.multiLineXaxis,
  //     "multiLineOptions":this.multiLineOptions,

      "donutYaxis": this.donutYaxis,
      "donutXaxis": this.donutXaxis,
      "decimalplaces": this.donutDecimalPlaces,
  //     "donutOptions":this.donutOptions,

      "kpiData": kpiData,
      "kpiFontSize": kpiFontSize,
      "kpicolor": kpiColor,
      "kpiNumber" : this.KPINumber,
      "kpiPrefix" : this.KPIPrefix,
      "kpiSuffix" : this.KPISuffix,
      "kpiDecimalUnit" : this.KPIDisplayUnits,
      "kpiDecimalPlaces" : this.KPIDecimalPlaces
  },
  "isApexChart" : this.isApexCharts,
  "isEChart" : this.isEChatrts,
  "savedChartOptions" : savedChartOptions,
  "customizeOptions" : customizeObject,
  "numberFormat" : {
    "decimalPlaces" : this.decimalPlaces,
    "displayUnits" : this.displayUnits,
    "prefix" : this.prefix,
    "suffix" : this.suffix
  }
}
}
console.log(this.retriveDataSheet_id)
if(this.retriveDataSheet_id){
  console.log("Sheet Update")
  this.workbechService.sheetUpdate(obj,this.retriveDataSheet_id).subscribe({next: (responce:any) => {
   this.tabs[this.SheetIndex].sheet_name = this.sheetTitle;
    if(responce){
      // Swal.fire({
      //   icon: 'success',
      //   text: responce.message,
      //   width: '200px',
      // })
      this.toasterService.success(responce.message,'success',{ positionClass: 'toast-top-right'});

    //   this.getSheetNames();
    //  this.sheetRetrive();
    }
      let obj : object= {
        "sheet_id":this.retriveDataSheet_id
      }
      this.workbechService.dashboardSheetsUpdate(obj).subscribe({next: (responce:any) => {
        console.log('sheet_dash_update');
        console.log(responce);
      }
    })
  
  },
  error: (error) => {
    console.log(error);
    Swal.fire({
      icon: 'error',
      text: error.error.message,
      width: '200px',
    })
  }
}
)
}else{
  this.retriveDataSheet_id = '';
  this.workbechService.sheetSave(obj).subscribe({next: (responce:any) => {
   this.tabs[this.SheetIndex] = this.sheetTitle;
    console.log(responce);
    if(responce){
      // Swal.fire({
      //   icon: 'success',
      //   text: responce.message,
      //   width: '200px',
      // })
      this.toasterService.success(responce.message,'success',{ positionClass: 'toast-top-right'});
      this.retriveDataSheet_id = responce.sheet_id;
      // this.getSheetNames();
      // this.sheetRetrive();
      this.SheetSavePlusEnabled.splice(0, 1);
      this.getSheetList();
    }
    this.saveTableData= [];
    this.savedisplayedColumns = [];
    this.saveBar =[];
    this.barXaxis = [];
    this.savePie = [];
    this.pieXaxis =[];
    this.lineYaxis = [];
    this.lineXaxis =[];
    this.areaYaxis =[];
    this.areaXaxis =[];
    this.sidebysideBarYaxis =[];
    this.sidebysideBarXaxis =[];
    this.stokedBarYaxis =[];
    this.stokedBarXaxis =[];
    this.barLineYaxis =[];
    this.barLineXaxis =[];
    this.hStockedYaxis =[];
    this.hStockedXaxis =[];
    this.hgroupedYaxis =[];
    this.hgroupedXaxis =[];
    this.multiLineYaxis =[];
    this.multiLineXaxis =[];
    this.donutYaxis =[];
    this.donutXaxis =[];
    this.measureValues = [];
  //  this.draggedRowsData = [];
   // this.draggedColumnsData = [];
  },
  error: (error) => {
    console.log(error);
    Swal.fire({
      icon: 'error',
      text: error.error.message,
      width: '200px',
    })
   
  }
}
)
}

  }
sheetTagTitle : any;
sheetChartId : any;

mergeFilters(filtersData: any[], filtersList: any[]): any[] {
  return filtersData.map((filter) => {
    const matchingFilter = filtersList.find(
      (item) => item.col_name === filter.col_name
    );
    if (matchingFilter) {
      // Replace filter_id with id from filters_list
      return { ...filter, filter_id: matchingFilter.id };
    }
    return filter; // Return the original filter if no match is found
  });
}

sheetRetrive(isDuplicate : boolean,duplicateFilterData?:any){
  this.getChartData();
  console.log(this.tabs);
  const obj={
  "queryset_id":this.qrySetId,
  "server_id": this.databaseId,
}

this.workbechService.sheetGet(obj,this.retriveDataSheet_id).subscribe({next: (responce:any) => {
        if(isDuplicate){
          this.retriveDataSheet_id = '';
        } else {
          this.retriveDataSheet_id = responce?.sheet_id;
          this.sheetName = responce?.sheet_name;
          this.sheetTitle = responce?.sheet_name;
          this.sheetfilter_querysets_id = responce?.sheetfilter_querysets_id || responce?.sheet_filter_quereyset_ids;
          if(!responce.sheet_tag_name){
            this.sheetTagName = responce?.sheet_name;
          }
          else{
            this.sheetTagName = responce?.sheet_tag_name;
          }
        }
        this.chartId = responce?.chart_id;
        this.sheetChartId = responce?.chart_id;
        this.sheetCustomQuery = responce?.custom_query;
        this.sheetResponce = responce?.sheet_data;
        this.draggedColumns=this.sheetResponce?.columns;
        if(!this.filterQuerySetId){
          this.filterQuerySetId = responce?.datasource_queryset_id;
        }
        this.draggedRows = this.sheetResponce?.rows;
        this.draggedMeasureValues = this.sheetResponce?.pivotMeasure; 
        this.mulColData = responce?.col_data;
        this.mulRowData = responce?.row_data;
        this.pivotMeasureValues = responce?.pivot_measure

        this.pivotMeasureData = this.sheetResponce?.pivotMeasure_Data;
        this.pivotColumnData = this.sheetResponce?.col;
        this.pivotRowData = this.sheetResponce?.row;

        this.tablePaginationRows=responce?.row_data;
        this.tablePaginationColumn=responce?.col_data;
  if (isDuplicate && duplicateFilterData) {
    let filterData = responce?.filters_data;
    this.dimetionMeasure = this.mergeFilters(filterData, duplicateFilterData);
  } else {
    this.dimetionMeasure = responce?.filters_data;
  }
        this.createdBy = responce?.created_by;
        this.color1 = responce?.sheet_data?.results?.color1;
        this.color2 = responce?.sheet_data?.results?.color2;
        this.tablePaginationCustomQuery = responce?.custom_query;
        this.donutDecimalPlaces = this.sheetResponce?.results.decimalplaces;
        if(this.sheetResponce?.numberFormat?.decimalPlaces){ 
          this.decimalPlaces = this.sheetResponce?.numberFormat?.decimalPlaces;
        }
        if(this.sheetResponce?.numberFormat?.displayUnits){
          this.displayUnits = this.sheetResponce?.numberFormat?.displayUnits;
        }
        if(this.sheetResponce?.numberFormat?.prefix){
          this.prefix = this.sheetResponce?.numberFormat?.prefix;
        }
        if(this.sheetResponce?.numberFormat?.suffix){
          this.suffix = this.sheetResponce?.numberFormat?.suffix;
        }
        // this.GridColor = responce.sheet_data.savedChartOptions.chart.background;
        // this.apexbBgColor = responce.sheet_data.savedChartOptions.grid.borderColor;
        if(isDuplicate && duplicateFilterData){
          duplicateFilterData.forEach((filter: any)=>{
            this.filterId.push(filter.id);
          });
        } else {
        responce?.filters_data.forEach((filter: any)=>{
          this.filterId.push(filter.filter_id);
        });
      }
      this.isTopFilter = !this.dimetionMeasure.some((column: any) => column.top_bottom && column.top_bottom.length>0);
        this.isEChatrts = this.sheetResponce?.isEChart;
        this.isApexCharts = this.sheetResponce?.isApexChart;
        this.dateDrillDownSwitch = this.sheetResponce?.isDrillDownData;
        this.locationDrillDownSwitch = this.sheetResponce?.customizeOptions?.locationDrillDownSwitch;
        this.isLocationFeild = this.sheetResponce?.customizeOptions?.isLocationField;
        this.draggedDrillDownColumns = this.sheetResponce?.drillDownHierarchy ? this.sheetResponce.drillDownHierarchy : [];
        this.heirarchyColumnData = this.sheetResponce?.heirarchyColumnData ? this.sheetResponce?.heirarchyColumnData : [];
        this.selectedSortColumnData = this.sheetResponce?.selectedSortColumnData ? this.sheetResponce?.selectedSortColumnData : null;
        if(this.isEChatrts){
          this.selectedChartPlugin = 'echart';
        } else {
          this.isApexCharts = true;
          this.selectedChartPlugin = 'apex';
        }
        this.sheetTagTitle = this.sanitizer.bypassSecurityTrustHtml(this.sheetTagName);
        // this.displayUnits = 'none';
        
        if(this.sheetResponce.columns_data){
          this.draggedColumnsData = this.sheetResponce?.columns_data;
        }
        else{
          this.draggedColumns.forEach((res:any) => {
            this.draggedColumnsData.push([res.column,res.data_type,"",""])
          });
        }
        if(this.sheetResponce.rows_data){
          this.draggedRowsData = this.sheetResponce?.rows_data;
        }
        else{
          this.draggedRows.forEach((res:any) => {
            this.draggedRowsData.push([res.column,res.data_type,"",res.alias ? res.alias : ""])
          });
        }
        if(this.sheetResponce.pivotMeasure){
          this.draggedMeasureValues = this.sheetResponce?.pivotMeasure;
          this.draggedMeasureValuesData = this.sheetResponce?.pivotMeasureValuesData
        }
        else if(this.draggedMeasureValues){
          this.draggedMeasureValues.forEach((res:any) => {
            this.draggedMeasureValuesData.push([res.column,res.data_type,"",res.alias ? res.alias : ""])
          });
        }
        // this.table = false;
        this.chartsDataSet(responce);
        if(responce.chart_id == 1){
          // this.tableData = this.sheetResponce.results.tableData;
          this.displayedColumns = this.sheetResponce?.results.tableColumns;
          this.bandingSwitch = this.sheetResponce?.results.banding;
          this.color1 = this.sheetResponce?.results?.color1;
          this.color2 = this.sheetResponce?.results?.color2;
          this.table = true;
          this.pivotTable = false;
          this.bar = false;
          this.pie = false;
          this.line = false;
          this.area = false;
          this.sidebyside = false;
          this.stocked = false;
          this.barLine = false;
          this.horizentalStocked = false;
          this.grouped = false;
          this.multiLine = false;
          this.donut = false;
          this.radar = false;
          this.kpi = false;
          this.heatMap = false;
          this.map = false
          this.funnel = false;
          this.guage = false;
          this.calendar = false;
          this.tableDisplayPagination();
        }
        if(responce.chart_id == 9){
          // this.tableData = this.sheetResponce.results.tableData;
          this.displayedColumns = this.sheetResponce?.results.tableColumns;
          this.table = false;
          this.pivotTable = true;
          this.bar = false;
          this.pie = false;
          this.line = false;
          this.area = false;
          this.sidebyside = false;
          this.stocked = false;
          this.barLine = false;
          this.horizentalStocked = false;
          this.grouped = false;
          this.multiLine = false;
          this.donut = false;
          this.radar = false;
          this.kpi = false;
          this.heatMap = false;
          this.map = false
          this.funnel = false;
          this.guage = false;
          this.calendar = false;
          this.pivotTableDatatransform();
        }
        if(responce.chart_id == 25){
          this.tablePreviewRow = this.sheetResponce?.results?.kpiData;
          this.KPINumber = this.sheetResponce?.results?.kpiNumber;
          this.kpiFontSize = this.sheetResponce?.results?.kpiFontSize;
          this.kpiColor = this.sheetResponce?.results?.kpicolor;
          if(this.sheetResponce?.results?.kpiPrefix) {
            this.KPIPrefix = this.sheetResponce.results.kpiPrefix;
          }
          if(this.sheetResponce?.results?.kpiSuffix) {
            this.KPISuffix = this.sheetResponce.results.kpiSuffix;
          }
          this.KPIDisplayUnits = this.sheetResponce?.results?.kpiDecimalUnit,
          this.KPIDecimalPlaces = this.sheetResponce?.results?.kpiDecimalPlaces,
          this.table = false;
          this.pivotTable = false;
          this.bar = false;
          this.pie = false;
          this.line = false;
          this.area = false;
          this.sidebyside = false;
          this.stocked = false;
          this.barLine = false;
          this.horizentalStocked = false;
          this.grouped = false;
          this.multiLine = false;
          this.donut = false;
          this.radar = false;
          this.kpi = true;
          this.heatMap = false;
          this.funnel = false;
          this.guage = false;
          this.map = false;
          this.calendar = false;
        }
        if(responce.chart_id == 29){
          this.http.get('./assets/maps/world.json').subscribe((geoJson: any) => {
            echarts.registerMap('world', geoJson);  // Register the map data
          });
          this.table = false;
          this.pivotTable = false;
          this.bar = false;
          this.pie = false;
          this.line = false;
          this.area = false;
          this.sidebyside = false;
          this.stocked = false;
          this.barLine = false;
          this.horizentalStocked = false;
          this.grouped = false;
          this.multiLine = false;
          this.donut = false;
          this.radar = false;
          this.kpi = false;
          this.heatMap = false;
          this.funnel = false;
          this.guage = false;
          this.map = true;
          this.calendar = false;
          this.chartType = 'map';
        }
       if(responce.chart_id == 6){
        // this.chartsRowData = this.sheetResponce.results.barYaxis;
        // this.chartsColumnData = this.sheetResponce.results.barXaxis;
        this.chartType = 'bar';
      //  this.barChart();
        this.bar = true;
        this.table = false;
        this.pivotTable = false;
          this.pie = false;
          this.line = false;
          this.area = false;
          this.sidebyside = false;
          this.stocked = false;
          this.barLine = false;
          this.horizentalStocked = false;
          this.grouped = false;
          this.multiLine = false;
          this.donut = false;
          this.radar = false;
          this.kpi = false;
          this.heatMap = false;
          this.funnel = false;
          this.guage = false;
          this.map = false;
          this.calendar = false;
       }
       if(responce.chart_id == 24){
        this.chartType = 'pie';
        // this.pieChart();
        this.bar = false;
        this.table = false;
        this.pivotTable = false;
          this.pie = true;
          this.line = false;
          this.area = false;
          this.sidebyside = false;
          this.stocked = false;
          this.barLine = false;
          this.horizentalStocked = false;
          this.grouped = false;
          this.multiLine = false;
          this.donut = false;
          this.radar = false;
          this.kpi = false;
          this.heatMap = false;
          this.funnel = false;
          this.map = false;
          this.guage = false;
          this.calendar = false;
       }
       if(responce.chart_id == 13){
        this.chartType = 'line';
        // this.lineChart();
        this.bar = false;
        this.table = false;
        this.pivotTable = false;
          this.pie = false;
          this.line = true;
          this.area = false;
          this.sidebyside = false;
          this.stocked = false;
          this.barLine = false;
          this.horizentalStocked = false;
          this.grouped = false;
          this.multiLine = false;
          this.donut = false;
          this.radar = false;
          this.kpi = false;
          this.heatMap = false;
          this.funnel = false;
          this.guage = false;
          this.map = false;
          this.calendar = false;
       }
       if(responce.chart_id == 17){
        this.chartType = 'area';
        // this.areaChart();
        this.bar = false;
        this.table = false;
        this.pivotTable = false;
          this.pie = false;
          this.line = false;
          this.area = true;
          this.sidebyside = false;
          this.stocked = false;
          this.barLine = false;
          this.horizentalStocked = false;
          this.grouped = false;
          this.multiLine = false;
          this.donut = false;
          this.radar = false;
          this.kpi = false;
          this.heatMap = false;
          this.funnel = false;
          this.guage = false;
          this.map = false;
          this.calendar = false;
       }
       if(responce.chart_id == 7){
        this.chartType = 'sidebyside';
        // this.sidebysideBar();
        this.bar = false;
        this.table = false;
        this.pivotTable = false;
          this.pie = false;
          this.line = false;
          this.area = false;
          this.sidebyside = true;
          this.stocked = false;
          this.barLine = false;
          this.horizentalStocked = false;
          this.grouped = false;
          this.multiLine = false;
          this.donut = false;
          this.radar = false;
          this.kpi = false;
          this.heatMap = false;
          this.funnel = false;
          this.guage = false;
          this.map = false;
          this.calendar = false;
       }
       if(responce.chart_id == 5){
        this.chartType = 'stocked';
        // this.stockedBar();
        this.bar = false;
        this.table = false;
        this.pivotTable = false;
          this.pie = false;
          this.line = false;
          this.area = false;
          this.sidebyside = false;
          this.stocked = true;
          this.barLine = false;
          this.horizentalStocked = false;
          this.grouped = false;
          this.multiLine = false;
          this.donut = false;
          this.radar = false;
          this.kpi = false;
          this.heatMap = false;
          this.funnel = false;
          this.map = false;
          this.guage = false;
          this.calendar = false;
       }
       if(responce.chart_id == 4){
        this.chartType = 'barline';
        // this.barLineChart();
        this.bar = false;
        this.table = false;
        this.pivotTable = false;
          this.pie = false;
          this.line = false;
          this.area = false;
          this.sidebyside = false;
          this.stocked = false;
          this.barLine = true;
          this.horizentalStocked = false;
          this.grouped = false;
          this.multiLine = false;
          this.donut = false;
          this.radar = false;
          this.kpi = false;
          this.heatMap = false;
          this.funnel = false;
          this.map = false;
          this.guage = false;
          this.calendar = false;
       }
       if(responce.chart_id == 12){
        this.chartType = 'radar';
        // this.dualAxisColumnData = this.sheetResponce.results.barLineXaxis;
        this.bar = false;
        this.table = false;
        this.pivotTable = false;
          this.pie = false;
          this.line = false;
          this.area = false;
          this.sidebyside = false;
          this.stocked = false;
          this.barLine = false;
          this.horizentalStocked = false;
          this.grouped = false;
          this.multiLine = false;
          this.donut = false;
          this.radar = true;
          this.kpi = false;
          this.heatMap = false;
          this.funnel = false;
          this.guage = false;
          this.map = false;
          this.calendar = false;
       }
       if(responce.chart_id == 2){
        this.chartType = 'hstocked';
        // this.horizentalStockedBar();
        this.bar = false;
        this.table = false;
        this.pivotTable = false;
          this.pie = false;
          this.line = false;
          this.area = false;
          this.sidebyside = false;
          this.stocked = false;
          this.barLine = false;
          this.horizentalStocked = true;
          this.grouped = false;
          this.multiLine = false;
          this.donut = false;
          this.radar = false;
          this.kpi = false;
          this.heatMap = false;
          this.funnel = false;
          this.map = false;
          this.guage = false;
          this.calendar = false;
       }
       if(responce.chart_id == 3){
        this.chartType = 'hgrouped';
        // this.hGrouped();
        this.bar = false;
        this.table = false;
        this.pivotTable = false;
          this.pie = false;
          this.line = false;
          this.area = false;
          this.sidebyside = false;
          this.stocked = false;
          this.barLine = false;
          this.horizentalStocked = false;
          this.grouped = true;
          this.multiLine = false;
          this.donut = false;
          this.radar = false;
          this.kpi = false;
          this.heatMap = false;
          this.funnel = false;
          this.guage = false;
          this.map = false;
          this.calendar = false;
       }
       if(responce.chart_id == 8){
        this.chartType = 'multiline';
        // this.multiLineChart();
        this.bar = false;
        this.table = false;
        this.pivotTable = false;
          this.pie = false;
          this.line = false;
          this.area = false;
          this.sidebyside = false;
          this.stocked = false;
          this.barLine = false;
          this.horizentalStocked = false;
          this.grouped = false;
          this.multiLine = true;
          this.donut = false;
          this.radar = false;
          this.kpi = false;
          this.heatMap = false;
          this.funnel = false;
          this.guage = false;
          this.map = false;
          this.calendar = false;
       }
       if(responce.chart_id == 10){
        this.chartType = 'donut';
        // this.donutChart();
        this.bar = false;
        this.table = false;
        this.pivotTable = false;
          this.pie = false;
          this.line = false;
          this.area = false;
          this.sidebyside = false;
          this.stocked = false;
          this.barLine = false;
          this.horizentalStocked = false;
          this.grouped = false;
          this.multiLine = false;
          this.donut = true;
          this.radar = false;
          this.kpi = false;
          this.heatMap = false;
          this.funnel = false;
          this.guage = false;
          this.map = false;
          this.calendar = false;
       }
       if(responce.chart_id == 26){
        this.chartType = 'heatmap';
        this.bar = false;
        this.table = false;
        this.pivotTable = false;
          this.pie = false;
          this.line = false;
          this.area = false;
          this.sidebyside = false;
          this.stocked = false;
          this.barLine = false;
          this.horizentalStocked = false;
          this.grouped = false;
          this.multiLine = false;
          this.donut = false;
          this.radar = false;
          this.kpi = false;
          this.heatMap = true;
          this.funnel = false;
          this.guage = false;
          this.map = false;
          this.calendar = false;
       }
       if(responce.chart_id == 27){
        this.chartType = 'funnel';
        this.bar = false;
        this.table = false;
        this.pivotTable = false;
          this.pie = false;
          this.line = false;
          this.area = false;
          this.sidebyside = false;
          this.stocked = false;
          this.barLine = false;
          this.horizentalStocked = false;
          this.grouped = false;
          this.multiLine = false;
          this.donut = false;
          this.radar = false;
          this.kpi = false;
          this.heatMap = false;
          this.funnel = true;
          this.guage = false;
          this.map = false;
          this.calendar = false;
       }
       if(responce.chart_id == 28){
        this.chartType = 'guage';
        this.bar = false;
        this.table = false;
        this.pivotTable = false;
          this.pie = false;
          this.line = false;
          this.area = false;
          this.sidebyside = false;
          this.stocked = false;
          this.barLine = false;
          this.horizentalStocked = false;
          this.grouped = false;
          this.multiLine = false;
          this.donut = false;
          this.radar = false;
          this.kpi = false;
          this.heatMap = false;
          this.funnel = false;
          this.guage = true;
          this.map = false;
          this.calendar = false;
       }
       if(responce.chart_id == 11){
        this.chartType = 'calendar';
        this.bar = false;
        this.table = false;
        this.pivotTable = false;
          this.pie = false;
          this.line = false;
          this.area = false;
          this.sidebyside = false;
          this.stocked = false;
          this.barLine = false;
          this.horizentalStocked = false;
          this.grouped = false;
          this.multiLine = false;
          this.donut = false;
          this.radar = false;
          this.kpi = false;
          this.heatMap = false;
          this.funnel = false;
          this.guage = false;
          this.map = false;
          this.calendar = true;
       }
       this.setCustomizeOptions(this.sheetResponce.customizeOptions);
       this.getDimensionAndMeasures();
       this.changeSelectedColumn();
        // setTimeout(()=>{
        //   // this.updateNumberFormat();
        // }, 1000);
      },
      error: (error) => {
        console.log(error);
        this.getChartData();
      }
    }
  )
  }
  filterName:any
  filterType:any;
  openSuperScaled(modal: any,data:any) {
    this.filterSearch = '';
    this.filterDataArray = [];
    this.isExclude = false;
    this.modalService.open(modal, {
      centered: true,
      windowClass: 'animate__animated animate__zoomIn',
    });
    if(data.data_type == 'calculated'){
      this.filterName = data.field_name;
      this.filterCalculatedFieldLogic = data.column;
    } else {
    this.filterName = data.column;
    }
    this.filterType = data.data_type;
    this.filterDataGet();
  }
  filterData = [] as any;
  filter_id: any;
  minValue: any;
  maxValue: any;
  floor: any;
  ceil: any;
  minDate: string = '';
  maxDate: string = '';
  options: Options ={};
  filterDateRange : any[] = [];
  updateDateRange() {
    const format: Intl.DateTimeFormatOptions = { 
      year: 'numeric',
      month: '2-digit', 
      day: '2-digit',  
    };
    const minDateObj = new Date(this.minValue);
    const maxDateObj = new Date(this.maxValue);
    this.minDate = `${minDateObj.getFullYear()}/${(minDateObj.getMonth() + 1).toString().padStart(2, '0')}/${minDateObj.getDate().toString().padStart(2, '0')}`;
    this.maxDate = `${maxDateObj.getFullYear()}/${(maxDateObj.getMonth() + 1).toString().padStart(2, '0')}/${maxDateObj.getDate().toString().padStart(2, '0')}`;
    this.filterDateRange = [this.minDate, this.maxDate];
  }
  formatExtractType : string = '';
  extractTypesForTab : any[] = ['year','quarter','month','day','week number','weekdays','count','count_distinct','min','max'];
  extractAggregateTypes : any[] = ['count','count_distinct','min','max'];
  filterDataGet(){
    if(this.activeTabId === 4){
      this.totalDataLength = this.tablePreviewColumn[0]?.result_data?.length;
    }
    const obj={
      "hierarchy_id" :this.databaseId,
      "query_set_id":this.qrySetId,
      "type_of_filter" : "sheet",
      "datasource_queryset_id" :this.filterQuerySetId,
      "col_name":this.filterName,
      "data_type":this.extractAggregateTypes.includes(this.formatExtractType) ? 'aggregate' : this.filterType,
      "search":this.filterSearch,
      "parent_user":this.createdBy,
      "field_logic" : this.filterCalculatedFieldLogic?.length > 0 ? this.filterCalculatedFieldLogic : null,
      "is_calculated": this.filterType == 'calculated' ? true : false,
      "format_date" : this.activeTabId === 2 ? 'year/month/day' :this.formatExtractType
}
  this.workbechService.filterPost(obj).subscribe({next: (responce:any) => {
        console.log(responce);
        const convertedArray = responce.col_data.map((item: any) => ({ label: item, selected: false }));
        this.filterData = convertedArray;

        if(this.dateList.includes(responce.dtype)){
          let rawLabel = this.filterData[0].label;
          let datePart = rawLabel.split(" ")[0];
          let [year, month, day] = datePart.split("/");
          this.floor = new Date(`${year}-${month}-${day}`).getTime();
          // this.floor = new Date(this.filterData[0].label).getTime();

          rawLabel = this.filterData[this.filterData.length - 1].label;
          datePart = rawLabel.split(" ")[0];
          [year, month, day] = datePart.split("/");
          this.ceil = new Date(`${year}-${month}-${day}`).getTime();
          // this.ceil = new Date(this.filterData[this.filterData.length - 1].label).getTime();

          this.minValue = this.floor;
          this.maxValue = this.ceil;
          this.options = {
            floor: this.floor,
            ceil: this.ceil,
            step: 24 * 60 * 60 * 1000,
            showSelectionBar: true,
            selectionBarGradient: {
              from: '#5a66f1',
              to: '#5a66f1',
            },
            translate: (value: number): string => {
              return new Date(value).toLocaleDateString();
            }
          };
          this.updateDateRange();
          this.filterDateRange = [];
        }
        //this.filter_id = responce.filter_id;
      },
      error: (error) => {
        console.log(error);
      }
    }
  )
  }
  toggleEditAllRows(event:any){
    // this.isAllSelected = !this.isAllSelected;
    this.filterDataArray = [];
    this.filterData.forEach((element: any) => { element['selected'] = this.isAllSelected; if(this.isAllSelected){this.filterDataArray.push(element.label)} });
    console.log(this.filterData)
  }

  filterDataArray = [] as any;
  filterCheck(event:any,data:any){
    if(event.target.checked){
      this.filterDataArray.push(data);
    }else{
      let index1 = this.filterDataArray.findIndex((i:any) => i == data);
      this.filterDataArray.splice(index1, 1);
    }
   console.log(this.filterDataArray)
  }
  totalDataLength : any;
  filterDataPut(){
    // this.dimetionMeasure = [];
    this.sortedData = [];
    if(this.activeTabId === 4){
      this.totalDataLength = this.tablePreviewColumn[0]?.result_data?.length;
    }
    const obj={
    //"filter_id": this.filter_id,
    "hierarchy_id": this.databaseId,
    "queryset_id": this.qrySetId,
    "type_of_filter":"sheet",
    "datasource_querysetid" : this.filterQuerySetId,
    "range_values": this.filterDateRange,
    "select_values":this.filterDataArray,
    "col_name":this.filterName,
    "data_type":this.filterType,
    "parent_user":this.createdBy,
    "is_exclude":this.isExclude,
    "field_logic" : this.filterCalculatedFieldLogic?.length > 0 ? this.filterCalculatedFieldLogic : null,
    "is_calculated": this.filterType == 'calculated' ? true : false,
    "format_date" : this.activeTabId === 2 ? 'year/month/day' :this.formatExtractType,
    "top_bottom": this.activeTabId === 4 ? [this.selectedTopColumn,this.topAggregate,this.topLimit,this.topType] : null
}
  this.workbechService.filterPut(obj).subscribe({next: (responce:any) => {
        console.log(responce);
        this.filterId.push(responce.filter_id);
        this.filter_id=responce.filter_id
        this.dimetionMeasure.push({"col_name":this.filterName,"data_type":this.filterType,"filter_id":responce.filter_id,"top_bottom":this.activeTabId === 4 ? ['top'] : null});
        this.isTopFilter = !this.dimetionMeasure.some((column: any) => column.top_bottom && column.top_bottom.length>0);
        this.dataExtraction();
        this.filterDataArray = [];
        this.filterDateRange = [];
        this.formatExtractType = '';
        this.selectedTopColumn = 'select';
        this.topAggregate = 'sum';
        this.topLimit = 5;
        this.topType = 'desc';
        this.isTopFilter = !this.dimetionMeasure.some((column: any) => column.top_bottom && column.top_bottom.length>0);
      },
      error: (error) => {
        console.log(error);
      }
    }
  )
  }
  filterEditGet(){
    this.filterData = [];
    const obj={
      "type_filter":"chartfilter",
      "hierarchy_id" :this.databaseId,
      "filter_id" :this.filter_id,
      "search":this.editFilterSearch
}
  this.workbechService.filterEditPost(obj).subscribe({next: (responce:any) => {
        console.log(responce);
        this.filter_id = responce.filter_id;
        this.filterName=responce.column_name;
        this.filterType=responce.data_type;
        this.filterCalculatedFieldLogic = responce.field_logic;
        this.isExclude = responce.is_exclude;
        this.formatExtractType = this.extractTypesForTab.includes(responce?.format_type) ? responce?.format_type : '';
        if(responce?.top_bottom){
          this.topType = responce?.top_bottom[3];
          this.topLimit = responce?.top_bottom[2];
          this.selectedTopColumn = responce?.top_bottom[0];
          this.topAggregate = responce?.top_bottom[1];
        }
        if(this.formatExtractType){
          this.activeTabId = 3;
        }
        else if(responce?.range_values && responce?.range_values.length > 0 && responce?.format_type === 'year/month/day'){
          this.activeTabId = 2;
        }
        else if(responce?.top_bottom && responce?.top_bottom.length>0){
          this.activeTabId = 4;
        }
        else {
          this.activeTabId = 1;
        }
        responce.result.forEach((element:any) => {
          this.filterData.push(element);
        });
        this.filterData.forEach((filter:any)=>{
          if(filter.selected){
            this.filterDataArray.push(filter.label);
          }
        })
        if(this.dateList.includes(responce.data_type) && responce?.range_values){
          let rawLabel = this.filterData[0].label;
          let datePart = rawLabel.split(" ")[0];
          let [year, month, day] = datePart.split("/");
          this.floor = new Date(`${year}-${month}-${day}`).getTime();

          rawLabel = this.filterData[this.filterData.length - 1].label;
          datePart = rawLabel.split(" ")[0];
          [year, month, day] = datePart.split("/");
          this.ceil = new Date(`${year}-${month}-${day}`).getTime();

          rawLabel = responce.range_values[0];
          datePart = rawLabel.split(" ")[0];
          [year, month, day] = datePart.split("/");

          this.minValue = new Date(`${year}-${month}-${day}`).getTime();

          rawLabel = responce.range_values[responce.range_values.length - 1];
          datePart = rawLabel.split(" ")[0];
          [year, month, day] = datePart.split("/");

          this.maxValue = new Date(`${year}-${month}-${day}`).getTime();

          this.options = {
            floor: this.floor,
            ceil: this.ceil,
            step: 24 * 60 * 60 * 1000,
            showSelectionBar: true,
            selectionBarGradient: {
              from: '#5a66f1',
              to: '#5a66f1',
            },
            translate: (value: number): string => {
              return new Date(value).toLocaleDateString();
            }
          };

          this.updateDateRange();
          this.filterDateRange = [];
        }
      },
      error: (error) => {
        console.log(error);
      }
    }
  )
  }
  filterDataEditArray = [] as any;
  filterDataEditPut(){
    this.sortedData = [];
    const obj={
      "filter_id": this.filter_id,
      "hierarchy_id": this.databaseId,
      "queryset_id": this.qrySetId,
      "type_of_filter":"sheet",
      "datasource_querysetid" : this.filterQuerySetId,
      "range_values": this.filterDateRange,
      "select_values":this.filterDataArray,
      "col_name":this.filterName,
      "data_type":this.filterType,
      "is_exclude":this.isExclude,
      "field_logic" : this.filterCalculatedFieldLogic?.length > 0 ? this.filterCalculatedFieldLogic : null,
      "is_calculated": this.filterType == 'calculated' ? true : false,
      "format_date" : this.activeTabId === 2 ? 'year/month/day' :this.formatExtractType,
      "top_bottom": this.activeTabId === 4 ? [this.selectedTopColumn,this.topAggregate,this.topLimit,this.topType] : null
  }
    this.workbechService.filterPut(obj).subscribe({next: (responce:any) => {
          console.log(responce);
          this.isTopFilter = !this.dimetionMeasure.some((column: any) => column.top_bottom && column.top_bottom.length>0);
          this.dataExtraction();
          this.filterDataArray = [];
          this.filterDateRange = [];
          this.isAllSelected = false;
          this.selectedTopColumn = 'select';
          this.topAggregate = 'sum';
          this.topLimit = 5;
          this.topType = 'desc';
        },
        error: (error) => {
          console.log(error);
        }
      }
    )
  }
  filterDelete(index:any,filterId:any){
  this.sortedData = [];
  this.workbechService.filterDelete(filterId).subscribe({next: (responce:any) => {
        this.dimetionMeasure.splice(index, 1);
       let index1 = this.filterId.findIndex((i:any) => i == filterId);
         this.filterId.splice(index1, 1);
         this.isTopFilter = !this.dimetionMeasure.some((column: any) => column.top_bottom && column.top_bottom.length>0);
         this.dataExtraction();
      },
      error: (error) => {
        console.log(error);
      }
    }
  )
  }
  openSuperScaledModal(modal: any,type:any) {
    if(type === undefined){
      this.measureValue = '-Select-';
    }else{
    this.measureValue = type;
    }
    console.log(this.measureValue)
    this.modalService.open(modal, {
      centered: true,
      windowClass: 'animate__animated animate__zoomIn',
    });
}
openSuperScalededitFilter(modal: any,data:any) {
  this.editFilterSearch = '';
  this.modalService.open(modal, {
    centered: true,
    windowClass: 'animate__animated animate__zoomIn',
  });
  console.log(data);
  this.filterType = data.data_type;
  if ('filter_id' in data) {
    this.filterName = data.col_name;
    this.filter_id = data.filter_id;
  }
  else{
    this.filterName = data.column;
    this.dimetionMeasure.forEach((column:any)=>{
      if(column.col_name === data.column){
        this.filter_id = column.filter_id;
      }
    })
  }
  this.filterEditGet();
}
filterAdded : boolean = false;
isTopFilter : boolean = true;
editFilterCheck(data:any){
  if(this.dimetionMeasure.length>0){
    this.filterAdded = this.dimetionMeasure.some((column: any) => column.col_name === data);
    this.isTopFilter = !this.dimetionMeasure.some((column: any) => column.top_bottom && column.top_bottom.length>0);
  }
  else{
    this.filterAdded = false;
    this.isTopFilter = true;
  }
}
gotoDashboard(){
  // if(!this.fromFileId){
  const encodedDatabaseId = btoa(this.databaseId.toString());
  const encodedQuerySetId = btoa(this.qrySetId.toString());
  this.router.navigate(['/analytify/sheetscomponent/sheetsdashboard'+'/'+ encodedDatabaseId +'/' +encodedQuerySetId])
  // }
// if(this.fromFileId){
//   const encodedFileId = btoa(this.fileId.toString())
//   const encodedQuerySetId = btoa(this.qrySetId.toString());
//   this.router.navigate(['/insights/sheetscomponent/sheetsdashboard/fileId'+'/'+ encodedFileId +'/' +encodedQuerySetId])
// }
}
viewDashboard(){
  // if(this.fromFileId){
  //   const encodedDatabaseId = btoa(this.fileId.toString());
  //   const encodedQuerySetId = btoa(this.qrySetId.toString());
  //   const encodedDashboardId = btoa(this.dashboardId.toString());
  //   this.router.navigate(['insights/home/sheetsdashboard'+'/'+ encodedDatabaseId +'/' +encodedQuerySetId +'/' + encodedDashboardId])

  // } else {
  const encodedDatabaseId = btoa(this.databaseId.toString());
  const encodedQuerySetId = btoa(this.qrySetId.toString());
  const encodedDashboardId = btoa(this.dashboardId.toString());
  this.router.navigate(['analytify/home/sheetsdashboard'+'/'+ encodedDatabaseId +'/' +encodedQuerySetId +'/' + encodedDashboardId])
  // }

}

marksColor2(color:any){
console.log(color)
}
rename(index:any,name:any,event:any){
  this.oldColumn = '';
this.oldColumn = name;
//let rename = this.draggedColumnsData.indexOf((i:any) => i === index);
//console.log(rename[0])
let reName=`${this.draggedColumnsData.at(index)}`;
console.log(reName.split(',')[0])
}

renameColumn(index:any,column:any,event:any){
  this.newColumn = '';
  this.newColumn = column;
  if (event.keyCode === 13) {
  this.renameColumns();
 }
}
renameColumns(){
  const obj={
    "database_id":this.databaseId,
    "queryset_id":this.qrySetId,
    "old_col_name" :this.oldColumn,
    "new_col_name":this.newColumn
}
  this.workbechService.renameColumn(obj).subscribe({next: (responce:any) => {
        console.log(responce);
        this.columnsData();
      },
      error: (error) => {
        console.log(error);
      }
    }
  )
 }

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
    toolbar: ['heading', '|', 'bold', 'italic', 'underline','|', 'fontSize', 'fontFamily', 'fontColor', '|', 'alignment'],
    plugins: [
      Bold, Essentials, Italic, Mention, Paragraph, Undo, Font, Alignment, Underline, RemoveFormat, SelectAll, Heading],
  };

  // editorConfig1 = {
  //   toolbar: [],
  //   plugins: [
  //     Bold, Essentials, Italic, Mention, Paragraph, Undo, Font, Alignment, Underline, RemoveFormat, SelectAll, Heading],
  // };

  toggleEditor() {
    this.editor = !this.editor;
  }
  updateSheetName() {
    // const inputElement = document.getElementById('htmlContent') as HTMLInputElement;
    // if (inputElement) {
    //   inputElement.innerHTML = this.sheetTagName;
    //   inputElement.style.paddingTop = '1.5%';
    // }
    this.sheetTagTitle = this.sanitizer.bypassSecurityTrustHtml(this.sheetTagName);
    const parser = new DOMParser();
    const doc = parser.parseFromString(this.sheetTagName, 'text/html');
    this.sheetTitle = doc.body.textContent+'';
  }
  allignmentChange(event: any, section: any) {
    let object : any = {};
    if (section === 'dimension') {
      this.dimensionAlignment = event;
    }
    else {
      this.measureAlignment = event;
    }
  }
  toggleSwitch(type : string) {
    let object:any;
    if(type === 'banding'){
      this.bandingSwitch = !this.bandingSwitch;
      if(!this.bandingSwitch){
        this.color1 = undefined;
        this.color2 = undefined;
      }
    }
    else if(type === 'xlabel'){
      this.xLabelSwitch = !this.xLabelSwitch;
    }
    else if(type === 'ylabel'){
      this.yLabelSwitch = !this.yLabelSwitch;
    }
    else if(type === 'xgrid'){
      this.xGridSwitch = !this.xGridSwitch;
    }
    else if(type === 'ygrid'){
      this.yGridSwitch = !this.yGridSwitch;
    }
    else if(type === 'legend'){
      this.legendSwitch = !this.legendSwitch;
    }
    else if(type === 'dataLabels'){
      this.dataLabels = !this.dataLabels;
    }
    else if(type === 'label'){
      this.label = !this.label;
    }
    else if(type === 'distributed'){
      this.isDistributed = !this.isDistributed;
    }
  }
  enableZoom(){
    this.isZoom = !this.isZoom;
  }

  formattedData : any[] = [];
  formatNumber(value: number): string {
    let formattedNumber = value+'';

    // if (this.displayUnits !== 'none') {
      switch (this.displayUnits) {
        case 'K':
          formattedNumber = (value / 1_000).toFixed(this.decimalPlaces) + 'K';
          break;
        case 'M':
          formattedNumber = (value / 1_000_000).toFixed(this.decimalPlaces) + 'M';
          break;
        case 'B':
          formattedNumber = (value / 1_000_000_000).toFixed(this.decimalPlaces) + 'B';
          break;
        case 'G':
          formattedNumber = (value / 1_000_000_000_000).toFixed(this.decimalPlaces) + 'G';
          break;
        case 'none':
          formattedNumber = (value/1).toFixed(this.decimalPlaces);
          break;
      }
    // }
    this.formattedData.push(this.prefix + formattedNumber + this.suffix);
    return this.prefix + formattedNumber + this.suffix;
  }

  formatKPINumber() {
    let formattedNumber = this.tablePreviewRow[0].result_data[0]+'';
    let value = this.tablePreviewRow[0].result_data[0];
    if (this.KPIDisplayUnits !== 'none') {
      switch (this.KPIDisplayUnits) {
        case 'K':
          formattedNumber = (value / 1_000).toFixed(this.KPIDecimalPlaces) + 'K';
          break;
        case 'M':
          formattedNumber = (value / 1_000_000).toFixed(this.KPIDecimalPlaces) + 'M';
          break;
        case 'B':
          formattedNumber = (value / 1_000_000_000).toFixed(this.KPIDecimalPlaces) + 'B';
          break;
        case 'G':
          formattedNumber = (value / 1_000_000_000_000).toFixed(this.KPIDecimalPlaces) + 'G';
          break;
        case '%':
          this.KPIPercentageDivisor = Math.pow(10, Math.floor(Math.log10(value)) + 1); // Get next power of 10
          let percentageValue = (value / this.KPIPercentageDivisor) * 100; // Convert to percentage
          formattedNumber = percentageValue.toFixed(this.KPIDecimalPlaces) + ' %'; // Keep decimals
          break;
      }
    } else {
      formattedNumber = (value).toFixed(this.KPIDecimalPlaces)
    }

    this.KPINumber = this.KPIPrefix + formattedNumber + this.KPISuffix;
  }
  numberPopupTrigger(){
    this.numberPopup = !this.numberPopup;
  }

  updateTableFormat(){

  }

 getChartSuggestions() {
  
  const obj ={
    id:this.qrySetId
  }

  this.workbechService.getServerTablesList(obj).subscribe(
    data => {
      console.log(data)
      if (Array.isArray(data.data)) {
        // Handle the case where data.data is an array
        console.log(data.data.length);
        this.chartSuggestions = data.data;
        this.errorMessage = '';
      } else if (typeof data.data === 'string') {
        // Handle the case where data.data is a message
        console.log('Message:', data.data);
        // Optionally handle the message case, for example by showing it to the user
        this.chartSuggestions = [];
        this.errorMessage = data.data;
      } else {
        // Handle unexpected data format
        console.error('Unexpected data format:', data.data);
        this.chartSuggestions = [];
        this.errorMessage = 'Unexpected data format';
      }

    },
    error => {
      const apiKey = localStorage.getItem('API_KEY');
      if (error.error.message === 'Queryset ID is required'){
        this.chartSuggestions = null;
        this.errorMessage = ""
      }
      else if  (!apiKey || apiKey.trim() === '') {
        // Store the current URL before navigating to the configure page
        localStorage.setItem('previousUrl', this.router.url);
        this.chartSuggestions = null;
        // API Key is missing or empty, show the message and navigate to the configure page on click
        // this.errorMessage = `The GPT API Key is missing. Please <a href="/insights/configure-page/configure">add the GPT API Key</a> to proceed.`;
        this.errorMessage1 = 'the GPT API key is missing. Please'
        // this.router.navigate(['/insights/configure-page/configure']);
      } else {
        // Handle other errors
        console.log("Error:", error.message);
        this.chartSuggestions = null;
        this.errorMessage = `We're experiencing a <b>'data-ruption'</b>! Please reconnect to the database and try again.`;
        console.error(error);
      }
    }
  );
}
routeConfigure(){
  this.router.navigate(['/analytify/configure-page/configure'])
}
fetchChartData(chartData: any){
  this.databaseId = chartData.hierarchy_id;
          this.qrySetId = chartData.queryset_id;
          this.draggedColumnsData = chartData.col;
          this.draggedRowsData = chartData.row;
          this.draggedColumns = chartData.columns;
          this.draggedRows = chartData.rows;
          this.filterId =[];
          this.filterQuerySetId = chartData.datasource_quertsetid,
          // this.sheetfilter_querysets_id = null;
          
          console.log("This is ShaetData",chartData)
          this.sheetTitle = chartData.chart_title;
          this.sheetTagName = chartData.chart_title;
          if (chartData.chart_type.toLowerCase().includes("bar")){
            this.chartDisplay(false,true,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,6);
          }else if (chartData.chart_type.toLowerCase().includes("pie")){
            this.chartDisplay(false,false,false,false,true,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,24);
          }else if (chartData.chart_type.toLowerCase().includes("line")){
            this.chartDisplay(false,false,false,true,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,13);
          }else if (chartData.chart_type.toLowerCase().includes("area")){
            this.chartDisplay(false,false,true,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,17);
          }else if (chartData.chart_type.toLowerCase().includes("donut")){
            this.chartDisplay(false,false,false,false,false,false,false,false,false,false,false,true,false,false,false,false,false,false,false,false,10);
          }
          this.dataExtraction();

}
customizechangeChartPlugin() {
  if (this.selectedChartPlugin == 'apex') {
    this.isApexCharts = true;
    this.isEChatrts = false;
  } else {
    this.isApexCharts = false;
    this.isEChatrts = true;
  }
  // this.reAssignChartData();
}
  changeChartPlugin(value:any) {
    this.selectedChartPlugin = value;
    if (this.selectedChartPlugin == 'apex') {
      this.isApexCharts = true;
      this.isEChatrts = false;
    } else {
      this.isApexCharts = false;
      this.isEChatrts = true;
    }
    // if(this.retriveDataSheet_id){
    //   if((this.sheetResponce.isEChart && this.isEChatrts && (this.sheetChartId === this.chartId)) || (this.sheetResponce.isApexChart && this.isApexCharts && (this.sheetChartId === this.chartId))){
    //     this.sheetRetrive(false);
    //   } else {
    //     this.reAssignChartData();
    //     this.resetCustomizations();
    //   }
    // } else{
    //   this.reAssignChartData();
    //   this.resetCustomizations();
    // }
    // this.reAssignChartData();
  }


  marksColor(color: any, colorCase: number) { //1 for x,3 for y for grid line color
    console.log(color)
    switch (colorCase) {
      case 1: this.xGridColor = color; break;
      case 2: this.yLabelColor = color; break;
      case 3: this.yGridColor = color; break;
      case 4: this.color = color; break;
      case 5: this.xLabelColor = color; break;
      case 6: this.backgroundColor = color; break;
    }
     // this.updateEchartOptions();
  }

  setCustomizeOptions(data: any) {
    this.isZoom = data.isZoom ?? true;
    this.xGridColor = data.xGridColor ?? '#2392c1';
    this.xGridSwitch = data.xGridSwitch ?? false;
    this.xLabelSwitch = data.xLabelSwitch ?? true;
    this.xLabelColor = data.xLabelColor ?? '#2392c1';
    this.yLabelSwitch = data.yLabelSwitch ?? true;
    this.yGridColor = data.yGridColor ?? '#2392c1';
    this.yGridSwitch = data.yGridSwitch ?? false;
    this.yLabelColor = data.yLabelColor ?? '#2392c1';
    this.xLabelFontFamily = data.xLabelFontFamily ?? 'sans-serif';
    this.xLabelFontSize = data.xLabelFontSize ?? 12;
    this.xlabelFontWeight = data.xlabelFontWeight ?? 400;
    this.backgroundColor = data.backgroundColor ?? '#fff';
    this.color = data.color ?? '#2392c1';
    this.selectedColorScheme = data.selectedColorScheme ?? ['#00d1c1', '#30e0cf', '#48efde', '#5dfeee', '#fee74f', '#feda40', '#fecd31', '#fec01e', '#feb300'],
    this.ylabelFontWeight = data.ylabelFontWeight ?? 400;
    this.isBold = data.isBold ?? false;
    this.isXlabelBold = data.isXlabelBold ?? false;
    this.isYlabelBold = data.isYlabelBold ?? false;
    this.isTableHeaderBold = data.isTableHeaderBold ?? false;
    this.isTableDataBold = data.isTableDataBold ?? false;
    this.yLabelFontFamily = data.yLabelFontFamily ?? 'sans-serif';
    this.yLabelFontSize = data.yLabelFontSize ?? 12;
    this.bandingSwitch = data.bandingSwitch ?? false;
    this.backgroundColorSwitch = data.backgroundColorSwitch ?? false;
    this.chartColorSwitch = data.chartColorSwitch ?? false;
    this.barColorSwitch = data.barColorSwitch ?? false;
    this.lineColorSwitch = data.lineColorSwitch ?? false;
    this.gridLineColorSwitch = data.gridLineColorSwitch ?? false;
    this.xLabelColorSwitch = data.xLabelColorSwitch ?? false;
    this.xGridLineColorSwitch = data.xGridLineColorSwitch ?? false;
    this.yLabelColorSwitch = data.yLabelColorSwitch ?? false;
    this.yGridLineColorSwitch = data.yGridLineColorSwitch ?? false;
    this.bandingColorSwitch = data.bandingColorSwitch ?? false;
    this.kpiColorSwitch = data.kpiColorSwitch ?? false;
    this.funnelColorSwitch = data.funnelColorSwitch ?? false;
    this.color1 = data.color1 ?? undefined;
    this.color2 = data.color2 ?? undefined;
    this.kpiColor = data.kpiColor ?? '#000000';
    this.barColor = data.barColor ?? '#4382f7';
    this.lineColor = data.lineColor ?? '#38ff98';
    this.GridColor = data.GridColor ?? '#089ffc';
    this.legendSwitch = data.legendSwitch ?? true;
    this.dataLabels = data.dataLabels ?? true;
    this.label = data.label ?? true;
    this.donutSize = data.donutSize ?? 50;
    this.isDistributed = data.isDistributed ?? true;
    this.kpiFontSize = data.kpiFontSize ?? 3;
    this.minValueGuage = data.minValueGuage ?? 0;
    this.maxValueGuage = data.maxValueGuage ?? 100;
    this.donutDecimalPlaces = data.donutDecimalPlaces ?? 2;
    this.decimalPlaces = data.decimalPlaces ?? 2;
    this.legendsAllignment = data.legendsAllignment ?? 'bottom';
    this.displayUnits = data.displayUnits || 'none';
    this.suffix = data.suffix ?? '';
    this.prefix = data.prefix ?? '';
    this.dataLabelsFontFamily = data.dataLabelsFontFamily ?? 'sans-serif';
    this.dataLabelsFontSize = data.dataLabelsFontSize ?? '12px';
    this.dataLabelsFontPosition = data.dataLabelsFontPosition ?? 'top';
    this.measureAlignment = data.measureAlignment ?? 'center';
    this.dimensionAlignment = data.dimensionAlignment ?? 'center';
    this.dimensionColor = data.dimensionColor ?? '#2392c1';
    this.measureColor = data.measureColor ?? '#2392c1';
    this.dataLabelsColor = data.dataLabelsColor ?? '#0a5a2';
    this.tableDataFontFamily = data.tableDataFontFamily ?? 'sans-serif';
    this.tableDataFontSize = data.tableDataFontSize ?? '12px';
    this.tableDataFontWeight = data.tableDataFontWeight ?? 400;
    this.tableDataFontStyle = data.tableDataFontStyle ?? 'normal';
    this.tableDataFontDecoration = data.tableDataFontDecoration ?? 'none';
    this.tableDataFontColor = data.tableDataFontColor ?? '#000000';
    this.tableDataFontAlignment = data.tableDataFontAlignment ?? 'left';
    this.headerFontFamily = data.headerFontFamily ?? "'Arial', sans-serif";
    this.headerFontSize = data.headerFontSize ?? '16px';
    this.headerFontWeight = data.headerFontWeight ?? 700;
    this.headerFontStyle = data.headerFontStyle ?? 'normal';
    this.headerFontDecoration = data.headerFontDecoration ?? 'none';
    this.headerFontColor = data.headerFontColor ?? '#000000'
    this.headerFontAlignment = data.headerFontAlignment ?? 'left';
    this.sortType = data.sortType ?? 0;
    this.dataLabelsLineFontPosition =data.dataLabelsLineFontPosition ?? 'top';
    this.dataLabelsBarFontPosition = data.dataLabelsBarFontPosition ?? 'top';
    this.topLegend = data.topLegend === '' ? null : data.topLegend;
    this.leftLegend = data.leftLegend === '' ? null : data.leftLegend;
    this.legendOrient = data.legendOrient === '' ? null : data.legendOrient
    this.bottomLegend = data.bottomLegend === '' ? null : data.bottomLegend
    this.rightLegend = data.rightLegend === '' ? null : data.rightLegend
    this.sortColumn = data.sortColumn ?? 'select';
    this.locationDrillDownSwitch = data.locationDrillDownSwitch ?? false;
    this.KPIDecimalPlaces = data.KPIDecimalPlaces ?? 2,
    this.KPIDisplayUnits = data.KPIDisplayUnits ?? 'none',
    this.KPIPrefix = data.KPIPrefix ?? '',
    this.KPISuffix = data.KPISuffix ?? ''
  }

  resetCustomizations(){
    this.isZoom = false;
    this.xGridColor = '#2392c1';
    this.xGridSwitch = false;
    this.xLabelSwitch = true;
    this.xLabelColor = '#2392c1';
    this.yLabelSwitch = true;
    this.yGridColor = '#2392c1';
    this.yGridSwitch = false;
    this.yLabelColor = '#2392c1';
    this.xLabelFontFamily = 'sans-serif';
    this.xLabelFontSize = 12;
    this.xlabelFontWeight = 400;
    this.backgroundColor = '#fff';
    this.color = '#2392c1';
    this.selectedColorScheme = ['#00d1c1', '#30e0cf', '#48efde', '#5dfeee', '#fee74f', '#feda40', '#fecd31', '#fec01e', '#feb300'],
    this.ylabelFontWeight = 400;
    this.isBold = false;
    this.isTableHeaderBold = false;
    this.isTableDataBold = false;
    this.isXlabelBold = false;
    this.isYlabelBold = false;
    this.yLabelFontFamily = 'sans-serif';
    this.yLabelFontSize = 12;
    this.bandingSwitch = false;
    this.backgroundColorSwitch = false;
    this.chartColorSwitch = false;
    this.barColorSwitch = false;
    this.lineColorSwitch = false;
    this.gridLineColorSwitch = false;
    this.xLabelColorSwitch = false;
    this.xGridLineColorSwitch = false;
    this.yLabelColorSwitch = false;
    this.yGridLineColorSwitch = false;
    this.bandingColorSwitch = false;
    this.kpiColorSwitch = false;
    this.funnelColorSwitch = false;
    this.color1 = undefined;
    this.color2 = undefined;
    this.kpiColor = '#000000';
    this.barColor = '#4382f7';
    this.lineColor = '#38ff98';
    this.GridColor = '#089ffc';
    this.legendSwitch = true;
    this.dataLabels = true;
    this.label = true;
    this.donutSize = 50;
    this.isDistributed = true;
    this.kpiFontSize = '3';
    this.minValueGuage = 0;
    this.maxValueGuage = 100;
    this.donutDecimalPlaces = 2;
    // this.decimalPlaces = 0;
    this.legendsAllignment = 'bottom';
    // this.displayUnits = 'none';
    // this.suffix = '';
    // this.prefix = '';
    this.dataLabelsFontFamily = 'sans-serif';
    this.dataLabelsFontSize = '12px';
    this.dataLabelsFontPosition = 'top';
    this.measureAlignment = 'center';
    this.dimensionAlignment = 'center';
    this.dimensionColor = '#2392c1';
    this.measureColor = '#2392c1';
    this.dataLabelsColor = '#2392c1';
    this.tableDataFontFamily = 'sans-serif';
    this.tableDataFontSize = '12px';
    this.tableDataFontWeight = 400;
    this.tableDataFontStyle = 'normal';
    this.tableDataFontDecoration = 'none';
    this.tableDataFontColor = '#000000';
    this.tableDataFontAlignment = 'left';
    this.headerFontFamily = "'Arial', sans-serif";
    this.headerFontSize = '16px';
    this.headerFontWeight = 700;
    this.headerFontStyle = 'normal';
    this.headerFontDecoration = 'none';
    this.headerFontColor = '#000000'
    this.headerFontAlignment = 'left';
    this.sortType = 0;
    this.dataLabelsLineFontPosition = 'top';
    this.dataLabelsBarFontPosition = 'top';
    this.topLegend = null;
    this.leftLegend = 'center';
    this.legendOrient = 'horizontal'
    this.bottomLegend = '0%'
    this.rightLegend = null
    this.sortColumn = 'select';
    this.locationDrillDownSwitch = false;
    // this.KPIDecimalPlaces = 0,
    // this.KPIDisplayUnits = 'none',
    // this.KPIPrefix = '',
    // this.KPISuffix = ''
  }

  sendPrompt() {
    if (this.userPrompt.trim()) {
      const obj = {
        id: this.qrySetId,
        prompt: this.userPrompt.trim()
      };
      this.workbechService.getServerTablesList(obj).subscribe(
        data => {
          this.zone.run(() => {
            if (Array.isArray(data.data)) {
              this.chartSuggestions = data.data;
              this.errorMessage = '';
            } else if (typeof data.data === 'string') {
              this.chartSuggestions = [];
              this.errorMessage = data.data;
            } else {
              this.chartSuggestions = [];
              this.errorMessage = 'Unexpected data format';
            }
          });
        },
        error => {
          const apiKey = localStorage.getItem('API_KEY');
          if (error.error.message === 'Queryset ID is required'){
            this.chartSuggestions = null;
            this.errorMessage = ""
          }
          else if  (!apiKey || apiKey.trim() === '') {
            this.chartSuggestions = null;
            // API Key is missing or empty, show the message and navigate to the configure page
            // this.errorMessage = `The GPT API Key is missing. Please <a href="/insights/configure-page/configure">add the GPT API Key</a> to proceed.`;
            this.errorMessage1 = 'the GPT API key is missing. Please'
            // this.router.navigate(['/insights/configure-page/configure']);
          } else {
            // Handle other errors
            console.log("Error:", error.message);
            this.chartSuggestions = null;
            this.errorMessage = `We're experiencing a <b>'data-ruption'</b>! Please reconnect to the database and try again.`;
            console.error(error);
          }
        }
      );
    }
  }
  
  startVoiceRecognition() {
    const recognition = new (window as any).webkitSpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
  
    recognition.start();
  
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      this.zone.run(() => {
        this.userPrompt = transcript;
        this.sendPrompt();
      });
    };
  
    recognition.onerror = (event: any) => {
      console.error('Voice recognition error', event);
      this.zone.run(() => {
        this.errorMessage = 'Voice recognition error';
      });
    };
  
    recognition.onend = () => {
      console.log('Voice recognition ended');
    };
  }
  openSelectDashboard(modal : any){
    this.modalService.open(modal, {
      centered: true,
      windowClass: 'animate__animated animate__zoomIn',
    });
  }
  dashboardList : any[] = [];
  getDashboardsList() {
    this.workbechService.getuserDashboardsList().subscribe({
      next: (responce: any) => {
        console.log(responce);
        this.dashboardList = responce;
      },
      error: (error) => {
        console.log(error);
        Swal.fire({
          icon: 'error',
          text: error.error.message,
          width: '200px',
        })
      }
    })
  }
  async moveToDashboard(){
    if(this.selectedDashboardId > 0) {
      this.dashboardId = this.selectedDashboardId;
    }
    if(this.tabs && this.sheetList &&  this.tabs.length != this.sheetList.length){
      await this.getSheetNames();
    }
    console.log(this.dashboardId);
    let sheetIds = this.sheetList.map(sheet => sheet.id)
    let obj = {
      dashboard_id : this.dashboardId,
      sheet_ids : sheetIds
    }
    this.workbechService.addSheetToDashboard(obj).subscribe({
      next: () => {
        this.viewDashboard();
      },
      error: (error) => {
        console.log(error);
        Swal.fire({
          icon: 'error',
          text: error.error.message,
          width: '200px',
        })
      }
    })
  }
  openDateFormatModal(modal: any){
    this.modalService.open(modal, {
      centered: true,
      windowClass: 'animate__animated animate__zoomIn',
    });
  }
  dateFormat(column:any, index:any, format:any){
    if(this.selectedSortColumnData && this.selectedSortColumnData.length > 0 && this.selectedSortColumnData[0] === column.column && this.selectedSortColumnData[2] === this.draggedColumnsData[index][2]){
      this.selectedSortColumnData[2] = format;
    }
    if(format === ''){
      this.draggedColumnsData[index] = [column.column,column.data_type,format,""];
      this.draggedColumns[index] = {column:column.column,data_type:column.data_type,type:format};
     }else if(format === '-Select-'){
      this.draggedColumnsData[index] = [column.column,column.data_type,'',''];
      this.draggedColumns[index] = {column:column.column,data_type:column.data_type,type:''};
     }
     else{
      this.draggedColumnsData[index] = [column.column, "date", format,''];
      this.draggedColumns[index] = { column: column.column, data_type: column.data_type, type: format };
      console.log(this.draggedColumns);
     }
     this.dataExtraction();
  }
  dateAggregation(column:any, index:any, type:any){
    if(this.selectedSortColumnData && this.selectedSortColumnData.length > 0 && this.selectedSortColumnData[0] === column.column && this.selectedSortColumnData[2] === this.draggedColumnsData[index][2]){
      this.selectedSortColumnData[2] = type;
    }
    if (type === '') {
      this.draggedColumnsData[index] = [column.column, column.data_type, type, ''];
      this.draggedColumns[index] = { column: column.column, data_type: column.data_type, type: type };
    }
    else {
      this.draggedColumnsData[index] = [column.column, "aggregate", type, ''];
      this.draggedColumns[index] = { column: column.column, data_type: column.data_type, type: type };
      console.log(this.draggedColumns);
    }
    this.dataExtraction();
  }

  sliderOptions = {
    floor: 1,
    ceil: 20,
    step: 0.1,
    showTicks: true
  };
  getFontSize(): string {
    return `${this.kpiFontSize}rem`;
  }

  searchFilterList(){
    this.filterDataGet();
  }
  editFilterList(){
    this.filterEditGet();
  }
  drillDownColumndrop(event: CdkDragDrop<string[]>){
        console.log(event)
        let item: any = event.previousContainer.data[event.previousIndex];
        if(item && item.column) {
          this.draggedDrillDownColumns.push(item.column);
          let columnData = [item.column,item.data_type,'',''];
          this.heirarchyColumnData.push(columnData);
        }
  }
  removeDrillDownColumn(index:any,column:any){
       
    this.draggedDrillDownColumns.splice(index, 1);
    this.heirarchyColumnData.splice(index,1);
    if (index <= 0) {
      this.drillDownIndex = 0;
      this.draggedDrillDownColumns = [];
      this.drillDownObject = [];
      this.dateDrillDownSwitch = false;
      this.locationDrillDownSwitch = false;
      this.heirarchyColumnData = [];
    } else if (index <= this.drillDownIndex) {
      this.drillDownObject = this.drillDownObject.slice(0, index - 1);
      this.drillDownIndex = index - 1;
    } 
       this.dataExtraction();
      }
      draggedMeasureValuesData = [] as any;
      measureValuesdrop(event: CdkDragDrop<string[]>){
        console.log(event)
            let item: any = event.previousContainer.data[event.previousIndex];
            let copy: any = JSON.parse(JSON.stringify(item));
          let element: any = {};
          for(let attr in copy) {
          if (attr == 'title') {
            element[attr] = copy[attr];
          } else {
            element[attr] = copy[attr];
          }
        }
        this.draggedMeasureValues.splice(event.currentIndex, 0, element);
        event.currentIndex = this.draggedMeasureValues.indexOf(element);
        const rowIndexMap = new Map((this.draggedMeasureValues as any[]).map((row, index) => [row.column, index]));
        if(element.data_type == 'calculated') {
          this.draggedMeasureValuesData.splice(event.currentIndex, 0,[element.column, element.data_type, "", element.field_name]);
        } else {
        this.draggedMeasureValuesData.splice(event.currentIndex, 0,[element.column, element.data_type, "", ""]);
        }
        if (this.dateList.includes(element.data_type)) {
          this.dateFormat(element, event.currentIndex, 'year');
        } else {
          console.log('measurerows',this.draggedMeasureValuesData)
          this.dataExtraction();
        }
      }

      removemeasureValuesRow(index:any,column:any){
        this.draggedMeasureValues.splice(index, 1);
        this.draggedMeasureValuesData.splice(index, 1);
        this.dataExtraction();

      }
      toggleDateSwitch(){
            this.dateDrillDownSwitch = !this.dateDrillDownSwitch;
            this.heirarchyColumnData = [];
            if(this.dateDrillDownSwitch){
              this.draggedDrillDownColumns = ["year","quarter","month","date"];
              this.draggedDrillDownColumns.forEach((columnType:any)=>{
                let columnData = JSON.parse(JSON.stringify(this.draggedColumnsData[0]));
                columnData[2] = columnType;
                this.heirarchyColumnData.push(columnData);
              });
              console.log(this.heirarchyColumnData);
              this.drillDownIndex = 0;
            } else {
              this.drillDownIndex = 0;
              this.draggedDrillDownColumns = [];
              this.drillDownObject = [];
            }
             
            this.dataExtraction();
         }

  toggleLocationSwitch(onColumnRemove : boolean) {
    this.heirarchyColumnData = [];
    if(onColumnRemove) {
    this.locationDrillDownSwitch = !this.locationDrillDownSwitch;
    }
    if (this.locationDrillDownSwitch) {
      this.draggedDrillDownColumns = this.locationHeirarchyList
  .map((hierarchy) =>
    this.tableColumnsData
      .flatMap((columns: any) => columns?.dimensions || []) // Flatten dimensions
      .find((dimension: any) => dimension?.column?.toLowerCase() === hierarchy) // Match the hierarchy
  )
  .filter((dimension: any) => dimension) // Remove undefined results for unmatched items
  .map((dimension: any) => dimension?.column);
      let dataTypes : any [] = [];
      this.draggedDrillDownColumns.map((drillDown : any) => {
        let matchedColumn = this.tableColumnsData.flatMap((table : any) =>
          table.dimensions.filter((dim : any) => dim.column.toLowerCase() === drillDown.toLowerCase())
        )[0];
        dataTypes.push(matchedColumn.data_type);
      });
      this.draggedDrillDownColumns.forEach((column: any,index: any) => {
        let columnData = JSON.parse(JSON.stringify(this.draggedColumnsData[0]));
        columnData[0] = column;
        columnData[1] = dataTypes[index];
        this.heirarchyColumnData.push(columnData);
      });
      console.log(this.heirarchyColumnData);
      this.drillDownIndex = 0;
    } else {
      this.drillDownIndex = 0;
      this.draggedDrillDownColumns = [];
      this.drillDownObject = [];
    }

    this.dataExtraction();
  }
        
          callDrillDown(){
            this.dataExtraction();
          }
        
          goDrillDownBack(){
            // if(this.isMapChartDrillDown && this.drillDownIndex === 1){
            //   this.map = true;
            //   this.bar = false;
            //   this.chartId = 29;
            //   this.chartType = 'map';
            //   this.isMapChartDrillDown = false;
            // }
            if(this.drillDownIndex > 0) {
              this.drillDownIndex--;
              this.drillDownObject.pop();
              this.callDrillDown();
            }         
          }
  
  changeLegendsAllignment(allignment:any){
    this.legendsAllignment = allignment;
    if(allignment === 'top'){
      this.topLegend= 'top',
      this.leftLegend= 'center',
      this.legendOrient= 'horizontal'
      this.bottomLegend = '',
      this.rightLegend = ''
    }
    if(allignment === 'bottom'){
      this.bottomLegend= '0%', 
          this.leftLegend= 'center', 
          this.legendOrient= 'horizontal'
          this.topLegend='',
          this.rightLegend =''

    }
    if(allignment === 'left'){
      this.leftLegend= '0%', 
      this.topLegend = 'center', 
      this.legendOrient= 'vertical'
      this.rightLegend = '',
      this.bottomLegend =''
    }
    if(allignment === 'right'){
      this.rightLegend= '0%', 
      this.topLegend= 'center', 
      this.legendOrient= 'vertical'
      this.leftLegend = '',
      this.bottomLegend = ''
    }
  }

  setOriginalData(){
        if(this.bar){//bar
          if(!this.originalData){
            this.originalData = {categories: this.chartsColumnData , data:this.chartsRowData };
          }
        }
        else if(this.pie){//pie
          if(!this.originalData){
            this.originalData = {categories: this.chartsColumnData , data:this.chartsRowData };
          }
        }
        else if(this.donut){//pie
          if(!this.originalData){
            this.originalData = {categories: this.chartsColumnData , data:this.chartsRowData };
          }
        }
        if(this.map){//map
          if(!this.originalData){
            this.originalData = {categories: this.dualAxisColumnData , data:this.dualAxisRowData }
          }
        }
      }     
      viewQuery(modal:any){
        this.modalService.open(modal, {
          centered: true,
          windowClass: 'animate__animated animate__zoomIn',
          size: 'lg'
        });
      }
      copyQuery(){
        if (navigator.clipboard) {
          navigator.clipboard.writeText(this.tablePaginationCustomQuery).then(() => {
            console.log(this.tablePaginationCustomQuery);
            this.toasterService.success('Query Copied', 'success', { positionClass: 'toast-top-right' });
          }).catch(err => {
            console.error('Could not copy text: ', err);
            this.fallbackCopyTextToClipboard(this.tablePaginationCustomQuery);
          });
        } else {
          // Fallback if navigator.clipboard is not available
          this.fallbackCopyTextToClipboard(this.tablePaginationCustomQuery);
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
            this.toasterService.success('Query Copied', 'success', { positionClass: 'toast-top-right' });
          } else {
            console.error('Fallback: Could not copy text');
          }
        } catch (err) {
          console.error('Fallback: Unable to copy', err);
        }
        document.body.removeChild(textArea);
      }
      donutDecimalPlaces: number = 2;

      setDataLabelsFontStyle(fontStyle:any){
        if(fontStyle === 'B'){
          this.isBold = !this.isBold;
        }
        else if(fontStyle === 'I'){
          this.isItalic = !this.isItalic;
        }
        else if(fontStyle === 'U'){
          this.isUnderline = !this.isUnderline;
        }
      }
      selectedElement!: HTMLElement;
      dataLabelsFontColor(event:any){
        if (this.selectedElement) {
          this.selectedElement.style.border = 'none';
        }
        const element = event.target as HTMLElement;
        this.selectedElement = event.target as HTMLElement;
        this.selectedElement.style.border = '2px solid var(--primary-color)';
        const color = window.getComputedStyle(element).backgroundColor;
        this.dataLabelsColor = color;
        element.style.border = `1px solid black`;
        this.selectedElement = element;
      }
      setDataLabelsFontPosition(position:any){
        this.dataLabelsFontPosition = position;
      }
      setDataLabelsBarFontPosition(position:any){
        this.dataLabelsBarFontPosition = position;
      }
      setDataLabelsLineFontPosition(position:any){
        this.dataLabelsLineFontPosition = position;
      }
      resetChartColor(){
        this.color = '#2392c1';
        this.barColor = '#4382F7';
        this.lineColor = '#38FF98';
        this.marksColor2(this.color);
      }
      resetBandingColor(){
        this.color1 = '#d4d3d2';
        this.color2 = '#ffffff'; 
      }
      resetGridColor(){
        this.GridColor = '#0f0f0f';
      }
      resetBackgroundColor(){
        this.backgroundColor = '#ffffff';
      }
      resetKpiColor(){
        this.kpiColor = '#0f0f0f';
      }
      resetEchartXGridColor(){
        this.xGridColor = '#0f0f0f';
        this.marksColor(this.xGridColor,1)
      }
      resetEchartYGridColor(){
        this.yGridColor = '#0f0f0f';
        this.marksColor(this.yGridColor,3)
      }
      sheetNotSaveAlert(): Promise<boolean> {
        // if (this.goToSheetButtonClicked) {
        //   // If the "Go to Sheet" button is clicked, skip the alert
        //   return Promise.resolve(true);
        // }
        this.loaderService.hide();
        return Swal.fire({
          position: "center",
          icon: "warning",
          title: "Your work has not been saved, Do you want to continue?",
          showConfirmButton: true,
          showCancelButton: true,
          confirmButtonText: 'Yes',
          cancelButtonText: 'No',
        }).then((result) => {
          if (result.isConfirmed) {
            // User clicked "Yes", allow navigation
            return true;
          } else {
            // User clicked "No", prevent navigation
            // this.loaderService.hide();
            return false;
          }
        });
      }
      canNavigate(): boolean {
        // This is handled in the functional guard
        return this.retriveDataSheet_id ? false:((this.draggedColumns.length>0 || this.draggedRows.length>0)?true:false);
      }

      getSheetList(){
        const obj = {
          "server_id": this.databaseId,
          "queryset_id": this.qrySetId,
        }
        this.workbechService.getSheetNames(obj).subscribe({
          next: (responce: any) => {
            this.tabs = responce.data;
            // (responce.data as any[]).forEach((sheet,index)=>{
            //   this.tabs.push(sheet);
              // if(sheet.id === this.retriveDataSheet_id){
              //   this.selectedTabIndex = index;
              // }
            // });
          },
          error: (error) => {
            console.log(error);
          }
      })
    }

    setChartType(){
      this.selectedChartPlugin = localStorage.getItem('chartType')+'';
      this.changeChartPlugin(this.selectedChartPlugin);
    }
    dimensionsColorChange(event:any){
      if (this.selectedElement) {
        this.selectedElement.style.border = 'none';
      }
        const element = event.target as HTMLElement;
        this.selectedElement = event.target as HTMLElement;
        this.selectedElement.style.border = '2px solid var(--primary-color)';
        const color = window.getComputedStyle(element).backgroundColor;
        this.dimensionColor = color;
      
    }
    measuresColorChange(event:any){
      if (this.selectedElement) {
        this.selectedElement.style.border = 'none';
      }
        const element = event.target as HTMLElement;
        this.selectedElement = event.target as HTMLElement;
        this.selectedElement.style.border = '2px solid var(--primary-color)';
        const color = window.getComputedStyle(element).backgroundColor;
        this.measureColor = color;
      
    }

    // updateChart(heatMap?{dataLabels:{formatter: this.formatNumber.bind(this)}}:{ yaxis: {labels: {formatter: this.formatNumber.bind(this)}}})

    fetchCalculatedFields(id : any){
      this.workbechService.fetchCalculatedFields(id).subscribe({
        next: (response: any) => {
          this.calculatedFieldId = id;
          this.isEditCalculatedField = true;
          this.calculatedFieldLogic = response[0].actual_dragged_logic;
          this.calculatedFieldName = response[0].field_name;
          this.calculatedFieldFunction = response[0].functionName;
          this.nestedCalculatedFieldData = response[0].nestedFunctionName;
        },
        error: (error) => {
          console.log(error);
        }
      })
    }

    dropCalculatedField(tableName: string , columnName : string){
      let regex;
      let hasContentInsideParentheses;
      switch(this.nestedCalculatedFieldData) {
        case 'abs': 
          this.calculatedFieldLogic = 'ABS("' + tableName + '"."' + columnName + '")';
        break; 
        case 'ceiling':
          this.calculatedFieldLogic = 'CEILING("' + tableName + '"."' + columnName + '")';
          break; 
        case 'floor': 
        this.calculatedFieldLogic = 'FLOOR("' + tableName + '"."' + columnName + '")';
        break; 
        case 'round':
        this.calculatedFieldLogic = 'ROUND("' + tableName + '"."' + columnName + '")';
           break; 
        case 'left': 
        regex = /^LEFT\(\s*[^,]*\s*,\s*[^)]*\s*\)$/;
        this.calculatedFieldLogic.trim();
        if (!this.calculatedFieldLogic.startsWith('LEFT(') || !this.calculatedFieldLogic.endsWith(')') || !regex.test(this.calculatedFieldLogic)) {
          this.isValidCalculatedField = false;
          this.validationMessage = "Invalid Syntax.";
        } else{
        this.calculatedFieldLogic = this.calculatedFieldLogic.trim();
        const params = this.calculatedFieldLogic.slice(5, -1).trim(); // Removes 'LEFT(' and ')'
        const [param1, param2] = params.split(',');
        if (param2 === undefined) {
          this.isValidCalculatedField = false;
          this.validationMessage = "Missing Parameters.";
        }
        this.calculatedFieldLogic = "LEFT("+'"'+tableName+'"."'+columnName+'",'+param2+")";    
      }
        break; 
        case 'right': 
        this.calculatedFieldLogic.trim();
        regex = /^RIGHT\(\s*[^,]*\s*,\s*[^)]*\s*\)$/;
        if (!this.calculatedFieldLogic.startsWith('RIGHT(') || !this.calculatedFieldLogic.endsWith(')') || !regex.test(this.calculatedFieldLogic)) {
          this.isValidCalculatedField = false;
          this.validationMessage = "Invalid Syntax.";
        } else{
        this.calculatedFieldLogic = this.calculatedFieldLogic.trim();
        const params = this.calculatedFieldLogic.slice(6, -1).trim(); // Removes 'LEFT(' and ')'
        const [param1, param2] = params.split(',');
        if (param2 === undefined) {
          this.isValidCalculatedField = false;
          this.validationMessage = "Missing Parameters.";
        }
        this.calculatedFieldLogic = "RIGHT("+'"'+tableName+'"."'+columnName+'",'+param2+")";   
      }
        break;
        case 'mid': 
        this.calculatedFieldLogic = "SUBSTRING("+'"'+tableName+'"."'+columnName+'"'+ " FROM   FOR  " + ")";
        break; 
        case 'length':
          this.calculatedFieldLogic = 'LENGTH("' + tableName + '"."' + columnName + '")';
        break; 
        case 'trim':
          this.calculatedFieldLogic = 'TRIM("' + tableName + '"."' + columnName + '")';
        break; 
        case 'upper': 
        this.calculatedFieldLogic = 'UPPER("' + tableName + '"."' + columnName + '")';
        break; 
        case 'lower': 
        this.calculatedFieldLogic = 'LOWER("' + tableName + '"."' + columnName + '")';
        break; 
        case 'replace': 
        this.calculatedFieldLogic = this.calculatedFieldLogic.trim();
        regex = /^REPLACE\(\s*([^,]*)\s*,\s*([^,]*)\s*,\s*([^,]*)\s*\)$/;
        if (!this.calculatedFieldLogic.startsWith('REPLACE(') || !this.calculatedFieldLogic.endsWith(')') || !regex.test(this.calculatedFieldLogic)) {
          this.isValidCalculatedField = false;
          this.validationMessage = "Invalid Syntax.";
        } else{
        const params = this.calculatedFieldLogic.slice(7, -1).trim(); // Removes 'LEFT(' and ')'
        const [param1, param2, param3] = params.split(',');
        if (param2 === undefined || param3 == undefined) {
          this.isValidCalculatedField = false;
          this.validationMessage = "Missing Parameters.";
        }
        this.calculatedFieldLogic = "REPLACE("+'"'+tableName+'"."'+columnName+'",'+param2+ ',' + param3 + ")";  
      } 
        break; 
        case 'split': 
        this.calculatedFieldLogic = this.calculatedFieldLogic.trim();
        regex = /^split_part\(\s*([^,]*)\s*,\s*([^,]*)\s*,\s*([^,]*)\s*\)$/;
        if (!this.calculatedFieldLogic.startsWith('split_part(') || !this.calculatedFieldLogic.endsWith(')') || !regex.test(this.calculatedFieldLogic)) {
          this.isValidCalculatedField = false;
          this.validationMessage = "Invalid Syntax.";
        } else{
        const params = this.calculatedFieldLogic.slice(10, -1).trim(); // Removes 'LEFT(' and ')'
        const [param1, param2, param3] = params.split(',');
        if (param2 === undefined || param3 == undefined) {
          this.isValidCalculatedField = false;
          this.validationMessage = "Missing Parameters.";
        }
        this.calculatedFieldLogic = "split_part("+'"'+tableName+'"."'+columnName+'",'+param2+ ',' + param3 + ")";  
      }
        break; 
        case 'find': 
        this.calculatedFieldLogic = "POSITION( '' IN "+'"'+tableName+'"."'+columnName + '"' +")";  
        break; 
        case 'dateadd':
          this.calculatedFieldLogic = '"'+tableName+'"."'+columnName + '" ' +"+ INTERVAL ''";  
        break;
        case 'datediff':
          this.calculatedFieldLogic = 'CURRENT_DATE - "'+tableName+'"."'+columnName + '"' ;
        break; 
        case 'datepart': 
        this.calculatedFieldLogic = 'DATE_PART("year", ' + '"'+ tableName +'"."'+ columnName + '")';
        break; 
        case 'now': break; 
        case 'today': break; 
        case 'parse': 
        this.calculatedFieldLogic = 'TO_CHAR("'+ tableName +'"."'+ columnName + '", "dd-mm-yyyy")';
        break; 
        case 'average':
          hasContentInsideParentheses = /\(.*[^\s)]\)/.test(this.calculatedFieldLogic);
          if (hasContentInsideParentheses) {
            let newString = '"' + tableName + '"."' + columnName + '")';
            this.calculatedFieldLogic = this.calculatedFieldLogic.replace(/\)\s*$/, ` ${newString})`);
          } else {
            this.calculatedFieldLogic = 'AVG("' + tableName + '"."' + columnName + '")';
          }
          break; 
        case 'count':
          hasContentInsideParentheses = /\(.*[^\s)]\)/.test(this.calculatedFieldLogic);
          if (hasContentInsideParentheses) {
            let newString = '"' + tableName + '"."' + columnName + '")';
            this.calculatedFieldLogic = this.calculatedFieldLogic.replace(/\)\s*$/, ` ${newString})`);
          } else {
            this.calculatedFieldLogic = 'COUNT("' + tableName + '"."' + columnName + '")';
          }
        break; 
        case 'countd':
          hasContentInsideParentheses = /\(.*[^\s)]\)/.test(this.calculatedFieldLogic);
          if (hasContentInsideParentheses) {
            let newString = '"' + tableName + '"."' + columnName + '")';
            this.calculatedFieldLogic = this.calculatedFieldLogic.replace(/\)\s*$/, ` ${newString})`);
          } else {
            this.calculatedFieldLogic = 'COUNT( DISTINCT "' + tableName + '"."' + columnName + '")';
          }
        break;
        case 'max':
          hasContentInsideParentheses = /\(.*[^\s)]\)/.test(this.calculatedFieldLogic);
          if (hasContentInsideParentheses) {
            let newString = '"' + tableName + '"."' + columnName + '")';
            this.calculatedFieldLogic = this.calculatedFieldLogic.replace(/\)\s*$/, ` ${newString})`);
          } else {
            this.calculatedFieldLogic = 'MAX("' + tableName + '"."' + columnName + '")';
          }
        break; 
        case 'min':
          hasContentInsideParentheses = /\(.*[^\s)]\)/.test(this.calculatedFieldLogic);
          if (hasContentInsideParentheses) {
            let newString = '"' + tableName + '"."' + columnName + '")';
            this.calculatedFieldLogic = this.calculatedFieldLogic.replace(/\)\s*$/, ` ${newString})`);
          } else {
            this.calculatedFieldLogic = 'MIN("' + tableName + '"."' + columnName + '")';
          }
        break; 
        case 'sum':
          hasContentInsideParentheses = /\(.*[^\s)]\)/.test(this.calculatedFieldLogic);
          if (hasContentInsideParentheses) {
            let newString = '"' + tableName + '"."' + columnName + '")';
            this.calculatedFieldLogic = this.calculatedFieldLogic.replace(/\)\s*$/, ` ${newString})`);
          } else {
            this.calculatedFieldLogic = 'SUM("' + tableName + '"."' + columnName + '")';
          }
        break; 
        
      }
    }

  calculatedFieldsDrop(event: CdkDragDrop<string[]>) {
    console.log(event)
    let item: any = event.previousContainer.data[event.previousIndex];
    if (item && item.column && item.table_name) {
      if (!(this.calculatedFieldFunction == 'logical' || this.calculatedFieldFunction == 'arithematic')) {
        this.dropCalculatedField(item.table_name, item.column); 
      } else {
        if (this.calculatedFieldLogic?.length) {
          this.calculatedFieldLogic = this.calculatedFieldLogic + '"' + item.table_name + '"."' + item.column + '"';
        } else {
          this.calculatedFieldLogic = '"' + item.table_name + '"."' + item.column + '"';
        }
      }
    }
  }

  applyCalculatedFields(event: any, ngbdropdownevent: any) {
    if (!(this.calculatedFieldFunction == 'arithematic')) {
      this.validateCalculatedField();
    } else {
      this.validateExpression();
    }
    if (this.isValidCalculatedField) {
      if (this.isEditCalculatedField) {
        let requestObj = {
          query_set_id: this.qrySetId,
          database_id: this.databaseId,
          field_name: this.calculatedFieldName,
          actual_fields_logic: this.calculatedFieldLogic,
          cal_field_id: this.calculatedFieldId,
          functionName: this.calculatedFieldFunction,
          nestedFunctionName: this.nestedCalculatedFieldData
        }
        this.workbechService.editCalculatedFields(requestObj).subscribe({
          next: (responce: any) => {
            this.isEditCalculatedField = false;
            event.close();
            ngbdropdownevent.close();
            this.columnsData();
            this.validationMessage = '';
            this.toasterService.success('Updated Field Successfully', 'success', { positionClass: 'toast-top-right' });

          },
          error: (error) => {
            this.validationMessage = error?.error?.error;
            console.log(error);
          }
        })
      } else {
        let requestObj = {
          query_set_id: this.qrySetId,
          database_id: this.databaseId,
          field_name: this.calculatedFieldName,
          actual_fields_logic: this.calculatedFieldLogic,
          functionName: this.calculatedFieldFunction,
          nestedFunctionName: this.nestedCalculatedFieldData
        }
        this.workbechService.applyCalculatedFields(requestObj).subscribe({
          next: (responce: any) => {
            this.validationMessage = '';
            this.isEditCalculatedField = false;
            event.close();
            this.columnsData();
            this.toasterService.success('Added Successfully', 'success', { positionClass: 'toast-top-right' });

          },
          error: (error) => {
            this.validationMessage = error?.error?.error;
            console.log(error);
          }
        })
      }
    }
  }

    // Step 1: Check for valid characters
    private preValidateExpression(expression: string): void {
      // Check for adjacent parentheses without an operator
      if (/\)\s*\(/.test(expression)) {
        throw new Error('Invalid expression: Missing operator between parentheses.');
      }
    }

    validateExpression(): void {
      try {
        this.preValidateExpression(this.calculatedFieldLogic);
        const regex = /"([^"]+)"\.\"([^"]+)\"/g;
        let validateFieldData = _.cloneDeep(this.calculatedFieldLogic);
        validateFieldData = validateFieldData.replace(regex, (_, tableName, columnName) => {
          return `${tableName}_${columnName}`;
        });
        parse(validateFieldData);
        this.isValidCalculatedField = true;
      } catch (error) {
        this.validationMessage = (error as Error).message;
        this.isValidCalculatedField = false;
      }
    }

    validateFormula(regex: RegExp){
      return regex.test(this.calculatedFieldLogic);
    }

    validateCalculatedField(){
      switch(this.nestedCalculatedFieldData) {
        case 'abs':
          if(!this.validateFormula(/^ABS\((-?\d+(\.\d+)?|"[a-zA-Z0-9_()]*"\."[a-zA-Z0-9_()]*")\)$/)){
            this.isValidCalculatedField = false;
            this.validationMessage = 'Invalid Syntax';
            return false;
          } else{
            this.isValidCalculatedField = true;
            return true;
          }

        break; 
        case 'ceiling':
          if(!this.validateFormula(/^CEILING\((-?\d+(\.\d+)?|"[a-zA-Z0-9_()]*"\."[a-zA-Z0-9_()]*")\)$/)){
            this.isValidCalculatedField = false;
            this.validationMessage = 'Invalid Syntax';
            return false;
          } 
          else{
            this.isValidCalculatedField = true;
            return true;
          }
          break; 
        case 'floor': 
        if(!this.validateFormula(/^FLOOR\((-?\d+(\.\d+)?|"[a-zA-Z0-9_()]*"\."[a-zA-Z0-9_()]*")\)$/)){
          this.isValidCalculatedField = false;
          this.validationMessage = 'Invalid Syntax';
        }
          else{
            this.isValidCalculatedField = true;
            return true;
          }
        break; 
        case 'round':
          if(!this.validateFormula(/^ROUND\((-?\d+(\.\d+)?|"[a-zA-Z0-9_()]*"\."[a-zA-Z0-9_()]*")\)$/)){
            this.isValidCalculatedField = false;
            this.validationMessage = 'Invalid Syntax';
            return false;
          } 
          else{
            this.isValidCalculatedField = true;
            return true;
          }
           break; 
        case 'left': 
        if(!this.validateFormula(/^LEFT\(\s*("[a-zA-Z0-9_()]+"\.\"[a-zA-Z0-9_\(\)\[\]]+\")\s*,\s*(\d+)\s*\)$/)){
          this.isValidCalculatedField = false;
          this.validationMessage = 'Invalid Syntax';
          return false;
        } 
        else{
          this.isValidCalculatedField = true;
          return true;
        }
        break; 
        case 'right': 
        if(!this.validateFormula(/^RIGHT\(\s*("[a-zA-Z0-9_()]+"\.\"[a-zA-Z0-9_\(\)\[\]]+\")\s*,\s*(\d+)\s*\)$/)){
          this.isValidCalculatedField = false;
          this.validationMessage = 'Invalid Syntax';
          return false;
        } 
        else{
          this.isValidCalculatedField = true;
          return true;
        }
        break;
        case 'mid': 
        if(!this.validateFormula(/^SUBSTRING\(\s*"([^"]+)"\.\"([^"]+)\"\s+FROM\s+(\d+)\s+FOR\s+(\d+)\s*\)$/)){
          this.isValidCalculatedField = false;
          this.validationMessage = 'Invalid Syntax';
          return false;
        } 
        else{
          this.isValidCalculatedField = true;
          return true;
        }
        break; 
        case 'length':
          if(!this.validateFormula(/^LENGTH\("([a-zA-Z0-9_()]+)"\."([a-zA-Z0-9_\(\)]+)"\)$/)){
            this.isValidCalculatedField = false;
            this.validationMessage = 'Invalid Syntax';
            return false;
          } 
          else{
            this.isValidCalculatedField = true;
            return true;
          }
        break; 
        case 'trim':
          if(!this.validateFormula(/^TRIM\("([a-zA-Z0-9_()]+)"\."([a-zA-Z0-9_\(\)]+)"\)$/)){
            this.isValidCalculatedField = false;
            this.validationMessage = 'Invalid Syntax';
            return false;
          } 
          else{
            this.isValidCalculatedField = true;
            return true;
          }
        break; 
        case 'upper':
          if(!this.validateFormula(/^UPPER\("([a-zA-Z0-9_()]+)"\."([a-zA-Z0-9_\(\)]+)"\)$/)){
            this.isValidCalculatedField = false;
            this.validationMessage = 'Invalid Syntax';
            return false;
          } 
          else{
            this.isValidCalculatedField = true;
            return true;
          }
        break; 
        case 'lower':
          if(!this.validateFormula(/^LOWER\("([a-zA-Z0-9_()]+)"\."([a-zA-Z0-9_\(\)]+)"\)$/)){
            this.isValidCalculatedField = false;
            this.validationMessage = 'Invalid Syntax';
            return false;
          } 
          else{
            this.isValidCalculatedField = true;
            return true;
          }
        break; 
        case 'replace': 
        if(!this.validateFormula(/^REPLACE\(\s*"([^"]+)"\."([^"]+)"\s*,\s*["']([^"']*)["']\s*,\s*["']([^"']*)["']\s*\)$/)){
          this.isValidCalculatedField = false;
          this.validationMessage = 'Invalid Syntax';
          return false;
        } 
        else{
          this.isValidCalculatedField = true;
          return true;
        }
        break; 
        case 'split': 
        if(!this.validateFormula(/^split_part\(\s*"([^"]+)"\.\"([^"]+)\"\s*,\s*\"([^\"]*)\"\s*,\s*(\d+)\s*\)$/)){
          this.isValidCalculatedField = false;
          this.validationMessage = 'Invalid Syntax';
          return false;
        } 
        else{
          this.isValidCalculatedField = true;
          return true;
        }
        break; 
        case 'find':
          if(!this.validateFormula(/^POSITION\(\s*(['"])([^\1]+)\1\s+IN\s+"([^"]+)"\.\"([^"]+)\"\s*\)$/)){
            this.isValidCalculatedField = false;
            this.validationMessage = 'Invalid Syntax';
            return false;
          } 
          else{
            this.isValidCalculatedField = true;
            return true;
          }
          break; 
          case 'dateadd': 
          if(!this.validateFormula(/\+\s*INTERVAL/)){
            this.isValidCalculatedField = false;
            this.validationMessage = 'Invalid Syntax';
            return false;
          } 
          else{
            this.isValidCalculatedField = true;
            return true;
          }
          break;
          case 'datediff':
            this.isValidCalculatedField = true;
              return true;
          break; 
          case 'datepart': 
          if(!this.validateFormula(/^DATE_PART\(\s*(.+?)\s*,\s*(.+?)\s*\)$/)){
            this.isValidCalculatedField = false;
            this.validationMessage = 'Invalid Syntax';
            return false;
          } 
          else{
            this.isValidCalculatedField = true;
            return true;
          }
          break; 
          case 'now': 
          this.isValidCalculatedField = true;
            return true;
          break; 
          case 'today': 
          this.isValidCalculatedField = true;
            return true;
          break; 
          case 'parse':
            if(!this.validateFormula(/^TO_CHAR\(\s*(.+?)\s*,\s*'dd-mm-yyyy'\s*\)$/)){
              this.isValidCalculatedField = false;
              this.validationMessage = 'Invalid Syntax';
              return false;
            } 
            else{
              this.isValidCalculatedField = true;
              return true;
            }
          break; 
          case 'case': 
          if(!this.validateFormula(/^CASE\s+(WHEN\s+.+?\s+THEN\s+.+?(\s+WHEN\s+.+?\s+THEN\s+.+?)*(\s+ELSE\s+.+?)?\s+END)$/)){
            this.isValidCalculatedField = false;
            this.validationMessage = 'Invalid Syntax';
            return false;
          } 
          else{
            this.isValidCalculatedField = true;
            return true;
          } 
          break; 
        case 'ifnull': 
        if(!this.validateFormula(/^COALESCE\(\s*([^,]+(?:\s*,\s*[^,]+)*)\s*\)$/)){
          this.isValidCalculatedField = false;
          this.validationMessage = 'Invalid Syntax';
          return false;
        } 
        else{
          this.isValidCalculatedField = true;
          return true;
        }
        break; 
        case 'average': 
        if(!this.validateFormula(/^AVERAGE\(\s*.+?\s*\)$/)){
          this.isValidCalculatedField = false;
          this.validationMessage = 'Invalid Syntax';
          return false;
        } 
        else{
          this.isValidCalculatedField = true;
          return true;
        }
        break; 
        case 'count':
          if(!this.validateFormula(/^COUNT\(\s*.+?\s*\)$/)){
            this.isValidCalculatedField = false;
            this.validationMessage = 'Invalid Syntax';
            return false;
          } 
          else{
            this.isValidCalculatedField = true;
            return true;
          }
        break; 
        case 'countd':
          if(!this.validateFormula(/^COUNT\(\s*DISTINCT\s+.+\s*\)$/)){
            this.isValidCalculatedField = false;
            this.validationMessage = 'Invalid Syntax';
            return false;
          } 
          else{
            this.isValidCalculatedField = true;
            return true;
          }
          
        break;
        case 'max':
          if(!this.validateFormula(/^MAX\(\s*.+?\s*\)$/)){
            this.isValidCalculatedField = false;
            this.validationMessage = 'Invalid Syntax';
            return false;
          } 
          else{
            this.isValidCalculatedField = true;
            return true;
          }
          break; 
        case 'min':
          if(!this.validateFormula(/^MIN\(\s*.+?\s*\)$/)){
            this.isValidCalculatedField = false;
            this.validationMessage = 'Invalid Syntax';
            return false;
          } 
          else{
            this.isValidCalculatedField = true;
            return true;
          }
        break; 
        case 'sum':
          if(!this.validateFormula(/^SUM\(\s*.+?\s*\)$/)){
            this.isValidCalculatedField = false;
            this.validationMessage = 'Invalid Syntax';
            return false;
          } 
          else{
            this.isValidCalculatedField = true;
            return true;
          }  
        break; 
        
      }
    }

    calculatedFieldData(){
      this.nestedCalculatedFieldData = '';
      this.calculatedFieldLogic = '';
    }

    nestedCalculatedFieldFunction(){
      switch(this.nestedCalculatedFieldData) {
        case 'abs':
          this.calculatedFieldLogic = 'ABS()';
        break; 
        case 'ceiling':
          this.calculatedFieldLogic = 'CEILING()';
          break; 
        case 'floor': 
        this.calculatedFieldLogic = 'FLOOR()';
        break; 
        case 'round':
        this.calculatedFieldLogic = 'ROUND()';
           break; 
        case 'left': 
        this.calculatedFieldLogic = 'LEFT( , )';
        break; 
        case 'right': 
        this.calculatedFieldLogic = 'RIGHT( , )';
        break;
        case 'mid': 
        this.calculatedFieldLogic = 'SUBSTRING( from  for )';
        break; 
        case 'length': 
        this.calculatedFieldLogic = 'LENGTH()';
        break; 
        case 'trim':
         this.calculatedFieldLogic = 'TRIM()';
        break; 
        case 'upper': 
        this.calculatedFieldLogic = 'UPPER()';
        break; 
        case 'lower': 
        this.calculatedFieldLogic = 'LOWER()';
        break; 
        case 'replace': 
        this.calculatedFieldLogic = 'REPLACE(, ,)';
        break; 
        case 'split':
          this.calculatedFieldLogic = 'split_part(, ,)';
        break; 
        case 'find':
          this.calculatedFieldLogic = "POSITION( '' IN )";
        break; 
        case 'dateadd': 
        this.calculatedFieldLogic = 'CURRENT_DATE + INTERVAL ';
        break;
        case 'datediff':
          this.calculatedFieldLogic = 'CURRENT_DATE - ';
        break; 
        case 'datepart': 
        this.calculatedFieldLogic = "DATE_PART('year', current_timestamp)";
        break; 
        case 'now': 
        this.calculatedFieldLogic = 'current_timestamp()';
        break; 
        case 'today': 
        this.calculatedFieldLogic = 'CURRENT_DATE()';
        break; 
        case 'parse':
          this.calculatedFieldLogic = "TO_CHAR(, 'dd-mm-yyyy')";
        break; 
        case 'case':
          this.calculatedFieldLogic = 'CASE expression WHEN value THEN result ELSE default END';
        break; 
        case 'ifnull':
          this.calculatedFieldLogic = 'COALESCE()';
        break; 
        case 'average':
          this.calculatedFieldLogic = 'AVG()';
        break; 
        case 'count': 
        this.calculatedFieldLogic = 'COUNT()';
        break; 
        case 'countd':
          this.calculatedFieldLogic = 'COUNTD()';
        break;
        case 'max':
          this.calculatedFieldLogic = 'MAX()';
        break; 
        case 'min':
          this.calculatedFieldLogic = 'MIN()';
        break; 
        case 'sum': 
        this.calculatedFieldLogic = 'SUM()';
        break; 
        
      }
    }
    tableDataColorChange(event:any){
      if (this.selectedElement) {
        this.selectedElement.style.border = 'none';
      }
      const element = event.target as HTMLElement;
      this.selectedElement = event.target as HTMLElement;
      this.selectedElement.style.border = '2px solid var(--primary-color)';
      this.tableDataFontColor = window.getComputedStyle(element).backgroundColor;
    }
    headerColorChange(event:any){
      if (this.selectedElement) {
        this.selectedElement.style.border = 'none';
      }
      const element = event.target as HTMLElement;
      this.selectedElement = event.target as HTMLElement;
      this.selectedElement.style.border = '2px solid var(--primary-color)';
      this.headerFontColor = window.getComputedStyle(element).backgroundColor;
    }
    sortedData : TableRow[] = [];
    tableColumnSort(sortType:any, column : any){
      this.sortedData = [...this.tableDataDisplay];
      if(sortType === 'default'){
        this.sortedData = [];
      }
      else if(sortType === 'ascending'){
        this.sortedData.sort((a, b) => {
          if (a[column] < b[column]) {
            return -1;
          }
          if (a[column] > b[column]) {
            return 1;
          }
          return 0;
        });
      }
      else if(sortType === 'descending'){
        this.sortedData.sort((a, b) => {
          if (a[column] > b[column]) {
            return -1;
          }
          if (a[column] < b[column]) {
            return 1;
          }
          return 0;
        });
      }
    }
    deleteCalculationField(id : any){
      this.workbechService.deleteCalculatedFields(id).subscribe({
        next: (response: any) => {
          this.columnsData();
          this.toasterService.success('Deleted Successfully', 'success', { positionClass: 'toast-top-right' });
        },
        error: (error) => {
          console.log(error);
        }
      })
    }

    addCalculatedField(){
      if(!this.isEditCalculatedField){
        this.calculatedFieldName = '';
     this.calculatedFieldFunction = '';
     this.nestedCalculatedFieldData = '';
     this.calculatedFieldLogic = '';
     this.isEditCalculatedField = false;
      }
    }

    isMapChartDrillDown : boolean = false;
    setDrilldowns(event : any){
      this.drillDownIndex = event.drillDownIndex;
      this.draggedDrillDownColumns = event.draggedDrillDownColumns;
      this.drillDownObject = event.drillDownObject;
      // if (this.map) {
      //   if (this.drillDownIndex != 0) {
      //     this.map = false;
      //     this.bar = true;
      //     this.chartId = 6;
      //     this.chartType = 'bar';
      //     this.isMapChartDrillDown = true;
      //   }
      // }
      this.setOriginalData();
      this.dataExtraction();
    }
    isSheetSaveOrUpdate : boolean = false;
    chartOptionsSet : any;
    setChartOptions(event : any){
      this.chartOptionsSet = event.chartOptions;
      this.sheetSave();
      this.isSheetSaveOrUpdate = false;
    }
    clearSheetConfirmation(){
      Swal.fire({
        title: "Are you sure you want to clear the sheet?",
        text: "Except for the filters, the sheet will be cleared.",
        position: "center",
        icon: "warning",
        showConfirmButton: true,
        showCancelButton: true,
        confirmButtonText: 'Yes',
        cancelButtonText: 'No',
      }).then((result) => {
        if (result.isConfirmed) {
          this.clearSheet();
        }
      })
    }
    clearSheet(){
      this.draggedColumns = [];
      this.draggedColumnsData = [];
      this.draggedRows = [];
      this.draggedRowsData = [];
      this.draggedMeasureValues = [];
      this.draggedMeasureValuesData = [];
      this.draggedDrillDownColumns = [];
      this.tablePaginationCustomQuery = '';
      this.chartsColumnData = [];
      this.chartsRowData = [];
      this.dualAxisColumnData = [];
      this.dualAxisRowData = [];
      this.tableColumnsDisplay = [];
      this.tableDataDisplay = [];
      this.KPINumber = '';
      this.drillDownObject = [];
      this.dateDrillDownSwitch = false;
      this.resetCustomizations();
      this.table = true;
      this.pivotTable = false;
      this.bar = false;
      this.area = false;
      this.line = false;
      this.pie = false;
      this.sidebyside = false;
      this.stocked = false;
      this.barLine = false;
      this.horizentalStocked = false;
      this.grouped = false;
      this.multiLine = false;
      this.donut = false;
      this.chartId = 1;
      this.radar = false;
      this.kpi = false;
      this.heatMap = false;
      this.guage = false;
      this.funnel = false;
      this.calendar = false;
      this.map = false;
    }
    sortColumn : any = 'select';
    columnNamesForSort : any [] = [];
    columnsDataForSort : any [] = [];
    selectedSortColumnData : any[] | null = null;
    selectedColumnIndex : number = -1;
    getDimensionAndMeasures(){
      this.columnNamesForSort = [];
      this.columnsDataForSort = [];
      if(this.draggedDrillDownColumns && this.draggedDrillDownColumns.length > 0 && this.heirarchyColumnData && this.heirarchyColumnData.length > 0){
        this.draggedColumns.forEach((column:any, index: any)=>{
          let col = JSON.parse(JSON.stringify(column));
          if(this.dateDrillDownSwitch){
            col.type = this.heirarchyColumnData[this.drillDownIndex][2];
          }
          else{
            col.column = this.heirarchyColumnData[this.drillDownIndex][0];
            col.data_type = this.heirarchyColumnData[this.drillDownIndex][1];
          }
          if (col && typeof col === 'object') {
            this.columnNamesForSort.push({ ...col });
          } 
          this.columnsDataForSort.push(this.draggedColumnsData[index]);
        });
      } else{
        this.draggedColumns.forEach((column:any, index: any)=>{
          if (column && typeof column === 'object') {
            this.columnNamesForSort.push({ ...column });
          } 
          this.columnsDataForSort.push(this.draggedColumnsData[index]);
        });
      }
      this.draggedRows.forEach((row:any, index: any)=>{
        if (row && typeof row === 'object') {
          this.columnNamesForSort.push({ ...row });
        } 
        this.columnsDataForSort.push(this.draggedRowsData[index]);
      });
      console.log('columnsdisplay',this.columnNamesForSort)
      console.log('columnforpayload',this.columnsDataForSort)
    }
    changeSelectedColumn(){
      console.log(this.sortColumn);
      this.columnNamesForSort.forEach((column:any,index:any)=>{
        if((this.sortColumn.alias && this.sortColumn.alias === column.alias) || (this.sortColumn.field_name && this.sortColumn.field_name === column.field_name) || (this.sortColumn.type && this.sortColumn.type === column.type && this.sortColumn.column === column.column) || (this.sortColumn.column && this.sortColumn.column === column.column)){
          this.sortColumn = column;
          this.selectedColumnIndex = index;
        }
      });
    }
    sortColumns(){
      if(this.sortType === 'none' || this.sortType === 0){
        this.selectedSortColumnData = null;
      } else{
        if (this.selectedColumnIndex != -1) {
          let column = JSON.parse(JSON.stringify(this.columnsDataForSort[this.selectedColumnIndex]));
          column[4] = this.sortType;
          this.selectedSortColumnData = column;
        }
      }
      this.dataExtraction();
    }

    topType : string = 'desc';
    topLimit : number = 5;
    selectedTopColumn : any = 'select';
    topAggregate : string = 'sum';
}