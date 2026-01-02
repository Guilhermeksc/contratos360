import os
import sys

# Caminho raiz do seu projeto Django
DJANGO_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'django_licitacao360')

# Nome do app que não será afetado (opcional - deixe vazio para processar todos)
EXCLUDED_APP = ''

def delete_migrations():
    deleted_count = 0
    skipped_count = 0
    
    for root, dirs, files in os.walk(DJANGO_ROOT):
        if 'migrations' in dirs:
            migrations_path = os.path.join(root, 'migrations')
            app_name = os.path.basename(os.path.dirname(migrations_path))
            
            # Pula o app se estiver na lista de exclusão
            if EXCLUDED_APP and app_name == EXCLUDED_APP:
                print(f"\n⏭️  Pulando app: {app_name}")
                skipped_count += 1
                continue
            
            print(f"\n📁 Verificando app: {app_name}")
            
            # Lista todos os arquivos no diretório migrations
            try:
                files_in_migrations = os.listdir(migrations_path)
            except Exception as e:
                print(f"✗ Erro ao listar arquivos em {migrations_path}: {str(e)}")
                continue
            
            # Deleta todos os arquivos exceto __init__.py
            for file in files_in_migrations:
                file_path = os.path.join(migrations_path, file)
                
                # Mantém apenas __init__.py
                if file == '__init__.py':
                    print(f"  ✓ Mantendo: {file}")
                    continue
                
                # Deleta arquivos .py e outros arquivos (como .pyc, etc)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"  ✓ Deletado: {file}")
                        deleted_count += 1
                    elif os.path.isdir(file_path):
                        # Remove diretórios também (caso existam __pycache__)
                        import shutil
                        shutil.rmtree(file_path)
                        print(f"  ✓ Diretório removido: {file}")
                        deleted_count += 1
                except Exception as e:
                    print(f"  ✗ Erro ao deletar {file}: {str(e)}")

    print(f"\n{'='*50}")
    print(f"✨ Concluído!")
    print(f"📊 Arquivos deletados: {deleted_count}")
    if skipped_count > 0:
        print(f"⏭️  Apps pulados: {skipped_count}")
    print(f"📝 Obs: Arquivos '__init__.py' foram mantidos.")
    print(f"{'='*50}")

if __name__ == '__main__':
    delete_migrations()