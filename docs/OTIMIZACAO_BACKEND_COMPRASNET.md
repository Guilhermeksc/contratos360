# Otimizando o backend Django para requisições ComprasNet

Este guia descreve, passo a passo, como tornar a sincronização com a API do ComprasNet mais leve e adequada ao novo fluxo de carregamento sob demanda das abas (Histórico, Empenhos, Itens e Arquivos). Toda a lógica permanece usando o PostgreSQL do Django — não há leitura de bases offline fora do ORM.

## 1. Isolar a sincronização básica de contratos
1. Abra `backend/django_licitacao360/apps/gestao_contratos/services/ingestion.py:318-364` e remova as chamadas para os links `historico`, `empenhos`, `itens` e `arquivos` dentro de `sync_contratos_por_uasg`.  
2. Mantenha apenas a persistência do modelo `Contrato` (método `_save_contrato`) e o filtro de vigência `_filter_contracts_by_vigency`.  
3. Atualize o objeto `stats` retornado para contar apenas contratos sincronizados; os demais contadores devem voltar zerados até que uma sincronização detalhada seja solicitada.

> Resultado: o comando `python manage.py sync_comprasnet --uasg <codigo>` passa a baixar apenas os dados imprescindíveis para listar contratos, eliminando as quatro chamadas extras por contrato.

## 2. Registrar status da última sincronização detalhada
1. No modelo `Contrato` (`backend/django_licitacao360/apps/gestao_contratos/models/contrato.py`) adicione campos como `detalhes_atualizados_em` (DateTimeField) e flags booleanas (`historico_atualizado`, etc.) para sabermos se cada aba já foi populada.  
2. Gere e aplique uma migration (`python manage.py makemigrations gestao_contratos && python manage.py migrate gestao_contratos`).  
3. Atualize o serializer `ContratoDetailSerializer` (`serializers/contrato.py:30-116`) para expor esses metadados; o frontend poderá exibir “Atualizar” ou “Carregar” conforme necessário.

## 3. Criar endpoints por aba com carregamento sob demanda
1. No `ContratoViewSet` (`views/contrato_views.py:153-210`) acrescente ações específicas:
   - `@action(detail=True, methods=['post'], url_path='sincronizar/historico')`
   - `@action(detail=True, methods=['post'], url_path='sincronizar/empenhos')`  
   (repita para itens e arquivos).
2. Cada ação deve chamar um novo método no serviço (`ComprasNetIngestionService`) que aceite o contrato e o tipo de dado desejado, buscando o link certo e salvando somente aquela tabela. Atualize também `sync_contrato_detalhes` para tornar `data_types` parametrizável.
3. Retorne imediatamente o serializer correspondente (`HistoricoContratoSerializer`, etc.), permitindo que o frontend mostre um loading enquanto aguarda a resposta e renderize a aba assim que os registros chegarem.

## 4. Implementar o fetch específico no serviço de ingestão
1. Em `services/ingestion.py` crie um método privado, por exemplo `_sync_single_related_dataset(self, contrato, data_type)`, que:
   - Busca o contrato mais recente na API (`/api/contrato/{id}`) para obter o link atualizado.
   - Usa `_fetch_api_data` somente para o `data_type` solicitado.
   - Persiste via `_save_historico`, `_save_empenhos`, etc. e atualiza os campos de status criados no Passo 2.
2. Use este método nas novas ações da view e também exponha-o via `sync_contrato_detalhes` (mantendo a possibilidade de sincronizar todas as abas de uma vez quando necessário).

## 5. Reutilizar as viewsets existentes de leitura
1. As rotas já registradas em `backend/django_licitacao360/apps/gestao_contratos/urls.py` (`/api/contratos/historico/`, `/empenhos/`, `/itens/`, `/arquivos/`) devem permanecer servindo dados exclusivamente do banco.  
2. Depois que o frontend dispara `POST /api/contratos/<id>/sincronizar/<aba>/`, ele deve consultar o respectivo endpoint de leitura passando `?contrato=<id>` para montar a aba; nenhuma lógica acessa bases locais.

## 6. Ajustar o frontend para chamadas individuais
1. Ao trocar de aba, chamar o endpoint de sincronização correspondente e exibir um spinner até a resposta.  
2. Assim que o backend confirmar a atualização, requisitar os dados já persistidos usando os viewsets de leitura.  
3. Opcionalmente armazenar em memória o timestamp/flag devolvido para não repetir uma sincronização caso o usuário volte para a aba na mesma sessão.

## 7. Monitorar e validar
1. Adicione logs claros ao serviço (`print` ou `logger.info`) indicando quando uma aba é sincronizada sob demanda; isso facilita auditar o carregamento lazy.  
2. Garanta testes unitários para `_sync_single_related_dataset` cobrindo cenários de falha de rede e dados vazios.  
3. Execute `pytest` ou os testes existentes antes do deploy e valide manualmente que o comando `sync_comprasnet` ficou significativamente mais rápido (logs semelhantes ao trecho fornecido não devem mais aparecer).

Seguindo esses passos, o backend mantém apenas os dados mínimos atualizados durante a sincronização de uma UASG e disponibiliza loaders individuais para cada aba, atendendo ao requisito de buscar dados somente quando o usuário solicitar e sempre a partir do banco de dados do Django.
