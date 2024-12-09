import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SharedService {
    private downloadRequestSource = new Subject<void>();
    private refreshRequestSource = new Subject<void>();

    downloadRequested$ = this.downloadRequestSource.asObservable();
    refreshRequested$ = this.refreshRequestSource.asObservable();



  download() {
       this.downloadRequestSource.next(); 
  }

  refresh() {
    this.refreshRequestSource.next(); // Notify subscribers that a refresh has been requested

  }
}