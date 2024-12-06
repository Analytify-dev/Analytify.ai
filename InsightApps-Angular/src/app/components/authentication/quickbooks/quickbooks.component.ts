import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../../shared/services/auth.service';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-quickbooks',
  standalone: true,
  imports: [],
  templateUrl: './quickbooks.component.html',
  styleUrl: './quickbooks.component.scss'
})
export class QuickbooksComponent implements OnInit {
constructor(private router:Router,private authService:AuthService){
  const currentUrl = this.router.url;
  if ((currentUrl.includes('/authentication/quickbooks'))) {
    let url = this.router.url;
    console.log(url);
    this.getToken(url);
  }
  if ((currentUrl.includes('/authentication/salesforce'))) {
    let url = this.router.url;
    console.log(url);
    this.getSalesforceToken(url);
  }
}

ngOnInit(){

}
getToken(url:any){
  const obj = {
    redirect_url: url
  }
  this.authService.getTokenQuickbook(obj)
    .subscribe(
      {
        next: (data: any) => {
          console.log(data);
          if (data.message === 'Success') {
            //const connectedToQuickbooks = data.quickbooksConnected;
            //localStorage.setItem('connectedToQuickbooks', JSON.stringify(connectedToQuickbooks));
            // this.connectionSuccess = true;
            // this.getCompanyDetails();
            // const quickBooksId = data.quickbooks_id;
            const quickBooksId = btoa(data.quickbooks_id.toString());
            this.router.navigate(['/insights/database-connection/tables/quickbooks/'+quickBooksId]);
          }
        },
        error: (error: any) => {
          console.log(error);
          if(error){
            Swal.fire({
              icon: 'error',
              title: 'oops!',
              text: error.error.message,
              width: '400px',
            })
            this.router.navigate(['./insights/datasources/view-connections'])
          }
        }
      }
    )
}
getSalesforceToken(url:any){
  const obj = {
    redirect_url: url
  }
  this.authService.getTokensalesforce(obj)
    .subscribe(
      {
        next: (data: any) => {
          console.log(data);
          if (data) {
            //const connectedToQuickbooks = data.quickbooksConnected;
            //localStorage.setItem('connectedToQuickbooks', JSON.stringify(connectedToQuickbooks));
            // this.connectionSuccess = true;
            // this.getCompanyDetails();
            // const quickBooksId = data.quickbooks_id;
            const salesforceId = btoa(data.salesforce_id.toString());
            this.router.navigate(['/insights/database-connection/tables/quickbooks/'+salesforceId]);
          }
        },
        error: (error: any) => {
          console.log(error);
          if(error){
            Swal.fire({
              icon: 'error',
              title: 'oops!',
              text: error.error.message,
              width: '400px',
            })
            this.router.navigate(['./insights/datasources/view-connections'])
          }
        }
      }
    )
}
}
