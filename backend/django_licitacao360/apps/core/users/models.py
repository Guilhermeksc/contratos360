from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.exceptions import ValidationError


class UsuarioManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("O campo username é obrigatório.")
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("nivel_acesso", 1)  # Nível padrão
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("nivel_acesso", 3)  # Superuser sempre nível 3
        # Superuser tem acesso a todos os módulos
        extra_fields.setdefault("acesso_planejamento", True)
        extra_fields.setdefault("acesso_contratos", True)
        extra_fields.setdefault("acesso_gerata", True)
        extra_fields.setdefault("acesso_empresas", True)
        extra_fields.setdefault("acesso_processo_sancionatorio", True)
        extra_fields.setdefault("acesso_controle_interno", True)
        return self.create_user(username, password, **extra_fields)


class Usuario(AbstractUser):
    """
    Modelo de usuário customizado com níveis de acesso e permissões por módulo.
    
    Níveis de acesso:
    - Nível 1: Menos privilégios (consulta básica)
    - Nível 2: Privilégios intermediários (edição limitada)
    - Nível 3: Máximos privilégios (acesso completo)
    
    Módulos disponíveis:
    - Planejamento
    - Contratos
    - Gerata
    - Empresas
    - Processo Sancionatório
    - Controle Interno
    """
    username = None  # remove o campo padrão
    username = models.CharField("Username", max_length=20, unique=True)
    
    # Nível de acesso (1, 2 ou 3)
    nivel_acesso = models.IntegerField(
        "Nível de Acesso",
        choices=[
            (1, "Nível 1 - Básico"),
            (2, "Nível 2 - Intermediário"),
            (3, "Nível 3 - Completo"),
        ],
        default=1,
        help_text="Nível 3 tem mais privilégios. Nível 1 tem menos privilégios."
    )
    
    # Permissões por módulo
    acesso_planejamento = models.BooleanField(
        "Acesso ao Módulo Planejamento",
        default=False,
        help_text="Permite acesso ao módulo de Planejamento"
    )
    acesso_contratos = models.BooleanField(
        "Acesso ao Módulo Contratos",
        default=False,
        help_text="Permite acesso ao módulo de Contratos"
    )
    acesso_gerata = models.BooleanField(
        "Acesso ao Módulo Gerata",
        default=False,
        help_text="Permite acesso ao módulo Gerata"
    )
    acesso_empresas = models.BooleanField(
        "Acesso ao Módulo Empresas",
        default=False,
        help_text="Permite acesso ao módulo de Empresas"
    )
    acesso_processo_sancionatorio = models.BooleanField(
        "Acesso ao Módulo Processo Sancionatório",
        default=False,
        help_text="Permite acesso ao módulo de Processo Sancionatório"
    )
    acesso_controle_interno = models.BooleanField(
        "Acesso ao Módulo Controle Interno",
        default=False,
        help_text="Permite acesso ao módulo de Controle Interno"
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["nivel_acesso"]

    objects = UsuarioManager()

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ["username"]

    def clean(self):
        """Validações do modelo"""
        super().clean()
        
        # Validação: Nível 3 deve ter acesso a todos os módulos
        if self.nivel_acesso == 3:
            if not all([
                self.acesso_planejamento,
                self.acesso_contratos,
                self.acesso_gerata,
                self.acesso_empresas,
                self.acesso_processo_sancionatorio,
                self.acesso_controle_interno,
            ]):
                raise ValidationError({
                    'nivel_acesso': 'Usuários de nível 3 devem ter acesso a todos os módulos.'
                })
    
    def save(self, *args, **kwargs):
        """Garante que nível 3 sempre tem acesso a todos os módulos"""
        if self.nivel_acesso == 3:
            self.acesso_planejamento = True
            self.acesso_contratos = True
            self.acesso_gerata = True
            self.acesso_empresas = True
            self.acesso_processo_sancionatorio = True
            self.acesso_controle_interno = True
        super().save(*args, **kwargs)

    def tem_acesso_modulo(self, modulo: str) -> bool:
        """
        Verifica se o usuário tem acesso a um módulo específico.
        
        Args:
            modulo: Nome do módulo ('planejamento', 'contratos', 'gerata', 
                    'empresas', 'processo_sancionatorio', 'controle_interno')
        
        Returns:
            bool: True se o usuário tem acesso, False caso contrário
        """
        # Superuser sempre tem acesso
        if self.is_superuser:
            return True
        
        # Mapeamento de módulos para campos
        modulos_map = {
            'planejamento': 'acesso_planejamento',
            'contratos': 'acesso_contratos',
            'gerata': 'acesso_gerata',
            'empresas': 'acesso_empresas',
            'processo_sancionatorio': 'acesso_processo_sancionatorio',
            'controle_interno': 'acesso_controle_interno',
        }
        
        campo = modulos_map.get(modulo.lower())
        if not campo:
            return False
        
        return getattr(self, campo, False)
    
    def get_modulos_acesso(self) -> list:
        """
        Retorna lista de módulos aos quais o usuário tem acesso.
        
        Returns:
            list: Lista de nomes dos módulos com acesso
        """
        modulos = []
        modulos_map = {
            'planejamento': self.acesso_planejamento,
            'contratos': self.acesso_contratos,
            'gerata': self.acesso_gerata,
            'empresas': self.acesso_empresas,
            'processo_sancionatorio': self.acesso_processo_sancionatorio,
            'controle_interno': self.acesso_controle_interno,
        }
        
        for modulo, tem_acesso in modulos_map.items():
            if tem_acesso:
                modulos.append(modulo)
        
        return modulos
    
    def get_nivel_display_name(self) -> str:
        """Retorna o nome amigável do nível de acesso"""
        return dict(self._meta.get_field('nivel_acesso').choices).get(self.nivel_acesso, 'Desconhecido')

    def __str__(self):
        nivel_nome = self.get_nivel_display_name()
        modulos = ', '.join(self.get_modulos_acesso()) if self.get_modulos_acesso() else 'Nenhum módulo'
        return f"{self.username} - {nivel_nome} ({modulos})"
