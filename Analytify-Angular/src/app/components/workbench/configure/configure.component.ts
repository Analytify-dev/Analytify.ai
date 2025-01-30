import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { WorkbenchService } from '../workbench.service';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { SharedModule } from '../../../shared/sharedmodule';
// import { data } from '../../charts/echarts/echarts';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-configure',
  standalone: true,
  imports: [FormsModule, CommonModule, SharedModule],
  templateUrl: './configure.component.html',
  styleUrl: './configure.component.scss',
})
export class ConfigureComponent {
  apiKey: string = '';
  errorMessage: string = '';
  showPassword: boolean = false;

  constructor(
    private workbechService: WorkbenchService,
    private http: HttpClient,
    private router: Router
  ) {}

  submitApiKey() {
    const obj = {
      key: this.apiKey,
    };
    this.workbechService.openApiKey(obj).subscribe({
      next: (data: any) => {
        if (data) {
          localStorage.setItem('API_KEY', obj.key);
          Swal.fire({
            icon: 'success',
            title: 'API Key Verification Success',
            text: 'Verified',
            width: '400px',
          }).then(() => {
            // Redirect to the previous page after success
            const previousUrl = localStorage.getItem('previousUrl');
            if (previousUrl) {
              this.router.navigateByUrl(previousUrl);
              localStorage.removeItem('previousUrl'); // Clear the stored URL
            } else {
              this.router.navigate(['analytify/home']); // Redirect to a default route if no previous URL
            }
          });
        }
      },
      error: (error: any) => {
        Swal.fire({
          icon: 'warning',
          text: error.error.message,
          width: '300px',
        });
        console.log(error);
      },
    });
  }
  preventSpaces(event: KeyboardEvent) {
    if (event.code === 'Space' || event.key === ' ') {
      event.preventDefault();
    }
  }

  togglePasswordVisibility() {
    this.showPassword = !this.showPassword;
  }
}
