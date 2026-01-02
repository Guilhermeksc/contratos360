import { Route } from '@angular/router';

type ComponentLoader = () => Promise<any>;

export interface RouteSegmentConfig {
  title: string;
  path: string;
  loadComponent: ComponentLoader;
  children?: RouteSegmentConfig[];
}

export interface ModuleRouteConfig {
  title: string;
  path: string;
  defaultChild?: string;
  segments: RouteSegmentConfig[];
}

export const MODULE_ROUTE_CONFIGS: ModuleRouteConfig[] = [
  {
    title: 'App1 Intendência',
    path: 'app1-intendencia',
    defaultChild: 'bibliografia',
    segments: [
      {
        title: 'Bibliografia',
        path: 'bibliografia',
        loadComponent: () =>
          import('../modules/app1-intendencia/app1-intendencia-bibliografia/app1-intendencia-bibliografia').then(
            (m) => m.App1IntendenciaBibliografia
          ),
        children: [
          {
            title: 'Cadeias de Suprimentos e Logística',
            path: 'cadeias-suprimentos-logistica',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/1-cadeias-suprimentos-logistica/cadeias-suprimentos-logistica').then(
                (m) => m.CadeiasSuprimentosLogistica
              )
          },
          {
            title: 'EMA-400 - Logística da Marinha',
            path: 'ema-400',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/2-ema-400/ema-400').then(
                (m) => m.Ema400
              )
          },
          {
            title: 'EMA-401 - Mobilização Marítima',
            path: 'ema-401',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/3-ema-401/ema-401').then(
                (m) => m.Ema401
              )
          },
          {
            title: 'MD-41-M-01 - Doutrina de Mobilização Militar',
            path: 'md-41-m-01',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/4-md-41-m-01/md-41-m-01').then(
                (m) => m.Md41M01
              )
          },
          {
            title: 'MD-41-M-02 - Manual de Mobilização Militar',
            path: 'md-41-m-02',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/5-md-41-m-02/md-41-m-02').then(
                (m) => m.Md41M02
              )
          },
          {
            title: 'MD-41-M-03 - Manual para o Planejamento da Mobilização Militar',
            path: 'md-41-m-03',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/6-md-41-m-03/md-41-m-03').then(
                (m) => m.Md41M03
              )
            },
            {
            title: 'Lei nº 11.631/2007 - Lei de Mobilização Nacional',
            path: 'lei-11631',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/7-lei11631/lei11631').then(
                (m) => m.Lei11631
              )
          },
          {
            title: 'Decreto nº 6.592/2008 - Regulamenta a Lei de Mobilização Nacional',
            path: 'lei-6592',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/8-decreto6592/decreto6592').then(
                (m) => m.Decreto6592
              )
          },
          {
            title: 'EMA-420 - Diretrizes para Gestão dos Sistemas de Defesa e Embarcações de Apoio',
            path: 'ema-420',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/9-ema-420/ema-420').then(
                (m) => m.Ema420
              )
          },
          {
            title: 'DGMM-0130 - Manual do Apoio Logístico Integrado',
            path: 'dgmm-0130',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/10-dgmm-0130/dgmm-0130').then(
                (m) => m.Dgmm0130
              )
          },
          {
            title: 'MD-40-M-01 - Manual de Boas Práticas para a Gestão do Ciclo de Vida de Sistemas de Defesa',
            path: 'md-40-m-01',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/11-md-40-m-01/md-40-m-01').then(
                (m) => m.Md40M01
              )
          },
          {
            title: 'MD-44-M-02 - Manual de Boas Práticas de Custo do Ciclo de Vida de Sistemas de Defesa',
            path: 'md-44-m-02',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/12-md-44-m-02/md-44-m-02').then(
                (m) => m.Md44M02
              )
          },
          {
            title: 'SGM-201 - Normas para Execução do Abastecimento',
            path: 'sgm-201',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/13-sgm201/sgm201').then(
                (m) => m.Sgm201
              )
          },
          {
            title: 'Decreto nº 7.970/2013 - Regulamenta a Lei nº 12.598/2012 e estabelece normas especiais para a compra, contratação e desenvolvimento de produtos e sistemas de defesa',
            path: 'decreto-7970',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/14-decreto7970/decreto7970').then(
                (m) => m.Decreto7970
              )
          },
          {
            title: 'Lei nº 12.598/2012 - Estabelece normas especiais para a compra, contratação e desenvolvimento de produtos e sistemas de defesa',
            path: 'lei-12598',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/15-lei12598/lei12598').then(
                (m) => m.Lei12598
              )
          },
          {
            title: 'Lei nº 14.133/2021 - Lei de Licitações e Contratos Administrativos',
            path: 'lei-14133',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/16-lei14133/lei14133').then(
                (m) => m.Lei14133
              )
          },
          {
            title: 'Portaria nº 280/2019 - Aprova as Normas de Compensação Tecnológica, Industrial e Comercial (Offset)',
            path: 'portaria-280',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/17-portaria280/portaria280').then(
                (m) => m.Portaria280
              )
          },
          {
            title: 'Portaria nº 223/2016 - Aprova as Diretrizes para a Compensação Comercial, Industrial e Tecnológica (“OFFSET”)',
            path: 'portaria-223',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/18-portaria223/portaria223').then(
                (m) => m.Portaria223
              )
          },
          {
            title: 'Portaria nº 899/2005 - Aprova a Política Nacional da Indústria de Defesa',
            path: 'portaria-899',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/19-portaria899/portaria899').then(
                (m) => m.Portaria899
              )
          },
          {
            title: 'Portaria nº 586/2006 - Aprova as Ações Estratégicas para a Política Nacional da Indústria de Defesa',
            path: 'portaria-586',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/20-portaria586/portaria586').then(
                (m) => m.Portaria586
              )
          },
          {
            title: 'Portaria nº 15/2018 - Aprova a Política de Obtenção de Produtos de Defesa (POBPRODE)',
            path: 'portaria-15',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/21-portaria15/portaria15').then(
                (m) => m.Portaria15
              )
          },
          {
            title: 'Portaria nº 3.662/2021 - Estabelece a Política de Compensação Tecnológica, Industrial e Comercial do Ministério da Defesa - PComTIC Defesa',
            path: 'portaria-3662',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/22-portaria3662/portaria3662').then(
                (m) => m.Portaria3662
              )
          },
          {
            title: 'SGM-301 - Normas para Execução do Abastecimento',
            path: 'sgm-301',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/23-sgm301/sgm301').then(
                (m) => m.Sgm301
              )
          },
          {
            title: 'MTO - Manual Técnico de Orçamento',
            path: 'mto',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/24-mto/mto').then(
                (m) => m.Mto
              )
          },
          {
            title: 'SGM-601 - Normas sobre Auditoria, Análise e Apresentação de Contas na Marinha',
            path: 'sgm-601',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/25-sgm601/sgm601').then(
                (m) => m.Sgm601
              )
          },
          {
            title: 'SGM-602 - Normas sobre Ressarcimento ao Erário',
            path: 'sgm-602',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/26-sgm602/sgm602').then(
                (m) => m.Sgm602
              )
          },
          {
            title: 'IN-98 - Instrução Normativa sobre a instauração, a organização e o encaminhamento ao Tribunal de Contas da União dos processos de tomada de contas especial',
            path: 'in-98',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/27-in98/in98').then(
                (m) => m.In98
              )
          },
          {
            title: 'IN-3 - Instrução Normativa sobre a instauração, a organização e o encaminhamento ao Tribunal de Contas da União dos processos de tomada de contas especial',
            path: 'in-3',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/28-in3/in3').then(
                (m) => m.In3
              )
          },
          {
            title: 'SGM-107 - Normas sobre Excelência de Gestão',
            path: 'sgm-107',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/29-sgm107/sgm107').then(
                (m) => m.Sgm107
              )
          },
          {
            title: 'SGM-401 - Normas para a Gestão do Plano Diretor',
            path: 'sgm-401',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/30-sgm401/sgm401').then(
                (m) => m.Sgm401
              )
          },
          {
            title: 'EMA-020 - Normas de Governança da Marinha',
            path: 'ema-020',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/31-ema020/ema020').then(
                (m) => m.Ema020
              )
          },
          {
            title: 'EMA-301 - Fundamentos Doutrinários da Marinha',
            path: 'ema-301',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/32-ema301/ema301').then(
                (m) => m.Ema301
              )
          },
          {
            title: 'EMA-305 - Doutrina Militar Naval',
            path: 'ema-305',
            loadComponent: () =>
              import('../modules/app1-intendencia/app1-intendencia-bibliografia/33-ema305/ema305').then(
                (m) => m.Ema305
              )
          }
        ]
      },
      {
        title: 'Flash Cards',
        path: 'flash-cards',
        loadComponent: () =>
          import(
            '../modules/app1-intendencia/app1-intendencia-flashcards/app1-intendencia-flashcards'
          ).then((m) => m.App1IntendenciaFlashcards)
      },         
      {
        title: 'Perguntas',
        path: 'perguntas',
        loadComponent: () =>
          import(
            '../modules/app1-intendencia/app1-intendencia-perguntas/app1-intendencia-perguntas'
          ).then((m) => m.App1IntendenciaPerguntas)
      },
    ]
  },
  {
    title: 'App2 Estratégia',
    path: 'app2-estrategia',
    defaultChild: 'bibliografia',
    segments: [
      {
        title: 'Bibliografia',
        path: 'bibliografia',
        loadComponent: () =>
          import('../modules/app2-estrategia/app2-estrategia-bibliografia/app2-estrategia-bibliografia').then(
            (m) => m.App2EstrategiaBibliografia
          ),
        children: [
          {
            title: 'COUTAU-BÉGARIE. Tratado de Estratégia',
            path: 'tratado-de-estrategia',
            loadComponent: () =>
              import('../modules/app2-estrategia/app2-estrategia-bibliografia/tratado-de-estrategia/tratado-de-estrategia').then(
                (m) => m.TratadoDeEstrategia
              )
          },
          {
            title: 'WEDIN. Estratégias Marítimas no Século XXI: A contribuição do Almirante Castex',
            path: 'estrategias-maritimas',
            loadComponent: () =>
              import('../modules/app2-estrategia/app2-estrategia-bibliografia/estrategias-maritimas/estrategias-maritimas').then(
                (m) => m.EstrategiasMaritimas
              )
          },
          {
            title: 'EMA-310 - Estratégia de Defesa Marítima',
            path: 'ema-310-estrategia',
            loadComponent: () =>
              import('../modules/app2-estrategia/app2-estrategia-bibliografia/ema-310-estrategia/ema-310-estrategia').then(
                (m) => m.Ema310Estrategia
              )
          }
        ]
      },
      {
        title: 'Flash Cards',
        path: 'flash-cards',
        loadComponent: () =>
          import(
            '../modules/app2-estrategia/app2-estrategia-flashcards/app2-estrategia-flashcards'
          ).then((m) => m.App2EstrategiaFlashcards)
      }, 
      {
        title: 'Perguntas',
        path: 'perguntas',
        loadComponent: () =>
          import('../modules/app2-estrategia/app2-estrategia-perguntas/app2-estrategia-perguntas').then(
            (m) => m.App2EstrategiaPerguntas
          )
      },
      {
        title: 'Conceitos',
        path: 'conceitos',
        loadComponent: () =>
          import('../modules/app2-estrategia/app2-estrategia-conceitos/app2-estrategia-conceitos').then(
            (m) => m.App2EstrategiaConceitos
          )
      }
    ]
  },
  {
    title: 'App3 Planejamento Militar',
    path: 'app3-planejamento-militar',
    defaultChild: 'bibliografia',
    segments: [
      {
        title: 'Bibliografia',
        path: 'bibliografia',
        loadComponent: () =>
          import('../modules/app3-planejamento-militar/app3-planejamento-militar-bibliografia/app3-planejamento-militar-bibliografia').then(
            (m) => m.App3PlanejamentoMilitarBibliografia
          ),
        children: [
          {
            title: 'Lei nº 97/1999 - Organização, Preparo e o Emprego das Forças Armadas',
            path: 'lei-97',
            loadComponent: () =>
              import('../modules/app3-planejamento-militar/app3-planejamento-militar-bibliografia/lei-97/lei-97').then(
                (m) => m.Lei97
              )
          },
          {
            title: 'Decreto 7.276/2010 - Estrutura Militar de Defesa',
            path: 'decreto-7276',
            loadComponent: () =>
              import('../modules/app3-planejamento-militar/app3-planejamento-militar-bibliografia/decreto-7276/decreto-7276').then(
                (m) => m.Decreto7276
              )
          },
          {
            title: 'MD30-M-01 - Doutrina de Operações Conjuntas',
            path: 'md-30-m-01',
            loadComponent: () =>
              import('../modules/app3-planejamento-militar/app3-planejamento-militar-bibliografia/md-30-m-01/md-30-m-01').then(
                (m) => m.Md30M01
              )
          },
          {
            title: 'MD30-M-01 (2º Volume) - Doutrina de Operações Conjuntas',
            path: 'md-30-m-01-2',
            loadComponent: () =>
              import('../modules/app3-planejamento-militar/app3-planejamento-militar-bibliografia/md-30-m-01-2/md-30-m-01-2').then(
                (m) => m.Md30M012
              )
          }
        ]
      },
      {
        title: 'Flash Cards',
        path: 'flash-cards',
        loadComponent: () =>
          import(
            '../modules/app3-planejamento-militar/app3-planejamento-militar-flashcards/app3-planejamento-militar-flashcards'
          ).then((m) => m.App3PlanejamentoMilitarFlashcards)
      },
      {
        title: 'Perguntas',
        path: 'perguntas',
        loadComponent: () =>
          import(
            '../modules/app3-planejamento-militar/app3-planejamento-militar-perguntas/app3-planejamento-militar-perguntas'
          ).then((m) => m.App3PlanejamentoMilitarPerguntas)
      },
      {
        title: 'Conceitos',
        path: 'conceitos',
        loadComponent: () =>
          import('../modules/app3-planejamento-militar/app3-planejamento-militar-conceitos/app3-planejamento-militar-conceitos').then(
            (m) => m.App3PlanejamentoMilitarConceitos
          )
      },
    ]
  },
  {
    title: 'App4 História',
    path: 'app4-historia',
    defaultChild: 'bibliografia',
    segments: [
      {
        title: 'Bibliografia',
        path: 'bibliografia',
        loadComponent: () =>
          import('../modules/app4-historia/app4-historia-bibliografia/app4-historia-bibliografia').then(
            (m) => m.App4HistoriaBibliografia
          ),
        children: [
          {
            title: 'Breve História',
            path: 'breve-historia',
            loadComponent: () =>
              import('../modules/app4-historia/app4-historia-bibliografia/breve-historia/breve-historia').then(
                (m) => m.BreveHistoria
              )
          },
          {
            title: 'Guerra no Mar',
            path: 'guerra-no-mar',
            loadComponent: () =>
              import('../modules/app4-historia/app4-historia-bibliografia/guerra-no-mar/guerra-no-mar').then(
                (m) => m.GuerraNoMar
              )
          },
          {
            title: 'História das Guerras',
            path: 'historia-das-guerras',
            loadComponent: () =>
              import('../modules/app4-historia/app4-historia-bibliografia/historia-das-guerras/historia-das-guerras').then(
                (m) => m.HistoriaDasGuerras
              )
          },
          {
            title: 'Síntese Histórica',
            path: 'sintese-historica',
            loadComponent: () =>
              import('../modules/app4-historia/app4-historia-bibliografia/sintese-historica/sintese-historica').then(
                (m) => m.SinteseHistorica
              )
          }
        ]
      },
      {
        title: 'Flash Cards',
        path: 'flash-cards',
        loadComponent: () =>
          import(
            '../modules/app4-historia/app4-historia-flashcards/app4-historia-flashcards'
          ).then((m) => m.App4HistoriaFlashcards)
      },
      {
        title: 'Perguntas',
        path: 'perguntas',
        loadComponent: () =>
          import('../modules/app4-historia/app4-historia-perguntas/app4-historia-perguntas').then(
            (m) => m.App4HistoriaPerguntas
          )
      },
      {
        title: 'Líderes Históricos',
        path: 'lideres-historicos',
        loadComponent: () =>
          import(
            '../modules/app4-historia/app4-historia-lideres/app4-historia-lideres'
          ).then((m) => m.App4HistoriaLideres)
      }
    ]
  },
  {
    title: 'App6 Geopolítica',
    path: 'app6-geopolitica-relacoes-internacionais',
    defaultChild: 'bibliografia',
    segments: [
      {
        title: 'Bibliografia',
        path: 'bibliografia',
        loadComponent: () =>
          import('../modules/app6-geopolitica-relacoes-internacionais/app6-geopolitica-relacoes-internacionais-bibliografia/app6-geopolitica-relacoes-internacionais-bibliografia').then(
            (m) => m.App6GeopoliticaRelacoesInternacionaisBibliografia
          ),
        children: [
          {
            title: 'A Vingança da Geografia',
            path: 'vinganca-geografia',
            loadComponent: () =>
              import('../modules/app6-geopolitica-relacoes-internacionais/app6-geopolitica-relacoes-internacionais-bibliografia/vinganca-geografia/vinganca-geografia').then(
                (m) => m.VingancaGeografia
              )
          },
          {
            title: 'Geopolítica e Modernidade',
            path: 'geopolitica-modernidade',
            loadComponent: () =>
              import('../modules/app6-geopolitica-relacoes-internacionais/app6-geopolitica-relacoes-internacionais-bibliografia/geopolitica-modernidade/geopolitica-modernidade').then(
                (m) => m.GeopoliticaModernidade
              )
          },
          {
            title: 'Novas Geopolíticas',
            path: 'novas-geopoliticas',
            loadComponent: () =>
              import('../modules/app6-geopolitica-relacoes-internacionais/app6-geopolitica-relacoes-internacionais-bibliografia/novas-geopoliticas/novas-geopoliticas').then(
                (m) => m.NovasGeopoliticas
              )
          },
          {
            title: 'Princípios de Relações Internacionais',
            path: 'principios-ri',
            loadComponent: () =>
              import('../modules/app6-geopolitica-relacoes-internacionais/app6-geopolitica-relacoes-internacionais-bibliografia/principios-ri/principios-ri').then(
                (m) => m.PrincipiosRi
              )
          }
        ]
      },
      {
        title: 'Flash Cards',
        path: 'flash-cards',
        loadComponent: () =>
          import(
            '../modules/app6-geopolitica-relacoes-internacionais/app6-geopolitica-relacoes-internacionais-flashcards/app6-geopolitica-relacoes-internacionais-flashcards'
          ).then((m) => m.App6GeopoliticaRelacoesInternacionaisFlashcards)
      },
      {
        title: 'Perguntas',
        path: 'perguntas',
        loadComponent: () =>
          import(
            '../modules/app6-geopolitica-relacoes-internacionais/app6-geopolitica-relacoes-internacionais-perguntas/app6-geopolitica-relacoes-internacionais-perguntas'
          ).then((m) => m.App6GeopoliticaRelacoesInternacionaisPerguntas)
      },
      {
        title: 'Conceitos',
        path: 'conceitos',
        loadComponent: () =>
          import(
            '../modules/app6-geopolitica-relacoes-internacionais/app6-geopolitica-relacoes-internacionais-conceitos/app6-geopolitica-relacoes-internacionais-conceitos'
          ).then((m) => m.App6GeopoliticaRelacoesInternacionaisConceitos)
      },
      {
        title: 'Teóricos',
        path: 'teoricos',
        loadComponent: () =>
          import(
            '../modules/app6-geopolitica-relacoes-internacionais/app6-geopolitica-relacoes-internacionais-pensadores/app6-geopolitica-relacoes-internacionais-pensadores'
          ).then((m) => m.App6GeopoliticaRelacoesInternacionaisPensadores)
      }
    ]
  },
  {
    title: 'App7 Política',
    path: 'app7-politica',
    defaultChild: 'bibliografia',
    segments: [
      {
        title: 'Bibliografia',
        path: 'bibliografia',
        loadComponent: () =>
          import('../modules/app7-politica/app7-politica-bibliografia/app7-politica-bibliografia').then(
            (m) => m.App7PoliticaBibliografia
          ),
        children: [
          {
            title: 'Ciência Política',
            path: 'ciencia-politica',
            loadComponent: () =>
              import('../modules/app7-politica/app7-politica-bibliografia/ciencia-politica/ciencia-politica').then(
                (m) => m.CienciaPolitica
              )
          },
          {
            title: 'Constituição da República Federativa do Brasil',
            path: 'constituicao-brasil',
            loadComponent: () =>
              import('../modules/app7-politica/app7-politica-bibliografia/constituicao-brasil/constituicao-brasil').then(
                (m) => m.ConstituicaoBrasil
              )
          },
          {
            title: 'Estratégia Nacional de Defesa',
            path: 'estrategia-nacional-defesa',
            loadComponent: () =>
              import('../modules/app7-politica/app7-politica-bibliografia/estrategia-nacional-defesa/estrategia-nacional-defesa').then(
                (m) => m.EstrategiaNacionalDefesa
              )
          },
          {
            title: 'Política Nacional de Defesa',
            path: 'politica-nacional-defesa',
            loadComponent: () =>
              import('../modules/app7-politica/app7-politica-bibliografia/politica-nacional-defesa/politica-nacional-defesa').then(
                (m) => m.PoliticaNacionalDefesa
              )
          },
          {
            title: 'Lei Complementar nº 97',
            path: 'lei-complementar-97',
            loadComponent: () =>
              import('../modules/app7-politica/app7-politica-bibliografia/lei-complementar-97/lei-complementar-97').then(
                (m) => m.LeiComplementar97
              )
          },
          {
            title: 'Decreto nº 12.481 - Política Marítima Nacional (PMN)',
            path: 'decreto-12481',
            loadComponent: () =>
              import('../modules/app7-politica/app7-politica-bibliografia/decreto-12481/decreto-12481').then(
                (m) => m.Decreto12481
              )
          },
          {
            title: 'Economia Azul - vetor para o desenvolvimento do Brasil',
            path: 'economia-azul',
            loadComponent: () =>
              import('../modules/app7-politica/app7-politica-bibliografia/economia-azul/economia-azul').then(
                (m) => m.EconomiaAzul
              )
          },
          {
            title: 'EMA-323 - Política Naval',
            path: 'ema-323',
            loadComponent: () =>
              import('../modules/app7-politica/app7-politica-bibliografia/ema-323/ema-323').then(
                (m) => m.Ema323
              )
          },
          {
            title: 'Decreto nº 12.363 - Plano Setorial para os Recursos do Mar',
            path: 'decreto-12363',
            loadComponent: () =>
              import('../modules/app7-politica/app7-politica-bibliografia/decreto-12363/decreto-12363').then(
                (m) => m.Decreto12363
              )
          }
        ]
      },
      {
        title: 'Flash Cards',
        path: 'flash-cards',
        loadComponent: () =>
          import(
            '../modules/app7-politica/app7-politica-flashcards/app7-politica-flashcards'
          ).then((m) => m.App7PoliticaFlashcards)
      },
      {
        title: 'Conceitos',
        path: 'conceitos',
        loadComponent: () =>
          import('../modules/app7-politica/app7-politica-conceitos/app7-politica-conceitos').then(
            (m) => m.App7PoliticaConceitos
          )
      },
      {
        title: 'Perguntas',
        path: 'perguntas',
        loadComponent: () =>
          import('../modules/app7-politica/app7-politica-perguntas/app7-politica-perguntas').then(
            (m) => m.App7PoliticaPerguntas
          )
      },
      {
        title: 'Resumo',
        path: 'resumo',
        loadComponent: () =>
          import('../modules/app7-politica/app7-politica-resumo/app7-politica-resumo').then(
            (m) => m.App7PoliticaResumo
          )
      }
    ]
  },
  {
    title: 'App8 Direito',
    path: 'app8-direito',
    defaultChild: 'bibliografia',
    segments: [
  {
        title: 'Bibliografia',
        path: 'bibliografia',
        loadComponent: () =>
          import('../modules/app8-direito/app8-direito-bibliografia/app8-direito-bibliografia').then(
            (m) => m.App8DireitoBibliografia
          ),
        children: [
          {
            title: 'EMA-135',
            path: 'ema-135',
            loadComponent: () =>
              import('../modules/app8-direito/app8-direito-bibliografia/ema-135/ema-135').then(
                (m) => m.Ema135
              )
          },
          {
            title: 'A Lei da Guerra',
            path: 'lei-da-guerra',
            loadComponent: () =>
              import('../modules/app8-direito/app8-direito-bibliografia/lei-da-guerra/lei-da-guerra').then(
                (m) => m.LeiDaGuerra
              )
          },
          {
            title: 'Carta das Nações Unidas',
            path: 'carta-nacoes-unidas',
            loadComponent: () =>
              import('../modules/app8-direito/app8-direito-bibliografia/3-carta-nacoes-unidas/carta-nacoes-unidas').then(
                (m) => m.CartaNacoesUnidas
              )
          },
          {
            title: 'Feridos, enfermos e náufragos',
            path: 'feridos-enfermos',
            loadComponent: () =>
              import('../modules/app8-direito/app8-direito-bibliografia/feridos-enfermos/feridos-enfermos').then(
                (m) => m.FeridosEnfermos
              )
          },
          {
            title: 'Protocolo I',
            path: 'protocolo-i',
            loadComponent: () =>
              import('../modules/app8-direito/app8-direito-bibliografia/protocolo-i/protocolo-i').then(
                (m) => m.ProtocoloI
              )
          },
          {
            title: 'Protocolo II',
            path: 'protocolo-ii',
            loadComponent: () =>
              import('../modules/app8-direito/app8-direito-bibliografia/protocolo-ii/protocolo-ii').then(
                (m) => m.ProtocoloII
              )
          },
          {
            title: 'San Remo Manual',
            path: 'san-remo-manual',
            loadComponent: () =>
              import('../modules/app8-direito/app8-direito-bibliografia/san-remo-manual/san-remo-manual').then(
                (m) => m.SanRemoManual
              )
          },
          {
            title: 'Concenção das Nações Unidas sobre o Direito do Mar',
            path: 'cnudm',
            loadComponent: () =>
              import('../modules/app8-direito/app8-direito-bibliografia/cnudm/cnudm').then(
                (m) => m.Cnudm
              )
          },
          {
            title: 'Entorpecentes e Psicotrópicos',
            path: 'entorpecentes-psicotropicos',
            loadComponent: () =>
              import('../modules/app8-direito/app8-direito-bibliografia/entorpecentes-psicotropicos/entorpecentes-psicotropicos').then(
                (m) => m.EntorpecentesPsicotropicos
              )
          },
          {
            title: 'Pacto de São José',
            path: 'pacto-sao-jose',
            loadComponent: () =>
              import('../modules/app8-direito/app8-direito-bibliografia/pacto-sao-jose/pacto-sao-jose').then(
                (m) => m.PactoSaoJose
              )
          },
          {
            title: 'Declaração Universal dos Direitos Humanos',
            path: 'declaracao-direitos-humanos',
            loadComponent: () =>
              import('../modules/app8-direito/app8-direito-bibliografia/declaracao-direitos-humanos/declaracao-direitos-humanos').then(
                (m) => m.DeclaracaoDireitosHumanos
              )
          },
          {
            title: 'Direito dos Tratados',
            path: 'declaracao-direito-tratados',
            loadComponent: () =>
              import('../modules/app8-direito/app8-direito-bibliografia/declaracao-direito-tratados/declaracao-direito-tratados').then(
                (m) => m.DeclaracaoDireitoTratados
              )
          }
        ]
      },
      {
        title: 'Flash Cards',
        path: 'flash-cards',
        loadComponent: () =>
          import('../modules/app8-direito/app8-direito-flashcards/app8-direito-flashcards').then((m) => m.App8DireitoFlashcards)
      },
      {
        title: 'Conceitos',
        path: 'conceitos',
        loadComponent: () =>
          import('../modules/app8-direito/app8-direito-conceitos/app8-direito-conceitos').then((m) => m.App8DireitoConceitos)
      },
      {
        title: 'Perguntas',
        path: 'perguntas',
        loadComponent: () =>
          import('../modules/app8-direito/app8-direito-perguntas/app8-direito-perguntas').then(
            (m) => m.App8DireitoPerguntas
          )
      },
      {
        title: 'Resumo',
        path: 'resumo',
        loadComponent: () =>
          import('../modules/app8-direito/app8-direito-resumo/app8-direito-resumo').then(
            (m) => m.App8DireitoResumo
          )
      }
    ]
  },
  {
    title: 'App9 Economia',
    path: 'app9-economia',
    defaultChild: 'bibliografia',
    segments: [
      {
        title: 'Bibliografia',
        path: 'bibliografia',
        loadComponent: () =>
          import('../modules/app9-economia/app9-economia-bibliografia/app9-economia-bibliografia').then(
            (m) => m.App9EconomiaBibliografia
          ),
        children: [
          {
            title: 'Economia Brasileira Contemporânea',
            path: 'economia-brasileira',
            loadComponent: () =>
              import('../modules/app9-economia/app9-economia-bibliografia/economia-brasileira/economia-brasileira').then(
                (m) => m.EconomiaBrasileira
              )
          },
          {
            title: 'Economia Micro e Macro – Teoria, Exercícios e Casos',
            path: 'economia-micro-macro',
            loadComponent: () =>
              import('../modules/app9-economia/app9-economia-bibliografia/economia-micro-macro/economia-micro-macro').then(
                (m) => m.EconomiaMicroMacro
              )
          },
          {
            title: 'Economia Azul',
            path: 'economia-azul-2',
            loadComponent: () =>
              import('../modules/app9-economia/app9-economia-bibliografia/economia-azul-2/economia-azul-2').then(
                (m) => m.EconomiaAzul2
              )
          }
        ]
      },
      {
        title: 'Flash Cards',
        path: 'flash-cards',
        loadComponent: () =>
          import(
            '../modules/app9-economia/app9-economia-flashcards/app9-economia-flashcards'
          ).then((m) => m.App9EconomiaFlashcards)
      }, 
      {
        title: 'Perguntas',
        path: 'perguntas',
        loadComponent: () =>
          import('../modules/app9-economia/app9-economia-perguntas/app9-economia-perguntas').then(
            (m) => m.App9EconomiaPerguntas
          )
      },
      {
        title: 'Conceitos',
        path: 'conceitos',
        loadComponent: () =>
          import(
            '../modules/app9-economia/app9-economia-conceitos/app9-economia-conceitos'
          ).then((m) => m.App9EconomiaConceitos)
      }
    ]
  }
];

export const moduleRoutes: Route[] = MODULE_ROUTE_CONFIGS.map(({ path, defaultChild, segments }) => {
  const children: Route['children'] = [
    {
      path: '',
      redirectTo: defaultChild ?? segments[0]?.path ?? '',
      pathMatch: 'full'
    },
    ...segments.map(({ path: segmentPath, loadComponent, children }) => {
      if (children && children.length > 0) {
        // Se tem filhos, criar rotas aninhadas SEM redirecionamento automático
        const nestedChildren: Route['children'] = [
          ...children.map(({ path: childPath, loadComponent: childLoadComponent }) => ({
            path: childPath,
            loadComponent: childLoadComponent
          }))
        ];
        
        return {
          path: segmentPath,
          loadComponent,
          children: nestedChildren
        };
      } else {
        // Se não tem filhos, rota simples
        return {
          path: segmentPath,
          loadComponent
        };
      }
    })
  ];

  return {
    path,
    children
  };
});

export const defaultHomeRedirect = `${MODULE_ROUTE_CONFIGS[0]?.path ?? ''}/${
  MODULE_ROUTE_CONFIGS[0]?.defaultChild ?? MODULE_ROUTE_CONFIGS[0]?.segments[0]?.path ?? ''
}`;
