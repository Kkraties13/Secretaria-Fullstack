from school.models import Aluno, Turmas

# IDs válidos de turmas
ids_validos = set(Turmas.objects.values_list('id', flat=True))

# Corrige alunos com turma inválida
total_corrigidos = 0
for aluno in Aluno.objects.all():
    if aluno.class_choices_id and aluno.class_choices_id not in ids_validos:
        aluno.class_choices = None
        aluno.save()
        print(f"Corrigido aluno {aluno.complet_name_aluno} (id={aluno.id})")
        total_corrigidos += 1

print(f"Correção concluída. {total_corrigidos} alunos corrigidos.")
