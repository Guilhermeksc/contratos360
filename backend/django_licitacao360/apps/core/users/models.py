from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UsuarioManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("O campo username é obrigatório.")
        extra_fields.setdefault("is_active", True)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, password, **extra_fields)


class Usuario(AbstractUser):
    username = None  # remove o campo padrão
    username = models.CharField("username", max_length=20, unique=True)
    perfil = models.CharField("Perfil", max_length=50, choices=[
        ("admin", "Administrador"),
        ("consulta", "Consulta"),
        ("editor", "Editor"),        
    ])

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["perfil"]

    objects = UsuarioManager()

    def __str__(self):
        return f"{self.username} ({self.perfil})"
