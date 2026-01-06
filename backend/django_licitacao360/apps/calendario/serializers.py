from rest_framework import serializers

from .models import CalendarioEvento


class CalendarioEventoSerializer(serializers.ModelSerializer):
    """Serializer para eventos do calendário."""
    
    class Meta:
        model = CalendarioEvento
        fields = [
            "id",
            "nome",
            "data",
            "descricao",
            "cor",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
