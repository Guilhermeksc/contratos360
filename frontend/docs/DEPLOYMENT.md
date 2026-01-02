# GitHub Actions Deployment Setup

## Configuração dos Secrets

Para que o GitHub Actions funcione corretamente, você precisa configurar os seguintes secrets no seu repositório:

### Secrets Obrigatórios para Deploy em Servidor:

1. **HOST** - IP ou domínio do seu servidor
2. **USERNAME** - Nome de usuário SSH do servidor
3. **SSH_KEY** - Chave SSH privada para acesso ao servidor
4. **PORT** - Porta SSH (padrão: 22)
5. **PROJECT_PATH** - Caminho do projeto no servidor (padrão: /opt/cemos-2028)

### Secrets Opcionais para Docker Hub:

1. **DOCKER_HUB_USERNAME** - Seu username do Docker Hub
2. **DOCKER_HUB_ACCESS_TOKEN** - Token de acesso do Docker Hub

## Como configurar os secrets:

1. Vá para: `Settings` > `Secrets and variables` > `Actions`
2. Clique em `New repository secret`
3. Adicione cada secret com seu respectivo valor

## Preparação do Servidor:

### 1. Instalar Docker e Docker Compose no servidor:

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar Docker Compose V2 (recomendado)
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# OU usar Docker Compose plugin (mais moderno)
# Já incluído no Docker Desktop e versões recentes do Docker Engine
```

### 2. Clonar o repositório no servidor:

```bash
# Criar diretório do projeto
sudo mkdir -p /opt/cemos-2028
sudo chown $USER:$USER /opt/cemos-2028

# Clonar repositório
git clone https://github.com/Guilhermeksc/cemos-2028.git /opt/cemos-2028
cd /opt/cemos-2028
```

### 3. Configurar permissões e arquivos:

```bash
# Dar permissões adequadas
sudo chown -R $USER:$USER /opt/cemos-2028

# Se necessário, criar arquivo .env (opcional - variáveis já estão no docker-compose.yml)
# cp .env.example .env
# nano .env
```

## Funcionamento do Workflow:

### Mudanças Implementadas para Compatibilidade:

1. **Docker Compose V2**: Uso de `docker compose` em vez de `docker-compose`
2. **Variáveis de Ambiente**: Criação automática do arquivo .env durante o CI
3. **Health Checks**: Melhorados para usar os endpoints corretos da API
4. **Timeouts**: Aumentados para aguardar a inicialização completa dos serviços
5. **Logs**: Adicionados para debugging em caso de falhas
6. **Criação de Admin**: Script automático para criar usuário admin

### Jobs do Workflow:

1. **Test**: Executa testes automatizados a cada push/PR
2. **Build and Deploy**: Faz deploy automático apenas no branch master/main
3. **Deploy Local**: Executa build de desenvolvimento em PRs para verificação

## Estrutura dos Serviços (compatível):

```yaml
# Serviços definidos no docker-compose.yml:
- backend: Django + Gunicorn (porta interna 8000)
- db: PostgreSQL 18 (porta interna 5432)
- nginx: Nginx + Angular (porta externa 8088 → interna 80)
```

## Portas utilizadas:

- **Frontend (Nginx)**: 8088 (externa) → 80 (interna)
- **Backend (Django)**: 8000 (interna) 
- **Database (PostgreSQL)**: 5432 (interna)

## Endpoints da API:

- **Health Check**: `GET /api/health/`
- **Login**: `POST /api/auth/login/`
- **Token Refresh**: `POST /api/auth/token/refresh/`

## Monitoramento:

Após o deploy, verifique:
- Site disponível em: `http://SEU_SERVIDOR:8088`
- Logs: `docker-compose logs -f`
- Status: `docker-compose ps`

## Solução de Problemas:

### Se o deploy falhar:

1. Verifique os logs do GitHub Actions
2. Conecte-se ao servidor e execute:
   ```bash
   docker-compose logs backend
   docker-compose logs nginx
   ```

### Para fazer deploy manual:

```bash
ssh usuario@seu-servidor
cd cemos-2028
git pull origin master
docker-compose down
docker-compose up -d --build
```

## Melhorias Futuras:

1. Adicionar notificações (Slack, email)
2. Implementar rollback automático
3. Adicionar smoke tests pós-deploy
4. Configurar monitoramento de saúde
5. Implementar deploy blue-green