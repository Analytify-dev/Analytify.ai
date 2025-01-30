import { Component, EventEmitter, Input, Output, SimpleChanges, ViewChild } from '@angular/core';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { NgSelectModule } from '@ng-select/ng-select';
import { ChartComponent, NgApexchartsModule } from 'ng-apexcharts';
import { NgxEchartsModule } from 'ngx-echarts';
import { SharedModule } from '../../../shared/sharedmodule';
import _ from 'lodash';
import { fontWeight } from 'html2canvas/dist/types/css/property-descriptors/font-weight';

interface Dimension {
  name: string;
  values: string[];
}

@Component({
  selector: 'app-insight-apex',
  standalone: true,
  imports: [SharedModule, NgxEchartsModule, NgSelectModule,NgbModule,
    NgApexchartsModule
    ],
  templateUrl: './insight-apex.component.html',
  styleUrl: './insight-apex.component.scss'
})
export class InsightApexComponent {
  @Input() chartsRowData: any; 
  @Input() chartsColumnData: any;
  @Input() dualAxisColumnData : any;
  @Input() dualAxisRowData : any;
  @Input() chartType : any;
  @Input() tablePreviewRow = [] as any;
  @Input() xGridSwitch : any;
  @Input() xLabelSwitch : any;
  @Input() yLabelSwitch : any;
  @Input() yGridSwitch : any;
  @Input() xLabelFontFamily : any;
  @Input() xLabelFontSize : any;
  @Input() xlabelFontWeight : any;
  @Input() backgroundColor : any;
  @Input() color : any;
  @Input() ylabelFontWeight : any;
  @Input() isBold : any;
  @Input() yLabelFontFamily : any;
  @Input() yLabelFontSize : any;
  @Input() barColor : any;
  @Input() lineColor : any;
  @Input() gridColor : any;
  @Input() legendSwitch : any;
  @Input() dataLabels: any;
  @Input() label : any;
  @Input() donutSize : any;
  @Input() isDistributed : any;
  @Input() minValueGuage : any;
  @Input() maxValueGuage : any;
  @Input() legendsAllignment: any;
  @Input() dataLabelsFontFamily : any;
  @Input() dataLabelsFontSize : any;
  @Input() dataLabelsFontPosition : any;
  @Input() measureAlignment : any;
  @Input() dimensionAlignment : any;
  @Input() dataLabelsColor : any;
  @Input() displayUnits : any;
  @Input() decimalPlaces : any;
  @Input() prefix : any;
  @Input() suffix : any;
  @Input() donutDecimalPlaces : any;
  @Input() drillDownIndex : any;
  @Input() draggedDrillDownColumns : any;
  @Input() drillDownObject : any;
  @Input() sortType : any;
  @Input() isSheetSaveOrUpdate : any;
  @Input() dataLabelsBarFontPosition:any;
  @Input() dataLabelsLineFontPosition:any;
  @Input() selectedColorScheme:any;
  @Output() setDrilldowns = new EventEmitter<object>();
  @Output() saveOrUpdateChart = new EventEmitter<object>();
  
  @ViewChild('barChart') barCharts!: ChartComponent;
  @ViewChild('areaChart') areaCharts!: ChartComponent;
  @ViewChild('lineChart') lineCharts!: ChartComponent;
  @ViewChild('sidebyside') sideBySideCharts!: ChartComponent;
  @ViewChild('stocked') stockedCharts!: ChartComponent;
  @ViewChild('barline') barLineCharts!: ChartComponent;
  @ViewChild('horizentalstocked') horizontalStockedCharts!: ChartComponent;
  @ViewChild('grouped') groupedCharts!: ChartComponent;
  @ViewChild('multiline') multiLineCharts!: ChartComponent;
  @ViewChild('piechart') pieCharts!: ChartComponent;
  @ViewChild('donutchart') donutCharts!: ChartComponent;
  @ViewChild('funnelChart') funnelCharts!: ChartComponent;
  @ViewChild('guageChart') guageCharts!: ChartComponent;
  @ViewChild('heatmapchart') heatmapCharts!: ChartComponent;
  series: any[] = [];
  chartOptions: any = {};
  guageNumber : any;
  valueToDivide : any;
  formattedData : any[] = [];

  ngOnInit(){
    // this.generateChart();
  }

  ngOnChanges(changes: SimpleChanges) {
    // if(changes['chartType']){
      this.generateChart();
    // }
    
    if(changes['chartsColumnData']  || changes['dualAxisColumnData'] ){
      // if(changes['chartsColumnData'].currentValue.length>0 || changes['dualAxisColumnData'].currentValue.length>0){
        this.updateCategories();
      // }
    }
    if(changes['chartsRowData'] || changes['dualAxisRowData'] ){
      // if(changes['chartsRowData'].currentValue.length>0 || changes['dualAxisRowData'].currentValue.length>0){
        this.updateSeries();
      // }
    }
    if(changes['xLabelFontFamily']){
      this.dimensionsFontFamilyChange();
    }
    if(changes['xLabelFontSize']){
      this.dimensionsFontSizeChange();
    }
    if(changes['xlabelFontWeight']){
      this.dimensionsFontWeightChange();
    }
    if(changes['dimensionAlignment']){
      this.dimensionsAlignmentChange();
    }
    if(changes['yLabelFontFamily']){
      this.measuresFontFamilyChange();
    }
    if(changes['yLabelFontSize']){
      this.measuresFontSizeChange();
    }
    if(changes['ylabelFontWeight']){
      this.measuresFontWeightChange();
    }
    if(changes['measureAlignment']){
      this.measuresAlignmentChange();
    }
    if(changes['dataLabelsFontFamily']){
      this.setDataLabelsFontFamily();
    }
    if(changes['dataLabelsFontSize']){
      this.setDataLabelsFontSize();
    }
    // if(changes['dataLabelsBarFontPosition']){
    //   this.setDataLabelsBarFontPosition();
    // }
    // if(changes['dataLabelsLineFontPosition']){
    //   this.setDataLabelsLineFontPosition();
    // }
    if(changes['isBold']){
      this.setDataLabelsFontWeight();
    }
    if(changes['dataLabelsColor']){
      this.dataLabelsFontColor();
    }
    if(changes['dataLabelsFontPosition']){
      this.setDataLabelsFontPosition();
    }
    if(changes['xLabelSwitch']){
      this.xLabelShowOrHide();
    }
    if(changes['yLabelSwitch']){
      this.yLabelShowOrHide();
    }
    if(changes['xGridSwitch']){
      this.xGridShowOrHide();
    }
    if(changes['yGridSwitch']){
      this.yGridShowOrHide();
    }
    if(['donut','pie'].includes(this.chartType) && changes['legendSwitch']){
      this.legendsShowOrHide();
    }
    if(['donut','pie'].includes(this.chartType) && changes['dataLabels']){
      this.dataLabelsShowOrHide();
    }
    if(this.chartType == 'donut' && changes['label']){
      this.labelsShowOrHide();
    }
    if(this.chartType == 'funnel' && changes['isDistributed']){
      this.colorDistribution();
    }
    if(['donut','pie'].includes(this.chartType) && changes['legendsAllignment']){
      this.legendPositionChange();
    }
    if(this.chartType == 'donut' && changes['donutSize']){
      this.donutSizeChange();
    }
    if(changes['backgroundColor']){
      this.setBackgroundColor();
    }
    if(changes['barColor'] || changes['lineColor'] || changes['color'] || changes['selectedColorScheme']){
      this.setChartColor();
    }
    if(changes['gridColor']){
      this.gridLineColor();
    }
    if((changes['displayUnits'] || changes['decimalPlaces'] || changes['prefix'] || changes['suffix'] || changes['donutDecimalPlaces']) && !changes['chartType']){
      this.updateNumberFormat();
    }
    if(this.chartType == 'guage' && (changes['minValueGuage'] || changes['maxValueGuage'])){
      this.customMinMaxGuage();
    }
    // if(['funnel','bar'].includes(this.chartType) && changes['sortType'] && changes['sortType']?.currentValue !== 0){
    //   this.sortSeries(this.sortType);
    // }
    if(this.isSheetSaveOrUpdate){
      let object = {
        chartOptions : this.chartOptions
      }
      this.saveOrUpdateChart.emit(object);
    }
    // if(changes['drillDownIndex']){
    //   this.updateDrilldowns();
    // }
    console.log(this.chartOptions);
  }

  updateSeries() {
    if (this.chartType === 'bar') {
      this.chartOptions.series[0].data = this.chartsRowData;
      this.barCharts?.updateOptions({ series: this.chartOptions.series });
    } else if (this.chartType === 'area') {
      this.chartOptions.series[0].data = this.chartsRowData;
      this.areaCharts?.updateOptions({ series: this.chartOptions.series });
    } else if (this.chartType === 'line') {
      this.chartOptions.series[0].data = this.chartsRowData;
      this.lineCharts?.updateOptions({ series: this.chartOptions.series });
    } else if (this.chartType === 'pie') {
      this.chartOptions.series = this.chartsRowData;
      this.pieCharts?.updateOptions({ series: this.chartOptions.series });
    } else if (this.chartType === 'sidebyside') {
      this.chartOptions.series = this.dualAxisRowData;
      this.sideBySideCharts?.updateOptions({ series: this.chartOptions.series });
    } else if (this.chartType === 'stocked') {
      this.chartOptions.series = this.dualAxisRowData;
      this.stockedCharts?.updateOptions({ series: this.chartOptions.series });
    } else if (this.chartType === 'barline') {
      this.chartOptions.series[0].data = this.dualAxisRowData[0]?.data;
      this.chartOptions.series[1].data = this.dualAxisRowData[1]?.data;
      this.barLineCharts?.updateOptions({ series: this.chartOptions.series });
    } else if (this.chartType === 'hstocked') {
      this.chartOptions.series = this.dualAxisRowData;
      this.horizontalStockedCharts?.updateOptions({ series: this.chartOptions.series });
    } else if (this.chartType === 'hgrouped') {
      this.chartOptions.series = this.dualAxisRowData;
      this.groupedCharts?.updateOptions({ series: this.chartOptions.series });
    } else if (this.chartType === 'multiline') {
      this.chartOptions.series = this.dualAxisRowData;
      this.multiLineCharts?.updateOptions({ series: this.chartOptions.series });
    } else if (this.chartType === 'donut') {
      this.chartOptions.series = this.chartsRowData;
      this.donutCharts?.updateOptions({ series: this.chartOptions.series });
    } else if (this.chartType === 'funnel') {
      this.chartOptions.series = this.dualAxisRowData;
      this.funnelCharts?.updateOptions({ series: this.chartOptions.series });
    } 
    else if (this.chartType === 'heatmap') {
      this.chartOptions.series = this.dualAxisRowData;
      this.heatmapCharts?.updateOptions({ series: this.chartOptions.series });
    }
    let isValid = this.validateSeriesData(this.chartOptions.series);
    if (!isValid) {
      this.chartOptions.series = [];
      console.log('invalid series data');
    }
  }
  updateCategories(){
    const dimensions: Dimension[] = this.dualAxisColumnData;
    const categories = this.flattenDimensions(dimensions);
    if(this.barCharts){
      this.chartOptions.xaxis.categories = this.chartsColumnData.map((category : any)  => category === null ? 'null' : category);
      this.barCharts.updateOptions({ xaxis: this.chartOptions.xaxis });
    } else if(this.areaCharts){
      this.chartOptions.xaxis.categories = this.chartsColumnData.map((category : any)  => category === null ? 'null' : category);
      this.areaCharts.updateOptions({ xaxis: this.chartOptions.xaxis });
    } else if(this.lineCharts){
      this.chartOptions.xaxis.categories = this.chartsColumnData.map((category : any)  => category === null ? 'null' : category);
      this.lineCharts.updateOptions({ xaxis: this.chartOptions.xaxis });
    } else if(this.pieCharts){
      this.chartOptions.labels = this.chartsColumnData.map((category : any)  => category === null ? 'null' : category);
      this.pieCharts.updateOptions({ labels: this.chartOptions.labels });
    } else if(this.sideBySideCharts){
      this.chartOptions.xaxis.categories = categories;
      this.sideBySideCharts.updateOptions({ xaxis: this.chartOptions.xaxis });
    } else if(this.stockedCharts){
      this.chartOptions.xaxis.categories = categories;
      this.stockedCharts.updateOptions({ xaxis: this.chartOptions.xaxis });
    } else if(this.barLineCharts){
      this.chartOptions.xaxis.categories = categories;
      this.barLineCharts.updateOptions({ xaxis: this.chartOptions.xaxis });
    } else if(this.horizontalStockedCharts){
      this.chartOptions.xaxis.categories = categories;
      this.horizontalStockedCharts.updateOptions({ xaxis: this.chartOptions.xaxis });
    } else if(this.groupedCharts){
      this.chartOptions.xaxis.categories = categories;
      this.groupedCharts.updateOptions({ xaxis: this.chartOptions.xaxis });
    } else if(this.multiLineCharts){
      this.chartOptions.xaxis.categories = categories;
      this.multiLineCharts.updateOptions({ xaxis: this.chartOptions.xaxis });
    } else if(this.donutCharts){
      this.chartOptions.labels = this.chartsColumnData.map((category : any)  => category === null ? 'null' : category);
      this.donutCharts.updateOptions({ labels: this.chartOptions.labels });
    } else if(this.funnelCharts){
      this.chartOptions.xaxis.categories = categories;
      this.funnelCharts.updateOptions({ xaxis: this.chartOptions.xaxis });
    }
    else if(this.heatmapCharts){
      this.chartOptions.xaxis.categories = categories;
      this.heatmapCharts.updateOptions({ xaxis: this.chartOptions.xaxis });
    }
  }

  updateChart(){
    if (this.sideBySideCharts) {
      this.sideBySideCharts.updateOptions(this.chartOptions);
    }
  }

  ngOnDestroy(): void {
    if(this.barCharts){
      this.barCharts.destroy();
    } else if(this.areaCharts){
      this.areaCharts.destroy();
    } else if(this.lineCharts){
      this.lineCharts.destroy();
    } else if(this.pieCharts){
      this.pieCharts.destroy();
    } else if(this.sideBySideCharts){
      this.sideBySideCharts.destroy();
    } else if(this.stockedCharts){
      this.stockedCharts.destroy();
    } else if(this.barLineCharts){
      this.barLineCharts.destroy();
    } else if(this.horizontalStockedCharts){
      this.horizontalStockedCharts.destroy();
    } else if(this.groupedCharts){
      this.groupedCharts.destroy();
    } else if(this.multiLineCharts){
      this.multiLineCharts.destroy();
    } else if(this.donutCharts){
      this.donutCharts.destroy();
    } else if(this.funnelCharts){
      this.funnelCharts.destroy();
    } else if(this.guageCharts){
      this.guageCharts.destroy();
    } else if(this.heatmapCharts){
      this.heatmapCharts.destroy();
    }
  }

  generateChart(){
    if(this.chartType === 'bar'){
      this.barChart();
    } else if(this.chartType === 'area'){
      this.areaChart();
    } else if(this.chartType === 'line'){
      this.lineChart();
    } else if(this.chartType === 'pie'){
      this.pieChart();
    } else if(this.chartType === 'sidebyside'){
      this.sideBySide();
    } else if(this.chartType === 'stocked'){
      this.stockedChart();
    } else if(this.chartType === 'barline'){
      this.barLineChart();
    } else if(this.chartType === 'hstocked'){
      this.hStockedChart();
    } else if(this.chartType === 'hgrouped'){
      this.hGroupedChart();
    } else if(this.chartType === 'multiline'){
      this.multiLineChart();
    } else if(this.chartType === 'donut'){
      this.donutChart();
    } else if(this.chartType === 'heatmap'){
      this.heatMapChart();
    } else if(this.chartType === 'funnel'){
      this.funnelChart();
    } else if(this.chartType === 'guage'){
      this.guageChart();
    }
    let isValid = this.validateSeriesData(this.chartOptions.series);
    if (!isValid) {
      this.chartOptions.series = [];
      console.log('invalid series data');
    }
  }

  flattenDimensions(dimensions: Dimension[]): string[] {
    const numCategories = Math.max(...dimensions.map(dim => dim.values.length));
    return Array.from({ length: numCategories }, (_, index) => {
      return dimensions.map(dim => dim.values[index] === null ? 'null' : dim.values[index] || '').join(',');
    });
  }
  validateSeriesData(series: any[]): boolean {
    if(['pie', 'donut', 'guage'].includes(this.chartType)) {
      return series?.every((value: any) => typeof value === 'number' || (!isNaN(value) && !isNaN(parseFloat(value))) || value === null);
    } else {
      return series?.every((set) =>
        set?.data?.every((value: any) => typeof value === 'number' || (!isNaN(value) && !isNaN(parseFloat(value))) || value === null)
      );
    }
  }
  barChart() {
    const self = this;
    this.chartOptions = {
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
              let dObject = {
                drillDownIndex : self.drillDownIndex,
                draggedDrillDownColumns :self.draggedDrillDownColumns,
                drillDownObject : self.drillDownObject
              }
              self.setDrilldowns.emit(dObject);
              // self.setOriginalData();
              // self.dataExtraction();
            }
          }
        }
      },
      xaxis: {
        categories: this.chartsColumnData.map((category : any)  => category === null ? 'null' : category),
        tickPlacement: 'on',
        position: 'bottom',
        labels: {
          show: this.xLabelSwitch,
          offsetX: (this.dimensionAlignment === 'center' ? 0 : (this.dimensionAlignment === 'left' ? -10 : 10)),
          style: {
            colors: [],
            fontSize: this.xLabelFontSize,
            fontFamily: this.xLabelFontFamily,
            fontWeight: this.xlabelFontWeight,
            },
        },
      },
      yaxis:{
        show: true,
        labels: {
          show: this.yLabelSwitch,
          offsetY: (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)),
          style: {
            colors: [],
            fontSize: this.yLabelFontSize,
            fontFamily: this.yLabelFontFamily,
            fontWeight: this.ylabelFontWeight,
          },
          formatter: this.formatNumber.bind(this)
        },
      },
      grid: {
        show: true,
        borderColor: this.gridColor,
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
            position: this.dataLabelsFontPosition,
          },
        },
      },
      dataLabels: {
        enabled: true,
        formatter: this.formatNumber.bind(this),
        offsetY: -20,
        style: {
          fontSize: this.dataLabelsFontSize,
          fontFamily: this.dataLabelsFontFamily,
          fontWeight: this.isBold ? 700 : 400,
          colors: [this.dataLabelsColor],
        },
      },
      colors: [this.color]
    };
  }
  areaChart() {
    this.chartOptions = {
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
          fontSize: this.dataLabelsFontSize,
          fontFamily: this.dataLabelsFontFamily,
          fontWeight: this.isBold ? 700 : 400,
          colors: [this.dataLabelsColor],
        },
        background: {
          enabled: false,
        }
      },
      stroke: {
        curve: "straight",
      },
      grid: {
        borderColor: this.gridColor,
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
      // labels: this.chartsColumnData.map((category: any) => category === null ? 'null' : category),
      colors: [this.color],
      xaxis: {
        categories: this.chartsColumnData.map((category : any)  => category === null ? 'null' : category),
        type: "",
        labels: {
          show: this.xLabelSwitch,
          offsetX: (this.dimensionAlignment === 'center' ? 0 : (this.dimensionAlignment === 'left' ? -10 : 10)),
          style: {
            // colors: this.color,
            fontSize: this.xLabelFontSize,
            fontFamily: this.xLabelFontFamily,
            fontWeight: this.xlabelFontWeight,
          },
        },
        tickPlacement: 'on'
      },
      yaxis: {
        labels: {
          show: true,
          offsetY: (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)),
          style: {
            // colors: this.color,
            fontSize: this.yLabelFontSize,
            fontFamily: this.yLabelFontFamily,
            fontWeight: this.ylabelFontWeight,
          },
          formatter: this.formatNumber.bind(this)
        },
      },
    };
  }
  lineChart() {
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
      },
      colors: [this.color],
      dataLabels: {
        enabled: true,
        formatter: this.formatNumber.bind(this),
        offsetY: -10,
        style: {
          fontSize: this.dataLabelsFontSize,
          fontFamily: this.dataLabelsFontFamily,
          fontWeight: this.isBold ? 700 : 400,
          colors: [this.dataLabelsColor],
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
        borderColor: this.gridColor,
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
      xaxis: {
        categories: this.chartsColumnData.map((category: any) => category === null ? 'null' : category),
        tickPlacement: 'on',
        labels: {
          show: true,
          offsetX: (this.dimensionAlignment === 'center' ? 0 : (this.dimensionAlignment === 'left' ? -10 : 10)),
          style: {
            // colors: this.color,
            fontSize: this.xLabelFontSize,
            fontFamily: this.xLabelFontFamily,
            fontWeight: this.xlabelFontWeight,
          },
        }
      },
      yaxis: {
        labels: {
          show: true,
          offsetY: (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)),
          style: {
            // colors: this.color,
            fontSize: this.yLabelFontSize,
            fontFamily: this.yLabelFontFamily,
            fontWeight: this.ylabelFontWeight,
          },
          formatter: this.formatNumber.bind(this)
        }
      }
    }
  }
  pieChart() {
    const self = this;
    this.chartOptions = {
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
              const selectedXValue = self.chartOptions.labels[config.dataPointIndex];
              console.log('X-axis value:', selectedXValue);
              let nestedKey = self.draggedDrillDownColumns[self.drillDownIndex];
              self.drillDownIndex++;
              let obj = { [nestedKey]: selectedXValue };
              self.drillDownObject.push(obj);
              let dObject = {
                drillDownIndex : self.drillDownIndex,
                draggedDrillDownColumns :self.draggedDrillDownColumns,
                drillDownObject : self.drillDownObject
              }
              self.setDrilldowns.emit(dObject);
              // self.setOriginalData();
              // self.dataExtraction();
            }
          }
        }
      },
       colors:this.selectedColorScheme,
      labels: this.chartsColumnData.map((category: any) => category === null ? 'null' : category),
      legend: {
        show: this.legendSwitch,
        position: this.legendsAllignment
      },
      dataLabels: {
        enabled: this.dataLabels,
        dropShadow: {
          enabled: false
        }
      },
    };
  }
  sideBySide() {
    const dimensions: Dimension[] = this.dualAxisColumnData;
    const categories = this.flattenDimensions(dimensions);

    this.chartOptions = {
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
      colors: this.selectedColorScheme,
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
      },
      plotOptions: {
        bar: {
          horizontal: false,
          columnWidth: '55%',
          dataLabels: {
            position: this.dataLabelsFontPosition,
          }
        },
      },
      dataLabels: {
        enabled: true,
        formatter: this.formatNumber.bind(this),
        offsetY: -20,
        style: {
          fontSize: this.dataLabelsFontSize,
          fontFamily: this.dataLabelsFontFamily,
          fontWeight: this.isBold ? 700 : 400,
          colors: [this.dataLabelsColor],
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
          offsetX: (this.dimensionAlignment === 'center' ? 0 : (this.dimensionAlignment === 'left' ? -10 : 10)),
          style: {
            // colors: this.color,
            fontSize: this.xLabelFontSize,
            fontFamily: this.xLabelFontFamily,
            fontWeight: this.xlabelFontWeight,
          },
        },
      },
      yaxis: {
        title: {
          text: '',
        },
        labels: {
          show: this.yLabelSwitch,
          offsetY: (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)),
          style: {
            // colors: this.color,
            fontSize: this.yLabelFontSize,
            fontFamily: this.yLabelFontFamily,
            fontWeight: this.ylabelFontWeight,
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
            return val;
          },
        },
      },
      grid: {
        borderColor: this.gridColor,
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
  }
  stockedChart(){
    const dimensions: Dimension[] = this.dualAxisColumnData;
    const categories = this.flattenDimensions(dimensions);

    this.chartOptions = {
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
      colors: this.selectedColorScheme,
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
            position: this.dataLabelsFontPosition,
          }
        }
      },
      xaxis: {
        type: "category",
        categories: categories,
        tickPlacement: 'on',
        labels: {
          show: this.xLabelSwitch,
          offsetX: (this.dimensionAlignment === 'center' ? 0 : (this.dimensionAlignment === 'left' ? -10 : 10)),
          style: {
            colors: [],
            fontSize: this.xLabelFontSize,
            fontFamily: this.xLabelFontFamily,
            fontWeight: this.xlabelFontWeight,
          },
        },
      },
      yaxis: {
        show: true,
        labels: {
          show: this.yLabelSwitch,
          offsetY: (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)),
          style: {
            colors: [],
            fontSize: this.yLabelFontSize,
            fontFamily: this.yLabelFontFamily,
            fontWeight: this.ylabelFontWeight,
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
        borderColor: this.gridColor,
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
          fontSize: this.dataLabelsFontSize,
          fontFamily: this.dataLabelsFontFamily,
          fontWeight: this.isBold ? 700 : 400,
          colors: [this.dataLabelsColor],
        },
      }
    };
  }
  barLineChart(){
    const dimensions: Dimension[] = this.dualAxisColumnData;
    const categories = this.flattenDimensions(dimensions);

    this.chartOptions = {
      series: [
        {
          name: this.dualAxisRowData[0]?.name,
          type: "column",
          data: this.dualAxisRowData[0]?.data,
          color: this.barColor,
          dataLabels: {
            enabled: true,
            offsetX: 0,
            offsetY: (this.dataLabelsBarFontPosition === 'center' ? 0 : (this.dataLabelsBarFontPosition === 'top' ? -10 : 10)),
          },
        },
        {
          name: this.dualAxisRowData[1]?.name,
          type: "line",
          data: this.dualAxisRowData[1]?.data,
          color: this.lineColor,
          dataLabels: {
            enabled: true,
            offsetX: 0,
            offsetY: (this.dataLabelsLineFontPosition === 'center' ? 0 : (this.dataLabelsLineFontPosition === 'left' ? -10 : 10)),
          },
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
        borderColor: this.gridColor,
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
        // offsetY: (this.dataLabelsBarFontPosition === 'center' ? 0 : (this.dataLabelsBarFontPosition === 'top' ? -10 : 10)),
        // offsetX: (this.dataLabelsLineFontPosition === 'center' ? 0 : (this.dataLabelsLineFontPosition === 'left' ? -10 : 10)),
        style: {
          fontSize: this.dataLabelsFontSize,
          fontFamily: this.dataLabelsFontFamily,
          fontWeight: this.isBold ? 700 : 400,
          colors: [this.dataLabelsColor],
        },
        background: {
          enabled: false,
        }
      },
      // labels: categories,
      xaxis: {
        categories: categories,
        type: "",
        tickPlacement: 'on',
        labels: {
          show: this.xLabelSwitch,
          offsetX: (this.dimensionAlignment === 'center' ? 0 : (this.dimensionAlignment === 'left' ? -10 : 10)),
          style: {
            colors: [],
            fontSize: this.xLabelFontSize,
            fontFamily: this.xLabelFontFamily,
            fontWeight: this.xlabelFontWeight,
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
            offsetY: (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)),
            style: {
              colors: [],
              fontSize: this.yLabelFontSize,
              fontFamily: this.yLabelFontFamily,
              fontWeight: this.ylabelFontWeight,
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
            offsetY: (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)),
            style: {
              colors: [],
              fontSize: this.yLabelFontSize,
              fontFamily: this.yLabelFontFamily,
              fontWeight: this.ylabelFontWeight,
            },
            formatter: this.formatNumber.bind(this)
          }
        }
      ],
      plotOptions: {
        bar: {
          dataLabels: {
            position: this.dataLabelsFontPosition,
          }
        }
      }

    };
  }
  hStockedChart(){
    const dimensions: Dimension[] = this.dualAxisColumnData;
    const categories = this.flattenDimensions(dimensions);

    this.chartOptions = {
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
      colors: this.selectedColorScheme,
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
            position: this.dataLabelsFontPosition,
          }
        }
      },
      xaxis: {
        type: "category",
        categories: categories,
        labels: {
          show: this.xLabelSwitch,
          offsetX: (this.dimensionAlignment === 'center' ? 0 : (this.dimensionAlignment === 'right' ? -10 : 10)),
          style: {
            colors: [],
            fontSize: this.xLabelFontSize,
            fontFamily: this.xLabelFontFamily,
            fontWeight: this.xlabelFontWeight,
          },
          formatter: this.formatNumber.bind(this)
        }
      },
      yaxis: {
        show: true,
        labels: {
          show: this.yLabelSwitch,
          offsetY: (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)),
          style: {
            colors: [],
            fontSize: this.yLabelFontSize,
            fontFamily: this.yLabelFontFamily,
            fontWeight: this.ylabelFontWeight,
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
        borderColor: this.gridColor,
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
          fontSize: this.dataLabelsFontSize,
          fontFamily: this.dataLabelsFontFamily,
          fontWeight: this.isBold ? 700 : 400,
          colors: [this.dataLabelsColor],
        },
      }
    };
  }
  hGroupedChart(){
    const dimensions: Dimension[] = this.dualAxisColumnData;
    const categories = this.flattenDimensions(dimensions);

    this.chartOptions = {
      series: this.dualAxisRowData,
      chart: {
        type: "bar",
        height: 430,
        background: this.backgroundColor,
      },
      colors: this.selectedColorScheme,
      plotOptions: {
        bar: {
          horizontal: true,
          dataLabels: {
            position: this.dataLabelsFontPosition
          }
        }
      },
      dataLabels: {
        enabled: true,
        formatter: this.formatNumber.bind(this),
        offsetY: -6,
        style: {
          fontSize: this.dataLabelsFontSize,
          fontFamily: this.dataLabelsFontFamily,
          fontWeight: this.isBold ? 700 : 400,
          colors: [this.dataLabelsColor],
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
          offsetX: (this.dimensionAlignment === 'center' ? 0 : (this.dimensionAlignment === 'right' ? -10 : 10)),
          style: {
            colors: [],
            fontSize: this.xLabelFontSize,
            fontFamily: this.xLabelFontFamily,
            fontWeight: this.xlabelFontWeight,
          },
          formatter: this.formatNumber.bind(this)
        },
      },
      yaxis: {
        show: true,
        labels: {
          show: this.yLabelSwitch,
          offsetY: (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)),
          style: {
            colors: [],
            fontSize: this.yLabelFontSize,
            fontFamily: this.yLabelFontFamily,
            fontWeight: this.ylabelFontWeight,
          },
        },
      },
      grid: {
        show: true,
        borderColor: this.gridColor,
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
  }
  multiLineChart(){
    const dimensions: Dimension[] = this.dualAxisColumnData;
    const categories = this.flattenDimensions(dimensions);

    this.chartOptions = {
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
      colors: this.selectedColorScheme,
      dataLabels: {
        enabled: true,
        formatter: this.formatNumber.bind(this),
        offsetY: -20,
        style: {
          fontSize: this.dataLabelsFontSize,
          fontFamily: this.dataLabelsFontFamily,
          fontWeight: this.isBold ? 700 : 400,
          colors: [this.dataLabelsColor],
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
          offsetX: (this.dimensionAlignment === 'center' ? 0 : (this.dimensionAlignment === 'left' ? -10 : 10)),
          style: {
            colors: [],
            fontSize: this.xLabelFontSize,
            fontFamily: this.xLabelFontFamily,
            fontWeight: this.xlabelFontWeight,
          },
        },
      },
      yaxis: {
        show: true,
        labels: {
          show: this.yLabelSwitch,
          offsetY: (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)),
          style: {
            colors: [],
            fontSize: this.yLabelFontSize,
            fontFamily: this.yLabelFontFamily,
            fontWeight: this.ylabelFontWeight,
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
        borderColor: this.gridColor,
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
  }
  donutChart(){
    const self = this;
    this.chartOptions = {
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
              let dObject = {
                drillDownIndex : self.drillDownIndex,
                draggedDrillDownColumns :self.draggedDrillDownColumns,
                drillDownObject : self.drillDownObject
              }
              self.setDrilldowns.emit(dObject);
              // self.setOriginalData();
              // self.dataExtraction();
            }
          }
        }
      },
      colors: this.selectedColorScheme,
      labels: this.chartsColumnData.map((category: any) => category === null ? 'null' : category),
      // responsive: [
      //   {
      //     breakpoint: 100,
      //     options: {
      //       chart: {
      //         width: 10
      //       },
      //     }
      //   }
      // ],
      legend: {
        show: this.legendSwitch,
        position: this.legendsAllignment
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
                show: this.label,
                showAlways: this.label,
                formatter: (w:any) => {
                  return w.globals.seriesTotals.reduce((a:any, b:any) => {
                    return +a + b
                  }, 0).toFixed(this.donutDecimalPlaces);
                }
              }
            },
            size: this.donutSize+'%'
          }
        }
      },
    };
  }
  heatMapChart(){
    const dimensions: Dimension[] = this.dualAxisColumnData;
    const categories = this.flattenDimensions(dimensions);

    this.chartOptions = {
      series: this.dualAxisRowData,
      chart: {
        height: 350,
        type: 'heatmap',
        background: this.backgroundColor,
      },
      colors: this.selectedColorScheme,
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
          fontSize: this.dataLabelsFontSize,
          fontFamily: this.dataLabelsFontFamily,
          fontWeight: this.isBold ? 700 : 400,
          colors: [this.dataLabelsColor],
        },
        formatter: this.formatNumber.bind(this)
      },
      xaxis: {
        type: 'category',
        categories: categories,
        labels: {
          show: this.xLabelSwitch,
          offsetX: (this.dimensionAlignment === 'center' ? 0 : (this.dimensionAlignment === 'left' ? -10 : 10)),
          style: {
            colors: [],
            fontSize: this.xLabelFontSize,
            fontFamily: this.xLabelFontFamily,
            fontWeight: this.xlabelFontWeight,
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
          offsetY: (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10)),
          style: {
            colors: [],
            fontSize: this.yLabelFontSize,
            fontFamily: this.yLabelFontFamily,
            fontWeight: this.ylabelFontWeight,
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
          lines:false
        },
        yaxis:{
          lines:false
        }
      }
    };
  }
  funnelChart(){
    const dimensions: Dimension[] = this.dualAxisColumnData;
    const categories = this.flattenDimensions(dimensions);

    this.chartOptions = {
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
          distributed : this.isDistributed,
          dataLabels: {
            position:  this.dataLabelsFontPosition,
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
        style: {
          fontSize: this.dataLabelsFontSize,
          fontFamily: this.dataLabelsFontFamily,
          fontWeight: this.isBold ? 700 : 400,
          colors: [this.dataLabelsColor],
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
      colors: this.selectedColorScheme
    };
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
  customMinMaxGuage() {
    this.valueToDivide = this.maxValueGuage - this.minValueGuage;
    this.guageChart1();
  }
  guageChart1() {
    // this.guageNumber = _.cloneDeep(this.tablePreviewRow[0]?.result_data?.[0] ?? 0);
    // this.maxValueGuage = this.maxValueGuage ? this.maxValueGuage:this.KPINumber*2
    //  const valueToDivide = this.maxValueGuage-this.minValueGuage
    // Initialize the chart options
    const self = this;
    this.chartOptions = {
      series: [((this.guageNumber / this.valueToDivide) * 100)], // Correct percentage calculation
      chart: {
        height: 350,
        type: 'radialBar',
        background: this.backgroundColor,
        toolbar: {
          show: true
        },
        events: {
          mounted: function(chartContext:any, config:any) {
            const applyStyles = () => {
              const valueElement = document.querySelector('.apexcharts-datalabel-value') as HTMLElement;
              if (valueElement) {
                valueElement.style.fill = self.dataLabelsColor;
                valueElement.style.setProperty('fill', self.dataLabelsColor, 'important');
              }

              const nameElement = document.querySelector('.apexcharts-datalabel-label') as HTMLElement;
              if (nameElement) {
                nameElement.style.fill = self.dataLabelsColor;
                nameElement.style.setProperty('fill', self.dataLabelsColor, 'important');
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
              color: this.dataLabelsColor,
              fontSize: this.dataLabelsFontSize,
              fontFamily: this.dataLabelsFontFamily,
              fontWeight: this.isBold ? 700 : 400
            },
            value: {
              formatter: (val: any) => `${val.toFixed(2)}%`, // Displaying percentage
              show: true,
              color: this.dataLabelsColor,
              fontSize: this.dataLabelsFontSize,
              fontFamily: this.dataLabelsFontFamily,
              fontWeight: this.isBold ? 700 : 400
            },
          },
          min: this.minValueGuage,  // Use user's min value
          max: this.maxValueGuage
        }
      },

      tooltip: {
        enabled: true,
        shared: false, // Set to false for individual tooltips
        // custom: ({ series }: { series: number[] }) => {
        //   return `<div style="padding: 10px;">
        //                 <strong>Value:</strong> ${this.guageNumber}<br>
        //                 <strong>Percentage:</strong> ${series[0].toFixed(2)}%
        //             </div>`;
        // }
      },
      stroke: {
        lineCap: "round"
      },
      labels: [this.tablePreviewRow[0]?.col ?? 'Label'], // Fallback for label
    };
  }

  dimensionsFontFamilyChange() {
    if (this.chartOptions?.xaxis?.labels?.style?.fontFamily) {
      this.chartOptions.xaxis.labels.style.fontFamily = this.xLabelFontFamily;

      let object = { xaxis: this.chartOptions.xaxis };
      if (this.barCharts) {
        this.barCharts.updateOptions(object);
      }
      else if (this.areaCharts) {
        this.areaCharts.updateOptions(object);
      }
      else if (this.lineCharts) {
        this.lineCharts.updateOptions(object);
      }
      else if (this.sideBySideCharts) {
        this.sideBySideCharts.updateOptions(object);
      }
      else if (this.stockedCharts) {
        this.stockedCharts.updateOptions(object);
      }
      else if (this.barLineCharts) {
        this.barLineCharts.updateOptions(object);
      }
      else if (this.horizontalStockedCharts) {
        this.horizontalStockedCharts.updateOptions(object);
      }
      else if (this.groupedCharts) {
        this.groupedCharts.updateOptions(object);
      }
      else if (this.multiLineCharts) {
        this.multiLineCharts.updateOptions(object);
      }
      else if (this.heatmapCharts) {
        this.heatmapCharts.updateOptions(object);
      }
    }
  }
  dimensionsFontSizeChange() {
    if (this.chartOptions?.xaxis?.labels?.style?.fontSize) {
      this.chartOptions.xaxis.labels.style.fontSize = this.xLabelFontSize;

      let object = { xaxis: this.chartOptions.xaxis };
      if (this.barCharts) {
        this.barCharts.updateOptions(object);
      }
      else if (this.areaCharts) {
        this.areaCharts.updateOptions(object);
      }
      else if (this.lineCharts) {
        this.lineCharts.updateOptions(object);
      }
      else if (this.sideBySideCharts) {
        this.sideBySideCharts.updateOptions(object);
      }
      else if (this.stockedCharts) {
        this.stockedCharts.updateOptions(object);
      }
      else if (this.barLineCharts) {
        this.barLineCharts.updateOptions(object);
      }
      else if (this.horizontalStockedCharts) {
        this.horizontalStockedCharts.updateOptions(object);
      }
      else if (this.groupedCharts) {
        this.groupedCharts.updateOptions(object);
      }
      else if (this.multiLineCharts) {
        this.multiLineCharts.updateOptions(object);
      }
      else if (this.heatmapCharts) {
        this.heatmapCharts.updateOptions(object);
      }
    }
  }
  dimensionsFontWeightChange(){
    if(this.chartOptions?.xaxis?.labels?.style?.fontWeight){
      this.chartOptions.xaxis.labels.style.fontWeight = this.xlabelFontWeight;
    
    let object = { xaxis:  this.chartOptions.xaxis };
    if (this.barCharts) {
      this.barCharts.updateOptions(object);
    }
    else if (this.areaCharts) {
      this.areaCharts.updateOptions(object);
    }
    else if (this.lineCharts) {
      this.lineCharts.updateOptions(object);
    }
    else if (this.sideBySideCharts) {
      this.sideBySideCharts.updateOptions(object);
    }
    else if (this.stockedCharts) {
      this.stockedCharts.updateOptions(object);
    }
    else if (this.barLineCharts) {
      this.barLineCharts.updateOptions(object);
    }
    else if (this.horizontalStockedCharts) {
      this.horizontalStockedCharts.updateOptions(object);
    }
    else if (this.groupedCharts) {
      this.groupedCharts.updateOptions(object);
    }
    else if (this.multiLineCharts) {
      this.multiLineCharts.updateOptions(object);
    }
    else if (this.heatmapCharts) {
      this.heatmapCharts.updateOptions(object);
    }
  }
  }
  dimensionsAlignmentChange(){
    if(this.chartOptions?.xaxis?.labels && (this.barCharts || this.areaCharts || this.lineCharts || this.sideBySideCharts || this.stockedCharts || this.barLineCharts || this.horizontalStockedCharts || this.groupedCharts || this.multiLineCharts || this.heatmapCharts)){
      this.chartOptions.xaxis.labels.offsetX = (this.dimensionAlignment === 'center' ? 0 : (this.dimensionAlignment === 'left' ? -10 : 10));
    
    let object = { xaxis:  this.chartOptions.xaxis };
    if (this.barCharts) {
      this.barCharts.updateOptions(object);
    }
    else if (this.areaCharts) {
      this.areaCharts.updateOptions(object);
    }
    else if (this.lineCharts) {
      this.lineCharts.updateOptions(object);
    }
    else if (this.sideBySideCharts) {
      this.sideBySideCharts.updateOptions(object);
    }
    else if (this.stockedCharts) {
      this.stockedCharts.updateOptions(object);
    }
    else if (this.barLineCharts) {
      this.barLineCharts.updateOptions(object);
    }
    else if (this.horizontalStockedCharts) {
      this.chartOptions.xaxis.labels.offsetX = (this.dimensionAlignment === 'center' ? 0 : (this.dimensionAlignment === 'right' ? -10 : 10));
      object = { xaxis:  this.chartOptions.xaxis };
      this.horizontalStockedCharts.updateOptions(object);
    }
    else if (this.groupedCharts) {
      this.chartOptions.xaxis.labels.offsetX = (this.dimensionAlignment === 'center' ? 0 : (this.dimensionAlignment === 'right' ? -10 : 10));
      object = { xaxis:  this.chartOptions.xaxis };
      this.groupedCharts.updateOptions(object);
    }
    else if (this.multiLineCharts) {
      this.multiLineCharts.updateOptions(object);
    }
    else if (this.heatmapCharts) {
      this.heatmapCharts.updateOptions(object);
    }
  }
  }
  measuresFontFamilyChange(){
    if(this.chartOptions?.yaxis){
      if (this.chartOptions.yaxis.length > 0) {
        (this.chartOptions.yaxis as any[]).forEach((data) => {
          if(data?.labels?.style?.fontFamily){
            data.labels.style.fontFamily = this.yLabelFontFamily;
          }
        })
      }
      else {
        if(this.chartOptions?.yaxis?.labels?.style?.fontFamily){
          this.chartOptions.yaxis.labels.style.fontFamily = this.yLabelFontFamily;
        }
      }
    
    let object = {yaxis: this.chartOptions.yaxis};
    if (this.barCharts) {
      this.barCharts.updateOptions(object);
    }
    else if (this.areaCharts) {
      this.areaCharts.updateOptions(object);
    }
    else if (this.lineCharts) {
      this.lineCharts.updateOptions(object);
    }
    else if (this.sideBySideCharts) {
      this.sideBySideCharts.updateOptions(object);
    }
    else if (this.stockedCharts) {
      this.stockedCharts.updateOptions(object);
    }
    else if (this.barLineCharts) {
      this.barLineCharts.updateOptions(object);
    }
    else if (this.horizontalStockedCharts) {
      this.horizontalStockedCharts.updateOptions(object);
    }
    else if (this.groupedCharts) {
      this.groupedCharts.updateOptions(object);
    }
    else if (this.multiLineCharts) {
      this.multiLineCharts.updateOptions(object);
    }
    else if (this.heatmapCharts) {
      this.heatmapCharts.updateOptions(object);
    }
  }
  }
  measuresFontSizeChange(){
    if(this.chartOptions?.yaxis){
      if (this.chartOptions.yaxis.length > 0) {
        (this.chartOptions.yaxis as any[]).forEach((data) => {
          if(data?.labels?.style?.fontSize){
            data.labels.style.fontSize = this.yLabelFontSize;
          }
        })
      }
      else {
        if(this.chartOptions?.yaxis?.labels?.style?.fontSize){
          this.chartOptions.yaxis.labels.style.fontSize = this.yLabelFontSize;
        }
      }
    
    let object = {yaxis: this.chartOptions.yaxis};
    if (this.barCharts) {
      this.barCharts.updateOptions(object);
    }
    else if (this.areaCharts) {
      this.areaCharts.updateOptions(object);
    }
    else if (this.lineCharts) {
      this.lineCharts.updateOptions(object);
    }
    else if (this.sideBySideCharts) {
      this.sideBySideCharts.updateOptions(object);
    }
    else if (this.stockedCharts) {
      this.stockedCharts.updateOptions(object);
    }
    else if (this.barLineCharts) {
      this.barLineCharts.updateOptions(object);
    }
    else if (this.horizontalStockedCharts) {
      this.horizontalStockedCharts.updateOptions(object);
    }
    else if (this.groupedCharts) {
      this.groupedCharts.updateOptions(object);
    }
    else if (this.multiLineCharts) {
      this.multiLineCharts.updateOptions(object);
    }
    else if (this.heatmapCharts) {
      this.heatmapCharts.updateOptions(object);
    }
  }
  }
  measuresFontWeightChange(){
    if(this.chartOptions?.yaxis){
      if (this.chartOptions.yaxis.length > 0) {
        (this.chartOptions.yaxis as any[]).forEach((data) => {
          if(data?.labels?.style?.fontWeight){
            data.labels.style.fontWeight = this.ylabelFontWeight;
          }
        })
      }
      else {
        if(this.chartOptions?.yaxis?.labels?.style?.fontWeight){
          this.chartOptions.yaxis.labels.style.fontWeight = this.ylabelFontWeight;
        }
      }
    
    let object = {yaxis: this.chartOptions.yaxis};
    if (this.barCharts) {
      this.barCharts.updateOptions(object);
    }
    else if (this.areaCharts) {
      this.areaCharts.updateOptions(object);
    }
    else if (this.lineCharts) {
      this.lineCharts.updateOptions(object);
    }
    else if (this.sideBySideCharts) {
      this.sideBySideCharts.updateOptions(object);
    }
    else if (this.stockedCharts) {
      this.stockedCharts.updateOptions(object);
    }
    else if (this.barLineCharts) {
      this.barLineCharts.updateOptions(object);
    }
    else if (this.horizontalStockedCharts) {
      this.horizontalStockedCharts.updateOptions(object);
    }
    else if (this.groupedCharts) {
      this.groupedCharts.updateOptions(object);
    }
    else if (this.multiLineCharts) {
      this.multiLineCharts.updateOptions(object);
    }
    else if (this.heatmapCharts) {
      this.heatmapCharts.updateOptions(object);
    }
  }
  }
  measuresAlignmentChange(){
    if(this.chartOptions?.yaxis){
      if (this.chartOptions.yaxis.length > 0) {
        (this.chartOptions.yaxis as any[]).forEach((data) => {
          if(data?.labels){
            data.labels.offsetY = (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10));
          }
        })
      }
      else {
        if(this.chartOptions?.yaxis?.labels){
          this.chartOptions.yaxis.labels.offsetY = (this.measureAlignment === 'center' ? 0 : (this.measureAlignment === 'top' ? -10 : 10));
        }
      }
    
    let object = {yaxis: this.chartOptions.yaxis};
    if (this.barCharts) {
      this.barCharts.updateOptions(object);
    }
    else if (this.areaCharts) {
      this.areaCharts.updateOptions(object);
    }
    else if (this.lineCharts) {
      this.lineCharts.updateOptions(object);
    }
    else if (this.sideBySideCharts) {
      this.sideBySideCharts.updateOptions(object);
    }
    else if (this.stockedCharts) {
      this.stockedCharts.updateOptions(object);
    }
    else if (this.barLineCharts) {
      this.barLineCharts.updateOptions(object);
    }
    else if (this.horizontalStockedCharts) {
      this.horizontalStockedCharts.updateOptions(object);
    }
    else if (this.groupedCharts) {
      this.groupedCharts.updateOptions(object);
    }
    else if (this.multiLineCharts) {
      this.multiLineCharts.updateOptions(object);
    }
    else if (this.heatmapCharts) {
      this.heatmapCharts.updateOptions(object);
    }
  }
  }
  setDataLabelsFontFamily(){
    let object;
    if(this.guageCharts){
      if(this.chartOptions?.plotOptions?.radialBar?.dataLabels?.value?.fontFamily){
        this.chartOptions.plotOptions.radialBar.dataLabels.value.fontFamily = this.dataLabelsFontFamily;
      }
      object = {plotOptions : this.chartOptions.plotOptions};
    } else{
      if(this.chartOptions?.dataLabels?.style?.fontFamily){
        this.chartOptions.dataLabels.style.fontFamily = this.dataLabelsFontFamily;
      }
      object = { dataLabels: this.chartOptions.dataLabels};
    }

    if (this.barCharts) {
      this.barCharts.updateOptions(object);
    }
    else if (this.areaCharts) {
      this.areaCharts.updateOptions(object);
    }
    else if (this.lineCharts) {
      this.lineCharts.updateOptions(object);
    }
    else if (this.sideBySideCharts) {
      this.sideBySideCharts.updateOptions(object);
    }
    else if (this.stockedCharts) {
      this.stockedCharts.updateOptions(object);
    }
    else if (this.barLineCharts) {
      this.barLineCharts.updateOptions(object);
    }
    else if (this.horizontalStockedCharts) {
      this.horizontalStockedCharts.updateOptions(object);
    }
    else if (this.groupedCharts) {
      this.groupedCharts.updateOptions(object);
    }
    else if (this.multiLineCharts) {
      this.multiLineCharts.updateOptions(object);
    }
    else if (this.heatmapCharts) {
      this.heatmapCharts.updateOptions(object);
    } 
    else if(this.funnelCharts) {
      this.funnelCharts.updateOptions(object);
    }
    else if(this.guageCharts){
      this.guageCharts.updateOptions(object);
    }
  }
  setDataLabelsFontSize(){
    let object;
    if(this.guageCharts){
      if(this.chartOptions?.plotOptions?.radialBar?.dataLabels?.value?.fontSize){
        this.chartOptions.plotOptions.radialBar.dataLabels.value.fontSize = this.dataLabelsFontSize;
      }
      object = {plotOptions : this.chartOptions.plotOptions};
    } else{
      if(this.chartOptions?.dataLabels?.style?.fontSize){
        this.chartOptions.dataLabels.style.fontSize = this.dataLabelsFontSize;
      }
      object = { dataLabels: this.chartOptions.dataLabels};
    }

    if (this.barCharts) {
      this.barCharts.updateOptions(object);
    }
    else if (this.areaCharts) {
      this.areaCharts.updateOptions(object);
    }
    else if (this.lineCharts) {
      this.lineCharts.updateOptions(object);
    }
    else if (this.sideBySideCharts) {
      this.sideBySideCharts.updateOptions(object);
    }
    else if (this.stockedCharts) {
      this.stockedCharts.updateOptions(object);
    }
    else if (this.barLineCharts) {
      this.barLineCharts.updateOptions(object);
    }
    else if (this.horizontalStockedCharts) {
      this.horizontalStockedCharts.updateOptions(object);
    }
    else if (this.groupedCharts) {
      this.groupedCharts.updateOptions(object);
    }
    else if (this.multiLineCharts) {
      this.multiLineCharts.updateOptions(object);
    }
    else if (this.heatmapCharts) {
      this.heatmapCharts.updateOptions(object);
    } 
    else if(this.funnelCharts) {
      this.funnelCharts.updateOptions(object);
    }
    else if(this.guageCharts){
      this.guageCharts.updateOptions(object);
    }
  }
  setDataLabelsLineFontPosition(){
    if(this.barLineCharts){
    if(this.dataLabelsLineFontPosition === 'center')
    {
    this.chartOptions.dataLabels.offsetY = '0';
    let object = {dataLabels:this.chartOptions.dataLabels}
    this.barLineCharts.updateOptions(object);
    }
    if(this.dataLabelsLineFontPosition === 'top')
      {
      this.chartOptions.dataLabels.offsetY = '-10';
      let object = {dataLabels:this.chartOptions.dataLabels}
      this.barLineCharts.updateOptions(object);
      }
      if(this.dataLabelsLineFontPosition === 'bottom')
        {
        this.chartOptions.dataLabels.offsetY = '10';
        let object = {dataLabels:this.chartOptions.dataLabels}
        this.barLineCharts.updateOptions(object);
        }
      }
  }
  setDataLabelsBarFontPosition(){
    if(this.barLineCharts){
      if(this.dataLabelsLineFontPosition === 'center')
      {
      this.chartOptions.series[0].dataLabels.offsetY = '0';
      let object = {series:[{dataLabels:{offsetY:'0'}},
        {

        }
      ]}
      this.barLineCharts.updateOptions(object);
      }
      if(this.dataLabelsLineFontPosition === 'top')
        {
        this.chartOptions.dataLabels.offsetX = '-10';
        let object = {dataLabels:this.chartOptions.dataLabels}
        this.barLineCharts.updateOptions(object);
        }
        if(this.dataLabelsLineFontPosition === 'bottom')
          {
          this.chartOptions.dataLabels.offsetX = '10';
          let object = {dataLabels:this.chartOptions.dataLabels}
          this.barLineCharts.updateOptions(object);
          }
        }
  }
  setDataLabelsFontWeight(){
    let object;
    if(this.guageCharts){
      if(this.chartOptions?.plotOptions?.radialBar?.dataLabels?.value?.fontWeight){
        this.chartOptions.plotOptions.radialBar.dataLabels.value.fontWeight = this.isBold ? 700 : 400;
      }
      object = {plotOptions : this.chartOptions.plotOptions};
    } else{
      if(this.chartOptions?.dataLabels?.style?.fontWeight){
        this.chartOptions.dataLabels.style.fontWeight = this.isBold ? 700 : 400;
      }
      object = { dataLabels: this.chartOptions.dataLabels};
    }

    if (this.barCharts) {
      this.barCharts.updateOptions(object);
    }
    else if (this.areaCharts) {
      this.areaCharts.updateOptions(object);
    }
    else if (this.lineCharts) {
      this.lineCharts.updateOptions(object);
    }
    else if (this.sideBySideCharts) {
      this.sideBySideCharts.updateOptions(object);
    }
    else if (this.stockedCharts) {
      this.stockedCharts.updateOptions(object);
    }
    else if (this.barLineCharts) {
      this.barLineCharts.updateOptions(object);
    }
    else if (this.horizontalStockedCharts) {
      this.horizontalStockedCharts.updateOptions(object);
    }
    else if (this.groupedCharts) {
      this.groupedCharts.updateOptions(object);
    }
    else if (this.multiLineCharts) {
      this.multiLineCharts.updateOptions(object);
    }
    else if (this.heatmapCharts) {
      this.heatmapCharts.updateOptions(object);
    } 
    else if(this.funnelCharts) {
      this.funnelCharts.updateOptions(object);
    }
    else if(this.guageCharts){
      this.guageCharts.updateOptions(object);
    }
  }
  dataLabelsFontColor(){
    let object;
    if(this.guageCharts){
      if(this.chartOptions?.plotOptions?.radialBar?.dataLabels?.value?.color){
        this.chartOptions.plotOptions.radialBar.dataLabels.value.color = this.dataLabelsColor;
      }
      object = {plotOptions : this.chartOptions.plotOptions};
    } else{
      if(this.chartOptions?.dataLabels?.style?.colors){
        this.chartOptions.dataLabels.style.colors = [this.dataLabelsColor];
      }
      object = { dataLabels: this.chartOptions.dataLabels};
    }

    if (this.barCharts) {
      this.barCharts.updateOptions(object);
    }
    else if (this.areaCharts) {
      this.areaCharts.updateOptions(object);
    }
    else if (this.lineCharts) {
      this.lineCharts.updateOptions(object);
    }
    else if (this.sideBySideCharts) {
      this.sideBySideCharts.updateOptions(object);
    }
    else if (this.stockedCharts) {
      this.stockedCharts.updateOptions(object);
    }
    else if (this.barLineCharts) {
      this.barLineCharts.updateOptions(object);
    }
    else if (this.horizontalStockedCharts) {
      this.horizontalStockedCharts.updateOptions(object);
    }
    else if (this.groupedCharts) {
      this.groupedCharts.updateOptions(object);
    }
    else if (this.multiLineCharts) {
      this.multiLineCharts.updateOptions(object);
    }
    else if (this.heatmapCharts) {
      this.heatmapCharts.updateOptions(object);
    } 
    else if(this.funnelCharts) {
      this.funnelCharts.updateOptions(object);
    }
    else if(this.guageCharts){
      this.guageCharts.updateOptions(object);
    }
  }
  setDataLabelsFontPosition(){
    let object;
    if(this.areaCharts || this.lineCharts || this.multiLineCharts){
      if(this.chartOptions?.dataLabels){
        this.chartOptions.dataLabels.offsetY = (this.dataLabelsFontPosition === 'top') ? -10 : ((this.dataLabelsFontPosition === 'center') ? 0 : 10);
      }
      object = {dataLabels : this.chartOptions.dataLabels};
    } else{
      if(this.chartOptions?.plotOptions?.bar?.dataLabels?.position){
        this.chartOptions.plotOptions.bar.dataLabels.position = this.dataLabelsFontPosition;
      }
      object = { plotOptions: this.chartOptions.plotOptions};
    }

    if (this.barCharts) {
      this.barCharts.updateOptions(object);
    }
    else if (this.areaCharts) {
      this.areaCharts.updateOptions(object);
    }
    else if (this.lineCharts) {
      this.lineCharts.updateOptions(object);
    }
    else if (this.sideBySideCharts) {
      this.sideBySideCharts.updateOptions(object);
    }
    else if (this.stockedCharts) {
      this.stockedCharts.updateOptions(object);
    }
    else if (this.barLineCharts) {
      this.barLineCharts.updateOptions(object);
    }
    else if (this.horizontalStockedCharts) {
      this.horizontalStockedCharts.updateOptions(object);
    }
    else if (this.groupedCharts) {
      this.groupedCharts.updateOptions(object);
    }
    else if (this.heatmapCharts) {
      this.heatmapCharts.updateOptions(object);
    } 
    else if(this.funnelCharts) {
      this.funnelCharts.updateOptions(object);
    }
    else if(this.multiLineCharts) {
      this.multiLineCharts.updateOptions(object);
    }
  }
  xLabelShowOrHide(){
    if(this.chartOptions?.xaxis?.labels){
      this.chartOptions.xaxis.labels.show = this.xLabelSwitch;
    
    let object = { xaxis:  this.chartOptions.xaxis };
    if (this.barCharts) {
      this.barCharts.updateOptions(object);
    }
    else if (this.areaCharts) {
      this.areaCharts.updateOptions(object);
    }
    else if (this.lineCharts) {
      this.lineCharts.updateOptions(object);
    }
    else if (this.sideBySideCharts) {
      this.sideBySideCharts.updateOptions(object);
    }
    else if (this.stockedCharts) {
      this.stockedCharts.updateOptions(object);
    }
    else if (this.barLineCharts) {
      this.barLineCharts.updateOptions(object);
    }
    else if (this.horizontalStockedCharts) {
      this.horizontalStockedCharts.updateOptions(object);
    }
    else if (this.groupedCharts) {
      this.groupedCharts.updateOptions(object);
    }
    else if (this.multiLineCharts) {
      this.multiLineCharts.updateOptions(object);
    }
    else if (this.heatmapCharts) {
      this.heatmapCharts.updateOptions(object);
    }
  }
  }
  yLabelShowOrHide(){
    if(this.chartOptions?.yaxis){
      if (this.chartOptions.yaxis.length > 0) {
        (this.chartOptions.yaxis as any[]).forEach((data) => {
          if(data?.labels){
            data.labels.show = this.yLabelSwitch;
          }
        })
      }
      else {
        if(this.chartOptions?.yaxis?.labels){
          this.chartOptions.yaxis.labels.show = this.yLabelSwitch;
        }
      }
    
    let object = {yaxis: this.chartOptions.yaxis};
    if (this.barCharts) {
      this.barCharts.updateOptions(object);
    }
    else if (this.areaCharts) {
      this.areaCharts.updateOptions(object);
    }
    else if (this.lineCharts) {
      this.lineCharts.updateOptions(object);
    }
    else if (this.sideBySideCharts) {
      this.sideBySideCharts.updateOptions(object);
    }
    else if (this.stockedCharts) {
      this.stockedCharts.updateOptions(object);
    }
    else if (this.barLineCharts) {
      this.barLineCharts.updateOptions(object);
    }
    else if (this.horizontalStockedCharts) {
      this.horizontalStockedCharts.updateOptions(object);
    }
    else if (this.groupedCharts) {
      this.groupedCharts.updateOptions(object);
    }
    else if (this.multiLineCharts) {
      this.multiLineCharts.updateOptions(object);
    }
    else if (this.heatmapCharts) {
      this.heatmapCharts.updateOptions(object);
    }
  }
  }
  xGridShowOrHide(){
    if(this.chartOptions?.grid?.xaxis?.lines){
      this.chartOptions.grid.xaxis.lines.show = this.xGridSwitch;
    
    let object = { grid:  this.chartOptions.grid };
    if (this.barCharts) {
      this.barCharts.updateOptions(object);
    }
    else if (this.areaCharts) {
      this.areaCharts.updateOptions(object);
    }
    else if (this.lineCharts) {
      this.lineCharts.updateOptions(object);
    }
    else if (this.sideBySideCharts) {
      this.sideBySideCharts.updateOptions(object);
    }
    else if (this.stockedCharts) {
      this.stockedCharts.updateOptions(object);
    }
    else if (this.barLineCharts) {
      this.barLineCharts.updateOptions(object);
    }
    else if (this.horizontalStockedCharts) {
      this.horizontalStockedCharts.updateOptions(object);
    }
    else if (this.groupedCharts) {
      this.groupedCharts.updateOptions(object);
    }
    else if (this.multiLineCharts) {
      this.multiLineCharts.updateOptions(object);
    }
    else if (this.heatmapCharts) {
      this.heatmapCharts.updateOptions(object);
    }
    }
  }
  yGridShowOrHide(){
    if(this.chartOptions?.grid?.yaxis?.lines){
      this.chartOptions.grid.yaxis.lines.show = this.yGridSwitch;
    
    let object = { grid:  this.chartOptions.grid };
    if (this.barCharts) {
      this.barCharts.updateOptions(object);
    }
    else if (this.areaCharts) {
      this.areaCharts.updateOptions(object);
    }
    else if (this.lineCharts) {
      this.lineCharts.updateOptions(object);
    }
    else if (this.sideBySideCharts) {
      this.sideBySideCharts.updateOptions(object);
    }
    else if (this.stockedCharts) {
      this.stockedCharts.updateOptions(object);
    }
    else if (this.barLineCharts) {
      this.barLineCharts.updateOptions(object);
    }
    else if (this.horizontalStockedCharts) {
      this.horizontalStockedCharts.updateOptions(object);
    }
    else if (this.groupedCharts) {
      this.groupedCharts.updateOptions(object);
    }
    else if (this.multiLineCharts) {
      this.multiLineCharts.updateOptions(object);
    }
    else if (this.heatmapCharts) {
      this.heatmapCharts.updateOptions(object);
    }
  }
  }
  legendsShowOrHide(){
    if(this.chartOptions?.legend){
      this.chartOptions.legend.show = this.legendSwitch;
    
    let object = { legend:  this.chartOptions.legend };
    if (this.pieCharts) {
      this.pieCharts.updateOptions(object);
    }
    else if (this.donutCharts) {
      this.donutCharts.updateOptions(object);
    }
  }
  }
  dataLabelsShowOrHide(){
    if(this.chartOptions?.dataLabels){
      this.chartOptions.dataLabels.enabled = this.dataLabels;
    
    let object = { dataLabels:  this.chartOptions.dataLabels };
    if (this.pieCharts) {
      this.pieCharts.updateOptions(object);
    }
    else if (this.donutCharts) {
      this.donutCharts.updateOptions(object);
    }
  }
  }
  labelsShowOrHide(){
    if (this.donutCharts) {
      this.chartOptions.plotOptions.pie.donut.labels.show = this.label;
      let object = { plotOptions:  this.chartOptions.plotOptions };
      this.donutCharts.updateOptions(object);
    }
  }
  colorDistribution(){
    if (this.funnelCharts) {
      this.chartOptions.colors = this.isDistributed ? [] : [this.color];
      this.chartOptions.plotOptions.bar.distributed = this.isDistributed;
      let object = { colors: this.chartOptions.colors, plotOptions: this.chartOptions.plotOptions };
      this.funnelCharts.updateOptions(object);
    }
  }
  legendPositionChange(){
    if(this.chartOptions?.legend?.position){
      this.chartOptions.legend.position = this.legendsAllignment;
    
    let object = { legend:  this.chartOptions.legend };
    if (this.pieCharts) {
      this.pieCharts.updateOptions(object);
    }
    else if (this.donutCharts) {
      this.donutCharts.updateOptions(object);
    }
  }
  }
  donutSizeChange(){
    if (this.donutCharts) {
      this.chartOptions.plotOptions.pie.donut.size = this.donutSize+'%';
      let object = { plotOptions:  this.chartOptions.plotOptions };
      this.donutCharts.updateOptions(object);
    }
  }
  setBackgroundColor() {
    if(this.chartOptions?.chart?.background){
      this.chartOptions.chart.background = this.backgroundColor;
    
    let object = { chart: this.chartOptions.chart };

    if (this.barCharts) {
      this.barCharts.updateOptions(object);
    }
    else if (this.areaCharts) {
      this.areaCharts.updateOptions(object);
    }
    else if (this.lineCharts) {
      this.lineCharts.updateOptions(object);
    }
    else if (this.sideBySideCharts) {
      this.sideBySideCharts.updateOptions(object);
    }
    else if (this.stockedCharts) {
      this.stockedCharts.updateOptions(object);
    }
    else if (this.barLineCharts) {
      this.barLineCharts.updateOptions(object);
    }
    else if (this.horizontalStockedCharts) {
      this.horizontalStockedCharts.updateOptions(object);
    }
    else if (this.groupedCharts) {
      this.groupedCharts.updateOptions(object);
    }
    else if (this.heatmapCharts) {
      this.heatmapCharts.updateOptions(object);
    }
    else if (this.funnelCharts) {
      this.funnelCharts.updateOptions(object);
    }
    else if (this.pieCharts) {
      this.pieCharts.updateOptions(object);
    }
    else if (this.donutCharts) {
      this.donutCharts.updateOptions(object);
    }
    else if (this.guageCharts) {
      this.guageCharts.updateOptions(object);
    }

  }
  }
  setChartColor(){
    let object;
    if(this.chartType === 'barline'){
      if(this.chartOptions?.series[0]?.color || this.chartOptions?.series[1]?.color){
        this.chartOptions.series[0].color = this.barColor;
        this.chartOptions.series[1].color = this.lineColor;
      }
      object = { series: this.chartOptions.series };
    }
    // else if(this.funnelCharts){
    //   if(this.chartOptions?.colors){
    //     this.chartOptions.colors = this.isDistributed ? [] : [this.color];
    //   }
    //   object = { colors: this.chartOptions.colors }
    // }
    else if(['sidebyside','stocked','hstocked','hgrouped','multiline','heatmap','funnel','pie','donut'].includes(this.chartType))  {
      this.chartOptions.colors = this.selectedColorScheme
      object = { colors: this.chartOptions.colors };
    }
    else if(['bar','area','line','guage'].includes(this.chartType)){
      if(this.chartOptions?.colors){
        // if(this.chartType === 'funnel'){
        //   this.chartOptions.colors = this.selectedColorScheme;
        // }
        // else{
          this.chartOptions.colors = [this.color];
        // }
      }
      object = { colors: this.chartOptions.colors };
    }

    if (this.chartType === 'bar') {
      this.barCharts?.updateOptions(object);
    }
    else if (this.chartType === 'area') {
      this.areaCharts?.updateOptions(object);
    }
    else if (this.chartType === 'line') {
      this.lineCharts?.updateOptions(object);
    }
    else if (this.chartType === 'barline') {
      this.barLineCharts?.updateOptions(object);
    }
    else if (this.chartType === 'funnel') {
      this.funnelCharts?.updateOptions(object);
    }
    else if (this.chartType === 'guage') {
      this.guageCharts?.updateOptions(object);
    }
    else if(this.chartType === 'sidebyside'){
      this.sideBySideCharts?.updateOptions(object);
    }
    else if(this.chartType === 'pie'){
      this.pieCharts?.updateOptions(object);
    }
    else if(this.chartType === 'donut'){
      this.donutCharts?.updateOptions(object);
    }
    else if(this.chartType === 'stocked'){
      this.stockedCharts?.updateOptions(object);
    }
    else if(this.chartType === 'hstocked'){
      this.horizontalStockedCharts?.updateOptions(object);
    }
    else if(this.chartType === 'hgrouped'){
      this.groupedCharts?.updateOptions(object);
    }
    else if(this.chartType === 'multiline'){
      this.multiLineCharts?.updateOptions(object);
    }
    else if(this.chartType === 'heatmap'){
      this.heatmapCharts?.updateOptions(object);
    }
  }
  gridLineColor(){
    if(this.chartOptions?.grid?.borderColor){
      this.chartOptions.grid.borderColor = this.gridColor;
    
    let object = { grid: this.chartOptions.grid };

    if (this.barCharts) {
      this.barCharts.updateOptions(object);
    }
    else if (this.areaCharts) {
      this.areaCharts.updateOptions(object);
    }
    else if (this.lineCharts) {
      this.lineCharts.updateOptions(object);
    }
    else if (this.sideBySideCharts) {
      this.sideBySideCharts.updateOptions(object);
    }
    else if (this.stockedCharts) {
      this.stockedCharts.updateOptions(object);
    }
    else if (this.barLineCharts) {
      this.barLineCharts.updateOptions(object);
    }
    else if (this.horizontalStockedCharts) {
      this.horizontalStockedCharts.updateOptions(object);
    }
    else if (this.groupedCharts) {
      this.groupedCharts.updateOptions(object);
    }
    else if (this.multiLineCharts) {
      this.multiLineCharts.updateOptions(object);
    }
  }
  }
  formatNumber(value: number): string {
    let formattedNumber = value + '';

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
        formattedNumber = (value / 1).toFixed(this.decimalPlaces);
        break;
    }
    this.formattedData.push(this.prefix + formattedNumber + this.suffix);
    return this.prefix + formattedNumber + this.suffix;
  }
  updateNumberFormat() {
    let object;
    if (this.horizontalStockedCharts || this.groupedCharts) {
      if(this.chartOptions?.dataLabels?.formatter){
        this.chartOptions.dataLabels.formatter = this.formatNumber.bind(this);
      }
      if(this.chartOptions?.xaxis?.labels?.formatter){
        this.chartOptions.xaxis.labels.formatter = this.formatNumber.bind(this);
      }
      object = { dataLabels: this.chartOptions.dataLabels, xaxis: this.chartOptions.xaxis };
    }
    else if (this.heatmapCharts) {
      if(this.chartOptions?.dataLabels?.formatter){
        this.chartOptions.dataLabels.formatter = this.formatNumber.bind(this);
      }
      object = { dataLabels: this.chartOptions.dataLabels };
    }
    else if (this.funnelCharts) {
      if(this.chartOptions?.dataLabels?.formatter){
        this.chartOptions.dataLabels.formatter = (val: any, opts: any) => {
          const category = opts.w.config.xaxis.categories[opts.dataPointIndex];
          const formattedValue = this.formatNumber(val);
          return `${category}: ${formattedValue}`;
        }
      }
      object = { dataLabels: this.chartOptions.dataLabels };
    }
    else if(this.donutCharts){
      if(this.chartOptions?.plotOptions?.pie?.donut?.labels?.total?.formatter){
        this.chartOptions.plotOptions.pie.donut.labels.total.formatter = (w:any) => {
          return w.globals.seriesTotals.reduce((a:any, b:any) => {
            return +a + b
          }, 0).toFixed(this.donutDecimalPlaces);
        }
      }
      object = { plotOptions: this.chartOptions.plotOptions };
    }
    else if(!(this.pieCharts || this.guageCharts)) {
      if(this.chartOptions?.dataLabels?.formatter){
        this.chartOptions.dataLabels.formatter = this.formatNumber.bind(this);
      }
      if(this.chartOptions?.yaxis){
        if (this.chartOptions.yaxis.length > 0) {
          (this.chartOptions.yaxis as any[]).forEach((data) => {
            if(data?.labels?.formatter){
              data.labels.formatter = this.formatNumber.bind(this);
            }
          });
        }
        else {
          if(this.chartOptions?.yaxis?.labels?.formatter){
            this.chartOptions.yaxis.labels.formatter = this.formatNumber.bind(this);
          }
        }
      }
      object = { dataLabels: this.chartOptions.dataLabels, yaxis: this.chartOptions.yaxis };
    }

    if (this.barCharts) {
      this.barCharts.updateOptions(object);
    }
    else if (this.areaCharts) {
      this.areaCharts.updateOptions(object);
    }
    else if (this.lineCharts) {
      this.lineCharts.updateOptions(object);
    }
    else if (this.sideBySideCharts) {
      this.sideBySideCharts.updateOptions(object);
    }
    else if (this.stockedCharts) {
      this.stockedCharts.updateOptions(object);
    }
    else if (this.barLineCharts) {
      this.barLineCharts.updateOptions(object);
    }
    else if (this.horizontalStockedCharts) {
      this.horizontalStockedCharts.updateOptions(object);
    }
    else if (this.groupedCharts) {
      this.groupedCharts.updateOptions(object);
    }
    else if (this.multiLineCharts) {
      this.multiLineCharts.updateOptions(object);
    }
    else if(this.donutCharts){
      this.donutCharts.updateOptions(object);
    }
    else if (this.heatmapCharts) {
      this.heatmapCharts.updateOptions(object);
    }
    else if (this.funnelCharts) {
      this.funnelCharts.updateOptions(object);
    }
  }
  updateDrilldowns(){
    const self = this;
    if(this.barCharts || this.pieCharts || this.donutCharts){
      this.chartOptions.chart.events = {
        dataPointSelection: function (event: any, chartContext: any, config: any) {
          const selectedXValue = self.chartOptions.xaxis.categories[config.dataPointIndex];
          if (self.drillDownIndex < self.draggedDrillDownColumns.length - 1) {
            const selectedXValue = self.chartsColumnData[config.dataPointIndex];
            console.log('X-axis value:', selectedXValue);
            let nestedKey = self.draggedDrillDownColumns[self.drillDownIndex];
            self.drillDownIndex++;
            let obj = { [nestedKey]: selectedXValue };
            self.drillDownObject.push(obj);
            let dObject = {
              drillDownIndex : self.drillDownIndex,
              draggedDrillDownColumns :self.draggedDrillDownColumns,
              drillDownObject : self.drillDownObject
            }
            self.setDrilldowns.emit(dObject);
          }
        }
      }
    }
    if (this.barCharts) {
      this.barCharts.updateOptions(this.chartOptions.chart);
    }
    else if (this.pieCharts) {
      this.pieCharts.updateOptions(this.chartOptions.chart);
    }
    else if (this.donutCharts) {
      this.donutCharts.updateOptions(this.chartOptions.chart);
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
  //   if (this.chartType === 'funnel') {
  //     const numbers = this.chartOptions.series[0].data;
  //     const labels = this.chartOptions.xaxis.categories;
  //     const sortedData = this.sort(sortType, numbers, labels);

  //     this.chartOptions.series[0].data = sortedData.sortedNumbers;
  //     this.chartOptions.xaxis.categories = sortedData.sortedLabels;
  //     this.funnelCharts?.updateOptions({ series: this.chartOptions.series, xaxis: this.chartOptions.xaxis });
  //   } 
  //   else if (this.chartType === 'bar') {
  //     const numbers = this.chartOptions.series[0].data;
  //     const labels = this.chartOptions.xaxis.categories;
  //     const sortedData = this.sort(sortType, numbers, labels);

  //     this.chartOptions.series[0].data = sortedData.sortedNumbers;
  //     this.chartOptions.xaxis.categories = sortedData.sortedLabels;
  //     this.barCharts?.updateOptions({ series: this.chartOptions.series, xaxis: this.chartOptions.xaxis });
  //   }
  // }
}
// }

// }
