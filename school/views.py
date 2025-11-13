from django.shortcuts import render
from django import template
from .models import Turmas, Aluno 
from django.urls import reverse
from django.shortcuts import redirect

# FUNÇÕES DE UTILIDADE
def dict_get(d, key):
    if isinstance(d, dict):
        return d.get(key)
    return d

register = template.Library()
register.filter('dict_get', dict_get)


# 🚨 HUB PRINCIPAL (FUNÇÃO QUE ESTAVA FALTANDO)
def desempenho_index(request):
    """HUB principal de desempenho (apenas links para a coordenação/professores)"""
    
    # Exemplo: Redirecionar usuários não logados para o login ou uma landing page.
    # if not request.user.is_authenticated:
    #     return redirect('login') 
        
    return render(request, 'desempenho_index.html')