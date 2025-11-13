# Sistema de Gestão Escolar - app-escola

Este projeto é um sistema web desenvolvido em Django para gerenciar informações de alunos, turmas, professores, contratos, notas e desempenho escolar. Abaixo está uma explicação detalhada de cada parte do sistema, como funciona e para que serve.

## Estrutura do Projeto

- **core/**: Configurações principais do projeto Django.
  - `settings.py`: Configurações globais (banco de dados, apps instalados, arquivos estáticos, etc).
  - `urls.py`: Rotas principais do projeto, incluindo as rotas do app `school` e do admin.
  - `wsgi.py` e `asgi.py`: Arquivos para deploy.

- **school/**: App principal da escola, onde estão os modelos, views, formulários, validações e utilitários.
  - `models.py`: Define as tabelas do banco de dados:
    - **Responsavel**: Dados dos responsáveis pelos alunos.
    - **Aluno**: Dados dos alunos, vínculo com responsável e turma.
    - **Turmas**: Informações das turmas (ano, itinerário, padrinho, representante).
    - **Materia**: Disciplinas/matérias oferecidas.
    - **Professor**: Dados dos professores e suas relações com matérias e turmas.
    - **Contrato**: Controle de contratos assinados dos alunos.
    - **Nota**: Notas dos alunos por matéria.
  - `views.py`: Funções que processam as requisições e retornam páginas HTML ou PDFs:
    - Geração de contrato em PDF.
    - Exibição e geração de boletim do aluno (HTML e PDF).
    - Gráficos de desempenho do aluno, turma e disciplina.
    - Relatórios de turma.
    - Páginas de seleção para análise de desempenho.
  - `forms.py`: Formulários para interação com o usuário, como marcar contratos como assinados.
  - `validators.py`: Funções para validar CPF e telefone nos formulários e modelos.
  - `utils/graphs.py`: Função utilitária para gerar gráficos de barras em base64 para exibição nos relatórios e páginas.
  - `scripts/atualizar_turmas_alunos.py`: Script para atualizar o vínculo de alunos com turmas, útil em migrações de dados.
  - `templates/`: Páginas HTML usadas nas views, incluindo boletim, contrato, gráficos e relatórios.

- **db.sqlite3**: Banco de dados SQLite usado pelo Django.
- **manage.py**: Utilitário para comandos administrativos do Django (migrar banco, rodar servidor, criar superusuário, etc).
- **env/**: Ambiente virtual Python com dependências do projeto.

## Como Funciona

- O sistema permite cadastrar alunos, responsáveis, professores, turmas e matérias.
- É possível lançar notas para os alunos em cada disciplina.
- O sistema gera boletins e contratos em PDF.
- Gráficos de desempenho são gerados automaticamente para alunos, turmas e disciplinas, destacando notas baixas.
- Contratos assinados podem ser enviados e armazenados.
- Validações automáticas garantem a integridade dos dados (ex: CPF e telefone).

## Para que Serve

- Facilita o controle acadêmico e administrativo da escola.
- Permite análise visual do desempenho dos alunos e turmas.
- Automatiza a geração de documentos escolares.
- Centraliza informações de alunos, professores, turmas e contratos.

## Como Executar

1. Ative o ambiente virtual:
   .\env\Scripts\Activate.ps1

2. Instale as dependências (se necessário):
   pip install -r requirements.txt

3. Rode as migrações:
   python manage.py migrate

4. Crie um superusuário:
   python manage.py createsuperuser

5. Inicie o servidor:
   python manage.py runserver
   
6. Acesse o sistema em [http://localhost:8000](http://localhost:8000)

---

Este README cobre toda a estrutura, funcionamento e propósito do sistema. Para dúvidas ou contribuições, consulte o código-fonte ou entre em contato com o desenvolvedor.
