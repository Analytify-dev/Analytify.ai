import { Injectable,NgZone } from '@angular/core';
import { AngularFireModule } from '@angular/fire/compat';
import { AngularFireAuth } from '@angular/fire/compat/auth';
import { Router } from '@angular/router';
import { environment } from '../../../environments/environment';
import { AngularFirestoreDocument } from '@angular/fire/compat/firestore';
import { HttpClient } from '@angular/common/http';
import { of } from 'rxjs';
export interface User {
  uid: string;
  email: string;
  displayName: string;
  photoURL: string;
  emailVerified: boolean;
}
@Injectable({
  providedIn: 'root',
})
export class AuthService {
  authState: any;
  afAuth: any;
  afs: any;
  emailActivationToken:any;
  public showLoader:boolean=false;
  accessToken:any;
  constructor(private afu: AngularFireAuth, private router: Router,public ngZone: NgZone,private http: HttpClient) {
    this.afu.authState.subscribe((auth: any) => {
      this.authState = auth;
    });

  }

  // all firebase getdata functions

  get isUserAnonymousLoggedIn(): boolean {
    return this.authState !== null ? this.authState.isAnonymous : false;
  }

  get currentUserId(): string {
    return this.authState !== null ? this.authState.uid : '';
  }

  get currentUserName(): string {
    return this.authState['email'];
  }

  get currentUser(): any {
    return this.authState !== null ? this.authState : null;
  }

  get isUserEmailLoggedIn(): boolean {
    if (this.authState !== null && !this.isUserAnonymousLoggedIn) {
      return true;
    } else {
      return false;
    }
  }

//   registerWithEmail(email: string, password: string) {
//     return this.afu
//       .createUserWithEmailAndPassword(email, password)
//       .then((user: any) => {
//         this.authState = user;
//       })
//       .catch((_error: any) => {
//         console.log(_error);
//         throw _error;
//       });
//   }

//   loginWithEmail(email: string, password: string) {
//     return this.afu
//       .signInWithEmailAndPassword(email, password)
//       .then((user: any) => {
//         this.authState = user;
//       })
//       .catch((_error: any) => {
//         console.log(_error);
//         throw _error;
//       });
//   }

//   singout(): void {
//     this.afu.signOut();
//     this.router.navigate(['/login']);
//   }
  

//     // Sign up with email/password
//     SignUp(email:any, password:any) {
//       return this.afAuth.createUserWithEmailAndPassword(email, password)
//         .then((result:any) => {
//           /* Call the SendVerificaitonMail() function when new user sign
//           up and returns promise */
//           this.SendVerificationMail();
//           this.SetUserData(result.user);
//         }).catch((error:any) => {
//           window.alert(error.message)
//         })
//     }


//     // main verification function
//     SendVerificationMail() {
//       return this.afAuth.currentUser.then((u:any) => u.sendEmailVerification()).then(() => {
//           this.router.navigate(['/dashboard']);
//         })
//     }
//       // Set user
//   SetUserData(user:any) {
//     const userRef: AngularFirestoreDocument<any> = this.afs.doc(`users/${user.uid}`);
//     const userData: User = {
//       email: user.email,
//       displayName: user.displayName,
//       uid: user.uid,
//       photoURL: user.photoURL || 'src/favicon.ico',
//       emailVerified: user.emailVerified
//     };
//     userRef.delete().then(function () {})
//           .catch(function (error:any) {});
//     return userRef.set(userData, {
//       merge: true
//     });
//   }
//  // sign in function
//  SignIn(email:any, password:any) {
//   return this.afAuth.signInWithEmailAndPassword(email, password)
//     .then((result:any) => {
//       if (result.user.emailVerified !== true) {
//         this.SetUserData(result.user);
//         this.SendVerificationMail();
//         this.showLoader = true;
//       } else {
//         this.showLoader = false;
//         this.ngZone.run(() => {
//           this.router.navigate(['/auth/login']);
//         });
//       }
//     }).catch((error:any) => {
//       throw error;
//     })
// }
// ForgotPassword(passwordResetEmail:any) {
//   return this.afAuth.sendPasswordResetEmail(passwordResetEmail)
//     .then(() => {
//       window.alert('Password reset email sent, check your inbox.');
//     }).catch((error:any) => {
//       window.alert(error);
//     });
// }

login(email: string, password: string) {
  return this.http
    .post<any>(`${environment.apiUrl}/login/`, {
      email,
      password,
    })
  }
register(data:any){
  return this.http.post<any>(`${environment.apiUrl}/new_signup`, data )  

}
validateOtp(otp:any){
  return this.http.post<any>(`${environment.apiUrl}/activation/`+this.emailActivationToken,otp);
}
forgotPassword(data:any){
  return this.http.post<any>(`${environment.apiUrl}/reset_password/`,data);
}
resetPassword(token:any,data:any){
  return this.http.put<any>(`${environment.apiUrl}/reset_password/confirm`+'/'+token,data);
}
reactivateEmail(data:any){
  return this.http.post<any>(`${environment.apiUrl}/re_activation`+'/',data);

}
getTokenQuickbook(data:any){
  const currentUser = localStorage.getItem( 'currentUser' );
  this.accessToken = JSON.parse( currentUser! )['Token'];
  return this.http.post<any>(`${environment.apiUrl}/quickbooks_token/`+this.accessToken,data); 
}
getTokensalesforce(data:any){
  const currentUser = localStorage.getItem( 'currentUser' );
  this.accessToken = JSON.parse( currentUser! )['Token'];
  return this.http.post<any>(`${environment.apiUrl}/callback/`+this.accessToken,data); 
}
resendOtpApi(obj:any){
  return this.http.post<any>(`${environment.apiUrl}/resendotp/`,obj); 
}
logOut(){
  localStorage.removeItem('username');
         localStorage.removeItem('currentUser');
        //  this.currentUserSubject.next(this.currentUserValue);
         localStorage.clear();
         //this.userSubject.next(null);
         window.location.reload();
  
         this.router.navigate(['/authentication/signin']) 
        //  .then(() => {
        //  }); 
         return of({ success: false });
  }
}
