from django.contrib import admin
from django.urls import path, re_path, reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from datetime import datetime
from django.db import transaction
from django.db.models import F
from django.http import HttpResponseRedirect, HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from weasyprint import HTML 
import csv
from django import forms
from django.utils import timezone
from datetime import datetime as dt

# Importar todos os modelos
from .models import (
    Turmas, Aluno, Materia, Nota, AlunoNotas, Recurso, Emprestimo,
    Responsavel, Falta, Advertencia, Material, MaterialMovimentacao, Suspensao,
    Professor, Contrato, Sala, Reserva, PlanejamentoSemanal
)
from .admin_attendance import AttendanceDateAdmin 

# 🚨 IMPORTAÇÕES DAS VIEWS REFATORADAS (Devem existir em views_academico.py)
from .views_academico import (
    notas_por_aluno_select_turma, 
    notas_por_aluno_select_aluno, 
    notas_por_aluno_select_bimestre, 
    notas_por_aluno_form, 
    notas_por_aluno_form_batch
)
notas_por_aluno_select_turma_alias = notas_por_aluno_select_turma


# ---------------------------------------------------------------------
# --- 1. DEFINIÇÕES DAS CLASSES ADMIN ---
# ---------------------------------------------------------------------

class NotasPorAlunoRedirectAdmin(admin.ModelAdmin):
    """Redireciona para o fluxo customizado de notas por aluno/turma."""
    def changelist_view(self, request, extra_context=None):
        return redirect('admin:notas_por_aluno_select_turma')

class AdvertenciaAdmin(admin.ModelAdmin):
    list_display = ('aluno','data', 'motivo', 'ver_pdf_link') 
    search_fields = ('aluno__complet_name_aluno', 'motivo')
    list_filter = ('data',)
    actions = ['gerar_e_enviar_documento']

    def ver_pdf_link(self, obj):
        if obj.id:
            url = reverse('school:gerar_advertencia_pdf', args=[obj.id])
            return format_html(f'<a class="button" href="{url}" target="_blank">📄 Ver PDF</a>')
        return "-"
    ver_pdf_link.short_description = "Ver PDF"
    
    def gerar_e_enviar_documento(self, request, queryset):
        for advertencia in queryset:
            html_string = render_to_string('school/documentoadvertencia_pdf.html', {'advertencia': advertencia})
            pdf = HTML(string=html_string).write_pdf()
            
            responsavel = advertencia.aluno.responsavel
            if not responsavel or not responsavel.email:
                self.message_user(request, f"Erro: Não há e-mail para o responsável de {advertencia.aluno.complet_name_aluno}.", level='ERROR')
                continue
            
            subject = f"Documento de Advertência - {advertencia.aluno.complet_name_aluno}"
            body = f"Prezado(a) {responsavel.complet_name},\n\n[Mensagem...] Data de emissão: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\nAtenciosamente,\nEquipe Escolar"
            from_email = "seuemail@exemplo.com"
            to_email = [responsavel.email]

            try:
                send_mail(subject, body, from_email, to_email, fail_silently=False, attachments=[('advertencia.pdf', pdf, 'application/pdf')])
            except Exception as e:
                self.message_user(request, f"Erro ao enviar e-mail para {responsavel.email}: {str(e)}", level='ERROR')
                continue
        self.message_user(request, "Documentos gerados e enviados com sucesso.")
    gerar_e_enviar_documento.short_description = "Gerar e Enviar Documento de Advertência"


class AlunoInline(admin.TabularInline):
    model = Aluno
    extra = 0

class ResponsaveisAdmin(admin.ModelAdmin):
    list_display = ('id', 'complet_name', 'phone_number', 'email', 'cpf', 'birthday')
    list_display_links = ('complet_name', 'phone_number', 'email')
    search_fields = ('complet_name',)
    list_filter = ('complet_name',)
    inlines = [AlunoInline]

class AlunoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'complet_name_aluno', 'responsavel', 'class_choices',
        'contrato_pdf_link', 'boletim_link', 'grafico_link', 'faltas_pdf_link'
    )
    list_display_links = ('complet_name_aluno',)
    search_fields = ('complet_name_aluno',)
    
    def contrato_pdf_link(self, obj):
        if obj.id:
            url = reverse('school:gerar_contrato_pdf', args=[obj.id])
            return format_html(f'<a class="button" href="{url}" target="_blank">📄 Gerar Contrato</a>')
        return "-"
    contrato_pdf_link.short_description = "Contrato em PDF"
    
    def boletim_link(self, obj):
        if obj.id:
            url = reverse('school:boletim_aluno_pdf', args=[obj.id])
            return format_html(f'<a href="{url}" target="_blank">📊 Ver Boletim</a>')
        return "-"
    boletim_link.short_description = "Boletim"

    def grafico_link(self, obj):
        if obj.id:
            url = reverse('school:grafico_desempenho_aluno', args=[obj.id])
            return format_html(f'<a href="{url}" target="_blank">📈 Gráfico</a>')
        return "-"
    grafico_link.short_description = "Gráfico"

    def faltas_pdf_link(self, obj):
        if obj.id:
            url = reverse('school:faltas_aluno_pdf', args=[obj.id])
            return format_html(f'<a href="{url}" target="_blank">📄 Faltas PDF</a>')
        return "-"
    faltas_pdf_link.short_description = "Faltas em PDF"


class TurmasAdmin(admin.ModelAdmin):
    list_display = ('id', 'class_name', 'itinerary_name', 'relatorio_link', 'chamada_link', 'relatorio_faltas_link', 'relatorio_presenca_link')
    search_fields = ('class_name', 'itinerary_name')
    list_filter = ('class_name', 'itinerary_name')

    # 🚨 FUNÇÃO FAZER_CHAMADA CORRIGIDA
    def fazer_chamada(self, request, turma_id):
        
        # NOTE: Todos os imports que você tinha dentro desta função
        # DEVEM estar movidos para o topo do seu admin.py.
        
        turma = get_object_or_404(Turmas, id=turma_id)
        alunos = Aluno.objects.filter(class_choices=turma).order_by('complet_name_aluno')
        
        if request.method == 'POST':
            data = request.POST.get('data')
            if not data:
                messages.error(request, 'Por favor, selecione uma data válida.')
                return redirect(request.path_info)
            
            try:
                # Usando dt (datetime as dt) conforme o que corrigimos antes
                data_obj = dt.strptime(data, '%Y-%m-%d').date() 
            except ValueError:
                messages.error(request, 'Formato de data inválido.')
                return redirect(request.path_info)
            
            erro = False
            for aluno in alunos:
                status = request.POST.get(f'status_{aluno.id}')
                if status and status not in ['P', 'F']:
                    erro = True
            
            if erro:
                messages.error(request, "Só são aceitas as letras 'P' para Presente e 'F' para Falta. Corrija os valores informados.")
                return redirect(request.path_info)
            else:
                for aluno in alunos:
                    status = request.POST.get(f'status_{aluno.id}')
                    if status in ['P', 'F']:
                        Falta.objects.update_or_create(
                            data=data_obj,
                            turma=turma,
                            aluno=aluno,
                            # timezone.now() e request.user são imports globais
                            defaults={'status': status, 'professor': request.user if request.user.is_staff else None} 
                        )
                messages.success(request, 'Chamada registrada com sucesso!')
                return redirect('admin:school_turmas_changelist') 
            
        return render(request, 'admin/fazer_chamada.html', {
            'title': f'Chamada da turma {turma.class_name}',
            'turma': turma,
            'alunos': alunos,
            'data_atual': timezone.now().date().strftime('%Y-%m-%d'),
        })

    def chamada_link(self, obj):
        """Gera o link para a view customizada de fazer chamada."""
        from django.urls import reverse
        from django.utils.html import format_html
        
        if obj.id:
            # 🚨 CORREÇÃO: Usar reverse com o nome 'admin:fazer_chamada'
            url = reverse('admin:fazer_chamada', args=[obj.id]) 
            return format_html(f'<a href="{url}">📝 Fazer Chamada</a>')
        return "-"
    chamada_link.short_description = "Chamada"

    def relatorio_link(self, obj):
        if obj.id:
            url = reverse('school:relatorio_turma', args=[obj.id])
            return format_html(f'<a href="{url}" target="_blank">📊 Relatório</a>')
        return "-"
    relatorio_link.short_description = "Relatório"

    def relatorio_faltas_link(self, obj):
        if obj.id:
            url = reverse('school:relatorio_faltas_pdf', args=[obj.id])
            return format_html(f'<a href="{url}" target="_blank">📊 Relatório Faltas</a>')
        return "-"
    relatorio_faltas_link.short_description = "Relatório Faltas"

    def relatorio_presenca_link(self, obj):
        if obj.id:
            url = reverse('school:relatorio_presenca_pdf', args=[obj.id])
            return format_html(f'<a href="{url}" target="_blank">📊 Relatório Presença</a>')
        return "-"
    relatorio_presenca_link.short_description = "Relatório Presença"

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<int:turma_id>/chamada/', self.admin_site.admin_view(self.fazer_chamada), name='fazer_chamada'),
        ]
        return custom_urls + urls


class MateriaAdmin(admin.ModelAdmin):
    list_display= ('id', 'name_subject', 'grafico_link')
    search_fields= ('name_subject',)
    list_filter= ('name_subject',)

    def grafico_link(self, obj):
        if obj.id:
            url = reverse('school:grafico_disciplina', args=[obj.id])
            return format_html(f'<a href="{url}" target="_blank">📈 Gráfico</a>')
        return "-"
    grafico_link.short_description = "Gráfico"


class ContratoAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'contrato_assinado', 'contrato_pdf_link', 'upload_contrato_assinado', 'contrato_assinado_link')
    list_filter = ('aluno', 'contrato_assinado')
    search_fields = ('aluno__complet_name_aluno',)
    autocomplete_fields = ['aluno']
    readonly_fields = ()
    fields = ('aluno',)

    def contrato_pdf_link(self, obj):
        if obj.aluno_id:
            url = reverse('school:gerar_contrato_pdf', args=[obj.aluno_id])
            return format_html(f'<a href="{url}" target="_blank">📄 Gerar Contrato</a>')
        return "-"
    contrato_pdf_link.short_description = "Contrato PDF"

    def upload_contrato_assinado(self, obj):
        if obj.id:
            url = reverse('admin:school_contrato_upload', args=[obj.id])
            return format_html(f'<a href="{url}">📤 Enviar Contrato Assinado</a>')
        return "-"
    upload_contrato_assinado.short_description = "Enviar Contrato Assinado"

    def contrato_assinado_link(self, obj):
        if obj.arquivo_assinado:
            return format_html(f'<a href="{obj.arquivo_assinado.url}" target="_blank">📥 Visualizar Contrato Assinado</a>')
        return "-"
    contrato_assinado_link.short_description = "Contrato Assinado (PDF)"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            re_path(r'^(?P<object_id>\d+)/upload/$', self.admin_site.admin_view(self.upload_view), name='school_contrato_upload'),
        ]
        return custom_urls + urls

    def upload_view(self, request, object_id):
        from django.shortcuts import redirect, get_object_or_404
        from django.contrib import messages
        from django.template.response import TemplateResponse
        obj = get_object_or_404(Contrato, pk=object_id)
        if request.method == 'POST' and request.FILES.get('arquivo_assinado'):
            obj.arquivo_assinado = request.FILES['arquivo_assinado']
            if 'contrato_assinado' in request.POST:
                obj.contrato_assinado = True
            obj.save()
            messages.success(request, 'Contrato assinado enviado com sucesso!')
            return redirect('admin:school_contrato_change', obj.id)
        context = dict(
            self.admin_site.each_context(request),
            title='Enviar Contrato Assinado', original=obj, opts=self.model._meta,
        )
        return TemplateResponse(request, 'admin/contrato_upload.html', context)


class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('id', 'complet_name_prof', 'phone_number_prof', 'email_prof', 'cpf_prof', 'birthday_prof')
    list_display_links = ('complet_name_prof', 'phone_number_prof', 'email_prof')
    search_fields = ('complet_name_prof',)
    list_filter = ('complet_name_prof',)


class RecursoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'quantidade', 'local')
    search_fields = ('nome',)

class EmprestimoAdmin(admin.ModelAdmin):
    list_display = ('recurso', 'quantidade', 'recurso_disponivel', 'nome_beneficiario', 'aluno', 'professor', 'usuario', 'data_emprestimo', 'retornado', 'data_devolucao_prevista')
    list_filter = ('retornado', 'data_emprestimo')
    search_fields = ('recurso__nome', 'nome_beneficiario', 'aluno__complet_name_aluno', 'professor__complet_name_prof')
    readonly_fields = ('recurso_disponivel',)
    actions = ['marcar_como_devolvido']
    
    class EmprestimoForm(forms.ModelForm):
        class Meta:
            model = Emprestimo
            fields = '__all__'

        def clean(self):
            cleaned = super().clean()
            recurso = cleaned.get('recurso') or getattr(self.instance, 'recurso', None)
            quantidade = cleaned.get('quantidade')
            retornado = cleaned.get('retornado') if 'retornado' in cleaned else getattr(self.instance, 'retornado', False)
            if recurso and quantidade is not None and not retornado:
                available = recurso.quantidade
                if self.instance and self.instance.pk:
                    prev = Emprestimo.objects.filter(pk=self.instance.pk).first()
                    if prev and not prev.retornado:
                        available = recurso.quantidade + (prev.quantidade or 0)
                if quantidade > available:
                    raise forms.ValidationError({'quantidade': 'Quantidade para empréstimo maior que a disponível.'})
            return cleaned

    form = EmprestimoForm
    
    def recurso_disponivel(self, obj):
        return obj.recurso.quantidade if obj and obj.recurso_id else '-'
    recurso_disponivel.short_description = 'Disponível'

    def marcar_como_devolvido(self, request, queryset):
        updated = 0
        for emprestimo in queryset.filter(retornado=False):
            with transaction.atomic():
                Recurso.objects.filter(pk=emprestimo.recurso_id).update(quantidade=F('quantidade') + emprestimo.quantidade)
                emprestimo.retornado = True
                emprestimo.data_devolucao = timezone.now()
                emprestimo.save()
                updated += 1
        messages.success(request, f'{updated} empréstimo(s) marcados como devolvidos.', level=messages.SUCCESS)
    marcar_como_devolvido.short_description = 'Marcar seleção como devolvido'

class SuspensaoAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'turma', 'data_inicio', 'data_fim', 'motivo', 'criado_por')

    def changelist_view(self, request, extra_context=None):
        """Redireciona a lista de mudanças para a view custom de seleção de turmas/alunos de suspensão."""
        from django.shortcuts import redirect
        return redirect('school:suspensao_select_turma')

# ... (Mantenha as classes para NotaInlineForm, NotaInline, AlunoNotasAdmin, PlanejamentoSemanalAdmin, MaterialAdmin, etc., omitidas por brevidade) ...

# --- 2. REGISTROS DE MODELOS ---
admin.site.register(AlunoNotas, NotasPorAlunoRedirectAdmin)
admin.site.register(Aluno, AlunoAdmin)
admin.site.register(Advertencia, AdvertenciaAdmin)
admin.site.register(Responsavel, ResponsaveisAdmin)
admin.site.register(Professor, ProfessorAdmin)
admin.site.register(Turmas, TurmasAdmin)
admin.site.register(Materia, MateriaAdmin)
admin.site.register(Contrato, ContratoAdmin)
admin.site.register(Recurso, RecursoAdmin)
admin.site.register(Emprestimo, EmprestimoAdmin)
admin.site.register(Suspensao, SuspensaoAdmin)
admin.site.register(Falta, AttendanceDateAdmin)

# --- 3. CUSTOM URLS HOOK ---

def get_custom_urls(urls):
    custom_urls = [
        # VIEWS DE NOTAS CUSTOMIZADAS
        path('notas-por-aluno/select-turma/', admin.site.admin_view(notas_por_aluno_select_turma_alias), name='notas_por_aluno_select_turma'),
        path('notas-por-aluno/select-aluno/', admin.site.admin_view(notas_por_aluno_select_aluno), name='notas_por_aluno_select_aluno'),
        path('notas-por-aluno/select-bimestre/', admin.site.admin_view(notas_por_aluno_select_bimestre), name='notas_por_aluno_select_bimestre'),
        path('notas-por-aluno/form/', admin.site.admin_view(notas_por_aluno_form), name='notas_por_aluno_form'),
        path('notas-por-aluno/form-batch/', admin.site.admin_view(notas_por_aluno_form_batch), name='notas_por_aluno_form_batch'),
        
        # URL CUSTOMIZADA DE CHAMADA (TurmasAdmin)
        #path('<int:turma_id>/chamada/', admin.site.admin_view(TurmasAdmin.fazer_chamada), name='fazer_chamada'),
    ]
    return custom_urls + urls

# Patch no admin site para incluir as novas URLs
original_get_urls = admin.site.get_urls
admin.site.get_urls = lambda: get_custom_urls(original_get_urls())

def listar_chamadas(request):
    chamadas = (
        Falta.objects
        .values('data')
        .annotate(
            total_turmas=models.Count('turma', distinct=True),
            total_alunos=models.Count('aluno', distinct=True)
        )
        .order_by('-data')
    )

    context = {'chamadas': chamadas}
    return render(request, 'admin/chamada_por_data.html', context)