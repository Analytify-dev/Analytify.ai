import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'formatMeasure',
  standalone: true
})
export class FormatMeasurePipe implements PipeTransform {
  transform(
    value: any,
    decimalPlaces: number,
    prefix: string ,
    suffix: string ,
    displayUnit: string
  ) {
    if (typeof value !== 'number' || isNaN(value)) {
      return value; 
    } else if(typeof value == 'number') {
    let formattedNumber : string = String(value);
    if (displayUnit !== 'none') {
      switch (displayUnit) {
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
      }
    } else {
      formattedNumber = (value).toFixed(decimalPlaces)
    }

    return  prefix + formattedNumber + suffix;
  }
  }
}

