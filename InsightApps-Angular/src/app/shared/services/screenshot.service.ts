import { Injectable } from '@angular/core';
import html2canvas from 'html2canvas';

@Injectable({
  providedIn: 'root',
})
export class ScreenshotService {
  capture(element: HTMLElement): Promise<string> {
    return html2canvas(element, {
      useCORS: true, // Enable CORS for images
      scrollX: 0,
      scrollY: 0, // Ensure the correct scroll position
      backgroundColor: null, // Transparent background
      width: element.scrollWidth, // Ensure the full width is captured
      height: element.scrollHeight, // Ensure the full height is captured
      scale: 2, // Increase scale for better quality
    }).then((canvas) => {
      return canvas.toDataURL('image/png');
    }).catch((error) => {
      console.error('Error in html2canvas:', error);
      throw error;
    });
  }
  
}