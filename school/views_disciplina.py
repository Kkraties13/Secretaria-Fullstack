from django.shortcuts import get_object_or_404, render
from django.http import FileResponse, HttpResponse
from django.db.models import Count
from django.template.loader import render_to_string
from weasyprint import HTML # Necessário para faltas_aluno_pdf
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import io
from datetime import datetime # Para faltas_datas

# Importar modelos
from .models import Falta, Turmas, Aluno
from django.shortcuts import render
# ------------------- FALTAS DO ALUNO (HTML e PDF) -------------------

def faltas_aluno_pdf(request, aluno_id):
    """Gera o PDF com o resumo e detalhes das faltas do aluno."""
    # Assumindo que você tem o template faltas_aluno_pdf.html criado.
    
    aluno = get_object_or_404(Aluno, id=aluno_id)
    faltas = Falta.objects.filter(aluno=aluno, status='F')
    total_faltas = faltas.count()
    turma = aluno.class_choices
    
    # Calcular total de aulas (assumindo que o total de chamadas é o total de aulas)
    total_aulas = Falta.objects.filter(turma=turma).values('data').distinct().count()
    percentual = (total_faltas / total_aulas * 100) if total_aulas > 0 else 0
    passou_limite = percentual > 25
    
    html_string = render_to_string('faltas_aluno_pdf.html', {
        'aluno': aluno,
        'faltas': faltas,
        'total_faltas': total_faltas,
        'total_aulas': total_aulas,
        'percentual': round(percentual, 2),
        'passou_limite': passou_limite
    })
    
    pdf = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    # Abrir no navegador
    response['Content-Disposition'] = f'inline; filename="faltas_{aluno.complet_name_aluno}.pdf"'
    return response


def faltas_aluno(request, aluno_id):
    """Exibe a página HTML de faltas do aluno (visualização)."""
    aluno = get_object_or_404(Aluno, id=aluno_id)
    faltas = Falta.objects.filter(aluno=aluno, status='F')
    total_faltas = faltas.count()
    turma = aluno.class_choices
    
    total_aulas = Falta.objects.filter(turma=turma).values('data').distinct().count()
    percentual = (total_faltas / total_aulas * 100) if total_aulas > 0 else 0
    passou_limite = percentual > 25
    
    return render(request, 'faltas_aluno.html', {
        'aluno': aluno,
        'faltas': faltas,
        'total_faltas': total_faltas,
        'total_aulas': total_aulas,
        'percentual': round(percentual, 2),
        'passou_limite': passou_limite
    })


# ------------------- RELATÓRIOS POR TURMA (PDF) -------------------

def relatorio_faltas_pdf(request, turma_id):
    """Relatório de faltas de uma turma em PDF (ReportLab)."""
    turma = get_object_or_404(Turmas, id=turma_id)
    faltas = Falta.objects.filter(turma=turma, status='F')
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    data = [['Data', 'Aluno', 'Professor', 'Observação']]
    for falta in faltas:
        data.append([falta.data, falta.aluno.complet_name_aluno, falta.professor.username if falta.professor else '', falta.observacao or ''])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename=f'relatorio_faltas_{turma.class_name}.pdf')


def relatorio_presenca_pdf(request, turma_id):
    """Relatório de presenças de uma turma em PDF (ReportLab)."""
    turma = get_object_or_404(Turmas, id=turma_id)
    presencas = Falta.objects.filter(turma=turma, status='P')
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    data = [['Data', 'Aluno', 'Professor', 'Observação (Presença)']]
    for p in presencas: 
        data.append([
            p.data, 
            p.aluno.complet_name_aluno, 
            p.professor.username if p.professor else '', 
            p.observacao or ''
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen), 
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename=f'relatorio_presenca_{turma.class_name}.pdf')


# ------------------- RELATÓRIOS EXCEDENTES / DATAS (HTML) -------------------

def relatorio_faltas_excedidas(request):
    """Exibe uma lista de alunos que excederam o limite de faltas (25%)."""
    alunos_excedentes = []
    turmas = Turmas.objects.all()
    for turma in turmas:
        alunos = Aluno.objects.filter(class_choices=turma)
        total_aulas = Falta.objects.filter(turma=turma).values('data').distinct().count()
        for aluno in alunos:
            faltas = Falta.objects.filter(aluno=aluno, turma=turma, status='F').count()
            if total_aulas > 0 and faltas / total_aulas > 0.25:
                alunos_excedentes.append({
                    'aluno': aluno.complet_name_aluno, 'turma': turma, 'faltas': faltas,
                    'percentual': round(faltas / total_aulas * 100, 2)
                })
    return render(request, 'relatorio_faltas.html', {'alunos_excedentes': alunos_excedentes})


def faltas_datas(request):
    """Exibe as datas de chamadas salvas (para navegação)."""
    # Esta view é um placeholder para navegação, geralmente resolvida no admin,
    # mas mantida aqui para o URL.
    return render(request, 'faltas_datas.html')