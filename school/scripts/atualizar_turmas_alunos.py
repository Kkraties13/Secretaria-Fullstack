from school.models import Turmas, Aluno

def get_or_create_turma(codigo):
    # Mapeamento dos códigos antigos para os dados das turmas
    mapa = {
        '1A': {'class_name': '1°', 'itinerary_name': 'CN'},
        '1B': {'class_name': '1°', 'itinerary_name': 'DS'},
        '1C': {'class_name': '1°', 'itinerary_name': 'DJ'},
        '2A': {'class_name': '2°', 'itinerary_name': 'CN'},
        '2B': {'class_name': '2°', 'itinerary_name': 'DS'},
        '2C': {'class_name': '2°', 'itinerary_name': 'DJ'},
        '3A': {'class_name': '3°', 'itinerary_name': 'CN'},
        '3B': {'class_name': '3°', 'itinerary_name': 'DS'},
        '3C': {'class_name': '3°', 'itinerary_name': 'DJ'},
    }
    if codigo not in mapa:
        return None
    dados = mapa[codigo]
    turma, _ = Turmas.objects.get_or_create(
        class_name=dados['class_name'],
        itinerary_name=dados['itinerary_name'],
        defaults={
            'godfather_prof': 'Padrinho',
            'class_representante': 'Representante',
        }
    )
    return turma

for aluno in Aluno.objects.all():
    turma = get_or_create_turma(aluno.class_choices)
    if turma:
        print(f"Atualizando {aluno.complet_name_aluno} para turma {turma.class_name} {turma.itinerary_name}")
        aluno.class_choices = turma.id  # Quando for ForeignKey
        aluno.save()
    else:
        print(f"Aluno {aluno.complet_name_aluno} com turma desconhecida: {aluno.class_choices}")

print("Atualização concluída. Agora altere o campo class_choices para ForeignKey e rode as migrações.")
