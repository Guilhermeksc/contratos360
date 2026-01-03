# Guia de Otimização: Backend Django - API ComprasNet

Este guia detalha o processo completo para otimizar as requisições à API do ComprasNet, implementando carregamento sob demanda (lazy loading) para as abas de Histórico, Empenhos, Itens e Arquivos.

## 📋 Objetivo

Atualmente, durante a sincronização de contratos de uma UASG, o sistema busca automaticamente os dados de histórico, empenhos, itens e arquivos para cada contrato, tornando o processo extremamente lento. O objetivo é:

1. **Sincronizar apenas dados básicos** do contrato durante a sincronização inicial
2. **Carregar dados detalhados sob demanda** quando o usuário selecionar a aba correspondente
3. **Manter todos os dados no PostgreSQL** (sem leitura offline)
4. **Fornecer endpoints individuais** para sincronização de cada aba

## 🎯 Resultado Esperado

- Sincronização inicial de UASG: **muito mais rápida** (apenas dados básicos dos contratos)
- Carregamento de abas: **sob demanda** com loading individualizado
- Logs limpos: sem múltiplas requisições para histórico/empenhos/itens/arquivos durante sincronização inicial

---

## Passo 1: Remover Busca Automática de Dados Detalhados

### 1.1 Modificar `sync_contratos_por_uasg`

**Arquivo:** `backend/django_licitacao360/apps/gestao_contratos/services/ingestion.py`

**Localização:** Método `sync_contratos_por_uasg` (linhas 283-369)

**Ação:** Remover as chamadas para buscar histórico, empenhos, itens e arquivos dentro do loop de processamento de contratos.

**Antes:**
```python
# Dentro do loop (linhas 338-360)
if "historico" in links:
    historico_data = self._fetch_api_data(links["historico"])
    if historico_data:
        self._save_historico(contrato, historico_data)
        stats['historicos'] += len(historico_data)

if "empenhos" in links:
    empenhos_data = self._fetch_api_data(links["empenhos"])
    if empenhos_data:
        self._save_empenhos(contrato, empenhos_data)
        stats['empenhos'] += len(empenhos_data)

if "itens" in links:
    itens_data = self._fetch_api_data(links["itens"])
    if itens_data:
        self._save_itens(contrato, itens_data)
        stats['itens'] += len(itens_data)

if "arquivos" in links:
    arquivos_data = self._fetch_api_data(links["arquivos"])
    if arquivos_data:
        self._save_arquivos(contrato, arquivos_data)
        stats['arquivos'] += len(arquivos_data)
```

**Depois:**
```python
# Remover completamente essas chamadas
# Manter apenas:
contrato = self._save_contrato(contrato_data, uasg_code)
stats['contratos_processados'] += 1
```

**Ajustar retorno de stats:**
```python
# Inicializar stats apenas com contratos_processados
stats = {
    'contratos_processados': 0,
    'historicos': 0,
    'empenhos': 0,
    'itens': 0,
    'arquivos': 0,
}

# Retornar stats com zeros para os demais campos
```

---

## Passo 2: Adicionar Campos de Status no Modelo Contrato

### 2.1 Modificar o Modelo `Contrato`

**Arquivo:** `backend/django_licitacao360/apps/gestao_contratos/models/contrato.py`

**Ação:** Adicionar campos para rastrear quando cada aba foi atualizada pela última vez.

**Adicionar após o campo `raw_json` (linha ~135):**
```python
# Campos de status de sincronização detalhada
historico_atualizado_em = models.DateTimeField(
    null=True,
    blank=True,
    verbose_name="Histórico Atualizado Em",
    help_text="Data/hora da última sincronização do histórico"
)
empenhos_atualizados_em = models.DateTimeField(
    null=True,
    blank=True,
    verbose_name="Empenhos Atualizados Em",
    help_text="Data/hora da última sincronização dos empenhos"
)
itens_atualizados_em = models.DateTimeField(
    null=True,
    blank=True,
    verbose_name="Itens Atualizados Em",
    help_text="Data/hora da última sincronização dos itens"
)
arquivos_atualizados_em = models.DateTimeField(
    null=True,
    blank=True,
    verbose_name="Arquivos Atualizados Em",
    help_text="Data/hora da última sincronização dos arquivos"
)
```

### 2.2 Criar e Aplicar Migration

**Comando:**
```bash
cd backend/django_licitacao360
python manage.py makemigrations gestao_contratos
python manage.py migrate gestao_contratos
```

**Verificar:** A migration deve criar os 4 novos campos no banco de dados.

---

## Passo 3: Atualizar Serializer para Expor Status de Sincronização

### 3.1 Modificar `ContratoDetailSerializer`

**Arquivo:** `backend/django_licitacao360/apps/gestao_contratos/serializers/contrato.py`

**Ação:** Adicionar campos de status de sincronização no serializer.

**Adicionar no método `get_fields` ou diretamente na classe Meta (após linha 81):**
```python
# Adicionar nos fields do Meta
'historico_atualizado_em',
'empenhos_atualizados_em',
'itens_atualizados_em',
'arquivos_atualizados_em',
```

**Ou adicionar como SerializerMethodField:**
```python
historico_atualizado_em = serializers.DateTimeField(read_only=True)
empenhos_atualizados_em = serializers.DateTimeField(read_only=True)
itens_atualizados_em = serializers.DateTimeField(read_only=True)
arquivos_atualizados_em = serializers.DateTimeField(read_only=True)
```

**Adicionar nos fields do Meta:**
```python
fields = [
    # ... campos existentes ...
    'historico_atualizado_em',
    'empenhos_atualizados_em',
    'itens_atualizados_em',
    'arquivos_atualizados_em',
    # ... resto dos campos ...
]
```

---

## Passo 4: Criar Método para Sincronização Individual de Abas

### 4.1 Adicionar Método no Serviço de Ingestão

**Arquivo:** `backend/django_licitacao360/apps/gestao_contratos/services/ingestion.py`

**Ação:** Criar método privado para sincronizar uma única aba de dados.

**Adicionar após o método `sync_contrato_detalhes` (após linha 433):**
```python
def _sync_single_related_dataset(
    self, 
    contrato: Contrato, 
    data_type: str
) -> Dict[str, int]:
    """
    Sincroniza um único tipo de dado relacionado (histórico, empenhos, itens ou arquivos).
    
    Args:
        contrato: Instância do Contrato
        data_type: Tipo de dado ('historico', 'empenhos', 'itens' ou 'arquivos')
    
    Returns:
        Dicionário com estatísticas da sincronização
    """
    from django.utils import timezone
    
    # Validação do tipo de dado
    valid_types = ['historico', 'empenhos', 'itens', 'arquivos']
    if data_type not in valid_types:
        raise ValueError(f"Tipo de dado inválido: {data_type}. Deve ser um de {valid_types}")
    
    # Busca dados atualizados do contrato para obter links atualizados
    url = f"{self.BASE_URL}/contrato/{contrato.id}"
    contrato_data = self._fetch_api_data(url)
    
    if not contrato_data:
        print(f"⚠ Não foi possível obter dados atualizados do contrato {contrato.id}.")
        return {data_type: 0}
    
    # Se retornou lista, pega o primeiro item
    if isinstance(contrato_data, list) and contrato_data:
        contrato_data = contrato_data[0]
    
    links = contrato_data.get("links", {})
    link_key = data_type
    
    if link_key not in links:
        print(f"⚠ Link para {data_type} não encontrado no contrato {contrato.id}.")
        return {data_type: 0}
    
    # Busca e salva dados
    data = self._fetch_api_data(links[link_key])
    count = 0
    
    if data:
        # Mapeia tipo de dado para método de salvamento
        save_methods = {
            'historico': (self._save_historico, 'historico_atualizado_em'),
            'empenhos': (self._save_empenhos, 'empenhos_atualizados_em'),
            'itens': (self._save_itens, 'itens_atualizados_em'),
            'arquivos': (self._save_arquivos, 'arquivos_atualizados_em'),
        }
        
        save_method, field_name = save_methods[data_type]
        save_method(contrato, data)
        count = len(data)
        
        # Atualiza timestamp de sincronização
        setattr(contrato, field_name, timezone.now())
        contrato.save(update_fields=[field_name])
        
        print(f"✅ {data_type.capitalize()} do contrato {contrato.id} sincronizado: {count} registros")
    
    return {data_type: count}
```

### 4.2 Atualizar `sync_contrato_detalhes` para Aceitar Tipos Específicos

**Arquivo:** `backend/django_licitacao360/apps/gestao_contratos/services/ingestion.py`

**Ação:** Modificar método para aceitar lista opcional de tipos de dados.

**Modificar assinatura do método (linha 371):**
```python
def sync_contrato_detalhes(
    self, 
    contrato_id: str,
    data_types: Optional[List[str]] = None
) -> Dict[str, int]:
    """
    Sincroniza detalhes de um contrato específico.
    
    Args:
        contrato_id: ID do contrato
        data_types: Lista opcional de tipos de dados a sincronizar.
                   Se None, sincroniza todos ('historico', 'empenhos', 'itens', 'arquivos').
                   Valores válidos: 'historico', 'empenhos', 'itens', 'arquivos'
    
    Returns:
        Dicionário com estatísticas da sincronização
    """
```

**Modificar corpo do método:**
```python
try:
    contrato = Contrato.objects.get(id=contrato_id)
except Contrato.DoesNotExist:
    print(f"⚠ Contrato {contrato_id} não encontrado.")
    return {'historicos': 0, 'empenhos': 0, 'itens': 0, 'arquivos': 0}

# Se não especificado, sincroniza todos
if data_types is None:
    data_types = ['historico', 'empenhos', 'itens', 'arquivos']

stats = {
    'historicos': 0,
    'empenhos': 0,
    'itens': 0,
    'arquivos': 0,
}

# Sincroniza cada tipo solicitado
for data_type in data_types:
    if data_type in ['historico', 'empenhos', 'itens', 'arquivos']:
        result = self._sync_single_related_dataset(contrato, data_type)
        stats.update(result)

print(f"✅ Detalhes do contrato {contrato_id} sincronizados: {stats}")
return stats
```

---

## Passo 5: Criar Endpoints Individuais no ViewSet

### 5.1 Adicionar Ações no `ContratoViewSet`

**Arquivo:** `backend/django_licitacao360/apps/gestao_contratos/views/contrato_views.py`

**Ação:** Adicionar ações customizadas para sincronizar cada aba individualmente.

**Adicionar após o método `detalhes` (após linha 206):**
```python
@action(
    detail=True, 
    methods=['post'], 
    url_path='sincronizar/historico',
    permission_classes=[AllowAny]
)
def sincronizar_historico(self, request, pk=None):
    """Sincroniza histórico de um contrato específico"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        contrato = self.get_object()
        service = ComprasNetIngestionService()
        result = service._sync_single_related_dataset(contrato, 'historico')
        
        logger.info(f'Histórico do contrato {pk} sincronizado: {result}')
        response = Response({
            'success': True,
            'contrato_id': pk,
            'stats': result,
            'message': 'Histórico sincronizado com sucesso'
        })
        response['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as e:
        import traceback
        logger.error(f'Erro ao sincronizar histórico do contrato {pk}: {str(e)}')
        response = Response(
            {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc() if request.query_params.get('debug') == 'true' else None
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        response['Access-Control-Allow-Origin'] = '*'
        return response

@action(
    detail=True, 
    methods=['post'], 
    url_path='sincronizar/empenhos',
    permission_classes=[AllowAny]
)
def sincronizar_empenhos(self, request, pk=None):
    """Sincroniza empenhos de um contrato específico"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        contrato = self.get_object()
        service = ComprasNetIngestionService()
        result = service._sync_single_related_dataset(contrato, 'empenhos')
        
        logger.info(f'Empenhos do contrato {pk} sincronizados: {result}')
        response = Response({
            'success': True,
            'contrato_id': pk,
            'stats': result,
            'message': 'Empenhos sincronizados com sucesso'
        })
        response['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as e:
        import traceback
        logger.error(f'Erro ao sincronizar empenhos do contrato {pk}: {str(e)}')
        response = Response(
            {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc() if request.query_params.get('debug') == 'true' else None
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        response['Access-Control-Allow-Origin'] = '*'
        return response

@action(
    detail=True, 
    methods=['post'], 
    url_path='sincronizar/itens',
    permission_classes=[AllowAny]
)
def sincronizar_itens(self, request, pk=None):
    """Sincroniza itens de um contrato específico"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        contrato = self.get_object()
        service = ComprasNetIngestionService()
        result = service._sync_single_related_dataset(contrato, 'itens')
        
        logger.info(f'Itens do contrato {pk} sincronizados: {result}')
        response = Response({
            'success': True,
            'contrato_id': pk,
            'stats': result,
            'message': 'Itens sincronizados com sucesso'
        })
        response['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as e:
        import traceback
        logger.error(f'Erro ao sincronizar itens do contrato {pk}: {str(e)}')
        response = Response(
            {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc() if request.query_params.get('debug') == 'true' else None
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        response['Access-Control-Allow-Origin'] = '*'
        return response

@action(
    detail=True, 
    methods=['post'], 
    url_path='sincronizar/arquivos',
    permission_classes=[AllowAny]
)
def sincronizar_arquivos(self, request, pk=None):
    """Sincroniza arquivos de um contrato específico"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        contrato = self.get_object()
        service = ComprasNetIngestionService()
        result = service._sync_single_related_dataset(contrato, 'arquivos')
        
        logger.info(f'Arquivos do contrato {pk} sincronizados: {result}')
        response = Response({
            'success': True,
            'contrato_id': pk,
            'stats': result,
            'message': 'Arquivos sincronizados com sucesso'
        })
        response['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as e:
        import traceback
        logger.error(f'Erro ao sincronizar arquivos do contrato {pk}: {str(e)}')
        response = Response(
            {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc() if request.query_params.get('debug') == 'true' else None
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        response['Access-Control-Allow-Origin'] = '*'
        return response
```

---

## Passo 6: Endpoints de Leitura (Já Existem)

### 6.1 Verificar Endpoints de Leitura

Os endpoints de leitura já estão implementados e registrados:

- `GET /api/contratos/historico/?contrato=<id>` - Lista histórico de um contrato
- `GET /api/contratos/empenhos/?contrato=<id>` - Lista empenhos de um contrato
- `GET /api/contratos/itens/?contrato=<id>` - Lista itens de um contrato
- `GET /api/contratos/arquivos/?contrato=<id>` - Lista arquivos de um contrato

**Nenhuma alteração necessária** - esses endpoints já servem dados do PostgreSQL.

---

## Passo 7: Fluxo de Uso no Frontend

### 7.1 Fluxo Recomendado

1. **Sincronização Inicial:**
   - Frontend chama `POST /api/contratos/sync/?uasg=<codigo>`
   - Backend sincroniza apenas dados básicos dos contratos
   - Resposta rápida sem buscar histórico/empenhos/itens/arquivos

2. **Ao Selecionar Aba:**
   - Frontend verifica se a aba já foi sincronizada (usando campos `*_atualizado_em` do `ContratoDetailSerializer`)
   - Se não sincronizada ou desatualizada:
     - Chama `POST /api/contratos/<id>/sincronizar/<aba>/` (ex: `sincronizar/historico`)
     - Exibe loading durante a sincronização
     - Após sucesso, chama `GET /api/contratos/<aba>/?contrato=<id>` para obter dados
   - Se já sincronizada:
     - Chama diretamente `GET /api/contratos/<aba>/?contrato=<id>`

### 7.2 Exemplo de Endpoints

**Sincronização de Histórico:**
```
POST /api/contratos/527331/sincronizar/historico/
```

**Leitura de Histórico:**
```
GET /api/contratos/historico/?contrato=527331
```

**Sincronização de Empenhos:**
```
POST /api/contratos/527331/sincronizar/empenhos/
```

**Leitura de Empenhos:**
```
GET /api/contratos/empenhos/?contrato=527331
```

---

## Passo 8: Validação e Testes

### 8.1 Testar Sincronização Inicial

```bash
# Executar sincronização de uma UASG
python manage.py sync_comprasnet --uasg 787010

# Verificar logs - NÃO deve aparecer:
# - Buscando dados em .../historico
# - Buscando dados em .../empenhos
# - Buscando dados em .../itens
# - Buscando dados em .../arquivos

# Deve aparecer apenas:
# Processando contrato X/Y: ...
#   Criado/Atualizado contrato ...
```

### 8.2 Testar Sincronização Individual

```bash
# Via API (usando curl ou Postman)
curl -X POST http://localhost:8000/api/contratos/527331/sincronizar/historico/

# Verificar resposta
{
  "success": true,
  "contrato_id": "527331",
  "stats": {"historico": 3},
  "message": "Histórico sincronizado com sucesso"
}

# Verificar dados salvos
curl http://localhost:8000/api/contratos/historico/?contrato=527331
```

### 8.3 Verificar Campos de Status

```bash
# Verificar se campos foram criados
python manage.py shell
>>> from apps.gestao_contratos.models import Contrato
>>> c = Contrato.objects.first()
>>> print(c.historico_atualizado_em)
>>> print(c.empenhos_atualizados_em)
```

---

## Passo 9: Logs e Monitoramento

### 9.1 Adicionar Logs Detalhados

**Arquivo:** `backend/django_licitacao360/apps/gestao_contratos/services/ingestion.py`

**No método `_sync_single_related_dataset`, adicionar logs:**
```python
print(f"🔄 Sincronizando {data_type} do contrato {contrato.id}...")
# ... código de sincronização ...
print(f"✅ {data_type.capitalize()} do contrato {contrato.id} sincronizado: {count} registros")
```

### 9.2 Logs Esperados Após Otimização

**Durante sincronização inicial:**
```
Processando contrato 1/29: 00001/2025
  Criado contrato 00001/2025
Processando contrato 2/29: 00002/2025
  Atualizado contrato 00002/2025
...
✅ Sincronização da UASG 787010 concluída: {'contratos_processados': 29, 'historicos': 0, 'empenhos': 0, 'itens': 0, 'arquivos': 0}
```

**Durante sincronização individual:**
```
🔄 Sincronizando historico do contrato 527331...
 - Buscando dados em https://contratos.comprasnet.gov.br/api/contrato/527331/historico (Tentativa 1/3)
✅ Historico do contrato 527331 sincronizado: 3 registros
```

---

## 📝 Resumo das Alterações

### Arquivos Modificados:

1. **`services/ingestion.py`**
   - Remover busca automática de histórico/empenhos/itens/arquivos em `sync_contratos_por_uasg`
   - Adicionar método `_sync_single_related_dataset`
   - Modificar `sync_contrato_detalhes` para aceitar tipos específicos

2. **`models/contrato.py`**
   - Adicionar 4 campos de timestamp: `historico_atualizado_em`, `empenhos_atualizados_em`, `itens_atualizados_em`, `arquivos_atualizados_em`

3. **`serializers/contrato.py`**
   - Adicionar campos de timestamp no `ContratoDetailSerializer`

4. **`views/contrato_views.py`**
   - Adicionar 4 ações: `sincronizar_historico`, `sincronizar_empenhos`, `sincronizar_itens`, `sincronizar_arquivos`

### Arquivos Não Modificados (mas importantes):

- `views/offline_views.py` - Endpoints de leitura já existem e funcionam
- `urls.py` - Rotas já estão registradas
- `serializers/offline.py` - Serializers já existem

### Migrations:

- Criar e aplicar migration para os novos campos de timestamp

---

## ✅ Checklist de Implementação

- [ ] Passo 1: Remover busca automática em `sync_contratos_por_uasg`
- [ ] Passo 2: Adicionar campos de status no modelo `Contrato`
- [ ] Passo 3: Criar e aplicar migration
- [ ] Passo 4: Atualizar serializer para expor campos de status
- [ ] Passo 5: Criar método `_sync_single_related_dataset`
- [ ] Passo 6: Atualizar `sync_contrato_detalhes` para aceitar tipos específicos
- [ ] Passo 7: Adicionar ações no `ContratoViewSet` (4 endpoints)
- [ ] Passo 8: Testar sincronização inicial (deve ser rápida)
- [ ] Passo 9: Testar sincronização individual de cada aba
- [ ] Passo 10: Verificar logs (sem requisições extras durante sync inicial)
- [ ] Passo 11: Atualizar frontend para usar novos endpoints

---

## 🚀 Benefícios Esperados

1. **Performance:** Sincronização inicial 4-5x mais rápida (elimina 4 requisições por contrato)
2. **UX:** Carregamento sob demanda com feedback visual (loading)
3. **Escalabilidade:** Menor carga na API do ComprasNet
4. **Flexibilidade:** Usuário controla quando atualizar cada aba
5. **Rastreabilidade:** Campos de timestamp permitem saber quando cada aba foi atualizada

---

## 📚 Referências

- Documentação Django REST Framework: https://www.django-rest-framework.org/api-guide/viewsets/#marking-extra-actions-for-routing
- Documentação Django Models: https://docs.djangoproject.com/en/stable/topics/db/models/
- API ComprasNet: https://contratos.comprasnet.gov.br/api/

---

**Última atualização:** 2025-01-XX  
**Versão:** 1.0


