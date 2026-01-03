import { Injectable } from '@angular/core';

// TODO: Implementar quando módulos estiverem disponíveis
// import { MODULE_ROUTE_CONFIGS } from '../routes/module-route.config';

@Injectable({ providedIn: 'root' })
export class RouteMappingService {
  
  getRouteConfigs() {
    // TODO: Retornar MODULE_ROUTE_CONFIGS quando disponível
    return [];
  }
  
  getRouteByPath(path: string) {
    // TODO: Implementar quando MODULE_ROUTE_CONFIGS estiver disponível
    return null;
  }
}
