from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import Advertencia, Aluno, Responsavel # Importe os modelos

def gerar_advertencia_pdf(request, advertencia_id):
    # Busca a advertência pelo ID
    advertencia = get_object_or_404(Advertencia, id=advertencia_id)
    
    # Busca o aluno e o responsável
    aluno = advertencia.aluno
    responsavel = aluno.responsavel
    
    # Contexto passado ao template
    context = {
        'advertencia': advertencia,
        'aluno': aluno,
        'responsavel': responsavel,
    }

    # Template padrão unificado
    html_string = render_to_string('documentoadvertencia_pdf.html', context)

    # Gera o PDF
    pdf = HTML(string=html_string).write_pdf()

    # Retorna o PDF como resposta HTTP
    response = HttpResponse(pdf, content_type='application/pdf')
    # Mude para 'inline' para abrir no navegador
    response['Content-Disposition'] = f'inline; filename="advertencia_{aluno.complet_name_aluno}.pdf"'

    return response