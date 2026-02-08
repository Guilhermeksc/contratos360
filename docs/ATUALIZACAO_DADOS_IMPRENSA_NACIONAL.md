# Documentação: Atualização de Dados da Imprensa Nacional (INLABS)

## Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Componentes Principais](#componentes-principais)
4. [Fluxo de Atualização](#fluxo-de-atualização)
5. [Configuração](#configuração)
6. [Execução Manual](#execução-manual)
7. [Execução Automática (Celery Beat)](#execução-automática-celery-beat)
8. [API REST](#api-rest)
9. [Modelo de Dados](#modelo-de-dados)
10. [Troubleshooting](#troubleshooting)

---

## Visão Geral

O sistema de atualização de dados da Imprensa Nacional é responsável por coletar automaticamente artigos publicados no Diário Oficial da União (DOU) através do portal INLABS (Imprensa Nacional - Laboratório de Automação e Segurança). 

O sistema filtra especificamente artigos relacionados ao **Comando da Marinha** e armazena essas informações no banco de dados para posterior consulta e análise.

### Características Principais

- **Coleta Automática**: Execução agendada via Celery Beat
- **Filtragem Inteligente**: Busca artigos por palavra-chave na categoria
- **Lock Distribuído**: Previne execuções simultâneas da mesma data
- **Retry Automático**: Sistema de tentativas com backoff exponencial
- **API REST**: Endpoints para consulta dos dados coletados

---

## Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    Celery Beat Scheduler                    │
│              (Agendamento Periódico - 8h e 10h)            │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Task: collect_inlabs_articles                   │
│              (tasks.py - Lock Distribuído)                  │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│         Service: ingest_inlabs_articles                     │
│         (services/inlabs_downloader.py)                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Download   │ │  Extraction  │ │  Persistence │
│   (Selenium) │ │   (XML/ZIP)  │ │   (Django)   │
└──────────────┘ └──────────────┘ └──────────────┘
        │               │               │
        └───────────────┼───────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Model: InlabsArticle                           │
│              (models.py - PostgreSQL)                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Componentes Principais

### 1. **tasks.py** - Tarefas Celery

Localização: `apps/imprensa_nacional/tasks.py`

**Função Principal**: `collect_inlabs_articles`

- Task Celery compartilhada (`@shared_task`)
- Implementa lock distribuído usando Redis para evitar execuções simultâneas
- Retry automático com backoff de 120 segundos (máximo 3 tentativas)
- Gerencia transações de banco de dados

**Características**:
- Lock distribuído com timeout de 1 hora
- Logging detalhado de todas as operações
- Tratamento de erros robusto
- Fechamento garantido de conexões de banco

### 2. **inlabs_downloader.py** - Serviço de Download

Localização: `apps/imprensa_nacional/services/inlabs_downloader.py`

**Função Principal**: `ingest_inlabs_articles`

Este serviço é o núcleo do sistema de coleta, responsável por:

1. **Download do Arquivo ZIP**
   - Autenticação no portal INLABS usando Selenium
   - Download do arquivo ZIP da edição do DOU
   - Retry automático em caso de falha

2. **Extração e Processamento**
   - Extração do arquivo ZIP
   - Leitura de arquivos XML
   - Filtragem de artigos por palavra-chave

3. **Persistência**
   - Salvamento no banco de dados usando `update_or_create`
   - Mapeamento de campos XML para modelo Django
   - Transações atômicas

**Classes e Funções Principais**:

- `InlabsDownloadConfig`: Configuração do download
- `InlabsDownloadError`: Exceção customizada
- `fetch_inlabs_articles()`: Baixa e processa artigos
- `persist_inlabs_articles()`: Salva no banco de dados
- `ingest_inlabs_articles()`: Função principal que orquestra o processo

### 3. **models.py** - Modelo de Dados

Localização: `apps/imprensa_nacional/models.py`

**Modelo**: `InlabsArticle`

Armazena todas as informações dos artigos coletados, incluindo:

- Identificadores: `article_id`, `edition_date`
- Metadados: `name`, `pub_name`, `art_type`, `art_category`
- Conteúdo: `body_html`, `art_notes`
- Dados brutos: `raw_payload` (JSON)
- Métodos auxiliares: `extract_uasg()`, `extract_om_name()`, `extract_objeto()`

**Constraints**:
- `unique_together`: (`article_id`, `edition_date`)
- Índice em `edition_date` para consultas rápidas

### 4. **import_inlabs.py** - Comando de Importação Manual

Localização: `apps/imprensa_nacional/management/commands/import_inlabs.py`

Comando Django para execução manual da importação:

```bash
python manage.py import_inlabs --date 2026-01-05
```

### 5. **sync_celery_beat.py** - Sincronização de Tarefas

Localização: `apps/imprensa_nacional/management/commands/sync_celery_beat.py`

Comando para sincronizar tarefas periódicas do `CELERY_BEAT_SCHEDULE` para o banco de dados:

```bash
python manage.py sync_celery_beat
```

**Funcionalidades**:
- Cria tarefas periódicas no banco
- Atualiza tarefas existentes
- Desabilita tarefas removidas do schedule

### 6. **views.py** - API REST

Localização: `apps/imprensa_nacional/views.py`

**ViewSet**: `InlabsArticleViewSet`

- ViewSet somente leitura (`ReadOnlyModelViewSet`)
- Filtros: `edition_date`, `article_id`, `pub_name`, `art_type`
- Busca: `name`, `art_category`, `art_notes`, `body_html`
- Ordenação: `edition_date`, `article_id`, `pub_name`, `created_at`

### 7. **urls.py** - Rotas da API

Localização: `apps/imprensa_nacional/urls.py`

Registra o router REST com o endpoint:
- `/api/imprensa-nacional/articles/`

---

## Fluxo de Atualização

### Fluxo Automático (Celery Beat)

```
1. Celery Beat verifica agendamento (8h e 10h)
   ↓
2. Dispara task collect_inlabs_articles()
   ↓
3. Task adquire lock distribuído no Redis
   ↓
4. Se lock adquirido:
   ├─ Chama ingest_inlabs_articles()
   ├─ Verifica disponibilidade do arquivo
   ├─ Autentica no INLABS (Selenium)
   ├─ Baixa arquivo ZIP
   ├─ Extrai e processa XMLs
   ├─ Filtra artigos por palavra-chave
   ├─ Salva no banco de dados
   └─ Remove lock
   ↓
5. Se lock não adquirido:
   └─ Loga aviso e retorna (skip)
```

### Fluxo Manual (Comando Django)

```
1. Usuário executa: python manage.py import_inlabs --date YYYY-MM-DD
   ↓
2. Comando chama diretamente ingest_inlabs_articles()
   ↓
3. Mesmo processo de download e persistência
   ↓
4. Retorna resultado no console
```

---

## Configuração

### Variáveis de Ambiente

As seguintes variáveis devem estar configuradas no `.env`:

```bash
# Credenciais INLABS
INLABS_EMAIL=seu_email@exemplo.com
INLABS_PASSWORD=sua_senha

# Configurações opcionais
INLABS_SECTION=DO3                    # Seção do DOU (padrão: DO3)
INLABS_ARTCATEGORY_KEYWORD=Comando da Marinha  # Palavra-chave para filtro
INLABS_DOWNLOAD_ROOT=/app/tmp/inlabs  # Diretório de download
INLABS_DOWNLOAD_ATTEMPTS=3            # Tentativas de download
INLABS_DOWNLOAD_TIMEOUT=60            # Timeout em segundos
INLABS_DOWNLOAD_RETRY_DELAY=5         # Delay entre tentativas (segundos)

# Chrome/Chromium
CHROME_BIN=/usr/bin/chromium          # Caminho do Chromium

# Redis (para lock distribuído)
CELERY_BROKER_URL=redis://redis:6379/0
```

### Configuração no Django Settings

No arquivo `settings.py`, as seguintes configurações são relevantes:

```python
# Celery Beat Schedule
CELERY_BEAT_SCHEDULE = {
    "coletar_inlabs_08": {
        "task": "django_licitacao360.apps.imprensa_nacional.tasks.collect_inlabs_articles",
        "schedule": crontab(hour=8, minute=0),  # Diariamente às 8:00
    },
    "coletar_inlabs_10": {
        "task": "django_licitacao360.apps.imprensa_nacional.tasks.collect_inlabs_articles",
        "schedule": crontab(hour=10, minute=0),  # Diariamente às 10:00
    },
}

# Timezone
CELERY_TIMEZONE = "America/Sao_Paulo"
```

### Sincronização Inicial

Após configurar o `CELERY_BEAT_SCHEDULE`, execute:

```bash
python manage.py sync_celery_beat
```

Isso criará/atualizará as tarefas periódicas no banco de dados.

---

## Execução Manual

### Importação de uma Data Específica

```bash
# Importar data específica
python manage.py import_inlabs --date 2026-01-05

# Importar data atual (hoje)
python manage.py import_inlabs
```

### Execução via Task Celery (Manual)

```python
from django_licitacao360.apps.imprensa_nacional.tasks import collect_inlabs_articles

# Executar para data específica
result = collect_inlabs_articles.delay("2026-01-05")

# Executar para data atual
result = collect_inlabs_articles.delay()
```

### Execução Direta do Serviço

```python
from datetime import date
from django_licitacao360.apps.imprensa_nacional.services.inlabs_downloader import ingest_inlabs_articles

# Importar data específica
result = ingest_inlabs_articles(date(2026, 1, 5))

# Resultado:
# {
#     "edition_date": "2026-01-05",
#     "downloaded_file": "/path/to/file.zip",
#     "saved_articles": 42
# }
```

### Importação em Lote (Múltiplas Datas)

Para importar múltiplas datas de uma vez, use o comando `import_inlabs_batch`:

#### Importar Intervalo de Datas

```bash
# Importar todas as datas de 2025-10-09 até 2026-02-07
docker compose exec backend python manage.py import_inlabs_batch \
    --start-date 2025-10-09 \
    --end-date 2026-02-07

# Com delay personalizado entre importações (padrão: 2 segundos)
docker compose exec backend python manage.py import_inlabs_batch \
    --start-date 2025-10-09 \
    --end-date 2026-02-07 \
    --delay 5
```

#### Importar Lista Específica de Datas

```bash
# Importar apenas datas específicas
docker compose exec backend python manage.py import_inlabs_batch \
    --dates 2025-10-09 2025-10-10 2025-10-11 2026-02-06 2026-02-07
```

#### Opções Avançadas

```bash
# Pular datas que já possuem artigos no banco
docker compose exec backend python manage.py import_inlabs_batch \
    --start-date 2025-10-09 \
    --end-date 2026-02-07 \
    --skip-existing

# Continuar mesmo quando ocorrer erro em uma data
docker compose exec backend python manage.py import_inlabs_batch \
    --start-date 2025-10-09 \
    --end-date 2026-02-07 \
    --continue-on-error \
    --delay 3
```

#### Script Shell Alternativo

Também está disponível um script shell para uso direto:

```bash
# Usar o script shell
cd backend/django_licitacao360/apps/imprensa_nacional/scripts
./import_batch.sh 2025-10-09 2026-02-07 2

# Ou via docker compose
docker compose exec backend bash -c \
    "cd django_licitacao360/apps/imprensa_nacional/scripts && ./import_batch.sh 2025-10-09 2026-02-07 2"
```

**Parâmetros do comando `import_inlabs_batch`**:

- `--start-date`: Data inicial do intervalo (YYYY-MM-DD) - **obrigatório** (exceto quando usar `--dates`)
- `--end-date`: Data final do intervalo (YYYY-MM-DD) - opcional (usa data atual se omitido)
- `--dates`: Lista específica de datas para importar (sobrescreve start-date/end-date)
- `--skip-existing`: Pula datas que já possuem artigos no banco
- `--delay`: Delay em segundos entre cada importação (padrão: 2)
- `--continue-on-error`: Continua importação mesmo quando ocorre erro

**Exemplo de Saída**:

```
Iniciando importação em lote: 122 datas
Intervalo: 2025-10-09 até 2026-02-07

[1/122] Processando 2025-10-09...
✅ 2025-10-09: 15 artigos salvos

[2/122] Processando 2025-10-10...
⚠️  2025-10-10: Arquivo não disponível (pulando)

...

============================================================
RESUMO DA IMPORTAÇÃO EM LOTE
============================================================
Total de datas processadas: 122
✅ Sucessos: 95
⚠️  Puladas (arquivo não disponível): 20
❌ Erros: 7
📊 Total de artigos salvos: 1420
```

---

## Execução Automática (Celery Beat)

### Configuração do Celery Beat

O Celery Beat está configurado para executar a coleta automaticamente:

- **8:00 BRT/BRST**: Primeira execução diária
- **10:00 BRT/BRST**: Segunda execução diária (backup)

### Verificação do Status

```bash
# Verificar tarefas periódicas no banco
python manage.py shell
```

```python
from django_celery_beat.models import PeriodicTask

# Listar tarefas INLABS
tasks = PeriodicTask.objects.filter(name__startswith="coletar_inlabs")
for task in tasks:
    print(f"{task.name}: enabled={task.enabled}, schedule={task.crontab}")
```

### Logs

Os logs são registrados no logger `imprensa_nacional.tasks` e `imprensa_nacional.services.inlabs_downloader`.

Exemplo de log de sucesso:
```
INFO: Iniciando coleta INLABS para 2026-01-05
INFO: Coleta INLABS finalizada. data=2026-01-05 artigos=42
```

Exemplo de log de lock:
```
WARNING: Coleta INLABS já em execução para 2026-01-05. Ignorando execução duplicada.
```

---

## API REST

### Endpoint Base

```
GET /api/imprensa-nacional/articles/
```

### Filtros Disponíveis

```
GET /api/imprensa-nacional/articles/?edition_date=2026-01-05
GET /api/imprensa-nacional/articles/?article_id=12345
GET /api/imprensa-nacional/articles/?pub_name=DO3
GET /api/imprensa-nacional/articles/?art_type=Aviso de Licitação-Pregão
```

### Busca (Search)

```
GET /api/imprensa-nacional/articles/?search=Comando da Marinha
```

Busca nos campos: `name`, `art_category`, `art_notes`, `body_html`

### Ordenação

```
GET /api/imprensa-nacional/articles/?ordering=-edition_date
GET /api/imprensa-nacional/articles/?ordering=article_id
```

### Exemplo de Resposta

```json
{
    "count": 42,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "article_id": "12345",
            "edition_date": "2026-01-05",
            "name": "Aviso de Licitação",
            "art_category": "Comando da Marinha / OM XYZ",
            "art_type": "Aviso de Licitação-Pregão",
            "body_html": "<body>...</body>",
            "created_at": "2026-01-05T08:15:00Z",
            "updated_at": "2026-01-05T08:15:00Z"
        }
    ]
}
```

### Detalhes de um Artigo

```
GET /api/imprensa-nacional/articles/{id}/
```

---

## Modelo de Dados

### InlabsArticle

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | AutoField | Chave primária |
| `article_id` | CharField(64) | ID do artigo no INLABS |
| `edition_date` | DateField | Data da edição (indexado) |
| `name` | CharField(255) | Nome/título do artigo |
| `id_oficio` | CharField(100) | ID do ofício |
| `pub_name` | CharField(100) | Nome da publicação |
| `art_type` | CharField(100) | Tipo do artigo |
| `pub_date` | CharField(32) | Data de publicação |
| `art_class` | CharField(255) | Classificação do artigo |
| `art_category` | CharField(255) | Categoria (ex: "Comando da Marinha / OM") |
| `art_notes` | TextField | Notas do artigo |
| `pdf_page` | CharField(255) | Página no PDF |
| `edition_number` | CharField(32) | Número da edição |
| `highlight_type` | CharField(64) | Tipo de destaque |
| `highlight_priority` | CharField(64) | Prioridade do destaque |
| `highlight` | TextField | Texto de destaque |
| `highlight_image` | CharField(255) | Imagem de destaque |
| `highlight_image_name` | CharField(255) | Nome da imagem |
| `materia_id` | CharField(64) | ID da matéria |
| `body_html` | TextField | Conteúdo HTML do artigo |
| `source_filename` | CharField(255) | Nome do arquivo XML origem |
| `source_zip` | CharField(255) | Nome do arquivo ZIP origem |
| `raw_payload` | JSONField | Dados brutos do XML |
| `created_at` | DateTimeField | Data de criação |
| `updated_at` | DateTimeField | Data de atualização |

### Métodos Auxiliares

#### `extract_uasg() -> str | None`

Extrai o número UASG do conteúdo HTML do artigo.

```python
article = InlabsArticle.objects.get(id=1)
uasg = article.extract_uasg()  # Retorna "123456" ou None
```

#### `extract_om_name() -> str | None`

Extrai o nome da Organização Militar (OM) do campo `art_category`.

```python
om_name = article.extract_om_name()  # Retorna "OM XYZ" ou None
```

#### `extract_objeto() -> str | None`

Extrai o objeto da licitação (quando `art_type` é "Aviso de Licitação-Pregão").

```python
objeto = article.extract_objeto()  # Retorna texto do objeto ou None
```

### Constraints e Índices

- **Unique Together**: (`article_id`, `edition_date`)
- **Índice**: `edition_date` (para consultas rápidas por data)
- **Ordenação Padrão**: `-edition_date`, `article_id`

---

## Troubleshooting

### Problema: Lock não é liberado

**Sintoma**: Task não executa porque o lock está ativo.

**Solução**:
```python
# Conectar ao Redis e remover lock manualmente
import redis
from urllib.parse import urlparse
from django.conf import settings

broker_url = settings.CELERY_BROKER_URL
parsed = urlparse(broker_url)
redis_client = redis.Redis(
    host=parsed.hostname or "redis",
    port=parsed.port or 6379,
    db=2,
    decode_responses=True,
)

# Remover lock de uma data específica
lock_key = "inlabs:lock:2026-01-05"
redis_client.delete(lock_key)
```

### Problema: Credenciais inválidas

**Sintoma**: Erro de autenticação no INLABS.

**Solução**:
1. Verificar variáveis `INLABS_EMAIL` e `INLABS_PASSWORD`
2. Testar login manual no portal INLABS
3. Verificar se há CAPTCHA (pode exigir intervenção manual)

### Problema: Download falha repetidamente

**Sintoma**: Timeout ou arquivo não encontrado.

**Soluções**:
1. Verificar se a edição está disponível no portal INLABS
2. Aumentar `INLABS_DOWNLOAD_TIMEOUT`
3. Verificar conectividade de rede
4. Verificar logs do Selenium para erros específicos

### Problema: Nenhum artigo encontrado

**Sintoma**: Download bem-sucedido mas `saved_articles = 0`.

**Possíveis Causas**:
1. Palavra-chave não encontrada nos artigos
2. Formato do XML mudou
3. Filtro muito restritivo

**Solução**:
```python
# Verificar artigos coletados antes da filtragem
from django_licitacao360.apps.imprensa_nacional.services.inlabs_downloader import (
    fetch_inlabs_articles,
    InlabsDownloadConfig
)
from datetime import date

config = InlabsDownloadConfig(target_date=date(2026, 1, 5))
zip_path, articles = fetch_inlabs_articles(config)
print(f"Total de artigos coletados: {len(articles)}")
```

### Problema: Task não executa no horário agendado

**Sintoma**: Celery Beat não dispara a task.

**Verificações**:
1. Verificar se Celery Beat está rodando:
   ```bash
   docker compose ps celery_beat
   ```

2. Verificar logs do Celery Beat:
   ```bash
   docker compose logs celery_beat
   ```

3. Verificar se tarefas estão habilitadas no banco:
   ```python
   from django_celery_beat.models import PeriodicTask
   task = PeriodicTask.objects.get(name="coletar_inlabs_08")
   print(f"Enabled: {task.enabled}")
   ```

4. Re-sincronizar tarefas:
   ```bash
   python manage.py sync_celery_beat
   ```

### Problema: Erro de conexão com Redis

**Sintoma**: Lock distribuído não funciona.

**Solução**:
1. Verificar se Redis está rodando:
   ```bash
   docker compose ps redis
   ```

2. Verificar `CELERY_BROKER_URL` no settings
3. Testar conexão:
   ```python
   from django_licitacao360.apps.imprensa_nacional.tasks import get_redis_client
   redis_client = get_redis_client()
   redis_client.ping()  # Deve retornar True
   ```

### Problema: Arquivos temporários acumulando

**Sintoma**: Espaço em disco sendo consumido.

**Solução**: Os arquivos são salvos em `INLABS_DOWNLOAD_ROOT`. Limpar manualmente se necessário:

```bash
# Limpar downloads antigos (manter últimos 7 dias)
find /app/tmp/inlabs -type d -mtime +7 -exec rm -rf {} +
```

---

## Monitoramento

### Métricas Importantes

1. **Taxa de Sucesso**: Percentual de execuções bem-sucedidas
2. **Artigos Coletados**: Número médio de artigos por execução
3. **Tempo de Execução**: Duração média do processo
4. **Falhas de Lock**: Quantas vezes a execução foi pulada por lock

### Logs Recomendados

- Logs de início/fim de cada execução
- Logs de erros com stack trace completo
- Logs de lock adquirido/liberado
- Logs de download (tentativas e sucessos)

### Alertas Sugeridos

- Falha consecutiva por mais de 2 dias
- Nenhum artigo coletado por mais de 3 dias
- Tempo de execução acima de 1 hora
- Erro de autenticação

---

## Melhorias Futuras

1. **Notificações**: Enviar alertas quando nenhum artigo for encontrado
2. **Retry Inteligente**: Retry apenas para erros transitórios
3. **Cache**: Cachear credenciais de autenticação
4. **Métricas**: Integração com sistema de métricas (Prometheus/Grafana)
5. **Webhook**: Notificar sistemas externos quando novos artigos forem coletados
6. **Filtros Avançados**: Permitir múltiplas palavras-chave ou expressões regulares

---

## Referências

- [Documentação Celery Beat](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html)
- [Documentação Django Celery Beat](https://django-celery-beat.readthedocs.io/)
- [Portal INLABS](https://inlabs.in.gov.br/)
- [Documentação Selenium](https://www.selenium.dev/documentation/)

---

**Última Atualização**: 2026-02-07
