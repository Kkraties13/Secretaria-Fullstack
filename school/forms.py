from django import forms
from .models import Contrato, Suspensao


# Formulário para marcar o contrato como assinado
class ContratoAssinadoForm(forms.ModelForm):
    class Meta:
        # Define o modelo associado ao formulário
        model = Contrato
        # Campos que serão exibidos no formulário
        fields = ['contrato_assinado']


# Formulário para registrar suspensão
class SuspensaoForm(forms.ModelForm):
    class Meta:
        model = Suspensao
        fields = ['aluno', 'turma', 'data_inicio', 'data_fim', 'motivo']
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'type': 'date'}),
            'motivo': forms.Textarea(attrs={'rows': 4}),
        }