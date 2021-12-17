import {
	HttpEvent,
	HttpHandler,
	HttpInterceptor,
	HttpRequest,
} from "@angular/common/http";
import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { finalize }  from "rxjs/operators";
import { UIService } from "src/app/_services/ui.service";

@Injectable()
export class ProgressBarInterceptor implements HttpInterceptor {
	constructor(public progressService: UIService) {}

	intercept(
		request: HttpRequest<any>,
		next: HttpHandler
	): Observable<HttpEvent<any>> {
		this.progressService.isLoading.next(true);
		console.log("true");
		return next.handle(request).pipe(
			finalize(() => {
				this.progressService.isLoading.next(false);
				console.log("false");
			})
		);
	}
}
