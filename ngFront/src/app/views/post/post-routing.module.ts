import {NgModule} from "@angular/core";
import {RouterModule, Routes} from "@angular/router";

const routes: Routes = [

  {
    path: "detail",
    loadChildren: () =>
      import("./post-detail/post-detail.module").then(
        (m) => m.PostDetailModule
      ),
    data: {animation: "detail"},
  },
  {
    path: "create",
    loadChildren: () =>
      import("./post-create/post-create.module").then(
        (m) => m.PostCreateModule
      ),
  },
  {
    path: "delete",
    loadChildren: () =>
      import("./post-delete/post-delete.module").then(
        (m) => m.PostDeleteModule
      ),
  }, {
    path: "",
    pathMatch: "full",
    loadChildren: () =>
      import("./post-list/post-list.module").then(
        (m) => m.PostListModule
      ),
  },
];

@NgModule({
  imports: [
    RouterModule.forChild(routes),
  ],
  exports: [RouterModule],
})
export class PostRoutingModule {
}
