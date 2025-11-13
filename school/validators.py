import re
from django.core.exceptions import ValidationError

def validar_telefone(value):
    # Remove todos os caracteres não numéricos do telefone
    telefone = re.sub(r'\D','', value)
    # Verifica se o telefone possui 10 ou 11 dígitos
    if len(telefone) not in [10,11]:
        raise ValidationError('O numero de telefone deve ter 10 ou 11 dígitos.')
    # Verifica se o telefone contém apenas números
    if not telefone.isdigit():
        raise ValidationError('O telefone deve conter apenas números.')

def validar_cpf(cpf):
    # Remove todos os caracteres que não são dígitos do CPF
    cpf = re.sub(r'[^0-9]', '', cpf)
    # Verifica se o CPF possui 11 dígitos
    if len(cpf) != 11:
        raise ValidationError('CPF inválido')
    # Verifica se todos os dígitos são iguais (CPFs como 11111111111 são inválidos)
    if len(set(cpf)) == 1:
        raise ValidationError('CPF inválido')
    soma = 0
    # Calcula o primeiro dígito verificador
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    soma = 0
    # Calcula o segundo dígito verificador
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    # Verifica se os dígitos calculados conferem com os dígitos informados
    if int(cpf[9]) != digito1 or int(cpf[10]) != digito2:
        raise ValidationError('CPF inválido')

def validar_cpf_model(value):
    # Valida o CPF e lança exceção se for inválido
    if not validar_cpf(value):
        raise ValidationError('CPF inválido')