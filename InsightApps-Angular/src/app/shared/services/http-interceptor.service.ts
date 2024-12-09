import { HttpErrorResponse, HttpEvent, HttpHandler, HttpInterceptor, HttpInterceptorFn, HttpRequest, HttpResponse } from '@angular/common/http';
import { Injectable, NgZone } from '@angular/core';
import { LoaderService } from './loader.service';
import { Observable } from 'rxjs';
import { tap, finalize } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
  })
  export class HttpInterceptorService implements HttpInterceptor {

  constructor(private loaderService: LoaderService,private zone: NgZone) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // console.log('Interceptor: show loader');
    this.zone.run(() => this.loaderService.show());

    return next.handle(req).pipe(
      finalize(() => {
        // console.log('Interceptor: hide loader');
        this.zone.run(() => this.loaderService.hide());
      })
    );
  }
  
}

// export const HttpInterceptorService: HttpInterceptorFn = (req,next) => {}