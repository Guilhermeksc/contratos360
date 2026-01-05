"""Compatibilidade para importações antigas de gestao_contratos."""

from django_licitacao360.apps.uasgs.models import ComimSup, Uasg  # noqa: F401

__all__ = ['ComimSup', 'Uasg']

