import { ChangeDetectorRef, Component, ElementRef, EventEmitter, input, Input, Output, SimpleChanges, ViewChild } from '@angular/core';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { NgSelectModule } from '@ng-select/ng-select';
import * as echarts from 'echarts';
import { NgxEchartsDirective } from 'ngx-echarts';
import { NgxEchartsModule } from 'ngx-echarts';
import { SharedModule } from '../../../shared/sharedmodule';
import _, { inRange } from 'lodash';
import { fontFamily } from 'html2canvas/dist/types/css/property-descriptors/font-family';
import { fontWeight } from 'html2canvas/dist/types/css/property-descriptors/font-weight';
import { lastValueFrom } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { position } from 'html2canvas/dist/types/css/property-descriptors/position';
import { bottom } from '@popperjs/core';

interface Dimension {
  name: string;
  values: string[];
}
@Component({
  selector: 'app-insight-echart',
  standalone: true,
  imports: [SharedModule, NgxEchartsModule, NgSelectModule,NgbModule,
    NgxEchartsModule
    ],
  templateUrl: './insight-echart.component.html',
  styleUrl: './insight-echart.component.scss'
})
export class InsightEchartComponent {
  @Input() chartsRowData: any; 
  @Input() isZoom: any;
  @Input() chartsColumnData: any;
  @Input() chartType!:string;
  @Input() dualAxisColumnData:any;
  @Input() dualAxisRowData:any;
  @Input() donutSize:any;
  @Input() radarRowData:any;
  @Input() displayUnits:any;
  @Input() decimalPlaces:any;
  @Input() dataLabelsFontPosition:any;
  @Input() backgroundColor:any
  @Input() xlabelAlignment:any;
  @Input() xGridColor:any;
  @Input() xGridSwitch:any;
  @Input() xLabelColor:any;
  @Input() xLabelSwitch:any;
  @Input() xLabelFontFamily:any;
  @Input() xLabelFontSize:any;
  @Input() xlabelFontWeight:any;
  @Input() yLabelColor:any;
  @Input() yLabelSwitch:any;
  @Input() yGridColor:any;
  @Input() yGridSwitch:any;
  @Input() color:any;
  @Input() dataLabels:any;
  @Input() legendSwitch:any
  @Input() ylabelFontWeight:any;
  @Input() yLabelFontSize:any;
  @Input() yLabelFontFamily:any;
  @Input() dataLabelsFontSize:any;
  @Input() dataLabelsFontFamily:any;
  @Input() dataLabelsColor:any;
  @Input() barColor:any;
  @Input() lineColor:any;
  @Input() measureColor:any;
  @Input() dimensionColor:any;
  @Input() legendsAllignment:any
  @Input() prefix : any;
  @Input() suffix : any;
  @Input() donutDecimalPlaces :any;
  @Input() isBold:any;
  @Input() sortType : any;
  @Input() dimensionAlignment : any;
  @Input() dataLabelsBarFontPosition:any;
  @Input() dataLabelsLineFontPosition:any;
  @Input() isSheetSaveOrUpdate : any;
  @Input() drillDownIndex : any;
  @Input() draggedDrillDownColumns : any;
  @Input() drillDownObject : any;
  @Input() selectedColorScheme :any;
  @Input() topLegend:any;
  @Input() rightLegend:any;
  @Input() bottomLegend:any;
  @Input() legendOrient:any;
  @Input() leftLegend:any;
  @Input() isDistributed : any;
  @Output() saveOrUpdateChart = new EventEmitter<object>();
  @Output() setDrilldowns = new EventEmitter<object>();

  width: string = '100%'; // Width of the chart
  height: string = '400px'; // Height of the chart
  @ViewChild('chartContainer', { static: true }) chartContainer!: ElementRef;
  private chartInstance!: echarts.ECharts;
  // @ViewChild('NgxEchartsDirective', { static: true }) chartDirective!: NgxEchartsDirective; 
     formattedData : any[] = [];

  series: any[] = [];
  chartOptions: any = {};
  constructor(private cdr: ChangeDetectorRef,private http: HttpClient){}

 
  // ngAfterViewInit() {
  //   this.chartInstance = echarts.init(this.chartContainer.nativeElement);
  //   this.updateChart();
  // }

  ngAfterViewInit(): void {
    this.initChart(); // Initialize the chart after the view is loaded
    this.cdr.detectChanges();

  }

  private initChart(): void {
    if (this.chartContainer?.nativeElement) {
      // Initialize the ECharts instance
      this.chartInstance = echarts.init(this.chartContainer.nativeElement);

      // Apply initial options
      this.updateChartTest();
      if(this.chartType === 'map'){
        this.chartInstance.on('click', (event) => this.handleChartClick(event));
      }
      else{
        this.chartInstance.on('click', this.onChartClick.bind(this));
      }
    }
    // const container = document.querySelector('.chart-container') as HTMLElement;
    // this.chartInstance = echarts.init(container);
    // this.updateChart();
  }

  updateChartTest(){
    if(this.chartType === 'map'){
      this.http.get('./assets/maps/world.json').subscribe((geoJson: any) => {
        echarts.registerMap('world', geoJson);
        this.chartInstance?.setOption(this.chartOptions,true);
      });
    }
    else{
      this.chartInstance?.setOption(
        this.chartOptions,true);
    }
  }

  updateChart() {
    if (this.chartInstance) {
      let obj = this.isZoom ? [{
        type: 'slider',
        show: true
      }] : [{
        type: 'slider',
        show: false
      }]
      this.chartOptions['dataZoom'] = obj;
      this.chartInstance?.setOption(
        this.chartOptions,true);
    }
  }
  ngOnDestroy(): void {
    if (this.chartInstance) {
      this.chartInstance.dispose(); // Dispose of the chart instance to avoid memory leaks
    }
  }

  barChart(){
    this.chartOptions = {
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
        formatter:(params:any) => params[0].name + " : " +  this.formatNumber(params[0].data) 
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
          color:this.dimensionColor,
          // align: this.xlabelAlignment,// Hide xAxis labels
          interval: 0, // Show all labels
          padding: [10, 0, 10, 0],
          align: this.dimensionAlignment,
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
          color:this.measureColor,
          rotate:0,
          formatter: function(value:any) {
            return value.length > 5 ? value.substring(0, 2) + '...' : value; // Truncate long labels
        }
        // formatter:(params:any) => this.formatNumber(params.value) 
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
            position: this.dataLabelsFontPosition,
            align:'center',
            fontFamily:this.dataLabelsFontFamily,
            fontSize:this.dataLabelsFontSize,
            fontWeight:this.isBold ? 700 : 400,
            color:this.dataLabelsColor,
            formatter:(params:any) => this.formatNumber(params.value) 
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
flattenDimensions(dimensions: Dimension[]): string[] {
  const numCategories = Math.max(...dimensions.map(dim => dim.values.length));
  return Array.from({ length: numCategories }, (_, index) => {
    return dimensions.map(dim => dim.values[index] === null ? 'null' : dim.values[index] || '').join(',');
  });
}
funnelchart(){
  const dimensions: Dimension[] = this.dualAxisColumnData;
    const categories = this.flattenDimensions(dimensions);
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
  this.chartOptions = {
    color: this.isDistributed ? this.selectedColorScheme : this.color,
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
          position:this.dataLabelsFontPosition,
          fontFamily:this.dataLabelsFontFamily,
          fontSize:this.dataLabelsFontSize,
          fontWeight:this.isBold ? 700 : 400,
          color:this.dataLabelsColor,
          formatter: (params: any) => {
            const formattedValue = this.formatNumber(params.value);
            return `${params.name}: ${formattedValue}`;
          }
        },
      },
    ],
  };
}
stackedChart(){
  const dimensions: Dimension[] = this.dualAxisColumnData;
  const categories = this.flattenDimensions(dimensions);
  let yaxisOptions = _.cloneDeep(this.dualAxisRowData);
  yaxisOptions.forEach((bar : any)=>{
  bar["type"]="bar";
  bar["stack"]="total";
  });
  this.chartOptions = {
    backgroundColor: this.backgroundColor,
    color:this.selectedColorScheme,
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
          color: this.yGridColor
        }, show: this.yGridSwitch
      },
      axisLine: {
        lineStyle: {
          color: this.yLabelColor,
        },
      },
      axisLabel: {
        show: this.yLabelSwitch,
        fontFamily: this.yLabelFontFamily,
        fontSize: this.yLabelFontSize,
        fontWeight: this.ylabelFontWeight,
        color:this.measureColor,

        // align: this.ylabelAlignment// Hide xAxis labels
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
        color: this.dimensionColor,
        align: this.dimensionAlignment
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
          position:this.dataLabelsFontPosition, // Position of the labels (e.g., 'top', 'inside', etc.)
          //color:'#000', // Customize label color (default black)
          // fontSize:12, // Customize label font size
          // fontWeight:'bold', // Customize label font weight
          // fontFamily:'Helvetica, Arial, sans-serif' // Use custom font family if needed
          fontFamily:this.dataLabelsFontFamily,
          fontSize:this.dataLabelsFontSize,
          fontWeight:this.isBold ? 700 : 400,
          color:this.dataLabelsColor,
          formatter:(params:any) => this.formatNumber(params.value) 
      }
  })),        

  };
}
sidebySide(){
  const dimensions: Dimension[] = this.dualAxisColumnData;
  const categories = this.flattenDimensions(dimensions);
  let yaxisOptions = _.cloneDeep(this.dualAxisRowData);
  yaxisOptions.forEach((bar : any)=>{
  bar["type"]="bar";
  });
  this.chartOptions = {
    backgroundColor: this.backgroundColor,
    color:this.selectedColorScheme,
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
        show: this.yGridSwitch, // Always show the grid lines
        lineStyle: {
          color: this.yGridColor, // Replace with a test color
          width: 1, // Set a specific width
          type: 'solid', // Solid, dashed, or dotted line
        },
      },
      axisLine: {
        lineStyle: {
          color: this.yLabelColor,
        },
      },
      axisLabel: {
        show: this.yLabelSwitch,
        fontFamily: this.yLabelFontFamily,
        fontSize: this.yLabelFontSize,
        fontWeight: this.ylabelFontWeight,
        color:this.measureColor,
        // align: this.yla// Hide xAxis labels
      }
    },
    toggleGridLines: true,
    xAxis: {
      type: 'category',
      data: categories,
      nameLocation:this.xlabelAlignment,
      axisLine: {
        lineStyle: {
          color: this.xLabelColor
        }
      },
      axisLabel: {
        show: this.xLabelSwitch,
        fontFamily: this.xLabelFontFamily,
        fontSize: this.xLabelFontSize,
        fontWeight: this.xlabelFontWeight,
        color:this.dimensionColor,
        align: this.dimensionAlignment
      },
      splitLine: {
        lineStyle: {
          color: this.xGridColor
        },
        show: this.xGridSwitch
      }
    },
    series: yaxisOptions.map((series: any) => ({
      ...series,
      label: {
          show: true, // Enable data labels
          position: this.dataLabelsFontPosition, // Position of the labels (e.g., 'top', 'inside', etc.)
          // color: '#000', // Customize label color
          // fontSize: 12, // Customize label font size
          // fontWeight: 'bold', // Customize label font weight
          // fontFamily: 'Helvetica, Arial, sans-serif' // Use custom font family if needed
          fontFamily:this.dataLabelsFontFamily,
          fontSize:this.dataLabelsFontSize,
          fontWeight:this.isBold ? 700 : 400,
          color:this.dataLabelsColor,
          formatter:(params:any) => this.formatNumber(params.value)
      }
  })),
  };
}
hgroupedChart(){
  const dimensions: Dimension[] = this.dualAxisColumnData;
  const categories = this.flattenDimensions(dimensions);
  let yaxisOptions = _.cloneDeep(this.dualAxisRowData);
  yaxisOptions.forEach((bar : any)=>{
  bar["type"]="bar";
  });
  this.chartOptions = {
    backgroundColor: this.backgroundColor,
    color:this.selectedColorScheme,
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
        color: this.dimensionColor,
        // align: this.xlabelAlignment,// Hide xAxis labels
        align: this.dimensionAlignment
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
        fontFamily: this.yLabelFontFamily,
        fontSize: this.yLabelFontSize,
        fontWeight: this.ylabelFontWeight,
        color:this.measureColor,

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
          // color:'#000', // Default label color (can be updated)
          // fontSize:this.xLabelFontSize, // Default label font size
          // fontWeight:'bold', // Default label font weight
          // fontFamily:this.xLabelFontFamily // Default label font family
          fontFamily:this.dataLabelsFontFamily,
          fontSize:this.dataLabelsFontSize,
          fontWeight:this.isBold ? 700 : 400,
          color:this.dataLabelsColor,
          formatter:(params:any) => this.formatNumber(params.value)
      }
  })),

  };
}
hstackedChart(){
  const dimensions: Dimension[] = this.dualAxisColumnData;
  const categories = this.flattenDimensions(dimensions);
  let yaxisOptions = _.cloneDeep(this.dualAxisRowData);
  yaxisOptions.forEach((bar : any)=>{
  bar["type"]="bar";
  bar["stack"]="total";
  });
  this.chartOptions = {
    backgroundColor: this.backgroundColor,
    color:this.selectedColorScheme,
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
        color: this.dimensionColor,
        // align: this.xlabelAlignment// Hide xAxis labels
        align: this.dimensionAlignment
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
        fontFamily: this.yLabelFontFamily,
        fontSize: this.yLabelFontSize,
        fontWeight: this.ylabelFontWeight,
        color:this.measureColor,

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
          // color:'#000', // Default label color (can be updated)
          // fontSize:this.xLabelFontSize, // Default label font size
          // fontWeight:'bold', // Default label font weight
          // fontFamily:this.xLabelFontFamily // Default label font family
          fontFamily:this.dataLabelsFontFamily,
          fontSize:this.dataLabelsFontSize,
          fontWeight:this.isBold ? 700 : 400,
          color:this.dataLabelsColor,
          formatter:(params:any) => this.formatNumber(params.value)
      }
  })),
    

  };
  console.log('Categories:', categories);
console.log('Y Axis Options:', yaxisOptions);
}
areaChart(){
  this.chartOptions = {
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
      formatter:(params:any) => params[0].name + ' : ' + this.formatNumber(params[0].value) 
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
        color: this.dimensionColor,
        // align: this.xlabelAlignment// Hide xAxis labels
        align: this.dimensionAlignment
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
        color:this.measureColor,

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
        label: { show: true,
          fontFamily:this.dataLabelsFontFamily,
          fontSize:this.dataLabelsFontSize,
          fontWeight:this.isBold ? 700 : 400,
          color:this.dataLabelsColor,
          position:this.dataLabelsFontPosition,
          formatter:(params:any) => this.formatNumber(params.value) 
        },
        type: 'line',
        data: this.chartsRowData,
        areaStyle: {}
      },
    ],
    color: this.color

  };
console.log(this.chartsRowData,this.chartsColumnData,'areachart')

}
lineChart(){
  this.chartOptions = {
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
      formatter:(params:any) => params[0].name + ' : ' + this.formatNumber(params[0].value) 
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
        color: this.dimensionColor,
        // align: this.xlabelAlignment// Hide xAxis labels
        align: this.dimensionAlignment
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
        color:this.measureColor,

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
        label: { show: true,
          fontFamily:this.dataLabelsFontFamily,
          fontSize:this.dataLabelsFontSize,
          fontWeight:this.isBold ? 700 : 400,
          color:this.dataLabelsColor,
          position:this.dataLabelsFontPosition,
          formatter:(params:any) => this.formatNumber(params.value) 
        },
        type: 'line',
        data: this.chartsRowData,
      
      },
    ],
    color: this.color

  };
}
pieChart(){
  let combinedArray = this.chartsRowData.map((value : any, index :number) => ({
    value: value,
    name: this.chartsColumnData[index]
  }));
  // let legendObject = this.setEchartLegendAlignment();
  this.chartOptions = {
    backgroundColor: this.backgroundColor,
    color:this.selectedColorScheme,
    tooltip: {
      trigger: 'item',
      formatter:(params:any) => params.name + ' : ' + this.formatNumber(params.value) 
    },
    legend: {
          bottom: this.bottomLegend, 
          left: this.leftLegend, 
          orient: this.legendOrient,
          right:this.rightLegend,
          top:this.topLegend,
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
  console.log('pieoptions',this.chartOptions)
}
donutChart(){
  let combinedArray = this.chartsRowData.map((value : any, index :number) => ({
    value: value,
    name: this.chartsColumnData[index]
  }));
  // let legendObject = this.setEchartLegendAlignment();
  this.chartOptions = {
    backgroundColor: this.backgroundColor,
    color:this.selectedColorScheme,
    tooltip: {
      trigger: 'item',
    },
    legend: {
      bottom: this.bottomLegend, 
          left: this.leftLegend, 
          orient: this.legendOrient,
          right:this.rightLegend,
          top:this.topLegend,
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
barLineChart(){
  const dimensions: Dimension[] = this.dualAxisColumnData;
  const categories = this.flattenDimensions(dimensions);
  this.chartOptions = {
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
      show: this.isZoom,
      type: 'slider'
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
          show:this.xLabelSwitch,
          color: this.xLabelColor, // Customize label color
          fontSize: this.xLabelFontSize, // Customize font size
          fontFamily: this.xLabelFontFamily, // Customize font family
          fontWeight: 'bold', // Customize font weight
          align: this.dimensionAlignment,
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
        show:this.yLabelSwitch,
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
        show:this.yLabelSwitch,
        name: 'Line Axis',
        position: 'right',
        axisLabel: {
          show:this.yLabelSwitch,
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
    series: [
      {
        name: this.dualAxisRowData[0]?.name,
        type: 'bar',
        data: this.dualAxisRowData[0]?.data,
        itemStyle:{
          color:this.barColor, // Default bar color
          
      },
        label:{
          show:true,
          fontFamily:this.dataLabelsFontFamily,
          fontSize:this.dataLabelsFontSize,
          fontWeight:this.isBold ? 700 : 400,
          position:this.dataLabelsBarFontPosition,
          align:'center',
          formatter:(params:any) => this.formatNumber(params.value) 
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
          color: this.lineColor,
          fontFamily:this.dataLabelsFontFamily,
          fontSize:this.dataLabelsFontSize,
          fontWeight:this.isBold ? 700 : 400,
        },
        data: this.dualAxisRowData[1]?.data,
        label:{
          show:true,
          fontFamily:this.dataLabelsFontFamily,
          fontSize:this.dataLabelsFontSize,
          fontWeight:this.isBold ? 700 : 400,
          position:this.dataLabelsFontPosition,
          formatter:(params:any) => this.formatNumber(params.value) 
        }
      }
    ]
  };
}
multiLineChart(){
  const dimensions: Dimension[] = this.dualAxisColumnData;
  const categories = this.flattenDimensions(dimensions);
  let yaxisOptions = _.cloneDeep(this.dualAxisRowData);
  yaxisOptions.forEach((bar : any)=>{
  bar["type"]="line";
  bar["stack"]="Total";
  });
  this.chartOptions = {
    backgroundColor: this.backgroundColor,
    color:this.selectedColorScheme,
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
        color: this.dimensionColor,
        // align: this.xlabelAlignment// Hide xAxis labels
        align: this.dimensionAlignment
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
        fontFamily: this.yLabelFontFamily,
        fontSize: this.yLabelFontSize,
        fontWeight: this.ylabelFontWeight,
        color:this.measureColor,

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
          // color:'#000', // Default label color (can be updated)
          // fontSize:this.xLabelFontSize, // Default label font size
          // fontWeight:'bold', // Default label font weight
          // fontFamily:this.xLabelFontFamily // Default label font family
          fontFamily:this.dataLabelsFontFamily,
          fontSize:this.dataLabelsFontSize,
          fontWeight:this.isBold ? 700 : 400,
          color:this.dataLabelsColor,
          formatter:(params:any) => this.formatNumber(params.value) 
      }
  })),
  };
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
  this.chartOptions = {
    backgroundColor: this.backgroundColor,
    tooltip: { trigger: "item" },
    legend: {
      bottom: 'bottom', left: 'center', orient: 'horizontal'
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
  color: this.color, // Add color array for series
  series:[
    {
        type:'radar',
        data:this.radarRowData.map((dataItem: any) => ({
            ...dataItem,
            label:{
                show:this.dataLabels,
                fontFamily:this.dataLabelsFontFamily,
                fontSize:this.dataLabelsFontSize,
                fontWeight:this.isBold ? 700 : 400,
                color:this.dataLabelsColor,
                position:this.dataLabelsFontPosition,
                formatter:(params:any) => this.formatNumber(params.value) 
            }
        }))
    }
]
  }
}
heatMapChart(){
  const dimensions: Dimension[] = this.dualAxisColumnData;
  const categories = this.flattenDimensions(dimensions);
  this.chartOptions = {
    backgroundColor: this.backgroundColor,
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
            // rotate: 45,
            textStyle: {
                color: this.xLabelColor,
                fontSize: this.xLabelFontSize,
                fontFamily: this.xLabelFontFamily,
                fontWeight: this.xlabelFontWeight,
                align: this.dimensionAlignment
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
        max : this.getMaxValue(this.dualAxisRowData),
        calculable : true,
        orient : 'horizontal',
        left : 'center',
        // bottom : '15%',
        top: '5%',
        inRange : {
          color:this.selectedColorScheme,
        }
    },
    series : [{
      name : this.dualAxisRowData,
      type : 'heatmap',
      data : this.prepareHeatmapData(this.dualAxisRowData), // Prepare your data accordingly
      label : {
          show : true,
          fontFamily:this.dataLabelsFontFamily,
          fontSize:this.dataLabelsFontSize,
          fontWeight:this.isBold ? 700 : 400,
          color:this.dataLabelsColor,
          position:this.dataLabelsFontPosition,
          formatter: (params:any) => this.formatNumber(params.value[2])
          // formatter : (params: { value: number[]; }) => this.formatNumber(params.value[2]) // Assuming value[2] holds the number to format
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
calendarChart() {
  let calendarData: any[] = [];
  let years: Set<any> = new Set();

  // Populate calendarData and collect years
  this.chartsColumnData.forEach((data: any, index: any) => {
      let formattedDate = data.split(" ")[0];
      let arr = [formattedDate, this.chartsRowData[index]];
      calendarData.push(arr);

      const year = new Date(formattedDate).getFullYear();
      years.add(year);
  });

  const minValue = this.chartsRowData.reduce((a: any, b: any) => (a < b ? a : b), Infinity);
  const maxValue = this.chartsRowData.reduce((a: any, b: any) => (a > b ? a : b), -Infinity);

  // Convert years set to array and sort it in ascending order
  let yearArray = Array.from(years).sort((a: any, b: any) => a - b);

  // Define the height for each calendar
  const calendarHeight = 120;  // Adjust height for better visibility
  const yearGap = 30;  // Reduced gap between years
  const totalHeight = (calendarHeight + yearGap) * yearArray.length;
  this.height = (totalHeight+25)+'px';

  // Create multiple calendar instances, one for each year
  let calendars = yearArray.map((year: any, idx: any) => ({
      top: idx === 0 ? 25 : ((calendarHeight + yearGap) * idx) + 25,
      range: year.toString(),
      cellSize: ['auto', 12],
      splitLine: {
          show: true,
          lineStyle: {
              color: '#000',
              width: 1
          }
      },
      yearLabel: {
        show: true,
        margin: 25,
        fontSize: 14,
        fontWeight: 'bold'
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
        show: true,
        yAxisIndex: 0,
        start: 0,  // Starting position of the scroll
        end: 50,  // The scroll window size (adjustable)
        orient: 'vertical',  // Allow vertical scrolling
        zoomLock: false,  // Disable zoom lock for flexibility
    },
    {
      type: 'inside',
      yAxisIndex: 0,
      start: 0,
      end: 50
  }
];

this.chartOptions = {
  color:this.selectedColorScheme,
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
  dataZoom: dataZoomConfig
};

  console.log(this.chartOptions,'calender');
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
mapChart(){
  let minData : number = 0;
  let maxData: number = Math.max(...this.chartsRowData);
  let result:any[] = [];

  if(!(this.draggedDrillDownColumns>0 || this.drillDownIndex>0)){
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
  }

if(this.chartsColumnData && this.chartsColumnData.length > 1){
minData= Math.min(...this.chartsRowData);
}
if(Number.isNaN(minData) || Number.isNaN(maxData)){
 minData = 0;
 maxData = 1;
}
let mapChartOptions = {
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
let barChartOptions = {
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
    nameLocation: this.xlabelAlignment,
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
      color: this.dimensionColor,
      // align: this.xlabelAlignment,// Hide xAxis labels
      interval: 0, // Show all labels
      padding: [10, 0, 10, 0],
      align: this.dimensionAlignment,
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
      show: this.yGridSwitch
    },
    axisLabel: {
      show: this.yLabelSwitch,
      fontFamily: this.yLabelFontFamily,
      fontSize: this.yLabelFontSize,
      fontWeight: this.ylabelFontWeight,
      color:this.measureColor,
      rotate:0,
      formatter: function(value:any) {
        return value.length > 5 ? value.substring(0, 2) + '...' : value; // Truncate long labels
    }
    // formatter:(params:any) => this.formatNumber(params.value) 
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
        position: this.dataLabelsFontPosition,
        align:'center',
        fontFamily:this.dataLabelsFontFamily,
        fontSize:this.dataLabelsFontSize,
        fontWeight:this.isBold ? 700 : 400,
        color: this.dataLabelsColor,
        formatter:(params:any) => this.formatNumber(params.value) 
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
this.chartOptions = this.draggedDrillDownColumns.length > 0 ? (this.drillDownIndex > 0 ? barChartOptions : mapChartOptions) : mapChartOptions
console.log(this.chartOptions);
 }
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

private updateChartOptions(): void {
  if (this.chartInstance) {
    this.chartInstance?.setOption(this.chartOptions, true); // Update chart options dynamically
  }
}

ngOnInit(){
  // this.chartInitialize()
}
chartInitialize(){
  if(this.chartType ==='bar'){
    this.barChart();
  }else if(this.chartType ==='funnel'){
  this.funnelchart();
  }
  else if(this.chartType ==='stocked'){
    this.stackedChart();
  }
  else if(this.chartType === 'sidebyside'){
    this.sidebySide();
  }
  else if(this.chartType === 'hgrouped'){
    this.hgroupedChart();
  }
  else if(this.chartType === 'hstocked'){
    this.hstackedChart();
  }
  else if(this.chartType === 'area'){
    this.areaChart();
  }
  else if (this.chartType === 'line'){
    this.lineChart();
  }
  else if(this.chartType === 'pie'){
    this.pieChart();
  }
  else if(this.chartType === 'donut'){
    this.donutChart();
  }
  else if(this.chartType === 'barline'){
    this.barLineChart();
  }
  else if(this.chartType === 'multiline'){
    this.multiLineChart();
  }
  else if(this.chartType === 'radar'){
    this.radarChart();
  }
  else if(this.chartType === 'heatmap'){
    this.heatMapChart();
  }
  else if(this.chartType === 'calendar'){
    this.calendarChart();
  }
  else if(this.chartType === 'map'){
    this.http.get('./assets/maps/world.json').subscribe((geoJson: any) => {
      echarts.registerMap('world', geoJson);
      this.chartInstance.resize();
    });
    this.mapChart();
  }
}
  // }
  resetchartoptions(){
    if (!this.chartInstance) {
      console.warn('Chart instance is not initialized.');
      return;
    }
    else{
      this.chartInitialize();
      this.chartInstance?.setOption(this.chartOptions, true); // Full reset
    }
  }
  ngOnChanges(changes: SimpleChanges) {
    if (!this.chartInstance) {
      this.chartInitialize();
    }
     if(changes['chartType']){
      this.chartInitialize();
     }
    if(changes['chartsColumnData']  || changes['dualAxisColumnData'] ){
      // if(changes['chartsColumnData']?.currentValue?.length>0 || changes['dualAxisColumnData']?.currentValue?.length>0){
        // this.updateCategories();
        this.resetchartoptions();
      // }
    }
    if(changes['chartsRowData'] || changes['dualAxisRowData'] ){
      // if(changes['chartsRowData']?.currentValue?.length>0 || changes['dualAxisRowData']?.currentValue?.length>0){
        // this.updateSeries();
        this.resetchartoptions();
      // }
    }
    if(changes['isZoom']){
      if (this.chartInstance) {

        let obj ={
          dataZoom: this.isZoom ? [
            {
              type: 'slider',
              show: true
            }] : [{
              type: 'slider',
              show: false
            }
          ]
        }
        this.chartInstance?.setOption(obj);
        this.chartOptions = { ...this.chartOptions, ...obj };
        // this.chartInstance?.setOption({
        //   dataZoom: this.isZoom ? [
        //     {
        //       type: 'slider',
        //       show: true
        //     }] : [{
        //       type: 'slider',
        //       show: false
        //     }
        //   ]
        // }
        // );
      }
    }
    if(changes['xLabelFontFamily']){
      if(this.chartInstance){
        this.xLabelFontFamilySetOptions()
      }
    }
    if(changes['xLabelFontSize']){
      if(this.chartInstance){
        this.xLabelFontSizeSetOption();
      }
    }
    if(changes['xlabelFontWeight']){
      if(this.chartInstance){
        this.xlabelFontWeightSetOption();
      }
    }
    if(changes['dimensionAlignment']){
      if(this.chartInstance){
        this.dimensionsAlignmentSetOption();
      }
    }
    if(changes['dimensionColor']){
      if(this.chartInstance){
        this.dimensionColorSetOption();
      }
    }
    if(changes['yLabelFontFamily']){
      if(this.chartInstance){
        this.yLabelFontFamilySetOptions();
      }
    }
    if(changes['yLabelFontSize']){
      if(this.chartInstance){
        this.yLabelFontSizeSetOptions();
      }
    }
    if(changes['ylabelFontWeight']){
      if(this.chartInstance){
        this.ylabelFontWeightSetOptions();
      }
    }
    if(changes['measureColor']){
      if(this.chartInstance){
        this.measureColorSetOptions();
      }
    }
    if(changes['dataLabelsFontFamily']){
      if(this.chartInstance){
        this.dataLabelsFontFamilySetOptions();
      }
    }
    if(changes['dataLabelsFontSize']){
      if(this.chartInstance){
        this.dataLabelsFontSizeSetOptions();
      }
    }
    if(changes['dataLabelsColor']){
      if(this.chartInstance){
        this.dataLabelsColorSetOptions();
      }
    }
    if(changes['dataLabelsFontPosition']){
      if(this.chartInstance){
        this.dataLabelsFontPositionSetOptions();
      }
    }
    if(changes['dataLabelsBarFontPosition']){
      if(this.chartInstance){
        this.dataLabelsBarFontPositionSetOptions();
      }
    }
    if(changes['dataLabelsLineFontPosition']){
      if(this.chartInstance){
        this.dataLabelsLineFontPositionSetOptions();
      }
    }
    if(changes['xLabelSwitch']){
      if(this.chartInstance){
        this.xLabelSwitchSetOptions();
      }
    }
    if(changes['yLabelSwitch']){
      if(this.chartInstance){
        this.yLabelSwitchSetOptions();
      }
    }
    if(changes['xGridSwitch']){
      if(this.chartInstance){
        this.xGridSwitchSetOptions();
      }
    }
    if(changes['yGridSwitch']){
      if(this.chartInstance){
        this.yGridSwitchSetOptions();
      }
    }
    if(changes['legendSwitch']){
      if(this.chartInstance){
        this.legendSwitchSetOptions();
      }
    }
    if(changes['dataLabels']){
      if(this.chartInstance){
        this.dataLabelsSetOptions();
      }
    }
    if(changes['color'] || changes['barColor'] || changes['lineColor'] || changes['selectedColorScheme'] || changes['isDistributed']){
      if(this.chartInstance){
        this.colorSetOptions();
      }
    }
    if(changes['xGridColor']){
      if(this.chartInstance){
        this.xGridColorSetOptions();
      }
    }
    if(changes['yGridColor']){
      if(this.chartInstance){
        this.yGridColorSetOptions();
      }
    }
    if(changes['backgroundColor']){
      if(this.chartInstance){
        this.backgroundColorSetOptions();
      }
    }
    if(changes['legendsAllignment']){
      if(this.chartInstance){
        this.legendsAllignmentSetOptions()
      }
    }
    if(changes['selectedColorScheme']){
      if(this.chartInstance){
        this.selectedColorSchemeSetOptions()
      }
    }
    if((changes['displayUnits'] || changes['decimalPlaces'] || changes['prefix'] || changes['suffix'] || changes['donutDecimalPlaces']) && !changes['chartType']){
      this.updateNumberFormat();
    }
    if(changes['donutSize']){
      this.donutSizeChange();
    }
    if(changes['isBold']){
      this.setDatalabelsFontWeight();
    }
    // if(this.chartType === 'bar' && changes['sortType'] && changes['sortType']?.currentValue !== 0){
    //   this.sortSeries(this.sortType);
    // }
    if(this.isSheetSaveOrUpdate){
      let object = {
        chartOptions : this.chartOptions
      }
      this.saveOrUpdateChart.emit(object);
    }
    console.log(this.chartOptions);
  }
  xLabelFontFamilySetOptions(){
    if(this.chartType !== 'heatmap'){
    let obj = {
      xAxis :{
        axisLabel :{
          fontFamily: this.xLabelFontFamily
        }
      }
    }   
    this.chartInstance?.setOption(obj);
    this.chartOptions.xAxis.axisLabel.fontFamily = this.xLabelFontFamily;
  }else if(this.chartType ==='heatmap'){
    let obj = {
      xAxis :{
        axisLabel :{
          textStyle:{
            fontFamily: this.xLabelFontFamily
          }
        }
      }
    } 
    this.chartInstance?.setOption(obj);
    this.chartOptions.xAxis.axisLabel.textStyle.fontFamily = this.xLabelFontFamily;
    
  }

  }
  xLabelFontSizeSetOption(){
    if(this.chartType === 'barline'){
    let obj ={
      xAxis :[{
        axisLabel :{
          fontSize: this.xLabelFontSize
        }
      }]
    }
    this.chartInstance?.setOption(obj);
    this.chartOptions.xAxis[0].axisLabel.fontSize = this.xLabelFontSize;

  }
  else if(this,this.chartType === 'heatmap'){
    let obj ={
      xAxis :{
        axisLabel :{
          textStyle:{
          fontSize: this.xLabelFontSize
          }
        }
      }
    }
    this.chartInstance?.setOption(obj);
    this.chartOptions.xAxis.axisLabel.textStyle.fontSize = this.xLabelFontSize;
  }
  else{
    let obj ={
      xAxis :{
        axisLabel :{
          fontSize: this.xLabelFontSize
        }
      }
    }
    this.chartInstance?.setOption(obj);
    this.chartOptions.xAxis.axisLabel.fontSize = this.xLabelFontSize;
  }
  }
  xlabelFontWeightSetOption(){
    if(this.chartType ==='barline'){
    let obj ={
      xAxis :[{
        axisLabel :{
          fontWeight: this.xlabelFontWeight
        }
      }]
    }
    this.chartInstance?.setOption(obj);
    this.chartOptions.xAxis.axisLabel.fontWeight = this.xlabelFontWeight;
  }
 else if(this.chartType === 'heatmap'){
    let obj ={
      xAxis :{
        axisLabel :{
          textStyle:{
          fontWeight: this.xlabelFontWeight
          }
        }
      }
    }
    this.chartInstance?.setOption(obj);
    this.chartOptions.xAxis.axisLabel.textStyle.fontWeight = this.xlabelFontWeight;
  }
  else{
    let obj ={
      xAxis :{
        axisLabel :{
          fontWeight: this.xlabelFontWeight
        }
      }
    }
    this.chartInstance?.setOption(obj);
    this.chartOptions.xAxis.axisLabel.fontWeight = this.xlabelFontWeight;
  }
  }
  dimensionColorSetOption(){
    if(this.chartType ==='barline'){
      let obj ={
        xAxis :[{
          axisLabel :{
            color: this.dimensionColor
          }
        }]
      }
      this.chartInstance?.setOption(obj);
      this.chartOptions.xAxis[0].axisLabel.color = this.dimensionColor;
    }
   else if(this.chartType === 'heatmap'){
      let obj ={
        xAxis :{
          axisLabel :{
            textStyle:{
              color: this.dimensionColor
            }
          }
        }
      }
      this.chartInstance?.setOption(obj);
      this.chartOptions.xAxis.axisLabel.textStyle.color = this.dimensionColor;
    }
    else{
      let obj ={
        xAxis :{
          axisLabel :{
            color: this.dimensionColor
          }
        }
      }
      this.chartInstance?.setOption(obj);
      this.chartOptions.xAxis.axisLabel.color = this.dimensionColor;
     }
  }
  yLabelFontFamilySetOptions(){
    if(this.chartType ==='barline'){
     let obj ={
      yAxis: [
        {
          axisLabel: {
            fontFamily: this.yLabelFontFamily,
          },
        },
        {
          axisLabel: {
            fontFamily: this.yLabelFontFamily, 
          },
        },
      ],
     }
      this.chartInstance?.setOption(obj);
      this.chartOptions.yAxis[0].axisLabel.fontFamily = this.yLabelFontFamily;
      this.chartOptions.yAxis[1].axisLabel.fontFamily = this.yLabelFontFamily;
    }
    else if(this.chartType === 'heatmap'){
      let obj ={
        yAxis :{
          axisLabel :{
            textStyle:{
              fontFamily: this.yLabelFontFamily
            }
          }
        }
      }
      this.chartInstance?.setOption(obj);
      this.chartOptions.yAxis.axisLabel.textStyle.fontFamily = this.yLabelFontFamily;
    }
    else{
      let obj ={
        yAxis :{
          axisLabel :{
            fontFamily: this.yLabelFontFamily
          }
        }
      }
      this.chartInstance?.setOption(obj);
      this.chartOptions.yAxis.axisLabel.fontFamily = this.yLabelFontFamily;
    }
  }
  yLabelFontSizeSetOptions(){
  if(this.chartType ==='barline'){
     let obj ={
      yAxis: [
        {
          axisLabel: {
            fontSize: this.yLabelFontSize, // Update for 'Bar Axis'
          },
        },
        {
          axisLabel: {
            fontSize: this.yLabelFontSize, // Update for 'Bar Axis'
          },
        },
      ],
     }
      this.chartInstance?.setOption(obj);
      this.chartOptions.yAxis[0].axisLabel.fontSize = this.yLabelFontSize;
      this.chartOptions.yAxis[1].axisLabel.fontSize = this.yLabelFontSize;    }
    else if(this.chartType === 'heatmap'){
      let obj ={
        yAxis :{
          axisLabel :{
            textStyle:{
              fontSize: this.yLabelFontSize
            }
          }
        }
      }
      this.chartInstance?.setOption(obj);
      this.chartOptions.yAxis.axisLabel.textStyle.fontSize = this.yLabelFontSize;
    }
    else{
      let obj ={
        yAxis :{
          axisLabel :{
            fontSize: this.yLabelFontSize
          }
        }
      }
      this.chartInstance?.setOption(obj);
      this.chartOptions.yAxis.axisLabel.fontSize = this.yLabelFontSize;
    }
  }
  ylabelFontWeightSetOptions(){
    if(this.chartType ==='barline'){
      let obj ={
       yAxis: [
         {
           axisLabel: {
            fontWeight: this.ylabelFontWeight, // Update for 'Bar Axis'
           },
         },
         {
           axisLabel: {
            fontWeight: this.ylabelFontWeight, // Update for 'Bar Axis'
           },
         },
       ],
      }
       this.chartInstance?.setOption(obj);
       this.chartOptions.yAxis[0].axisLabel.fontWeight = this.ylabelFontWeight;
       this.chartOptions.yAxis[1].axisLabel.fontWeight = this.ylabelFontWeight;
     }
     else if(this.chartType === 'heatmap'){
       let obj ={
         yAxis :{
           axisLabel :{
             textStyle:{
              fontWeight: this.ylabelFontWeight
             }
           }
         }
       }
       this.chartInstance?.setOption(obj);
       this.chartOptions.yAxis.axisLabel.textStyle.fontWeight = this.ylabelFontWeight;
      }
     else{
       let obj ={
         yAxis :{
           axisLabel :{
            fontWeight: this.ylabelFontWeight
           }
         }
       }
       this.chartInstance?.setOption(obj);
       this.chartOptions.yAxis.axisLabel.fontWeight = this.ylabelFontWeight;
     }
  }
  measureColorSetOptions(){
    if(this.chartType ==='barline'){
      let obj ={
       yAxis: [
         {
           axisLabel: {
             color: this.measureColor, // Update for 'Bar Axis'
           },
         },
         {
           axisLabel: {
             color: this.measureColor, // Update for 'Bar Axis'
           },
         },
       ],
      }
       this.chartInstance?.setOption(obj);
       this.chartOptions.yAxis[0].axisLabel.color = this.measureColor;
       this.chartOptions.yAxis[1].axisLabel.color = this.measureColor;     }
     else if(this.chartType === 'heatmap'){
       let obj ={
         yAxis :{
           axisLabel :{
             textStyle:{
               color: this.measureColor
             }
           }
         }
       }
       this.chartInstance?.setOption(obj);
       this.chartOptions.yAxis.axisLabel.textStyle.color = this.measureColor
     }
     else{
       let obj ={
         yAxis :{
           axisLabel :{
             color: this.measureColor
           }
         }
       }
       this.chartInstance?.setOption(obj);
       this.chartOptions.yAxis.axisLabel.color = this.measureColor;
     }
  }
  dataLabelsFontFamilySetOptions(){
    if(this.chartType ==='barline'){
      let obj ={
       series: [
         {
           label: {
            fontFamily: this.dataLabelsFontFamily, // Update for 'Bar Axis'
           },
         },
         {
          label: {
            fontFamily: this.dataLabelsFontFamily,
           },
         },
       ],
      }
       this.chartInstance?.setOption(obj);
       this.chartOptions.series[0].label.fontFamily = this.dataLabelsFontFamily;
       this.chartOptions.series[1].label.fontFamily = this.dataLabelsFontFamily  `1`;
      }
     else if(this.chartType === 'radar'){
      this.chartOptions.series[0].data.forEach((dataItem: { label: { fontFamily: any; }; }) => {
        if (dataItem.label) { // Ensure label exists before updating
            dataItem.label.fontFamily = this.dataLabelsFontFamily;
        }
    });
       this.chartInstance?.setOption(this.chartOptions,true);
     }
     else if(this.chartType === 'multiline' || this.chartType === 'hgrouped' || this.chartType === 'hstocked' || this.chartType === 'stocked' || this.chartType === 'sidebyside'){
      this.chartOptions.series.forEach((series: { label: { fontFamily: any; }; }) => {
        series.label.fontFamily = this.dataLabelsFontFamily; 
    });
    this.chartInstance?.setOption(this.chartOptions,true)
     }
     else{
       let obj ={
         series :[
          {
           label :{
            fontFamily: this.dataLabelsFontFamily
           }
         }]
       }
       this.chartInstance?.setOption(obj);
       this.chartOptions.series[0].label.fontFamily = this.dataLabelsFontFamily;
     }
  }
  dataLabelsFontSizeSetOptions(){
    if(this.chartType ==='barline'){
      let obj ={
       series: [
         {
           label: {
            fontSize: this.dataLabelsFontSize, // Update for 'Bar Axis'
           },
         },
         {
          label: {
            fontSize: this.dataLabelsFontSize,
           },
         },
       ],
      }
       this.chartInstance?.setOption(obj);
       this.chartOptions.series[0].label.fontSize = this.dataLabelsFontSize;
       this.chartOptions.series[1].label.fontSize = this.dataLabelsFontSize;
      }
     else if(this.chartType === 'radar'){
      this.chartOptions.series[0].data.forEach((dataItem: { label: { fontSize: any; }; }) => {
        if (dataItem.label) { // Ensure label exists before updating
            dataItem.label.fontSize = this.dataLabelsFontSize;
        }
    });
       this.chartInstance?.setOption(this.chartOptions,true)
     }
     else if(this.chartType === 'multiline' || this.chartType === 'hgrouped' || this.chartType === 'hstocked' || this.chartType === 'stocked' || this.chartType === 'sidebyside'){
      this.chartOptions.series.forEach((series: { label: { fontSize: any; }; }) => {
        series.label.fontSize = this.dataLabelsFontSize; 
    });
    this.chartInstance?.setOption(this.chartOptions,true)
     }
     else{
       let obj ={
         series :[
          {
           label :{
            fontSize: this.dataLabelsFontSize
           }
         }]
       }
       this.chartInstance?.setOption(obj);
       this.chartOptions.series[0].label.fontSize = this.dataLabelsFontSize
      //  this.chartOptions = { ...this.chartOptions, ...obj };
     }
  }
  dataLabelsColorSetOptions(){
    if(this.chartType ==='barline'){
      let obj ={
       series: [
         {
           label: {
            color: this.dataLabelsColor, // Update for 'Bar Axis'
           },
         },
         {
          label: {
            color: this.dataLabelsColor,
           },
         },
       ],
      }
       this.chartInstance?.setOption(obj);
       this.chartOptions.series[0].label.color = this.dataLabelsColor;
       this.chartOptions.series[1].label.color = this.dataLabelsColor;     }
     else if(this.chartType === 'radar'){
      this.chartOptions.series[0].data.forEach((dataItem: { label: { color: string; }; }) => {
        dataItem.label.color = this.dataLabelsColor;
    });
       this.chartInstance?.setOption(this.chartOptions,true)
     }
     else if(this.chartType === 'multiline' || this.chartType === 'hgrouped' || this.chartType === 'hstocked' || this.chartType === 'stocked' || this.chartType === 'sidebyside'){
      this.chartOptions.series.forEach((series: { label: { color: any; }; }) => {
        series.label.color = this.dataLabelsColor; 
    });
    this.chartInstance?.setOption(this.chartOptions,true)
     }
     else{
       let obj ={
         series :[
          {
           label :{
            color: this.dataLabelsColor
           }
         }]
       }
       this.chartInstance?.setOption(obj);
       this.chartOptions.series[0].label.color = this.dataLabelsColor
     }
  }
  dataLabelsFontPositionSetOptions(){
      if(this.chartType === 'radar'){
      this.chartOptions.series[0].data.forEach((dataItem: { label: { position: any; }; }) => {
        if (dataItem.label) { // Ensure label exists before updating
            dataItem.label.position = this.dataLabelsFontPosition;
        }
    });
       this.chartInstance?.setOption(this.chartOptions,true)
     }
     else if(this.chartType === 'multiline' || this.chartType === 'hgrouped' || this.chartType === 'hstocked' || this.chartType === 'stocked' || this.chartType === 'sidebyside'){
      this.chartOptions.series.forEach((series: { label: { position: any; }; }) => {
        series.label.position = this.dataLabelsFontPosition; 
    });
    this.chartInstance?.setOption(this.chartOptions,true)
     }
     else if(this.chartType ==='funnel'){
      if(this.dataLabelsFontPosition === 'center'){
        let obj ={
          series :[
           {
            label :{
             position: 'inside'
            }
          }]
        }
        this.chartInstance?.setOption(obj);
        this.chartOptions.series[0].label.position = 'inside' ;
      } else if(this.dataLabelsFontPosition === 'top'){
        let obj ={
          series :[
           {
            label :{
             position: 'right'
            }
          }]
        }
        this.chartInstance?.setOption(obj);
        this.chartOptions.series[0].label.position = 'right' ;
      }
      else if(this.dataLabelsFontPosition === 'bottom'){
        let obj ={
          series :[
           {
            label :{
             position: 'left'
            }
          }]
        }
        this.chartInstance?.setOption(obj);
        this.chartOptions.series[0].label.position = 'left' ;
      }
     }
     else{
      if(this.dataLabelsFontPosition === 'center'){
        let obj ={
          series :[
           {
            label :{
             position: 'inside'
            }
          }]
        }
        this.chartInstance?.setOption(obj);
        this.chartOptions.series[0].label.position = 'inside' ;
      }
      else{
        let obj ={
          series :[
           {
            label :{
             position: this.dataLabelsFontPosition
            }
          }]
        }
        this.chartInstance?.setOption(obj);
        this.chartOptions.series[0].label.position = this.dataLabelsFontPosition ;
      }
     }
  }
  dataLabelsBarFontPositionSetOptions(){
      if(this.chartType ==='barline'){
        if(this.dataLabelsBarFontPosition === 'center'){
      let obj ={
       series: [
         {
           label: {
            position: 'inside',
           
          },
         },
         {
       
         },
       ],
      }
       this.chartInstance?.setOption(obj);
       this.chartOptions.series[0].label.position = 'inside';
    }
    else{
      let obj ={
        series: [
          {
            label: {
             position:this.dataLabelsBarFontPosition,
           },
          },
          {
        
          },
        ],
       }
        this.chartInstance?.setOption(obj);
        this.chartOptions.series[0].label.position = this.dataLabelsBarFontPosition;
    }
     }
  }
  dataLabelsLineFontPositionSetOptions(){
    if(this.chartType ==='barline'){
    let obj ={
      series: [
        {
       
        },
        {
          label: {
            position:this.dataLabelsLineFontPosition,
          },
        },
      ],
     }
      this.chartInstance?.setOption(obj);
      this.chartOptions.series[1].label.position = this.dataLabelsLineFontPosition;
    }
  }
  setDatalabelsFontWeight(){
    if(this.chartType ==='barline'){
      let obj ={
       series: [
         {
           label: {
            fontWeight: this.isBold ? 700 : 400, // Update for 'Bar Axis'
           },
         },
         {
          label: {
            fontWeight: this.isBold ? 700 : 400,
           },
         },
       ],
      }
       this.chartInstance?.setOption(obj);
       this.chartOptions.series[0].label.fontWeight = this.isBold ? 700 : 400;
       this.chartOptions.series[1].label.fontWeight = this.isBold ? 700 : 400;
      }
     else if(this.chartType === 'radar'){
      this.chartOptions.series[0].data.forEach((dataItem: { label: { fontWeight: any; }; }) => {
        if (dataItem.label) { // Ensure label exists before updating
            dataItem.label.fontWeight = this.isBold ? 700 : 400;
        }
    });
       this.chartInstance?.setOption(this.chartOptions,true)
     }
     else if(this.chartType === 'multiline' || this.chartType === 'hgrouped' || this.chartType === 'hstocked' || this.chartType === 'stocked' || this.chartType === 'sidebyside'){
      this.chartOptions.series.forEach((series: { label: { fontWeight: any; }; }) => {
        series.label.fontWeight = this.isBold ? 700 : 400; 
    });
    this.chartInstance?.setOption(this.chartOptions,true)
     }
     else{
       let obj ={
         series :[
          {
           label :{
            fontWeight: this.isBold ? 700 : 400
           }
         }]
       }
       this.chartInstance?.setOption(obj);
       this.chartOptions.series[0].label.fontWeight = this.isBold ? 700 : 400;
      //  this.chartOptions = { ...this.chartOptions, ...obj };
     }
  }
  xLabelSwitchSetOptions(){
    if(this.chartType === 'barline'){
      let obj ={
        xAxis :[{
          axisLabel :{
            show: this.xLabelSwitch
          }
        }]
      }
      this.chartInstance?.setOption(obj);
      this.chartOptions.xAxis[0].axisLabel.show = this.xLabelSwitch;
    }
    else{
      let obj ={
        xAxis :{
          axisLabel :{
            show: this.xLabelSwitch
          }
        }
      }
      this.chartInstance?.setOption(obj);
      this.chartOptions.xAxis.axisLabel.show =this.xLabelSwitch;
  }
  }
  yLabelSwitchSetOptions(){
    if(this.chartType === 'barline'){
      let obj ={
        yAxis :[{
          show:this.yLabelSwitch,
        },
      {
          show: this.yLabelSwitch
      }
    ]
      }
      this.chartInstance?.setOption(obj);
      this.chartOptions.yAxis[0].show = this.yLabelSwitch;
      this.chartOptions.yAxis[1].show = this.yLabelSwitch;
    }
    else{
      let obj ={
        yAxis :{
          axisLabel :{
            show: this.yLabelSwitch
          }
        }
      }
      this.chartInstance?.setOption(obj);
      this.chartOptions.yAxis.axisLabel.show = this.yLabelSwitch;
  }
  }
  xGridSwitchSetOptions(){
    if(this.chartType === 'barline'){
      let obj ={
        xAxis :[{
          splitLine :{
            show: this.xGridSwitch
          }
        },
      {
    
      }
    ]
      }
      this.chartInstance?.setOption(obj);
      this.chartOptions.xAxis[0].splitLine.show = this.xGridSwitch;
    }
    else if(this.chartType === 'line'){
      let obj ={
        xAxis :[{
          splitLine :{
            show: this.xGridSwitch
          }
        },
      {
    
      }
    ]
      }
      this.chartInstance?.setOption(obj);
      this.chartOptions.xAxis.splitLine.lineStyle.show = this.xGridSwitch;
    }
    else{
      let obj ={
        xAxis :{
          splitLine :{
            show: this.xGridSwitch
          }
        }
      }
      this.chartInstance?.setOption(obj);
      this.chartOptions.xAxis.splitLine.show = this.xGridSwitch;
  }
  }
  yGridSwitchSetOptions(){
    if(this.chartType === 'barline'){
      let obj ={
        yAxis :[{
          splitLine :{
            show: this.yGridSwitch
          }
        },
      {
        splitLine :{
          show: this.yGridSwitch
        }
      }
    ]
      }
      this.chartInstance?.setOption(obj);
      this.chartOptions.yAxis[0].splitLine.show = this.yGridSwitch;
      this.chartOptions.yAxis[1].splitLine.show = this.yGridSwitch;
    }
    else{
      let obj ={
        yAxis :{
          splitLine :{
            show: this.yGridSwitch
          }
        }
      }
      this.chartInstance?.setOption(obj);
      this.chartOptions.yAxis.splitLine.show = this.yGridSwitch;
  }
  }
  legendSwitchSetOptions(){
    if(this.chartType === 'donut' || this.chartType === 'pie' || this.chartType === 'radar'){
      let obj ={
        legend :{
            show: this.legendSwitch
        }
      }
      this.chartInstance?.setOption(obj);
      this.chartOptions.legend.show = this.legendSwitch;
    }
  }
  dataLabelsSetOptions(){
    if(this.chartType === 'donut' || this.chartType === 'pie'){
      let obj ={
        series :[{
          label:{
            show: this.dataLabels
          }
        }]
      }
      this.chartInstance?.setOption(obj);
      this.chartOptions.series[0].label.show = this.dataLabels;
    }
    else if(this.chartType === 'radar'){
      this.chartOptions.series[0].data.forEach((dataItem: { label: { show: boolean; }; }) => {
        dataItem.label.show = this.dataLabels; // Show or hide labels based on checkbox state
    }); 
    this.chartInstance?.setOption(this.chartOptions,true)
    }
  }
  colorSetOptions(){
    if(this.chartType === 'barline'){
      let obj ={
        series :[{
          itemStyle :{
            color: this.barColor
          }
        },
        {
          lineStyle :{
            color: this.lineColor
          }
        }
    ]
      }
      this.chartInstance?.setOption(obj);
      this.chartOptions.series[0].itemStyle.color = this.barColor;
      this.chartOptions.series[1].lineStyle.color = this.lineColor;
    } else if(this.chartType === 'funnel'){
      let obj ={
        color:this.isDistributed ? this.selectedColorScheme : this.color
       }
       this.chartInstance?.setOption(obj);
       this.chartOptions.color = this.isDistributed ? this.selectedColorScheme : this.color;
    } else if(this.chartType === 'stocked'
       || this.chartType === 'sidebyside' || this.chartType === 'hgrouped' || this.chartType === 'hstocked' ||  
       this.chartType === 'multiline' || this.chartType === 'pie' || this.chartType === 'donut' || 
       this.chartType === 'calendar'){
      let obj ={
        color:this.selectedColorScheme
       }
       this.chartInstance?.setOption(obj);
       this.chartOptions.color = this.selectedColorScheme;
    }else if(this.chartType ==='heatmap'){
      let obj ={
        visualMap :{
          inRange :{
            color:this.selectedColorScheme
          }
        }
      }
      this.chartInstance?.setOption(obj)
      this.chartOptions.visualMap.inRange.color = this.selectedColorScheme;
    }
    else{
      let obj ={
       color:this.color
      }
      this.chartInstance?.setOption(obj)
      this.chartOptions.color = this.color;
      console.log('chartoptionsecahrtcolor',this.chartOptions)
  }
  }
  dimensionsAlignmentSetOption() {
    if(this.dimensionAlignment === 'right'){
    let obj ={
      xAxis :{
        axisLabel :{
          align: 'left'
        }
      }
    }
    this.chartInstance?.setOption(obj);
    this.chartOptions.xAxis.axisLabel.align = 'left';
  }else if(this.dimensionAlignment === 'left'){
    let obj ={
      xAxis :{
        axisLabel :{
          align: 'right'
        }
      }
    }
    this.chartInstance?.setOption(obj);
    this.chartOptions.xAxis.axisLabel.align = 'right';
  }else if(this.dimensionAlignment === 'right'){
    let obj ={
      xAxis :{
        axisLabel :{
          align: 'left'
        }
      }
    }
    this.chartInstance?.setOption(obj);
    this.chartOptions.xAxis.axisLabel.align = 'left';
  } else{
    let obj ={
      xAxis :{
        axisLabel :{
          align:this.dimensionAlignment
        }
      }
    }
    this.chartInstance?.setOption(obj);
    this.chartOptions.xAxis.axisLabel.align = this.dimensionAlignment;
  }
    
  }
  xGridColorSetOptions(){
    if(this.chartType === 'barline'){
      let obj ={
        xAxis :[{
          splitLine :{
            lineStyle:{
              color: this.xGridColor
            }
          }
        },
        {
         
        }
    ]
      }
      this.chartInstance?.setOption(obj);
      this.chartOptions.xAxis[0].splitLine.lineStyle.color = this.xGridColor;
    }else if(this.chartType === 'hgrouped'){
      let obj ={
        xAxis :[{
            splitLine:{
              lineStyle:{
                color: this.xGridColor
              }
            }
          

        },
    ]
      }
      this.chartInstance?.setOption(obj);
      this.chartOptions.xAxis.splitLine.lineStyle.color = this.xGridColor;
    }
    else{
      let obj ={
        xAxis :{
          splitLine :{
            lineStyle:{
              color: this.xGridColor
            }
          }
        },
   
      }
      this.chartInstance?.setOption(obj);
      this.chartOptions.xAxis.splitLine.lineStyle.color = this.xGridColor;
  }
  }
  yGridColorSetOptions(){
    if(this.chartType === 'barline'){
      let obj ={
        yAxis :[{
          splitLine :{
            lineStyle:{
              color: this.yGridColor
            }
          }
        },
        {
          splitLine :{
            lineStyle:{
              color: this.yGridColor
            }
          }
        }
    ]
      }
      this.chartInstance?.setOption(obj);
    this.chartOptions.yAxis[0].splitLine.lineStyle.color = this.yGridColor;
    this.chartOptions.yAxis[1].splitLine.lineStyle.color = this.yGridColor;
    }else if(this.chartType === 'hgrouped'){
      let obj ={
        yAxis :[{
            splitLine:{
              lineStyle:{
                color: this.yGridColor
              }
            }
                  },
    ]
      }
      this.chartInstance?.setOption(obj);
      this.chartOptions.yAxis[0].splitLine.lineStyle.color = this.yGridColor;
    }
    else{
      let obj ={
        yAxis :{
          splitLine :{
            lineStyle:{
              color: this.yGridColor
            }
          }
        },
   
      }
      this.chartInstance?.setOption(obj);
      this.chartOptions.yAxis.splitLine.lineStyle.color = this.yGridColor;
  }
  }
  backgroundColorSetOptions(){
      let obj ={
        backgroundColor:this.backgroundColor
      }
      this.chartInstance?.setOption(obj);
      this.chartOptions = { ...this.chartOptions, ...obj };
  }
  legendsAllignmentSetOptions(){
    if(this.chartType === 'pie' || this.chartType === 'donut'){
    if(this.legendsAllignment === 'top'){
    let obj ={
      legend :{
        top: this.topLegend,
        left: this.leftLegend,
        orient: this.legendOrient,
        bottom:'null',
        right:'null',
        show: this.legendSwitch 
      },
    }
    this.chartOptions.legend = obj;
    this.chartInstance?.setOption(obj)
  }
  else if(this.legendsAllignment === 'bottom'){
    let obj ={
      legend :{
          bottom: this.bottomLegend, 
          left: this.leftLegend, 
          orient: this.legendOrient,
          // right:'null',
          // top:'null',
          show: this.legendSwitch,

      },
    }
    this.chartOptions.legend = obj;
    this.chartInstance?.setOption(obj)
  }
  else if(this.legendsAllignment === 'left'){
    let obj ={
      legend :{
          left: this.leftLegend, 
          top: this.topLegend, 
          orient: this.legendOrient,
          show: this.legendSwitch 
      },
    }
    this.chartOptions.legend = obj;
    this.chartInstance?.setOption(obj)
  }
  else if(this.legendsAllignment === 'right'){
    let obj ={
      legend :{
         right: this.rightLegend, 
         top:this.topLegend, 
         orient:this.legendOrient,
         show: this.legendSwitch 
      },
    }
    this.chartOptions.legend = obj;
    this.chartInstance?.setOption(obj)
  }
  }
  else if(this.chartType === 'radar'){
    let legendPosition: any = {};

    if (this.legendsAllignment === 'top') {
      legendPosition = { top: 'top', left: 'center', orient: 'horizontal' };
    } 
    else if (this.legendsAllignment === 'bottom') {
      legendPosition = { bottom: 'bottom', left: 'center', orient: 'horizontal' };
    } 
    else if (this.legendsAllignment === 'left') {
      legendPosition = { left: 'left', top: 'middle', orient: 'vertical' };
    } 
    else if (this.legendsAllignment === 'right') {
      legendPosition = { right: 'right', top: 'middle', orient: 'vertical' };
    }
    
    // Ensure `legend.data` is defined properly
    const legendData = this.radarRowData.map((dataItem: any) => ({
      name: dataItem.name
    }));
    
    // Removing conflicting properties
    ['top', 'bottom', 'left', 'right'].forEach((prop) => {
      if (!legendPosition[prop]) delete this.chartOptions.legend[prop];
    });
    
    // Apply the updated legend options
    this.chartOptions.legend = {
      ...this.chartOptions.legend,
      ...legendPosition,
      data: legendData,  // Ensure data is set
      show:this.legendSwitch,
    };
      this.chartInstance?.setOption({ legend: this.chartOptions.legend });
  }
  }
  selectedColorSchemeSetOptions(){
    let obj = {
      color:this.selectedColorScheme
    }
    this.chartInstance?.setOption(obj);
    this.chartOptions.color = this.selectedColorScheme;
  }
  donutSizeChange(){
    let obj ={
      series:[{
        radius: [this.donutSize+'%' , '70%']
      }]
    }
    this.chartInstance?.setOption(obj);
    this.chartOptions.series[0].radius = [this.donutSize+'%' , '70%'];
  }
updateNumberFormat(){
  if(this.chartType === 'bar'){
    this.chartOptions.series[0].label.formatter = (params:any) => this.formatNumber(params.value);
    this.chartOptions.yAxis.axisLabel.formatter = (value:any) => this.formatNumber(value);
  } else if(this.chartType === 'line'){
    this.chartOptions.series[0].label.formatter = (params:any) => this.formatNumber(params.value);
    this.chartOptions.yAxis.axisLabel.formatter = (value:any) => this.formatNumber(value);
  } else if(this.chartType === 'area'){
    this.chartOptions.series[0].label.formatter = (params:any) => this.formatNumber(params.value);
    this.chartOptions.yAxis.axisLabel.formatter = (value:any) => this.formatNumber(value);
  } else if(this.chartType === 'pie'){
    this.chartOptions.series[0].label.formatter = (params:any) => this.formatNumber(params.value);
    this.chartOptions.yAxis.axisLabel.formatter = (value:any) => this.formatNumber(value);
  } else if(this.chartType === 'donut'){
    this.chartOptions.series[0].label.formatter = (params:any) => this.formatNumber(params.value);
    this.chartOptions.yAxis.axisLabel.formatter = (value:any) => this.formatNumber(value);
  } else if(this.chartType === 'sidebyside'){
    this.chartOptions.series.forEach((data : any)=>{
      data.label.formatter = (params:any) => this.formatNumber(params.value);
    })
    // this.eSideBySideBarChartOptions.series.label.formatter = (params:any) => this.formatNumber(params.value);
    this.chartOptions.yAxis.axisLabel.formatter = (value:any) => this.formatNumber(value);
  } else if(this.chartType === 'stocked'){
    this.chartOptions.series.forEach((data : any)=>{
      data.label.formatter = (params:any) => this.formatNumber(params.value);
    })
    // this.eStackedBarChartOptions.series.label.formatter = (params:any) => this.formatNumber(params.value);
    this.chartOptions.yAxis.axisLabel.formatter = (value:any) => this.formatNumber(value);
  } else if(this.chartType === 'barline'){
    this.chartOptions.series.forEach((data : any)=>{
      data.label.formatter = (params:any) => this.formatNumber(params.value);
    })
    // this.eBarLineChartOptions.series.label.formatter = (params:any) => this.formatNumber(params.value);
    this.chartOptions.yAxis[0].axisLabel.formatter = (value:any) => this.formatNumber(value);
    this.chartOptions.yAxis[1].axisLabel.formatter = (value:any) => this.formatNumber(value);
  } else if(this.chartType === 'hstocked'){
    this.chartOptions.series.forEach((data : any)=>{
      data.label.formatter = (params:any) => this.formatNumber(params.value);
    })
    // this.ehorizontalStackedBarChartOptions.series.label.formatter = (params:any) => this.formatNumber(params.value);
    this.chartOptions.xAxis.axisLabel.formatter = (value:any) => this.formatNumber(value);
  } else if(this.chartType === 'hgrouped'){
    this.chartOptions.series.forEach((data : any)=>{
      data.label.formatter = (params:any) => this.formatNumber(params.value);
    })
    // this.eGroupedBarChartOptions.series.label.formatter = (params:any) => this.formatNumber(params.value);
    this.chartOptions.xAxis.axisLabel.formatter = (value:any) => this.formatNumber(value);
  } else if(this.chartType === 'multiline'){
    this.chartOptions.series.forEach((data : any)=>{
      data.label.formatter = (params:any) => this.formatNumber(params.value);
    })
    // this.eMultiLineChartOptions.series.label.formatter = (params:any) => this.formatNumber(params.value);
    this.chartOptions.yAxis.axisLabel.formatter = (value:any) => this.formatNumber(value);
  } else if(this.chartType === 'radar'){
    this.chartOptions.series.forEach((data : any)=>{
      data.data.forEach((measure:any)=>{
        measure.label.formatter = (params:any) => this.formatNumber(params.value);
      })
    })
    // this.eRadarChartOptions.series.label.formatter = (params:any) => this.formatNumber(params.value);
    // this.eRadarChartOptions.yAxis.axisLabel.formatter = (value:any) => this.formatNumber(value);
  } else if(this.chartType === 'heatmap'){
    this.chartOptions.series.forEach((data : any)=>{
      data.label.formatter = (params:any) => this.formatNumber(params.value[2]);
    })
    // this.eHeatMapChartOptions.series.label.formatter = (params:any) => this.formatNumber(params.value);
  } else if(this.chartType === 'funnel'){
    this.chartOptions.series.forEach((data : any)=>{
      data.label.formatter = (params:any) => {
        const formattedValue = this.formatNumber(params.value);
        return `${params.name}: ${formattedValue}`;
    };
    })
    // this.eFunnelChartOptions.series.label.formatter = (params:any) => this.formatNumber(params.value);
    // this.eFunnelChartOptions.yAxis.axisLabel.formatter = (value:any) => this.formatNumber(value);
  }
  this.chartInstance?.setOption(this.chartOptions,true)

}

updateCategories(){
  if(this.chartType === 'bar' || this.chartType === 'line' || this.chartType === 'area'){
   let obj={
    xAxis:{
      data:this.chartsColumnData
    }
   }
   this.chartInstance?.setOption(obj);
   this.chartOptions.xAxis.data =this.chartsColumnData;
  } else if(this.chartType === 'pie'){
    let combinedArray = this.chartsRowData.map((value : any, index :number) => ({
      value: value,
      name: this.chartsColumnData[index]
    }));
    let obj ={
      series :{
        data:combinedArray
      }
    }
    this.chartInstance?.setOption(obj);
    this.chartOptions.series.data = combinedArray;
  } else if(this.chartType === 'donut'){
    let combinedArray = this.chartsRowData.map((value : any, index :number) => ({
      value: value,
      name: this.chartsColumnData[index]
    }));
    let obj ={
      series :[{
        data:combinedArray
      }]
    }
    this.chartInstance?.setOption(obj);
    this.chartOptions.series[0].data = combinedArray;
  } else if(this.chartType === 'sidebyside' || this.chartType === 'stocked' || this.chartType === 'multiline' || this.chartType === 'heatmap'){
    const dimensions: Dimension[] = this.dualAxisColumnData;
    const categories = this.flattenDimensions(dimensions);
    let obj ={
      xAxis:{
        data:categories
      }
    }
    this.chartInstance?.setOption(obj);
    this.chartOptions.xAxis.data = categories;
  }else if(this.chartType === 'barline'){
  const dimensions: Dimension[] = this.dualAxisColumnData;
  const categories = this.flattenDimensions(dimensions);
  let obj ={
    xAxis:[{
      data:categories
    }]
  }
  this.chartInstance?.setOption(obj);
  this.chartOptions.xAxis[0].data = categories;
} else if(this.chartType === 'hstocked' || this.chartType === 'hgrouped'){
    const dimensions: Dimension[] = this.dualAxisColumnData;
    const categories = this.flattenDimensions(dimensions);
    let obj ={
      yAxis:{
        data:categories
      }
    }
    this.chartInstance?.setOption(obj);
    this.chartOptions.yAxis.data = categories;
  } else if(this.chartType === 'radar'){
    const dimensions: Dimension[] = this.dualAxisColumnData;
    const categories = this.flattenDimensions(dimensions);
    let radarArray = categories.map((value: any, index: number) => ({
      name: categories[index]
    }));
    let legendArray = this.radarRowData.map((data: any) => ({
      name: data.name
    }));
    let obj ={
      legend:{
        data:legendArray
      },
      radar:{
        indicator:radarArray
      }
    }
    this.chartInstance?.setOption(obj);
    this.chartOptions.legend.data = legendArray;
    this.chartOptions.radar.indicator = legendArray;
  } else if(this.chartType === 'funnel'){
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
  let obj ={
    series:[{
      data:combinedArray
    }]
  }
  this.chartInstance?.setOption(obj);
  this.chartOptions.series[0].data = combinedArray;

  }

}
updateSeries(){
  if(this.chartType === 'bar' || this.chartType === 'line' || this.chartType === 'area'){
    let obj={
     series:[{
       data:this.chartsRowData
     }]
    }
    this.chartInstance?.setOption(obj);
    this.chartOptions.series[0].data = this.chartsRowData;
}  else if(this.chartType === 'pie'){
  let combinedArray = this.chartsRowData.map((value : any, index :number) => ({
    value: value,
    name: this.chartsColumnData[index]
  }));
  let obj ={
    series :{
      data:combinedArray
    }
  }
  this.chartInstance?.setOption(obj);
  this.chartOptions.series.data = combinedArray;
} else if(this.chartType === 'donut'){
  let combinedArray = this.chartsRowData.map((value : any, index :number) => ({
    value: value,
    name: this.chartsColumnData[index]
  }));
  let obj ={
    series :[{
      data:combinedArray
    }]
  }
  this.chartInstance?.setOption(obj);
  this.chartOptions.series[0].data = combinedArray;
} else if(this.chartType === 'sidebyside' || this.chartType === 'stocked' || this.chartType === 'hstocked' || this.chartType === 'hgrouped' || this.chartType === 'multiline'){
  let yaxisOptions = _.cloneDeep(this.dualAxisRowData);
  let obj ={
    series:yaxisOptions
  }
  this.chartInstance?.setOption(obj);
  this.chartOptions.series = yaxisOptions;
} else if(this.chartType === 'barline'){
  let obj ={
    series:[
      {
      name:this.dualAxisRowData[0]?.name,
      data:this.dualAxisRowData[0]?.data
    },
    {
      name:this.dualAxisRowData[1]?.name,
      data:this.dualAxisRowData[1]?.data
    }
  ]
  }
  this.chartInstance?.setOption(obj);
  this.chartOptions.series[0].name = obj.series[0]?.name;
  this.chartOptions.series[0].data = obj.series[0]?.data;
  this.chartOptions.series[1].name = obj.series[1]?.name;
  this.chartOptions.series[1].data = obj.series[1]?.data;
} else if(this.chartType === 'radar'){
  let obj ={
    series:[
      {data:this.radarRowData}
    ]
  }
  this.chartInstance?.setOption(obj);
  this.chartOptions.series[0].data = this.radarRowData;
} else if(this.chartType === 'heatmap'){
  let obj ={
    yAxis:{
      data:this.dualAxisRowData
    }
  }
  this.chartInstance?.setOption(obj);
  this.chartOptions.yAxis.data = this.dualAxisRowData;
} else if(this.chartType === 'funnel'){
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
  let obj ={
    series:[{
      data:combinedArray
    }]
  }
  this.chartInstance?.setOption(obj);
  this.chartOptions.series[0].data = combinedArray;

}

}
// sort(sortType: any, numbers: any, labels: any) {
//   let pairedData = numbers.map((num: any, index: any) => [num, labels[index]]);

//   if (sortType === 'ascending') {
//     pairedData.sort((a: any, b: any) => a[0] - b[0]);
//   } else if (sortType === 'descending') {
//     pairedData.sort((a: any, b: any) => b[0] - a[0]);
//   } else if(sortType === 'none'){
//     pairedData = this.chartsRowData.map((num: any, index: any) => [num, this.chartsColumnData[index]])
//   }

//   const sortedNumbers = pairedData.map((pair: any) => pair[0]);
//   const sortedLabels = pairedData.map((pair: any) => pair[1]);
//   return { sortedNumbers, sortedLabels };
// }
// sortSeries(sortType: any) {
//  if (this.chartType === 'bar') {
//   const numbers = this.chartOptions.series[0].data;
//   const labels = this.chartOptions.xAxis.data;
//   const sortedData = this.sort(sortType, numbers, labels);
//   let obj={
//     series:[{
//       data:sortedData.sortedNumbers
//     }],
//     xAxis:{
//       data:sortedData.sortedLabels
//     }
//   }
//   this.chartInstance?.setOption(obj);
//   // this.chartOptions.series[0].data = sortedData.sortedNumbers;
//   // this.chartOptions.xAxis.data = sortedData.sortedLabels;

//   }
// }
  onChartClick(event: any) {
    if (this.drillDownIndex < this.draggedDrillDownColumns.length - 1) {
      console.log('X-axis value:', event.name);
      let nestedKey = this.draggedDrillDownColumns[this.drillDownIndex];
      this.drillDownIndex++;
      let obj = { [nestedKey]: event.name };
      this.drillDownObject.push(obj);
      let dObject = {
        drillDownIndex : this.drillDownIndex,
        draggedDrillDownColumns :this.draggedDrillDownColumns,
        drillDownObject : this.drillDownObject
      }
      this.setDrilldowns.emit(dObject);
      // this.setOriginalData();
      // this.dataExtraction();
    }
  }
  private handleChartClick(event: any): void {
    this.onMapChartClick(event).catch((error) => {
      console.error('Error handling chart click:', error);
    });
  }
  async onMapChartClick(event: any) {
    const regionName = event.name;
    if (regionName === 'United States') {
      const geoJson = await lastValueFrom(
        this.http.get<any>(`assets/maps/USA.json`)
      );
      echarts.registerMap(regionName, geoJson);
    } else {
     
    }
    // this.setOriginalData();
    if (this.drillDownIndex < this.draggedDrillDownColumns.length - 1) {
      console.log('X-axis value:', regionName);
      let nestedKey = this.draggedDrillDownColumns[this.drillDownIndex];
      this.drillDownIndex++;
      let obj = { [nestedKey]: regionName };
      this.drillDownObject.push(obj);
      // this.map = false;
      // if (this.drillDownIndex > 0) {
      //   this.bar = true;
      //   this.chartId = 6;
      // }
      // this.dataExtraction();
      let dObject = {
        drillDownIndex : this.drillDownIndex,
        draggedDrillDownColumns :this.draggedDrillDownColumns,
        drillDownObject : this.drillDownObject
      }
      this.setDrilldowns.emit(dObject);
    }
  }
}