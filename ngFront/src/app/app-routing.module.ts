import { NgModule }             from "@angular/core";
import { RouterModule, Routes } from "@angular/router";


const routes: Routes = [
	{
		path: "login",
		data: { animation: '' },
		// canLoad:[LogedinGuard],
		loadChildren: () =>
			import("./views/login/login.module").then((m) => m.LoginModule),
	},
	{
		path: "post",
		// canActivate: [AuthGuard],
		loadChildren: () =>
			import("./views/post/post-routing.module").then((m) => m.PostRoutingModule),
	},
	{ path: "", redirectTo: "post", pathMatch: "full" },
	
	{
		path        : "**",
		loadChildren: () =>
			import("./views/not-found/not-found.module").then(
				(m) => m.NotFoundModule
			),
	},
];

@NgModule({
	imports: [RouterModule.forRoot(routes)],
	exports: [RouterModule],
})
export class AppRoutingModule{
}
