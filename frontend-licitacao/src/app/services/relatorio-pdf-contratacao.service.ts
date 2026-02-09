import { Injectable } from '@angular/core';
import jsPDF from 'jspdf';
import { CompraDetalhada, CompraListagem } from '../interfaces/pncp.interface';

@Injectable({
  providedIn: 'root'
})
export class RelatorioPdfContratacaoService {
  
  /**
   * Determina qual ícone usar baseado na situação do item
   */
  private getIconPath(situacao: string): string {
    const situacaoLower = situacao.toLowerCase();
    if (situacaoLower.includes('homologado')) {
      return '/assets/img/svg/checked.svg';
    } else if (situacaoLower.includes('em andamento')) {
      return '/assets/img/svg/time.svg';
    } else {
      return '/assets/img/svg/warning.svg';
    }
  }

  /**
   * Converte SVG para base64
   */
  private async loadIconAsBase64(iconPath: string): Promise<string | null> {
    try {
      const response = await fetch(iconPath);
      const svgText = await response.text();
      
      // Cria um canvas para converter SVG para imagem
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      if (!ctx) return null;
      
      canvas.width = 50;
      canvas.height = 50;
      
      // Cria uma imagem do SVG
      return new Promise((resolve) => {
        const img = new Image();
        const svgBlob = new Blob([svgText], { type: 'image/svg+xml;charset=utf-8' });
        const url = URL.createObjectURL(svgBlob);
        
        img.onload = () => {
          try {
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            const imgData = canvas.toDataURL('image/png');
            URL.revokeObjectURL(url);
            resolve(imgData);
          } catch (e) {
            URL.revokeObjectURL(url);
            resolve(null);
          }
        };
        
        img.onerror = () => {
          URL.revokeObjectURL(url);
          resolve(null);
        };
        
        img.src = url;
      });
    } catch (error) {
      return null;
    }
  }

  /**
   * Adiciona ícone ao PDF (síncrono, usando base64 pré-carregado)
   */
  private addIconToPDF(
    doc: jsPDF,
    iconBase64: string | null,
    x: number,
    y: number,
    size: number = 5
  ): void {
    if (iconBase64) {
      try {
        doc.addImage(iconBase64, 'PNG', x, y - size, size, size);
      } catch (e) {
        // Ignora erros
      }
    }
  }
  
  /**
   * Gera relatório em PDF da compra detalhada
   */
  async gerarRelatorioPDF(
    compra: CompraDetalhada,
    compraListagem: CompraListagem,
    uasgTexto: string,
    ano: number | null
  ): Promise<void> {
    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    const margin = 20;
    const maxWidth = pageWidth - (margin * 2);
    let yPosition = margin;

    // Função para adicionar rodapé em cada página
    const addFooter = (pageNum: number, totalPages: number) => {
      const footerY = pageHeight - 8;
      const dataHora = new Date().toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
      
      doc.setFontSize(9);
      doc.setTextColor(100, 100, 100);
      const footerText = `Relatório gerado pelo Sistema Licitação360 em ${dataHora}`;
      const footerWidth = doc.getTextWidth(footerText);
      doc.text(footerText, (pageWidth - footerWidth) / 2, footerY);
      
      // Número da página
      doc.text(`Página ${pageNum} de ${totalPages}`, pageWidth - margin - 20, footerY);
    };

    let currentPage = 1;
    let totalPages = 1;

    // Função para verificar se precisa de nova página
    const checkNewPage = (requiredSpace: number): boolean => {
      if (yPosition + requiredSpace > pageHeight - 14) {
        doc.addPage();
        currentPage++;
        totalPages++;
        yPosition = margin;
        // Reseta a cor do texto para preta após nova página
        doc.setTextColor(33, 33, 33);
        return true;
      }
      return false;
    };

    // Título do relatório: {modalidade} nº {numero da compra}/{ano}
    const modalidadeNome = compraListagem.modalidade?.nome || 'Contratação';
    const numeroCompra = compraListagem.numero_compra;
    const anoCompra = compraListagem.ano_compra;
    const tituloRelatorio = `${modalidadeNome} nº ${numeroCompra}/${anoCompra}`;
    
    // Informações da contratação
    doc.setFontSize(9);
    const informacoes = [
      ['Sequencial do PNCP:', compra.sequencial_compra.toString()],
      ['Número do Processo:', compraListagem.numero_processo || 'N/A'],
      ['Link PNCP:', `https://pncp.gov.br/app/editais/00394502000144/${compraListagem.ano_compra}/${compra.sequencial_compra}`],
      ['Objeto:', compra.objeto_compra],
      ['Amparo Legal:', compra.amparo_legal?.nome || 'N/A'],
      ['Modo de Disputa:', compra.modo_disputa?.nome || 'N/A'],
      ['Data Publicação PNCP:', this.formatarData(compra.data_publicacao_pncp)],
      ['Valor Total Estimado:', this.formatarValor(compra.valor_total_estimado)],
      ['Valor Total Homologado:', this.formatarValor(compra.valor_total_homologado)],
      ['Percentual de Desconto:', this.formatarPercentual(compra.percentual_desconto)]
    ];

    // Resumo dos itens
    const resumoItens = this.calcularResumoItens(compra);

    // Calcula altura necessária antes de desenhar o cabeçalho
    let alturaNecessaria = 35; // Altura do título
    informacoes.forEach(([label, value]) => {
      if (label === 'Link PNCP:') {
        const linkText = String(value);
        const lines = doc.splitTextToSize(linkText, maxWidth - 60);
        alturaNecessaria += lines.length * 4 + 2;
      } else {
        const lines = doc.splitTextToSize(String(value), maxWidth - 60);
        alturaNecessaria += lines.length * 4 + 2;
      }
    });

    // Espaço para o resumo dos itens
    const resumoLines = 5;
    alturaNecessaria += resumoLines * 4 + 6;
    
    // Adiciona margem extra mínima (apenas 5px para evitar que o último campo fique colado na borda)
    const headerHeight = alturaNecessaria + 5;
    
    // Desenha o cabeçalho com altura calculada
    doc.setFillColor(245, 245, 245);
    doc.rect(0, 0, pageWidth, headerHeight, 'F');
    
    doc.setFontSize(18);
    doc.setTextColor(33, 33, 33);
    doc.setFont('helvetica', 'bold');
    doc.text(tituloRelatorio, margin, 25);
    
    // UASG na mesma linha do título (à direita)
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(100, 100, 100);
    const uasgText = `UASG: ${uasgTexto}`;
    const uasgWidth = doc.getTextWidth(uasgText);
    doc.text(uasgText, pageWidth - margin - uasgWidth, 25);
    
    // Informações começam abaixo do título
    let currentY = 35;
    doc.setFontSize(9);
    doc.setTextColor(33, 33, 33);

    informacoes.forEach(([label, value], index) => {
      checkNewPage(8);
      doc.setFont('helvetica', 'bold');
      doc.text(label, margin, currentY);
      doc.setFont('helvetica', 'normal');
      
      // Se for o link, adiciona como link clicável
      if (label === 'Link PNCP:') {
        const linkText = String(value);
        const lines = doc.splitTextToSize(linkText, maxWidth - 60);
        
        // Adiciona o texto do link em azul
        doc.setTextColor(0, 0, 255); // Azul para links
        
        lines.forEach((line: string, lineIndex: number) => {
          const lineYPos = currentY - (lines.length - lineIndex - 1) * 4;
          doc.text(line, margin + 50, lineYPos);
          
          // Adiciona o link clicável
          const lineWidth = doc.getTextWidth(line);
          const lineHeight = 4;
          // jsPDF link: x, y (from top), width, height
          // Ajusta Y para o centro da linha de texto
          doc.link(margin + 50, lineYPos - 3, lineWidth, lineHeight, { url: linkText });
        });
        
        doc.setTextColor(33, 33, 33); // Volta para cor normal
        currentY += lines.length * 4 + 2;
      } else {
        const lines = doc.splitTextToSize(String(value), maxWidth - 60);
        doc.text(lines, margin + 50, currentY);
        currentY += lines.length * 4 + 2;
      }
    });

    // Resumo dos itens (abaixo do percentual de desconto)
    currentY += 4;
    checkNewPage(20);
    doc.setFont('helvetica', 'bold');
    doc.text('Resumo dos Itens:', margin, currentY);
    doc.setFont('helvetica', 'normal');

    currentY += 4;
    doc.text(`Total: ${resumoItens.total}`, margin, currentY);
    currentY += 4;
    doc.text(`Homologados: ${resumoItens.homologados}`, margin, currentY);
    currentY += 4;
    doc.text(`Fracassados: ${resumoItens.fracassados}`, margin, currentY);
    currentY += 4;
    doc.text(`Em andamento: ${resumoItens.emAndamento}`, margin, currentY);
    currentY += 4;
    doc.text(`Percentual de Conclusão: ${resumoItens.percentualConclusao}`, margin, currentY);
    
    // Ajusta o yPosition para começar após o cabeçalho completo
    yPosition = currentY + 15;

    // Pré-carrega todos os ícones necessários
    const iconCache = new Map<string, string | null>();
    if (compra.itens && compra.itens.length > 0) {
      const uniqueSituacoes = [...new Set(compra.itens.map(item => item.situacao_compra_item_nome))];
      await Promise.all(
        uniqueSituacoes.map(async (situacao) => {
          const iconPath = this.getIconPath(situacao);
          if (!iconCache.has(iconPath)) {
            const base64 = await this.loadIconAsBase64(iconPath);
            iconCache.set(iconPath, base64);
          }
        })
      );
    }

    // Itens da Compra
    if (compra.itens && compra.itens.length > 0) {
      checkNewPage(15);
      yPosition += 5; // Espaço extra antes da seção de itens
      doc.setTextColor(33, 33, 33); // Garante cor preta
      doc.setFontSize(14);
      doc.setFont('helvetica', 'bold');
      doc.text('Itens da Contratação', margin, yPosition);
      yPosition += 10;
      
      compra.itens.forEach((item, index) => {
        checkNewPage(25);
        
        // Garante cor preta para cada item
        doc.setTextColor(33, 33, 33);
        
        // Adiciona ícone baseado na situação (discreto à esquerda)
        const iconPath = this.getIconPath(item.situacao_compra_item_nome);
        const iconBase64 = iconCache.get(iconPath) || null;
        const iconSize = 4;
        const iconX = margin - 5; // Posição ao lado do item
        const iconY = yPosition + 1; // Alinha verticalmente com o texto
        this.addIconToPDF(doc, iconBase64, iconX, iconY, iconSize);
        
        // Item X - Descrição na mesma linha
        doc.setFontSize(11);
        doc.setFont('helvetica', 'bold');
        const itemTitle = `Item ${item.numero_item} - `;
        const itemTitleWidth = doc.getTextWidth(itemTitle);
        doc.text(itemTitle, margin, yPosition);
        
        doc.setFont('helvetica', 'normal');
        const descStartX = margin + itemTitleWidth;
        const descMaxWidth = pageWidth - margin - descStartX;
        const descLines = doc.splitTextToSize(item.descricao, descMaxWidth);
        doc.text(descLines, descStartX, yPosition);
        yPosition += descLines.length * 3.5 + 1;

        // Linha 1: Situação, Quantidade e Unidade de fornecimento (mesma linha)
        doc.setFontSize(8);
        checkNewPage(6);
        let currentX = margin;

        doc.setFont('helvetica', 'bold');
        doc.text('Situação:', currentX, yPosition);
        doc.setFont('helvetica', 'normal');
        currentX += doc.getTextWidth('Situação: ') + 2;
        const situacaoWidth = pageWidth - currentX - margin;
        const situacaoLines = doc.splitTextToSize(item.situacao_compra_item_nome, situacaoWidth);
        doc.text(situacaoLines[0], currentX, yPosition);
        currentX += doc.getTextWidth(`${situacaoLines[0]} `) + 10;

        doc.setFont('helvetica', 'bold');
        doc.text('Quantidade:', currentX, yPosition);
        doc.setFont('helvetica', 'normal');
        currentX += doc.getTextWidth('Quantidade: ') + 2;
        const quantidadeFormatada = this.formatarQuantidade(item.quantidade);
        doc.text(quantidadeFormatada, currentX, yPosition);
        currentX += doc.getTextWidth(`${quantidadeFormatada} `) + 10;

        doc.setFont('helvetica', 'bold');
        doc.text('Unidade de fornecimento:', currentX, yPosition);
        doc.setFont('helvetica', 'normal');
        currentX += doc.getTextWidth('Unidade de fornecimento: ') + 2;
        const unidadeWidth = pageWidth - currentX - margin;
        const unidadeLines = doc.splitTextToSize(item.unidade_medida, unidadeWidth);
        doc.text(unidadeLines[0], currentX, yPosition);
        yPosition += 3;

        // Resultados do Item (otimizado)
        if (item.resultados && item.resultados.length > 0) {
          const resultados = item.resultados; // Variável local para evitar erro de lint
          checkNewPage(15);
          yPosition += 1;
          
          resultados.forEach((resultado, resIndex) => {
            checkNewPage(12);
            
            // Garante cor preta para cada resultado
            doc.setTextColor(33, 33, 33);
            
            doc.setFontSize(8);
            
            // Linha 2: Fornecedor
            doc.setFont('helvetica', 'bold');
            doc.text('Fornecedor:', margin, yPosition);
            doc.setFont('helvetica', 'normal');
            const fornecedorText = `${resultado.fornecedor_detalhes.cnpj_fornecedor} - ${resultado.fornecedor_detalhes.razao_social}`;
            const fornecedorLines = doc.splitTextToSize(fornecedorText, maxWidth - 45);
            doc.text(fornecedorLines, margin + 35, yPosition);
            yPosition += fornecedorLines.length * 3.5 + 1;

            // Linha 3: Valor Estimado Unitário, Valor Estimado Homologado e Percentual de Desconto
            checkNewPage(6);
            let resX = margin;

            const quantidadeNum = parseFloat(item.quantidade || '1');
            const valorUnitarioEstimado = item.valor_unitario_estimado
              ? parseFloat(item.valor_unitario_estimado)
              : (quantidadeNum > 0 ? parseFloat(item.valor_total_estimado || '0') / quantidadeNum : 0);

            doc.setFont('helvetica', 'bold');
            doc.text('Valor Estimado Unitário:', resX, yPosition);
            doc.setFont('helvetica', 'normal');
            resX += doc.getTextWidth('Valor Estimado Unitário: ') + 2;
            const valorEstimadoUnitText = this.formatarValor(valorUnitarioEstimado.toString());
            doc.text(valorEstimadoUnitText, resX, yPosition);
            resX += doc.getTextWidth(`${valorEstimadoUnitText} `) + 8;

            doc.setFont('helvetica', 'bold');
            doc.text('Valor Estimado Homologado:', resX, yPosition);
            doc.setFont('helvetica', 'normal');
            resX += doc.getTextWidth('Valor Estimado Homologado: ') + 2;
            const valorHomologadoUnitText = this.formatarValor(resultado.valor_unitario_homologado);
            doc.text(valorHomologadoUnitText, resX, yPosition);
            resX += doc.getTextWidth(`${valorHomologadoUnitText} `) + 8;

            if (valorUnitarioEstimado > 0) {
              const valorUnitarioHomologadoNum = parseFloat(resultado.valor_unitario_homologado || '0');
              const percentualDescUnit = ((valorUnitarioEstimado - valorUnitarioHomologadoNum) / valorUnitarioEstimado) * 100;
              doc.setFont('helvetica', 'bold');
              doc.text('Percentual de Desconto:', resX, yPosition);
              doc.setFont('helvetica', 'normal');
              resX += doc.getTextWidth('Percentual de Desconto: ') + 2;
              doc.text(`${percentualDescUnit.toFixed(2)}%`, resX, yPosition);
              resX += doc.getTextWidth(`${percentualDescUnit.toFixed(2)}% `) + 8;
            }

            yPosition += 3;
            
            // Linha separadora removida
          });
        }

        if (index < compra.itens.length - 1) {
          yPosition += 1;
          doc.setDrawColor(220, 220, 220);
          doc.setLineWidth(0.2);
          doc.line(margin, yPosition, pageWidth - margin, yPosition);
          doc.setDrawColor(0, 0, 0);
          yPosition += 4;
        }
      });
    }

    // Atualiza rodapé de todas as páginas com o número total correto
    for (let i = 1; i <= totalPages; i++) {
      doc.setPage(i);
      addFooter(i, totalPages);
    }

    // Salva o PDF
    const nomeArquivo = `Relatorio_Contratacao_${compraListagem.numero_compra.replace(/\//g, '_')}_${ano || 'N/A'}.pdf`;
    doc.save(nomeArquivo);
  }

  /**
   * Formata valor monetário
   */
  private formatarValor(valor: string | null | undefined): string {
    if (!valor) return '-';
    const num = parseFloat(valor);
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(num);
  }

  /**
   * Formata percentual
   */
  private formatarPercentual(valor: string | null | undefined): string {
    if (!valor) return '-';
    const num = parseFloat(valor);
    return `${num.toFixed(2)}%`;
  }

  /**
   * Formata data
   */
  private formatarData(data: string | null | undefined): string {
    if (!data) return '-';
    try {
      const date = new Date(data);
      return date.toLocaleDateString('pt-BR');
    } catch {
      return data;
    }
  }


  /**
   * Formata quantidade removendo zeros finais
   */
  private formatarQuantidade(valor: string | number | null | undefined): string {
    if (valor === null || valor === undefined) return '-';
    if (typeof valor === 'number') {
      return Number.isInteger(valor) ? `${valor}` : `${valor}`.replace(/0+$/g, '').replace(/[.,]$/g, '');
    }
    const texto = String(valor).trim();
    if (!texto) return '-';
    if (!/^-?\d+(?:[.,]\d+)?$/.test(texto)) return texto;
    return texto
      .replace(/([.,]\d*?[1-9])0+$/g, '$1')
      .replace(/[.,]0+$/g, '');
  }

  /**
   * Calcula resumo de itens por situação
   */
  private calcularResumoItens(compra: CompraDetalhada): {
    total: number;
    homologados: number;
    fracassados: number;
    emAndamento: number;
    percentualConclusao: string;
  } {
    const itens = compra.itens || [];
    const total = itens.length;

    const normalize = (texto: string) => texto.toLowerCase();
    const homologados = itens.filter((item) => normalize(item.situacao_compra_item_nome || '').includes('homolog')).length;
    const fracassados = itens.filter((item) => normalize(item.situacao_compra_item_nome || '').includes('fracass')).length;
    const emAndamento = itens.filter((item) => {
      const valor = normalize(item.situacao_compra_item_nome || '');
      return valor.includes('andamento') || valor.includes('em andamento');
    }).length;

    const percentualConclusao = total > 0 ? `${((homologados / total) * 100).toFixed(2)}%` : '-';

    return {
      total,
      homologados,
      fracassados,
      emAndamento,
      percentualConclusao
    };
  }
}
