# Chegada Segura — Backend Django

Backend funcional do projeto **Chegada Segura**, convertido para **Django + Django REST Framework + PostgreSQL**, mantendo o escopo apresentado nas imagens e no texto do projeto.

## Escopo

- Cadastros de alunos, responsáveis, turmas, horários e vínculos.
- Tablet supervisionado por `X-Kiosk-Key`.
- Conferência de RA + nome sem tratar isso como prova de identidade.
- Funcionário autenticado confirma a chegada.
- Horário sempre definido pelo servidor.
- Regra de atraso por turma: horário de início + tolerância.
- Uma ocorrência por aluno por data escolar.
- Fila de WhatsApp com tentativas, pendências, falhas e backoff.
- Webhook para `sent`, `delivered`, `read` e `failed`.
- Painel diário/mensal com ocorrências e estudantes distintos separados.
- Distribuição por turma/turno e evolução diária.
- Histórico individual restrito à direção/administração.
- Correção/cancelamento com autor, data, justificativa e antes/depois.
- Auditoria.
- Autenticação JWT e controle por papel.
- Testes automatizados.
- Docker/PostgreSQL.

## Stack

- Python 3.13
- Django 5.2+
- Django REST Framework
- SimpleJWT
- PostgreSQL
- Requests para WhatsApp Cloud API
- pytest/pytest-django

## Rodando com Docker

```bash
copy .env.example .env
```

No Linux/macOS:

```bash
cp .env.example .env
```

Depois:

```bash
docker compose up --build
```

API: `http://localhost:8000`

Health: `GET /health/`

O container executa migrations e `seed_demo` antes de iniciar o Gunicorn.

## Rodando localmente

Crie um ambiente virtual e instale:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Configure `.env`, deixe o PostgreSQL disponível e rode:

```bash
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

## Usuário de desenvolvimento

- usuário: `admin`
- e-mail: `admin@chegadasegura.local`
- senha: `Admin@12345`

Troque a senha antes de qualquer uso real.

## Fluxo do tablet

### 1. Conferência

```http
GET /api/tablet/student/?ra=100001&name=Aluno%20Demonstração
X-Kiosk-Key: change-this-kiosk-key
```

O telefone do responsável não aparece nessa resposta.

### 2. Login

```http
POST /api/auth/login/
Content-Type: application/json

{"username":"admin","password":"Admin@12345"}
```

O login aceita tanto usuário quanto e-mail.

### 3. Registro supervisionado

```http
POST /api/tablet/check-ins/
Authorization: Bearer <access>
X-Kiosk-Key: change-this-kiosk-key
Content-Type: application/json

{"ra":"100001","name":"Aluno Demonstração"}
```

O backend busca o vínculo ativo, usa o horário do servidor, calcula atraso e cria uma notificação para cada responsável ativo.

## Regra de atraso

Para uma turma com início `07:00` e tolerância `10`:

- `07:10`: no horário;
- `07:11`: 11 minutos de atraso.

A regra textual aplicada é salva na ocorrência para preservar o contexto histórico mesmo que a configuração da turma seja alterada posteriormente.

## WhatsApp

Por padrão `WHATSAPP_ENABLED=False`, portanto nenhum envio externo ocorre.

Para produção:

```env
WHATSAPP_ENABLED=True
WHATSAPP_API_VERSION=v23.0
WHATSAPP_PHONE_NUMBER_ID=...
WHATSAPP_ACCESS_TOKEN=...
WHATSAPP_TEMPLATE_NAME=chegada_segura_chegada
WHATSAPP_TEMPLATE_LANGUAGE=pt_BR
WHATSAPP_VERIFY_TOKEN=um-token-secreto-diferente
```

O template deve existir e estar aprovado no WhatsApp Business/Meta. O backend envia quatro parâmetros: aluno, turma, horário e situação.

Processamento manual:

```http
POST /api/notifications/process-now/
Authorization: Bearer <access>
```

Em produção, esse endpoint pode ser chamado por um cron/worker. A primeira versão deliberadamente não adiciona Celery/Redis, mantendo a infraestrutura mínima do projeto.

## Principais endpoints

| Método | Endpoint | Uso |
|---|---|---|
| GET | `/health/` | saúde |
| POST | `/api/auth/login/` | login |
| POST | `/api/auth/refresh/` | renovar JWT |
| GET | `/api/auth/me/` | usuário atual |
| GET | `/api/tablet/student/` | conferir aluno |
| POST | `/api/tablet/check-ins/` | chegada supervisionada |
| GET/POST | `/api/students/` | alunos |
| PATCH | `/api/students/:id/` | aluno |
| GET | `/api/students/:id/history/` | histórico restrito |
| POST | `/api/students/:id/guardians/` | responsável |
| PATCH | `/api/students/:id/guardians/:id/` | responsável |
| GET/POST | `/api/classes/` | turmas/horários |
| PATCH | `/api/classes/:id/` | turma |
| GET/POST | `/api/enrollments/` | vínculos |
| PATCH | `/api/enrollments/:id/` | vínculo |
| GET/POST | `/api/arrivals/` | ocorrências |
| PATCH | `/api/arrivals/:id/correction/` | correção/cancelamento |
| GET | `/api/dashboard/` | painel |
| GET | `/api/notifications/` | fila |
| POST | `/api/notifications/process-now/` | processar fila |
| GET/POST | `/api/users/` | usuários admin |
| PATCH | `/api/users/:id/` | usuário admin |
| GET | `/webhooks/whatsapp/` | verificação Meta |
| POST | `/webhooks/whatsapp/status/` | status Meta |

## Filtros do painel

Exemplos:

```text
/api/dashboard/?date=2026-10-06
/api/dashboard/?month=2026-10
/api/dashboard/?month=2026-10&classId=<uuid>
/api/dashboard/?date=2026-10-06&shift=MORNING
```

Os indicadores distinguem **ocorrências** e **estudantes distintos**, conforme o documento do projeto.

## Segurança e privacidade

- RA + nome são conferência de cadastro, não autenticação de identidade.
- O ponto de entrada deve ser supervisionado.
- O telefone do responsável é acessível apenas por endpoints autenticados de funcionários/direção/admin e não é retornado pelo tablet.
- JWT é obrigatório para operações protegidas.
- O kiosk key é obrigatório para endpoints do tablet.
- Correções exigem justificativa e ficam auditadas.
- Em produção, usar HTTPS, segredo forte, backups, controle de acesso e política de retenção.

## Testes

Com dependências instaladas:

```bash
python manage.py test
```

ou:

```bash
pytest
```

A validação sintática dos arquivos Python foi realizada durante a montagem deste pacote. A execução efetiva do Django não pôde ser feita neste ambiente porque não havia acesso à internet para instalar Django/DRF.

## OpenAPI

A especificação inicial está em `openapi.yaml`.
