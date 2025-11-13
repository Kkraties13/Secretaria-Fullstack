from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from school.models import CalendarioAcademico, AgendaProfessor, Notificacao


class Command(BaseCommand):
    help = 'Gera notificações para eventos e atividades próximas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias',
            type=int,
            default=1,
            help='Número de dias de antecedência para gerar notificações (padrão: 1)'
        )

    def handle(self, *args, **options):
        dias_antecedencia = options['dias']
        data_limite = timezone.now().date() + timedelta(days=dias_antecedencia)
        
        self.stdout.write(f'Gerando notificações para eventos até {data_limite}...')
        
        # Gerar notificações para eventos do calendário acadêmico
        eventos_proximos = CalendarioAcademico.objects.filter(
            data_inicio__lte=data_limite,
            data_inicio__gte=timezone.now().date()
        ).exclude(
            # Evitar duplicar notificações já criadas
            id__in=Notificacao.objects.filter(
                evento_calendario__isnull=False
            ).values_list('evento_calendario_id', flat=True)
        )
        
        notificacoes_eventos = 0
        for evento in eventos_proximos:
            dias_restantes = (evento.data_inicio - timezone.now().date()).days
            
            if dias_restantes == 0:
                titulo = f"🚨 HOJE: {evento.titulo}"
                mensagem = f"O evento '{evento.titulo}' acontece hoje!"
            elif dias_restantes == 1:
                titulo = f"⏰ AMANHÃ: {evento.titulo}"
                mensagem = f"O evento '{evento.titulo}' acontece amanhã ({evento.data_inicio.strftime('%d/%m/%Y')})."
            else:
                titulo = f"📅 Em {dias_restantes} dias: {evento.titulo}"
                mensagem = f"O evento '{evento.titulo}' acontece em {dias_restantes} dias ({evento.data_inicio.strftime('%d/%m/%Y')})."
            
            if evento.turma:
                mensagem += f" Turma: {evento.turma}"
            
            if evento.descricao:
                mensagem += f"\n\nDescrição: {evento.descricao}"
            
            Notificacao.objects.create(
                titulo=titulo,
                mensagem=mensagem,
                tipo='evento_proximo',
                evento_calendario=evento
            )
            notificacoes_eventos += 1
        
        # Gerar notificações para atividades dos professores
        atividades_proximas = AgendaProfessor.objects.filter(
            data__lte=data_limite,
            data__gte=timezone.now().date()
        ).exclude(
            # Evitar duplicar notificações já criadas
            id__in=Notificacao.objects.filter(
                atividade_professor__isnull=False
            ).values_list('atividade_professor_id', flat=True)
        )
        
        notificacoes_atividades = 0
        for atividade in atividades_proximas:
            dias_restantes = (atividade.data - timezone.now().date()).days
            
            if dias_restantes == 0:
                titulo = f"🚨 HOJE: {atividade.titulo}"
                mensagem = f"A atividade '{atividade.titulo}' está agendada para hoje às {atividade.hora_inicio.strftime('%H:%M')}."
            elif dias_restantes == 1:
                titulo = f"⏰ AMANHÃ: {atividade.titulo}"
                mensagem = f"A atividade '{atividade.titulo}' está agendada para amanhã ({atividade.data.strftime('%d/%m/%Y')}) às {atividade.hora_inicio.strftime('%H:%M')}."
            else:
                titulo = f"📋 Em {dias_restantes} dias: {atividade.titulo}"
                mensagem = f"A atividade '{atividade.titulo}' está agendada para {atividade.data.strftime('%d/%m/%Y')} às {atividade.hora_inicio.strftime('%H:%M')}."
            
            mensagem += f"\nProfessor: {atividade.professor.complet_name_prof}"
            
            if atividade.descricao:
                mensagem += f"\n\nDescrição: {atividade.descricao}"
            
            Notificacao.objects.create(
                titulo=titulo,
                mensagem=mensagem,
                tipo='atividade_proxima',
                atividade_professor=atividade,
                professor=atividade.professor
            )
            notificacoes_atividades += 1
        
        total_notificacoes = notificacoes_eventos + notificacoes_atividades
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Notificações geradas com sucesso!\n'
                f'- Eventos do calendário: {notificacoes_eventos}\n'
                f'- Atividades de professores: {notificacoes_atividades}\n'
                f'- Total: {total_notificacoes}'
            )
        )

