from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone  # Necessário para timezone.now()
from datetime import datetime, date  # Necessário para date.today() e datetime
from django.urls import reverse # Importar reverse se for necessário
from django.db.models import F # Para operações de banco de dados (se for usar)

# Importar Modelos necessários
from .models import (
    CalendarioAcademico, Turmas, AgendaProfessor, Professor, Notificacao,
    Aluno, #InscricaoEvento # InscricaoEvento para a nova funcionalidade
)


# ------------------- CALENDÁRIO ACADÊMICO -------------------

def calendario_academico(request):
    eventos = CalendarioAcademico.objects.all().order_by('data_inicio')
    eventos_por_mes = {}
    for evento in eventos:
        mes_ano = evento.data_inicio.strftime('%Y-%m')
        if mes_ano not in eventos_por_mes: eventos_por_mes[mes_ano] = []
        eventos_por_mes[mes_ano].append(evento)
    
    context = {'eventos': eventos, 'eventos_por_mes': eventos_por_mes, 'hoje': date.today()}
    return render(request, 'calendario_academico.html', context)


def adicionar_evento_calendario(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descricao = request.POST.get('descricao')
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        tipo_evento = request.POST.get('tipo_evento')
        turma_id = request.POST.get('turma')
        
        if not titulo or not data_inicio or not tipo_evento:
            messages.error(request, 'Título, data de início e tipo de evento são obrigatórios.')
            return render(request, 'calendario_form.html', {'turmas': Turmas.objects.all(), 'tipos_evento': CalendarioAcademico.TIPO_EVENTO_CHOICES})
        
        evento = CalendarioAcademico(
            titulo=titulo, descricao=descricao, data_inicio=data_inicio,
            data_fim=data_fim if data_fim else None, tipo_evento=tipo_evento,
            turma_id=turma_id if turma_id else None
        )
        evento.save()
        messages.success(request, 'Evento adicionado com sucesso!')
        return redirect('calendario_academico')
    
    context = {'turmas': Turmas.objects.all(), 'tipos_evento': CalendarioAcademico.TIPO_EVENTO_CHOICES}
    return render(request, 'calendario_form.html', context)


def editar_evento_calendario(request, evento_id):
    evento = get_object_or_404(CalendarioAcademico, id=evento_id)
    if request.method == 'POST':
        evento.titulo = request.POST.get('titulo')
        evento.descricao = request.POST.get('descricao')
        evento.data_inicio = request.POST.get('data_inicio')
        evento.data_fim = request.POST.get('data_fim') if request.POST.get('data_fim') else None
        evento.tipo_evento = request.POST.get('tipo_evento')
        turma_id = request.POST.get('turma')
        evento.turma_id = turma_id if turma_id else None
        
        evento.save()
        messages.success(request, 'Evento atualizado com sucesso!')
        return redirect('calendario_academico')
    
    context = {'evento': evento, 'turmas': Turmas.objects.all(), 'tipos_evento': CalendarioAcademico.TIPO_EVENTO_CHOICES}
    return render(request, 'calendario_form.html', context)


def excluir_evento_calendario(request, evento_id):
    evento = get_object_or_404(CalendarioAcademico, id=evento_id)
    if request.method == 'POST':
        evento.delete()
        messages.success(request, 'Evento excluído com sucesso!')
        return redirect('calendario_academico')
    context = {'evento': evento}
    return render(request, 'confirmar_exclusao.html', context)


# NOVIDADE: Inscrição em Eventos
#def inscrever_aluno_evento(request, evento_id):
#    evento = get_object_or_404(CalendarioAcademico, id=evento_id)
#    
#    if request.user.is_authenticated:
#        try:
#            # Assume que o usuário está ligado a um Aluno (ajuste conforme seu modelo)
#            aluno = Aluno.objects.get(user=request.user) 
#        except Aluno.DoesNotExist:
#            messages.error(request, "Seu perfil não está associado a um aluno.")
#            return redirect('calendario_academico')
#    else:
#        messages.error(request, "Faça login para se inscrever.")
#        return redirect('login') # ou a URL de login que você tiver
#
#    if InscricaoEvento.objects.filter(evento=evento, aluno=aluno).exists():
#        messages.warning(request, "Você já está inscrito neste evento.")
#    else:
#        InscricaoEvento.objects.create(evento=evento, aluno=aluno, status='CONFIRMADO')
#        messages.success(request, f"Inscrição no evento '{evento.titulo}' realizada com sucesso!")
#        
#    return redirect('calendario_academico')


# ------------------- AGENDA DE PROFESSORES -------------------

def agenda_professor(request, professor_id):
    professor = get_object_or_404(Professor, id=professor_id)
    atividades = AgendaProfessor.objects.filter(professor=professor).order_by('data', 'hora_inicio')
    atividades_por_data = {}
    for atividade in atividades:
        data_str = atividade.data.strftime('%Y-%m-%d')
        if data_str not in atividades_por_data: atividades_por_data[data_str] = []
        atividades_por_data[data_str].append(atividade)
    
    context = {'professor': professor, 'atividades': atividades, 'atividades_por_data': atividades_por_data, 'hoje': date.today()}
    return render(request, 'agenda_professor.html', context)


def adicionar_atividade_agenda(request, professor_id):
    professor = get_object_or_404(Professor, id=professor_id)
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descricao = request.POST.get('descricao')
        data = request.POST.get('data')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fim = request.POST.get('hora_fim')
        tipo_atividade = request.POST.get('tipo_atividade')
        
        if not titulo or not data or not hora_inicio or not tipo_atividade:
            messages.error(request, 'Título, data, hora de início e tipo de atividade são obrigatórios.')
            return render(request, 'agenda_professor_form.html', {'professor': professor, 'tipos_atividade': AgendaProfessor.TIPO_ATIVIDADE_CHOICES})
        
        atividade = AgendaProfessor(
            professor=professor, titulo=titulo, descricao=descricao, data=data,
            hora_inicio=hora_inicio, hora_fim=hora_fim if hora_fim else None,
            tipo_atividade=tipo_atividade
        )
        atividade.save()
        messages.success(request, 'Atividade adicionada com sucesso!')
        return redirect('agenda_professor', professor_id=professor.id)
    
    context = {'professor': professor, 'tipos_atividade': AgendaProfessor.TIPO_ATIVIDADE_CHOICES}
    return render(request, 'agenda_professor_form.html', context)


def editar_atividade_agenda(request, atividade_id):
    atividade = get_object_or_404(AgendaProfessor, id=atividade_id)
    if request.method == 'POST':
        atividade.titulo = request.POST.get('titulo')
        atividade.descricao = request.POST.get('descricao')
        atividade.data = request.POST.get('data')
        atividade.hora_inicio = request.POST.get('hora_inicio')
        atividade.hora_fim = request.POST.get('hora_fim') if request.POST.get('hora_fim') else None
        atividade.tipo_atividade = request.POST.get('tipo_atividade')
        
        atividade.save()
        messages.success(request, 'Atividade atualizada com sucesso!')
        return redirect('agenda_professor', professor_id=atividade.professor.id)
    
    context = {'atividade': atividade, 'professor': atividade.professor, 'tipos_atividade': AgendaProfessor.TIPO_ATIVIDADE_CHOICES}
    return render(request, 'agenda_professor_form.html', context)


def excluir_atividade_agenda(request, atividade_id):
    atividade = get_object_or_404(AgendaProfessor, id=atividade_id)
    professor_id = atividade.professor.id
    if request.method == 'POST':
        atividade.delete()
        messages.success(request, 'Atividade excluída com sucesso!')
        return redirect('agenda_professor', professor_id=professor_id)
    context = {'atividade': atividade}
    return render(request, 'confirmar_exclusao_atividade.html', context)


def lista_professores_agenda(request):
    professores = Professor.objects.all().order_by('complet_name_prof')
    context = {'professores': professores}
    return render(request, 'lista_professores_agenda.html', context)


# ------------------- NOTIFICAÇÕES -------------------

def listar_notificacoes(request):
    notificacoes = Notificacao.objects.all().order_by('-data_criacao')
    context = {
        'notificacoes': notificacoes, 'total_notificacoes': notificacoes.count(),
        'notificacoes_nao_enviadas': notificacoes.filter(enviada=False).count(),
    }
    return render(request, 'notificacoes.html', context)


def marcar_notificacao_enviada(request, notificacao_id):
    notificacao = get_object_or_404(Notificacao, id=notificacao_id)
    if request.method == 'POST':
        notificacao.enviada = True
        notificacao.data_envio = timezone.now()
        notificacao.save()
        messages.success(request, 'Notificação marcada como enviada!')
    return redirect('listar_notificacoes')


def excluir_notificacao(request, notificacao_id):
    notificacao = get_object_or_404(Notificacao, id=notificacao_id)
    if request.method == 'POST':
        notificacao.delete()
        messages.success(request, 'Notificação excluída com sucesso!')
        return redirect('listar_notificacoes')
    context = {'notificacao': notificacao}
    return render(request, 'confirmar_exclusao_notificacao.html', context)


def inscrever_aluno_evento(request, evento_id):
    evento = get_object_or_404(CalendarioAcademico, id=evento_id)

    if request.user.is_authenticated:
        try:
            # Assume que o usuário está ligado a um Aluno (ajuste conforme seu modelo)
            aluno = Aluno.objects.get(user=request.user) 
        except Aluno.DoesNotExist:
            messages.error(request, "Seu perfil não está associado a um aluno.")
            return redirect('calendario_academico')
    else:
        messages.error(request, "Faça login para se inscrever.")
        return redirect('login') # ou a URL de login que você tiver

    if InscricaoEvento.objects.filter(evento=evento, aluno=aluno).exists():
        messages.warning(request, "Você já está inscrito neste evento.")
    else:
        InscricaoEvento.objects.create(evento=evento, aluno=aluno)
        messages.success(request, f"Inscrição no evento '{evento.titulo}' realizada com sucesso!")

    return redirect('calendario_academico')