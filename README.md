# Sistema de Reserva de Salas - Backend

API RESTful desenvolvida em Python com FastAPI para gerenciamento de reservas de salas de reunião.

## 🚀 Tecnologias Utilizadas

- **FastAPI**: Framework web moderno e rápido para construção de APIs
- **SQLAlchemy**: ORM para Python, facilitando interação com banco de dados
- **PostgreSQL**: Banco de dados relacional robusto e escalável
- **Pydantic**: Validação de dados e serialização
- **JWT**: Autenticação baseada em tokens
- **Alembic**: Ferramenta de migração de banco de dados
- **Uvicorn**: Servidor ASGI de alta performance

## 📋 Pré-requisitos

- Python 3.9 ou superior
- PostgreSQL 12 ou superior
- pip (gerenciador de pacotes Python)

## 🔧 Instalação

1. **Clone o repositório** (ou navegue até a pasta do backend):
```bash
cd backend
```

2. **Crie um ambiente virtual** (recomendado):
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente**:
```bash
# Copie o arquivo .env.example para .env
cp .env.example .env

# Edite o arquivo .env com suas configurações
# DATABASE_URL=postgresql://user:password@localhost:5432/reservas_db
# SECRET_KEY=sua-chave-secreta-aqui
```

5. **Crie o banco de dados PostgreSQL**:
```sql
CREATE DATABASE reservas_db;
```

6. **Execute as migrações** (opcional, as tabelas são criadas automaticamente):
```bash
# Se usar Alembic (futuro)
alembic upgrade head
```

## 🏃 Como Executar

1. **Ative o ambiente virtual** (se ainda não estiver ativo):
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

2. **Inicie o servidor**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. **Acesse a documentação interativa**:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## 📚 Estrutura do Projeto

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicação principal FastAPI
│   ├── database.py          # Configuração do banco de dados
│   ├── models.py            # Modelos SQLAlchemy
│   ├── schemas.py           # Schemas Pydantic
│   ├── auth.py              # Lógica de autenticação
│   ├── services.py          # Serviços de negócio (validação de conflitos)
│   └── routers/
│       ├── __init__.py
│       ├── salas.py         # Rotas de salas
│       ├── reservas.py      # Rotas de reservas
│       └── auth.py          # Rotas de autenticação
├── alembic/                 # Migrações de banco de dados
├── .env.example             # Exemplo de variáveis de ambiente
├── requirements.txt         # Dependências Python
└── README.md                # Este arquivo
```

## 🔑 Funcionalidades

### Salas
- ✅ Listar todas as salas
- ✅ Obter sala por ID
- ✅ Criar nova sala
- ✅ Atualizar sala existente
- ✅ Excluir sala

### Reservas
- ✅ Listar todas as reservas (com filtros)
- ✅ Obter reserva por ID
- ✅ Criar nova reserva com **validação de conflitos de horário**
- ✅ Atualizar reserva existente com validação
- ✅ Excluir reserva
- ✅ Verificar disponibilidade de sala em horário específico

### Autenticação (Opcional)
- ✅ Registrar novo usuário
- ✅ Login com JWT
- ✅ Obter usuário atual

## 🛡️ Validações Implementadas

### Reservas
- **Conflito de horários**: Impede reservas sobrepostas na mesma sala
- **Data de fim posterior à data de início**: Validação temporal
- **Sala ativa**: Apenas salas ativas podem ser reservadas
- **Campos obrigatórios**: Validação de campos requeridos

### Salas
- **Nome único**: Não permite salas com mesmo nome
- **Campos obrigatórios**: Validação de campos requeridos

## 📡 Endpoints Principais

### Salas
- `GET /api/salas/` - Listar salas
- `GET /api/salas/{id}` - Obter sala
- `POST /api/salas/` - Criar sala
- `PUT /api/salas/{id}` - Atualizar sala
- `DELETE /api/salas/{id}` - Excluir sala

### Reservas
- `GET /api/reservas/` - Listar reservas (com filtros)
- `GET /api/reservas/{id}` - Obter reserva
- `POST /api/reservas/` - Criar reserva
- `PUT /api/reservas/{id}` - Atualizar reserva
- `DELETE /api/reservas/{id}` - Excluir reserva
- `GET /api/reservas/sala/{id}/disponibilidade` - Verificar disponibilidade

### Autenticação
- `POST /api/auth/register` - Registrar usuário
- `POST /api/auth/login` - Fazer login
- `GET /api/auth/me` - Obter usuário atual

## 🔒 Segurança

- **JWT Tokens**: Autenticação baseada em tokens
- **Hash de senhas**: Uso de bcrypt para hash de senhas
- **CORS**: Configurado para permitir requisições do frontend
- **Validação de dados**: Pydantic valida todos os dados de entrada
- **SQL Injection**: Protegido pelo uso de ORM (SQLAlchemy)

## 🧪 Testes

Para testar a API, você pode usar:
- A documentação interativa (Swagger UI) em `/api/docs`
- Ferramentas como Postman ou Insomnia
- O frontend React que acompanha este projeto

## 📝 Padrões e Boas Práticas

- **Separação de responsabilidades**: Rotas, serviços, modelos e schemas separados
- **Documentação automática**: FastAPI gera documentação automaticamente
- **Type hints**: Uso extensivo de type hints para melhor manutenibilidade
- **Validação de dados**: Pydantic para validação e serialização
- **ORM**: SQLAlchemy para abstração do banco de dados
- **Migrations**: Alembic para controle de versão do banco de dados

## 🐳 Docker (Opcional)

Para executar com Docker:

```bash
# Criar e iniciar containers
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar containers
docker-compose down
```

## 📄 Licença

Este projeto foi desenvolvido como parte de um processo seletivo.

## 👤 Autor

Desenvolvido para o processo seletivo da Matricial Capital.

# matricial_back
