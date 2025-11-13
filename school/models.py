from django.db import models
from .validators import validar_telefone, validar_cpf, validar_cpf_model
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import os
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F

# Função usada por migrations antigas para definir data fim padrão de suspensões
def get_default_data_fim():
    return datetime.now() + timedelta(days=7)

# Create your models here.
class Responsavel(models.Model):
    complet_name = models.CharField(max_length=50, verbose_name= "Nome completo do responsável")
    phone_number = models.CharField(max_length=11, validators=[validar_telefone], verbose_name= "Telefone xxxxxxxxxxx")
    email = models.EmailField(max_length=100, verbose_name= "Email do responsável")
    cpf = models.CharField(max_length=11, unique=True, validators= [validar_cpf], verbose_name= "CPF do responsável")
    birthday = models.DateField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Referência ao modelo de usuário configurado
        on_delete=models.CASCADE,  # O que acontece se o usuário for deletado (ex: CASCADE deleta o aluno também)
        related_name='responsavel',# Nome reverso para acessar de User para Aluno (opcional, mas útil)
        null=True,                 # Permite que o campo seja nulo, se não for obrigatório
        blank=True                 # Permite que o campo fique em branco no admin/formulários
    )

    def __str__(self):
        return self.complet_name
    

class Aluno(models.Model):
    ANO_CHOICES = (
        ("1A", "1° ano A"),
        ("1B", "1° ano B"),
        ("1C", "1° ano C"),
        ("2CN", "2° ano CN"),
        ("2DS", "2° ano DS"),
        ("2JG", "2° ano JOGOS"),
        ("3CN", "3° ano CN"),
        ("3DS", "3° ano DS"),
        ("3JG", "3° ano JOGOS"),
    )

    # Informações do aluno, como telefone, matrícula, email, CPF e data de nascimento
    complet_name_aluno = models.CharField(max_length=100, verbose_name= "Nome completo do aluno")
    # Relação com o responsável
    responsavel= models.ForeignKey(Responsavel, on_delete=models.CASCADE, related_name="complet_name_aluno")
    phone_number_aluno = models.CharField(max_length=11, validators=[validar_telefone], verbose_name= "Telefone xxxxxxxxxxx")
    matricula_aluno= models.CharField(max_length=50, verbose_name = "Matrícula do aluno")
    email_aluno = models.EmailField(max_length=100, verbose_name= "Email do aluno")
    cpf_aluno = models.CharField(max_length=11, unique=True, validators= [validar_cpf], verbose_name= "CPF do aluno")
    birthday_aluno = models.DateField()
    # Alterando para ForeignKey para Turmas
    class_choices = models.ForeignKey('Turmas', on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Turma do aluno")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Referência ao modelo de usuário configurado
        on_delete=models.CASCADE,  # O que acontece se o usuário for deletado (ex: CASCADE deleta o aluno também)
        related_name='aluno',      # Nome reverso para acessar de User para Aluno (opcional, mas útil)
        null=True,                 # Permite que o campo seja nulo, se não for obrigatório
        blank=True                 # Permite que o campo fique em branco no admin/formulários
    )

    def __str__(self):
        # Retorna o nome completo do aluno para exibição
        return self.complet_name_aluno

    def media_notas(self):
        # Calcula a média das notas do aluno usando agregação
        return self.notas.aggregate(media=models.Avg('nota'))['media']

    def total_faltas(self):
        return self.faltas.filter(status='F').count()

    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Aluno"

# Modelo para registrar faltas/presenças
from django.conf import settings
# Modelo para registrar faltas/presenças

class Falta(models.Model):
    STATUS_CHOICES = (
        ('P', 'Presente'),
        ('F', 'Faltou'),
    )
    data = models.DateField(verbose_name="Data da chamada")
    turma = models.ForeignKey('Turmas', on_delete=models.CASCADE, related_name="faltas")
    aluno = models.ForeignKey('Aluno', on_delete=models.CASCADE, related_name="faltas")
    professor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False, verbose_name="Professor responsável", limit_choices_to={'is_staff': True})
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, verbose_name="Presença/Falta", default='P')
    observacao = models.TextField(blank=True, null=True, verbose_name="Observação sobre a falta")

    class Meta:
        unique_together = ('data', 'turma', 'aluno')
        verbose_name = "Falta"
        verbose_name_plural = "Faltas"

    def __str__(self):
        return f"{self.data} - {self.turma} - {self.aluno}: {self.get_status_display()}"
    ''
class Advertencia(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name="advertencias")
    data = models.DateField()
    motivo = models.TextField(verbose_name="Motivo da advertência")


    def advertencia_pdf_link(self, obj):
        from django.utils.html import format_html
        from django.urls import reverse
        if obj.id:
            url = reverse('gerar_advertencia_pdf', args=[obj.id])
            return format_html(f'<a class="button" href="{url}" target="_blank">📄 Gerar Advertência</a>')
        return "-"
    advertencia_pdf_link.short_description = "Advertência em PDF"


class AlunoNotas(Aluno):
    class Meta:
        # Define como proxy para visualização de notas por aluno
        proxy = True
        verbose_name = "Notas por Aluno"
        verbose_name_plural = "Notas por Aluno"
          
class Turmas (models.Model):
    # Opções de turma (ano escolar)
    TURMA_CHOICES = [
        ('1°', '1° ano'),
        ('2°', '2° ano'),
        ('3°', '3° ano'),
    ]
    # Opções de itinerário formativo
    ITINERARIO_CHOICES =[
        ('N', 'Nenhum'),
        ('CN', 'Ciências da Natureza'),
        ('DS', 'Desenvolvimento de Sistemas'),
        ('DJ', 'DEsenvolvimento de Jogos'),
    ]

    # informações da turma, como nome, itinerário, professor padrinho e representante	
    class_name = models.CharField(max_length=50, choices=TURMA_CHOICES, verbose_name="Turma " )
    itinerary_name = models.CharField(max_length=50, choices=ITINERARIO_CHOICES, verbose_name="Itinerário a qual essa turma pertence")
    godfather_prof = models.CharField(max_length=50, verbose_name="Professor padrinho da turma")
    class_representante = models.CharField(max_length=50, verbose_name="Representante da turma")


    def __str__(self):
        # Retorna a identificação da turma e itinerário
        return self.class_name + "" + self.itinerary_name
    
    class Meta:
        verbose_name = "Turma"
        verbose_name_plural = "Turma"
    
class Materia(models.Model):
    # Opções de matérias/disciplina
    MATERIA_CHOICES = (
        ("DS", "Desenvolvimento de Sistemas"),
        ("CN", "Ciencias da Natureza"),
        ("DJ", "Desenvolvimento de Jogos"),
        ("MAT", "Matematica"),
        ("CH", "Ciencias Humanas"),
        ("LG", "Linguagens")    
    )
    # Nome da matéria/disciplina
    name_subject = models.CharField(max_length=50, choices=MATERIA_CHOICES, verbose_name="Selecione a Materia desejada")

    def __str__(self):
        # Retorna o nome da matéria para exibição
        return self.name_subject
    
    class Meta:
        verbose_name = "Disciplina"
        verbose_name_plural = "Disciplina"
    
class Professor(models.Model):
    # informações do professor, como nome completo, matéria lecionada, telefone, matrícula, email, CPF e data de nascimento
    complet_name_prof = models.CharField(max_length=50, verbose_name= "Nome completo do professor", null=True)
    materia_prof = models.CharField(max_length=50, verbose_name= "Matéria lecionada pelo professor")
    phone_number_prof = models.CharField(max_length=11, validators= [validar_telefone], verbose_name= "Telefone xxxxxxxxxxx")
    matricula_prof= models.CharField(max_length=50, verbose_name = "Matrícula do professor")
    email_prof = models.EmailField(max_length=100, verbose_name= "Email do professor")
    cpf_prof = models.CharField(max_length=11, unique=True, validators= [validar_cpf], verbose_name= "CPF do professor", blank= False, null=True)
    # Associação opcional com o usuário do Django para permissões e login
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='professor_profile')
    birthday_prof = models.DateField(max_length=10, verbose_name= "data de nascimentp do professor")
    # Relação com a matéria (objeto Materia)
    subject_choice= models.ForeignKey(Materia, on_delete=models.CASCADE, related_name="materia", blank=False, null=True)
    # Relação com a turma (objeto Turmas)
    class_choices = models.ForeignKey(Turmas, on_delete=models.CASCADE, related_name="padrinho", blank=False, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Referência ao modelo de usuário configurado
        on_delete=models.CASCADE,  # O que acontece se o usuário for deletado (ex: CASCADE deleta o aluno também)
        related_name='professor',  # Nome reverso para acessar de User para Aluno (opcional, mas útil)
        null=True,                 # Permite que o campo seja nulo, se não for obrigatório
        blank=True                 # Permite que o campo fique em branco no admin/formulários
    )

    def __str__(self):
        # Retorna o nome completo do professor para exibição
        return self.complet_name_prof
    
    class Meta:
        verbose_name = "Professor"
        verbose_name_plural = "Professor"
    
class Contrato(models.Model):
    # Relação com o aluno
    aluno = models.ForeignKey('Aluno', on_delete=models.CASCADE)
    # Indica se o contrato foi assinado
    contrato_assinado = models.BooleanField(default=False, verbose_name="Contrato Assinado")
    # Arquivo do contrato assinado (upload)
    arquivo_assinado = models.FileField(upload_to='contratos_assinados/', blank=True, null=True, verbose_name="Arquivo do Contrato Assinado")

    def __str__(self):
        # Retorna uma string identificando o contrato pelo nome do aluno
        return f"Contrato de {self.aluno.complet_name_aluno}"

    class Meta:
        verbose_name = "Contrato"
        verbose_name_plural = "Contrato"
    
    
class Nota(models.Model):
    # Relação com o aluno
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='notas')
    # Relação com a matéria
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='notas')

    # Bimestre da nota
    BIMESTRE_CHOICES = [
        (1, '1º Bimestre'),
        (2, '2º Bimestre'),
        (3, '3º Bimestre'),
        (4, '4º Bimestre'),
    ]
    bimestre = models.PositiveSmallIntegerField(choices=BIMESTRE_CHOICES, verbose_name='Bimestre', null=True)

    # Valor da nota
    nota = models.DecimalField(max_digits=5, decimal_places=2)
    # Observação opcional sobre a nota
    observacao = models.TextField(blank=True, null=True)
    # Data de lançamento da nota (preenchida automaticamente)
    data_lancamento = models.DateField(auto_now_add=True)

    def __str__(self):
        # Retorna uma string com nome do aluno, matéria e nota
        return f"{self.aluno.complet_name_aluno} - {self.materia.name_subject}: {self.nota}"
    
    
    class Meta:
        verbose_name = "Nota"
        verbose_name_plural = "Nota"


class Material(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome do material")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    quantidade = models.PositiveIntegerField(default=0, verbose_name="Quantidade disponível")
    local = models.CharField(max_length=100, blank=True, null=True, verbose_name="Local de armazenamento")

    def __str__(self):
        return f"{self.nome} — {self.quantidade} disponíveis"

    class Meta:
        verbose_name = "Material"
        verbose_name_plural = "Materiais"


class MaterialMovimentacao(models.Model):
    TIPO = (
        ('ENTRADA', 'Entrada'),
        ('SAIDA', 'Saída'),
    )
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='movimentacoes')
    tipo = models.CharField(max_length=10, choices=TIPO)
    quantidade = models.PositiveIntegerField()
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    data = models.DateTimeField(auto_now_add=True)
    observacao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.material.nome} - {self.tipo} {self.quantidade} em {self.data.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name = "Movimentação de Material"
        verbose_name_plural = "Movimentações de Materiais"

    def save(self, *args, **kwargs):
        # Validação e ajuste do estoque do material automaticamente
        # Chamamos full_clean() para garantir validações de campo/modelo
        self.full_clean()

        # Somente no momento de criação aplicamos a alteração no estoque.
        # Usamos transação + select_for_update para evitar condições de corrida.
        if not self.pk:
            with transaction.atomic():
                mat = Material.objects.select_for_update().get(pk=self.material_id)
                if self.tipo == 'SAIDA':
                    # tentativa de decremento condicional: só atualiza se houver quantidade suficiente
                    updated = Material.objects.filter(pk=mat.pk, quantidade__gte=self.quantidade).update(quantidade=F('quantidade') - self.quantidade)
                    if updated == 0:
                        # nenhum registro atualizado -> estoque insuficiente
                        raise ValidationError({'quantidade': 'Quantidade para saída maior que a disponível.'})
                else:
                    Material.objects.filter(pk=mat.pk).update(quantidade=F('quantidade') + self.quantidade)
                super().save(*args, **kwargs)
                # Atualiza instância relacionada
                self.material.refresh_from_db()
        else:
            # Para edição simples, apenas salva (não recalcula estoque aqui)
            super().save(*args, **kwargs)

    def clean(self):
        # Validação adicional: não permitir retirada maior que o disponível
        if self.tipo == 'SAIDA' and self.material is not None:
            # Se a movimentação já existe (edição), considere o estado atual do DB
            current_qty = self.material.quantidade
            if self.pk:
                # Ao editar, buscamos o valor atual no DB para evitar inconsistências
                try:
                    current_qty = Material.objects.get(pk=self.material_id).quantidade
                except Material.DoesNotExist:
                    current_qty = 0
            if self.quantidade > current_qty:
                raise ValidationError({'quantidade': 'Quantidade para saída maior que a disponível.'})


class Sala(models.Model):
    TIPO = (
        ('SALA', 'Sala comum'),
        ('LAB', 'Laboratório'),
    )
    nome = models.CharField(max_length=100, unique=True, verbose_name='Nome da sala/laboratório')
    tipo = models.CharField(choices=TIPO, default='SALA', max_length=10)
    capacidade = models.PositiveIntegerField(default=30)

    def __str__(self):
        return f"{self.nome} ({self.capacidade})"

    class Meta:
        verbose_name = 'Sala'
        verbose_name_plural = 'Salas'


class Reserva(models.Model):
    sala = models.ForeignKey('Sala', on_delete=models.CASCADE, related_name='reservas')
    data = models.DateField(verbose_name='Data da reserva')
    hora_inicio = models.TimeField(verbose_name='Hora início')
    hora_fim = models.TimeField(verbose_name='Hora fim')
    observacao = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    professor = models.ForeignKey(User, limit_choices_to={'is_staff': True}, null=True, on_delete=models.SET_NULL)
    turma = models.ForeignKey('Turmas', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-data', 'hora_inicio']
        unique_together = (('sala', 'data', 'hora_inicio', 'hora_fim'),)

    def clean(self):
        # verifica conflito simples de horários
        conflicts = self.__class__.objects.filter(sala=self.sala, data=self.data).exclude(pk=self.pk)
        for r in conflicts:
            if (self.hora_inicio < r.hora_fim) and (r.hora_inicio < self.hora_fim):
                raise ValidationError('Intervalo de horário conflita com outra reserva para esta sala.')

    def __str__(self):
        return f"{self.sala.nome} - {self.data} {self.hora_inicio}-{self.hora_fim}"


class Recurso(models.Model):
    TIPO_RECURSO = (
        ('LIVRO', 'Livro'),
        ('COMPUTADOR', 'Computador'),
        ('OUTRO', 'Outro'),
    )
    nome = models.CharField(max_length=200, verbose_name='Nome do recurso')
    tipo = models.CharField(max_length=20, choices=TIPO_RECURSO, default='OUTRO')
    descricao = models.TextField(blank=True, null=True)
    quantidade = models.PositiveIntegerField(default=0, verbose_name='Quantidade disponível')
    local = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.nome} — {self.quantidade} disponíveis"

    class Meta:
        verbose_name = 'Recurso'
        verbose_name_plural = 'Recursos'


class Emprestimo(models.Model):
    recurso = models.ForeignKey(Recurso, on_delete=models.CASCADE, related_name='emprestimos')
    quantidade = models.PositiveIntegerField()
    # quem pegou: preferir Aluno/Professor quando possível
    aluno = models.ForeignKey('Aluno', on_delete=models.SET_NULL, blank=True, null=True, related_name='emprestimos')
    professor = models.ForeignKey('Professor', on_delete=models.SET_NULL, blank=True, null=True, related_name='emprestimos')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    nome_beneficiario = models.CharField(max_length=200, blank=True, null=True, verbose_name='Nome do beneficiário (opcional)')
    data_emprestimo = models.DateTimeField(auto_now_add=True)
    data_devolucao_prevista = models.DateField(blank=True, null=True)
    retornado = models.BooleanField(default=False)
    data_devolucao = models.DateTimeField(blank=True, null=True)
    observacao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.recurso.nome} x{self.quantidade} para {self.nome_beneficiario or self.aluno or self.professor or self.usuario}"

    class Meta:
        verbose_name = 'Empréstimo'
        verbose_name_plural = 'Empréstimos'

    def clean(self):
        # validações básicas
        # garante que quantidade foi informada
        if self.quantidade is None:
            raise ValidationError({'quantidade': 'Quantidade é obrigatória.'})
        if self.quantidade <= 0:
            raise ValidationError({'quantidade': 'Quantidade deve ser maior que zero.'})
        # valida disponibilidade do recurso para empréstimo
        if hasattr(self, 'recurso') and self.recurso is not None:
            available = self.recurso.quantidade
            # se for edição e o empréstimo anterior não estava devolvido,
            # o estoque atual já refletirá essa dedução; portanto somamos de volta
            if self.pk:
                try:
                    prev = Emprestimo.objects.get(pk=self.pk)
                except Emprestimo.DoesNotExist:
                    prev = None
                if prev and not prev.retornado:
                    available = self.recurso.quantidade + (prev.quantidade or 0)
            if self.quantidade > available:
                raise ValidationError({'quantidade': 'Quantidade para empréstimo maior que a disponível.'})

    def save(self, *args, **kwargs):
        # valida e ajusta estoque de recurso
        self.full_clean()
        with transaction.atomic():
            if not self.pk:
                # criação: decrementar estoque do recurso se houver quantidade suficiente
                updated = Recurso.objects.filter(pk=self.recurso_id, quantidade__gte=self.quantidade).update(quantidade=F('quantidade') - self.quantidade)
                if updated == 0:
                    raise ValidationError({'quantidade': 'Quantidade para empréstimo maior que a disponível.'})
                super().save(*args, **kwargs)
            else:
                prev = Emprestimo.objects.select_for_update().get(pk=self.pk)
                # se mudou de recurso
                if prev.recurso_id != self.recurso_id:
                    # retornar quantidade para recurso antigo se ainda não devolvido
                    if not prev.retornado:
                        Recurso.objects.filter(pk=prev.recurso_id).update(quantidade=F('quantidade') + prev.quantidade)
                    # debitar novo recurso
                    updated = Recurso.objects.filter(pk=self.recurso_id, quantidade__gte=self.quantidade).update(quantidade=F('quantidade') - self.quantidade)
                    if updated == 0:
                        raise ValidationError({'quantidade': 'Quantidade para empréstimo maior que a disponível no novo recurso.'})
                else:
                    # mesmo recurso: lidar com alterações de quantidade e com devolução
                    if not prev.retornado and self.retornado:
                        # devolução: repõe o estoque
                        Recurso.objects.filter(pk=self.recurso_id).update(quantidade=F('quantidade') + prev.quantidade)
                        self.data_devolucao = kwargs.get('force_now') or datetime.now()
                    elif prev.retornado and not self.retornado:
                        # estava devolvido, agora re-emprestando: precisa debitar estoque
                        updated = Recurso.objects.filter(pk=self.recurso_id, quantidade__gte=self.quantidade).update(quantidade=F('quantidade') - self.quantidade)
                        if updated == 0:
                            raise ValidationError({'quantidade': 'Quantidade para empréstimo maior que a disponível.'})
                    else:
                        # sem mudança de status devolução: ajustar pelo delta de quantidade
                        if not prev.retornado and not self.retornado:
                            diff = self.quantidade - prev.quantidade
                            if diff > 0:
                                updated = Recurso.objects.filter(pk=self.recurso_id, quantidade__gte=diff).update(quantidade=F('quantidade') - diff)
                                if updated == 0:
                                    raise ValidationError({'quantidade': 'Quantidade adicional para empréstimo maior que a disponível.'})
                            elif diff < 0:
                                Recurso.objects.filter(pk=self.recurso_id).update(quantidade=F('quantidade') + (-diff))
                super().save(*args, **kwargs)


class PlanejamentoSemanal(models.Model):
    """Planejamento semanal de aulas preenchido pelo professor.

    Cada instância representa a semana que começa em `semana_inicio`.
    Os campos segunda->sexta armazenam o planejamento (texto/atividades) para cada dia.
    """
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name='planejamentos')
    turma = models.ForeignKey('Turmas', on_delete=models.SET_NULL, blank=True, null=True, related_name='planejamentos')
    semana_inicio = models.DateField(verbose_name='Data (início da semana)')
    segunda = models.TextField(blank=True, null=True, verbose_name='Segunda')
    terca = models.TextField(blank=True, null=True, verbose_name='Terça')
    quarta = models.TextField(blank=True, null=True, verbose_name='Quarta')
    quinta = models.TextField(blank=True, null=True, verbose_name='Quinta')
    sexta = models.TextField(blank=True, null=True, verbose_name='Sexta')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Planejamento Semanal'
        verbose_name_plural = 'Planejamentos Semanais'
        unique_together = (('professor', 'semana_inicio', 'turma'),)

    def __str__(self):
        turma_label = f' - {self.turma}' if self.turma else ''
        return f'{self.professor.complet_name_prof} — semana {self.semana_inicio}{turma_label}'

    def save(self, *args, **kwargs):
        # normaliza semana_inicio para a segunda-feira da mesma semana
        if self.semana_inicio:
            weekday = self.semana_inicio.weekday()  # Monday == 0
            if weekday != 0:
                self.semana_inicio = self.semana_inicio - timedelta(days=weekday)
        super().save(*args, **kwargs)
        # após salvar, gere o PDF/HTML com o planejamento
        try:
            self.generate_planejamento_document()
        except Exception:
            # não bloquear o save em caso de erro na geração do documento
            pass

    arquivo_pdf = models.FileField(upload_to='planejamentos_pdf/', null=True, blank=True)

    def generate_planejamento_document(self):
        """Gera um documento (PDF quando possível) representando o quadro semanal.

        Tenta usar WeasyPrint para gerar PDF; se não disponível, salva um arquivo HTML.
        """
        from django.core.files.base import ContentFile
        from django.core.files.storage import default_storage
        from django.utils.html import escape

        # coletar itens por dia e ordem
        dias = ['segunda', 'terca', 'quarta', 'quinta', 'sexta']
        items_by_day = {d: [] for d in dias}
        for item in self.itens.order_by('dia', 'ordem'):
            items_by_day[item.dia].append(item)

        # calcular máximo de linhas (ordens) para montar a tabela
        max_rows = max((len(items_by_day[d]) for d in dias), default=0)

        # montar HTML simples
        html = ['<html><head><meta charset="utf-8"><style>table{border-collapse:collapse;width:100%;}td,th{border:1px solid #444;padding:8px;vertical-align:top;}th{background:#f0f0f0}</style></head><body>']
        html.append(f'<h2>Planejamento semanal - {escape(str(self.professor))} - semana {self.semana_inicio}</h2>')
        html.append('<table>')
        # cabeçalho dias
        html.append('<tr>')
        for d in dias:
            label = d.capitalize()
            html.append(f'<th>{label}</th>')
        html.append('</tr>')

        for row in range(max_rows):
            html.append('<tr>')
            for d in dias:
                if row < len(items_by_day[d]):
                    it = items_by_day[d][row]
                    materia = escape(it.materia.name_subject if it.materia else '')
                    conteudo = escape(it.conteudo or '')
                    html.append(f'<td><strong>{materia}</strong><div>{conteudo}</div></td>')
                else:
                    html.append('<td></td>')
            html.append('</tr>')

        html.append('</table></body></html>')
        html_str = '\n'.join(html)

        # tentar gerar PDF via weasyprint
        try:
            from weasyprint import HTML
            pdf_bytes = HTML(string=html_str).write_pdf()
            filename = f'planejamento_{self.pk}.pdf'
            self.arquivo_pdf.save(filename, ContentFile(pdf_bytes), save=False)
            super().save(update_fields=['arquivo_pdf'])
            return
        except Exception:
            # fallback: salvar HTML
            filename = f'planejamento_{self.pk}.html'
            self.arquivo_pdf.save(filename, ContentFile(html_str.encode('utf-8')), save=False)
            super().save(update_fields=['arquivo_pdf'])
        

class PlanejamentoItem(models.Model):
    DIAS = (
        ('segunda', 'Segunda'),
        ('terca', 'Terça'),
        ('quarta', 'Quarta'),
        ('quinta', 'Quinta'),
        ('sexta', 'Sexta'),
    )
    planejamento = models.ForeignKey(PlanejamentoSemanal, on_delete=models.CASCADE, related_name='itens')
    dia = models.CharField(max_length=10, choices=DIAS)
    ordem = models.PositiveSmallIntegerField(default=1)
    materia = models.ForeignKey('Materia', on_delete=models.SET_NULL, blank=True, null=True)
    conteudo = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ('dia', 'ordem')

    def __str__(self):
        return f'{self.get_dia_display()} #{self.ordem} - {self.materia or "(sem matéria)"}'
    
class Suspensao(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='suspensoes')
    turma = models.ForeignKey(Turmas, on_delete=models.CASCADE, related_name='suspensoes')
    data_inicio = models.DateField(verbose_name='Data de início')
    data_fim = models.DateField(blank=True, null=True, verbose_name='Data de fim (opcional)')
    motivo = models.TextField(verbose_name='Motivo da suspensão')
    criado_por = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Suspensão: {self.aluno} - {self.turma} ({self.data_inicio})"

    class Meta:
        verbose_name = 'Suspensão'
        verbose_name_plural = 'Suspensões'

class CalendarioAcademico(models.Model):
    TIPO_EVENTO_CHOICES = [
        ('prova', 'Prova'),
        ('feriado', 'Feriado'),
        ('evento', 'Evento'),
        ('entrega_trabalho', 'Entrega de Trabalho'),
        ('outros', 'Outros'),
    ]
    titulo = models.CharField(max_length=200, verbose_name="Título do Evento")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_fim = models.DateField(blank=True, null=True, verbose_name="Data de Término")
    tipo_evento = models.CharField(max_length=50, choices=TIPO_EVENTO_CHOICES, verbose_name="Tipo de Evento")
    turma = models.ForeignKey('Turmas', on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Turma (opcional)")

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Evento do Calendário Acadêmico"
        verbose_name_plural = "Eventos do Calendário Acadêmico"

class AgendaProfessor(models.Model):
    TIPO_ATIVIDADE_CHOICES = [
        ('aula', 'Aula'),
        ('reuniao', 'Reunião'),
        ('correcao_provas', 'Correção de Provas'),
        ('outros', 'Outros'),
    ]
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, verbose_name="Professor")
    titulo = models.CharField(max_length=200, verbose_name="Título da Atividade")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    data = models.DateField(verbose_name="Data da Atividade")
    hora_inicio = models.TimeField(verbose_name="Hora de Início")
    hora_fim = models.TimeField(blank=True, null=True, verbose_name="Hora de Término")
    tipo_atividade = models.CharField(max_length=50, choices=TIPO_ATIVIDADE_CHOICES, verbose_name="Tipo de Atividade")

    def __str__(self):
        return f"{self.titulo} - {self.professor.complet_name_prof}"

    class Meta:
        verbose_name = "Agenda do Professor"
        verbose_name_plural = "Agendas dos Professores"

class Notificacao(models.Model):
    TIPO_NOTIFICACAO_CHOICES = [
        ('evento_proximo', 'Evento Próximo'),
        ('atividade_proxima', 'Atividade Próxima'),
        ('lembrete', 'Lembrete'),
    ]
    
    titulo = models.CharField(max_length=200, verbose_name="Título da Notificação")
    mensagem = models.TextField(verbose_name="Mensagem")
    tipo = models.CharField(max_length=50, choices=TIPO_NOTIFICACAO_CHOICES, verbose_name="Tipo de Notificação")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_envio = models.DateTimeField(blank=True, null=True, verbose_name="Data de Envio")
    enviada = models.BooleanField(default=False, verbose_name="Notificação Enviada")
    
    # Relacionamentos opcionais para identificar o que gerou a notificação
    evento_calendario = models.ForeignKey(CalendarioAcademico, on_delete=models.CASCADE, blank=True, null=True)
    atividade_professor = models.ForeignKey(AgendaProfessor, on_delete=models.CASCADE, blank=True, null=True)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
        ordering = ['-data_criacao']

    class InscricaoEvento(models.Model):
    # Relacionamento com o evento
        evento = models.ForeignKey('CalendarioAcademico', on_delete=models.CASCADE, related_name='inscricoes')
        # Relacionamento com o aluno
        aluno = models.ForeignKey('Aluno', on_delete=models.CASCADE, related_name='inscricoes_eventos')
        data_inscricao = models.DateTimeField(auto_now_add=True)
        status_choices = (
            ('CONFIRMADO', 'Confirmado'),
            ('CANCELADO', 'Cancelado'),
            ('LISTA_ESPERA', 'Lista de Espera'),
        )
        status = models.CharField(max_length=20, choices=status_choices, default='CONFIRMADO', verbose_name='Status da Inscrição')

    class Meta:
        verbose_name = 'Inscrição em Evento'
        verbose_name_plural = 'Inscrições em Eventos'
        unique_together = ('evento', 'aluno') 

    def __str__(self):
        return f'{self.aluno.complet_name_aluno} em {self.evento.titulo}'
    
class Notificacao(models.Model):
    TIPO_NOTIFICACAO_CHOICES = [
        ('evento_proximo', 'Evento Próximo'),
        ('atividade_proxima', 'Atividade Próxima'),
        ('lembrete', 'Lembrete'),
    ]
    
    titulo = models.CharField(max_length=200, verbose_name="Título da Notificação")
    mensagem = models.TextField(verbose_name="Mensagem")
    tipo = models.CharField(max_length=50, choices=TIPO_NOTIFICACAO_CHOICES, verbose_name="Tipo de Notificação")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_envio = models.DateTimeField(blank=True, null=True, verbose_name="Data de Envio")
    enviada = models.BooleanField(default=False, verbose_name="Notificação Enviada")
    
    # Relacionamentos opcionais para identificar o que gerou a notificação
    evento_calendario = models.ForeignKey('CalendarioAcademico', on_delete=models.CASCADE, blank=True, null=True)
    atividade_professor = models.ForeignKey('AgendaProfessor', on_delete=models.CASCADE, blank=True, null=True)
    professor = models.ForeignKey('Professor', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
        ordering = ['-data_criacao']
        # 🚨 APAGUE QUALQUER LINHA unique_together QUE ESTIVER AQUI.
        # EX: SE ESTIVER 'unique_together = (('aluno', 'evento'),)', REMOVA!