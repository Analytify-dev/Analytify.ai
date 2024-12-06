import { Component, Input, SimpleChanges } from '@angular/core';
import {
  ApexAxisChartSeries,
  ApexChart,
  ApexXAxis,
  ApexDataLabels,
  ApexTitleSubtitle,
  ApexYAxis,
  ApexLegend,
  NgApexchartsModule
} from 'ng-apexcharts';
@Component({
  selector: 'app-charts-store',
  standalone: true,
  imports: [NgApexchartsModule],
  templateUrl: './charts-store.component.html',
  styleUrl: './charts-store.component.scss'
})
export class ChartsStoreComponent {
  @Input() chartData!: { xAxis: string[], yAxis: number[] };

  colArray: string[] = [];
  rowArray: number[] = [];
  public chartOptions: any;

  ngOnChanges(changes: SimpleChanges) {
    if (changes['chartData'] && this.chartData) {
      this.colArray = this.chartData.xAxis;
      this.rowArray = this.chartData.yAxis;
      console.log('colArray:', this.colArray, 'rowArray:', this.rowArray);
    }
  }

  initializeChart() {
    this.chartOptions = {
      series: [{
        name: 'Series 1',
        data: this.chartData ? this.chartData.yAxis : []
      }],
      chart: {
        height: 350,
        type: 'line'
      },
      title: {
        text: 'Line Chart'
      },
      xaxis: {
        categories: this.chartData ? this.chartData.xAxis : []
      },
      yaxis: {
        title: {
          text: 'Values'
        }
      },
      legend: {
        show: true
      }
    };
  }
  updateChart() {
    if (this.chartOptions) {
      this.chartOptions.series = [{
        name: 'Series 1',
        data: this.chartData.yAxis
      }];
      this.chartOptions.xaxis = {
        categories: this.chartData.xAxis
      };
    }
  }

}
