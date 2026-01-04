"""
View genérica para servir arquivos de mídia com autenticação
"""
import os
from django.http import FileResponse, Http404
from django.core.files.storage import default_storage
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def serve_file(request):
    """
    Serve arquivos de mídia após validação de autenticação
    
    URL esperada: /api/files/serve/?path=media/certificados/1/2024/uuid.pdf
    
    IMPORTANTE: Esta view garante que apenas usuários autenticados
    possam acessar arquivos de mídia. O Nginx deve fazer proxy
    de /media/ para esta view.
    """
    file_path = request.GET.get("path")
    
    if not file_path:
        return Response(
            {"detail": "Parâmetro 'path' é obrigatório"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validar que o caminho está dentro de MEDIA_ROOT
    from django.conf import settings
    media_root = os.path.abspath(settings.MEDIA_ROOT)
    
    # Remover prefixo /media/ se presente
    if file_path.startswith("media/"):
        file_path = file_path[6:]  # Remove "media/"
    elif file_path.startswith("/media/"):
        file_path = file_path[7:]  # Remove "/media/"
    
    full_path = os.path.abspath(os.path.join(media_root, file_path))
    
    # Verificar que o caminho está dentro de MEDIA_ROOT (prevenir path traversal)
    if not full_path.startswith(media_root):
        return Response(
            {"detail": "Caminho inválido"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Verificar existência do arquivo
    if not default_storage.exists(file_path):
        raise Http404("Arquivo não encontrado")
    
    try:
        # Abrir arquivo via storage
        file = default_storage.open(file_path, "rb")
        filename = os.path.basename(file_path)
        
        # Determinar content type baseado na extensão
        content_type = "application/octet-stream"
        if filename.lower().endswith(".pdf"):
            content_type = "application/pdf"
        elif filename.lower().endswith((".jpg", ".jpeg")):
            content_type = "image/jpeg"
        elif filename.lower().endswith(".png"):
            content_type = "image/png"
        
        # Criar resposta
        response = FileResponse(
            file,
            content_type=content_type,
            as_attachment=False  # Exibir no navegador
        )
        
        # Headers de segurança
        response["X-Content-Type-Options"] = "nosniff"
        response["Content-Disposition"] = f'inline; filename="{filename}"'
        
        return response
        
    except FileNotFoundError:
        raise Http404("Arquivo não encontrado no storage")
    except Exception as e:
        return Response(
            {"detail": f"Erro ao servir arquivo: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

