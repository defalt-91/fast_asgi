import { Component }                          from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute }                     from '@angular/router';
import { Store }                              from '@ngrx/store';
import { InputSlide }                         from "src/app/animations";
import { AppState }                           from "src/app/store";
import { LoginForm }                          from '../../_models/login-form';
import { userLogin }                          from '../../store/UserFeatureStore/actions/user-feature-store.actions';


@Component(
  {
    selector: 'app-login',
    templateUrl: './login.component.html',
    styleUrls: [ './login.component.scss' ],
    animations: [ InputSlide ]
  } )
export class LoginComponent {
  form: FormGroup;
  isOpen = false;
  formAnimate = 'nist';

  constructor(
    private route: ActivatedRoute,
    // private snackBar: MatSnackBar,
    private fb: FormBuilder,
    private store: Store<AppState>,
  ) {
    this.form = this.fb.group(
      {
        username: [ '', [ Validators.required, Validators.minLength( 4 ) ] ],
        password: [ '', [ Validators.required, Validators.minLength( 7 ) ] ],

      }
    )
  }

  get username() {
    return this.form.get( 'username' )!;
  }

  get password() {
    return this.form.controls.password;
  }

  login() {
    const formValue: LoginForm = this.form.value;
    if ( formValue.username && formValue.password && this.form.valid ) {
      this.store.dispatch( userLogin( { formValue } ) );
    }
  }

}
