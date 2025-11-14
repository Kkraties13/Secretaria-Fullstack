from django.shortcuts import render, redirect, get_object_or_404
from django import template
from .models import Turmas, Aluno 
from django.urls import reverse
from django.db.models import Avg, Sum, Count
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpRequest, JsonResponse
# Importações necessárias para Auth (adicionadas para completar o esqueleto)
from django.contrib.auth import login, logout, authenticate

# ==============================================================================
# FUNÇÕES DE UTILIDADE E FILTROS DO TEMPLATE (Mantido do seu código)
# ==============================================================================

def dict_get(d, key):
    """ Filtro de template customizado para acessar chaves de dicionário. """
    if isinstance(d, dict):
        return d.get(key)
    return d

register = template.Library()
register.filter('dict_get', dict_get)


# ==============================================================================
# 1. AUTENTICAÇÃO (Esqueleto - Funções essenciais para rotas de login/logout)
# ==============================================================================

def login_user(request: HttpRequest) -> HttpResponse:
    """ View de Login. OBS: Adicionar lógica real de autenticação aqui. """
    return render(request, 'school/auth/login.html')

def register_user(request: HttpRequest) -> HttpResponse:
    """ View de Registro. OBS: Adicionar lógica real de registro aqui. """
    return render(request, 'school/auth/register.html')

def logout_user(request: HttpRequest) -> HttpResponse:
    """ View de Logout. Rota: path('logout/', views.logout_user) """
    logout(request)
    return redirect('school:login') # Redireciona para a rota de login após sair

# ==============================================================================
# 2. ROTAS PRINCIPAIS E DASHBOARD
# ==============================================================================

@login_required
def index(request: HttpRequest) -> HttpResponse:
    """ 
    View para a página inicial (Dashboard).
    Rota: path('', views.index) 
    """
    context = {
        'titulo': 'Dashboard Principal',
        # OBS: Adicionar dados dinâmicos para os cards do dashboard
    }
    # O dashboard principal geralmente usa um template base, como dashboard.html
    return render(request, 'school/dashboard.html', context)

# ==============================================================================
# 3. GERENCIAMENTO GERAL (Alunos e Turmas - Esqueleto)
# ==============================================================================

@login_required
def alunos_index(request: HttpRequest) -> HttpResponse:
    """ Lista geral de todos os alunos. Rota: path('alunos/', ...) """
    # Busca todos os alunos e passa para o template
    alunos = Aluno.objects.select_related('responsavel', 'class_choices').all().order_by('complet_name_aluno')
    return render(request, 'alunos_index.html', {'alunos': alunos})

@login_required
def turmas_index(request: HttpRequest) -> HttpResponse:
    """ Lista geral de todas as turmas. Rota: path('turmas/', ...) """
    # turmas = Turmas.objects.all()
    return render(request, 'school/turmas/turmas_index.html', {'turmas': []})

@login_required
def professor_index(request: HttpRequest) -> HttpResponse:
    """ Painel do Professor com links para chamada e lançamento de notas. Rota: path('professores/', ...) """
    context = {
        'titulo': 'Painel do Professor',
    }
    return render(request, 'professor_index.html', context)


# ==============================================================================
# 4. VIEWS DE DESEMPENHO (Seu Código Otimizado e Unificado)
# ==============================================================================

@login_required
def desempenho_index(request):
    """HUB principal de desempenho (apenas links para a coordenação/professores)
    Esta função agora serve como o menu principal do Desempenho.
    Rota: path('desempenho/', views.desempenho_index)
    """
    
    # Busca todas as turmas disponíveis para listar no menu
    turmas = Turmas.objects.all().order_by('nome')

    context = {
        'title': 'Menu de Desempenho',
        'turmas': turmas,
    }
    
    # OBS: Recomenda-se usar um template específico para o hub de desempenho
    return render(request, 'school/desempenho/desempenho_hub.html', context)

@login_required
def ver_desempenho(request, turma_id):
    """
    Dashboard de desempenho:
    Mostra detalhes de desempenho de uma turma específica usando turma_id.
    Rota: path('desempenho/<int:turma_id>/', views.ver_desempenho)
    """
    
    try:
        # Tenta buscar a turma específica
        turma_selecionada = Turmas.objects.get(pk=turma_id)
        
        # Busca alunos dessa turma
        # Inclui anotações (annotations) para calcular a média de notas de cada aluno (se existir)
        # OBS: O campo 'notas__valor' pressupõe que você tem um modelo 'Notas' relacionado
        # ao 'Aluno' através de um ForeignKey ou ManyToMany.
        alunos_da_turma = Aluno.objects.filter(turma=turma_selecionada).annotate(
            # Exemplo de anotação (descomente e ajuste conforme seu modelo 'Notas'):
            # media_notas=Avg('notas__valor') 
        ).order_by('nome')
        
        # Calculando métricas da turma (ex: média da turma)
        # OBS: Adapte conforme a anotação acima.
        metrics = {
            'total_alunos': alunos_da_turma.count(),
            'media_turma_exemplo': 7.5, # Valor de exemplo
        }
        
        context = {
            'turma_selecionada': turma_selecionada,
            'alunos_da_turma': alunos_da_turma,
            'metrics': metrics,
            'title': f'Desempenho da Turma: {turma_selecionada.nome}',
            'turma_id': turma_id,
        }
        
    except Turmas.DoesNotExist:
        raise Http404("Turma não encontrada.")
    
    # O template principal para exibir o desempenho detalhado
    return render(request, 'school/desempenho/desempenho_detalhe.html', context)

def aluno_detalhe(request: HttpRequest, aluno_id: int) -> HttpResponse:
    """
    View de Detalhe do Aluno.
    Rota: path('alunos/detalhe/<int:aluno_id>/', views.aluno_detalhe)
    """
    # Tenta buscar o aluno, se não existir, retorna um erro 404
    aluno = get_object_or_404(Aluno, pk=aluno_id)
    
    # OBS: Aqui você pode adicionar lógica para buscar:
    # - Notas recentes do aluno.
    # - Faltas.
    # - Advertências.
    # - Informações de contato do responsável.

    context = {
        'titulo': f'Detalhe do Aluno: {aluno.nome}',
        'aluno': aluno,
        # Adicione mais dados conforme a necessidade do seu template
    }
    
    return render(request, 'school/alunos/aluno_detalhe.html', context)

def turma_detalhe(request: HttpRequest, turma_id: int) -> HttpResponse:
    """
    View de Detalhe da Turma.
    Rota: path('turmas/detalhe/<int:turma_id>/', views.turma_detalhe)
    """
    # Tenta buscar a turma, se não existir, retorna um erro 404
    turma = get_object_or_404(Turmas, pk=turma_id)
    
    # Busca todos os alunos associados a esta turma
    alunos_da_turma = Aluno.objects.filter(turma=turma).order_by('nome')
    
    # OBS: Você pode adicionar lógica para buscar:
    # - Médias da turma.
    # - Professores responsáveis pelas disciplinas.
    
    context = {
        'titulo': f'Detalhe da Turma: {turma.nome}',
        'turma': turma,
        'alunos_da_turma': alunos_da_turma,
    }
    
    return render(request, 'school/turmas/turma_detalhe.html', context)
