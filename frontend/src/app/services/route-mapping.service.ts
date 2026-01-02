import { Injectable } from '@angular/core';

import { MODULE_ROUTE_CONFIGS } from '../routes/module-route.config';

@Injectable({ providedIn: 'root' })
export class RouteMappingService {
  
  getRouteConfigs() {
    return MODULE_ROUTE_CONFIGS;
  }
  
  getRouteByPath(path: string) {
    return MODULE_ROUTE_CONFIGS.find(config => config.path === path);
  }
}
