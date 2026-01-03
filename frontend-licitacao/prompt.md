# Prompt de Implementação - Landing Page

- Inserir uma divisória logo após `<div class="modules-grid">` em `src/app/pages/home/home-landing/home-landing.component.html`, criando uma nova seção com 3 cards e seus ícones.
  - Card **Bibliografia ID**: usar `public/assets/img/svg/pilha-de-livros.svg` e, ao clicar, abrir o componente `BibliografiaId`.
  - Card **Cronograma**: usar `public/assets/img/svg/calendar.svg` e, ao clicar, abrir o componente `Cronograma`.
  - Card **Estatísticas**: usar `public/assets/img/svg/estatisticas.svg` e, ao clicar, abrir o componente `EstatisticaUser`.
- Para **Bibliografia ID**, carregar `public/assets/bibliografias.json` e converter para uma visualização HTML agrupada por matéria.
- Para **Cronograma**, o HTML de referência está em `src/app/pages/home/home-landing/cronograma/cronograma.html` (garantir que o card navegue para esse componente/rota).
- Para **Estatísticas**, acionar a navegação para a página de estatísticas, seguindo o padrão já usado em `src/app/pages/home/side-menu/side-menu.ts` no método `navigateEstatisticas()` (atualizar `home-landing.component.ts` de forma equivalente).
- Garantir que os 3 cards usem os SVGs indicados no `public/` e que os cliques acionem as rotas/componentes correspondentes.
