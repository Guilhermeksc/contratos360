"""Compatibilidade para importações antigas do serializer de UASG."""

from django_licitacao360.apps.uasgs.serializers import UasgSerializer  # noqa: F401

__all__ = ['UasgSerializer']

