# RelatorioPdfContratacaoService

Serviço Angular responsável pela geração de relatórios em PDF para contratos/contratações do sistema PNCP.

## Descrição

Este serviço gera relatórios PDF detalhados de contratações, incluindo informações do cabeçalho, dados da contratação, itens e resultados (fornecedores homologados). Os relatórios são formatados de forma profissional e otimizada para ocupar o espaço disponível.

## Funcionalidades

- ✅ Geração de PDF com layout profissional
- ✅ Cabeçalho dinâmico com informações da contratação
- ✅ Seção de itens otimizada com ícones de status
- ✅ Resultados detalhados por fornecedor
- ✅ Suporte a múltiplas páginas com rodapé
- ✅ Ícones visuais baseados na situação dos itens
- ✅ Links clicáveis para o PNCP

## Uso

### Importação

```typescript
import { RelatorioPdfContratacaoService } from './services/relatorio-pdf-contratacao.service';
```

### Injeção de Dependência

```typescript
constructor(
  private relatorioPdfService: RelatorioPdfContratacaoService
) {}
```

### Método Principal

#### `gerarRelatorioPDF()`

Gera e salva um relatório PDF da compra detalhada.

**Assinatura:**
```typescript
async gerarRelatorioPDF(
  compra: CompraDetalhada,
  compraListagem: CompraListagem,
  uasgTexto: string,
  ano: number | null
): Promise<void>
```

**Parâmetros:**
- `compra` (CompraDetalhada): Objeto com os detalhes completos da compra
- `compraListagem` (CompraListagem): Objeto com informações da listagem da compra
- `uasgTexto` (string): Texto formatado da UASG (ex: "12345 - SIGLA")
- `ano` (number | null): Ano da compra

**Exemplo de uso:**
```typescript
await this.relatorioPdfService.gerarRelatorioPDF(
  compraDetalhada,
  compraListagem,
  '12345 - UASG_EXEMPLO',
  2024
);
```

## Estrutura do Relatório

### Cabeçalho
- Título: `{Modalidade} nº {Número da Compra}/{Ano}`
- UASG (mesma linha do título, à direita)
- Informações da contratação:
  - Sequencial do PNCP
  - Número do Processo
  - Link PNCP (clicável)
  - Objeto
  - Amparo Legal
  - Modo de Disputa
  - Data Publicação PNCP
  - Valor Total Estimado
  - Valor Total Homologado
  - Percentual de Desconto

### Seção de Itens
Cada item contém:
- **Ícone de Status** (à esquerda):
  - ✅ `checked.svg` - Item Homologado
  - ⏱️ `time.svg` - Em Andamento
  - ⚠️ `warning.svg` - Outras situações
- **Cabeçalho**: Item X - Descrição
- **Informações em linha única**:
  - Quantidade
  - Unidade de Medida
  - Valor Total Estimado
  - Percentual de Desconto (se houver resultados)
  - Valor Total Homologado (se houver resultados)
  - Situação

### Resultados (Fornecedores)
Para cada resultado do item:
- **Primeira linha**: Fornecedor: {CNPJ} - {Razão Social}
- **Segunda linha**: Quantidade Homologada
- **Terceira linha**: Valor Unitário Estimado | Valor Unitário Homologado | Percentual de Desconto
- **Quarta linha**: Valor Total Homologado

## Métodos Privados

### `getIconPath(situacao: string): string`
Determina qual ícone SVG usar baseado na situação do item.

**Lógica:**
- Contém "homologado" → `/assets/img/svg/checked.svg`
- Contém "em andamento" → `/assets/img/svg/time.svg`
- Outros casos → `/assets/img/svg/warning.svg`

### `loadIconAsBase64(iconPath: string): Promise<string | null>`
Carrega um arquivo SVG e converte para base64 (PNG).

### `addIconToPDF(doc: jsPDF, iconBase64: string | null, x: number, y: number, size: number): void`
Adiciona um ícone ao PDF na posição especificada.

### `formatarValor(valor: string | null | undefined): string`
Formata valores monetários para o padrão brasileiro (R$).

### `formatarPercentual(valor: string | null | undefined): string`
Formata percentuais com 2 casas decimais.

### `formatarData(data: string | null | undefined): string`
Formata datas para o padrão brasileiro (DD/MM/YYYY).

## Características Técnicas

- **Biblioteca**: jsPDF
- **Formato de saída**: PDF
- **Suporte a múltiplas páginas**: Sim, com numeração automática
- **Rodapé**: Inclui data/hora de geração e número da página
- **Links**: Suporte a links clicáveis (Link PNCP)
- **Cores**: 
  - Texto principal: Preto (33, 33, 33)
  - Texto secundário: Cinza (100, 100, 100)
  - Links: Azul (0, 0, 255)
  - Fundo do cabeçalho: Cinza claro (245, 245, 245)

## Dependências

- `jsPDF`: Biblioteca para geração de PDFs
- Interfaces: `CompraDetalhada`, `CompraListagem` de `../interfaces/pncp.interface`

## Arquivos de Ícones Necessários

O serviço utiliza os seguintes arquivos SVG (devem estar em `/public/assets/img/svg/`):
- `checked.svg` - Ícone para itens homologados
- `time.svg` - Ícone para itens em andamento
- `warning.svg` - Ícone para outras situações

## Notas

- O serviço é assíncrono e aguarda o carregamento de todos os ícones antes de gerar o PDF
- Os ícones são pré-carregados e armazenados em cache para otimização
- O PDF é gerado e baixado automaticamente após a conclusão
- O nome do arquivo segue o padrão: `Relatorio_Contratacao_{numero_compra}_{ano}.pdf`

## Exemplo Completo

```typescript
import { Component } from '@angular/core';
import { RelatorioPdfContratacaoService } from './services/relatorio-pdf-contratacao.service';
import { CompraDetalhada, CompraListagem } from './interfaces/pncp.interface';

@Component({
  selector: 'app-exemplo',
  template: '<button (click)="gerarPDF()">Gerar PDF</button>'
})
export class ExemploComponent {
  constructor(
    private relatorioPdfService: RelatorioPdfContratacaoService
  ) {}

  async gerarPDF() {
    const compra: CompraDetalhada = { /* ... */ };
    const compraListagem: CompraListagem = { /* ... */ };
    
    await this.relatorioPdfService.gerarRelatorioPDF(
      compra,
      compraListagem,
      '12345 - UASG_EXEMPLO',
      2024
    );
  }
}
```

## Troubleshooting

### Ícones não aparecem
- Verifique se os arquivos SVG existem em `/public/assets/img/svg/`
- Verifique o console do navegador para erros de carregamento
- Certifique-se de que o método está sendo aguardado (`await`)

### PDF não é gerado
- Verifique se todos os parâmetros obrigatórios foram fornecidos
- Verifique se há erros no console do navegador
- Certifique-se de que o método está sendo chamado de forma assíncrona

### Formatação incorreta
- Verifique se os dados de entrada estão no formato correto
- Verifique se as interfaces `CompraDetalhada` e `CompraListagem` estão atualizadas
