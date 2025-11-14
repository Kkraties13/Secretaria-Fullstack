"""
Arquivo principal de rotas para o app 'school', após refatoração
para separar views por responsabilidade (Academico, Disciplina, Eventos).

Este arquivo contém todas as rotas de navegação, relatórios e eventos.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

# Importações dos Módulos Refatorados
from . import views # Para funções gerais/hubs (index, alunos, turmas, desempenho_index, login)
from . import views # Para funções gerais/hubs (index, alunos, turmas, desempenho_index, login)

# 🚨 1. VIEWS ACADÊMICAS (Contrato, Boletim, Gráficos, Suspensão, etc.)
from .views_academico import (
    gerar_contrato_pdf, boletim_aluno, boletim_aluno_pdf,
    grafico_desempenho_aluno, relatorio_turma, grafico_disciplina,
    desempenho_aluno_select, desempenho_turma_select, desempenho_disciplina_select,
    suspensao_select_turma, suspensao_select_aluno, suspensao_create, suspensao_list
)
# 🚨 2. VIEWS DISCIPLINA (Faltas e Presença)
from .views_disciplina import (
    faltas_aluno_pdf, relatorio_faltas_pdf, relatorio_presenca_pdf
)
# 🚨 3. VIEWS EVENTOS (Calendário, Agenda, Notificações)
from .views_eventos import (
    calendario_academico, adicionar_evento_calendario, editar_evento_calendario,
    excluir_evento_calendario, agenda_professor, adicionar_atividade_agenda,
    editar_atividade_agenda, excluir_atividade_agenda, lista_professores_agenda,
    listar_notificacoes, marcar_notificacao_enviada, excluir_notificacao,
    inscrever_aluno_evento
)

# Advertência (mantida separada)
from .views_advertencia import gerar_advertencia_pdf

app_name = 'school'

urlpatterns = [
    # Admin (Mantido)
    path('admin/', admin.site.urls),

    # ------------------------------------
    # Rotas Principais e Usuários (views.py)
    # ------------------------------------
    path('', views.index, name='index'), # Index principal usando a view funcional
    
    # Gerenciamento de Alunos e Turmas
    path('alunos/', views.alunos_index, name='alunos_index'),
    path('alunos/detalhe/<int:aluno_id>/', views.aluno_detalhe, name='aluno_detalhe'),
    path('turmas/', views.turmas_index, name='turmas_index'),
    path('turmas/detalhe/<int:turma_id>/', views.turma_detalhe, name='turma_detalhe'),
    path('professores/', views.professor_index, name='professor_index'),

    # Autenticação
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    
    # ------------------------------------
    # Rotas de Desempenho (VIEWS ACADÊMICAS e views.py)
    # ------------------------------------
    # HUB de seleção
    path('desempenho/', views.desempenho_index, name='desempenho_index'), 
    
    # Nova rota para desempenho detalhado de uma turma
    path('desempenho/<int:turma_id>/', views.ver_desempenho, name='ver_desempenho_turma'), 

    # Seleções e Relatórios
    path('desempenho/aluno/', desempenho_aluno_select, name='desempenho_aluno_select'),
    path('desempenho/turma/', desempenho_turma_select, name='desempenho_turma_select'),
    path('desempenho/disciplina/', desempenho_disciplina_select, name='desempenho_disciplina_select'),

    path('grafico/aluno/<int:aluno_id>/', grafico_desempenho_aluno, name='grafico_desempenho_aluno'),
    path('relatorio/turma/<int:turma_id>/', relatorio_turma, name='relatorio_turma'),
    path('grafico/disciplina/<int:materia_id>/', grafico_disciplina, name='grafico_disciplina'),


    # ------------------------------------
    # Documentos e Faltas (VIEWS ACADÊMICAS e VIEWS DISCIPLINA)
    # ------------------------------------
    path('gerar-contrato/<int:aluno_id>/', gerar_contrato_pdf, name='gerar_contrato_pdf'),
    path('boletim/<int:aluno_id>/', boletim_aluno, name='boletim_aluno'),
    path('boletim/<int:aluno_id>/pdf/', boletim_aluno_pdf, name='boletim_aluno_pdf'),

    path('faltas/aluno/<int:aluno_id>/pdf/', faltas_aluno_pdf, name='faltas_aluno_pdf'), 
    path('relatorio-faltas/<int:turma_id>/', relatorio_faltas_pdf, name='relatorio_faltas_pdf'),
    path('relatorio-presenca/<int:turma_id>/', relatorio_presenca_pdf, name='relatorio_presenca_pdf'),

    # Advertências
    path('advertencia/<int:advertencia_id>/pdf/', gerar_advertencia_pdf, name='gerar_advertencia_pdf'),

    # Suspensões
    path('suspensao/select/turma/', suspensao_select_turma, name='suspensao_select_turma'),
    path('suspensao/select/aluno/<int:turma_id>/', suspensao_select_aluno, name='suspensao_select_aluno'),
    path('suspensao/create/<int:turma_id>/<int:aluno_id>/', suspensao_create, name='suspensao_create'),
    path('suspensao/create/<int:turma_id>/', suspensao_create, name='suspensao_create_no_aluno'),
    path('suspensao/list/', suspensao_list, name='suspensao_list'),

    # ------------------------------------
    # Calendário e Eventos (VIEWS EVENTOS)
    # ------------------------------------
    # Calendário acadêmico
    path('calendario/', calendario_academico, name='calendario_academico'), # Rota funcional
    path('calendario/adicionar/', adicionar_evento_calendario, name='adicionar_evento_calendario'),
    path('calendario/<int:evento_id>/editar/', editar_evento_calendario, name='editar_evento_calendario'),
    path('calendario/<int:evento_id>/excluir/', excluir_evento_calendario, name='excluir_evento_calendario'),
    path('calendario/evento/<int:evento_id>/inscrever/', inscrever_aluno_evento, name='inscrever_aluno_evento'), 

    # Agenda de professores
    path('professores_agenda/', lista_professores_agenda, name='lista_professores_agenda'),
    path('agenda/professor/<int:professor_id>/', agenda_professor, name='agenda_professor'),
    path('agenda/professor/<int:professor_id>/adicionar/', adicionar_atividade_agenda, name='adicionar_atividade_agenda'),
    path('agenda/atividade/<int:atividade_id>/editar/', editar_atividade_agenda, name='editar_atividade_agenda'),
    path('agenda/atividade/<int:atividade_id>/excluir/', excluir_atividade_agenda, name='excluir_atividade_agenda'),

    # Notificações
    path('notificacoes/', listar_notificacoes, name='listar_notificacoes'),
    path('notificacoes/<int:notificacao_id>/enviada/', marcar_notificacao_enviada, name='marcar_notificacao_enviada'),
    path('notificacoes/<int:notificacao_id>/excluir/', excluir_notificacao, name='excluir_notificacao'),

    # ------------------------------------
    # Rotas de Templates Estáticas (Para páginas de menu)
    # ------------------------------------
    path('comunicados/', TemplateView.as_view(template_name='comunicados.html'), name='comunicados'),
    path('agenda/', TemplateView.as_view(template_name='agenda.html'), name='agenda'),
    path('atendimentos/', TemplateView.as_view(template_name='atendimentos.html'), name='atendimentos'),
    path('notas/', TemplateView.as_view(template_name='notas_academicas.html'), name='notas'),
    path('relatorios/', TemplateView.as_view(template_name='relatorios.html'), name='relatorios'),
    path('recursos/', TemplateView.as_view(template_name='recursos.html'), name='recursos'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)