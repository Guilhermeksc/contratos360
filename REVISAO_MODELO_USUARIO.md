# Revisão do Modelo de Usuário - Sistema de Níveis e Permissões por Módulo

## 📋 Resumo das Mudanças

O modelo de usuário foi completamente revisado para implementar um sistema de **3 níveis de acesso** e **permissões granulares por módulo**.

## 🎯 Estrutura Implementada

### Níveis de Acesso

- **Nível 1 - Básico**: Menos privilégios (consulta básica)
- **Nível 2 - Intermediário**: Privilégios intermediários (edição limitada)
- **Nível 3 - Completo**: Máximos privilégios (acesso completo)

**Regra importante**: Usuários de nível 3 têm acesso automático a **todos os módulos**.

### Módulos Disponíveis

Cada usuário pode ter acesso aos seguintes módulos:

1. **Planejamento** (`acesso_planejamento`)
2. **Contratos** (`acesso_contratos`)
3. **Gerata** (`acesso_gerata`)
4. **Empresas** (`acesso_empresas`)
5. **Processo Sancionatório** (`acesso_processo_sancionatorio`)
6. **Controle Interno** (`acesso_controle_interno`)

## 📝 Arquivos Modificados

### 1. Modelo (`models.py`)

- ✅ Removido campo `perfil` (antigo sistema)
- ✅ Adicionado campo `nivel_acesso` (1, 2 ou 3)
- ✅ Adicionados 6 campos booleanos para permissões por módulo
- ✅ Implementados métodos helper:
  - `tem_acesso_modulo(modulo)` - Verifica acesso a um módulo
  - `get_modulos_acesso()` - Retorna lista de módulos com acesso
  - `get_nivel_display_name()` - Retorna nome amigável do nível

### 2. Admin (`admin.py`)

- ✅ Interface atualizada com novos campos
- ✅ Visualização colorida dos níveis de acesso
- ✅ Lista de módulos com acesso
- ✅ Campos de módulo readonly para nível 3 (automático)

### 3. Serializers

**`serializers.py`**:
- ✅ `UsuarioSerializer` - Serializer completo com todos os campos
- ✅ `UsuarioListSerializer` - Serializer simplificado para listagem

**`auth/serializers.py`**:
- ✅ Token JWT atualizado com `nivel_acesso` e permissões por módulo
- ✅ Resposta de login inclui informações de acesso

### 4. Signals (`signals.py`)

- ✅ Atualizado para usar `nivel_acesso` ao invés de `perfil`
- ✅ Usuários criados com nível 1 por padrão
- ✅ Admin criado com nível 3

### 5. Management Commands

- ✅ `create_admin.py` atualizado para novo modelo

### 6. Migrations

- ✅ `0003_add_nivel_acesso_and_module_permissions.py` - Adiciona novos campos e migra dados
- ✅ `0004_remove_perfil_field.py` - Remove campo antigo `perfil`

## 🔄 Migração de Dados

A migration `0003` migra automaticamente usuários existentes:

- **Superusers** (`is_superuser=True`) → Nível 3 + acesso a todos os módulos
- **Staff users** (`is_staff=True`) → Nível 2
- **Outros usuários** → Nível 1 (padrão)

Se o campo `perfil` ainda existir durante a migração:
- `perfil='admin'` → Nível 3 + todos os módulos
- `perfil='editor'` → Nível 2
- `perfil='consulta'` ou `'user'` → Nível 1

## 🚀 Como Usar

### Verificar acesso a um módulo

```python
from django_licitacao360.apps.core.users.models import Usuario

user = Usuario.objects.get(username='usuario_teste')

# Verificar acesso
if user.tem_acesso_modulo('contratos'):
    # Usuário tem acesso ao módulo de contratos
    pass

# Listar módulos com acesso
modulos = user.get_modulos_acesso()
# Retorna: ['planejamento', 'contratos', 'gerata']
```

### Criar usuário com permissões

```python
# Nível 1 com acesso apenas a contratos
user = Usuario.objects.create_user(
    username='usuario1',
    password='senha123',
    nivel_acesso=1,
    acesso_contratos=True
)

# Nível 2 com acesso a múltiplos módulos
user = Usuario.objects.create_user(
    username='usuario2',
    password='senha123',
    nivel_acesso=2,
    acesso_planejamento=True,
    acesso_contratos=True,
    acesso_empresas=True
)

# Nível 3 (acesso automático a todos os módulos)
user = Usuario.objects.create_user(
    username='usuario3',
    password='senha123',
    nivel_acesso=3
    # Não precisa especificar módulos, são habilitados automaticamente
)
```

### No Admin Django

1. Acesse `/admin/users/usuario/`
2. Ao criar/editar usuário:
   - Selecione o **Nível de Acesso** (1, 2 ou 3)
   - Marque os **módulos** aos quais o usuário terá acesso
   - **Nota**: Nível 3 tem acesso automático a todos os módulos

## 🔐 Validações

- ✅ Nível 3 **sempre** tem acesso a todos os módulos (validação automática)
- ✅ Validação no método `clean()` do modelo
- ✅ Validação no método `save()` garante consistência

## 📊 Exemplo de Uso em Views/APIs

```python
from rest_framework.permissions import BasePermission

class TemAcessoModulo(BasePermission):
    """
    Permissão customizada para verificar acesso a módulos específicos
    """
    def __init__(self, modulo):
        self.modulo = modulo
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superuser sempre tem acesso
        if request.user.is_superuser:
            return True
        
        return request.user.tem_acesso_modulo(self.modulo)


# Uso em ViewSet
from rest_framework import viewsets
from rest_framework.decorators import action

class ContratoViewSet(viewsets.ModelViewSet):
    permission_classes = [TemAcessoModulo('contratos')]
    
    # ...
```

## ⚠️ Importante

1. **Migração**: Execute as migrations antes de usar:
   ```bash
   docker compose exec backend python manage.py migrate users
   ```

2. **Backward Compatibility**: O campo `perfil` foi removido. Se houver código que ainda usa `user.perfil`, será necessário atualizar.

3. **Token JWT**: Tokens antigos podem não funcionar. Usuários precisam fazer login novamente para obter novo token com as novas informações.

4. **Admin**: Usuários de nível 3 têm campos de módulo readonly no admin (são habilitados automaticamente).

## 📚 Métodos Úteis do Modelo

```python
# Verificar acesso
user.tem_acesso_modulo('contratos')  # True/False

# Listar módulos com acesso
user.get_modulos_acesso()  # ['planejamento', 'contratos', ...]

# Nome do nível
user.get_nivel_display_name()  # "Nível 3 - Completo"
```

## 🎨 Interface Admin

- **List Display**: Mostra username, nível de acesso (colorido), módulos com acesso, status
- **Filtros**: Por nível, status, e cada módulo individualmente
- **Cores**: 
  - Nível 1: Cinza
  - Nível 2: Laranja
  - Nível 3: Verde

## ✅ Checklist de Implementação

- [x] Modelo atualizado com níveis e módulos
- [x] Admin atualizado
- [x] Serializers atualizados
- [x] Signals atualizados
- [x] Management commands atualizados
- [x] Migrations criadas
- [ ] Testes unitários (recomendado)
- [ ] Documentação de API atualizada (se aplicável)
- [ ] Frontend atualizado para usar novos campos (se aplicável)


