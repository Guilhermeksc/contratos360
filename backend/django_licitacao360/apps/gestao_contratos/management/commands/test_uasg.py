"""
Management command para testar sincronização de uma UASG e verificar campos
Uso: python manage.py test_uasg --uasg 787010
"""
from django.core.management.base import BaseCommand
from decimal import Decimal

from ...models import Contrato, Uasg
from ...services.ingestion import ComprasNetIngestionService


class Command(BaseCommand):
    help = 'Testa sincronização de uma UASG e verifica se todos os campos estão sendo salvos corretamente'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--uasg',
            type=str,
            required=True,
            help='Código da UASG para testar (ex: 787010)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Número máximo de contratos para verificar (padrão: 10)',
        )
    
    def handle(self, *args, **options):
        uasg_code = options['uasg']
        limit = options['limit']
        
        self.stdout.write(self.style.SUCCESS(f'\n{"="*80}'))
        self.stdout.write(self.style.SUCCESS(f'Testando sincronização da UASG {uasg_code}'))
        self.stdout.write(self.style.SUCCESS(f'{"="*80}\n'))
        
        # Sincroniza a UASG
        service = ComprasNetIngestionService()
        self.stdout.write(f'Sincronizando contratos da UASG {uasg_code}...')
        stats = service.sync_contratos_por_uasg(uasg_code)
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Sincronização concluída: {stats}'))
        
        # Verifica contratos salvos
        contratos = Contrato.objects.filter(uasg__uasg=uasg_code)[:limit]
        total_contratos = Contrato.objects.filter(uasg__uasg=uasg_code).count()
        
        self.stdout.write(f'\nTotal de contratos salvos: {total_contratos}')
        self.stdout.write(f'Verificando primeiros {len(contratos)} contratos...\n')
        
        # Estatísticas
        campos_stats = {
            'id': 0,
            'numero': 0,
            'valor_global': 0,
            'fornecedor_nome': 0,
            'objeto': 0,
            'vigencia_inicio': 0,
            'vigencia_fim': 0,
        }
        
        problemas_valor_global = []
        
        for idx, contrato in enumerate(contratos, 1):
            self.stdout.write(f'\n--- Contrato {idx}/{len(contratos)} ---')
            self.stdout.write(f'ID: {contrato.id}')
            self.stdout.write(f'Número: {contrato.numero or "N/A"}')
            
            # Verifica campos
            if contrato.id:
                campos_stats['id'] += 1
            if contrato.numero:
                campos_stats['numero'] += 1
            if contrato.fornecedor_nome:
                campos_stats['fornecedor_nome'] += 1
            if contrato.objeto:
                campos_stats['objeto'] += 1
            if contrato.vigencia_inicio:
                campos_stats['vigencia_inicio'] += 1
            if contrato.vigencia_fim:
                campos_stats['vigencia_fim'] += 1
            
            # VERIFICAÇÃO CRÍTICA: valor_global
            if contrato.valor_global is not None:
                campos_stats['valor_global'] += 1
                self.stdout.write(self.style.SUCCESS(f'✅ valor_global: R$ {contrato.valor_global:,.2f}'))
                
                # Verifica tipo
                if not isinstance(contrato.valor_global, Decimal):
                    self.stdout.write(self.style.WARNING(
                        f'⚠️  ATENÇÃO: valor_global não é Decimal, é {type(contrato.valor_global)}'
                    ))
            else:
                self.stdout.write(self.style.ERROR(f'❌ valor_global: None (NÃO FOI SALVO)'))
                
                # Verifica o raw_json
                raw_valor = None
                if contrato.raw_json:
                    raw_valor = contrato.raw_json.get('valor_global')
                    self.stdout.write(f'   Valor no raw_json: {raw_valor} (tipo: {type(raw_valor).__name__ if raw_valor else "None"})')
                
                problemas_valor_global.append({
                    'id': contrato.id,
                    'numero': contrato.numero,
                    'raw_valor': raw_valor
                })
        
        # Relatório final
        self.stdout.write(f'\n{"="*80}')
        self.stdout.write('RELATÓRIO DE CAMPOS')
        self.stdout.write(f'{"="*80}\n')
        
        for campo, quantidade in campos_stats.items():
            porcentagem = (quantidade / len(contratos) * 100) if contratos else 0
            status_icon = "✅" if quantidade == len(contratos) else "⚠️"
            self.stdout.write(f'{status_icon} {campo:20} {quantidade:3}/{len(contratos)} ({porcentagem:5.1f}%)')
        
        # Relatório de problemas com valor_global
        if problemas_valor_global:
            self.stdout.write(f'\n{"="*80}')
            self.stdout.write(self.style.ERROR('PROBLEMAS COM valor_global:'))
            self.stdout.write(f'{"="*80}\n')
            
            for problema in problemas_valor_global:
                self.stdout.write(f'Contrato: {problema["numero"] or problema["id"]}')
                self.stdout.write(f'  ID: {problema["id"]}')
                self.stdout.write(f'  Valor no raw_json: {problema["raw_valor"]}')
                self.stdout.write('')
            
            self.stdout.write(self.style.WARNING(
                f'\n⚠️  {len(problemas_valor_global)} contratos sem valor_global salvo!'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'\n✅ Todos os {len(contratos)} contratos têm valor_global salvo corretamente!'
            ))
        
        # Estatísticas gerais
        total_com_valor = Contrato.objects.filter(
            uasg__uasg=uasg_code
        ).exclude(valor_global__isnull=True).count()
        
        total_sem_valor = Contrato.objects.filter(
            uasg__uasg=uasg_code,
            valor_global__isnull=True
        ).count()
        
        self.stdout.write(f'\n{"="*80}')
        self.stdout.write('ESTATÍSTICAS GERAIS (todos os contratos)')
        self.stdout.write(f'{"="*80}')
        self.stdout.write(f'Total de contratos: {total_contratos}')
        self.stdout.write(self.style.SUCCESS(f'Com valor_global: {total_com_valor}'))
        self.stdout.write(self.style.ERROR(f'Sem valor_global: {total_sem_valor}'))
        
        if total_contratos > 0:
            porcentagem = (total_com_valor / total_contratos * 100)
            self.stdout.write(f'Taxa de sucesso: {porcentagem:.1f}%')
        
        self.stdout.write('')



