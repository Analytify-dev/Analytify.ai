import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthService } from '../../../shared/services/auth.service';
import { Router } from '@angular/router';
import Swal from 'sweetalert2';
import { SharedModule } from '../../../shared/sharedmodule';

@Component({
  selector: 'app-email-reactivation',
  standalone: true,
  imports: [FormsModule,CommonModule,ReactiveFormsModule,SharedModule],
  templateUrl: './email-reactivation.component.html',
  styleUrl: './email-reactivation.component.scss'
})
export class EmailReactivationComponent {
  reactivationForm:FormGroup;
  emailActivationToken: any;
constructor(private formBuilder:FormBuilder,private authService:AuthService,private router:Router){
  this.reactivationForm = this.formBuilder.group({
    email: ['', [Validators.required, Validators.pattern('^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,4}$')]],
       })
}

ngOnInit(){

}
get f() {
  return this.reactivationForm.controls;
}
onSubmit(){
  this.authService.reactivateEmail(this.reactivationForm.value)
.subscribe({
  next:(data:any) => {
    console.log(data); 
    this.emailActivationToken = data.emailActivationToken;
    this.authService.emailActivationToken = data.emailActivationToken;
    this.router.navigate(['/authentication/email-activation/'+ this.emailActivationToken]);  

  },
  error:(error:any)=>{
    console.log(error);
    if(error){
      Swal.fire({
        icon: 'error',
        title: 'oops!',
        text: error.error.message,
        width: '400px',
      })
    }
    
  }
})
}
}
