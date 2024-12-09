import { Component,ViewChild,NgZone } from '@angular/core';
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
import { lastValueFrom } from 'rxjs';
import { evaluate, parse } from 'mathjs';

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
@Component({
  selector: 'app-sheets',
  standalone: true,
  providers: [
    {
      provide: NGX_ECHARTS_CONFIG,
      useFactory: () => ({ echarts: echarts }),
    },
  ],
  imports: [SharedModule, NgxEchartsModule, NgSelectModule,NgbModule,FormsModule,ReactiveFormsModule,MatIconModule,NgxColorsModule,
    CdkDropListGroup, CdkDropList,CommonModule, CdkDrag,NgApexchartsModule,MatTabsModule,MatFormFieldModule,MatInputModule,CKEditorModule,
    InsightsButtonComponent,NgxSliderModule,NgxPaginationModule,MatTooltipModule],
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
  chartOptions2:any;
  chartOptions3:any;
  chartOptions4:any;
  chartOptions6:any;
  chartOptions5:any;
  chartOptions7:any;
  chartOptions8:any;
  chartOptions9:any;
  chartOptions10:any;
  heatMapChartOptions: any;
  funnelChartOptions:any;
  guageChartOptions:any;
  eBarChartOptions: any;
  eStackedBarChartOptions: any;
  eGroupedBarChartOptions: any;
  eMultiLineChartOptions: any;
  ehorizontalStackedBarChartOptions: any;
  eSideBySideBarChartOptions: any;
  eAreaChartOptions: any;
  eLineChartOptions: any;
  ePieChartOptions: any;
  eDonutChartOptions: any;
  eBarLineChartOptions: any;
  eRadarChartOptions: any;
  eCalendarChartOptions:any;
  eHeatMapChartOptions:any;
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
  KPIDecimalPlaces: number = 0;
  KPIRoundPlaces: number = 0;
  KPIDisplayUnits: string = 'none';
  KPIPrefix: string = '';
  KPISuffix: string = '';
  isCustomSql = false;
  canDrop = true;
  createdBy : any;
  calculatedFieldFunction : string = '';
  nestedCalculatedFieldData : string = '';
  @ViewChild('barChart') barchart!: ChartComponent;
  @ViewChild(' bar-chart') eBarchart!: any;
  @ViewChild('areaChart') areachart!: ChartComponent;
  @ViewChild('lineChart') linechart!: ChartComponent;
  @ViewChild('sidebyside') sidebysideChart!: ChartComponent;
  @ViewChild('stocked') stockedChart!: ChartComponent;
  @ViewChild('barline') barlineChart!: ChartComponent;
  @ViewChild('horizentalstocked') horizontolstockedChart!: ChartComponent;
  @ViewChild('grouped') groupedChart!: ChartComponent;
  @ViewChild('multiline') multilineChart!: ChartComponent;
  @ViewChild('piechart') piechart!: ChartComponent;
  @ViewChild('donutchart') donutchart!: ChartComponent;
  @ViewChild('funnelChart') funnelCharts!: ChartComponent;
  @ViewChild('guageChart') guageCharts!: ChartComponent;
  @ViewChild('heatmapchart') heatmapcharts!: ChartComponent;

  radar: boolean = false;
  radarRowData: any = [];
  xlabelAlignment  = 'left';
  ylabelAlignment : VerticalAlign = 'center';
  dataLabelAlignment : MixedAlign = 'top';
  backgroundColor: string = '#fff';
  canEditDb = false;
  draggedDrillDownColumns = [] as any;
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
  isDistributed : boolean = false;
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
  measureAlignment : any = 'center';
  dimensionAlignment : any = 'center';
  colorPalette = COLOR_PALETTE;
  isValidCalculatedField! : boolean;
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

  constructor(private workbechService:WorkbenchService,private route:ActivatedRoute,private modalService: NgbModal,private router:Router,private zone: NgZone, private sanitizer: DomSanitizer,
    private templateService:ViewTemplateDrivenService,private toasterService:ToastrService,private loaderService:LoaderService, private http: HttpClient){   
    if(this.router.url.includes('/insights/sheets/dbId')){
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
     if(this.router.url.includes('/insights/sheets/fileId')){
      if (route.snapshot.params['id1'] && route.snapshot.params['id2']&& route.snapshot.params['id3'] ) {
        this.fileId = +atob(route.snapshot.params['id1']);
        this.qrySetId = +atob(route.snapshot.params['id2']);
        this.filterQuerySetId = atob(route.snapshot.params['id3']);
        // this.tabs[0] = this.sheetName;
        this.sheetTagName = this.sheetName;
        this.fromFileId = true;
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
  if(this.router.url.includes('/insights/home/dbId/sheets/')){
    if (route.snapshot.params['id1'] && route.snapshot.params['id2'] && route.snapshot.params['id3']) {
      this.databaseId = +atob(route.snapshot.params['id1']);
      this.qrySetId = +atob(route.snapshot.params['id2'])
      this.retriveDataSheet_id = +atob(route.snapshot.params['id3'])
      console.log(this.retriveDataSheet_id);
      //this.tabs[0] = this.sheetName;
      // this.sheetRetrive();
      }
   }
   if(this.router.url.includes('/insights/home/fileId/sheets/')){
    this.fromFileId = true;
    if (route.snapshot.params['id1'] && route.snapshot.params['id2'] && route.snapshot.params['id3']) {
      this.fileId = +atob(route.snapshot.params['id1']);
      this.qrySetId = +atob(route.snapshot.params['id2'])
      this.retriveDataSheet_id = +atob(route.snapshot.params['id3'])
      console.log(this.retriveDataSheet_id);
      //this.tabs[0] = this.sheetName;
      // this.sheetRetrive();
      }
   }


   if(this.router.url.includes('/insights/sheetsdashboard/sheets/fileId/')){
    this.sheetsDashboard = true;
    this.fromFileId = true;
    console.log("landing page")
    if (route.snapshot.params['id1'] && route.snapshot.params['id2'] && route.snapshot.params['id3'] && route.snapshot.params['id4']) {
      this.fileId = +atob(route.snapshot.params['id1']);
      this.qrySetId = +atob(route.snapshot.params['id2']);
      this.retriveDataSheet_id = +atob(route.snapshot.params['id3']);
      this.dashboardId = +atob(route.snapshot.params['id4']);
      console.log(this.retriveDataSheet_id)
      // this.sheetRetrive();
      }
   } 
   if(this.router.url.includes('/insights/sheetsdashboard/sheets/dbId/')){
    this.sheetsDashboard = true;
    this.fromFileId = false;
    console.log("landing page")
    if (route.snapshot.params['id1'] && route.snapshot.params['id2'] && route.snapshot.params['id3'] && route.snapshot.params['id4']) {
      this.databaseId = +atob(route.snapshot.params['id1']);
      this.qrySetId = +atob(route.snapshot.params['id2']);
      this.retriveDataSheet_id = +atob(route.snapshot.params['id3']);
      this.dashboardId = +atob(route.snapshot.params['id4']);
      console.log(this.retriveDataSheet_id)
      // this.sheetRetrive();
      }
   } 
   this.canEditDb = this.templateService.addDatasource();
   this.canDrop = !this.canEditDb
  }

  ngOnInit(): void {
    this.loaderService.hide();
    this.columnsData();
    this.sheetTitle = this.sheetTitle +this.sheetNumber;
    this.getSheetNames();
    this.getDashboardsList();
    this.setChartType();
    // this.sheetRetrive();
  }
 async getSheetNames():Promise<void>{
  //this.tabs = [];
  const obj={
    "server_id":this.databaseId,
    "queryset_id":this.qrySetId,
}as any;
if(this.fromFileId){
  delete obj.server_id;
  obj.file_id=this.fileId;
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
      const encodedFileId = btoa(this.fileId?.toString());

      const fromSource = this.fromFileId ? 'fileId' : 'dbId'
      const idToPass = this.fromFileId ? encodedFileId : encodeddbId;

      if (this.filterQuerySetId === null || this.filterQuerySetId === undefined) {
        // Encode 'null' to represent a null value
       const encodedDsQuerySetId = btoa('null');
       this.router.navigate(['/insights/database-connection/savedQuery/'+fromSource+'/'+idToPass+'/'+encodedqurysetId])
  
      } else {
        // Convert to string and encode
       const encodedDsQuerySetId = btoa(this.filterQuerySetId.toString());
       this.router.navigate(['/insights/database-connection/savedQuery/'+fromSource+'/'+idToPass+'/'+encodedqurysetId])
    
      } 
     }
    else{
    const encodeddbId = btoa(this.databaseId?.toString());
    const encodedqurysetId = btoa(this.qrySetId.toString());
    const encodedFileId = btoa(this.fileId?.toString());
    // this.router.navigate(['/insights/database-connection/sheets/'+encodeddbId+'/'+encodedqurysetId])

    const idToPass = this.fromFileId ? encodedFileId : encodeddbId;
    const fromSource = this.fromFileId ? 'fileId' : 'dbId'
  
    if (this.filterQuerySetId === null || this.filterQuerySetId === undefined) {
      // Encode 'null' to represent a null value
     const encodedDsQuerySetId = btoa('null');
     this.router.navigate(['/insights/database-connection/sheets/'+fromSource+'/'+idToPass+'/'+encodedqurysetId+'/'+encodedDsQuerySetId])

    } else {
      // Convert to string and encode
     const encodedDsQuerySetId = btoa(this.filterQuerySetId.toString());
     this.router.navigate(['/insights/database-connection/sheets/'+fromSource+'/'+idToPass+'/'+encodedqurysetId+'/'+encodedDsQuerySetId])
  
    }
  }

  }
  goToConnections(){
    this.router.navigate(['/insights/datasources/view-connections'])
  }
  toggleSubMenu(menu: any) {
    menu.expanded = !menu.expanded;
  }

  barChart() {
    if (this.isApexCharts) {
      const self = this;
        this.chartOptions3 = {
          series: [
            {
              name: "",
              data: this.chartsRowData 
            }
          ],
          annotations: {
            points: [{
              x: 'zoom',
              seriesIndex: 0,
              label: {
                borderColor: '#775DD0',
                offsetY: 0,
                style: {
                  color: '#fff',
                  background: '#775DD0',
                },
                text: 'zoom',
              }
            }]
          },
          chart: {
            toolbar: {
              show: true,
              offsetX: 0,
              offsetY: 0,
              tools: {
                download: true,
                selection: true,
                zoom: true,
                zoomin: true,
                zoomout: true,
                pan: true,
                reset: true || '<img src="./assets/images/icons/home-icon.png" width="20">',
              },
              autoSelected: 'zoom' 
            },
            type: 'bar',
            height: 320,
            background: this.backgroundColor,
            events: {
              dataPointSelection: function (event: any, chartContext: any, config: any) {
                const selectedXValue = self.chartsColumnData[config.dataPointIndex];
                console.log('X-axis value:', selectedXValue);
                if (self.drillDownIndex < self.draggedDrillDownColumns.length - 1) {
                  const selectedXValue = self.chartsColumnData[config.dataPointIndex];
                  console.log('X-axis value:', selectedXValue);
                  let nestedKey = self.draggedDrillDownColumns[self.drillDownIndex];
                  self.drillDownIndex++;
                  let obj = { [nestedKey]: selectedXValue };
                  self.drillDownObject.push(obj);
                  self.setOriginalData();
                  self.dataExtraction();
                }
              }
            }
          },
          title: {
            text: "",
            offsetY: 10,
            align: 'center',
            style: {
              color: this.color,
            },
          },
          xaxis: {
            categories: this.chartsColumnData.map((category : any)  => category === null ? 'null' : category),
            tickPlacement: 'on',
            position: 'bottom',
            labels: {
              show: this.xLabelSwitch,
              trim: true,
              hideOverlappingLabels: false,
              style: {
                colors: this.color,
                fontSize: '12px',
                fontFamily: 'Helvetica, Arial, sans-serif',
                fontWeight: 12,
                },
            },
            axisBorder: {
              show: false,
            },
            axisTicks: {
              show: false,
            },
            crosshairs: {
              fill: {
                type: 'gradient',
                gradient: {
                  stops: [0, 100],
                  opacityFrom: 0.4,
                  opacityTo: 0.5,
                },
              },
            },
            tooltip: {
              enabled: false,
              offsetY: -35,
            },
          },
          yaxis:{
            show: true,
            labels: {
              show: this.yLabelSwitch,
              style: {
                colors: [],
                fontSize: '12px',
                fontFamily: 'Helvetica, Arial, sans-serif',
                fontWeight: 12,
              },
              formatter: this.formatNumber.bind(this)
            },
            axisBorder: {
              show: false,
            },
            axisTicks: {
              show: false,
            },
          },
          grid: {
            show: true,
            borderColor: '#90A4AE',
            xaxis: {
              lines: {
                show: this.xGridSwitch
              }
            },
            yaxis: {
              lines: {
                show: this.yGridSwitch
              }
            },
          },
          plotOptions: {
            bar: {
              dataLabels: {
                hideOverflowingLabels:false,
                position: this.dataLabelAlignment,
              },
            },
          },
          dataLabels: {
            enabled: true,
            formatter: this.formatNumber.bind(this),
            offsetY: -20,
            style: {
              fontSize: '12px',
              colors: [this.color],
            },
          },
          // fill: {
          //   type: 'gradient',
          // },
          colors: [this.color]
        };
    } else {
      this.eBarChartOptions = {
        backgroundColor: this.backgroundColor,
        legend: {
          orient: 'vertical',
          left: 'left'
        },
        toolbox: {
          feature: {
            magicType: { show: true, type: ['line'] },
            restore: { show: true },
            saveAsImage: { show: true }
          }
        },
        tooltip: {
          trigger: 'axis',
        },
        axisPointer: {
          type: 'none'
        },
        dataZoom: [
          {
            show: this.isZoom,
            type: 'slider'
          },

        ],
        grid: {
          left: '3%',
          right: '4%',
          bottom: '13%',
          containLabel: true,
        },
        xAxis: {
          type: 'category',
          data: this.chartsColumnData,
          nameLocation:this.xlabelAlignment,
          splitLine: {
            lineStyle: {
              color: this.xGridColor
            }, show: this.xGridSwitch
          },
          axisLine: {
            lineStyle: {
              color: this.xLabelColor,
            },
          },
          axisLabel: {
            show: this.xLabelSwitch,
            fontFamily: this.xLabelFontFamily,
            fontSize: this.xLabelFontSize,
            fontWeight: this.xlabelFontWeight,
            // align: this.xlabelAlignment,// Hide xAxis labels
            interval: 0, // Show all labels
            padding: [10, 0, 10, 0],
            formatter: function(value:any) {
              return value.length > 5 ? value.substring(0, 5) + '...' : value; // Truncate long labels
          }
          }
        },
        toggleGridLines: true,
        yAxis: {
          type: 'value',
          axisLine: {
            lineStyle: {
              color: this.yLabelColor
            },
            show:this.yGridSwitch
          },
          axisLabel: {
            show: this.yLabelSwitch,
            fontFamily: this.yLabelFontFamily,
            fontSize: this.yLabelFontSize,
            fontWeight: this.ylabelFontWeight,
            rotate:0,
            formatter: function(value:any) {
              return value.length > 5 ? value.substring(0, 2) + '...' : value; // Truncate long labels
          }
          },
          splitLine: {
            lineStyle: {
              color: this.yGridColor
            },
            show: this.yGridSwitch
          }
        },
        // itemStyle: {borderWidth : '50px' },
        series: [
          {
            itemStyle: {
              borderRadius: 5
            },
            label: { show: true,
              position: 'center',
             },
            type: 'bar',
            barWidth: '80%',
            data: this.chartsRowData
            // data: this.chartsRowData.map((value: any, index: number) => ({
            //   value,
            //   itemStyle: { borderWidth: '50px' }
            // })),
          },
        ],
        color: this.color

      };
    }
  }

  // setEchartLegendAlignment(){
  //   switch(this.legendsAllignment) {
  //     case 'left': return {
  //       show: this.legendSwitch,
  //       orient: 'vertical',
  //       top : 'center',
  //       left: 'left'
  //     };
  //     case 'right': return {
  //       show: this.legendSwitch,
  //       orient: 'vertical',
  //       top : 'center',
  //       right: 'right'
  //     };
  //     case 'top': return {
  //       show: this.legendSwitch,
  //       orient: 'horizontal',
  //       top: 'top'
  //     };
  //     case 'bottom': return {
  //       show: this.legendSwitch,
  //       orient: 'horizontal',
  //       bottom: 'bottom'
  //     };
  //     default: return {
  //       show: this.legendSwitch,
  //       orient: 'horizontal',
  //       bottom: 'bottom'
  //     };
  //   }
  // }
  pieChart(){
    if(this.isApexCharts){
      const self = this;
        this.chartOptions4 = {
          series: this.chartsRowData,
          chart: {
            height: 300,
            type: 'pie',
            background: this.backgroundColor,
            events: {
              dataPointSelection: function (event: any, chartContext: any, config: any) {
                const selectedXValue = self.chartsColumnData[config.dataPointIndex];
                console.log('X-axis value:', selectedXValue);
                if (self.drillDownIndex < self.draggedDrillDownColumns.length - 1) {
                  const selectedXValue = self.chartOptions4.labels[config.dataPointIndex];
                  console.log('X-axis value:', selectedXValue);
                  let nestedKey = self.draggedDrillDownColumns[self.drillDownIndex];
                  self.drillDownIndex++;
                  let obj = { [nestedKey]: selectedXValue };
                  self.drillDownObject.push(obj);
                  self.setOriginalData();
                  self.dataExtraction();
                }
              }
            }
          },
          colors: ["#2392c1", "#31d1ce", "#f5b849", "#49b6f5", "#e6533c"],
          labels: this.chartsColumnData.map((category: any) => category === null ? 'null' : category),
          legend: {
            show: true,
            position: 'bottom'
          },
          dataLabels: {
            enabled: true,
            dropShadow: {
              enabled: false
            }
          },
          tooltip: {
            enabled:true,
            y: {
              formatter: function(value: number) {
                console.log("Tooltip triggered"); // Simple debug message
                return value;
              }
            }
          }
        };
    }
     else {
      let combinedArray = this.chartsRowData.map((value : any, index :number) => ({
        value: value,
        name: this.chartsColumnData[index]
      }));
      // let legendObject = this.setEchartLegendAlignment();
      this.ePieChartOptions = {
        backgroundColor: this.backgroundColor,
        tooltip: {
          trigger: 'item'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          type:'scroll',
          show: this.legendSwitch 
          },
              label: {
          show : this.dataLabels,
          formatter: '{b}: {d}%',
        },
        series: [
          {
            type: 'pie',
            radius: '50%',
            data: combinedArray,
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            label: {
              show: this.dataLabels, // Dynamically show or hide data labels            }
          }
        }
        ]
      };
    }
  }
  lineChart() {
    if (this.isApexCharts) {
      const self = this;
        this.chartOptions = {
          series: [{
            name: "",
            data: this.chartsRowData
          }],
          annotations: {
            points: [{
              x: 'zoom',
              seriesIndex: 0,
              label: {
                borderColor: '#775DD0',
                offsetY: 0,
                style: {
                  color: '#fff',
                  background: '#775DD0',
                },
                text: 'zoom',
              }
            }]
          },
          chart: {
            toolbar: {
              show: true,
              offsetX: 0,
              offsetY: 0,
              tools: {
                download: true,
                selection: true,
                zoom: true,
                zoomin: true,
                zoomout: true,
                pan: true,
                reset: true || '<img src="./assets/images/icons/home-icon.png" width="20">',
              },
              autoSelected: 'zoom' 
            },
            height: 350,
            type: 'line',
            background: this.backgroundColor,
            reponsive: true,
            zoom: {
              enabled: true
            },
            events: {
              mounted: (chart: any) => {
                chart.windowResizeHandler();
              },
              dataPointSelection: function (event: any, chartContext: any, config: any) {
                if (self.drillDownIndex < self.draggedDrillDownColumns.length - 1) {
                  const selectedXValue = self.chartsColumnData[config.dataPointIndex];
                  console.log('X-axis value:', selectedXValue);
                  let nestedKey = self.draggedDrillDownColumns[self.drillDownIndex];
                  self.drillDownIndex++;
                  let obj = { [nestedKey]: selectedXValue };
                  self.drillDownObject.push(obj);
                  self.setOriginalData();
                  self.dataExtraction();
                }
              },
            }
          },
            colors: [this.color],
            dataLabels: {
              enabled: true,
              formatter: this.formatNumber.bind(this),
              offsetY: -10,
              style: {
                fontSize: '12px',
                colors: [this.color],
              },
              background: {
                enabled: false,
              }
            },
            stroke: {
              curve: 'straight',
              width: 3,
            },
            grid: {
              borderColor: this.GridColor,
              show: true,
              xaxis: {
                lines: {
                  show: this.xGridSwitch
                }
              },
              tooltip: {
                intersect: true,
                shared: false
              },
              markers: { size: 10 },
              yaxis: {
                lines: {
                  show: this.yGridSwitch
                }
              },
            },
            title: {
              text: '',
              align: 'left',
              style: {
                fontSize: '13px',
                fontWeight: 'bold',
                color: this.color
              },
            },
            xaxis: {
              categories: this.chartsColumnData.map((category: any) => category === null ? 'null' : category),
              tickPlacement: 'on',
              labels: {
                show: this.xLabelSwitch,
                hideOverlappingLabels: false,
                trim: true,
                style: {
                  colors: this.color,
                  fontSize: '12px',
                  fontFamily: 'Helvetica, Arial, sans-serif',
                  fontWeight: 12,
                },
              }
            },
            yaxis: {
              labels: {
                show: 
                this.yLabelSwitch,
                style: {
                  colors: this.color,
                  fontSize: '12px',
                  fontFamily: 'Helvetica, Arial, sans-serif',
                  fontWeight: 12,
                },
                formatter: this.formatNumber.bind(this)
              }
            }
          }
      } else {
        this.eLineChartOptions = {
          backgroundColor: this.backgroundColor,
          legend: {
            orient: 'vertical',
            left: 'left'
          },
          toolbox: {
            feature: {
              magicType: { show: true, type: ['line'] },
              restore: { show: true },
              saveAsImage: { show: true }
            }
          },
          tooltip: {
            trigger: 'axis',
          },
          axisPointer: {
            type: 'none'
          },
          dataZoom: [
            {
              show: this.isZoom,
              type: 'slider'
            },

          ],
          grid: {
            left: '3%',
            right: '4%',
            bottom: '13%',
            containLabel: true,
          },
          xAxis: {
            type: 'category',
            data: this.chartsColumnData,
            nameLocation:this.xlabelAlignment,
            splitLine: {
              lineStyle: {
                color: this.xGridColor
              }, show: this.xGridSwitch
            },
            axisLine: {
              lineStyle: {
                color: this.xLabelColor,
              },
            },
            axisLabel: {
              show: this.xLabelSwitch,
              fontFamily: this.xLabelFontFamily,
              fontSize: this.xLabelFontSize,
              fontWeight: this.xlabelFontWeight,
              align: this.xlabelAlignment// Hide xAxis labels
            }
          },
          toggleGridLines: true,
          yAxis: {
            type: 'value',
            axisLine: {
              lineStyle: {
                color: this.yLabelColor
              }
            },
            axisLabel: {
              show: this.yLabelSwitch,
              fontFamily: this.xLabelFontFamily,
              fontSize: this.xLabelFontSize,
              fontWeight: this.xlabelFontWeight,
            },
            splitLine: {
              lineStyle: {
                color: this.yGridColor
              },
              show: this.yGridSwitch
            }
          },
          series: [
            {
              label: { show: true },
              type: 'line',
              data: this.chartsRowData
            },
          ],
          color: this.color

        };
      }
    }
    areaChart(){
      if (this.isApexCharts) {
          this.chartOptions1 = {
            series: [
              {
                name: "",
                data: this.chartsRowData,
              },
            ],
            annotations: {
              points: [{
                x: 'zoom',
                seriesIndex: 0,
                label: {
                  borderColor: '#775DD0',
                  offsetY: 0,
                  style: {
                    color: '#fff',
                    background: '#775DD0',
                  },
                  text: 'zoom',
                }
              }]
            },
            chart: {
              toolbar: {
                show: true,
                offsetX: 0,
                offsetY: 0,
                tools: {
                  download: true,
                  selection: true,
                  zoom: true,
                  zoomin: true,
                  zoomout: true,
                  pan: true,
                  reset: true || '<img src="./assets/images/icons/home-icon.png" width="20">',
                },
                autoSelected: 'zoom' 
              },
              type: "area",
              height: 350,
              background: this.backgroundColor,
              zoom: {
                enabled: true,
              },
            },
            dataLabels: {
              enabled: true,
              formatter: this.formatNumber.bind(this),
              offsetY: -10,
              style: {
                fontSize: '12px',
                colors: [this.color],
              },
              background: {
                enabled: false,
              }
            },
            stroke: {
              curve: "straight",
            },
            subtitle: {
              text: "",
              align: "left",
              style: {
                fontSize: "11px",
                fontWeight: "normal",
                color: this.color,
              },
            },
            grid: {
              borderColor: "rgba(119, 119, 142, 0.05)",
              show: true,
              xaxis: {
                lines: {
                  show: 
                  this.xGridSwitch
                }
              },
              yaxis: {
                lines: {
                  show: 
                  this.yGridSwitch
                }
              },
            },
            labels: this.chartsColumnData.map((category: any) => category === null ? 'null' : category),
            title: {
              text: "",
              align: "left",
              style: {
                fontSize: "13px",
                fontWeight: "bold",
                color: this.color,
              },
            },
            colors: [this.color],
            xaxis: {
              type: "",
              labels: {
                show: this.xLabelSwitch,
                style: {
                  colors: this.color,
                  fontSize: '12px',
                  fontFamily: 'Helvetica, Arial, sans-serif',
                  fontWeight: 12,
                },
              },
              tickPlacement: 'on'
            },
            yaxis: {
              labels: {
                show: this.yLabelSwitch,
                style: {
                  colors: this.color,
                  fontSize: '12px',
                  fontFamily: 'Helvetica, Arial, sans-serif',
                  fontWeight: 12,
                },
                formatter: this.formatNumber.bind(this)
              },
            },
          };
          console.log(this.chartOptions1);
      } else {
        this.eAreaChartOptions = {
          backgroundColor: this.backgroundColor,
          legend: {
            orient: 'vertical',
            left: 'left'
          },
          toolbox: {
            feature: {
              magicType: { show: true, type: ['line'] },
              restore: { show: true },
              saveAsImage: { show: true }
            }
          },
          tooltip: {
            trigger: 'axis',
          },
          axisPointer: {
            type: 'none'
          },
          dataZoom: [
            {
              show: this.isZoom,
              type: 'slider'
            },

          ],
          grid: {
            left: '3%',
            right: '4%',
            bottom: '13%',
            containLabel: true,
          },
          xAxis: {
            type: 'category',
            boundaryGap: false,
            data: this.chartsColumnData,
            nameLocation:this.xlabelAlignment,
            splitLine: {
              lineStyle: {
                color: this.xGridColor
              }, show: this.xGridSwitch
            },
            axisLine: {
              lineStyle: {
                color: this.xLabelColor,
              },
            },
            axisLabel: {
              show: this.xLabelSwitch,
              fontFamily: this.xLabelFontFamily,
              fontSize: this.xLabelFontSize,
              fontWeight: this.xlabelFontWeight,
              align: this.xlabelAlignment// Hide xAxis labels
            }
          },
          toggleGridLines: true,
          yAxis: {
            type: 'value',
            axisLine: {
              lineStyle: {
                color: this.yLabelColor
              }
            },
            axisLabel: {
              show: this.yLabelSwitch,
              fontFamily: this.xLabelFontFamily,
              fontSize: this.xLabelFontSize,
              fontWeight: this.xlabelFontWeight,
            },
            splitLine: {
              lineStyle: {
                color: this.yGridColor
              },
              show: this.yGridSwitch
            }
          },
          series: [
            {
              label: { show: true },
              type: 'line',
              data: this.chartsRowData,
              areaStyle: {}
            },
          ],
          color: this.color

        };
      }
    }
    sidebysideBar(){
      const dimensions: Dimension[] = this.dualAxisColumnData;
      const categories = this.flattenDimensions(dimensions);
      if(this.isApexCharts){
        this.chartOptions2 = {
          series: this.dualAxisRowData,
          annotations: {
            points: [{
              x: 'zoom',
              seriesIndex: 0,
              label: {
                borderColor: '#775DD0',
                offsetY: 0,
                style: {
                  color: '#fff',
                  background: '#775DD0',
                },
                text: 'zoom',
              }
            }]
          },
          colors: ['#2392c1', '#0dc9c5', '#f43f63'],
          chart: {
            toolbar: {
              show: true,
              offsetX: 0,
              offsetY: 0,
              tools: {
                download: true,
                selection: true,
                zoom: true,
                zoomin: true,
                zoomout: true,
                pan: true,
                reset: true || '<img src="./assets/images/icons/home-icon.png" width="20">',
              },
              autoSelected: 'zoom' 
            },
            type: 'bar',
            height: 320,
            background: this.backgroundColor
          },
          plotOptions: {
            bar: {
              horizontal: false,
              columnWidth: '55%',
              dataLabels: {
                position: 'top',
              }
            },
          },
          dataLabels: {
            enabled: true,
            formatter: this.formatNumber.bind(this),
            offsetY: -20,
            style: {
              fontSize: '12px',
              colors: [this.color],
            },
          },
          stroke: {
            show: true,
            width: 2,
            colors: ['transparent'],
          },
          xaxis: {
            categories: categories,
            tickPlacement: 'on',
            labels: {
              show: this.xLabelSwitch,
              hideOverlappingLabels: false,
              style: {
                colors: this.color,
                fontSize: '12px',
                fontFamily: 'Helvetica, Arial, sans-serif',
                fontWeight: 12,
              },
            },
          },
          yaxis: {
            title: {
              text: '',
            },
            labels: {
              show: this.yLabelSwitch,
              style: {
                colors: this.color,
                fontSize: '12px',
                fontFamily: 'Helvetica, Arial, sans-serif',
                fontWeight: 12,
              },
              formatter: this.formatNumber.bind(this)
            },
          },
          fill: {
            opacity: 1,
          },
          tooltip: {
            y: {
              formatter: function (val: any) {
                console.log(val)
                return val;
              },
            },
          },
          grid: {
            borderColor: this.GridColor,
            show: true,
            xaxis: {
              lines: {
                show: this.xGridSwitch
              }
            },
            yaxis: {
              lines: {
                show: this.yGridSwitch
              }
            },
          },
        };
    } else {
      let yaxisOptions = _.cloneDeep(this.dualAxisRowData);
      yaxisOptions.forEach((bar : any)=>{
bar["type"]="bar";
      });
      this.eSideBySideBarChartOptions = {
        backgroundColor: this.backgroundColor,
        legend: {
          orient: 'vertical',
          left: 'left'
        },
        toolbox: {
          feature: {
            magicType: { show: true, type: ['line'] },
            restore: { show: true },
            saveAsImage: { show: true }
          }
        },
        tooltip: {
          trigger: 'axis',
        },
        axisPointer: {
          type: 'none'
        },
        dataZoom: [
          {
            show: this.isZoom,
            type: 'slider'
          },

        ],
        grid: {
          left: '3%',
          right: '4%',
          bottom: '13%',
          containLabel: true,
        },
        yAxis: {
          type: 'value',
         
          splitLine: {
            lineStyle: {
              color: this.xGridColor
            }, show: this.xGridSwitch
          },
          axisLine: {
            lineStyle: {
              color: this.xLabelColor,
            },
          },
          axisLabel: {
            show: this.xLabelSwitch,
            fontFamily: this.xLabelFontFamily,
            fontSize: this.xLabelFontSize,
            fontWeight: this.xlabelFontWeight,
            align: this.xlabelAlignment// Hide xAxis labels
          }
        },
        toggleGridLines: true,
        xAxis: {
          type: 'category',
          data: categories,
          nameLocation:this.xlabelAlignment,
          axisLine: {
            lineStyle: {
              color: this.yLabelColor
            }
          },
          axisLabel: {
            show: this.yLabelSwitch,
            fontFamily: this.xLabelFontFamily,
            fontSize: this.xLabelFontSize,
            fontWeight: this.xlabelFontWeight,
          },
          splitLine: {
            lineStyle: {
              color: this.yGridColor
            },
            show: this.yGridSwitch
          }
        },
        series: yaxisOptions.map((series: any) => ({
          ...series,
          label: {
              show: true, // Enable data labels
              position: 'top', // Position of the labels (e.g., 'top', 'inside', etc.)
              formatter: '{c}', // Customize the label format (e.g., '{c}' for value)
              color: '#000', // Customize label color
              fontSize: 12, // Customize label font size
              fontWeight: 'bold', // Customize label font weight
              fontFamily: 'Helvetica, Arial, sans-serif' // Use custom font family if needed
          }
      })),
        color:this.color

      };
    }
    }
    flattenDimensions(dimensions: Dimension[]): string[] {
      const numCategories = Math.max(...dimensions.map(dim => dim.values.length));
      return Array.from({ length: numCategories }, (_, index) => {
        return dimensions.map(dim => dim.values[index] === null ? 'null' : dim.values[index] || '').join(',');
      });
    }
    stockedBar(){
      const dimensions: Dimension[] = this.dualAxisColumnData;
      const categories = this.flattenDimensions(dimensions);
      if(this.isApexCharts){
        this.chartOptions6 = {
          series: this.dualAxisRowData,
          annotations: {
            points: [{
              x: 'zoom',
              seriesIndex: 0,
              label: {
                borderColor: '#775DD0',
                offsetY: 0,
                style: {
                  color: '#fff',
                  background: '#775DD0',
                },
                text: 'zoom',
              }
            }]
          },
          chart: {
            type: "bar",
            height: 350,
            background: this.backgroundColor,
            stacked: true,
            toolbar: {
              show: true
            },
            zoom: {
              enabled: true
            }
          },
          responsive: [
            {
              breakpoint: 480,
              options: {
                legend: {
                  position: "bottom",
                  offsetX: -10,
                  offsetY: 0
                }

              }
            }
          ],
          plotOptions: {
            bar: {
              horizontal: false,
              dataLabels: {
                position: 'top',
              }
            }
          },
          xaxis: {
            type: "category",
            categories: categories,
            tickPlacement: 'on',
            labels: {
              show: this.xLabelSwitch,
              style: {
                colors: [],
                fontSize: '12px',
                fontFamily: 'Helvetica, Arial, sans-serif',
                fontWeight: 12,
              },
            },
          },
          yaxis: {
            show: true,
            labels: {
              show: this.yLabelSwitch,
              style: {
                colors: [],
                fontSize: '12px',
                fontFamily: 'Helvetica, Arial, sans-serif',
                fontWeight: 12,
              },
              formatter: this.formatNumber.bind(this)
            }
          },
          legend: {
            position: "right",
            offsetY: 40
          },
          fill: {
            opacity: 1
          },
          grid: {
            show: true,
            xaxis: {
              lines: {
                show: this.xGridSwitch
              }
            },
            yaxis: {
              lines: {
                show: this.yGridSwitch
              }
            },
          },
          dataLabels: {
            enabled: true,
            formatter: this.formatNumber.bind(this),
            offsetY: -20,
            style: {
              fontSize: '12px',
              colors: [this.color],
            },
          }
        };
    } else {
      let yaxisOptions = _.cloneDeep(this.dualAxisRowData);
      yaxisOptions.forEach((bar : any)=>{
bar["type"]="bar";
bar["stack"]="total";
      });
      this.eStackedBarChartOptions = {
        backgroundColor: this.backgroundColor,
        legend: {
          orient: 'vertical',
          left: 'left'
        },
        toolbox: {
          feature: {
            magicType: { show: true, type: ['line'] },
            restore: { show: true },
            saveAsImage: { show: true }
          }
        },
        tooltip: {
          trigger: 'axis',
        },
        axisPointer: {
          type: 'none'
        },
        dataZoom: [
          {
            show: this.isZoom,
            type: 'slider'
          },

        ],
        grid: {
          left: '3%',
          right: '4%',
          bottom: '13%',
          containLabel: true,
        },
        yAxis: {
          type: 'value',
         
          splitLine: {
            lineStyle: {
              color: this.xGridColor
            }, show: this.xGridSwitch
          },
          axisLine: {
            lineStyle: {
              color: this.xLabelColor,
            },
          },
          axisLabel: {
            show: this.xLabelSwitch,
            fontFamily: this.xLabelFontFamily,
            fontSize: this.xLabelFontSize,
            fontWeight: this.xlabelFontWeight,
            align: this.xlabelAlignment// Hide xAxis labels
          }
        },
        toggleGridLines: true,
        xAxis: {
          type: 'category',
          data: categories,
          nameLocation:this.xlabelAlignment,
          axisLine: {
            lineStyle: {
              color: this.yLabelColor
            }
          },
          axisLabel: {
            show: this.yLabelSwitch,
            fontFamily: this.xLabelFontFamily,
            fontSize: this.xLabelFontSize,
            fontWeight: this.xlabelFontWeight,
          },
          splitLine: {
            lineStyle: {
              color: this.yGridColor
            },
            show: this.yGridSwitch
          }
        },
        series: yaxisOptions.map((series:any) => ({
          ...series,
          label: {
              show:true, // Enable data labels
              position:'inside', // Position of the labels (e.g., 'top', 'inside', etc.)
              formatter:'{c}', // Customize the label format (e.g., '{c}' for value)
              color:'#000', // Customize label color (default black)
              fontSize:12, // Customize label font size
              fontWeight:'bold', // Customize label font weight
              fontFamily:'Helvetica, Arial, sans-serif' // Use custom font family if needed
          }
      })),        

      };
    }

    }

    barLineChart(){
      const dimensions: Dimension[] = this.dualAxisColumnData;
      const categories = this.flattenDimensions(dimensions);
      if (this.isApexCharts) {
          this.chartOptions5 = {
            series: [
              {
                name: this.dualAxisRowData[0]?.name,
                type: "column",
                data: this.dualAxisRowData[0]?.data,
                color: this.barColor
              },
              {
                name: this.dualAxisRowData[1]?.name,
                type: "line",
                data: this.dualAxisRowData[1]?.data,
                color: this.lineColor
              }
            ],
            annotations: {
              points: [{
                x: 'zoom',
                seriesIndex: 0,
                label: {
                  borderColor: '#775DD0',
                  offsetY: 0,
                  style: {
                    color: '#fff',
                    background: '#775DD0',
                  },
                  text: 'zoom',
                }
              }]
            },
            // colors: ['#00a5a2', '#31d1ce'],
            chart: {
              toolbar: {
                show: true,
                offsetX: 0,
                offsetY: 0,
                tools: {
                  download: true,
                  selection: true,
                  zoom: true,
                  zoomin: true,
                  zoomout: true,
                  pan: true,
                  reset: true || '<img src="./assets/images/icons/home-icon.png" width="20">',
                },
                autoSelected: 'zoom' 
              },
              height: 350,
              type: "line",
              background: this.backgroundColor
            },
            grid: {
              show: true,
              xaxis: {
                lines: {
                  show: this.xGridSwitch
                }
              },
              yaxis: {
                lines: {
                  show: this.yGridSwitch
                }
              },
            },
            stroke: {
              width: [0, 4]
            },
            title: {
              text: "",
              style: {
                fontSize: "13px",
                fontWeight: "bold",
                color: "#8c9097",
              },
            },
            dataLabels: {
              enabled: true,
              formatter: this.formatNumber.bind(this),
              offsetY: -20,
              style: {
                fontSize: '12px',
                // colors: [this.color],
              },
              background: {
                enabled: false,
              }
            },
            labels: categories,
            xaxis: {
              type: "",
              tickPlacement: 'on',
              labels: {
                show: this.xLabelSwitch,
                style: {
                  colors: [],
                  fontSize: '12px',
                  fontFamily: 'Helvetica, Arial, sans-serif',
                  fontWeight: 12,
                },
              }
            },
            yaxis: [
              {
                show: true,
                title: {
                  text: "",
                  style: {
                    fontSize: "13px",
                    fontWeight: "bold",
                    color: "#8c9097",
                  },
                },
                labels: {
                  show: this.yLabelSwitch,
                  style: {
                    colors: [],
                    fontSize: '12px',
                    fontFamily: 'Helvetica, Arial, sans-serif',
                    fontWeight: 12,
                  },
                  formatter: this.formatNumber.bind(this)
                }
              },
              {
                show: true,
                opposite: true,
                title: {
                  text: "",
                  style: {
                    fontSize: "13px",
                    fontWeight: "bold",
                    color: "#8c9097",
                  },
                },
                labels: {
                  show: this.yLabelSwitch,
                  style: {
                    colors: [],
                    fontSize: '12px',
                    fontFamily: 'Helvetica, Arial, sans-serif',
                    fontWeight: 12,
                  },
                  formatter: this.formatNumber.bind(this)
                }
              }
            ],
            plotOptions: {
              bar: {
                dataLabels: {
                  position: 'top',
                }
              }
            }

          };
      } else {
        this.eBarLineChartOptions = {
          backgroundColor: this.backgroundColor,
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'cross',
              crossStyle: {
                color: '#999'
              }, label: {
                backgroundColor: '#283b56'
              }
            }
          },
          dataZoom: {
            show: true,
            start: 0,
            end: 100
          },
          toolbox: {
            feature: {
              magicType: { show: true, type: ['bar', 'line'] },
              restore: { show: true },
              saveAsImage: { show: true }
            }
          },
          legend: {
            show:true
          },
          xAxis: [
            {
              type: 'category',
              data: categories,
              axisPointer: {
                type: 'shadow'
              },
              axisLabel: {
                color: this.xLabelColor, // Customize label color
                fontSize: this.xLabelFontSize, // Customize font size
                fontFamily: this.xLabelFontFamily, // Customize font family
                fontWeight: 'bold', // Customize font weight
                formatter(value:any) {
                    return value.length > 5 ? value.substring(0, 5) + '...' : value; // Truncate long labels
                }
            },
            splitLine: {
              lineStyle: {
                  color: this.xGridColor || '#cccccc' // Default x-axis grid line color
              },
              show: this.xGridSwitch // Toggle visibility based on user input
          }
            }
          ],
          yAxis: [
            {
              type: 'value',
              name: 'Bar Axis',
              position: 'left',
              axisLabel: {
                color: '#333', // Customize label color
                fontSize: 12, // Customize font size
                position: 'right',
                fontFamily: 'Arial, sans-serif', // Customize font family
                fontWeight: 'bold', // Customize font weight
                formatter(value:any) {
                    return value; // Customize label format (e.g., add units)
                }
            },
            splitLine: {
              lineStyle: {
                  color: this.yGridColor || '#cccccc' // Default x-axis grid line color
              },
              show: this.yGridSwitch // Toggle visibility based on user input
          }
            },
            {
              type: 'value',
              name: 'Line Axis',
              position: 'right',
              axisLabel: {
                color: '#333', // Customize label color
                fontSize: 12, // Customize font size
                position: 'left',
                fontFamily: 'Arial, sans-serif', // Customize font family
                fontWeight: 'bold', // Customize font weight
                formatter(value:any) {
                    return value ; // Customize label format (e.g., add units)
                }
            },
            splitLine: {
              lineStyle: {
                  color: this.yGridColor || '#cccccc' // Default x-axis grid line color
              },
              show: this.yGridSwitch // Toggle visibility based on user input
          }
            }
          ],
          // yAxis: {
          //       type: 'value',
          //       axisLine: {
          //           lineStyle: {
          //               color: "#8c9097"
          //           }
          //       },
          //       // splitLine: {
          //       //     lineStyle: {
          //       //         color: "rgba(142, 156, 173,0.1)"
          //       //     }
          //       // }
          //   },
          // yAxis: [
          //   {
          //     type: 'value',
          //     name: 'Precipitation',
          //     min: 0,
          //     max: 250,
          //     interval: 50,
          //     axisLabel: {
          //       formatter: '{value} ml'
          //     }
          //   }
          // ],
          series: [
            {
              name: this.dualAxisRowData[0]?.name,
              type: 'bar',
              // xAxisIndex: 1,
              // yAxisIndex: 1,
              // tooltip: {
              //   valueFormatter: function (value) {
              //     return value + ' ml';
              //   }
              // },
              data: this.dualAxisRowData[0]?.data,
              itemStyle:{
                color:this.barColor // Default bar color
            },
              label:{
                show:true,
              }
            },

            {
              name: this.dualAxisRowData[1]?.name,
              type: 'line',
              // xAxisIndex: 1,
              yAxisIndex: 1,
              // tooltip: {
              //   valueFormatter: function (value) {
              //     return value + ' °C';
              //   }
              // },
              lineStyle: {
                color: this.lineColor
              },
              data: this.dualAxisRowData[1]?.data,
              label:{
                show:true,
              }
            }
          ]
        };
      }
    }
    radarChart(){
      const dimensions: Dimension[] = this.dualAxisColumnData;
      const categories = this.flattenDimensions(dimensions);
      let radarArray = categories.map((value: any, index: number) => ({
        name: categories[index]
      }));
      let legendArray = this.radarRowData.map((data: any) => ({
        name: data.name
      }));
      this.eRadarChartOptions = {
        backgroundColor: this.backgroundColor,
        tooltip: { trigger: "item" },
        legend: {
          data: legendArray,
          show:this.legendSwitch,
          // orient: 'vertical',
          // left: 'center', 
          // bottom: '5%', 
        },
        radar: {
          axisName: {
            color: this.xLabelColor
          },
          axisLabel : {
            color : this.xLabelColor
          },
          // shape: 'circle',
          indicator:
            radarArray

        },
      //   label: {
      //     show: this.dataLabels, // Dynamically show or hide data labels            }
      // },
      series:[
        {
            type:'radar',
            data:this.radarRowData.map((dataItem: any) => ({
                ...dataItem,
                label:{
                    show:this.dataLabels,
                    formatter:'{c}',
                    color:'#000', // Default label color
                    fontSize:12, // Default label font size
                    fontFamily:'Arial' // Default label font family
                }
            }))
        }
    ]
      }
    }
    horizentalStockedBar(){
      const dimensions: Dimension[] = this.dualAxisColumnData;
      const categories = this.flattenDimensions(dimensions);
      if(this.isApexCharts){
        this.chartOptions7 = {
          series: this.dualAxisRowData,
          chart: {
            type: "bar",
            height: 350,
            background: this.backgroundColor,
            stacked: true,
            toolbar: {
              show: true
            },
            zoom: {
              enabled: true
            }
          },
          responsive: [
            {
              breakpoint: 480,
              options: {
                legend: {
                  position: "bottom",
                  offsetX: -10,
                  offsetY: 0
                }
              }
            }
          ],
          plotOptions: {
            bar: {
              horizontal: true,
              dataLabels: {
                position: 'top',
              }
            }
          },
          xaxis: {
            type: "category",
            categories: categories,
            labels: {
              show: this.xLabelSwitch,
              style: {
                colors: [],
                fontSize: '12px',
                fontFamily: 'Helvetica, Arial, sans-serif',
                fontWeight: 12,
              },
              formatter: this.formatNumber.bind(this)
            }
          },
          yaxis: {
            show: true,
            labels: {
              show: this.yLabelSwitch,
              style: {
                colors: [],
                fontSize: '12px',
                fontFamily: 'Helvetica, Arial, sans-serif',
                fontWeight: 12,
              },
            }
          },
          legend: {
            position: "right",
            offsetY: 40
          },
          fill: {
            opacity: 1
          },
          grid: {
            show: true,
            xaxis: {
              lines: {
                show: this.xGridSwitch
              }
            },
            yaxis: {
              lines: {
                show: this.yGridSwitch
              }
            },
          },
          dataLabels: {
            enabled: true,
            formatter: this.formatNumber.bind(this),
            offsetY: -20,
            style: {
              fontSize: '12px',
              colors: [this.color],
            },
          }
        };
    } else {
      let yaxisOptions = _.cloneDeep(this.dualAxisRowData);
      yaxisOptions.forEach((bar : any)=>{
bar["type"]="bar";
bar["stack"]="total";
      });
      this.ehorizontalStackedBarChartOptions = {
        backgroundColor: this.backgroundColor,
        legend: {
          orient: 'vertical',
          left: 'left'
        },
        toolbox: {
          feature: {
            magicType: { show: true, type: ['line'] },
            restore: { show: true },
            saveAsImage: { show: true }
          }
        },
        tooltip: {
          trigger: 'axis',
        },
        axisPointer: {
          type: 'none'
        },
        dataZoom: [
          {
            show: this.isZoom,
            type: 'slider'
          },

        ],
        grid: {
          left: '3%',
          right: '4%',
          bottom: '13%',
          containLabel: true,
        },
        xAxis: {
          type: 'value',
         
          splitLine: {
            lineStyle: {
              color: this.xGridColor
            }, show: this.xGridSwitch
          },
          axisLine: {
            lineStyle: {
              color: this.xLabelColor,
            },
          },
          axisLabel: {
            show: this.xLabelSwitch,
            fontFamily: this.xLabelFontFamily,
            fontSize: this.xLabelFontSize,
            fontWeight: this.xlabelFontWeight,
            align: this.xlabelAlignment// Hide xAxis labels
          }
        },
        toggleGridLines: true,
        yAxis: {
          type: 'category',
          data: categories,
          axisLine: {
            lineStyle: {
              color: this.yLabelColor
            }
          },
          axisLabel: {
            show: this.yLabelSwitch,
            fontFamily: this.xLabelFontFamily,
            fontSize: this.xLabelFontSize,
            fontWeight: this.xlabelFontWeight,
          },
          splitLine: {
            lineStyle: {
              color: this.yGridColor
            },
            show: this.yGridSwitch
          }
        },
        series:yaxisOptions.map((series:any) => ({
          ...series,
          label:{
              show:true, // Enable data labels
              position:'right', // Position of the labels (e.g., 'top', 'inside', etc.)
              formatter:'{c}', // Display the value of the bar
              color:'#000', // Default label color (can be updated)
              fontSize:this.xLabelFontSize, // Default label font size
              fontWeight:'bold', // Default label font weight
              fontFamily:this.xLabelFontFamily // Default label font family
          }
      })),
        

      };
    }
    }
    hGrouped(){
      const dimensions: Dimension[] = this.dualAxisColumnData;
      const categories = this.flattenDimensions(dimensions);
      if(this.isApexCharts){
        this.chartOptions8 = {
          series: this.dualAxisRowData,
          chart: {
            type: "bar",
            height: 430,
            background: this.backgroundColor,
          },
          plotOptions: {
            bar: {
              horizontal: true,
              dataLabels: {
                position: "top"
              }
            }
          },
          dataLabels: {
            enabled: true,
            formatter: this.formatNumber.bind(this),
            offsetY: -6,
            style: {
              fontSize: '12px',
              colors: [this.color],
            },
          },
          stroke: {
            show: true,
            width: 1,
            colors: ["#fff"]
          },
          xaxis: {
            categories: categories,
            labels: {
              show: this.xLabelSwitch,
              style: {
                colors: [],
                fontSize: '12px',
                fontFamily: 'Helvetica, Arial, sans-serif',
                fontWeight: 12,
              },
              formatter: this.formatNumber.bind(this)
            },
          },
          yaxis: {
            show: true,
            labels: {
              show: this.yLabelSwitch,
              style: {
                colors: [],
                fontSize: '12px',
                fontFamily: 'Helvetica, Arial, sans-serif',
                fontWeight: 12,
              },
            },
          },
          grid: {
            show: true,
            xaxis: {
              lines: {
                show: this.xGridSwitch
              }
            },
            yaxis: {
              lines: {
                show: this.yGridSwitch
              }
            },
          },
        };
     } else {
        let yaxisOptions = _.cloneDeep(this.dualAxisRowData);
        yaxisOptions.forEach((bar : any)=>{
  bar["type"]="bar";
        });
        this.eGroupedBarChartOptions = {
          backgroundColor: this.backgroundColor,
          legend: {
            orient: 'vertical',
            left: 'left'
          },
          toolbox: {
            feature: {
              magicType: { show: true, type: ['line'] },
              restore: { show: true },
              saveAsImage: { show: true }
            }
          },
          tooltip: {
            trigger: 'axis',
          },
          axisPointer: {
            type: 'none'
          },
          dataZoom: [
            {
              show: this.isZoom,
              type: 'slider'
            },
  
          ],
          grid: {
            left: '3%',
            right: '4%',
            bottom: '13%',
            containLabel: true,
          },
          xAxis: {
            type: 'value',
           
            splitLine: {
              lineStyle: {
                color: this.xGridColor
              }, show: this.xGridSwitch
            },
            axisLine: {
              lineStyle: {
                color: this.xLabelColor,
              },
            },
            axisLabel: {
              show: this.xLabelSwitch,
              fontFamily: this.xLabelFontFamily,
              fontSize: this.xLabelFontSize,
              fontWeight: this.xlabelFontWeight,
              align: this.xlabelAlignment// Hide xAxis labels
            }
          },
          toggleGridLines: true,
          yAxis: {
            type: 'category',
            data: categories,
            axisLine: {
              lineStyle: {
                color: this.yLabelColor
              }
            },
            axisLabel: {
              show: this.yLabelSwitch,
              fontFamily: this.xLabelFontFamily,
              fontSize: this.xLabelFontSize,
              fontWeight: this.xlabelFontWeight,
            },
            splitLine: {
              lineStyle: {
                color: this.yGridColor
              },
              show: this.yGridSwitch
            }
          },
          series:yaxisOptions.map((series:any) => ({
            ...series,
            label:{
                show:true, // Enable data labels
                position:'right', // Position of the labels (e.g., 'top', 'inside', etc.)
                formatter:'{c}', // Display the value of the bar
                color:'#000', // Default label color (can be updated)
                fontSize:this.xLabelFontSize, // Default label font size
                fontWeight:'bold', // Default label font weight
                fontFamily:this.xLabelFontFamily // Default label font family
            }
        })),
  
        };
      }
    }
    multiLineChart(){
      const dimensions: Dimension[] = this.dualAxisColumnData;
      const categories = this.flattenDimensions(dimensions);
      if(this.isApexCharts){
        this.chartOptions9 = {
          series: this.dualAxisRowData,
          annotations: {
            points: [{
              x: 'zoom',
              seriesIndex: 0,
              label: {
                borderColor: '#775DD0',
                offsetY: 0,
                style: {
                  color: '#fff',
                  background: '#775DD0',
                },
                text: 'zoom',
              }
            }]
          },
          chart: {
            toolbar: {
              show: true,
              offsetX: 0,
              offsetY: 0,
              tools: {
                download: true,
                selection: true,
                zoom: true,
                zoomin: true,
                zoomout: true,
                pan: true,
                reset: true || '<img src="./assets/images/icons/home-icon.png" width="20">',
              },
              autoSelected: 'zoom' 
            },
            height: 350,
            type: "line",
            background: this.backgroundColor,
          },
          dataLabels: {
            enabled: true,
            formatter: this.formatNumber.bind(this),
            offsetY: -20,
            style: {
              fontSize: '12px',
              // colors: [this.color],
            },
            background: {
              enabled: false,
            }
          },
          stroke: {
            width: 5,
            curve: "straight",
            dashArray: [0, 8, 5]
          },
          title: {
            text: "",
            align: "left"
          },
          legend: {
            tooltipHoverFormatter: function (val: any, opts: any) {
              return (
                val +
                " - <strong>" +
                opts.w.globals.series[opts.seriesIndex][opts.dataPointIndex] +
                "</strong>"
              );
            }
          },
          markers: {
            size: 0,
            hover: {
              sizeOffset: 6
            }
          },
          xaxis: {
            categories: categories,
            tickPlacement: 'on',
            labels: {
              show: this.xLabelSwitch,
              style: {
                colors: [],
                fontSize: '12px',
                fontFamily: 'Helvetica, Arial, sans-serif',
                fontWeight: 12,
              },
            },
          },
          yaxis: {
            show: true,
            labels: {
              show: this.yLabelSwitch,
              style: {
                colors: [],
                fontSize: '12px',
                fontFamily: 'Helvetica, Arial, sans-serif',
                fontWeight: 12,
              },
              formatter: this.formatNumber.bind(this)
            },
          },
          tooltip: {
            y: [
              {
                title: {
                  formatter: function (val: any) {
                    return val;
                  }
                }
              },
            ]
          },
          grid: {
            show: true,
            xaxis: {
              lines: {
                show: this.xGridSwitch
              }
            },
            yaxis: {
              lines: {
                show: this.yGridSwitch
              }
            },
          }
        };
    } else {
      let yaxisOptions = _.cloneDeep(this.dualAxisRowData);
      yaxisOptions.forEach((bar : any)=>{
bar["type"]="line";
bar["stack"]="Total";
      });
      this.eMultiLineChartOptions = {
        backgroundColor: this.backgroundColor,
        legend: {
          orient: 'vertical',
          left: 'left'
        },
        toolbox: {
          feature: {
            magicType: { show: true, type: ['bar'] },
            restore: { show: true },
            saveAsImage: { show: true }
          }
        },
        tooltip: {
          trigger: 'axis',
        },
        axisPointer: {
          type: 'none'
        },
        dataZoom: [
          {
            show: this.isZoom,
            type: 'slider'
          },

        ],
        grid: {
          left: '3%',
          right: '4%',
          bottom: '13%',
          containLabel: true,
        },
        xAxis: {
          type: 'category',
          data: categories,
         
          splitLine: {
            lineStyle: {
              color: this.xGridColor
            }, show: this.xGridSwitch
          },
          axisLine: {
            lineStyle: {
              color: this.xLabelColor,
            },
          },
          axisLabel: {
            show: this.xLabelSwitch,
            fontFamily: this.xLabelFontFamily,
            fontSize: this.xLabelFontSize,
            fontWeight: this.xlabelFontWeight,
            align: this.xlabelAlignment// Hide xAxis labels
          }
        },
        toggleGridLines: true,
        yAxis: {
          type:'value',
          axisLine: {
            lineStyle: {
              color: this.yLabelColor
            }
          },
          axisLabel: {
            show: this.yLabelSwitch,
            fontFamily: this.xLabelFontFamily,
            fontSize: this.xLabelFontSize,
            fontWeight: this.xlabelFontWeight,
          },
          splitLine: {
            lineStyle: {
              color: this.yGridColor
            },
            show: this.yGridSwitch
          }
        },
        series:yaxisOptions.map((series:any) => ({
          ...series,
          label:{
              show:true, // Enable data labels
              position:'right', // Position of the labels (e.g., 'top', 'inside', etc.)
              formatter:'{c}', // Display the value of the bar
              color:'#000', // Default label color (can be updated)
              fontSize:this.xLabelFontSize, // Default label font size
              fontWeight:'bold', // Default label font weight
              fontFamily:this.xLabelFontFamily // Default label font family
          }
      })),
        

      };
    }
    }
    donutChart(){
      const self = this;
      if(this.isApexCharts){
        this.chartOptions10 = {
          series: this.chartsRowData,
          chart: {
            type: "donut",
            background: this.backgroundColor,
            events: {
              dataPointSelection: function (event: any, chartContext: any, config: any) {
                if (self.drillDownIndex < self.draggedDrillDownColumns.length - 1) {
                  const selectedXValue = self.chartsColumnData[config.dataPointIndex];
                  console.log('X-axis value:', selectedXValue);
                  let nestedKey = self.draggedDrillDownColumns[self.drillDownIndex];
                  self.drillDownIndex++;
                  let obj = { [nestedKey]: selectedXValue };
                  self.drillDownObject.push(obj);
                  self.setOriginalData();
                  self.dataExtraction();
                }
              }
            }
          },
          labels: this.chartsColumnData.map((category: any) => category === null ? 'null' : category),
          responsive: [
            {
              breakpoint: 480,
              options: {
                chart: {
                  width: 100
                },
                legend: {
                  position: "bottom"
                }
              }
            }
          ],
          legend: {
            show: true,
          },
          dataLabels: {
            enabled: this.dataLabels,
          },
          plotOptions: {
            pie: {
              donut: {
                labels: {
                  show: true,
                  name: {
                    show: true
                  },
                  value: {
                    show: true,
                    formatter: (val:any) => {
                      return val;
                    }
                  },
                  total: {
                    show: true,
                    showAlways: true,
                    formatter: (w:any) => {
                      return w.globals.seriesTotals.reduce((a:any, b:any) => {
                        return +a + b
                      }, 0).toFixed(this.donutDecimalPlaces);
                    }
                  }
                }
              }
            }
          },
        };
        this.changeLegendsAllignment('bottom');
      } else {
          let combinedArray = this.chartsRowData.map((value : any, index :number) => ({
            value: value,
            name: this.chartsColumnData[index]
          }));
          // let legendObject = this.setEchartLegendAlignment();
          this.eDonutChartOptions = {
            backgroundColor: this.backgroundColor,
            tooltip: {
              trigger: 'item'
            },
            legend: {
              orient: 'vertical',
              left: 'left',
              type:'scroll',
              show: this.legendSwitch // Control legend visibility
          },            
          label: {
              show : this.dataLabels,
              formatter: '{b}: {d}%',
            },
            series: [
              {
                type: 'pie',
                radius: [this.donutSize+'%' , '70%'],
                data: combinedArray,
                avoidLabelOverlap: true,
                emphasis: {
                  itemStyle: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                  }
                },
                label: {
                  show: this.dataLabels, // Dynamically show or hide data labels            }
              }
              }
            ]
          };
        }
      }
    
     
      heatMapChart() {
        const dimensions: Dimension[] = this.dualAxisColumnData;
        const categories = this.flattenDimensions(dimensions);
        if(this.isApexCharts){
        this.heatMapChartOptions = {
          series: this.dualAxisRowData,
          chart: {
            height: 350,
            type: 'heatmap',
            background: this.backgroundColor,
          },
          plotOptions: {
            heatmap: {
              shadeIntensity: 0.5,
              colorScale: {
                ranges: [],
                // Stops define the gradient stops for color intensity
                stops: [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
                // Enable this to inverse the colors
                inverseColors: true
              }
            }
          },
          dataLabels: {
            enabled: true,
            style: {
              colors: [],
              fontSize: '12px',
              fontFamily: 'Helvetica, Arial, sans-serif',
              fontWeight: 12,
            },
            formatter: this.formatNumber.bind(this)
          },
          xaxis: {
            type: 'category',
            categories: categories,
            labels: {
              show: this.xLabelSwitch,
              style: {
                colors: [],
                fontSize: '12px',
                fontFamily: 'Helvetica, Arial, sans-serif',
                fontWeight: 12,
                },
            }
          },
          yaxis: {
            title: {
              text: ''
            },
            show: true,
            labels: {
              show: this.yLabelSwitch,
              style: {
                colors: [],
                fontSize: '12px',
                fontFamily: 'Helvetica, Arial, sans-serif',
                fontWeight: 12,
              },
            }
          },
          legend: {
            show: true,
            position: 'bottom'
          },
          grid: {
            padding: {
              right: 20
            },
            show:true,
            xaxis: {
              lines:this.xGridSwitch
            },
            yaxis:{
              lines:this.yGridSwitch
            }
          }
        };
      }else{
        this.eHeatMapChartOptions = {
          tooltip: {
              position: 'top'
          },
          grid: {
              left: '3%',
              right: '4%',
              bottom: '3%',
              containLabel: true
          },
          xAxis: {
              type: 'category',
              data: categories,
              axisLabel: {
                  show: this.xLabelSwitch,
                  interval: 0,
                  rotate: 45,
                  textStyle: {
                      color: this.xLabelColor,
                      fontSize: this.xLabelFontSize,
                      fontFamily: this.xLabelFontFamily,
                      fontWeight: this.xlabelFontWeight,
                  }
              }
          },
          yAxis: {
              type: 'category',
              data: this.dualAxisRowData.map((row: { name: any; }) => row.name), // Adjust as necessary
              axisLabel: {
                  show: this.yLabelSwitch,
                  textStyle: {
                      color:this.yLabelColor,
                      fontSize : this.yLabelFontSize,
                      fontFamily : this.yLabelFontFamily,
                      fontWeight : this.ylabelFontWeight
                  }
              }
          },
          visualMap: {
              min : 0,
              max : this.getMaxValue(this.dualAxisRowData),
              calculable : true,
              orient : 'horizontal',
              left : 'center',
              // bottom : '15%',
              top: '5%',
              inRange : {
                  color : ['#ffffff', '#ff0000'] // Adjust colors as needed
              }
          },
          series : [{
            name : this.dualAxisRowData,
            type : 'heatmap',
            data : this.prepareHeatmapData(this.dualAxisRowData), // Prepare your data accordingly
            label : {
                show : true,
                formatter : (params: { value: number[]; }) => this.formatNumber(params.value[2]) // Assuming value[2] holds the number to format
            },
            emphasis : {
                itemStyle : {
                    shadowBlur : 10,
                    shadowColor : '#333'
                }
            }
        }],
        dataZoom: [
          {
            show: this.isZoom,
            type: 'slider'
          },

        ],
      };
      }
      
      }
      prepareHeatmapData(rowData: any[]) {
        const heatmapData: any[][] = [];
        rowData.forEach((row, rowIndex) => {
            row.data.forEach((value: null | undefined, colIndex: any) => { // Assuming each row has a `data` array
                if (value !== null && value !== undefined) { // Ensure value is valid
                    heatmapData.push([colIndex, rowIndex, value]); // [xIndex, yIndex, value]
                }
            });
        });
        return heatmapData;
      }
      getMaxValue(rowData:any) {
        let max = Number.NEGATIVE_INFINITY; 
        rowData.forEach((row: { data: any[]; }) => {
            row.data.forEach(value => { 
                if (value !== null && value !== undefined) { 
                    max = Math.max(max, value); // Update max if current value is greater
                }
            });
        });
        return max === Number.NEGATIVE_INFINITY ? 0 : max; // Return 0 if no valid values found
    }

  funnelChart() {
    const dimensions: Dimension[] = this.dualAxisColumnData;
    const categories = this.flattenDimensions(dimensions);
    if (this.isEChatrts) {
      const combinedArray: any[] = [];
      this.dualAxisColumnData.forEach((item: any) => {
        this.dualAxisRowData.forEach((categoryObj: any) => {
          item.values.forEach((value: any, index: number) => {
            combinedArray.push({
              name: value,
              value: categoryObj.data[index]
            });
          });
        });
      });
      this.eFunnelChartOptions = {
        color:[this.color],
        tooltip: {
          trigger: 'item',
        },
        series: [
          {
            name: '',
            type: 'funnel',
            data: combinedArray,
            label: {
              show: true,
              fontFamily:this.dataLabelsFontFamily,
              fontSize:this.dataLabelsFontSize,
              formatter: '{b}: {c}', // {b} - name, {c} - primary value (default is sales here)
            },
          },
        ],
      };
    } else {
      this.funnelChartOptions = {
        series: this.dualAxisRowData,
        chart: {
          type: "bar",
          height: 350,
          background: this.backgroundColor,
        },
        plotOptions: {
          bar: {
            borderRadius: 0,
            horizontal: true,
            barHeight: "80%",
            isFunnel: true,
            dataLabels: {
              position: "center",
            }
          }
        },
        dataLabels: {
          enabled: true,
          formatter: (val: any, opts: any) => {
            const category = opts.w.config.xaxis.categories[opts.dataPointIndex];
            const formattedValue = this.formatNumber(val);
            return `${category}: ${formattedValue}`;
        },
          // formatter: this.formatNumber.bind(this),
          dropShadow: {
            enabled: true,
          },
          style: {
            fontSize: "8px",
            fontFamily: "Helvetica, Arial, sans-serif",
          },
        },
        title: {
        },
        xaxis: {
          categories: categories
        },
        legend: {
          show: false
        },
      };
    }
  }
      guageChart() {
        // Clone the gauge number from the API response
        this.guageNumber = _.cloneDeep(this.tablePreviewRow[0]?.result_data?.[0] ?? 0);
    
        // Define thresholds and corresponding max values
        const thresholds = [
          { limit: 1000, max: 1000 },       // Up to 1,000
          { limit: 10000, max: 10000 },     // Up to 10,000
          { limit: 100000, max: 100000 },    // Up to 1 lakh
          { limit: 500000, max: 500000 },    // Up to 5 lakhs
          { limit: 1000000, max: 1000000 },   // Up to 10 lakhs
            { limit: Infinity, max: Math.ceil(this.guageNumber / 1000000) * 1000000 } // Above 10 lakhs
        ];
    
        // Determine maxValueGuage based on guageNumber
        const determineMaxValue = (value: number) => {
            for (const threshold of thresholds) {
                if (value <= threshold.limit) {
                    return threshold.max;
                }
            }
        };
    
        // Set maxValueGuage based on guageNumber
        this.maxValueGuage = determineMaxValue(this.guageNumber)!;
    
        // Calculate the value to divide
        this.valueToDivide = this.maxValueGuage - this.minValueGuage;
        this.guageChart1()
      }
    customMinMaxGuage(){
       this.valueToDivide = this.maxValueGuage-this.minValueGuage;
       this.guageChart1();
    }
  
      guageChart1() {
        // this.guageNumber = _.cloneDeep(this.tablePreviewRow[0]?.result_data?.[0] ?? 0);
        // this.maxValueGuage = this.maxValueGuage ? this.maxValueGuage:this.KPINumber*2
        //  const valueToDivide = this.maxValueGuage-this.minValueGuage
        // Initialize the chart options
        this.guageChartOptions = {
          series: [ ((this.guageNumber / this.valueToDivide)*100)], // Correct percentage calculation
          chart: {
            height: 350,
            type: 'radialBar',
            background: this.backgroundColor,
            toolbar: {
              show: true
            },
          },
          colors: [this.color],

          plotOptions: {
            radialBar: {
              startAngle: -120,
              endAngle: 120,
              track: {
                background: '#333',
                startAngle: -120,
                endAngle: 120,
              },
              dataLabels: {
                show: true,
                name: {
                  offsetY: -20,
                  show: true,
                  color: '#888',
                  fontSize: '16px'
                },
                value: {
                  formatter: (val:any) => `${val.toFixed(2)}%`, // Displaying percentage
                  color: '#333',
                  fontSize: this.dataLabelsFontSize,
                  fontFamily:this.dataLabelsFontFamily,
                  show: true,
                },
              },
              min: this.minValueGuage,  // Use user's min value
              max: this.maxValueGuage
            }
          },
          
          tooltip: {
            enabled: true,
            shared: false, // Set to false for individual tooltips
            custom: ({ series }: { series: number[] }) => {
                return `<div style="padding: 10px;">
                            <strong>Value:</strong> ${this.guageNumber}<br>
                            <strong>Percentage:</strong> ${series[0].toFixed(2)}%
                        </div>`;
            }
        },
          fill: {
            type: "gradient",
            gradient: {
              shade: "dark",
              type: "horizontal",
              gradientToColors: ["#87D4F9"],
              stops: [0, 100]
            }
          },
          stroke: {
            lineCap: "round"
          },
          labels: [this.tablePreviewRow[0]?.col ?? 'Label'], // Fallback for label
        };
      }     
      calendarChart() {
        let calendarData: any[] = [];
        let years: Set<any> = new Set();
    
        // Populate calendarData and collect years
        this.chartsColumnData.forEach((data: any, index: any) => {
            let arr = [data, this.chartsRowData[index]];
            calendarData.push(arr);
    
            const year = new Date(data).getFullYear();
            years.add(year);
        });
    
        const minValue = this.chartsRowData.reduce((a: any, b: any) => (a < b ? a : b), Infinity);
        const maxValue = this.chartsRowData.reduce((a: any, b: any) => (a > b ? a : b), -Infinity);
    
        // Convert years set to array and sort it in ascending order
        let yearArray = Array.from(years).sort((a: any, b: any) => a - b);
    
        // Define the height for each calendar
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
    
        // Extract data for each year and assign to different series
        let series = yearArray.map((year: any) => {
            const yearData = calendarData.filter(d => new Date(d[0]).getFullYear() === year);
            return {
                type: 'heatmap',
                coordinateSystem: 'calendar',
                calendarIndex: yearArray.indexOf(year),
                data: yearData
            };
        });

        let dataZoomConfig = [
          {
              type: 'slider',
              yAxisIndex: 0,
              start: 0,  // Starting position of the scroll
              end: 100,  // The scroll window size (adjustable)
              orient: 'vertical',  // Allow vertical scrolling
              zoomLock: false,  // Disable zoom lock for flexibility
          }
      ];
    
        this.eCalendarChartOptions = {
            tooltip: {
                position: 'top',
                formatter: function (params: any) {
                    const date = params.data[0];
                    const value = params.data[1];
                    return `Date: ${date}<br/>Value: ${value}`;
                }
            },
            visualMap: {
                min: minValue,
                max: maxValue,
                calculable: true,
                orient: 'horizontal',
                left: 'center',
                top: 'bottom'
            },
            calendar: calendars,
            series: series,  // Assign filtered data series to the chart
            grid: {
                height: totalHeight,
                containLabel: true
            },
            dataZoom: dataZoomConfig 
        };
    
        console.log(this.eCalendarChartOptions);
    }

      tableDimentions = [] as any;
      tableMeasures = [] as any;
      columnsData(){
        const obj = {
          "db_id": this.databaseId,
          "queryset_id": this.qrySetId,
          "search": this.tableSearch
        } as any;
        if (this.fromFileId) {
          delete obj.db_id;
          obj.file_id = this.fileId;
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
        const obj = {
          "database_id": this.databaseId,
          "queryset_id": this.qrySetId,
          "col": draggedColumnsObj,
          "row": this.draggedRowsData,
          "filter_id": this.filterId,
          "datasource_querysetid": this.filterQuerySetId,
          "sheetfilter_querysets_id": this.sheetfilter_querysets_id,
          "hierarchy": this.draggedDrillDownColumns,
          "is_date": this.dateDrillDownSwitch,
          "drill_down": this.drillDownObject,
          "next_drill_down": this.draggedDrillDownColumns[this.drillDownIndex],
          "parent_user":this.createdBy
        } as any;
        if (this.fromFileId) {
          delete obj.database_id;
          obj.file_id = this.fileId;
        }
        this.workbechService.getDataExtraction(obj).subscribe({
          next: (responce: any) => {
            this.tablePaginationRows=responce.rows;
            this.tablePaginationColumn=responce.columns;
            this.tablePaginationCustomQuery=responce.custom_query;
            this.chartsDataSet(responce);
            this.mulColData = responce.columns;
            this.mulRowData = responce.rows;
            if (this.chartsRowData.length > 0) {
              // this.enableDisableCharts();
              // this.chartsOptionsSet();
              if (this.retriveDataSheet_id && !this.isEChatrts) {
                const dimensions: Dimension[] = this.dualAxisColumnData;
                const categories = this.flattenDimensions(dimensions);
                let object : any;
                if (this.barchart) {
                  this.chartOptions3.series[0].data = this.chartsRowData;
                  this.chartOptions3.xaxis.categories = this.chartsColumnData.map((category : any)  => category === null ? 'null' : category);
                  this.chartOptions3.xaxis.convertedCatToNumeric = true;
                  // console.log(this.chartOptions3.xaxis.categories);
                  // console.log(this.chartOptions3);
                  object = [{data : this.chartsRowData}];
                  this.barchart.updateSeries(object);
                  object = {xaxis: {categories : this.chartsColumnData.map((category : any)  => category === null ? 'null' : category), convertedCatToNumeric : true}};
                  this.barchart.updateOptions(object);
                  console.log(this.barchart);
                }
                else if (this.piechart) {
                  this.chartOptions4.series = this.chartsRowData;
                  this.chartOptions4.labels = this.chartsColumnData.map((category : any)  => category === null ? 'null' : category);
                }
                else if (this.linechart) {
                  this.chartOptions.series[0].data = this.chartsRowData;
                  this.chartOptions.xaxis.categories = this.chartsColumnData;
                  this.chartOptions.xaxis.convertedCatToNumeric = true;
                  object = [{data : this.chartsRowData}];
                  this.linechart.updateSeries(object);
                  object = {xaxis: {categories : this.chartsColumnData, convertedCatToNumeric : true}};
                  this.linechart.updateOptions(object);
                  console.log(this.linechart);
                }
                else if (this.areachart) {
                  this.chartOptions1.series[0].data = this.chartsRowData;
                  this.chartOptions1.labels = this.chartsColumnData;
                  this.chartOptions1.xaxis.convertedCatToNumeric = true;
                  object = [{data : this.chartsRowData}];
                  this.areachart.updateSeries(object);
                  object = {xaxis: {categories : this.chartsColumnData, convertedCatToNumeric : true}};
                  this.areachart.updateOptions(object);
                  console.log(this.linechart);
                }
                else if (this.sidebysideChart) {
                  this.chartOptions2.series = this.dualAxisRowData;
                  this.chartOptions2.xaxis.categories = categories;
                  object = [{data : this.dualAxisRowData}];
                  this.sidebysideChart.updateSeries(object);
                  object = {xaxis: {categories : categories}};
                  this.sidebysideChart.updateOptions(object);
                  console.log(this.sidebysideChart);
                }
                else if (this.stockedChart) {
                  this.chartOptions6.series = this.dualAxisRowData;
                  this.chartOptions6.xaxis.categories = categories;
                  object = [{data : this.dualAxisRowData}];
                  this.stockedChart.updateSeries(object);
                  object = {xaxis: {categories : categories}};
                  this.stockedChart.updateOptions(object);
                  console.log(this.stockedChart);
                }
                else if (this.barlineChart) {
                  // this.chartOptions5.series[0] = {name: this.dualAxisRowData[0]?.name,type: "column",data: this.dualAxisRowData[0]?.data};
                  // this.chartOptions5.series[1] = {name: this.dualAxisRowData[1]?.name,type: "line",data: this.dualAxisRowData[1]?.data};
                  this.chartOptions5.series[0].data = this.dualAxisRowData[0]?.data;
                  this.chartOptions5.series[1].data = this.dualAxisRowData[1]?.data;
                  this.chartOptions5.labels = categories;
                  this.chartOptions5.xaxis.categories = categories;
                  object = [{data : this.dualAxisRowData}];
                  this.barlineChart.updateSeries(object);
                  object = {xaxis: {categories : categories}};
                  this.barlineChart.updateOptions(object);
                  console.log(this.barlineChart);
                }
                else if (this.horizontolstockedChart) {
                  this.chartOptions7.series = this.dualAxisRowData;
                  this.chartOptions7.xaxis.categories = categories;
                  object = [{data : this.dualAxisRowData}];
                  this.horizontolstockedChart.updateSeries(object);
                  object = {xaxis: {categories : categories}};
                  this.horizontolstockedChart.updateOptions(object);
                  console.log(this.horizontolstockedChart);
                }
                else if (this.groupedChart) {
                  this.chartOptions8.series = this.dualAxisRowData;
                  this.chartOptions8.xaxis.categories = categories;
                  object = [{data : this.dualAxisRowData}];
                  this.groupedChart.updateSeries(object);
                  object = {xaxis: {categories : categories}};
                  this.groupedChart.updateOptions(object);
                  console.log(this.groupedChart);
                }
                else if (this.multilineChart) {
                  this.chartOptions9.series = this.dualAxisRowData;
                  this.chartOptions9.xaxis.categories = categories;
                  object = [{data : this.dualAxisRowData}];
                  this.multilineChart.updateSeries(object);
                  object = {xaxis: {categories : categories}};
                  this.multilineChart.updateOptions(object);
                  console.log(this.multilineChart);
                }
                else if (this.donutchart) {
                  this.chartOptions10.series = this.chartsRowData;
                  this.chartOptions10.labels = this.chartsColumnData.map((category : any)  => category === null ? 'null' : category);
                }
                else if (this.heatMap) {
                  this.heatMapChartOptions.series = this.dualAxisRowData;
                  this.heatMapChartOptions.xaxis.categories = categories;
                  object = [{data : this.dualAxisRowData}];
                  this.heatmapcharts.updateSeries(object);
                  object = {xaxis: {categories : categories}};
                  this.heatmapcharts.updateOptions(object);
                  console.log(this.heatmapcharts);
                }
                else if (this.funnel) {
                  this.funnelChartOptions.series = this.dualAxisRowData;
                  this.funnelChartOptions.xaxis.categories = categories;
                  object = [{data : this.dualAxisRowData}];
                  this.funnelCharts.updateSeries(object);
                  object = {xaxis: {categories : categories}};
                  this.funnelCharts.updateOptions(object);
                  console.log(this.funnelCharts);
                } else if(this.map){
                  this.mapChart();
                }
                else if(this.calendar){
                  this.calendarChart();
                }
                // this.updateChart();
              }
              else{
                this.chartsOptionsSet();
              }
            }
           
            if (((this.kpi || this.guage) && (this.draggedColumns.length > 0 || this.draggedRows.length !== 1)) || (!(this.kpi || this.guage) &&(this.draggedColumns.length < 1 || this.draggedRows.length < 1)) || (this.map && (this.draggedRows.length < 1 || this.draggedColumns.length != 1)) || (this.barLine && this.draggedRows.length !== 2)) {
              if(!this.table){
                this.toasterService.info('Changed to Table Chart','Info',{ positionClass: 'toast-top-right'});
              }
              this.table = true;
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
            } else if((this.draggedColumns.length > 1 && this.draggedRows.length > 0 && (this.pie || this.bar || this.area || this.line || this.donut))) {
              this.table = false;
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
              this.sidebysideBar();
              this.toasterService.info('Changed to Dual Axis Chart','Info',{ positionClass: 'toast-top-right'});
            }
            if(this.table){
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
            database_id: this.databaseId,
            file_id: this.fileId,
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

      chartsDataSet(data: any) {
        let sidebysideBarColumnData = [];
        this.sheetCustomQuery = data.custom_query;
        // this.sheetfilter_querysets_id = data.sheetfilter_querysets_id || data.sheet_filter_quereyset_ids;
        this.tablePreviewColumn = data.data?.col ? data.data.col : data.sheet_data?.col ? data.sheet_data.col : [];
        this.tablePreviewRow = data.data?.row ? data.data.row : data.sheet_data?.row ? data.sheet_data.row : [];
        
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

      chartsOptionsSet(){
        if (this.bar) {
          this.barChart();
        } else if (this.area) {
          this.areaChart();
        } else if (this.line) {
          this.lineChart();
        } else if (this.pie) {
          this.pieChart();
        } else if (this.sidebyside) {
          this.sidebysideBar();
        } else if (this.stocked) {
          this.stockedBar();
        } else if (this.barLine) {
          this.barLineChart();
        } else if (this.horizentalStocked) {
          this.horizentalStockedBar();
        } else if (this.grouped) {
          this.hGrouped();
        } else if (this.multiLine) {
          this.multiLineChart();
        } else if (this.donut) {
          this.donutChart();
        } else if (this.radar) {
          this.radarChart();
        } else if (this.heatMap) {
          this.heatMapChart();
        } else if (this.kpi){
          this.KPIChart();
        } else if (this.funnel){
          this.funnelChart();
        }else if(this.guage){
          this.guageChart();
        } else if(this.map){
          this.http.get('./assets/maps/world.json').subscribe((geoJson: any) => {
            echarts.registerMap('world', geoJson);  // Register the map data
      
            // Initialize the chart after the map is registered
            this.mapChart();
          });
        } else if(this.calendar){
          this.calendarChart();
        }
        
      }

      mapChart(){
       let minData : number = 0;
       let maxData: number = Math.max(...this.chartsRowData);
       let result:any[] = [];

       // Loop through the countries (assuming both data sets align by index)
       this.dualAxisColumnData[0].values.forEach((country: string, index: number) => {
         // Create an object for each country
         const countryData: any = { name: country , value : this.chartsRowData[index]};
     
         // Add each measure to the country object
         this.dualAxisRowData.forEach((measure:any) => {
           const measureName = measure.name; // e.g., sum(Sales), sum(Quantity)
           const measureValue = measure.data[index]; // Value for that measure
           countryData[measureName] = measureValue;
         });
     
         result.push(countryData);
       });
    if(this.chartsColumnData && this.chartsColumnData.length > 1){
    minData= Math.min(...this.chartsRowData);
    }
    if(Number.isNaN(minData) || Number.isNaN(maxData)){
      minData = 0;
      maxData = 1;
    }
    
    this.eMapChartOptions = {
      tooltip: {
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
          },
      visualMap: {
        min: minData,
        max: maxData,
        text: ['High', 'Low'],
        realtime: false,
        calculable: true,
        inRange: {
         color: ['lightskyblue', 'yellow', 'orangered']
        }
      },
      series: [{
        type: 'map',
        map: 'world',
        roam: this.isZoom,  
        data: result
      }]
    };
      }

      KPIChart(){
        this.KPINumber = _.cloneDeep(this.tablePreviewRow[0].result_data[0]);
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

      if (this.dateList.includes(element.data_type)) {
        this.dateFormat(element, event.currentIndex, 'year');
      } else {
        this.dataExtraction();
      }
    }
    dateList = ['date', 'time', 'datetime', 'timestamp', 'timestamp with time zone', 'timestamp without time zone', 'timezone', 'time zone', 'timestamptz'];
    integerList = ['numeric', 'int', 'float', 'number', 'double precision', 'smallint', 'integer', 'bigint', 'decimal', 'numeric', 'real', 'smallserial', 'serial', 'bigserial', 'binary_float', 'binary_double'];
    boolList = ['bool', 'boolean'];
    stringList = ['varchar','bp char','text','varchar2','NVchar2','char','Nchar','character varying','string'];
    rowdrop(event: CdkDragDrop<string[]>){
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
    this.draggedColumns.splice(index, 1);   
    this.draggedColumnsData.splice(index, 1);
    this.dateDrillDownSwitch = false;
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
  //   (this.draggedRowsData as any[]).forEach((data,index)=>{
  //    (data as any[]).forEach((aa)=>{ 
  //      if(column === aa){
  //        console.log(aa);
  //        this.draggedRowsData.splice(index, 1);
  //      }
  //    } );
  //  });   
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
    horizentalStocked:boolean,grouped:boolean,multiLine:boolean,donut:boolean,radar:boolean,kpi:any,heatMap:any,funnel:any,guage:boolean,map:boolean,calendar:boolean,chartId:any){
    this.table = table;
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
    this.KPIDecimalPlaces = 0;
    this.KPIRoundPlaces = 0;
    this.KPIDisplayUnits = 'none';
    this.KPIPrefix = '';
    this.KPISuffix = '';
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
    this.tabs.push('Sheet ' +this.sheetNumber);
    this.SheetSavePlusEnabled.push('Sheet ' +this.sheetNumber);
    this.selectedTabIndex = this.tabs.length - 1;
    this.sheetTagName = 'Sheet ' +this.sheetNumber;
    // this.setChartType();
    this.sheetRetrive(true);
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
                const idToPass = this.fromFileId ? this.fileId : this.databaseId;
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
      this.donutDecimalPlaces = 0;
      this.decimalPlaces = 0;
      this.barColor = '#4382f7';
      this.lineColor = '#38ff98';
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
  if(this.bar && this.chartId == 6){
    console.log(this.chartOptions3);
    this.saveBar = this.chartsRowData;
    this.barXaxis = this.chartsColumnData.map((category : any)  => category === null ? 'null' : category);
    if (this.originalData) {
      this.saveBar = this.originalData.data;
      this.barXaxis = this.originalData.categories;
      this.chartOptions3.xaxis.categories = this.originalData.categories;
      this.chartOptions3.series[0].data = this.originalData.data;
      tablePreviewRow = _.cloneDeep(this.tablePreviewRow);
      tablePreviewRow[0].result_data = this.originalData.data;
      tablePreviewCol = _.cloneDeep(this.tablePreviewColumn);
      tablePreviewCol[0].result_data = this.originalData.categories;
      delete this.originalData;
    }
    if(this.isApexCharts) {
      savedChartOptions = this.chartOptions3;
      this.barOptions = this.chartOptions3;
    } else {
      savedChartOptions = this.eBarChartOptions;
    }
  }
  if(this.pie && this.chartId == 24){
    this.savePie = this.chartsRowData;
    this.pieXaxis = this.chartsColumnData.map((category : any)  => category === null ? 'null' : category);
    if(this.isApexCharts) {
      savedChartOptions = _.cloneDeep(this.chartOptions4);
      this.pieOptions = this.chartOptions4;
    } else {
      savedChartOptions = this.ePieChartOptions;
    }
    if (this.originalData) {
      this.savePie = this.originalData.data;
      this.pieXaxis = this.originalData.categories;
      savedChartOptions.labels = this.originalData.categories;
      savedChartOptions.series = this.originalData.data;
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
    if(this.isApexCharts) {
      savedChartOptions = this.chartOptions;
      this.lineOptions = this.chartOptions;
    } else {
      savedChartOptions = this.eLineChartOptions;
    }
  }
  if(this.area && this.chartId == 17){
    this.areaYaxis = this.chartsRowData;
    this.areaXaxis = this.chartsColumnData;
    if(this.isApexCharts) {
      savedChartOptions = this.chartOptions1;
      this.areaOptions = this.chartOptions1;
    } else {
      savedChartOptions = this.eAreaChartOptions;
    }
  }
  if(this.sidebyside && this.chartId == 7){
    this.sidebysideBarYaxis = this.dualAxisRowData;
    this.sidebysideBarXaxis = this.dualAxisColumnData;
    if(this.isApexCharts) {
      this.sidebysideBarOptions = this.chartOptions2;
    savedChartOptions = this.chartOptions2;
    } else {
      savedChartOptions = this.eSideBySideBarChartOptions;
    }
    
  }
  if(this.stocked && this.chartId == 5){
    this.stokedBarYaxis = this.dualAxisRowData;
    this.stokedBarXaxis = this.dualAxisColumnData;
    if(this.isApexCharts) {
      this.stokedOptions = this.chartOptions6;
    savedChartOptions = this.chartOptions6;
    } else {
      savedChartOptions = this.eStackedBarChartOptions;
    }
    
  }
  if(this.barLine && this.chartId == 4){
    this.barLineYaxis = this.dualAxisRowData;
    this.barLineXaxis = this.dualAxisColumnData;
    if(this.isApexCharts) {
      savedChartOptions = this.chartOptions5;
      this.barLineOptions = this.chartOptions5;
    } else {
      savedChartOptions = this.eBarLineChartOptions;
    }
  }
  if(this.horizentalStocked && this.chartId == 2){
    this.hStockedYaxis = this.dualAxisRowData;
    this.hStockedXaxis = this.dualAxisColumnData;
    if(this.isApexCharts) {
      this.hStockedOptions = this.chartOptions7;
    savedChartOptions = this.chartOptions7;
    } else {
      savedChartOptions = this.ehorizontalStackedBarChartOptions;
    }
    
  }
  if(this.grouped && this.chartId == 3){
    this.hgroupedYaxis = this.dualAxisRowData;
    this.hgroupedXaxis = this.dualAxisColumnData;
    if(this.isApexCharts) {
      this.hgroupedOptions = this.chartOptions8;
      savedChartOptions = this.chartOptions8;
    } else {
      savedChartOptions = this.eGroupedBarChartOptions;
    }
    
  }
  if(this.multiLine && this.chartId == 8){
    this.multiLineYaxis = this.dualAxisRowData;
    this.multiLineXaxis = this.dualAxisColumnData;
    if(this.isApexCharts) {
      this.multiLineOptions = this.chartOptions9;
    savedChartOptions = this.chartOptions9;
    } else {
      savedChartOptions = this.eMultiLineChartOptions;
    }
    
  }
  if(this.donut && this.chartId == 10){
    
    this.donutYaxis = this.chartsRowData;
    this.donutXaxis = this.chartsColumnData.map((category : any)  => category === null ? 'null' : category);
    
    if (this.originalData) {
      this.donutYaxis = this.originalData.data;
      this.donutXaxis = this.originalData.categories;
      savedChartOptions.labels = this.originalData.categories;
      savedChartOptions.series = this.originalData.data;
      tablePreviewRow = _.cloneDeep(this.tablePreviewRow);
      tablePreviewRow[0].result_data = this.originalData.data;
      tablePreviewCol = _.cloneDeep(this.tablePreviewColumn);
      tablePreviewCol[0].result_data = this.originalData.categories;
      delete this.originalData;
    }
    if(this.isApexCharts) {
      savedChartOptions = _.cloneDeep(this.chartOptions10);
      this.donutOptions = this.chartOptions10;
    } else {
      savedChartOptions = this.eDonutChartOptions;
    }
  }
  if(this.radar && this.chartId == 12){
    this.barLineXaxis = this.dualAxisColumnData;
      savedChartOptions = this.eRadarChartOptions;
  }
  if(this.kpi && this.chartId == 25){
    kpiData = this.tablePreviewRow;
    kpiColor = this.kpiColor;
    kpiFontSize = this.kpiFontSize;
  }
  if(this.heatMap && this.chartId == 26){
    if(this.isApexCharts){
    savedChartOptions = this.heatMapChartOptions;
    }else{
      savedChartOptions = this.eHeatMapChartOptions;
    }
  }
  if(this.funnel && this.chartId == 27){
    if(this.isApexCharts) {
      savedChartOptions = this.funnelChartOptions;
    } else {
      savedChartOptions = this.eFunnelChartOptions;
    }
  }
  if(this.guage && this.chartId == 28){
    savedChartOptions = this.guageChartOptions;
    // savedChartOptions['max1'] = this.maxValue
    // savedChartOptions['min1'] = this.minValue

  }
  if(this.map && this.chartId == 29){
    savedChartOptions = this.eMapChartOptions;
  }
  if(this.calendar && this.chartId == 11){
    savedChartOptions = this.eCalendarChartOptions;
  }
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
    ylabelFontWeight : this.ylabelFontWeight,
    isBold : this.isBold,
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
    funnelColor : this.funnelColor,
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

  }
  // this.sheetTagName = this.sheetTitle;
  let draggedColumnsObj;
  if (this.dateDrillDownSwitch && this.draggedColumnsData && this.draggedColumnsData.length > 0) {
    draggedColumnsObj = _.cloneDeep(this.draggedColumnsData);
    draggedColumnsObj[0][2] = 'year'
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
  "custom_query":this.sheetCustomQuery,
  "data":{
    "drillDownHierarchy":this.draggedDrillDownColumns,
    "isDrillDownData" : this.dateDrillDownSwitch,
  "columns": this.draggedColumns,
  "columns_data":draggedColumnsObj,
  "rows": this.draggedRows,
  "rows_data":this.draggedRowsData,
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
}as any;
if(this.fromFileId){
  delete obj.server_id;
  obj.file_id=this.fileId; 
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
sheetRetrive(isDuplicate : boolean){
  this.getChartData();
  console.log(this.tabs);
  const obj={
  "queryset_id":this.qrySetId,
  "server_id": this.databaseId,
}as any;
if(this.fromFileId){
  delete obj.server_id;
  obj.file_id=this.fileId;
}

this.workbechService.sheetGet(obj,this.retriveDataSheet_id).subscribe({next: (responce:any) => {
        if(isDuplicate){
          this.retriveDataSheet_id = '';
        } else {
          this.retriveDataSheet_id = responce.sheet_id;
          this.sheetName = responce.sheet_name;
          this.sheetTitle = responce.sheet_name;
          this.sheetfilter_querysets_id = responce.sheetfilter_querysets_id || responce.sheet_filter_quereyset_ids;
          if(!responce.sheet_tag_name){
            this.sheetTagName = responce.sheet_name;
          }
          else{
            this.sheetTagName = responce.sheet_tag_name;
          }
        }
        this.chartId = responce.chart_id;
        this.sheetChartId = responce.chart_id;
        this.sheetCustomQuery = responce.custom_query;
        this.sheetResponce = responce.sheet_data;
        this.draggedColumns=this.sheetResponce.columns;
        this.filterQuerySetId = responce.datasource_queryset_id;
        this.draggedRows = this.sheetResponce.rows;
        this.mulColData = responce.col_data;
        this.mulRowData = responce.row_data;
        this.tablePaginationRows=responce.row_data;
        this.tablePaginationColumn=responce.col_data;
        this.dimetionMeasure = responce.filters_data;
        this.createdBy = responce.created_by;
        this.color1 = responce.sheet_data?.results?.color1;
        this.color2 = responce.sheet_data?.results?.color2;
        this.tablePaginationCustomQuery = responce.custom_query;
        this.donutDecimalPlaces = this.sheetResponce.results.decimalplaces;
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
        responce.filters_data.forEach((filter: any)=>{
          this.filterId.push(filter.filter_id);
        })
        this.isEChatrts = this.sheetResponce.isEChart;
        this.isApexCharts = this.sheetResponce.isApexChart;
        this.dateDrillDownSwitch = this.sheetResponce.isDrillDownData;
        this.draggedDrillDownColumns = this.sheetResponce.drillDownHierarchy ? this.sheetResponce.drillDownHierarchy : [];
        if(this.isEChatrts){
          this.selectedChartPlugin = 'echart';
        } else {
          this.isApexCharts = true;
          this.selectedChartPlugin = 'apex';
        }
        this.sheetTagTitle = this.sanitizer.bypassSecurityTrustHtml(this.sheetTagName);
        // this.displayUnits = 'none';
        
        if(this.sheetResponce.columns_data){
          this.draggedColumnsData = this.sheetResponce.columns_data;
        }
        else{
          this.draggedColumns.forEach((res:any) => {
            this.draggedColumnsData.push([res.column,res.data_type,"",""])
          });
        }
        if(this.sheetResponce.rows_data){
          this.draggedRowsData = this.sheetResponce.rows_data;
        }
        else{
          this.draggedRows.forEach((res:any) => {
            this.draggedRowsData.push([res.column,res.data_type,"",res.alias ? res.alias : ""])
          });
        }
        // this.table = false;
        this.chartsDataSet(responce);
        if(responce.chart_id == 1){
          // this.tableData = this.sheetResponce.results.tableData;
          this.displayedColumns = this.sheetResponce.results.tableColumns;
          this.bandingSwitch = this.sheetResponce.results.banding;
          this.color1 = this.sheetResponce.results.color1;
          this.color2 = this.sheetResponce.results.color2;
          this.table = true;
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
        if(responce.chart_id == 25){
          this.tablePreviewRow = this.sheetResponce.results.kpiData;
          this.KPINumber = this.sheetResponce.results.kpiNumber;
          this.kpiFontSize = this.sheetResponce.results.kpiFontSize;
          this.kpiColor = this.sheetResponce.results.kpicolor;
          if(this.sheetResponce.results.kpiPrefix) {
            this.KPIPrefix = this.sheetResponce.results.kpiPrefix;
          }
          if(this.sheetResponce.results.kpiSuffix) {
            this.KPISuffix = this.sheetResponce.results.kpiSuffix;
          }
          this.KPIDisplayUnits = this.sheetResponce.results.kpiDecimalUnit,
          this.KPIDecimalPlaces = this.sheetResponce.results.kpiDecimalPlaces,
          this.table = false;
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
      
            // Initialize the chart after the map is registered
            this.eMapChartOptions = this.sheetResponce.savedChartOptions;
            this.eMapChartOptions.tooltip = {
              formatter: (params: any) => {
                const { name, data } = params;
                if (data) {
                  const keys = Object.keys(data);
                  const values = Object.values(data);
                  let formattedString = '';
                  keys.forEach((key, index) => {
                    if (key)
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
            }
          });
          this.table = false;
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
        }
       if(responce.chart_id == 6){
        // this.chartsRowData = this.sheetResponce.results.barYaxis;
        // this.chartsColumnData = this.sheetResponce.results.barXaxis;
       if(this.isApexCharts){
        const self = this;
        this.chartOptions3 = this.sheetResponce.savedChartOptions;
        this.chartOptions3.xaxis.convertedCatToNumeric = true;
        this.barchart?.updateOptions(this.chartOptions3);
        if(this.chartOptions3?.dataLabels){
          this.chartOptions3.dataLabels.formatter = this.formatNumber.bind(this);
        }
        if(this.chartOptions3.yaxis.labels){
          this.chartOptions3.yaxis.labels.formatter = this.formatNumber.bind(this);
        }
        this.chartOptions3.chart.events = {
          dataPointSelection: function (event: any, chartContext: any, config: any) {
            const selectedXValue = self.chartOptions3.xaxis.categories[config.dataPointIndex];
            if (self.drillDownIndex < self.draggedDrillDownColumns.length - 1) {
              const selectedXValue = self.chartsColumnData[config.dataPointIndex];
              console.log('X-axis value:', selectedXValue);
              let nestedKey = self.draggedDrillDownColumns[self.drillDownIndex];
              self.drillDownIndex++;
              let obj = { [nestedKey]: selectedXValue };
              self.drillDownObject.push(obj);
              self.setOriginalData();
              self.dataExtraction();
            }
          }
        };
        console.log(this.chartOptions3.xaxis.convertedCatToNumeric);
        console.log(this.chartOptions3);
       } else {
         this.eBarChartOptions = this.sheetResponce.savedChartOptions;
       }
      //  this.barChart();
        this.bar = true;
        this.table = false;
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
        if(this.isApexCharts){
          const self = this;
          this.chartOptions4 = this.sheetResponce.savedChartOptions;
          this.changeLegendsAllignment(this.chartOptions4.legend.position);
          this.chartOptions4.chart.events =  {
          dataPointSelection: function(event:any, chartContext:any, config:any) {
           if(self.drillDownIndex < self.draggedDrillDownColumns.length - 1  ){
            const selectedXValue = self.chartOptions4.labels[config.dataPointIndex];
           console.log('X-axis value:', selectedXValue);
           let nestedKey = self.draggedDrillDownColumns[self.drillDownIndex];
           self.drillDownIndex++;
           let obj = { [nestedKey] : selectedXValue};
           self.drillDownObject.push(obj);
           self.setOriginalData();
           self.dataExtraction();
           }
          }
        };
        this.legendSwitch = this.chartOptions4.legend?.show;
        this.backgroundColor = this.chartOptions4?.chart?.background;
        this.dataLabels = this.chartOptions4?.dataLabels?.enabled;
        this.changeLegendsAllignment(this.sheetResponce.savedChartOptions.legend.position);
        } else {
          this.ePieChartOptions = this.sheetResponce.savedChartOptions;
          this.legendSwitch = this.ePieChartOptions?.legend?.show;
          this.legendsAllignment = this.ePieChartOptions?.legend?.left || this.ePieChartOptions?.legend?.right || this.ePieChartOptions?.legend?.top || this.ePieChartOptions?.legend?.bottom
          this.dataLabels = this.ePieChartOptions?.label?.show
        }
        // this.pieChart();
        this.bar = false;
        this.table = false;
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
        if(this.isApexCharts){
          const self = this;
          this.chartOptions = this.sheetResponce.savedChartOptions;
          this.chartOptions.xaxis.convertedCatToNumeric = true;
          this.linechart?.updateOptions(this.chartOptions);
          if(this.chartOptions?.dataLabels){
            this.chartOptions.dataLabels.formatter = this.formatNumber.bind(this);
          }
          if(this.chartOptions.yaxis.labels){
            this.chartOptions.yaxis.labels.formatter = this.formatNumber.bind(this);
          }
          this.chartOptions.events = {
            dataPointSelection: function (event: any, chartContext: any, config: any) {
              if (self.drillDownIndex < self.draggedDrillDownColumns.length - 1) {
                const selectedXValue = self.chartsColumnData[config.dataPointIndex];
                console.log('X-axis value:', selectedXValue);
                let nestedKey = self.draggedDrillDownColumns[self.drillDownIndex];
                self.drillDownIndex++;
                let obj = { [nestedKey]: selectedXValue };
                self.drillDownObject.push(obj);
                self.setOriginalData();
                self.callDrillDown();
              }
            }
          }
        } else {
          this.eLineChartOptions = this.sheetResponce.savedChartOptions;
        }
        // this.lineChart();
        this.bar = false;
        this.table = false;
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
        if(this.isApexCharts){
          this.chartOptions1 = this.sheetResponce.savedChartOptions;
          this.chartOptions1.xaxis.convertedCatToNumeric = true;
          this.areachart?.updateOptions(this.chartOptions1);
          if(this.chartOptions1?.dataLabels){
            this.chartOptions1.dataLabels.formatter = this.formatNumber.bind(this);
          }
          if(this.chartOptions1.yaxis.labels){
            this.chartOptions1.yaxis.labels.formatter = this.formatNumber.bind(this);
          }
        } else {
          this.eAreaChartOptions = this.sheetResponce.savedChartOptions;
        }
        // this.areaChart();
        this.bar = false;
        this.table = false;
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
        if(this.isApexCharts){
        this.chartOptions2 = this.sheetResponce.savedChartOptions;
        if(this.chartOptions2?.dataLabels){
          this.chartOptions2.dataLabels.formatter = this.formatNumber.bind(this);
        }
        if(this.chartOptions2.yaxis.labels){
          this.chartOptions2.yaxis.labels.formatter = this.formatNumber.bind(this);
        }
        } else {
          this.eSideBySideBarChartOptions = this.sheetResponce.savedChartOptions;
        }
        // this.sidebysideBar();
        this.bar = false;
        this.table = false;
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
        if(this.isApexCharts){
        this.chartOptions6 = this.sheetResponce.savedChartOptions;
        if(this.chartOptions6?.dataLabels){
          this.chartOptions6.dataLabels.formatter = this.formatNumber.bind(this);
        }
        if(this.chartOptions6.yaxis.labels){
          this.chartOptions6.yaxis.labels.formatter = this.formatNumber.bind(this);
        }
        } else {
          this.eStackedBarChartOptions = this.sheetResponce.savedChartOptions;
        }
        // this.stockedBar();
        this.bar = false;
        this.table = false;
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
        if(this.isApexCharts){
          this.chartOptions5 = this.sheetResponce.savedChartOptions;
          this.chartOptions5.dataLabels.formatter = this.formatNumber.bind(this);
          if(this.chartOptions5?.dataLabels){
            this.chartOptions5.dataLabels.formatter = this.formatNumber.bind(this);
          }
          if(this.chartOptions5.yaxis.labels){
            this.chartOptions5.yaxis[0].labels.formatter = this.formatNumber.bind(this);
            this.chartOptions5.yaxis[1].labels.formatter = this.formatNumber.bind(this);
          }
        
        } else {
          this.eBarLineChartOptions = this.sheetResponce.savedChartOptions;
        }
        // this.barLineChart();
        this.bar = false;
        this.table = false;
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
        this.dualAxisColumnData = this.sheetResponce.results.barLineXaxis;
        this.radarChart();
        this.bar = false;
        this.table = false;
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
          if(this.isApexCharts){
          
          } else {
            this.eRadarChartOptions = this.sheetResponce.savedChartOptions;
          }
       }
       if(responce.chart_id == 2){
        if(this.isApexCharts){
        this.chartOptions7 = this.sheetResponce.savedChartOptions;
        if(this.chartOptions7?.dataLabels){
          this.chartOptions7.dataLabels.formatter = this.formatNumber.bind(this);
        }
        if(this.chartOptions7.xaxis.labels){
          this.chartOptions7.xaxis.labels.formatter = this.formatNumber.bind(this);
        }
        } else {
          this.ehorizontalStackedBarChartOptions = this.sheetResponce.savedChartOptions;
        }
        // this.horizentalStockedBar();
        this.bar = false;
        this.table = false;
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
        if(this.isApexCharts){
        this.chartOptions8 = this.sheetResponce.savedChartOptions;
        if(this.chartOptions8?.dataLabels){
          this.chartOptions8.dataLabels.formatter = this.formatNumber.bind(this);
        }
        if(this.chartOptions8.xaxis.labels){
          this.chartOptions8.xaxis.labels.formatter = this.formatNumber.bind(this);
        }
        } else {
          this.eGroupedBarChartOptions = this.sheetResponce.savedChartOptions;
        }
        // this.hGrouped();
        this.bar = false;
        this.table = false;
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
        if(this.isApexCharts){
        this.chartOptions9 = this.sheetResponce.savedChartOptions;
        if(this.chartOptions9?.dataLabels){
          this.chartOptions9.dataLabels.formatter = this.formatNumber.bind(this);
        }
        if(this.chartOptions9.yaxis.labels){
          this.chartOptions9.yaxis.labels.formatter = this.formatNumber.bind(this);
        }
        } else {
          this.eMultiLineChartOptions = this.sheetResponce.savedChartOptions;
        }
        // this.multiLineChart();
        this.bar = false;
        this.table = false;
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
        if(this.isApexCharts){
        this.chartOptions10 = this.sheetResponce.savedChartOptions;
        this.legendSwitch = this.chartOptions10?.legend?.show;
        this.changeLegendsAllignment(this.chartOptions10?.legend?.position);
        this.dataLabels = this.chartOptions10?.dataLabels?.enabled;
        this.label = this.chartOptions10?.plotOptions?.pie?.donut?.labels?.show;
        this.donutSize = parseInt(this.chartOptions10?.plotOptions?.pie?.donut?.size?.replace('%', '').trim());
        this.chartOptions10.plotOptions.pie.donut.labels.total.formatter = (w:any) => {
          return w.globals.seriesTotals.reduce((a:any, b:any) => {
            return +a + b
          }, 0).toFixed(this.donutDecimalPlaces);
        };
        const self = this;
        this.chartOptions10.chart.events = {
          dataPointSelection: function (event: any, chartContext: any, config: any) {
            if (self.drillDownIndex < self.draggedDrillDownColumns.length - 1) {
              const selectedXValue = self.chartOptions10.labels[config.dataPointIndex];
              console.log('X-axis value:', selectedXValue);
              let nestedKey = self.draggedDrillDownColumns[self.drillDownIndex];
              self.drillDownIndex++;
              let obj = { [nestedKey]: selectedXValue };
              self.drillDownObject.push(obj);
              self.setOriginalData();
              self.callDrillDown();
            }
          }
        }
      }
        else {
          this.eDonutChartOptions = this.sheetResponce.savedChartOptions;
          this.legendSwitch = this.eDonutChartOptions?.legend?.show;
          this.legendsAllignment = this.eDonutChartOptions?.legend?.left || this.eDonutChartOptions?.legend?.right || this.eDonutChartOptions?.legend?.top || this.eDonutChartOptions?.legend?.bottom
          this.dataLabels = this.eDonutChartOptions?.label?.show;
          this.donutSize = parseInt(this.eDonutChartOptions?.series[0]?.radius[0]?.replace('%', '').trim());

        }
        // this.donutChart();
        this.bar = false;
        this.table = false;
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
        if(this.isApexCharts){
          this.heatMapChartOptions = this.sheetResponce.savedChartOptions;
          if(this.heatMapChartOptions?.dataLabels){
            this.heatMapChartOptions.dataLabels.formatter = this.formatNumber.bind(this);
          }
        } else {
          this.eHeatMapChartOptions = this.sheetResponce.savedChartOptions;
        }

        this.bar = false;
        this.table = false;
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
         if(this.isEChatrts){
          this.eFunnelChartOptions = this.sheetResponce.savedChartOptions;
         } else {
        this.funnelChartOptions = this.sheetResponce.savedChartOptions;
        if(this.funnelChartOptions?.dataLabels){
          this.funnelChartOptions.dataLabels.formatter = (val: any, opts: any) => {
            const category = opts.w.config.xaxis.categories[opts.dataPointIndex];
            const formattedValue = this.formatNumber(val);
            return `${category}: ${formattedValue}`;
        }
        }
        this.isDistributed = this.funnelChartOptions?.plotOptions?.bar?.distributed;
        this.funnelDLAllign = this.funnelChartOptions?.plotOptions?.bar?.dataLabels?.position;
        this.funnelDLFontFamily = this.funnelChartOptions?.dataLabels?.style?.fontFamily;
        this.funnelDLFontSize = this.funnelChartOptions?.dataLabels?.style?.fontSize;
        // this.funnelColor = this.funnelChartOptions?.series[0]?.color;
      }
        this.bar = false;
        this.table = false;
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
        this.guageChartOptions = this.sheetResponce.savedChartOptions;
        this.maxValueGuage = this.guageChartOptions.plotOptions.radialBar.max;
        this.minValueGuage =  this.guageChartOptions.plotOptions.radialBar.min;
        this.bar = false;
        this.table = false;
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
        this.eCalendarChartOptions = this.sheetResponce.savedChartOptions;
        this.eCalendarChartOptions.tooltip.formatter =  function (params: any) {
          const date = params.data[0];
          const value = params.data[1];
          return `Date: ${date}<br/>Value: ${value}`;
      }
        this.bar = false;
        this.table = false;
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
        setTimeout(()=>{
          this.updateNumberFormat();
        }, 1000);
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
  filterDataGet(){
    const obj={
      "database_id" :this.databaseId,
      "query_set_id":this.qrySetId,
      "type_of_filter" : "sheet",
      "datasource_queryset_id" :this.filterQuerySetId,
      "col_name":this.filterName,
       "data_type":this.filterType,
       "search":this.filterSearch,
       "parent_user":this.createdBy,
       "field_logic" : this.filterCalculatedFieldLogic?.length > 0 ? this.filterCalculatedFieldLogic : null,
       "is_calculated": this.filterType == 'calculated' ? true : false
      // "format_date":""
}as any;
if(this.fromFileId){
  delete obj.database_id;
  obj.file_id=this.fileId;
}
  this.workbechService.filterPost(obj).subscribe({next: (responce:any) => {
        console.log(responce);
        const convertedArray = responce.col_data.map((item: any) => ({ label: item, selected: false }));
        this.filterData = convertedArray;

        if(this.dateList.includes(responce.dtype)){
          this.floor = new Date(this.filterData[0].label).getTime();
          this.ceil = new Date(this.filterData[this.filterData.length - 1].label).getTime();
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
  filterDataPut(){
    // this.dimetionMeasure = [];
    this.sortedData = [];
    const obj={
    //"filter_id": this.filter_id,
    "database_id": this.databaseId,
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
       "is_calculated": this.filterType == 'calculated' ? true : false
}as any;
if(this.fromFileId){
  delete obj.database_id;
  obj.file_id=this.fileId;
}
  this.workbechService.filterPut(obj).subscribe({next: (responce:any) => {
        console.log(responce);
        this.filterId.push(responce.filter_id);
        this.filter_id=responce.filter_id
        this.dimetionMeasure.push({"col_name":this.filterName,"data_type":this.filterType,"filter_id":responce.filter_id});
        this.dataExtraction();
        this.filterDataArray = [];
        this.filterDateRange = [];
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
      "database_id" :this.databaseId,
      "filter_id" :this.filter_id,
      "search":this.editFilterSearch
}as any;
if(this.fromFileId){
  delete obj.database_id;
  obj.file_id=this.fileId;
}
  this.workbechService.filterEditPost(obj).subscribe({next: (responce:any) => {
        console.log(responce);
        this.filter_id = responce.filter_id;
        this.filterName=responce.column_name;
        this.filterType=responce.data_type;
        this.filterCalculatedFieldLogic = responce.field_logic;
        this.isExclude = responce.is_exclude;
        responce.result.forEach((element:any) => {
          this.filterData.push(element);
        });
        this.filterData.forEach((filter:any)=>{
          if(filter.selected){
            this.filterDataArray.push(filter.label);
          }
        })
        if(this.dateList.includes(responce.dtype)){
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
      "database_id": this.databaseId,
      "queryset_id": this.qrySetId,
      "type_of_filter":"sheet",
      "datasource_querysetid" : this.filterQuerySetId,
      "range_values": this.filterDateRange,
      "select_values":this.filterDataArray,
      "col_name":this.filterName,
      "data_type":this.filterType,
      "is_exclude":this.isExclude,
      "field_logic" : this.filterCalculatedFieldLogic?.length > 0 ? this.filterCalculatedFieldLogic : null,
      "is_calculated": this.filterType == 'calculated' ? true : false

  }as any;
  if(this.fromFileId){
    delete obj.database_id;
    obj.file_id=this.fileId;
  }
    this.workbechService.filterPut(obj).subscribe({next: (responce:any) => {
          console.log(responce);
          this.dataExtraction();
          this.filterDataArray = [];
          this.filterDateRange = [];
          this.isAllSelected = false;
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
editFilterCheck(data:any){
  if(this.dimetionMeasure.length>0){
    this.dimetionMeasure.forEach((column:any)=>{
      if(column.col_name === data){
        this.filterAdded = true;
      }
      else{
        this.filterAdded = false;
      }
    })
  }
  else{
    this.filterAdded = false;
  }
}
gotoDashboard(){
  if(!this.fromFileId){
  const encodedDatabaseId = btoa(this.databaseId.toString());
  const encodedQuerySetId = btoa(this.qrySetId.toString());
  this.router.navigate(['/insights/sheetscomponent/sheetsdashboard/dbId'+'/'+ encodedDatabaseId +'/' +encodedQuerySetId])
  }
if(this.fromFileId){
  const encodedFileId = btoa(this.fileId.toString())
  const encodedQuerySetId = btoa(this.qrySetId.toString());
  this.router.navigate(['/insights/sheetscomponent/sheetsdashboard/fileId'+'/'+ encodedFileId +'/' +encodedQuerySetId])
}
}
viewDashboard(){
  if(this.fromFileId){
    const encodedDatabaseId = btoa(this.fileId.toString());
    const encodedQuerySetId = btoa(this.qrySetId.toString());
    const encodedDashboardId = btoa(this.dashboardId.toString());
    this.router.navigate(['insights/home/sheetsdashboard'+'/'+ encodedDatabaseId +'/' +encodedQuerySetId +'/' + encodedDashboardId])

  } else {
  const encodedDatabaseId = btoa(this.databaseId.toString());
  const encodedQuerySetId = btoa(this.qrySetId.toString());
  const encodedDashboardId = btoa(this.dashboardId.toString());
  this.router.navigate(['insights/home/sheetsdashboard'+'/'+ encodedDatabaseId +'/' +encodedQuerySetId +'/' + encodedDashboardId])
  }

}

marksColor2(color:any){
console.log(this.dualAxisRowData);
console.log(color)
let object : any;
if(this.bar){
  if(this,this.isApexCharts){
  this.chartOptions3.colors = color;
  object = {colors: [color]};
  }else{
  this.eBarChartOptions.color = color

 }
}
else if(this.area){
  if(this.isApexCharts){
  this.chartOptions1.colors = color;
  object = {colors: [color]};
  }else{
    this.eAreaChartOptions.color = color
  }
}
else if(this.line){
  if(this.isApexCharts){
  this.chartOptions.colors = color;
  object = {colors: [color]};
  }else{
    this.eLineChartOptions.color = color
  }
}
else if(this.sidebyside){
  if(this.dualAxisRowData){
  }
  if(this.isApexCharts){
  this.chartOptions2.colors = color;
  object = {colors: [color]};
  }else{
  this.eSideBySideBarChartOptions.color = color
  }
}
else if(this.stocked){
  if(this.isApexCharts){
  this.chartOptions6.colors = color;
  object = {colors: [color]};
  }else{
    this.eStackedBarChartOptions.color = color
  }
}
else if(this.barLine){
  if(this.isApexCharts){
  this.chartOptions5.series[0].color = this.barColor;
  this.chartOptions5.series[1].color = this.lineColor;
  object = {colors: [this.barColor, this.lineColor]};
  }else{
    this.eBarLineChartOptions.series[0].itemStyle.color = this.barColor;
    this.eBarLineChartOptions.series[1].lineStyle.color = this.lineColor;

  }
}
else if(this.horizentalStocked){
  if(this.isApexCharts){
  this.chartOptions7.colors = color;
  object = {colors: [color]};
  }else{
    this.ehorizontalStackedBarChartOptions.color = color
  }
}
else if(this.grouped){
  if(this.isApexCharts){
  this.chartOptions8.colors = color;
  object = {colors: [color]};
  }else{
    this.eGroupedBarChartOptions.color = color
  }
}
else if(this.multilineChart){
  if(this.isApexCharts){
  this.chartOptions9.colors = color;
  object = {colors: [color]};
  }else{
    this.eMultiLineChartOptions.color = color;
  }
}
else if(this.funnel){
  // this.funnelChartOptions.colors = color;
  // object = {colors: [color]};
  if(this.isApexCharts){
  this.funnelChartOptions.series[0].color = color;
  object = {series: this.dualAxisRowData}
  object = object.series[0].color = color;
  }else{
    this.eFunnelChartOptions.color = color;
  }
}
else if(this.guage){
  this.guageChartOptions.colors = color;
  object = {colors: [color]};
}
else if(this.radar){
  this.eRadarChartOptions.color = color;
}
if(this.isApexCharts){
this.updateChart(object);
}else{
  this.updateEchartOptions();
}
}
// scolor : any;
// barColors(color:any, index: any){
//   if(index === 0){
//     this.chartOptions2.series[0].color = color;
//   }
//   if(index === 1){
//     this.chartOptions2.series[1].color = color;
//   }
//   if(index === 2){
//     this.chartOptions2.series[2].color = color;
//   }
//   this.updateChart();
// }
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
      if (event === 'center') {
        object = {xaxis: {labels : {offsetX : 0}, categories: this.chartsColumnData}};
        if(this.bar){
          if(this.isApexCharts){
          this.chartOptions3.xaxis.labels.offsetX = 0;
          }else{
            this.xlabelAlignment = 'Middle'
            this.eBarChartOptions.xAxis.nameLocation = 'Middle';
          }
        }
        else if(this.areachart){
          this.chartOptions1.xaxis.labels.offsetX = 0;
        }
        else if(this.linechart){
          this.chartOptions.xaxis.labels.offsetX = 0;
        }
        else if(this.sidebysideChart){
          this.chartOptions2.xaxis.labels.offsetX = 0;
        }
        else if(this.stockedChart){
          this.chartOptions6.xaxis.labels.offsetX = 0;
        }
        else if(this.barlineChart){
          this.chartOptions5.xaxis.labels.offsetX = 0;
        }
        else if(this.horizontolstockedChart){
          this.chartOptions7.xaxis.labels.offsetX = 0;
        }
        else if(this.groupedChart){
          this.chartOptions8.xaxis.labels.offsetX = 0;
        }
        else if(this.multilineChart){
          this.chartOptions9.xaxis.labels.offsetX = 0;
        }
        else if(this.heatMap){
          this.heatMapChartOptions.xaxis.labels.offsetX = 0;
        }

      }
      if (event === 'left') {
        object = {xaxis: {labels : {offsetX : -10}, categories: this.chartsColumnData}};
        if(this.bar){
          if(this.isApexCharts){
          this.chartOptions3.xaxis.labels.offsetX = -10;
          }else{
            this.xlabelAlignment = 'End'
            this.eBarChartOptions.xAxis.nameLocation = 'End';
          }
        }
        else if(this.areachart){
          this.chartOptions1.xaxis.labels.offsetX = -10;
        }
        else if(this.linechart){
          this.chartOptions.xaxis.labels.offsetX = -10;
        }
        else if(this.sidebysideChart){
          this.chartOptions2.xaxis.labels.offsetX = -10;
        }
        else if(this.stockedChart){
          this.chartOptions6.xaxis.labels.offsetX = -10;
        }
        else if(this.barlineChart){
          this.chartOptions5.xaxis.labels.offsetX = -10;
        }
        else if(this.horizontolstockedChart){
          this.chartOptions7.xaxis.labels.offsetX = -10;
        }
        else if(this.groupedChart){
          this.chartOptions8.xaxis.labels.offsetX = -10;
        }
        else if(this.multilineChart){
          this.chartOptions9.xaxis.labels.offsetX = -10;
        }
        else if(this.heatMap){
          this.heatMapChartOptions.xaxis.labels.offsetX = -10;
        }
      }
      if (event === 'right') {
        object = {xaxis: {labels : {offsetX : 10}, categories: this.chartsColumnData}};
        if(this.bar){
          if(this.isApexCharts){
          this.chartOptions3.xaxis.labels.offsetX = 10;
          }else{
            this.xlabelAlignment = 'Start'
            this.eBarChartOptions.xAxis.nameLocation = 'Start';
          }
        }
        else if(this.areachart){
          this.chartOptions1.xaxis.labels.offsetX = 10;
        }
        else if(this.linechart){
          this.chartOptions.xaxis.labels.offsetX = 10;
        }
        else if(this.sidebysideChart){
          this.chartOptions2.xaxis.labels.offsetX = 10;
        }
        else if(this.stockedChart){
          this.chartOptions6.xaxis.labels.offsetX = 10;
        }
        else if(this.barlineChart){
          this.chartOptions5.xaxis.labels.offsetX = 10;
        }
        else if(this.horizontolstockedChart){
          this.chartOptions7.xaxis.labels.offsetX = 10;
        }
        else if(this.groupedChart){
          this.chartOptions8.xaxis.labels.offsetX = 10;
        }
        else if(this.multilineChart){
          this.chartOptions9.xaxis.labels.offsetX = 10;
        }
        else if(this.heatMap){
          this.heatMapChartOptions.xaxis.labels.offsetX = 10;
        }
      }
    }
    else {
      this.measureAlignment = event;
      if (event === 'center') {
        object = {yaxis: {labels : {show: this.yLabelSwitch, offsetY : 0, style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }, formatter: this.formatNumber.bind(this)}}};
        if(this.barchart){
          if (this.chartOptions3.yaxis.length > 0) {
            (this.chartOptions3.yaxis as any[]).forEach((data) => {
              data.labels.offsetY = 0;
            })
          }
          else {
            this.chartOptions3.yaxis.labels.offsetY = 0;
          }
        }
        else if(this.areachart){
          if (this.chartOptions1.yaxis.length > 0) {
            (this.chartOptions1.yaxis as any[]).forEach((data) => {
              data.labels.offsetY = 0;
            })
          }
          else {
            this.chartOptions1.yaxis.labels.offsetY = 0;
          }
        }
        else if(this.linechart){
          if (this.chartOptions.yaxis.length > 0) {
            (this.chartOptions.yaxis as any[]).forEach((data) => {
              data.labels.offsetY = 0;
            })
          }
          else {
            this.chartOptions.yaxis.labels.offsetY = 0;
          }
        }
        else if(this.sidebysideChart){
          if (this.chartOptions2.yaxis.length > 0) {
            (this.chartOptions2.yaxis as any[]).forEach((data) => {
              data.labels.offsetY = 0;
            })
          }
          else {
            this.chartOptions2.yaxis.labels.offsetY = 0;
          }
        }
        else if(this.stockedChart){
          if (this.chartOptions6.yaxis.length > 0) {
            (this.chartOptions6.yaxis as any[]).forEach((data) => {
              data.labels.offsetY = 0;
            })
          }
          else {
            this.chartOptions6.yaxis.labels.offsetY = 0;
          }
        }
        else if(this.barlineChart){
          object = {yaxis: 
            [
              {show: true,labels : {show: this.yLabelSwitch, offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }, formatter: this.formatNumber.bind(this)}},
              {show: true,opposite: true,labels : {show: this.yLabelSwitch, offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }, formatter: this.formatNumber.bind(this)}}
            ]
          };
          if (this.chartOptions5.yaxis.length > 0) {
            (this.chartOptions5.yaxis as any[]).forEach((data) => {
              data.labels.offsetY = 0;
            })
          }
          else {
            this.chartOptions5.yaxis.labels.offsetY = 0;
          }
        }
        else if(this.horizontolstockedChart){
          object = {yaxis: {labels : {show: this.yLabelSwitch, offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }}}};
          if (this.chartOptions7.yaxis.length > 0) {
            (this.chartOptions7.yaxis as any[]).forEach((data) => {
              data.labels.offsetY = 0;
            })
          }
          else {
            this.chartOptions7.yaxis.labels.offsetY = 0;
          }
        }
        else if(this.groupedChart){
          object = {yaxis: {labels : {show: this.yLabelSwitch, offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }}}};
          if (this.chartOptions8.yaxis.length > 0) {
            (this.chartOptions8.yaxis as any[]).forEach((data) => {
              data.labels.offsetY = 0;
            })
          }
          else {
            this.chartOptions8.yaxis.labels.offsetY = 0;
          }
        }
        else if(this.multilineChart){
          if (this.chartOptions9.yaxis.length > 0) {
            (this.chartOptions9.yaxis as any[]).forEach((data) => {
              data.labels.offsetY = 0;
            })
          }
          else {
            this.chartOptions9.yaxis.labels.offsetY = 0;
          }
        }
        else if(this.heatMap){
          if (this.heatMapChartOptions.yaxis.length > 0) {
            (this.heatMapChartOptions.yaxis as any[]).forEach((data) => {
              data.labels.offsetY = 0;
            })
          }
          else {
            this.heatMapChartOptions.yaxis.labels.offsetY = 0;
          }
        }
      }
      if (event === 'top') {
        object = {yaxis: {labels : {show: this.yLabelSwitch, offsetY : -10, style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }, formatter: this.formatNumber.bind(this)}}};
        if(this.barchart){
          if (this.chartOptions3.yaxis.length > 0) {
            (this.chartOptions3.yaxis as any[]).forEach((data) => {
              data.labels.offsetY = -10;
            })
          }
          else {
            this.chartOptions3.yaxis.labels.offsetY = -10;
          }
        }
        else if(this.areachart){
          if (this.chartOptions1.yaxis.length > 0) {
            (this.chartOptions1.yaxis as any[]).forEach((data) => {
              data.labels.offsetY = -10;
            })
          }
          else {
            this.chartOptions1.yaxis.labels.offsetY = -10;
          }
        }
        else if(this.linechart){
          if (this.chartOptions.yaxis.length > 0) {
            (this.chartOptions.yaxis as any[]).forEach((data) => {
              data.labels.offsetY = -10;
            })
          }
          else {
            this.chartOptions.yaxis.labels.offsetY = -10;
          }
        }
        else if(this.sidebysideChart){
          if (this.chartOptions2.yaxis.length > 0) {
            (this.chartOptions2.yaxis as any[]).forEach((data) => {
              data.labels.offsetY = -10;
            })
          }
          else {
            this.chartOptions2.yaxis.labels.offsetY = -10;
          }
        }
        else if(this.stockedChart){
          if (this.chartOptions6.yaxis.length > 0) {
            (this.chartOptions6.yaxis as any[]).forEach((data) => {
              data.labels.offsetY = -10;
            })
          }
          else {
            this.chartOptions6.yaxis.labels.offsetY = -10;
          }
        }
        else if(this.barlineChart){
          object = {yaxis: 
            [
              {show: true,labels : {show: this.yLabelSwitch, offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }, formatter: this.formatNumber.bind(this)}},
              {show: true,opposite: true,labels : {show: this.yLabelSwitch, offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }, formatter: this.formatNumber.bind(this)}}
            ]
          };
          if (this.chartOptions5.yaxis.length > 0) {
            (this.chartOptions5.yaxis as any[]).forEach((data) => {
              data.labels.offsetY = -10;
            })
          }
          else {
            this.chartOptions5.yaxis.labels.offsetY = -10;
          }
        }
        else if(this.horizontolstockedChart){
          object = {yaxis: {labels : {show: this.yLabelSwitch, offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }}}};
          if (this.chartOptions7.yaxis.length > 0) {
            (this.chartOptions7.yaxis as any[]).forEach((data) => {
              data.labels.offsetY = -10;
            })
          }
          else {
            this.chartOptions7.yaxis.labels.offsetY = -10;
          }
        }
        else if(this.groupedChart){
          object = {yaxis: {labels : {show: this.yLabelSwitch, offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }}}};
          if (this.chartOptions8.yaxis.length > 0) {
            (this.chartOptions8.yaxis as any[]).forEach((data) => {
              data.labels.offsetY = -10;
            })
          }
          else {
            this.chartOptions8.yaxis.labels.offsetY = -10;
          }
        }
        else if(this.multilineChart){
          if (this.chartOptions9.yaxis.length > 0) {
            (this.chartOptions9.yaxis as any[]).forEach((data) => {
              data.labels.offsetY = -10;
            })
          }
          else {
            this.chartOptions9.yaxis.labels.offsetY = -10;
          }
        }
        else if(this.heatMap){
          if (this.heatMapChartOptions.yaxis.length > 0) {
            (this.heatMapChartOptions.yaxis as any[]).forEach((data) => {
              data.labels.offsetY = -10;
            })
          }
          else {
            this.heatMapChartOptions.yaxis.labels.offsetY = -10;
          }
        }
      }
      if (event === 'bottom') {
        object = {yaxis: {labels : {show: this.yLabelSwitch, offsetY : 10, style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }, formatter: this.formatNumber.bind(this)}}};
        if(this.barchart){
          if (this.chartOptions3.yaxis.length > 0) {
            (this.chartOptions3.yaxis as any[]).forEach((data) => {
              data.labels.offsetY = 10;
            })
          }
          else {
            this.chartOptions3.yaxis.labels.offsetY = 10;
          }
        }
        else if(this.areachart){
          if (this.chartOptions1.yaxis.length > 0) {
            (this.chartOptions1.yaxis as any[]).forEach((data) => {
              data.labels.offsetY = 10;
            })
          }
          else {
            this.chartOptions1.yaxis.labels.offsetY = 10;
          }
        }
        else if(this.linechart){
          if (this.chartOptions.yaxis.length > 0) {
            (this.chartOptions.yaxis as any[]).forEach((data) => {
              data.labels.offsetY = 10;
            })
          }
          else {
            this.chartOptions.yaxis.labels.offsetY = 10;
          }
        }
        else if(this.sidebysideChart){
          if (this.chartOptions2.yaxis.length > 0) {
            (this.chartOptions2.yaxis as any[]).forEach((data) => {
              data.labels.offsetY = 10;
            })
          }
          else {
            this.chartOptions2.yaxis.labels.offsetY = 10;
          }
        }
        else if(this.stockedChart){
          if (this.chartOptions6.yaxis.length > 0) {
            (this.chartOptions6.yaxis as any[]).forEach((data) => {
              data.labels.offsetY = 10;
            })
          }
          else {
            this.chartOptions6.yaxis.labels.offsetY = 10;
          }
        }
        else if(this.barlineChart){
          object = {yaxis: 
            [
              {show: true,labels : {show: this.yLabelSwitch, offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }, formatter: this.formatNumber.bind(this)}},
              {show: true,opposite: true,labels : {show: this.yLabelSwitch, offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }, formatter: this.formatNumber.bind(this)}}
            ]
          };
          if (this.chartOptions5.yaxis.length > 0) {
            (this.chartOptions5.yaxis as any[]).forEach((data) => {
              data.labels.offsetY = 10;
            })
          }
          else {
            this.chartOptions5.yaxis.labels.offsetY = 10;
          }
        }
        else if(this.horizontolstockedChart){
          object = {yaxis: {labels : {show: this.yLabelSwitch, offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }}}};
          if (this.chartOptions7.yaxis.length > 0) {
            (this.chartOptions7.yaxis as any[]).forEach((data) => {
              data.labels.offsetY = 10;
            })
          }
          else {
            this.chartOptions7.yaxis.labels.offsetY = 10;
          }
        }
        else if(this.groupedChart){
          object = {yaxis: {labels : {show: this.yLabelSwitch, offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }}}};
          if (this.chartOptions8.yaxis.length > 0) {
            (this.chartOptions8.yaxis as any[]).forEach((data) => {
              data.labels.offsetY = 10;
            })
          }
          else {
            this.chartOptions8.yaxis.labels.offsetY = 10;
          }
        }
        else if(this.multilineChart){
          if (this.chartOptions9.yaxis.length > 0) {
            (this.chartOptions9.yaxis as any[]).forEach((data) => {
              data.labels.offsetY = 10;
            })
          }
          else {
            this.chartOptions9.yaxis.labels.offsetY = 10;
          }
        }
        else if(this.heatMap){
          if (this.heatMapChartOptions.yaxis.length > 0) {
            (this.heatMapChartOptions.yaxis as any[]).forEach((data) => {
              data.labels.offsetY = 10;
            })
          }
          else {
            this.heatMapChartOptions.yaxis.labels.offsetY = 10;
          }
        }
      }
    }
    if(this.isApexCharts){
    this.updateChart(object);
    }else{
      this.updateEchartOptions();
    }
  }
  updateChart(object : any) {
    if (this.barchart) {
      this.barchart.updateOptions(object);
      console.log(this.chartOptions3);
      console.log(this.barchart);
    }
    else if(this.areachart){
      this.areachart.updateOptions(object);
      console.log(this.chartOptions1);
      console.log(this.areachart);
    }
    else if(this.linechart){
      this.linechart.updateOptions(object);
      console.log(this.chartOptions);
      console.log(this.linechart);
    }
    else if(this.sidebysideChart){
      this.sidebysideChart.updateOptions(object);
      console.log(this.chartOptions2);
      console.log(this.sidebysideChart);
    }
    else if(this.stockedChart){
      this.stockedChart.updateOptions(object);
      console.log(this.chartOptions6);
      console.log(this.stockedChart);
    }
    else if(this.barlineChart){
      this.barlineChart.updateOptions(object);
      console.log(this.chartOptions5);
      console.log(this.barlineChart);
    }
    else if(this.horizontolstockedChart){
      this.horizontolstockedChart.updateOptions(object);
      console.log(this.chartOptions7);
      console.log(this.horizontolstockedChart);
    }
    else if(this.groupedChart){
      this.groupedChart.updateOptions(object);
      console.log(this.chartOptions8);
      console.log(this.groupedChart);
    }
    else if(this.multilineChart){
      this.multilineChart.updateOptions(object);
      console.log(this.chartOptions9);
      console.log(this.multilineChart);
    }
    else if(this.piechart){
      this.piechart.updateOptions(object);
      console.log(this.chartOptions4);
      console.log(this.piechart);
    }
    else if(this.donutchart){
      this.donutchart.updateOptions(object);
      console.log(this.chartOptions10);
      console.log(this.donutchart);
    }
    else if(this.funnel){
      this.funnelCharts.updateOptions(object);
      console.log(this.funnelChartOptions);
      console.log(this.funnelCharts);
    }
    else if(this.guage){
      this.guageCharts.updateOptions(object);
      console.log(this.guageCharts);
    }
    else if(this.heatMap){
      this.heatmapcharts.updateOptions(object);
      console.log(this.heatMapChartOptions);
      console.log(this.heatmapcharts);
    }
  }

  updateEchartOptions(){
    const chartElement = document.getElementsByClassName('echart-charts')[0] as HTMLElement;
    if (this.bar) {
      echarts.init(chartElement).setOption(this.eBarChartOptions);
      console.log('barchartoptionsafterupdate', this.eBarChartOptions)
    }
    if (this.area) {
      echarts.init(chartElement).setOption(this.eAreaChartOptions);
      console.log('areachart optionsafterupdate', this.eAreaChartOptions)
    }
    if (this.line) {
      echarts.init(chartElement).setOption(this.eLineChartOptions);
      console.log('linechart optionsafterupdate', this.eLineChartOptions)
    }
    if (this.sidebyside) {
      echarts.init(chartElement).setOption(this.eSideBySideBarChartOptions);
      console.log('eSideBySideBarChartOptions afterupdate', this.eSideBySideBarChartOptions)
    }
    if (this.stocked) {
      echarts.init(chartElement).setOption(this.eStackedBarChartOptions);
      console.log('eStackedBarChartOptions afterupdate', this.eStackedBarChartOptions)
    }
    if (this.radar) {
      echarts.init(chartElement).setOption(this.eRadarChartOptions);
      console.log('eRadarChartOptions optionsafterupdate', this.eRadarChartOptions)
    }
    if (this.heatMap) {
      echarts.init(chartElement).setOption(this.eHeatMapChartOptions);
      console.log('eHeatMapChartOptions optionsafterupdate', this.eHeatMapChartOptions)
    }
    if (this.pie) {
      echarts.init(chartElement).setOption(this.ePieChartOptions);
      console.log('ePieChartOptions optionsafterupdate', this.ePieChartOptions)
    }
    if (this.donut) {
      echarts.init(chartElement).setOption(this.eDonutChartOptions);
      console.log('eDonutChartOptions optionsafterupdate', this.eDonutChartOptions)
    }
    if (this.grouped) {
      echarts.init(chartElement).setOption(this.eGroupedBarChartOptions);
      console.log('eGroupedBarChartOptions optionsafterupdate', this.eGroupedBarChartOptions)
    }
    if (this.multiLine) {
      echarts.init(chartElement).setOption(this.eMultiLineChartOptions);
      console.log('eMultiLineChartOptions optionsafterupdate', this.eMultiLineChartOptions)
    }
    if (this.barLine) {
      echarts.init(chartElement).setOption(this.eBarLineChartOptions);
      console.log('eBarLineChartOptions optionsafterupdate', this.eBarLineChartOptions)
    }
    if (this.horizentalStocked) {
      echarts.init(chartElement).setOption(this.ehorizontalStackedBarChartOptions);
      console.log('ehorizontalStackedBarChartOptions optionsafterupdate', this.ehorizontalStackedBarChartOptions)
    }
    if (this.funnel) {
      echarts.init(chartElement).setOption(this.eFunnelChartOptions);
      console.log('eFunnelChartOptions optionsafterupdate', this.eFunnelChartOptions)
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
      const dimensions: Dimension[] = this.dualAxisColumnData;
      const categories = this.flattenDimensions(dimensions);
      object = { xaxis: {labels: {show: this.xLabelSwitch}, categories: this.chartsColumnData}};
      if(this.bar){
        if(this.isApexCharts){
        this.chartOptions3.xaxis.labels.show = this.xLabelSwitch;
        this.chartOptions3.xaxis.categories = this.chartsColumnData;
        }else{
          this.eBarChartOptions.xAxis.axisLabel.show = this.xLabelSwitch;
        }
      }
      else if(this.area){
        if(this.isApexCharts){
        this.chartOptions1.xaxis.labels.show = this.xLabelSwitch;
        this.chartOptions1.xaxis.categories = this.chartsColumnData;
        }else{
          this.eAreaChartOptions.xAxis.axisLabel.show = this.xLabelSwitch;
        }
      }
      else if(this.line){
        if(this.isApexCharts){
        this.chartOptions.xaxis.labels.show = this.xLabelSwitch;
        this.chartOptions.xaxis.categories = this.chartsColumnData;
        }else{
          this.eLineChartOptions.xAxis.axisLabel.show = this.xLabelSwitch;
        }
      }
      else if(this.sidebyside){
        if(this.isApexCharts){
        this.chartOptions2.xaxis.labels.show = this.xLabelSwitch;
        this.chartOptions2.xaxis.categories = categories;
        }else{
          this.eSideBySideBarChartOptions.xAxis.axisLabel.show = this.xLabelSwitch;
        }
      }
      else if(this.stocked){
        if(this.isApexCharts){
        this.chartOptions6.xaxis.labels.show = this.xLabelSwitch;
        this.chartOptions6.xaxis.categories = categories;
        }else{
          this.eStackedBarChartOptions.xAxis.axisLabel.show = this.xLabelSwitch;
        }
      }
      else if(this.barLine){
        if(this.isApexCharts){
        this.chartOptions5.xaxis.labels.show = this.xLabelSwitch;
        this.chartOptions5.xaxis.categories = categories;
        }else{
          this.eBarLineChartOptions.xAxis[0].axisLabel.show = this.xLabelSwitch;
        }
      }
      else if(this.horizentalStocked){
        if(this.isApexCharts){
        this.chartOptions7.xaxis.labels.show = this.xLabelSwitch;
        this.chartOptions7.xaxis.categories = categories;
        }else{
          this.ehorizontalStackedBarChartOptions.xAxis.axisLabel.show = this.xLabelSwitch;
        }
      }
      else if(this.grouped){
        if(this.isApexCharts){
        this.chartOptions8.xaxis.labels.show = this.xLabelSwitch;
        this.chartOptions8.xaxis.categories = categories;
        }else{
          this.eGroupedBarChartOptions.xAxis.axisLabel.show = this.xLabelSwitch;
        }
      }
      else if(this.multiLine){
        if(this.isApexCharts){
        this.chartOptions9.xaxis.labels.show = this.xLabelSwitch;
        this.chartOptions9.xaxis.categories = categories;
        }else{
          this.eMultiLineChartOptions.xAxis.axisLabel.show = this.xLabelSwitch;
        }
      }
      else if(this.heatMap){
        if(this.isApexCharts){
        this.heatMapChartOptions.xaxis.labels.show = this.xLabelSwitch;
        this.heatMapChartOptions.xaxis.categories = categories;
        }else{
          this.eHeatMapChartOptions.xAxis.axisLabel.show = this.xLabelSwitch;
        }
      }

    }
    else if(type === 'ylabel'){
      this.yLabelSwitch = !this.yLabelSwitch;
      // object = { yaxis: {labels: {show: this.yLabelSwitch, style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }}}};
      object = {yaxis: {labels : {show: this.yLabelSwitch, offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }, formatter: this.formatNumber.bind(this)}}};
      if(this.bar){
        if(this.isApexCharts){
        if(this.chartOptions3.yaxis.length >0){
          (this.chartOptions3.yaxis as any[]).forEach((data)=>{
            data.labels.show = this.yLabelSwitch;
          })
        }
        else{
          this.chartOptions3.yaxis.labels.show = this.yLabelSwitch;
        }
      }else{
        this.eBarChartOptions.yAxis.axisLabel.show = this.yLabelSwitch;
      }
      }
      else if(this.area){
        if(this.isApexCharts){
        if(this.chartOptions1.yaxis.length >0){
          (this.chartOptions1.yaxis as any[]).forEach((data)=>{
            data.labels.show = this.yLabelSwitch;
          })
        }
        else{
          this.chartOptions1.yaxis.labels.show = this.yLabelSwitch;
        }
      }else{
        this.eAreaChartOptions.yAxis.axisLabel.show = this.yLabelSwitch;
      }
      }
      else if(this.line){
        if(this.isApexCharts){
        if(this.chartOptions.yaxis.length >0){
          (this.chartOptions.yaxis as any[]).forEach((data)=>{
            data.labels.show = this.yLabelSwitch;
          })
        }
        else{
          this.chartOptions.yaxis.labels.show = this.yLabelSwitch;
        }
      }else{
        this.eLineChartOptions.yAxis.axisLabel.show = this.yLabelSwitch;
      }
      }
      else if(this.sidebyside){
        if(this.isApexCharts){
        if(this.chartOptions2.yaxis.length >0){
          (this.chartOptions2.yaxis as any[]).forEach((data)=>{
            data.labels.show = this.yLabelSwitch;
          })
        }
        else{
          this.chartOptions2.yaxis.labels.show = this.yLabelSwitch;
        }
      }else{
        this.eSideBySideBarChartOptions.yAxis.axisLabel.show = this.yLabelSwitch;
      }
      }
      else if(this.stocked){
        if(this.isApexCharts){
        if(this.chartOptions6.yaxis.length >0){
          (this.chartOptions6.yaxis as any[]).forEach((data)=>{
            data.labels.show = this.yLabelSwitch;
          })
        }
        else{
          this.chartOptions6.yaxis.labels.show = this.yLabelSwitch;
        }
      }else{
        this.eStackedBarChartOptions.yAxis.axisLabel.show = this.yLabelSwitch;
      }
      }
      else if(this.barLine){
        object = {yaxis: 
          [
            {show: true,labels : {show: this.yLabelSwitch, offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }, formatter: this.formatNumber.bind(this)}},
            {show: true,opposite: true,labels : {show: this.yLabelSwitch, offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }, formatter: this.formatNumber.bind(this)}}
          ]
        };
        if(this.isApexCharts){
        if(this.chartOptions5.yaxis.length >0){
          (this.chartOptions5.yaxis as any[]).forEach((data)=>{
            data.labels.show = this.yLabelSwitch;
          })
        }
        else{
          this.chartOptions5.yaxis.labels.show = this.yLabelSwitch;
        }
      }else{
        this.eBarLineChartOptions.yAxis[1].axisLabel.show = this.yLabelSwitch;
      }
      }
      else if(this.horizentalStocked){
        object = {yaxis: {labels : {show: this.yLabelSwitch, offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }}}};
        if(this.isApexCharts){
        if(this.chartOptions7.yaxis.length >0){
          (this.chartOptions7.yaxis as any[]).forEach((data)=>{
            data.labels.show = this.yLabelSwitch;
          })
        }
        else{
          this.chartOptions7.yaxis.labels.show = this.yLabelSwitch;
        }
      }else{
        this.ehorizontalStackedBarChartOptions.yAxis.axisLabel.show = this.yLabelSwitch;
      }
      }
      else if(this.grouped){
        object = {yaxis: {labels : {show: this.yLabelSwitch, offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }}}};
        if(this.isApexCharts){
        if(this.chartOptions8.yaxis.length >0){
          (this.chartOptions8.yaxis as any[]).forEach((data)=>{
            data.labels.show = this.yLabelSwitch;
          })
        }
        else{
          this.chartOptions8.yaxis.labels.show = this.yLabelSwitch;
        }
      }else{
        this.eGroupedBarChartOptions.yAxis.axisLabel.show = this.yLabelSwitch;
      }
      }
      else if(this.multiLine){
        if(this.isApexCharts){
        if(this.chartOptions9.yaxis.length >0){
          (this.chartOptions9.yaxis as any[]).forEach((data)=>{
            data.labels.show = this.yLabelSwitch;
          })
        }
        else{
          this.chartOptions9.yaxis.labels.show = this.yLabelSwitch;
        }
      }else{
        this.eMultiLineChartOptions.yAxis.axisLabel.show = this.yLabelSwitch;
      }
      }
      else if(this.heatMap){
        if(this.isApexCharts){
        if(this.heatMapChartOptions.yaxis.length >0){
          (this.heatMapChartOptions.yaxis as any[]).forEach((data)=>{
            data.labels.show = this.yLabelSwitch;
          })
        }
        else{
          this.heatMapChartOptions.yaxis.labels.show = this.yLabelSwitch;
        }
      }else{
        this.eHeatMapChartOptions.yAxis.axisLabel.show = this.yLabelSwitch;
      }
    }
    }
    else if(type === 'xgrid'){
      this.xGridSwitch = !this.xGridSwitch;
      object = {grid: {xaxis: {lines: {show: this.xGridSwitch}}}};
      if(this.bar){
        if(this.isApexCharts){
        this.chartOptions3.grid.xaxis.lines.show = this.xGridSwitch;
        }else{
          this.eBarChartOptions.xAxis.splitLine.show = this.xGridSwitch;
        }
      }
      else if(this.area){
        if(this.isApexCharts){
        this.chartOptions1.grid.xaxis.lines.show = this.xGridSwitch;
        }else{
          this.eAreaChartOptions.xAxis.splitLine.show = this.xGridSwitch;
        }
      }
      else if(this.line){
        if(this.isApexCharts){
        this.chartOptions.grid.xaxis.lines.show = this.xGridSwitch;
        }else{
          this.eLineChartOptions.xAxis.splitLine.show = this.xGridSwitch;
        }
      }
      else if(this.sidebyside){
        if(this.isApexCharts){
        this.chartOptions2.grid.xaxis.lines.show = this.xGridSwitch;
        }else{
          this.eSideBySideBarChartOptions.xAxis.splitLine.show = this.xGridSwitch;
        }
      }
      else if(this.stocked){
        if(this.isApexCharts){
        this.chartOptions6.grid.xaxis.lines.show = this.xGridSwitch;
        }else{
          this.eStackedBarChartOptions.xAxis.splitLine.show = this.xGridSwitch;
        }
      }
      else if(this.barLine){
        if(this.isApexCharts){
        this.chartOptions5.grid.xaxis.lines.show = this.xGridSwitch;
        }else{
          this.eBarLineChartOptions.xAxis[0].splitLine.show = this.xGridSwitch;
        }
      }
      else if(this.horizentalStocked){
        if(this.isApexCharts){
        this.chartOptions7.grid.xaxis.lines.show = this.xGridSwitch;
        }else{
          this.ehorizontalStackedBarChartOptions.xAxis.splitLine.show = this.xGridSwitch;
        }
      }
      else if(this.grouped){
        if(this.isApexCharts){
        this.chartOptions8.grid.xaxis.lines.show = this.xGridSwitch;
        }else{
          this.eGroupedBarChartOptions.xAxis.splitLine.show = this.xGridSwitch;
        }
      }
      else if(this.multiLine){
        if(this.isApexCharts){
        this.chartOptions9.grid.xaxis.lines.show = this.xGridSwitch;
        }else{
          this.eMultiLineChartOptions.xAxis.splitLine.show = this.xGridSwitch;
        }
      }
      else if(this.heatMap){
        if(this.isApexCharts){
        this.heatMapChartOptions.grid.xaxis.lines.show = this.xGridSwitch;
        }else{
          this.eHeatMapChartOptions.xAxis.splitLine.show = this.xGridSwitch;
        }
      }
    }
    else if(type === 'ygrid'){
      this.yGridSwitch = !this.yGridSwitch;
      object = {grid: {yaxis: {lines: {show: this.yGridSwitch}}}};
      if(this.bar){
        if(this.isApexCharts){
        this.chartOptions3.grid.yaxis.lines.show = this.yGridSwitch;
        }else{
          this.eBarChartOptions.yAxis.splitLine.show = this.yGridSwitch;
        }
      }
      else if(this.area){
        if(this.isApexCharts){
        this.chartOptions1.grid.yaxis.lines.show = this.yGridSwitch;
        }else{
          this.eBarChartOptions.yAxis.splitLine.show = this.yGridSwitch;
        }
      }
      else if(this.line){
        if(this.isApexCharts){
        this.chartOptions.grid.yaxis.lines.show = this.yGridSwitch;
        }else{
          this.eLineChartOptions.yAxis.splitLine.show = this.yGridSwitch;
        }
      }
      else if(this.sidebyside){
        if(this.isApexCharts){
        this.chartOptions2.grid.yaxis.lines.show = this.yGridSwitch;
        }else{
          this.eSideBySideBarChartOptions.yAxis.splitLine.show = this.yGridSwitch;
        }
      }
      else if(this.stocked){
        if(this.isApexCharts){
        this.chartOptions6.grid.yaxis.lines.show = this.yGridSwitch;
        }else{
          this.eStackedBarChartOptions.yAxis.splitLine.show = this.yGridSwitch;
        }
      }
      else if(this.barLine){
        if(this.isApexCharts){
        this.chartOptions5.grid.yaxis.lines.show = this.yGridSwitch;
        }else{
          this.eBarLineChartOptions.yAxis[0].splitLine.show = this.yGridSwitch;
          this.eBarLineChartOptions.yAxis[1].splitLine.show = this.yGridSwitch;

        }
      }
      else if(this.horizentalStocked){
        if(this.isApexCharts){
        this.chartOptions7.grid.yaxis.lines.show = this.yGridSwitch;
        }else{
          this.ehorizontalStackedBarChartOptions.yAxis.splitLine.show = this.yGridSwitch;
        }
      }
      else if(this.grouped){
        if(this.isApexCharts){
        this.chartOptions8.grid.yaxis.lines.show = this.yGridSwitch;
        }else{
          this.eGroupedBarChartOptions.yAxis.splitLine.show = this.yGridSwitch;
        }
      }
      else if(this.multiLine){
        if(this.isApexCharts){
        this.chartOptions9.grid.yaxis.lines.show = this.yGridSwitch;
        }else{
          this.eMultiLineChartOptions.yAxis.splitLine.show = this.yGridSwitch;
        }
      }
      else if(this.heatMap){
        if(this.isApexCharts){
        this.heatMapChartOptions.grid.yaxis.lines.show = this.yGridSwitch;
        }
        else{
          this.eHeatMapChartOptions.yAxis.splitLine.show = this.yGridSwitch;
        }
      }
    }
    else if(type === 'legend'){
      this.legendSwitch = !this.legendSwitch;
      object = {legend: {show: this.legendSwitch}};
      if(this.pie){
        if(this.isApexCharts){
        this.chartOptions4.legend.show = this.legendSwitch;
        }
        else{
          this.ePieChartOptions.legend.show = this.legendSwitch;
        }
      }
      else if(this.donut){
        if(this.isApexCharts){
        this.chartOptions10.legend.show = this.legendSwitch;
        }else{
          this.eDonutChartOptions.legend.show = this.legendSwitch;
        }
      }
    else if(this.radar){
      this.eRadarChartOptions.legend.show = this.legendSwitch;
    }
    }
    else if(type === 'dataLabels'){
      this.dataLabels = !this.dataLabels;
      object = {dataLabels: {enabled: this.dataLabels}}; 
      if(this.pie){
        if(this.isApexCharts){
        this.chartOptions4.dataLabels.enabled = this.dataLabels;
        }else{
          this.ePieChartOptions.series[0].label.show = this.dataLabels;
        }
      }
      else if(this.donut){
        if(this.isApexCharts){
        this.chartOptions10.dataLabels.enabled = this.dataLabels;
        }else{
          this.eDonutChartOptions.series[0].label.show = this.dataLabels;
        }
      }
      else if(this.radar){
        this.eRadarChartOptions.series[0].data.forEach((dataItem: { label: { show: boolean; }; }) => {
          dataItem.label.show = this.dataLabels; // Show or hide labels based on checkbox state
      });      }
    }
    else if(type === 'label'){
      this.label = !this.label;
      object = {plotOptions: {pie: {donut: {labels: {show: this.label}}}}}
      if(this.donut){
        this.chartOptions10.plotOptions.pie.donut.labels.show = this.label;
      }
    }
    else if(type === 'distributed'){
      this.isDistributed = !this.isDistributed;
      if(this.isApexCharts){
      object = {plotOptions: {bar: {distributed: this.isDistributed}}};
      this.funnelChartOptions.plotOptions.bar.distributed = this.isDistributed;
      }else{
      // this.eFunnelChartOptions.series[0].label
      }
    }
    if(this.isApexCharts){
    this.updateChart(object);
    }else{
      this.updateEchartOptions();
    }
  }
  enableZoom(){
    this.isZoom = !this.isZoom;
    if (this.bar) {
      this.eBarChartOptions.dataZoom = this.isZoom ? [{
        type: 'slider',
        show: true
      }] : [{
        type: 'slider',
        show: false
      }];
    }
    if(this.line){
      this.eLineChartOptions.dataZoom = this.isZoom ? [{
        type: 'slider',
        show: true
      }] : [{
        type: 'slider',
        show: false
      }];
    }
    if(this.area){
      this.eAreaChartOptions.dataZoom = this.isZoom ? [{
        type: 'slider',
        show: true
      }] : [{
        type: 'slider',
        show: false
      }];
    }
    if(this.sidebyside){
      this.eSideBySideBarChartOptions.dataZoom = this.isZoom ? [{
        type: 'slider',
        show: true
      }] : [{
        type: 'slider',
        show: false
      }];
    }
    if(this.stocked){
      this.eStackedBarChartOptions.dataZoom = this.isZoom ? [{
        type: 'slider',
        show: true
      }] : [{
        type: 'slider',
        show: false
      }];
    }
    if(this.heatMap){
      this.eHeatMapChartOptions.dataZoom = this.isZoom ? [{
        type: 'slider',
        show: true
      }] : [{
        type: 'slider',
        show: false
      }];
    }
    if(this.barLine){
      this.eBarLineChartOptions.dataZoom = this.isZoom ? [{
        type: 'slider',
        show: true
      }] : [{
        type: 'slider',
        show: false
      }];
    }
    if(this.horizentalStocked){
      this.ehorizontalStackedBarChartOptions.dataZoom = this.isZoom ? [{
        type: 'slider',
        show: true
      }] : [{
        type: 'slider',
        show: false
      }];
    }
    if(this.grouped){
      this.eGroupedBarChartOptions.dataZoom = this.isZoom ? [{
        type: 'slider',
        show: true
      }] : [{
        type: 'slider',
        show: false
      }];
    }
    if(this.multiLine){
      this.eMultiLineChartOptions.dataZoom = this.isZoom ? [{
        type: 'slider',
        show: true
      }] : [{
        type: 'slider',
        show: false
      }];
    }
    this.updateEchartOptions()
  }

  changeAlignment(){

    if(this.bar){
      this.barChart();
    }
    else if(this.area){
      this.areaChart();
    }
    else if(this.line){
      this.lineChart();
    }
    else if(this.barLine){
      this.barLineChart();
    }
    else if(this.sidebyside){
      this.sidebysideBar();
    }
    else if(this.stocked){
      this.stockedBar();
    }
    else if(this.horizentalStocked){
      this.horizentalStockedBar();
    }
    else if(this.grouped){
      this.hGrouped();
    }
    else if(this.multiLine){
      this.multiLineChart();
    }
    else if(this.heatMap){
      this.heatMapChart();
    }
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
      }
    } else {
      formattedNumber = (value).toFixed(this.KPIDecimalPlaces)
    }

    this.KPINumber = this.KPIPrefix + formattedNumber + this.KPISuffix;
  }
  numberPopupTrigger(){
    this.numberPopup = !this.numberPopup;
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
  this.router.navigate(['/insights/configure-page/configure'])
}

fetchChartData(chartData: any){
  this.databaseId = chartData.database_id;
          this.qrySetId = chartData.queryset_id;
          this.draggedColumnsData = chartData.col;
          this.draggedRowsData = chartData.row;
          this.draggedColumns = chartData.columns;
          this.draggedRows = chartData.rows;
          this.filterId =[];
          this.filterQuerySetId = null,
          this.sheetfilter_querysets_id = null;
          
          console.log("This is ShaetData",chartData)
          this.sheetTitle = chartData.chart_title;
          this.sheetTagName = chartData.chart_title;
          if (chartData.chart_type.toLowerCase().includes("bar")){
            this.chartDisplay(false,true,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,6);
          }else if (chartData.chart_type.toLowerCase().includes("pie")){
            this.chartDisplay(false,false,false,false,true,false,false,false,false,false,false,false,false,false,false,false,false,false,false,24);
          }else if (chartData.chart_type.toLowerCase().includes("line")){
            this.chartDisplay(false,false,false,true,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,13);
          }else if (chartData.chart_type.toLowerCase().includes("area")){
            this.chartDisplay(false,false,true,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,17);
          }else if (chartData.chart_type.toLowerCase().includes("donut")){
            this.chartDisplay(false,false,false,false,false,false,false,false,false,false,false,true,false,false,false,false,false,false,false,10);
          }
          this.dataExtraction();

}

  changeChartPlugin() {
    if (this.selectedChartPlugin == 'apex') {
      this.isApexCharts = true;
      this.isEChatrts = false;
    } else {
      this.isApexCharts = false;
      this.isEChatrts = true;
    }
    if(this.retriveDataSheet_id){
      if((this.sheetResponce.isEChart && this.isEChatrts && (this.sheetChartId === this.chartId)) || (this.sheetResponce.isApexChart && this.isApexCharts && (this.sheetChartId === this.chartId))){
        this.sheetRetrive(false);
      } else {
        this.reAssignChartData();
        this.resetCustomizations();
      }
    } else{
      this.reAssignChartData();
      this.resetCustomizations();
    }
  }
  reAssignChartData() {
    if (this.bar) {
      this.barChart();
    } else if (this.area) {
      this.areaChart();
    } else if (this.line) {
      this.lineChart();
    } else if (this.pie) {
      this.pieChart();
    } else if (this.sidebyside) {
      this.sidebysideBar();
    } else if (this.stocked) {
      this.stockedBar();
    } else if (this.barLine) {
      this.barLineChart();
    } else if (this.horizentalStocked) {
      this.horizentalStockedBar();
    } else if (this.grouped) {
      this.hGrouped();
    } else if (this.multiLine) {
      this.multiLineChart();
    } else if (this.donut) {
      this.donutChart();
    } else if (this.radar) {
      this.radarChart();
    } else if (this.heatMap) {
      this.heatMapChart();
    } else if (this.kpi){
      this.KPIChart();
    } else if (this.funnel){
      this.funnelChart();
    }else if(this.guage){
      this.guageChart();
    } else if(this.map){
      this.mapChart();
    }
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
     if(colorCase === 1){
      if(this.bar){ 
          this.eBarChartOptions.xAxis.splitLine.lineStyle.color = this.xGridColor;
      }
      else if(this.area){
          this.eAreaChartOptions.xAxis.splitLine.lineStyle.color = this.xGridColor;
      }
      else if(this.line){
          this.eLineChartOptions.xAxis.splitLine.lineStyle.color = this.xGridColor;
      }
      else if(this.sidebyside){
          this.eSideBySideBarChartOptions.xAxis.splitLine.lineStyle.color = this.xGridColor;
      }
      else if(this.stocked){
          this.eStackedBarChartOptions.xAxis.splitLine.lineStyle.color = this.xGridColor;
      }
      else if(this.barLine){
          this.eBarLineChartOptions.xAxis[0].splitLine.lineStyle.color = this.xGridColor;
      }
      else if(this.horizentalStocked){
        this.ehorizontalStackedBarChartOptions.xAxis.splitLine.lineStyle.color = this.xGridColor;
      }
      else if(this.grouped){
          this.eGroupedBarChartOptions.xAxis[0].axisLabel.splitLine.lineStyle.color = this.xGridColor;
      }
      else if(this.multiLine){
          this.eMultiLineChartOptions.xAxis.splitLine.lineStyle.color = this.xGridColor;
      }
      else if(this.heatMap){
          this.eHeatMapChartOptions.xAxis.splitLine.lineStyle.color = this.xGridColor;
      }
    }
    if(colorCase === 3){
      if(this.bar){ 
          this.eBarChartOptions.yAxis.splitLine.lineStyle.color = this.yGridColor;
      }
      else if(this.area){
          this.eAreaChartOptions.yAxis.splitLine.lineStyle.color = this.yGridColor;
      }
      else if(this.line){
          this.eLineChartOptions.yAxis.splitLine.lineStyle.color = this.yGridColor;
      }
      else if(this.sidebyside){
          this.eSideBySideBarChartOptions.yAxis.splitLine.lineStyle.color = this.yGridColor;
      }
      else if(this.stocked){
          this.eStackedBarChartOptions.yAxis.splitLine.lineStyle.color = this.yGridColor;
      } 
      else if(this.barLine){
          this.eBarLineChartOptions.yAxis[0].splitLine.lineStyle.color = this.yGridColor;
          this.eBarLineChartOptions.yAxis[1].splitLine.lineStyle.color = this.yGridColor;

      }
      else if(this.horizentalStocked){
        this.ehorizontalStackedBarChartOptions.yAxis.splitLine.lineStyle.color = this.yGridColor;
      }
      else if(this.grouped){
          this.eGroupedBarChartOptions.yAxis[0].axisLabel.splitLine.lineStyle.color = this.yGridColor;
      }
      else if(this.multiLine){
          this.eMultiLineChartOptions.yAxis.splitLine.lineStyle.color = this.yGridColor;
      }
      else if(this.heatMap){
          this.eHeatMapChartOptions.yAxis.splitLine.lineStyle.color = this.yGridColor;
      }
    }
     this.updateEchartOptions();
  }

  setCustomizeOptions(data: any) {
    this.isZoom = data.isZoom || true;
    this.xGridColor = data.xGridColor || '#2392c1';
    this.xGridSwitch = data.xGridSwitch || false;
    this.xLabelSwitch = data.xLabelSwitch || true;
    this.xLabelColor = data.xLabelColor || '#2392c1';
    this.yLabelSwitch = data.yLabelSwitch || true;
    this.yGridColor = data.yGridColor || '#2392c1';
    this.yGridSwitch = data.yGridSwitch || false;
    this.yLabelColor = data.yLabelColor || '#2392c1';
    this.xLabelFontFamily = data.xLabelFontFamily || 'sans-serif';
    this.xLabelFontSize = data.xLabelFontSize || 12;
    this.xlabelFontWeight = data.xlabelFontWeight || 400;
    this.backgroundColor = data.backgroundColor || '#fff';
    this.color = data.color || '#2392c1';
    this.ylabelFontWeight = data.ylabelFontWeight || 400;
    this.isBold = data.isBold || false;
    this.yLabelFontFamily = data.yLabelFontFamily || 'sans-serif';
    this.yLabelFontSize = data.yLabelFontSize || 12;
    this.bandingSwitch = data.bandingSwitch || false;
    this.backgroundColorSwitch = data.backgroundColorSwitch || false;
    this.chartColorSwitch = data.chartColorSwitch || false;
    this.barColorSwitch = data.barColorSwitch || false;
    this.lineColorSwitch = data.lineColorSwitch || false;
    this.gridLineColorSwitch = data.gridLineColorSwitch || false;
    this.xLabelColorSwitch = data.xLabelColorSwitch || false;
    this.xGridLineColorSwitch = data.xGridLineColorSwitch || false;
    this.yLabelColorSwitch = data.yLabelColorSwitch || false;
    this.yGridLineColorSwitch = data.yGridLineColorSwitch || false;
    this.bandingColorSwitch = data.bandingColorSwitch || false;
    this.kpiColorSwitch = data.kpiColorSwitch || false;
    this.funnelColorSwitch = data.funnelColorSwitch || false;
    this.color1 = data.color1 || undefined;
    this.color2 = data.color2 || undefined;
    this.kpiColor = data.kpiColor || '#000000';
    this.barColor = data.barColor || '#4382f7';
    this.lineColor = data.lineColor || '#38ff98';
    this.GridColor = data.GridColor || '#089ffc';
    this.legendSwitch = data.legendSwitch || true;
    this.dataLabels = data.dataLabels || true;
    this.label = data.label || true;
    this.donutSize = data.donutSize || 50;
    this.isDistributed = data.isDistributed || false;
    this.kpiFontSize = data.kpiFontSize || 3;
    this.minValueGuage = data.minValueGuage || 0;
    this.maxValueGuage = data.maxValueGuage || 100;
    this.donutDecimalPlaces = data.donutDecimalPlaces || 0;
    this.decimalPlaces = data.decimalPlaces || 0;
    this.legendsAllignment = data.legendsAllignment || 'bottom';
    this.displayUnits = data.displayUnits || 'none';
    this.suffix = data.suffix || '';
    this.prefix = data.prefix || '';
    this.dataLabelsFontFamily = data.dataLabelsFontFamily || 'sans-serif';
    this.dataLabelsFontSize = data.dataLabelsFontSize || '12px';
    this.dataLabelsFontPosition = data.dataLabelsFontPosition || 'top';
    this.measureAlignment = data.measureAlignment || 'center';
    this.dimensionAlignment = data.dimensionAlignment || 'center';
    this.tableDataFontFamily = data.tableDataFontFamily || 'sans-serif';
    this.tableDataFontSize = data.tableDataFontSize || '12px';
    this.tableDataFontWeight = data.tableDataFontWeight || 400;
    this.tableDataFontStyle = data.tableDataFontStyle || 'normal';
    this.tableDataFontDecoration = data.tableDataFontDecoration || 'none';
    this.tableDataFontColor = data.tableDataFontColor || '#000000';
    this.tableDataFontAlignment = data.tableDataFontAlignment || 'left';
    this.headerFontFamily = data.headerFontFamily || "'Arial', sans-serif";
    this.headerFontSize = data.headerFontSize || '16px';
    this.headerFontWeight = data.headerFontWeight || 700;
    this.headerFontStyle = data.headerFontStyle || 'normal';
    this.headerFontDecoration = data.headerFontDecoration || 'none';
    this.headerFontColor = data.headerFontColor || '#000000'
    this.headerFontAlignment = data.headerFontAlignment || 'left';
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
    this.ylabelFontWeight = 400;
    this.isBold = false;
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
    this.isDistributed = false;
    this.kpiFontSize = '3';
    this.minValueGuage = 0;
    this.maxValueGuage = 100;
    this.donutDecimalPlaces = 0;
    this.decimalPlaces = 0;
    this.legendsAllignment = 'bottom';
    this.displayUnits = 'none';
    this.suffix = '';
    this.prefix = '';
    this.dataLabelsFontFamily = 'sans-serif';
    this.dataLabelsFontSize = '12px';
    this.dataLabelsFontPosition = 'top';
    this.measureAlignment = 'center';
    this.dimensionAlignment = 'center';
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
  gridLineColor(color: any){
    let object : any;
    if(color){
      object = {grid: { borderColor: color }}
      if(this.barchart){
        this.chartOptions3.grid.borderColor = color;
      }
      else if(this.areachart){
        this.chartOptions1.grid.borderColor = color;
      }
      else if(this.linechart){
        this.chartOptions.grid.borderColor = color;
      }
      else if(this.sidebysideChart){
        this.chartOptions2.grid.borderColor = color;
      }
      else if(this.stockedChart){
        this.chartOptions6.grid.borderColor = color;
      }
      else if(this.barlineChart){
        this.chartOptions5.grid.borderColor = color;
      }
      else if(this.horizontolstockedChart){
        this.chartOptions7.grid.borderColor = color;
      }
      else if(this.groupedChart){
        this.chartOptions8.grid.borderColor = color;
      }
      else if(this.multilineChart){
        this.chartOptions9.grid.borderColor = color;
      }
      this.updateChart(object);
    }
  }
  setBackgroundColor(color: any){
    let object:any;
    if (color) {
      object = { chart: { background: color } };
      if (this.bar) {
        if (this.isApexCharts) {
          this.chartOptions3.chart.background = color;
        } else {
          this.eBarChartOptions.backgroundColor = color;
        }
      }
      else if (this.area) {
        if (this.isApexCharts) {
          this.chartOptions1.chart.background = color;
        } else {
          this.eAreaChartOptions.backgroundColor = color;
        }
      }
      else if (this.line) {
        if (this.isApexCharts) {
          this.chartOptions.chart.background = color;
        } else {
          this.eLineChartOptions.backgroundColor = color;
        }
      }
      else if (this.sidebyside) {
        if (this.isApexCharts) {
          this.chartOptions2.chart.background = color;
        } else {
          this.eSideBySideBarChartOptions.backgroundColor = color;
        }
      }
      else if (this.stocked) {
        if (this.isApexCharts) {
          this.chartOptions6.chart.background = color;
        } else {
          this.eStackedBarChartOptions.backgroundColor = color;
        }
      }
      else if (this.barLine) {
        if (this.isApexCharts) {
          this.chartOptions5.chart.background = color;
        } else {
          this.eBarLineChartOptions.backgroundColor = color;
        }
      }
      else if (this.horizentalStocked) {
        if (this.isApexCharts) {
          this.chartOptions7.chart.background = color;
        } else {
          this.ehorizontalStackedBarChartOptions.backgroundColor = color;
        }
      }
      else if (this.grouped) {
        if (this.isApexCharts) {
          this.chartOptions8.chart.background = color;
        } else {
          this.eGroupedBarChartOptions.backgroundColor = color;
        }
      }
      else if (this.multiLine) {
        if (this.isApexCharts) {
          this.chartOptions9.chart.background = color;
        } else {
          this.eMultiLineChartOptions.backgroundColor = color;
        }
      }
      else if (this.pie) {
        if (this.isApexCharts) {
          this.chartOptions4.chart.background = color;
        } else {
          this.ePieChartOptions.backgroundColor = color;
        }
      }
      else if (this.donut) {
        if (this.isApexCharts) {
          this.chartOptions10.chart.background = color;
        } else {
          this.eDonutChartOptions.backgroundColor = color;
        }
      }
      else if (this.heatMap) {
        if (this.isApexCharts) {
          this.heatMapChartOptions.chart.background = color;
        } else {
          this.eHeatMapChartOptions.backgroundColor = color;
        }
      }
      else if (this.funnel) {
        if (this.isApexCharts) {
          this.funnelChartOptions.chart.background = color;
        } else {
          this.eFunnelChartOptions.backgroundColor = color;
        }
      }
      else if(this.radar){
        this.eRadarChartOptions.backgroundColor = color;
      }
      else if(this.guage){
        this.guageChartOptions.chart.background = color;

      }
      if (this.isApexCharts) {
        this.updateChart(object);
      } else {
        this.updateEchartOptions();
      }
    }
  }
  openDateFormatModal(modal: any){
    this.modalService.open(modal, {
      centered: true,
      windowClass: 'animate__animated animate__zoomIn',
    });
  }
  dateFormat(column:any, index:any, format:any){
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
        }
  }

  removeDrillDownColumn(index:any,column:any){
       
    this.draggedDrillDownColumns.splice(index, 1);
    if (index <= 0) {
      this.drillDownIndex = 0;
      this.draggedDrillDownColumns = [];
      this.drillDownObject = [];
    } else if (index <= this.drillDownIndex) {
      this.drillDownObject = this.drillDownObject.slice(0, index - 1);
      this.drillDownIndex = index - 1;
    } 
       this.dataExtraction();
      }

      toggleDateSwitch(){
            this.dateDrillDownSwitch = !this.dateDrillDownSwitch;
            if(this.dateDrillDownSwitch){
              this.draggedDrillDownColumns = ["year","quarter","month","date"];
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
            if(this.drillDownIndex > 0) {
              this.drillDownIndex--;
              this.drillDownObject.pop();
              this.callDrillDown();
            }         
          }
  
  changeLegendsAllignment(allignment:any){
    this.legendsAllignment = allignment;
      let object : any = {legend: {position: allignment}};
      if(this.pie){
        if(this.isApexCharts){
        this.legendsAllignment = allignment;
        this.chartOptions4.legend.position = allignment;
        }else{
          this.ePieChartOptions.legend.left = null;
        this.ePieChartOptions.legend.right = null;
        this.ePieChartOptions.legend.top = null;
        this.ePieChartOptions.legend.bottom = null;
          switch (allignment) {
            case 'top':
                // this.ePieChartOptions.legend.left = 'center';
                this.ePieChartOptions.legend.top = 'top';
                this.ePieChartOptions.legend.orient = 'horizontal';
                break;
            case 'bottom':
                // this.ePieChartOptions.legend.left = 'center';
                this.ePieChartOptions.legend.bottom = 'bottom';
                this.ePieChartOptions.legend.orient = 'horizontal';
                break;
            case 'left':
                this.ePieChartOptions.legend.left = 'left';
                this.ePieChartOptions.legend.orient = 'vertical';
                // this.ePieChartOptions.legend.top = 'center';
                break;
            case 'right':
                this.ePieChartOptions.legend.right = 'right';
                this.ePieChartOptions.legend.orient = 'vertical';
                // this.ePieChartOptions.legend.top = 'center';
                break;
            default:
                break;
        }
        }
      }
      else if(this.donut){
        if(this.isApexCharts){
        this.legendsAllignment = allignment;
        this.chartOptions10.legend.position = allignment;
        }else{
          this.eDonutChartOptions.legend.left = null;
        this.eDonutChartOptions.legend.right = null;
        this.eDonutChartOptions.legend.top = null;
        this.eDonutChartOptions.legend.bottom = null;
          switch (allignment) {
            case 'top':
                // this.ePieChartOptions.legend.left = 'center';
                this.eDonutChartOptions.legend.top = 'top';
                this.eDonutChartOptions.legend.orient = 'horizontal';
                break;
            case 'bottom':
                // this.ePieChartOptions.legend.left = 'center';
                this.eDonutChartOptions.legend.bottom = 'bottom';
                this.eDonutChartOptions.legend.orient = 'horizontal';
                break;
            case 'left':
                this.eDonutChartOptions.legend.left = 'left';
                this.eDonutChartOptions.legend.orient = 'vertical';
                // this.ePieChartOptions.legend.top = 'center';
                break;
            case 'right':
                this.eDonutChartOptions.legend.right = 'right';
                this.eDonutChartOptions.legend.orient = 'vertical';
                // this.ePieChartOptions.legend.top = 'center';
                break;
            default:
                break;
        }
        }
      }
      else if(this.radar){
        
        this.eRadarChartOptions.legend.left = allignment === 'left' ? 'left' : 
        allignment === 'right' ? 'right' :
        allignment === 'top' ? 'top' : 
        'bottom';
      }
      if(this.isApexCharts){
      this.updateChart(object);
      }else{
        this.updateEchartOptions();
      }
    
  }

  changeSize(){
    if(this.isEChatrts){
      this.donutChart();
    } else {
    let object : any = {plotOptions: { pie: {donut: {size: this.donutSize+'%'}}}};
    this.chartOptions10.plotOptions.pie.donut.size = this.donutSize+'%';
    this.updateChart(object);
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
      }
      sort(event: any, numbers: any, labels: any) {
        const pairedData = numbers.map((num: any, index: any) => [num, labels[index]]);
      
        if (event.target.value === 'ascending') {
          pairedData.sort((a: any, b: any) => a[0] - b[0]);
        } else if (event.target.value === 'descending') {
          pairedData.sort((a: any, b: any) => b[0] - a[0]);
        }

        const sortedNumbers = pairedData.map((pair: any) => pair[0]);
        const sortedLabels = pairedData.map((pair: any) => pair[1]);
      
        return { sortedNumbers, sortedLabels };
      }
      
      sortSeries(event: any) {
        if (this.funnel) {
          if(this.isEChatrts){
            let numbers : any[] = [];
            let labels: any[] = [];
            this.eFunnelChartOptions.series[0].data.forEach((data:any)=>{
              numbers.push(data.value);
              labels.push(data.name);
            })
            // const labels = this.eFunnelChartOptions.series[0].data.name;
            const sortedData = this.sort(event, numbers, labels);
            const funnelData : any[] = [];
            console.log(sortedData);
            sortedData.sortedLabels.forEach((name: any, index: number) => {
              funnelData.push({
                name: name,
                value: sortedData.sortedNumbers[index]
              });
            });
            this.eFunnelChartOptions.series[0].data = funnelData;
            this.updateEchartOptions();
          } else{
            const numbers = this.funnelChartOptions.series[0].data;
            const labels = this.funnelChartOptions.xaxis.categories;
            const sortedData = this.sort(event, numbers, labels);

            this.funnelChartOptions.series[0].data = sortedData.sortedNumbers;
            this.funnelChartOptions.xaxis.categories = sortedData.sortedLabels;
            this.funnelCharts.updateSeries([{ data: sortedData.sortedNumbers }]);
            this.funnelCharts.updateOptions({ xaxis: { categories: sortedData.sortedLabels } });
          }
        } 
        else if (this.bar) {
          if(this.isEChatrts){
            // this.eBarchart.setOption({
            //   xAxis: {
            //     data: this.chartsColumnData.map(item => item.name),
            //   },
            //   series: [
            //     {
            //       data: thiss.barData.map(item => item.value),
            //     },
            //   ],
            // });
            const numbers = this.eBarChartOptions.series[0].data;
            const labels = this.eBarChartOptions.xAxis.data;
            const sortedData = this.sort(event, numbers, labels);
            this.eBarChartOptions.series[0].data = sortedData.sortedNumbers;
            this.eBarChartOptions.xAxis.data = sortedData.sortedLabels;
            this.updateEchartOptions();
          } else {
            const numbers = this.chartOptions3.series[0].data;
            const labels = this.chartOptions3.xaxis.categories;
            const sortedData = this.sort(event, numbers, labels);
            console.log(numbers);
            this.chartOptions3.series[0].data = sortedData.sortedNumbers;
            this.chartOptions3.xaxis.categories = sortedData.sortedLabels;
            this.barchart.updateSeries([{ data: sortedData.sortedNumbers }]);
            this.barchart.updateOptions({xaxis:{categories: sortedData.sortedLabels}});
          }
        }
      }      
      funnelDLAllign:any;
      funnelDLFontFamily:any;
      funnelDLFontSize:any;
      funnelFontChange(event:any,type:any){
        let font = event.target.value;
        let object = {};
        if(type === 'family'){
          this.funnelChartOptions.dataLabels.style.fontFamily = font;
          object = { datalabels: { style: { fontFamily: font } } };
          object = this.funnelChartOptions
        } else if(type === 'size'){
          let size = event.target.value;
          this.funnelChartOptions.dataLabels.style.fontSize = size;
          object = { datalabels: { style: { fontSize: size } } };
          object = this.funnelChartOptions;
        } else if(type === 'allign'){
          let allign = event.target.value;
          this.funnelChartOptions.plotOptions.bar.dataLabels.position = allign;
          object = { plotOptions: { bar: { dataLabels: { position: allign } } } }
        }
        this.updateChart(object);
      }
      funnelColor:any;
      funnelColorChange(event:any){
      if(this.funnelColor){
        let selectedColor = event;
        this.funnelChartOptions.series[0].color = selectedColor;
        let object = {series: [{color: selectedColor}]}
        object = this.funnelChartOptions;
        this.updateChart(object);
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
      donutDecimalPlaces: number = 0;

      updateDonut(){
        this.donutchart.updateOptions(this.chartOptions10);
      }

      setDataLabelsFontFamily(event:any){
        let font = event.target.value;
        let object = { dataLabels: { style: { fontFamily: font } } };
        let guageObject = {plotOptions: {radialBar:{dataLabels: { value: { fontFamily: font } }} }};
        if(this.bar){
          if(this.isApexCharts){
          this.chartOptions3.dataLabels.style.fontFamily = font;
          }else{
            this.eBarChartOptions.series[0].label.fontFamily = font;
          }
          //  object = this.chartOptions3;
        }
        else if(this.area){
          if(this.isApexCharts){
          this.chartOptions1.dataLabels.style.fontFamily = font;
          // object = { dataLabels: { style: { fontFamily: font } } };
          // object = this.chartOptions1;
          }else{
            this.eAreaChartOptions.series[0].label.fontFamily = font;
          }
        }
        else if(this.line){
          if(this.isApexCharts){
          this.chartOptions.dataLabels.style.fontFamily = font;
          // object = { dataLabels: { style: { fontFamily: font } } };
          // object = this.chartOptions;
          }else{
            this.eLineChartOptions.series[0].label.fontFamily = font;
          }
        }
        else if(this.sidebyside){
          if(this.isApexCharts){
          this.chartOptions2.dataLabels.style.fontFamily = font;
          // object = { dataLabels: { style: { fontFamily: font } } };
          // object = this.chartOptions2;
          }else{
            this.eSideBySideBarChartOptions.series.forEach((series:any) => {
              series.label.fontFamily = font; // Set new font family
          });          
        }
        }
        else if(this.stocked){
          if(this.isApexCharts){
          this.chartOptions6.dataLabels.style.fontFamily = font;
          // object = { dataLabels: { style: { fontFamily: font } } };
          // object = this.chartOptions6;
          }else{
            this.eStackedBarChartOptions.series.forEach((series:any) => {
              series.label.fontFamily = font; // Set new font family
          });    
          }
        }
        else if(this.barLine){
          if(this.isApexCharts){
          this.chartOptions5.dataLabels.style.fontFamily = font;
          }else{
            this.eBarLineChartOptions.series.forEach((series: { label: { fontFamily: any; }; }) => {
              series.label.fontFamily = font; 
          });
          }
          // object = { dataLabels: { style: { fontFamily: font } } };
          // object = this.chartOptions5;
        }
        else if(this.horizentalStocked){
          if(this.isApexCharts){
          this.chartOptions7.dataLabels.style.fontFamily = font;
          }else{
            this.ehorizontalStackedBarChartOptions.series.forEach((series: { label: { fontFamily: any; }; }) => {
              series.label.fontFamily = font; 
          });
          }
          // object = { dataLabels: { style: { fontFamily: font } } };
          // object = this.chartOptions7;
        }
        else if(this.grouped){
          if(this.isApexCharts){
          this.chartOptions8.dataLabels.style.fontFamily = font;
          }else{
            this.eGroupedBarChartOptions.series.forEach((series: { label: { fontFamily: any; }; }) => {
              series.label.fontFamily = font; 
          });
          }
          // object = { dataLabels: { style: { fontFamily: font } } };
          // object = this.chartOptions8;
        }
        else if(this.multiLine){
          if(this.isApexCharts){
          this.chartOptions9.dataLabels.style.fontFamily = font;
          }else{
            this.eMultiLineChartOptions.series.forEach((series: { label: { fontFamily: any; }; }) => {
              series.label.fontFamily = font; 
          });
          }
          // object = { dataLabels: { style: { fontFamily: font } } };
          // object = this.chartOptions9;
        }
        else if(this.heatMap){
          if(this.isApexCharts){
          this.heatMapChartOptions.dataLabels.style.fontFamily = font;
          }else{
            this.eHeatMapChartOptions.series[0].label.fontFamily = font;
          }
        }
        else if(this.funnel){
          if(this.isApexCharts){
          this.funnelChartOptions.dataLabels.style.fontFamily = font;
          }else{
          this.eFunnelChartOptions.series[0].label.fontFamily = font  
          }
        }
        else if(this.radar){
          this.eRadarChartOptions.series[0].data.forEach((dataItem: { label: { fontFamily: any; }; }) => {
            if (dataItem.label) { // Ensure label exists before updating
                dataItem.label.fontFamily = font;
            }
        });
        }
        else if(this.guage){
          this.guageChartOptions.plotOptions.radialBar.dataLabels.value.fontFamily = font;
        }
        if(this.isApexCharts){
          if(this.guage){
            this.updateChart(guageObject);
          }else{
            this.updateChart(object);
          }
        }else{
          this.updateEchartOptions();
        }
      }

      setDataLabelsFontSize(event:any){
        let font = event.target.value;
        let object = { dataLabels: { style: { fontSize: font } } };
        let guageObject = {plotOptions: {radialBar:{dataLabels: { value: { fontSize: font } }} }};

        if(this.bar){
          if(this.isApexCharts){
          this.chartOptions3.dataLabels.style.fontSize = font;
          }else{
            this.eBarChartOptions.series[0].label.fontSize = font;
          }
        }
        else if(this.area){
          if(this.isApexCharts){
          this.chartOptions1.dataLabels.style.fontSize = font;
          }else{
            this.eAreaChartOptions.series[0].label.fontSize = font;
          }
        }
        else if(this.line){
          if(this.isApexCharts){
          this.chartOptions.dataLabels.style.fontSize = font;
          // object = { dataLabels: { style: { fontSize: font } } };
          // object = this.chartOptions;
          }else{
            this.eLineChartOptions.series[0].label.fontSize = font;
          }
        }
        else if(this.sidebyside){
          if(this.isApexCharts){
          this.chartOptions2.dataLabels.style.fontSize = font;
          // object = { dataLabels: { style: { fontSize: font } } };
          // object = this.chartOptions2;
          }else{
            this.eSideBySideBarChartOptions.series.forEach((series:any) => {
              series.label.fontSize = font; // Set new font family
          });    
          }
        }
        else if(this.stocked){
          if(this.isApexCharts){
          this.chartOptions6.dataLabels.style.fontSize = font;
          // object = { dataLabels: { style: { fontSize: font } } };
          // object = this.chartOptions6;
          }else{
            this.eStackedBarChartOptions.series.forEach((series:any) => {
              series.label.fontSize = font; // Set new font family
          });           }
        }
        else if(this.barLine){
          if(this.isApexCharts){
          this.chartOptions5.dataLabels.style.fontSize = font;
          }else{
            this.eBarLineChartOptions.series.forEach((series: { label: { fontSize: any; }; }) => {
              series.label.fontSize = font; 
          });
          }
          // object = { dataLabels: { style: { fontSize: font } } };
          // object = this.chartOptions5;
        }
        else if(this.horizentalStocked){
          if(this.isApexCharts){
          this.chartOptions7.dataLabels.style.fontSize = font;
          }else{
            this.ehorizontalStackedBarChartOptions.series.forEach((series: { label: { fontSize: any; }; }) => {
              series.label.fontSize = font; 
          });
          }
          // object = { dataLabels: { style: { fontSize: font } } };
          // object = this.chartOptions7;
        }
        else if(this.grouped){
          if(this.isApexCharts){
          this.chartOptions8.dataLabels.style.fontSize = font;
          }else{
            this.eGroupedBarChartOptions.series.forEach((series: { label: { fontSize: any; }; }) => {
              series.label.fontSize = font; 
          });
          }
          // object = { dataLabels: { style: { fontSize: font } } };
          // object = this.chartOptions8;
        }
        else if(this.multiLine){
          if(this.isApexCharts){
          this.chartOptions9.dataLabels.style.fontSize = font;
          }else{
            this.eMultiLineChartOptions.series.forEach((series: { label: { fontSize: any; }; }) => {
              series.label.fontSize = font; 
          });
          }
          // object = { dataLabels: { style: { fontSize: font } } };
          // object = this.chartOptions9;
        }
        else if(this.heatMap){
          if(this.isApexCharts){
          this.heatMapChartOptions.dataLabels.style.fontSize = font;
          }else{
            this.eHeatMapChartOptions.series[0].label.fontSize = font;
          }
        }
        else if(this.funnel){
          if(this.isApexCharts){
          this.funnelChartOptions.dataLabels.style.fontSize = font;
          }else{
            this.eFunnelChartOptions.series[0].label.fontSize = font  
          }
        }
        if(this.radar){
          this.eRadarChartOptions.series[0].data.forEach((dataItem: { label: { fontSize: any; }; }) => {
            if (dataItem.label) { // Ensure label exists before updating
                dataItem.label.fontSize = font;
            }
        });
        }
        if(this.guage){
          this.guageChartOptions.plotOptions.radialBar.dataLabels.value.fontSize = font;
        }
        if(this.isApexCharts){
          if(this.guage){
            this.updateChart(guageObject)
          }else{
        this.updateChart(object);
          }
        }else{
          this.updateEchartOptions();
        }
      }

      setDataLabelsFontStyle(fontStyle:any){
        let font: number;
        let object;
        if(fontStyle === 'B'){
          this.isBold = !this.isBold;
          font = this.isBold ? 700 : 400;
          object = { dataLabels: { style: { fontWeight: font } } };
          let guageObject = {plotOptions: {radialBar:{dataLabels: { value: { fontWeight: font } }} }};

          if(this.bar){
            if(this.isApexCharts){
            this.chartOptions3.dataLabels.style.fontWeight = font;
            }else{
              this.eBarChartOptions.series[0].label.fontWeight = font;
            }
            // object = this.chartOptions3;
          }
          else if(this.area){
            if(this.isApexCharts){
            this.chartOptions1.dataLabels.style.fontWeight = font;
            // object = { dataLabels: { style: { fontWeight: font } } };
            // object = this.chartOptions1;
            }else{
              this.eAreaChartOptions.series[0].label.fontWeight = font;
            }
          }
          else if(this.line){
            if(this.isApexCharts){
            this.chartOptions.dataLabels.style.fontWeight = font;
            // object = { dataLabels: { style: { fontWeight: font } } };
            // object = this.chartOptions;
            }else{
              this.eLineChartOptions.series[0].label.fontWeight = font;
            }
          }
          else if(this.sidebyside){
            if(this.isApexCharts){
            this.chartOptions2.dataLabels.style.fontWeight = font;
            // object = { dataLabels: { style: { fontWeight: font } } };
            // object = this.chartOptions2;
            }else{
              this.eSideBySideBarChartOptions.series.forEach((series:any) => {
                series.label.fontWeight = font; // Set new font family
            });    
            }
          }
          else if(this.stocked){
            if(this.isApexCharts){
            this.chartOptions6.dataLabels.style.fontWeight = font;
            // object = { dataLabels: { style: { fontWeight: font } } };
            // object = this.chartOptions6;
            }else{
              this.eStackedBarChartOptions.series.forEach((series:any) => {
                series.label.fontWeight = font; // Set new font family
            });             }
          }
          else if(this.barLine){
            if(this.isApexCharts){
            this.chartOptions5.dataLabels.style.fontWeight = font;
            }else{
              this.eBarLineChartOptions.series.forEach((series: { label: { fontWeight: any; }; }) => {
                series.label.fontWeight = font; 
            });
            }
            // object = { dataLabels: { style: { fontWeight: font } } };
            // object = this.chartOptions5;
          }
          else if(this.horizentalStocked){
            if(this.isApexCharts){
            this.chartOptions7.dataLabels.style.fontWeight = font;
            }else{
              this.ehorizontalStackedBarChartOptions.series.forEach((series: { label: { fontWeight: any; }; }) => {
                series.label.fontWeight = font; 
            });
            }
            // object = { dataLabels: { style: { fontWeight: font } } };
            // object = this.chartOptions7;
          }
          else if(this.grouped){
            if(this.isApexCharts){
            this.chartOptions8.dataLabels.style.fontWeight = font;
            }else{
              this.eGroupedBarChartOptions.series.forEach((series: { label: { fontWeight: any; }; }) => {
                series.label.fontWeight = font; 
            });
            }
            // object = { dataLabels: { style: { fontWeight: font } } };
            // object = this.chartOptions8;
          }
          else if(this.multiLine){
            if(this.isApexCharts){
            this.chartOptions9.dataLabels.style.fontWeight = font;
            }else{
              this.eMultiLineChartOptions.series.forEach((series: { label: { fontWeight: any; }; }) => {
                series.label.fontWeight = font; 
            });
            }
            // object = { dataLabels: { style: { fontWeight: font } } };
            // object = this.chartOptions9;
          }
          else if(this.heatMap){
            if(this.isApexCharts){
            this.heatMapChartOptions.dataLabels.style.fontWeight = font;
            }else{
              this.eHeatMapChartOptions.series[0].label.fontWeight = font;
            }
          }
          else if(this.funnel){
            if(this.isApexCharts){
            this.funnelChartOptions.dataLabels.style.fontWeight = font;
            }else{
              this.eFunnelChartOptions.series[0].label.fontWeight = font  
            }
          }
          else if(this.radar){
            this.eRadarChartOptions.series[0].data.forEach((dataItem: { label: { fontWeight: number; }; }) => {
              if (dataItem.label) { // Ensure label exists before updating
                  dataItem.label.fontWeight = font;
              }
          });
          }
          else if(this.guage){
            this.guageChartOptions.plotOptions.radialBar.dataLabels.value.fontWeight = font;
          }
          if(this.isApexCharts){
            if(this.guage){
          this.updateChart(guageObject);
            }else{
              this.updateChart(object)
            }
          }else{
            this.updateEchartOptions();
          }
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
        this.selectedElement.style.border = '2px solid #2392c1';
        const color = window.getComputedStyle(element).backgroundColor;
        let object = { dataLabels: { style: { colors : [color] } } };
        let guageObject = {plotOptions: {radialBar:{dataLabels: { value: { colors: color } }} }};

        if(this.bar){
          if(this.isApexCharts){
          this.chartOptions3.dataLabels.style.colors = [color];
          // object = { dataLabels: { style: { colors : [color] } } };
          }else{
            this.eBarChartOptions.series[0].label.color = color;
          }
          // object = this.chartOptions3;
        }
        else if(this.area){
          if(this.isApexCharts){
          this.chartOptions1.dataLabels.style.colors = [color];
          // object = { dataLabels: { style: { colors : [color] } } };
          // object = this.chartOptions1;
          }else{
            this.eAreaChartOptions.series[0].label.color = color;
          }
        }
        else if(this.line){
          if(this.isApexCharts){
          this.chartOptions.dataLabels.style.colors = [color];
          // object = { dataLabels: { style: { colors : [color] } } };
          // object = this.chartOptions;
          }else{
            this.eLineChartOptions.series[0].label.color = color;
          }
        }
        else if(this.sidebyside){
          if(this.isApexCharts){
          this.chartOptions2.dataLabels.style.colors = [color];
          // object = { dataLabels: { style: { colors : [color] } } };
          // object = this.chartOptions2;
          }else{
            this.eSideBySideBarChartOptions.series.forEach((series:any) => {
              series.label.color = color; // Set new font family
          }); 
          }
        }
        else if(this.stocked){
          if(this.isApexCharts){
          this.chartOptions6.dataLabels.style.colors = [color];
          // object = { dataLabels: { style: { colors : [color] } } };
          // object = this.chartOptions6;
          }else{
            this.eStackedBarChartOptions.series.forEach((series:any) => {
              series.label.color = color; // Set new font family
          }); 
          }
        }
        else if(this.barLine){
          if(this.isApexCharts){
          this.chartOptions5.dataLabels.style.colors = [color];
          }else{
            this.eBarLineChartOptions.series.forEach((series: { label: { color: any; }; }) => {
              series.label.color = color; 
          });
          }
          // object = { dataLabels: { style: { colors : [color] } } };
          // object = this.chartOptions5;
        }
        else if(this.horizentalStocked){
          if(this.isApexCharts){
          this.chartOptions7.dataLabels.style.colors = [color];
          }else{
            this.ehorizontalStackedBarChartOptions.series.forEach((series: { label: { color: any; }; }) => {
              series.label.color = color; 
          });
          }
          // object = { dataLabels: { style: { colors : [color] } } };
          // object = this.chartOptions7;
        }
        else if(this.grouped){
          if(this.isApexCharts){
          this.chartOptions8.dataLabels.style.colors = [color];
          }else{
            this.eGroupedBarChartOptions.series.forEach((series: { label: { color: any; }; }) => {
              series.label.color = color; 
          });
          }
          // object = { dataLabels: { style: { colors : [color] } } };
          // object = this.chartOptions8;
        }
        else if(this.multiLine){
          if(this.isApexCharts){
          this.chartOptions9.dataLabels.style.colors = [color];
          }else{
            this.eMultiLineChartOptions.series.forEach((series: { label: { color: any; }; }) => {
              series.label.color = color; 
          });
          }
          // object = { dataLabels: { style: { colors : [color] } } };
          // object = this.chartOptions9;
        }
        else if(this.heatMap){
          if(this.isApexCharts){
          this.heatMapChartOptions.dataLabels.style.colors = [color];
          }else{
            this.eHeatMapChartOptions.series[0].label.color = color;
          }
        }
        else if(this.funnel){
          if(this.isApexCharts){
          this.funnelChartOptions.dataLabels.style.colors = [color];
          }else{
            this.eFunnelChartOptions.series[0].label.color = color;  
          }
        }
        else if(this.radar){
          this.eRadarChartOptions.series[0].data.forEach((dataItem: { label: { color: string; }; }) => {
            dataItem.label.color = color;
        });        }
        if(this.guage){
          this.guageChartOptions.plotOptions.radialBar.dataLabels.value.colors = color.toString();
        }
        element.style.border = `1px solid black`;
        this.selectedElement = element;
        if(this.isApexCharts){
          if(this.guage){
            this.updateChart(guageObject)
          }else{
        this.updateChart(object);
          }
        }else{
          this.updateEchartOptions();
        }
      }

      setDataLabelsFontPosition(position:any){
        this.dataLabelsFontPosition = position;
        let object;
        object = { plotOptions: { bar: { dataLabels: { position: position } } } };
        if(this.bar){
          if(this.isApexCharts){
          this.chartOptions3.plotOptions.bar.dataLabels.position = position;
          }else{
            this.eBarChartOptions.series[0].label.position = position;
          }
        }
        else if(this.line){
          if(this.isApexCharts){
            object = { dataLabels: { offsetY: (position === 'top') ? -10 : ((position === 'center') ? 0 : 10) } };
            this.chartOptions.dataLabels.offsetY = (position === 'top') ? -10 : ((position === 'center') ? 0 : 10);
          } else{
            this.eLineChartOptions.series[0].label.position = position;
          }
        }
        else if(this.area){
          if(this.isApexCharts){
            object = { dataLabels: { offsetY: (position === 'top') ? -10 : ((position === 'center') ? 0 : 10) } };
            this.chartOptions1.dataLabels.offsetY = (position === 'top') ? -10 : ((position === 'center') ? 0 : 10);
          } else{
            this.eAreaChartOptions.series[0].label.position = position;
          }
        }
        else if(this.sidebyside){
          // object = { plotOptions: { bar: { dataLabels: { position: position } } } };
          if(this.isApexCharts){
          this.chartOptions2.plotOptions.bar.dataLabels.position = position;
          }else{
          this.eSideBySideBarChartOptions.series.forEach((series:any) => {
            series.label.position = position; // Set new font family
        });   
        } 
        }
        else if(this.stocked){
          if(this.isApexCharts){
          this.chartOptions6.plotOptions.bar.dataLabels.position = position;
          }else{
            this.eStackedBarChartOptions.series.forEach((series:any) => {
              series.label.position = position; // Set new font family
          }); 
          }
        }
        else if(this.barLine){
          if(this.isApexCharts){
          this.chartOptions5.plotOptions.bar.dataLabels.position = position;
          }else{
            this.eBarLineChartOptions.series.forEach((series: { label: { position: any; }; }) => {
              series.label.position = position; 
          });
          }
        }
        else if(this.horizentalStocked){
          // object = { plotOptions: { bar: { dataLabels: { position: position } } } };
          if(this.isApexCharts){
          this.chartOptions7.plotOptions.bar.dataLabels.position = position;
          }else{
            this.ehorizontalStackedBarChartOptions.series.forEach((series: { label: { position: any; }; }) => {
              series.label.position = position; 
          });
          }
        }
        else if(this.grouped){
          // object = { plotOptions: { bar: { dataLabels: { position: position } } } };
          if(this.isApexCharts){
          this.chartOptions8.plotOptions.bar.dataLabels.position = position;
          }else{
            this.eGroupedBarChartOptions.series.forEach((series: { label: { position: any; }; }) => {
              series.label.position = position; 
          });
          }
        }
        else if(this.heatMap){
          if(this.isApexCharts){
          this.heatMapChartOptions.plotOptions.bar.dataLabels.position = position;
          }else{
            this.eHeatMapChartOptions.series[0].label.position = position;
          }
        }
        else if(this.funnel){
          this.funnelChartOptions.plotOptions.bar.dataLabels.position = position;
        }
        if(this.isApexCharts){
        this.updateChart(object);
        }else{
          this.updateEchartOptions();
        }
      }
      resetChartColor(){
        this.color = '#00A5A2';
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
        this.gridLineColor(this.GridColor);
      }
      resetBackgroundColor(){
        this.backgroundColor = '#ffffff';
        this.setBackgroundColor(this.backgroundColor);
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
            this.loaderService.hide();
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
        } as any;
        if (this.fromFileId) {
          delete obj.server_id;
          obj.file_id = this.fileId;
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
      this.changeChartPlugin();
    }

    dimensionsFontFamilyChange(){
      let  object = {xaxis: {labels: {style: {fontFamily: this.xLabelFontFamily}}, categories: this.chartsColumnData}};
      if(this.bar){
        if(this.isApexCharts){
        this.chartOptions3.xaxis.labels.style.fontFamily = this.xLabelFontFamily;
      }else{
        this.eBarChartOptions.xAxis.axisLabel.fontFamily = this.xLabelFontFamily;
      }
    }
      else if (this.area) {
        if(this.isApexCharts){
        this.chartOptions1.xaxis.labels.style.fontFamily = this.xLabelFontFamily;
        }else{
          this.eAreaChartOptions.xAxis.axisLabel.fontFamily = this.xLabelFontFamily;
        }
      }
      else if(this.line){
        if(this.isApexCharts){
        this.chartOptions.xaxis.labels.style.fontFamily = this.xLabelFontFamily;
        }else{
          this.eLineChartOptions.xAxis.axisLabel.fontFamily = this.xLabelFontFamily;
        }
      }
      else if(this.sidebyside){
        if(this.isApexCharts){
        this.chartOptions2.xaxis.labels.style.fontFamily = this.xLabelFontFamily;
        }else{
          this.eSideBySideBarChartOptions.xAxis.axisLabel.fontFamily = this.xLabelFontFamily;
        }
      }
      else if(this.stocked){
        if(this.isApexCharts){
        this.chartOptions6.xaxis.labels.style.fontFamily = this.xLabelFontFamily;
        }else{
          this.eStackedBarChartOptions.xAxis.axisLabel.fontFamily = this.xLabelFontFamily; 
        }
      }
      else if(this.barLine){
        if(this.isApexCharts){
        this.chartOptions5.xaxis.labels.style.fontFamily = this.xLabelFontFamily;
        }else{
          this.eBarLineChartOptions.xAxis[0].axisLabel.fontFamily = this.xLabelFontFamily;
        }
      }
      else if(this.horizentalStocked){
        if(this.isApexCharts){
        this.chartOptions7.xaxis.labels.style.fontFamily = this.xLabelFontFamily;
        }else{
          this.ehorizontalStackedBarChartOptions.xAxis.axisLabel.fontFamily = this.xLabelFontFamily;
        }
      }
      else if(this.grouped){
        if(this.isApexCharts){
        this.chartOptions8.xaxis.labels.style.fontFamily = this.xLabelFontFamily;
        }else{
          this.eGroupedBarChartOptions.xAxis.axisLabel.fontFamily = this.xLabelFontFamily;
        }
      }
      else if(this.multiLine){
        if(this.isApexCharts){
        this.chartOptions9.xaxis.labels.style.fontFamily = this.xLabelFontFamily;
        }else{
          this.eMultiLineChartOptions.xAxis.axisLabel.fontFamily = this.xLabelFontFamily;
        }
      }
      else if(this.heatMap){
        if(this.isApexCharts){
        this.heatMapChartOptions.xaxis.labels.style.fontFamily = this.xLabelFontFamily;
        }else{
          this.eHeatMapChartOptions.xAxis.axisLabel.textStyle.fontFamily = this.xLabelFontFamily;
        }
      }
      if(this.isApexCharts){
      this.updateChart(object);
      }else{
        this.updateEchartOptions();
      }
    }
    dimensionsFontSizeChange(){
      let  object = {xaxis: {labels: {style: {fontSize: this.xLabelFontSize}}, categories: this.chartsColumnData}};
      if(this.bar){
        if(this.isApexCharts){
        this.chartOptions3.xaxis.labels.style.fontSize = this.xLabelFontSize;
        }else{
          this.eBarChartOptions.xAxis.axisLabel.fontSize = this.xLabelFontSize;
        }
      }
      else if (this.area) {
        if(this.isApexCharts){
        this.chartOptions1.xaxis.labels.style.fontSize = this.xLabelFontSize;
        }else{
        this.eAreaChartOptions.xAxis.axisLabel.fontSize = this.xLabelFontSize;  
        }
      }
      else if(this.line){
        if(this.isApexCharts){
        this.chartOptions.xaxis.labels.style.fontSize = this.xLabelFontSize;
         }else{
        this.eLineChartOptions.xAxis.axisLabel.fontSize = this.xLabelFontSize;  
        }
      }
      else if(this.sidebyside){
        if(this.isApexCharts){
        this.chartOptions2.xaxis.labels.style.fontSize = this.xLabelFontSize;
      }else{
        this.eSideBySideBarChartOptions.xAxis.axisLabel.fontSize = this.xLabelFontSize;  
        }
      }
      else if(this.stocked){
        if(this.isApexCharts){
        this.chartOptions6.xaxis.labels.style.fontSize = this.xLabelFontSize;
      }else{
        this.eStackedBarChartOptions.xAxis.axisLabel.fontSize = this.xLabelFontSize;  
        }
      }
      else if(this.barLine){
        if(this.isApexCharts){
        this.chartOptions5.xaxis.labels.style.fontSize = this.xLabelFontSize;
        }else{
          this.eBarLineChartOptions.xAxis[0].axisLabel.fontSize = this.xLabelFontSize;
        }
      }
      else if(this.horizentalStocked){
        if(this.isApexCharts){
        this.chartOptions7.xaxis.labels.style.fontSize = this.xLabelFontSize;
        }else{
          this.ehorizontalStackedBarChartOptions.xAxis.axisLabel.fontSize = this.xLabelFontSize;
        }
      }
      else if(this.grouped){
        if(this.isApexCharts){
        this.chartOptions8.xaxis.labels.style.fontSize = this.xLabelFontSize;
        }else{
          this.eGroupedBarChartOptions.xAxis.axisLabel.fontSize = this.xLabelFontSize;
        }
      }
      else if(this.multiLine){
        if(this.isApexCharts){
        this.chartOptions9.xaxis.labels.style.fontSize = this.xLabelFontSize;
        }else{
          this.eMultiLineChartOptions.xAxis.axisLabel.fontSize = this.xLabelFontSize
        }
      }
      else if(this.heatMap){
        if(this.isApexCharts){
        this.heatMapChartOptions.xaxis.labels.style.fontSize = this.xLabelFontSize;
        }else{
          this.eHeatMapChartOptions.xAxis.axisLabel.textStyle.fontSize = this.xLabelFontSize
        }
      }
      if(this.isApexCharts){
      this.updateChart(object);
      }else{
        this.updateEchartOptions();
      }
    }
    dimensionsFontWeightChange(){
      let  object = {xaxis: {labels: {style: {fontWeight: this.xlabelFontWeight}}, categories: this.chartsColumnData}};
      if(this.bar){
        if(this.isApexCharts){
        this.chartOptions3.xaxis.labels.style.fontWeight = this.xlabelFontWeight;
        }else{
          this.eBarChartOptions.xAxis.axisLabel.fontWeight = this.xlabelFontWeight;
        }
      }
      else if (this.area) {
        if(this.isApexCharts){
        this.chartOptions1.xaxis.labels.style.fontWeight = this.xlabelFontWeight;
        }else{
          this.eAreaChartOptions.xAxis.axisLabel.fontWeight = this.xlabelFontWeight;
        }
      }
      else if(this.line){
        if(this.isApexCharts){
        this.chartOptions.xaxis.labels.style.fontWeight = this.xlabelFontWeight;
        }else{
          this.eLineChartOptions.xAxis.axisLabel.fontWeight = this.xlabelFontWeight;
        }
      }
      else if(this.sidebyside){
        if(this.isApexCharts){
        this.chartOptions2.xaxis.labels.style.fontWeight = this.xlabelFontWeight;
        }else{
          this.eSideBySideBarChartOptions.xAxis.axisLabel.fontWeight = this.xlabelFontWeight;
        }
      }
      else if(this.stocked){
        if(this.isApexCharts){
        this.chartOptions6.xaxis.labels.style.fontWeight = this.xlabelFontWeight;
        }else{
          this.eStackedBarChartOptions.xAxis.axisLabel.fontWeight = this.xlabelFontWeight;
        }
      }
      else if(this.barLine){
        if(this.isApexCharts){
        this.chartOptions5.xaxis.labels.style.fontWeight = this.xlabelFontWeight;
        }else{
          this.eBarLineChartOptions.xAxis[0].axisLabel.fontWeight = this.xlabelFontWeight;
        }
      }
      else if(this.horizentalStocked){
        if(this.isApexCharts){
        this.chartOptions7.xaxis.labels.style.fontWeight = this.xlabelFontWeight;
        }else{
          this.ehorizontalStackedBarChartOptions.xAxis.axisLabel.fontWeight = this.xlabelFontWeight;
        }
      }
      else if(this.grouped){
        if(this.isApexCharts){
        this.chartOptions8.xaxis.labels.style.fontWeight = this.xlabelFontWeight;
        }else{
          this.eGroupedBarChartOptions.xAxis.axisLabel.fontWeight = this.xlabelFontWeight
        }
      }
      else if(this.multiLine){
        if(this.isApexCharts){
        this.chartOptions9.xaxis.labels.style.fontWeight = this.xlabelFontWeight;
        }else{
          this.eMultiLineChartOptions.xAxis.axisLabel.fontWeight = this.xlabelFontWeight
        }
      }
      else if(this.heatMap){
        if(this.isApexCharts){
        this.heatMapChartOptions.xaxis.labels.style.fontWeight = this.xlabelFontWeight;
        }else{
          this.eHeatMapChartOptions.xAxis.axisLabel.textStyle.fontWeight = this.xlabelFontWeight
        }
      }
      if(this.isApexCharts){
      this.updateChart(object);
      }else{
        this.updateEchartOptions();
      }
    }
    dimensionsColorChange(event:any){
      if (this.selectedElement) {
        this.selectedElement.style.border = 'none';
      }
        const element = event.target as HTMLElement;
        this.selectedElement = event.target as HTMLElement;
        this.selectedElement.style.border = '2px solid #2392c1';
        const color = window.getComputedStyle(element).backgroundColor;
        if(this.bar){
          this.eBarChartOptions.xAxis.axisLabel.color = color;
        }
        if(this.line){
          this.eLineChartOptions.xAxis.axisLabel.color = color;
        }
        if(this.area){
          this.eAreaChartOptions.xAxis.axisLabel.color = color;
        }
        if(this.sidebyside){
          this.eSideBySideBarChartOptions.xAxis.axisLabel.color = color;
        }
        if(this.stocked){
          this.eStackedBarChartOptions.xAxis.axisLabel.color = color;
        }
        if(this.barLine){
          this.eBarLineChartOptions.xAxis[0].axisLabel.color = color;
        }
        if(this.horizentalStocked){
          this.ehorizontalStackedBarChartOptions.xAxis.axisLabel.color = color;
        }
        if(this.grouped){
          this.eGroupedBarChartOptions.xAxis.axisLabel.color = color;
        }
        if(this.multiLine){
          this.eMultiLineChartOptions.xAxis.axisLabel.color = color;
        }
        if(this.heatMap){
          this.eHeatMapChartOptions.xAxis.axisLabel.textStyle.color = color;
        }
        this.updateEchartOptions();
    }
    measuresFontFamilyChange(){
      // let object = { yaxis: [{show: this.yLabelSwitch, labels: {show: this.yLabelSwitch, style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }, formatter: this.formatNumber.bind(this)} }] };
      let object;
      object = {yaxis: {labels : {show: this.yLabelSwitch, offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }, formatter: this.formatNumber.bind(this)}}};
      if (this.bar) {
        if(this.isApexCharts){
        if (this.chartOptions3.yaxis.length > 0) {
          (this.chartOptions3.yaxis as any[]).forEach((data) => {
            data.labels.style.fontFamily = this.yLabelFontFamily;
          })
        }
        else {
          this.chartOptions3.yaxis.labels.style.fontFamily = this.yLabelFontFamily;
        }
      }else{
        this.eBarChartOptions.yAxis.axisLabel.fontFamily = this.yLabelFontFamily;
      }
      }
      else if (this.area) {
        if(this.isApexCharts){
        if (this.chartOptions1.yaxis.length > 0) {
          (this.chartOptions1.yaxis as any[]).forEach((data) => {
            data.labels.style.fontFamily = this.yLabelFontFamily;
          })
        }
        else {
          this.chartOptions1.yaxis.labels.style.fontFamily = this.yLabelFontFamily;
        }
        }else{
          this.eAreaChartOptions.yAxis.axisLabel.fontFamily = this.yLabelFontFamily;
        }
      }
      else if(this.line){
        if(this.isApexCharts){
        if (this.chartOptions.yaxis.length > 0) {
          (this.chartOptions.yaxis as any[]).forEach((data) => {
            data.labels.style.fontFamily = this.yLabelFontFamily;
          })
        }
        else {
          this.chartOptions.yaxis.labels.style.fontFamily = this.yLabelFontFamily;
        }
      }else{
        this.eLineChartOptions.yAxis.axisLabel.fontFamily = this.yLabelFontFamily;
      }
      }
      else if(this.sidebyside){
        if(this.isApexCharts){
        if (this.chartOptions2.yaxis.length > 0) {
          (this.chartOptions2.yaxis as any[]).forEach((data) => {
            data.labels.style.fontFamily = this.yLabelFontFamily;
          })
        }
        else {
          this.chartOptions2.yaxis.labels.style.fontFamily = this.yLabelFontFamily;
        }
      }else{
        this.eSideBySideBarChartOptions.yAxis.axisLabel.fontFamily = this.yLabelFontFamily;
      }
      }
      else if(this.stocked){
        if(this.isApexCharts){
        if (this.chartOptions6.yaxis.length > 0) {
          (this.chartOptions6.yaxis as any[]).forEach((data) => {
            data.labels.style.fontFamily = this.yLabelFontFamily;
          })
        }
        else {
          this.chartOptions6.yaxis.labels.style.fontFamily = this.yLabelFontFamily;
        }
      }else{
        this.eStackedBarChartOptions.yAxis.axisLabel.fontFamily = this.yLabelFontFamily;
      }
      }
      else if(this.barLine){
        object = {yaxis: 
          [
            {show: true,labels : {show: this.yLabelSwitch, offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }, formatter: this.formatNumber.bind(this)}},
            {show: true,opposite: true,labels : {show: this.yLabelSwitch, offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }, formatter: this.formatNumber.bind(this)}}
          ]
        };
        if(this.isApexCharts){
        if (this.chartOptions5.yaxis.length > 0) {
          (this.chartOptions5.yaxis as any[]).forEach((data) => {
            data.labels.style.fontFamily = this.yLabelFontFamily;
          })
        }
        else {
          this.chartOptions5.yaxis.labels.style.fontFamily = this.yLabelFontFamily;
        }
      }else{
        this.eBarLineChartOptions.yAxis.forEach((axis: { axisLabel: { fontFamily: string; }; }) => {
          axis.axisLabel.fontFamily = this.yLabelFontFamily; // Update Y-axis label size
        });
      }
      }
      else if(this.horizentalStocked){
        object = {yaxis: {show: this.yLabelSwitch, labels : {offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }}}};
        if(this.isApexCharts){
        if (this.chartOptions7.yaxis.length > 0) {
          (this.chartOptions7.yaxis as any[]).forEach((data) => {
            data.labels.style.fontFamily = this.yLabelFontFamily;
          })
        }
        else {
          this.chartOptions7.yaxis.labels.style.fontFamily = this.yLabelFontFamily;
        }
      }else{
        this.ehorizontalStackedBarChartOptions.yAxis.axisLabel.fontFamily = this.yLabelFontFamily;
      }
      }
      else if(this.grouped){
        object = {yaxis: {show: this.yLabelSwitch, labels : {offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }}}};
        if(this.isApexCharts){
        if (this.chartOptions8.yaxis.length > 0) {
          (this.chartOptions8.yaxis as any[]).forEach((data) => {
            data.labels.style.fontFamily = this.yLabelFontFamily;
          })
        }
        else {
          this.chartOptions8.yaxis.labels.style.fontFamily = this.yLabelFontFamily;
        }
      }else{
        this.eGroupedBarChartOptions.yAxis.axisLabel.fontFamily = this.yLabelFontFamily;
      }
      }
      else if(this.multiLine){
        if(this.isApexCharts){
        if (this.chartOptions9.yaxis.length > 0) {
          (this.chartOptions9.yaxis as any[]).forEach((data) => {
            data.labels.style.fontFamily = this.yLabelFontFamily;
          })
        }
        else {
          this.chartOptions9.yaxis.labels.style.fontFamily = this.yLabelFontFamily;
        }
      }else{
        this.eMultiLineChartOptions.yAxis.axisLabel.fontFamily = this.yLabelFontFamily;
      }
      }
      else if(this.heatMap){
        if(this.isApexCharts){
        if (this.heatMapChartOptions.yaxis.length > 0) {
          (this.heatMapChartOptions.yaxis as any[]).forEach((data) => {
            data.labels.style.fontFamily = this.yLabelFontFamily;
          })
        }
        else {
          this.heatMapChartOptions.yaxis.labels.style.fontFamily = this.yLabelFontFamily;
        }
      }else{
        this.eHeatMapChartOptions.yAxis.axisLabel.textStyle.fontFamily = this.yLabelFontFamily;
      }
      }
      if(this.isApexCharts){
      this.updateChart(object);
      }else{
        this.updateEchartOptions();
      }
    }
    measuresFontSizeChange(){
      // let object = { yaxis: [{ labels: { style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }, formatter: this.formatNumber.bind(this)} }] };
      let object;
      object = {yaxis: {labels : {show: this.yLabelSwitch, offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }, formatter: this.formatNumber.bind(this)}}};
      if (this.bar) {
        if(this.isApexCharts){
        if (this.chartOptions3.yaxis.length > 0) {
          (this.chartOptions3.yaxis as any[]).forEach((data) => {
            data.labels.style.fontSize = this.yLabelFontSize;
          })
        }
        else {
          this.chartOptions3.yaxis.labels.style.fontSize = this.yLabelFontSize;
        }
      }else{
        this.eBarChartOptions.yAxis.axisLabel.fontSize = this.yLabelFontSize;

      }
      }
      else if (this.area) {
        if(this.isApexCharts){
        if (this.chartOptions1.yaxis.length > 0) {
          (this.chartOptions1.yaxis as any[]).forEach((data) => {
            data.labels.style.fontSize = this.yLabelFontSize;
          })
        }
        else {
          this.chartOptions1.yaxis.labels.style.fontSize = this.yLabelFontSize;
        }
      }else{
        this.eAreaChartOptions.yAxis.axisLabel.fontSize = this.yLabelFontSize;
      }
      }
      else if(this.line){
        if(this.isApexCharts){
        if (this.chartOptions.yaxis.length > 0) {
          (this.chartOptions.yaxis as any[]).forEach((data) => {
            data.labels.style.fontFamily = this.yLabelFontFamily;
          })
        }
        else {
          this.chartOptions.yaxis.labels.style.fontSize = this.yLabelFontSize;
        }
        }else{
          this.eLineChartOptions.yAxis.axisLabel.fontSize = this.yLabelFontSize;
        }
      }
      else if(this.sidebyside){
        if(this.isApexCharts){
        if (this.chartOptions2.yaxis.length > 0) {
          (this.chartOptions2.yaxis as any[]).forEach((data) => {
            data.labels.style.fontSize = this.yLabelFontSize;
          })
        }
        else {
          this.chartOptions2.yaxis.labels.style.fontSize = this.yLabelFontSize;
        }
        }else{
          this.eSideBySideBarChartOptions.yAxis.axisLabel.fontSize = this.yLabelFontSize;
        }

      }
      else if(this.stocked){
        if(this.isApexCharts){
        if (this.chartOptions6.yaxis.length > 0) {
          (this.chartOptions6.yaxis as any[]).forEach((data) => {
            data.labels.style.fontSize = this.yLabelFontSize;
          })
        }
        else {
          this.chartOptions6.yaxis.labels.style.fontSize = this.yLabelFontSize;
        }
      }else{
        this.eStackedBarChartOptions.yAxis.axisLabel.fontSize = this.yLabelFontSize;
      }
      }
      else if(this.barLine){
        object = {yaxis: 
          [
            {show: true,labels : {show: this.yLabelSwitch, offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }, formatter: this.formatNumber.bind(this)}},
            {show: true,opposite: true,labels : {show: this.yLabelSwitch, offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }, formatter: this.formatNumber.bind(this)}}
          ]
        };
        if(this.isApexCharts){
        if (this.chartOptions5.yaxis.length > 0) {
          (this.chartOptions5.yaxis as any[]).forEach((data) => {
            data.labels.style.fontSize = this.yLabelFontSize;
          })
        }
        else {
          this.chartOptions5.yaxis.labels.style.fontSize = this.yLabelFontSize;
        }
      }else{
         this.eBarLineChartOptions.yAxis.forEach((axis: { axisLabel: { fontSize: number; }; }) => {
          axis.axisLabel.fontSize = this.yLabelFontSize; // Update Y-axis label size
        });
        }
      }
      else if(this.horizentalStocked){
        object = {yaxis: {labels : {show: this.yLabelSwitch, offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }}}};
        if(this.isApexCharts){
        if (this.chartOptions7.yaxis.length > 0) {
          (this.chartOptions7.yaxis as any[]).forEach((data) => {
            data.labels.style.fontSize = this.yLabelFontSize;
          })
        }
        else {
          this.chartOptions7.yaxis.labels.style.fontSize = this.yLabelFontSize;
        }
      }else{
        this.ehorizontalStackedBarChartOptions.yAxis.axisLabel.fontSize = this.yLabelFontSize;
      }
      }
      else if(this.grouped){
        object = {yaxis: {labels : {show: this.yLabelSwitch, offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }}}};
        if(this.isApexCharts){
        if (this.chartOptions8.yaxis.length > 0) {
          (this.chartOptions8.yaxis as any[]).forEach((data) => {
            data.labels.style.fontSize = this.yLabelFontSize;
          })
        }
        else {
          this.chartOptions8.yaxis.labels.style.fontSize = this.yLabelFontSize;
        }
      }else{
        this.eGroupedBarChartOptions.yAxis.axisLabel.fontSize = this.yLabelFontSize;
      }
      }
      else if(this.multiLine){
        if(this.isApexCharts){
        if (this.chartOptions9.yaxis.length > 0) {
          (this.chartOptions9.yaxis as any[]).forEach((data) => {
            data.labels.style.fontSize = this.yLabelFontSize;
          })
        }
        else {
          this.chartOptions9.yaxis.labels.style.fontSize = this.yLabelFontSize;
        }
      }else{
        this.eMultiLineChartOptions.yAxis.axisLabel.fontSize = this.yLabelFontSize;
      }
      }
      else if(this.heatMap){
        if(this.isApexCharts){
        if (this.heatMapChartOptions.yaxis.length > 0) {
          (this.heatMapChartOptions.yaxis as any[]).forEach((data) => {
            data.labels.style.fontSize = this.yLabelFontSize;
          })
        }
        else {
          this.heatMapChartOptions.yaxis.labels.style.fontSize = this.yLabelFontSize;
        }
      }else{
        this.eHeatMapChartOptions.yAxis.axisLabel.textStyle.fontSize = this.yLabelFontSize;
      }
      }
      if(this.isApexCharts){
      this.updateChart(object);
      }else{
        this.updateEchartOptions();
      }
    }
    measuresFontWeightChange(){
      // let object = { yaxis: [{ labels: { style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }, formatter: this.formatNumber.bind(this)} }] };
      let object;
      object = {yaxis: {labels : {show: this.yLabelSwitch, offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }, formatter: this.formatNumber.bind(this)}}};
      if (this.bar) {
        if(this.isApexCharts){
        if (this.chartOptions3.yaxis.length > 0) {
          (this.chartOptions3.yaxis as any[]).forEach((data) => {
            data.labels.style.fontWeight = this.ylabelFontWeight;
          })
        }
        else {
          this.chartOptions3.yaxis.labels.style.fontWeight = this.ylabelFontWeight;
        }
      }else{
        this.eBarChartOptions.yAxis.axisLabel.fontWeight = this.ylabelFontWeight;
      }
      }
      else if (this.area) {
        if(this.isApexCharts){
        if (this.chartOptions1.yaxis.length > 0) {
          (this.chartOptions1.yaxis as any[]).forEach((data) => {
            data.labels.style.fontWeight = this.ylabelFontWeight;
          })
        }
        else {
          this.chartOptions1.yaxis.labels.style.fontWeight = this.ylabelFontWeight;
        }
      }else{
        this.eAreaChartOptions.yAxis.axisLabel.fontWeight = this.ylabelFontWeight;
      }
      }
      else if(this.line){
        if(this.isApexCharts){
        if (this.chartOptions.yaxis.length > 0) {
          (this.chartOptions.yaxis as any[]).forEach((data) => {
            data.labels.style.fontWeight = this.ylabelFontWeight;
          })
        }
        else {
          this.chartOptions.yaxis.labels.style.fontWeight = this.ylabelFontWeight;
        }
      }else{
        this.eLineChartOptions.yAxis.axisLabel.fontWeight = this.ylabelFontWeight;
      }
      }
      else if(this.sidebyside){
        if(this.isApexCharts){
        if (this.chartOptions2.yaxis.length > 0) {
          (this.chartOptions2.yaxis as any[]).forEach((data) => {
            data.labels.style.fontWeight = this.ylabelFontWeight;
          })
        }
        else {
          this.chartOptions2.yaxis.labels.style.fontWeight = this.ylabelFontWeight;
        }
      }else{
        this.eSideBySideBarChartOptions.yAxis.axisLabel.fontWeight = this.ylabelFontWeight;
      }
      }
      else if(this.stocked){
        if(this.isApexCharts){
        if (this.chartOptions6.yaxis.length > 0) {
          (this.chartOptions6.yaxis as any[]).forEach((data) => {
            data.labels.style.fontWeight = this.ylabelFontWeight;
          })
        }
        else {
          this.chartOptions6.yaxis.labels.style.fontWeight = this.ylabelFontWeight;
        }
      }else{
        this.eStackedBarChartOptions.yAxis.axisLabel.fontWeight = this.ylabelFontWeight;
      }
      }
      else if(this.barLine){
        object = {yaxis: 
          [
            {show: true,labels : {show: this.yLabelSwitch, offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }, formatter: this.formatNumber.bind(this)}},
            {show: true,opposite: true,labels : {show: this.yLabelSwitch, offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }, formatter: this.formatNumber.bind(this)}}
          ]
        };
        if(this.isApexCharts){
        if (this.chartOptions5.yaxis.length > 0) {
          (this.chartOptions5.yaxis as any[]).forEach((data) => {
            data.labels.style.fontWeight = this.ylabelFontWeight;
          })
        }
        else {
          this.chartOptions5.yaxis.labels.style.fontWeight = this.ylabelFontWeight;
        }
      }else{
        this.eBarLineChartOptions.yAxis.forEach((axis: { axisLabel: { fontWeight: number; }; }) => {
          axis.axisLabel.fontWeight = this.ylabelFontWeight; // Update Y-axis label size
        });      }
      }
      else if(this.horizentalStocked){
        object = {yaxis: {labels : {show: this.yLabelSwitch, offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }}}};
        if(this.isApexCharts){
        if (this.chartOptions7.yaxis.length > 0) {
          (this.chartOptions7.yaxis as any[]).forEach((data) => {
            data.labels.style.fontWeight = this.ylabelFontWeight;
          })
        }
        else {
          this.chartOptions7.yaxis.labels.style.fontWeight = this.ylabelFontWeight;
        }
      }else{
        this.ehorizontalStackedBarChartOptions.yAxis.axisLabel.fontWeight = this.ylabelFontWeight;
      }
      }
      else if(this.groupedChart){
        object = {yaxis: {labels : {show: this.yLabelSwitch, offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }}}};
        if(this.isApexCharts){
        if (this.chartOptions8.yaxis.length > 0) {
          (this.chartOptions8.yaxis as any[]).forEach((data) => {
            data.labels.style.fontWeight = this.ylabelFontWeight;
          })
        }
        else {
          this.chartOptions8.yaxis.labels.style.fontWeight = this.ylabelFontWeight;
        }
      }else{
        this.eGroupedBarChartOptions.yAxis.axisLabel.fontWeight = this.ylabelFontWeight;
      }
      }
      else if(this.multiLine){
        if(this.isApexCharts){
        if (this.chartOptions9.yaxis.length > 0) {
          (this.chartOptions9.yaxis as any[]).forEach((data) => {
            data.labels.style.fontWeight = this.ylabelFontWeight;
          })
        }
        else {
          this.chartOptions9.yaxis.labels.style.fontWeight = this.ylabelFontWeight;
        }
      }else{
        this.eMultiLineChartOptions.yAxis.axisLabel.fontWeight = this.ylabelFontWeight;
      }
      }
      else if(this.heatMap){
        if(this.isApexCharts){
        if (this.heatMapChartOptions.yaxis.length > 0) {
          (this.heatMapChartOptions.yaxis as any[]).forEach((data) => {
            data.labels.style.fontWeight = this.ylabelFontWeight;
          })
        }
        else {
          this.heatMapChartOptions.yaxis.labels.style.fontWeight = this.ylabelFontWeight;
        }
      }else{
        this.eHeatMapChartOptions.yAxis.axisLabel.textStyle.fontWeight = this.ylabelFontWeight;
      }
      }
      if(this.isApexCharts){
      this.updateChart(object);
      }else{
        this.updateEchartOptions();
      }
    }
    measuresColorChange(event:any){
      if (this.selectedElement) {
        this.selectedElement.style.border = 'none';
      }
        const element = event.target as HTMLElement;
        this.selectedElement = event.target as HTMLElement;
        this.selectedElement.style.border = '2px solid #2392c1';
        const color = window.getComputedStyle(element).backgroundColor;
        if(this.bar){
          this.eBarChartOptions.yAxis.axisLabel.color = color;
        }
        if(this.line){
          this.eLineChartOptions.yAxis.axisLabel.color = color;
        }
        if(this.area){
          this.eAreaChartOptions.yAxis.axisLabel.color = color;
        }
        if(this.sidebyside){
          this.eSideBySideBarChartOptions.yAxis.axisLabel.color = color;
        }
        if(this.stocked){
          this.eStackedBarChartOptions.yAxis.axisLabel.color = color;
        }
        if(this.barLine){
          this.eBarLineChartOptions.yAxis.forEach((axis: { axisLabel: { color: any; }; }) => {
            axis.axisLabel.color = color; // Update Y-axis label size
          });
        }
        if(this.horizentalStocked){
          this.ehorizontalStackedBarChartOptions.yAxis.axisLabel.color = color;
        }
        if(this.multiLine){
          this.eMultiLineChartOptions.yAxis.axisLabel.color = color;
        }
        if(this.grouped){
          this.eGroupedBarChartOptions.yAxis.axisLabel.color = color;
        }
        if(this.heatMap){
          this.eHeatMapChartOptions.yAxis.axisLabel.textStyle.color = color;
        }
        this.updateEchartOptions();
    }

    // updateChart(heatMap?{dataLabels:{formatter: this.formatNumber.bind(this)}}:{ yaxis: {labels: {formatter: this.formatNumber.bind(this)}}})
    updateNumberFormat(){
      let object;
      if(this.isApexCharts){
        if(this.heatMap){
          object = {dataLabels:{formatter: this.formatNumber.bind(this)}};
        }
        else if(this.funnel){
          object = {dataLabels:{formatter: (val: any, opts: any) => {
            const category = opts.w.config.xaxis.categories[opts.dataPointIndex];
            const formattedValue = this.formatNumber(val);
            return `${category}: ${formattedValue}`;
        }}};
        }
        else if(this.horizentalStocked || this.grouped){
          object = { xaxis: {labels: {formatter: this.formatNumber.bind(this)}}};
        }
        else if(this.barLine){
          object = {yaxis: 
            [
              {show: true,labels : {offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }, formatter: this.formatNumber.bind(this)}},
              {show: true,opposite: true,labels : {offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }, formatter: this.formatNumber.bind(this)}}
            ]
          };
        }
        else{
          object = {yaxis: {labels : {offsetY : (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)), style: { fontFamily: this.yLabelFontFamily,fontSize: this.yLabelFontSize, fontWeight: this.ylabelFontWeight }, formatter: this.formatNumber.bind(this)}}};
          // object = { yaxis: {labels: {formatter: this.formatNumber.bind(this)}}};
        }
        this.updateChart(object);
      }
      else if(this.isEChatrts){
        if(this.bar){
          this.eBarChartOptions.series[0].label.formatter = (params:any) => this.formatNumber(params.value);
          this.eBarChartOptions.yAxis.axisLabel.formatter = (value:any) => this.formatNumber(value);
        } else if(this.line){
          this.eLineChartOptions.series[0].label.formatter = (params:any) => this.formatNumber(params.value);
          this.eLineChartOptions.yAxis.axisLabel.formatter = (value:any) => this.formatNumber(value);
        } else if(this.area){
          this.eAreaChartOptions.series[0].label.formatter = (params:any) => this.formatNumber(params.value);
          this.eAreaChartOptions.yAxis.axisLabel.formatter = (value:any) => this.formatNumber(value);
        } else if(this.pie){
          this.ePieChartOptions.series[0].label.formatter = (params:any) => this.formatNumber(params.value);
          this.ePieChartOptions.yAxis.axisLabel.formatter = (value:any) => this.formatNumber(value);
        } else if(this.donut){
          this.eDonutChartOptions.series[0].label.formatter = (params:any) => this.formatNumber(params.value);
          this.eDonutChartOptions.yAxis.axisLabel.formatter = (value:any) => this.formatNumber(value);
        } else if(this.sidebyside){
          this.eSideBySideBarChartOptions.series.forEach((data : any)=>{
            data.label.formatter = (params:any) => this.formatNumber(params.value);
          })
          // this.eSideBySideBarChartOptions.series.label.formatter = (params:any) => this.formatNumber(params.value);
          this.eSideBySideBarChartOptions.yAxis.axisLabel.formatter = (value:any) => this.formatNumber(value);
        } else if(this.stocked){
          this.eStackedBarChartOptions.series.forEach((data : any)=>{
            data.label.formatter = (params:any) => this.formatNumber(params.value);
          })
          // this.eStackedBarChartOptions.series.label.formatter = (params:any) => this.formatNumber(params.value);
          this.eStackedBarChartOptions.yAxis.axisLabel.formatter = (value:any) => this.formatNumber(value);
        } else if(this.barLine){
          this.eBarLineChartOptions.series.forEach((data : any)=>{
            data.label.formatter = (params:any) => this.formatNumber(params.value);
          })
          // this.eBarLineChartOptions.series.label.formatter = (params:any) => this.formatNumber(params.value);
          this.eBarLineChartOptions.yAxis[0].axisLabel.formatter = (value:any) => this.formatNumber(value);
          this.eBarLineChartOptions.yAxis[1].axisLabel.formatter = (value:any) => this.formatNumber(value);
        } else if(this.horizentalStocked){
          this.ehorizontalStackedBarChartOptions.series.forEach((data : any)=>{
            data.label.formatter = (params:any) => this.formatNumber(params.value);
          })
          // this.ehorizontalStackedBarChartOptions.series.label.formatter = (params:any) => this.formatNumber(params.value);
          this.ehorizontalStackedBarChartOptions.xAxis.axisLabel.formatter = (value:any) => this.formatNumber(value);
        } else if(this.grouped){
          this.eGroupedBarChartOptions.series.forEach((data : any)=>{
            data.label.formatter = (params:any) => this.formatNumber(params.value);
          })
          // this.eGroupedBarChartOptions.series.label.formatter = (params:any) => this.formatNumber(params.value);
          this.eGroupedBarChartOptions.xAxis.axisLabel.formatter = (value:any) => this.formatNumber(value);
        } else if(this.multiLine){
          this.eMultiLineChartOptions.series.forEach((data : any)=>{
            data.label.formatter = (params:any) => this.formatNumber(params.value);
          })
          // this.eMultiLineChartOptions.series.label.formatter = (params:any) => this.formatNumber(params.value);
          this.eMultiLineChartOptions.yAxis.axisLabel.formatter = (value:any) => this.formatNumber(value);
        } else if(this.radar){
          this.eRadarChartOptions.series.forEach((data : any)=>{
            data.data.forEach((measure:any)=>{
              measure.label.formatter = (params:any) => this.formatNumber(params.value);
            })
          })
          // this.eRadarChartOptions.series.label.formatter = (params:any) => this.formatNumber(params.value);
          // this.eRadarChartOptions.yAxis.axisLabel.formatter = (value:any) => this.formatNumber(value);
        } else if(this.heatMap){
          this.eHeatMapChartOptions.series.forEach((data : any)=>{
            data.label.formatter = (params:any) => this.formatNumber(params.value[2]);
          })
          // this.eHeatMapChartOptions.series.label.formatter = (params:any) => this.formatNumber(params.value);
        } else if(this.funnel){
          this.eFunnelChartOptions.series.forEach((data : any)=>{
            data.label.formatter = (params:any) => {
              const formattedValue = this.formatNumber(params.value);
              return `${params.name}: ${formattedValue}`;
          };
          })
          // this.eFunnelChartOptions.series.label.formatter = (params:any) => this.formatNumber(params.value);
          // this.eFunnelChartOptions.yAxis.axisLabel.formatter = (value:any) => this.formatNumber(value);
        }
        this.updateEchartOptions();
      }3
    }
    fetchCalculatedFields(id : any){
      this.workbechService.fetchCalculatedFields(id).subscribe({
        next: (response: any) => {
          this.calculatedFieldId = id;
          this.isEditCalculatedField = true;
          this.calculatedFieldLogic = response[0].cal_logic;
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
            this.calculatedFieldLogic = 'AVG("' + tableName + '"."' + columnName + ')';
          }
          break; 
        case 'count':
          hasContentInsideParentheses = /\(.*[^\s)]\)/.test(this.calculatedFieldLogic);
          if (hasContentInsideParentheses) {
            let newString = '"' + tableName + '"."' + columnName + '")';
            this.calculatedFieldLogic = this.calculatedFieldLogic.replace(/\)\s*$/, ` ${newString})`);
          } else {
            this.calculatedFieldLogic = 'COUNT("' + tableName + '"."' + columnName + ')';
          }
        break; 
        case 'countd':
          hasContentInsideParentheses = /\(.*[^\s)]\)/.test(this.calculatedFieldLogic);
          if (hasContentInsideParentheses) {
            let newString = '"' + tableName + '"."' + columnName + '")';
            this.calculatedFieldLogic = this.calculatedFieldLogic.replace(/\)\s*$/, ` ${newString})`);
          } else {
            this.calculatedFieldLogic = 'COUNT( DISTINCT "' + tableName + '"."' + columnName + ')';
          }
        break;
        case 'max':
          hasContentInsideParentheses = /\(.*[^\s)]\)/.test(this.calculatedFieldLogic);
          if (hasContentInsideParentheses) {
            let newString = '"' + tableName + '"."' + columnName + '")';
            this.calculatedFieldLogic = this.calculatedFieldLogic.replace(/\)\s*$/, ` ${newString})`);
          } else {
            this.calculatedFieldLogic = 'MAX("' + tableName + '"."' + columnName + ')';
          }
        break; 
        case 'min':
          hasContentInsideParentheses = /\(.*[^\s)]\)/.test(this.calculatedFieldLogic);
          if (hasContentInsideParentheses) {
            let newString = '"' + tableName + '"."' + columnName + '")';
            this.calculatedFieldLogic = this.calculatedFieldLogic.replace(/\)\s*$/, ` ${newString})`);
          } else {
            this.calculatedFieldLogic = 'MIN("' + tableName + '"."' + columnName + ')';
          }
        break; 
        case 'sum':
          hasContentInsideParentheses = /\(.*[^\s)]\)/.test(this.calculatedFieldLogic);
          if (hasContentInsideParentheses) {
            let newString = '"' + tableName + '"."' + columnName + '")';
            this.calculatedFieldLogic = this.calculatedFieldLogic.replace(/\)\s*$/, ` ${newString})`);
          } else {
            this.calculatedFieldLogic = 'SUM("' + tableName + '"."' + columnName + ')';
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
          if(!this.validateFormula(/^ABS\("([a-zA-Z0-9_]+)"\."([a-zA-Z0-9_\(\)]+)"\)$/)){
            this.isValidCalculatedField = false;
            this.validationMessage = 'Invalid Syntax';
            return false;
          } else{
            this.isValidCalculatedField = true;
            return true;
          }

        break; 
        case 'ceiling':
          if(!this.validateFormula(/^CEILING\("([a-zA-Z0-9_]+)"\."([a-zA-Z0-9_\(\)]+)"\)$/)){
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
        if(!this.validateFormula(/^FLOOR\("([a-zA-Z0-9_]+)"\."([a-zA-Z0-9_\(\)]+)"\)$/)){
          this.isValidCalculatedField = false;
          this.validationMessage = 'Invalid Syntax';
        }
          else{
            this.isValidCalculatedField = true;
            return true;
          }
        break; 
        case 'round':
          if(!this.validateFormula(/^ROUND\("([a-zA-Z0-9_]+)"\."([a-zA-Z0-9_\(\)]+)"\)$/)){
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
        if(!this.validateFormula(/^LEFT\(\s*("[a-zA-Z0-9_]+"\.\"[a-zA-Z0-9_\(\)\[\]]+\")\s*,\s*(\d+)\s*\)$/)){
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
        if(!this.validateFormula(/^RIGHT\(\s*("[a-zA-Z0-9_]+"\.\"[a-zA-Z0-9_\(\)\[\]]+\")\s*,\s*(\d+)\s*\)$/)){
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
          if(!this.validateFormula(/^LENGTH\("([a-zA-Z0-9_]+)"\."([a-zA-Z0-9_\(\)]+)"\)$/)){
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
          if(!this.validateFormula(/^TRIM\("([a-zA-Z0-9_]+)"\."([a-zA-Z0-9_\(\)]+)"\)$/)){
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
          if(!this.validateFormula(/^UPPER\("([a-zA-Z0-9_]+)"\."([a-zA-Z0-9_\(\)]+)"\)$/)){
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
          if(!this.validateFormula(/^LOWER\("([a-zA-Z0-9_]+)"\."([a-zA-Z0-9_\(\)]+)"\)$/)){
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
        if(!this.validateFormula(/^REPLACE\(\s*"([^"]+)"\.\"([^"]+)\"\s*,\s*\"([^\"]*)\"\s*,\s*\"([^\"]*)\"\s*\)$/)){
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
      this.selectedElement.style.border = '2px solid #2392c1';
      this.tableDataFontColor = window.getComputedStyle(element).backgroundColor;
    }
    headerColorChange(event:any){
      if (this.selectedElement) {
        this.selectedElement.style.border = 'none';
      }
      const element = event.target as HTMLElement;
      this.selectedElement = event.target as HTMLElement;
      this.selectedElement.style.border = '2px solid #2392c1';
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
}