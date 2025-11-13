import io
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg 
from django.utils import timezone 
from weasyprint import HTML 

# Importações de Modelos e Forms
from .models import Aluno, Turmas, Nota, Materia, Falta, Responsavel, Suspensao
from django.db.models import Q
from .forms import SuspensaoForm
from .utils.graphs import gerar_grafico_barras

# 🚨 CONSTANTES NECESSÁRIAS PARA TODAS AS VIEWS
BIMESTRE_CHOICES = [(1, '1º Bimestre'), (2, '2º Bimestre'), (3, '3º Bimestre'), (4, '4º Bimestre')]
BIMESTRE_LABELS = {1: '1º Bimestre', 2: '2º Bimestre', 3: '3º Bimestre', 4: '4º Bimestre'}


# ------------------- CONTRATO / BOLETIM / GRÁFICOS -------------------

def gerar_contrato_pdf(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    responsavel = aluno.responsavel 
    
    context = {
        'aluno': aluno,
        'responsavel': responsavel
    }
    
    html_string = render_to_string('contrato.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="contrato_{aluno.id}.pdf"'
    
    pdf = HTML(string=html_string).write_pdf()
    response.write(pdf)
    return response


def boletim_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    
    # Constantes
    BIMESTRE_CHOICES = [(1, '1º Bimestre'), (2, '2º Bimestre'), (3, '3º Bimestre'), (4, '4º Bimestre')]
    
    notas = Nota.objects.filter(aluno=aluno).select_related('materia')
    total_faltas = aluno.faltas.filter(status='F').count()
    
    materias = list(Materia.objects.all())
    notas_dict = {m.id: {} for m in materias}
    for nota in notas:
        notas_dict[nota.materia.id][nota.bimestre] = nota
        
    materias_com_nota = []
    for materia in materias:
        materia.notas_por_bimestre = notas_dict.get(m.id, {})
        if materia.notas_por_bimestre:
            materias_com_nota.append(materia)
            
    context = {
        'aluno': aluno, 
        'materias': materias_com_nota, 
        'faltas_bimestre': total_faltas, 
        'bimestre_choices': BIMESTRE_CHOICES,
    }
    
    return render(request, 'boletim_select_bimestre.html', context)


def boletim_aluno_pdf(request, aluno_id):
    aluno = get_object_or_404(Aluno.objects.prefetch_related('notas__materia'), id=aluno_id)
    bimestre = request.GET.get('bimestre')
    
    materias = list(Materia.objects.all().only('id', 'name_subject'))
    notas = list(aluno.notas.select_related('materia').all())
    
    BIMESTRE_CHOICES = [(1, '1º Bimestre'), (2, '2º Bimestre'), (3, '3º Bimestre'), (4, '4º Bimestre')]
    meses_bimestre = {1: [1, 2, 3], 2: [4, 5, 6], 3: [8, 9], 4: [10, 11]}
    
    if bimestre:
        try:
            bimestre_int = int(bimestre)
            notas_bim = [n for n in notas if n.bimestre == bimestre_int]
            meses = meses_bimestre.get(bimestre_int, [])
            faltas_bimestre = aluno.faltas.filter(status='F', data__month__in=meses).count()
            presencas_bimestre = aluno.faltas.filter(status='P', data__month__in=meses).count()
            total_chamadas = faltas_bimestre + presencas_bimestre
            porcentagem_presenca = round((presencas_bimestre / total_chamadas) * 100, 1) if total_chamadas > 0 else None
            
            tem_alerta = any(nota.nota < 70 for nota in notas_bim)
            for materia in materias:
                materia.nota_bimestre = next((n for n in notas_bim if n.materia_id == materia.id), None)
            
            context = {
                'aluno': aluno, 'notas': notas_bim, 'faltas_bimestre': faltas_bimestre,
                'bimestre': bimestre_int, 'bimestre_choices': BIMESTRE_CHOICES, 'tem_alerta': tem_alerta,
                'materias': materias, 'porcentagem_presenca': porcentagem_presenca,
            }
            html_string = render_to_string('boletim_select_bimestre.html', context)
        except Exception:
            html_string = "<h1>Erro ao gerar PDF do boletim por bimestre.</h1>"
    else:
        # Lógica para Todos os Bimestres (Tabela consolidada)
        notas_dict = {m.id: {} for m in materias}
        for nota in notas:
            notas_dict[nota.materia.id][nota.bimestre] = nota
        materias_com_nota = [m for m in materias if notas_dict.get(m.id)]
        for m in materias_com_nota:
            m.notas_por_bimestre = notas_dict.get(m.id, {})
        
        tem_alerta = any(nota.nota < 70 for nota in notas)
        total_faltas = aluno.faltas.filter(status='F').count()
        context = {
            'aluno': aluno, 'materias': materias_com_nota, 'tem_alerta': tem_alerta,
            'bimestre': None, 'bimestre_choices': BIMESTRE_CHOICES, 'faltas_bimestre': total_faltas,
        }
        html_string = render_to_string('boletim_select_bimestre.html', context)

    pdf = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="boletim_{aluno.complet_name_aluno}.pdf"'
    
    return response


# ------------------- GRÁFICOS DE DESEMPENHO -------------------

def grafico_desempenho_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    notas = aluno.notas.all()
    
    labels = [f'{n.materia.name_subject} - {n.get_bimestre_display()}' for n in notas]
    values = [float(n.nota) for n in notas]
    cores = ['red' if v < 70 else 'skyblue' for v in values]
    
    grafico_base64 = gerar_grafico_barras(labels, values, cores, f'Desempenho de {aluno.complet_name_aluno}', 'Nota', ylim=(0, 100))
    
    context = {
        'aluno': aluno, 'notas': notas, 'tem_alerta': any(n.nota < 70 for n in notas), 
        'grafico': grafico_base64
    }
    return render(request, 'grafico_aluno.html', context) 


def relatorio_turma(request, turma_id):
    turma = get_object_or_404(Turmas, id=turma_id)
    alunos = Aluno.objects.filter(class_choices=turma)
    relatorio = []
    nomes = []
    medias = []
    cores = []
    
    for aluno in alunos:
        media = aluno.media_notas() 
        notas = Nota.objects.filter(aluno=aluno) 
        atencao = any(n.nota < 70 for n in notas)
        
        relatorio.append({'aluno': aluno, 'media': media, 'atencao': atencao})
        nomes.append(aluno.complet_name_aluno)
        medias.append(float(media) if media is not None else 0)
        cores.append('red' if atencao else 'skyblue')
    
    grafico = None
    if nomes:
        grafico = gerar_grafico_barras(nomes, medias, cores, f'Desempenho da Turma {turma.class_name}', 'Média')
    
    return render(request, 'relatorio_turma.html', {
        'turma': turma, 'relatorio': relatorio, 'grafico': grafico,
    })


def grafico_disciplina(request, materia_id):
    materia = get_object_or_404(Materia, id=materia_id)
    
    alunos_com_nota = Aluno.objects.filter(
        notas__materia=materia
    ).annotate(
        media_disciplina=Avg('notas__nota')
    ).order_by('complet_name_aluno')
    
    nomes = []
    medias = []
    cores = []
    
    for aluno in alunos_com_nota:
        nomes.append(aluno.complet_name_aluno)
        media = aluno.media_disciplina if aluno.media_disciplina is not None else 0
        medias.append(float(media))
        cores.append('red' if media < 70 else 'skyblue')

    grafico_base64 = None
    if nomes:
        grafico_base64 = gerar_grafico_barras(nomes, medias, cores, f'Desempenho em {materia.name_subject}', 'Nota Média', ylim=(0, 100))
    
    context = {'materia': materia, 'grafico': grafico_base64, 'alunos_com_nota': alunos_com_nota}
    return render(request, 'grafico_disciplina.html', context)


# ------------------- SELEÇÃO E NAVEGAÇÃO -------------------

def desempenho_aluno_select(request):
    alunos = Aluno.objects.all().order_by('complet_name_aluno')
    return render(request, 'desempenho_aluno_select.html', {'alunos': alunos})


def desempenho_turma_select(request):
    turmas = Turmas.objects.all().order_by('class_name')
    return render(request, 'desempenho_turma_select.html', {'turmas': turmas})


def desempenho_disciplina_select(request):
    materias = Materia.objects.all().order_by('name_subject')
    return render(request, 'desempenho_disciplina_select.html', {'materias': materias})


# ------------------- SUSPENSÃO -------------------

def suspensao_select_turma(request):
    turmas = Turmas.objects.all()
    return render(request, 'suspensao_select_turma.html', {'turmas': turmas})


def suspensao_select_aluno(request, turma_id):
    alunos = Aluno.objects.filter(class_choices_id=turma_id)
    turma = Turmas.objects.get(id=turma_id)
    return render(request, 'suspensao_select_aluno.html', {'alunos': alunos, 'turma': turma})


def suspensao_create(request, turma_id, aluno_id=None):
    if request.method == 'POST':
        form = SuspensaoForm(request.POST)
        if form.is_valid():
            susp = form.save(commit=False)
            if not susp.criado_por: susp.criado_por = request.user
            susp.save()
            return render(request, 'suspensao_success.html', {'suspensao': susp})
    else:
        initial = {}
        if aluno_id: initial['aluno'] = aluno_id
        if turma_id: initial['turma'] = turma_id
        form = SuspensaoForm(initial=initial)
    return render(request, 'suspensao_form.html', {'form': form})


def suspensao_list(request):
    """Lista suspensões. Opcionalmente filtra por turma via query `?turma=<id>`.
    Por padrão mostra apenas suspensões ativas (data_inicio <= hoje <= data_fim OR data_fim is null).
    """
    from datetime import date
    turma_id = request.GET.get('turma')
    mostrar_todas = request.GET.get('all') == '1'

    qs = Suspensao.objects.select_related('aluno', 'turma')
    if turma_id:
        qs = qs.filter(turma_id=turma_id)

    if not mostrar_todas:
        today = date.today()
        qs = qs.filter(data_inicio__lte=today).filter(Q(data_fim__isnull=True) | Q(data_fim__gte=today))

    suspensoes = qs.order_by('-data_inicio')
    turmas = Turmas.objects.all()
    context = {
        'suspensoes': suspensoes,
        'turmas': turmas,
        'selected_turma': int(turma_id) if turma_id else None,
        'mostrar_todas': mostrar_todas,
    }
    return render(request, 'suspensao_list.html', context)


# ------------------- CUSTOM VIEWS DE NOTAS (Para Admin) -------------------

def notas_por_aluno_select_turma(request):
    turmas = Turmas.objects.all().order_by('class_name')
    if 'turma' in request.GET:
        turma_id = request.GET['turma']
        return redirect(f"/admin/notas-por-aluno/form-batch/?turma={turma_id}")
    return render(request, 'admin/notas_por_aluno/select_turma.html', {'turmas': turmas})


def notas_por_aluno_form_batch(request):
    turma_id = request.GET.get('turma')
    turma = get_object_or_404(Turmas, id=turma_id)
    alunos = Aluno.objects.filter(class_choices=turma).order_by('complet_name_aluno')
    materias = Materia.objects.all().order_by('name_subject')
    
    mensagem = ''
    if request.method == 'POST':
        bimestre = request.POST.get('bimestre')
        for aluno in alunos:
            for materia in materias:
                nota_val = request.POST.get(f'nota_{aluno.id}_{materia.id}')
                obs_val = request.POST.get(f'obs_{aluno.id}_{materia.id}')
                if nota_val:
                    Nota.objects.update_or_create(
                        aluno=aluno,
                        materia=materia,
                        bimestre=int(bimestre),
                        defaults={
                            'nota': nota_val,
                            'observacao': obs_val,
                        }
                    )
        messages.success(request, 'Notas salvas com sucesso!')
        return redirect('admin:school_alunonotas_changelist')
        
    return render(request, 'admin/notas_por_aluno/form_notas_batch.html', {
        'turma': turma,
        'alunos': alunos,
        'materias': materias,
        'bimestre_choices': BIMESTRE_CHOICES,
        'mensagem': mensagem,
    })

def notas_por_aluno_select_aluno(request):
    turma_id = request.GET.get('turma')
    turma = get_object_or_404(Turmas, id=turma_id)
    alunos = Aluno.objects.filter(class_choices=turma).order_by('complet_name_aluno')
    if 'aluno' in request.GET:
        return redirect(f"/admin/notas-por-aluno/select-bimestre/?turma={turma_id}&aluno={request.GET['aluno']}")
    return render(request, 'admin/notas_por_aluno/select_aluno.html', {'turma': turma, 'alunos': alunos})

def notas_por_aluno_select_bimestre(request):
    turma_id = request.GET.get('turma')
    aluno_id = request.GET.get('aluno')
    turma = get_object_or_404(Turmas, id=turma_id)
    aluno = get_object_or_404(Aluno, id=aluno_id)
    if 'bimestre' in request.GET:
        return redirect(f"/admin/notas-por-aluno/form/?turma={turma_id}&aluno={aluno_id}&bimestre={request.GET['bimestre']}")
    return render(request, 'admin/notas_por_aluno/select_bimestre.html', {
        'turma': turma,
        'aluno': aluno,
        'bimestre_choices': BIMESTRE_CHOICES,
    })

def notas_por_aluno_form(request):
    turma_id = request.GET.get('turma')
    aluno_id = request.GET.get('aluno')
    bimestre = request.GET.get('bimestre')
    turma = get_object_or_404(Turmas, id=turma_id)
    aluno = get_object_or_404(Aluno, id=aluno_id)
    materias = Materia.objects.all().order_by('name_subject')
    
    bimestre_label = BIMESTRE_LABELS.get(int(bimestre), bimestre) if bimestre else 'Geral'
    
    mensagem = ''
    if request.method == 'POST':
        for materia in materias:
            nota_val = request.POST.get(f'nota_{materia.id}')
            obs_val = request.POST.get(f'obs_{materia.id}')
            if nota_val:
                Nota.objects.update_or_create(
                    aluno=aluno,
                    materia=materia,
                    bimestre=int(bimestre),
                    defaults={
                        'nota': nota_val,
                        'observacao': obs_val,
                    }
                )
        messages.success(request, 'Notas salvas com sucesso!')
        
    return render(request, 'admin/notas_por_aluno/form_notas.html', {
        'turma': turma,
        'aluno': aluno,
        'bimestre': bimestre,
        'bimestre_label': bimestre_label,
        'materias': materias,
        'mensagem': mensagem,
    })

@login_required
def listar_chamadas(request):
    chamadas = (
        Falta.objects
        .values('data')  # agrupa por data
        .annotate(total_alunos=models.Count('aluno', distinct=True))
        .order_by('-data')
    )
    
    context = {'chamadas': chamadas}
    return render(request, 'chamada_por_data.html', context)