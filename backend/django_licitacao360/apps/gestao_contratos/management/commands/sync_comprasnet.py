"""
Management command para sincronizar dados da API ComprasNet
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ...services.ingestion import ComprasNetIngestionService


class Command(BaseCommand):
    help = 'Sincroniza contratos da API pública do ComprasNet'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--uasg',
            type=str,
            help='Código da UASG para sincronizar (ex: 787010)',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Sincroniza todas as UASGs cadastradas',
        )
        parser.add_argument(
            '--contrato',
            type=str,
            help='ID do contrato para sincronizar detalhes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força atualização mesmo se os dados já existirem',
        )
    
    def handle(self, *args, **options):
        service = ComprasNetIngestionService()
        
        if options['contrato']:
            # Sincroniza detalhes de um contrato específico
            contrato_id = options['contrato']
            self.stdout.write(f'Sincronizando detalhes do contrato {contrato_id}...')
            stats = service.sync_contrato_detalhes(contrato_id)
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Detalhes sincronizados: {stats}'
                )
            )
        
        elif options['uasg']:
            # Sincroniza uma UASG específica
            uasg_code = options['uasg']
            self.stdout.write(f'Sincronizando contratos da UASG {uasg_code}...')
            stats = service.sync_contratos_por_uasg(uasg_code)
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Sincronização concluída: {stats}'
                )
            )
        
        elif options['all']:
            # Sincroniza todas as UASGs cadastradas
            from django_licitacao360.apps.uasgs.models import Uasg
            
            uasgs = Uasg.objects.all()
            if not uasgs.exists():
                raise CommandError('Nenhuma UASG cadastrada. Use --uasg para sincronizar uma UASG específica.')
            
            self.stdout.write(f'Sincronizando {uasgs.count()} UASGs...')
            
            total_stats = {
                'contratos_processados': 0,
                'historicos': 0,
                'empenhos': 0,
                'itens': 0,
                'arquivos': 0,
            }
            
            for uasg in uasgs:
                self.stdout.write(f'\nProcessando UASG {uasg.uasg}...')
                stats = service.sync_contratos_por_uasg(uasg.uasg)
                
                for key in total_stats:
                    total_stats[key] += stats.get(key, 0)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ Sincronização completa: {total_stats}'
                )
            )
        
        else:
            raise CommandError(
                'Especifique --uasg, --contrato ou --all. '
                'Use --help para mais informações.'
            )

