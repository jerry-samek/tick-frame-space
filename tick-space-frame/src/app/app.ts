import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { ViewportComponent } from '../pages/viewport/viewport.component';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, ViewportComponent, ViewportComponent],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('tick-space-frame');
}
