import { LoginComponent }      from "./login.component";
import { LoginRoutingModule }  from "src/app/views/login/login-routing.module";
import { NgModule }            from "@angular/core";
import { ReactiveFormsModule } from "@angular/forms";
import { MatButtonModule }     from "@angular/material/button";
import { MatDividerModule }    from "@angular/material/divider";
import { MatInputModule }      from "@angular/material/input";
import { CommonModule }        from "@angular/common";


@NgModule(
	{
		declarations: [LoginComponent],
		imports: [
			CommonModule,
			MatInputModule,
			ReactiveFormsModule,
			MatDividerModule,
			LoginRoutingModule,
			MatButtonModule,
		],
	})
export class LoginModule{
}
