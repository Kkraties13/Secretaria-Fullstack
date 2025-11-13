"""
Módulo de relatórios de faltas e presenças.

Este módulo fornece views para gerar relatórios de presença/falta em CSV
(compatível com Excel) e em PDF (usando ReportLab). Ele inclui também uma
view para selecionar a turma antes de gerar relatórios por turma.

Notas importantes:
- CSV: gerado em memória com BOM UTF-8 para garantir compatibilidade com
    Excel. O conteúdo é servido inline (cabeçalho Content-Disposition: inline).
- PDF: gerado com ReportLab e servido inline para que o navegador exiba o
    PDF como o boletim.
- Dependências externas: reportlab (para PDF). Em versões anteriores usamos
    pandas/openpyxl para XLSX; aqui a exportação é CSV para evitar dependências
    pesadas. Se reativar uso de pandas/openpyxl, instale os pacotes.

Inputs/Outputs (contrato mínimo):
- As views recebem `request` e, quando aplicável, `turma_id`.
- Retornam `HttpResponse` (CSV) ou `FileResponse` (PDF) com conteúdo inline.

Para desenvolvedores: editar as funções abaixo com cuidado; qualquer alteração
no formato do CSV ou na tabela do PDF deve preservar o uso de `utf-8-sig`
no CSV e `Content-Disposition: inline` para experiência consistente.
"""

import io
import pandas as pd
from django.http import FileResponse, HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from .models import Falta
from .models import Turmas

def gerar_relatorio_presenca_excel(request):
    """Gera um relatório de presenças/faltas em CSV.

    Entrada:
    - request: HttpRequest (não usa parâmetros URL)

    Saída:
    - HttpResponse com content_type 'text/csv' contendo CSV UTF-8 com BOM
      (compatível com Excel). O arquivo é servido inline para permitir visualização
      direta no navegador ou abrir no Excel.

    Observações:
    - A função calcula presenças e faltas por aluno a partir do modelo `Falta`.
    - Em caso de necessidade de colunas adicionais, inclua-as no cabeçalho
      e na criação de `rows` abaixo.
    """
    # Gerar CSV em memória (compatível com Excel) — evita dependência do openpyxl
    import csv

    # Cabeçalho
    header = ["Aluno", "Presenças", "Faltas", "% Presença", "Situação"]

    # Dados
    rows = []
    alunos = Falta.objects.values('aluno__complet_name_aluno').distinct()
    for aluno in alunos:
        nome = aluno['aluno__complet_name_aluno']
        total_presencas = Falta.objects.filter(aluno__complet_name_aluno=nome, status='P').count()
        total_faltas = Falta.objects.filter(aluno__complet_name_aluno=nome, status='F').count()
        total_aulas = total_presencas + total_faltas
        porcentagem = (total_presencas / total_aulas * 100) if total_aulas > 0 else 0
        status = "Aprovado" if porcentagem >= 80 else "Reprovado"
        rows.append([nome, total_presencas, total_faltas, f"{porcentagem:.1f}%", status])

    # Escrever CSV em memória com BOM para Excel (UTF-8)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(header)
    for r in rows:
        writer.writerow(r)

    csv_data = output.getvalue().encode('utf-8-sig')
    response = HttpResponse(csv_data, content_type='text/csv; charset=utf-8')
    # Servir inline (o navegador pode abrir ou oferecer opção) — semelhante ao comportamento do boletim
    response['Content-Disposition'] = 'inline; filename="relatorio_presencas.csv"'
    return response


def relatorio_select(request):
    """Renderiza uma página com a lista de turmas para seleção.

    A seleção da turma é obrigatória antes de gerar relatórios por turma. O
    template `relatorio_select.html` deve conter links que apontam para as
    views de geração por turma (CSV/PDF).
    """
    # Página para selecionar a turma antes de gerar relatórios
    turmas = Turmas.objects.all()
    from django.shortcuts import render
    return render(request, 'relatorio_select.html', {'turmas': turmas})


def gerar_relatorio_presenca_excel_turma(request, turma_id):
    """Gera CSV de presenças/faltas filtrado por `turma_id`.

    Entrada:
    - request: HttpRequest
    - turma_id: int (pk da turma)

    Saída:
    - HttpResponse com CSV (utf-8-sig) servido inline.

    Observações:
    - Filtra faltas pela turma antes de agregar por aluno.
    """
    import csv
    header = ["Aluno", "Presenças", "Faltas", "% Presença", "Situação"]
    rows = []
    alunos = Falta.objects.filter(turma_id=turma_id).values('aluno__complet_name_aluno').distinct()
    for aluno in alunos:
        nome = aluno['aluno__complet_name_aluno']
        total_presencas = Falta.objects.filter(turma_id=turma_id, aluno__complet_name_aluno=nome, status='P').count()
        total_faltas = Falta.objects.filter(turma_id=turma_id, aluno__complet_name_aluno=nome, status='F').count()
        total_aulas = total_presencas + total_faltas
        porcentagem = (total_presencas / total_aulas * 100) if total_aulas > 0 else 0
        status = "Aprovado" if porcentagem >= 80 else "Reprovado"
        rows.append([nome, total_presencas, total_faltas, f"{porcentagem:.1f}%", status])

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(header)
    for r in rows:
        writer.writerow(r)

    csv_data = output.getvalue().encode('utf-8-sig')
    response = HttpResponse(csv_data, content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'inline; filename="relatorio_presencas_turma_{turma_id}.csv"'
    return response


def gerar_relatorio_presenca_pdf_turma(request, turma_id):
    """Gera PDF (ReportLab) do relatório de presenças/faltas para uma turma.

    Entrada:
    - request: HttpRequest
    - turma_id: int

    Saída:
    - FileResponse com PDF servido inline.

    Observações:
    - Usa ReportLab para construir uma tabela básica; estilos são aplicados
      com TableStyle. Para relatórios mais ricos, considere gerar HTML e usar
      WeasyPrint (como em outros relatórios do projeto).
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elementos = [Paragraph("Relatório de Faltas e Presenças", styles['Title']), Spacer(1, 12)]

    dados_tabela = [["Aluno", "Presenças", "Faltas", "% Presença", "Situação"]]
    alunos = Falta.objects.filter(turma_id=turma_id).values('aluno__complet_name_aluno').distinct()
    for aluno in alunos:
        nome = aluno['aluno__complet_name_aluno']
        total_presencas = Falta.objects.filter(turma_id=turma_id, aluno__complet_name_aluno=nome, status='P').count()
        total_faltas = Falta.objects.filter(turma_id=turma_id, aluno__complet_name_aluno=nome, status='F').count()
        total_aulas = total_presencas + total_faltas
        porcentagem = (total_presencas / total_aulas * 100) if total_aulas > 0 else 0
        status = "Aprovado" if porcentagem >= 80 else "Reprovado"
        dados_tabela.append([nome, total_presencas, total_faltas, f"{porcentagem:.1f}%", status])

    tabela = Table(dados_tabela, repeatRows=1)
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    elementos.append(tabela)
    doc.build(elementos)

    buffer.seek(0)
    response = FileResponse(buffer, as_attachment=False, filename=f"relatorio_presencas_turma_{turma_id}.pdf")
    response['Content-Disposition'] = f'inline; filename="relatorio_presencas_turma_{turma_id}.pdf"'
    return response


def gerar_relatorio_presenca_pdf(request):
    """Gera PDF do relatório de presenças/faltas para todas as turmas.

    Sem argumentos de turma; agrupa por aluno em todo o colégio.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elementos = [Paragraph("Relatório de Faltas e Presenças", styles['Title']), Spacer(1, 12)]
    
    dados_tabela = [["Aluno", "Presenças", "Faltas", "% Presença", "Situação"]]
    
    alunos = Falta.objects.values('aluno__complet_name_aluno').distinct()
    for aluno in alunos:
        nome = aluno['aluno__complet_name_aluno']
        total_presencas = Falta.objects.filter(aluno__complet_name_aluno=nome, status='P').count()
        total_faltas = Falta.objects.filter(aluno__complet_name_aluno=nome, status='F').count()
        total_aulas = total_presencas + total_faltas
        porcentagem = (total_presencas / total_aulas * 100) if total_aulas > 0 else 0
        status = "Aprovado" if porcentagem >= 80 else "Reprovado"
        dados_tabela.append([nome, total_presencas, total_faltas, f"{porcentagem:.1f}%", status])
    
    tabela = Table(dados_tabela, repeatRows=1)
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    
    elementos.append(tabela)
    doc.build(elementos)
    
    buffer.seek(0)
    response = FileResponse(buffer, as_attachment=False, filename="relatorio_presencas.pdf")
    # Forçar exibição inline no navegador (como feito em boletim_aluno_pdf)
    response['Content-Disposition'] = 'inline; filename="relatorio_presencas.pdf"'
    return response
