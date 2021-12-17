import { Component, OnInit } from '@angular/core';
import { Store }             from "@ngrx/store";
import { AppState }          from "src/app/store";


@Component(
	{
		selector   : 'app-sidebar',
		templateUrl: './sidebar.component.html',
		styleUrls  : ['./sidebar.component.scss']
	})
export class SidebarComponent implements OnInit{
	show: boolean = false;
	isDark        = this.store.select(state => state.ui.Dark_Mode);
	
	constructor(private store: Store<AppState>) { }
	
	ngOnInit(): void {}
}
