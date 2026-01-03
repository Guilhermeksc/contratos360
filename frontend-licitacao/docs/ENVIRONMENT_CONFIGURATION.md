# Configuração de Environment para o PerguntasService

## Estrutura de Arquivos

```
src/
├── app/
│   ├── environments/
│   │   ├── environment.ts (desenvolvimento)
│   │   └── environment.prod.ts (produção)
│   └── services/
│       └── perguntas.service.ts
```

## Configuração dos Environments

### Development (environment.ts)
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8088/api'
};
```

### Production (environment.prod.ts)
```typescript
export const environment = {
  production: true,
  apiUrl: 'https://cemos2028.com.br/api'
};
```

## Como o Service usa o Environment

```typescript
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class PerguntasService {
  // A URL é construída dinamicamente baseada no environment
  private readonly apiUrl = `${environment.apiUrl}/perguntas/api`;
  
  // Resto do código...
}
```

## URLs Resultantes

### Development
- API Base: `http://localhost:8088/api/perguntas/api`
- Bibliografias: `http://localhost:8088/api/perguntas/api/bibliografias/`
- Perguntas Múltipla: `http://localhost:8088/api/perguntas/api/perguntas-multipla/`
- Perguntas V/F: `http://localhost:8088/api/perguntas/api/perguntas-vf/`
- Perguntas Correlação: `http://localhost:8088/api/perguntas/api/perguntas-correlacao/`

### Production
- API Base: `https://cemos2028.com.br/api/perguntas/api`
- Bibliografias: `https://cemos2028.com.br/api/perguntas/api/bibliografias/`
- Perguntas Múltipla: `https://cemos2028.com.br/api/perguntas/api/perguntas-multipla/`
- Perguntas V/F: `https://cemos2028.com.br/api/perguntas/api/perguntas-vf/`
- Perguntas Correlação: `https://cemos2028.com.br/api/perguntas/api/perguntas-correlacao/`

## Configuração do Angular.json

O `angular.json` está configurado para automaticamente substituir o arquivo de environment em produção:

```json
{
  "configurations": {
    "production": {
      "fileReplacements": [
        {
          "replace": "src/app/environments/environment.ts",
          "with": "src/app/environments/environment.prod.ts"
        }
      ]
    }
  }
}
```

## Como Compilar

### Development
```bash
ng serve
# ou
ng build --configuration=development
```

### Production
```bash
ng build --configuration=production
# ou
ng build --prod
```

## Vantagens desta Abordagem

1. **Flexibilidade**: Fácil mudança de URLs entre ambientes
2. **Manutenibilidade**: URL centralizada em um só lugar
3. **Segurança**: URLs de produção não ficam expostas em desenvolvimento
4. **Automação**: Build automático seleciona o environment correto
5. **Escalabilidade**: Fácil adição de novos environments (staging, testing, etc.)

## Exemplo de Uso em Componente

```typescript
import { Component, OnInit } from '@angular/core';
import { PerguntasService } from '../services/perguntas.service';
import { environment } from '../environments/environment';

@Component({
  selector: 'app-perguntas',
  templateUrl: './perguntas.component.html'
})
export class PerguntasComponent implements OnInit {
  isProduction = environment.production;
  
  constructor(private perguntasService: PerguntasService) {}
  
  ngOnInit() {
    console.log('Ambiente:', environment.production ? 'Produção' : 'Desenvolvimento');
    console.log('API URL:', environment.apiUrl);
    
    // O service automaticamente usa a URL correta
    this.perguntasService.getBibliografias().subscribe(response => {
      console.log('Dados carregados do ambiente:', this.isProduction ? 'produção' : 'desenvolvimento');
    });
  }
}
```

## Adicionando Novos Environments

Para adicionar um ambiente de staging, por exemplo:

1. Criar `environment.staging.ts`:
```typescript
export const environment = {
  production: false,
  apiUrl: 'https://staging.cemos2028.com.br/api'
};
```

2. Adicionar configuração no `angular.json`:
```json
"staging": {
  "fileReplacements": [
    {
      "replace": "src/app/environments/environment.ts",
      "with": "src/app/environments/environment.staging.ts"
    }
  ]
}
```

3. Build para staging:
```bash
ng build --configuration=staging
```