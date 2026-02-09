import { Injectable } from '@angular/core';
import * as XLSX from 'xlsx';
import { CompraDetalhada, CompraListagem } from '../interfaces/pncp.interface';

@Injectable({
  providedIn: 'root'
})
export class RelatorioXlsxContratacaoService {
  private aplicarFormatoNumerico(
    ws: XLSX.WorkSheet,
    colunas: string[],
    formato: string,
    rowStart: number = 2
  ): void {
    const range = XLSX.utils.decode_range(ws['!ref'] || 'A1');
    colunas.forEach((colKey) => {
      const colIndex = this.getColIndex(ws, colKey);
      if (colIndex === null) return;
      for (let r = rowStart - 1; r <= range.e.r; r++) {
        const cellAddress = XLSX.utils.encode_cell({ r, c: colIndex });
        const cell = ws[cellAddress];
        if (cell && typeof cell.v === 'number') {
          cell.z = formato;
        }
      }
    });
  }

  private getColIndex(ws: XLSX.WorkSheet, colKey: string): number | null {
    if (!ws['!ref']) return null;
    const range = XLSX.utils.decode_range(ws['!ref']);
    for (let c = range.s.c; c <= range.e.c; c++) {
      const cellAddress = XLSX.utils.encode_cell({ r: range.s.r, c });
      const cell = ws[cellAddress];
      if (cell && String(cell.v).trim() === colKey) {
        return c;
      }
    }
    return null;
  }

  private limparCelulasZero(ws: XLSX.WorkSheet, colunas: string[], rowStart: number = 2): void {
    const range = XLSX.utils.decode_range(ws['!ref'] || 'A1');
    colunas.forEach((colKey) => {
      const colIndex = this.getColIndex(ws, colKey);
      if (colIndex === null) return;
      for (let r = rowStart - 1; r <= range.e.r; r++) {
        const cellAddress = XLSX.utils.encode_cell({ r, c: colIndex });
        const cell = ws[cellAddress];
        if (!cell) continue;
        const value = cell.v;
        if (value === 0 || value === '0' || value === null || value === undefined) {
          delete ws[cellAddress];
        }
      }
    });
  }

  gerarRelatorioXLSX(
    compra: CompraDetalhada,
    compraListagem: CompraListagem,
    uasgTexto: string,
    ano: number | null
  ): void {
    const wb = XLSX.utils.book_new();

    const compraData = [
      {
        modalidade: compraListagem.modalidade?.nome || 'N/A',
        numero_compra: compraListagem.numero_compra,
        ano_compra: compraListagem.ano_compra,
        uasg: uasgTexto,
        sequencial_pncp: compra.sequencial_compra,
        numero_processo: compraListagem.numero_processo || 'N/A',
        link_pncp: `https://pncp.gov.br/app/editais/00394502000144/${compraListagem.ano_compra}/${compra.sequencial_compra}`,
        objeto: compra.objeto_compra,
        amparo_legal: compra.amparo_legal?.nome || 'N/A',
        modo_disputa: compra.modo_disputa?.nome || 'N/A',
        data_publicacao_pncp: compra.data_publicacao_pncp || '',
        valor_total_estimado: parseFloat(compra.valor_total_estimado || '0'),
        valor_total_homologado: parseFloat(compra.valor_total_homologado || '0'),
        percentual_desconto: parseFloat(compra.percentual_desconto || '0') / 100
      }
    ];

    const compraHeaders = [
      'modalidade',
      'numero_compra',
      'ano_compra',
      'uasg',
      'sequencial_pncp',
      'numero_processo',
      'link_pncp',
      'objeto',
      'amparo_legal',
      'modo_disputa',
      'data_publicacao_pncp',
      'valor_total_estimado',
      'valor_total_homologado',
      'percentual_desconto'
    ];

    const wsCompra = XLSX.utils.json_to_sheet(compraData, { header: compraHeaders });
    this.aplicarFormatoNumerico(wsCompra, [
      'valor_total_estimado',
      'valor_total_homologado'
    ], '#.##0,0000');
    this.aplicarFormatoNumerico(wsCompra, ['percentual_desconto'], '0,00%');
    XLSX.utils.book_append_sheet(wb, wsCompra, 'contratacao');

    const itensData = (compra.itens || []).map(item => {
      const valorHomologadoTotal = (item.resultados || []).reduce((sum, res) => {
        return sum + parseFloat(res.valor_total_homologado || '0');
      }, 0);

      const quantidadeNum = parseFloat(item.quantidade || '0') || 0;
      const valorUnitarioEstimadoNum = item.valor_unitario_estimado
        ? parseFloat(item.valor_unitario_estimado)
        : (quantidadeNum > 0 ? parseFloat(item.valor_total_estimado || '0') / quantidadeNum : 0);

      const totalQtdHomologada = (item.resultados || []).reduce((sum, res) => {
        return sum + (res.quantidade_homologada || 0);
      }, 0);

      const somaValorUnitHomologado = (item.resultados || []).reduce((sum, res) => {
        const valorUnit = parseFloat(res.valor_unitario_homologado || '0');
        return sum + (valorUnit * (res.quantidade_homologada || 0));
      }, 0);

      const valorUnitarioHomologadoNum = totalQtdHomologada > 0
        ? somaValorUnitHomologado / totalQtdHomologada
        : 0;

      const percentualDescontoNum = valorUnitarioEstimadoNum > 0
        ? ((valorUnitarioEstimadoNum - valorUnitarioHomologadoNum) / valorUnitarioEstimadoNum)
        : 0;

      return {
        numero_item: item.numero_item,
        descricao: item.descricao,
        quantidade: parseFloat(item.quantidade || '0'),
        unidade_medida: item.unidade_medida,
        valor_total_estimado: parseFloat(item.valor_total_estimado || '0'),
        valor_total_homologado: (item.resultados && item.resultados.length > 0 && valorHomologadoTotal > 0)
          ? valorHomologadoTotal
          : null,
        valor_unitario_estimado: valorUnitarioEstimadoNum,
        valor_unitario_homologado: totalQtdHomologada > 0
          ? valorUnitarioHomologadoNum
          : null,
        percentual_desconto: totalQtdHomologada > 0 && percentualDescontoNum > 0
          ? percentualDescontoNum
          : null,
        situacao: item.situacao_compra_item_nome
      };
    });

    const itensHeaders = [
      'numero_item',
      'descricao',
      'quantidade',
      'unidade_medida',
      'valor_total_estimado',
      'valor_total_homologado',
      'valor_unitario_estimado',
      'valor_unitario_homologado',
      'percentual_desconto',
      'situacao'
    ];

    const wsItens = XLSX.utils.json_to_sheet(itensData.length > 0 ? itensData : [{}], {
      header: itensHeaders
    });

    this.limparCelulasZero(wsItens, ['valor_total_homologado', 'percentual_desconto']);
    this.aplicarFormatoNumerico(wsItens, [
      'quantidade',
      'valor_total_estimado',
      'valor_total_homologado',
      'valor_unitario_estimado',
      'valor_unitario_homologado'
    ], '#.##0,0000');
    this.aplicarFormatoNumerico(wsItens, ['percentual_desconto'], '0,00%');
    XLSX.utils.book_append_sheet(wb, wsItens, 'itens');

    const resultadosData: Array<Record<string, string | number | null>> = [];
    (compra.itens || []).forEach(item => {
      (item.resultados || []).forEach(resultado => {
        resultadosData.push({
          numero_item: item.numero_item,
          descricao_item: item.descricao,
          fornecedor_cnpj: resultado.fornecedor_detalhes.cnpj_fornecedor,
          fornecedor_razao_social: resultado.fornecedor_detalhes.razao_social,
          quantidade_homologada: resultado.quantidade_homologada ?? 0,
          valor_unitario_homologado: parseFloat(resultado.valor_unitario_homologado || '0'),
          valor_total_homologado: parseFloat(resultado.valor_total_homologado || '0')
        });
      });
    });

    const resultadosHeaders = [
      'numero_item',
      'descricao_item',
      'fornecedor_cnpj',
      'fornecedor_razao_social',
      'quantidade_homologada',
      'valor_unitario_homologado',
      'valor_total_homologado'
    ];

    const wsResultados = XLSX.utils.json_to_sheet(resultadosData.length > 0 ? resultadosData : [{}], {
      header: resultadosHeaders
    });
    this.aplicarFormatoNumerico(wsResultados, [
      'quantidade_homologada',
      'valor_unitario_homologado',
      'valor_total_homologado'
    ], '#.##0,0000');
    XLSX.utils.book_append_sheet(wb, wsResultados, 'resultados');

    const nomeArquivo = `Relatorio_Contratacao_${compraListagem.numero_compra.replace(/\//g, '_')}_${ano || 'N/A'}.xlsx`;
    XLSX.writeFile(wb, nomeArquivo);
  }
}
