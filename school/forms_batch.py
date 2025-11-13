from django import forms

BIMESTRE_CHOICES = [
    (1, '1º Bimestre'),
    (2, '2º Bimestre'),
    (3, '3º Bimestre'),
    (4, '4º Bimestre'),
]

class BimestreBatchForm(forms.Form):
    bimestre = forms.ChoiceField(choices=BIMESTRE_CHOICES, label='Bimestre')
