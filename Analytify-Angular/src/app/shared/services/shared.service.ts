import { Injectable } from '@angular/core';
import { BehaviorSubject, Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SharedService {
  [x: string]: any;
    private downloadRequestSource = new Subject<void>();
    private refreshRequestSource = new Subject<void>();

    downloadRequested$ = this.downloadRequestSource.asObservable();
    refreshRequested$ = this.refreshRequestSource.asObservable();

    private localStorageValue = new BehaviorSubject<string | null>(localStorage.getItem('myValue'));
    public localStorageValue$ = this.localStorageValue.asObservable();

    setValue(newValue: string): void {
      localStorage.setItem('myValue', newValue);
      this.localStorageValue.next(newValue); // Notify subscribers
    }
  
    // Method to get the current value
    getValue(): string | null {
      return this.localStorageValue.getValue();
    }


  download() {
       this.downloadRequestSource.next(); 
  }

  refresh() {
    this.refreshRequestSource.next(); // Notify subscribers that a refresh has been requested

  }
}