import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
import { ViewconeService } from '../services/viewcone.service';

export const appConfig: ApplicationConfig = {
  providers: [
    ViewconeService,
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes)
  ]
};
