from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = 'Cria um usuário admin padrão, um usuário anderson e um usuário kopa se não existirem'

    def handle(self, *args, **options):
        Usuario = apps.get_model('users', 'Usuario')
        
        # Verifica se já existe um admin
        if not Usuario.objects.filter(username='admin').exists():
            # Cria o usuário admin padrão com nível 3 e acesso a todos os módulos
            admin_user = Usuario.objects.create_user(
                username='admin',
                password='@cemos2028',
                nivel_acesso=3  # Nível 3 tem acesso automático a todos os módulos
            )
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            
            self.stdout.write(
                self.style.SUCCESS('✅ Usuário admin padrão criado com sucesso!')
            )
            self.stdout.write(f'   Username: admin')
            self.stdout.write(f'   Password: @cemos2028')
            self.stdout.write(
                self.style.WARNING('   ⚠️  IMPORTANTE: Altere a senha padrão após o primeiro login!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('ℹ️  Usuário admin já existe. Nenhuma ação necessária.')
            )

        # Verifica/cria usuário 'anderson'
        if not Usuario.objects.filter(username='anderson').exists():
            anderson_user = Usuario.objects.create_user(
                username='anderson',
                password='@cemos2028',
                nivel_acesso=1  # Nível 1 por padrão
            )
            # Não é staff nem superuser por padrão
            anderson_user.save()

            self.stdout.write(
                self.style.SUCCESS('✅ Usuário "anderson" criado com sucesso!')
            )
            self.stdout.write(f'   Username: anderson')
            self.stdout.write(f'   Password: @cemos2028')
        else:
            self.stdout.write(
                self.style.WARNING('ℹ️  Usuário "anderson" já existe. Nenhuma ação necessária.')
            )

        # Verifica/cria usuário 'kopa'
        if not Usuario.objects.filter(username='kopa').exists():
            kopa_user = Usuario.objects.create_user(
                username='kopa',
                password='@cemos2028',
                nivel_acesso=1  # Nível 1 por padrão
            )
            # Não é staff nem superuser por padrão
            kopa_user.save()

            self.stdout.write(
                self.style.SUCCESS('✅ Usuário "kopa" criado com sucesso!')
            )
            self.stdout.write(f'   Username: kopa')
            self.stdout.write(f'   Password: @cemos2028')
        else:
            self.stdout.write(
                self.style.WARNING('ℹ️  Usuário "kopa" já existe. Nenhuma ação necessária.')
            )