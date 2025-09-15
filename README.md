# API de Imóveis (HATEOAS) - Projeto 2

API RESTful simples para gerenciar um catálogo de imóveis com suporte a HATEOAS.

**Status:** Implementação em Flask com operações CRUD e endpoints para busca por tipo e cidade.

**Principais arquivos**
- `app.py`: aplicação Flask com rotas e HATEOAS.
- `func.py`: funções de acesso ao banco (DAO) usando `mysql-connector-python`.
- `database_config.py`: leitura e validação das variáveis de ambiente para conexão MySQL.
- `imoveis.sql`: script SQL com criação da tabela e muitos registros de exemplo (formato SQL - contém instruções compatíveis com SQLite e MySQL com pequenas adaptações).
- `requirements.txt`: dependências do projeto.

**Endpoints principais**
- `GET /` : informações da API (HATEOAS links e estatísticas básicas).
- `GET /imoveis` : lista todos os imóveis.
- `GET /imoveis/<id>` : obtém um imóvel por `id`.
- `POST /imoveis` : cria um novo imóvel (JSON no body).
- `PUT /imoveis/<id>` : atualiza um imóvel existente (JSON no body).
- `DELETE /imoveis/<id>` : remove um imóvel.
- `GET /imoveis/tipo/<tipo>` : filtra por tipo de imóvel.
- `GET /imoveis/cidade/<cidade>` : filtra por cidade.
- `GET /health` : health check da API.

Pré-requisitos
- Python 3.10+ instalado
- Um servidor MySQL acessível
- Recomenda-se criar um ambiente virtual (venv)

Instalação

1. Criar e ativar um virtualenv (Windows PowerShell):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. Instalar dependências:

```powershell
python -m pip install -r requirements.txt
```

Configuração do banco de dados

O projeto usa MySQL via `mysql-connector-python`. Antes de rodar a aplicação, defina as seguintes variáveis de ambiente (ou use um `.env` com `python-dotenv`):

- `DB_HOST` (default: `localhost`)
- `DB_PORT` (default: `3306`)
- `DB_USER` (obrigatório)
- `DB_PASSWORD` (obrigatório)
- `DB_NAME` (obrigatório)

Exemplo (PowerShell):

```powershell
$env:DB_HOST = 'localhost'; $env:DB_PORT = '3306'; $env:DB_USER = 'seu_usuario'; $env:DB_PASSWORD = 'sua_senha'; $env:DB_NAME = 'imoveis_db'
```

Criar o schema e popular a tabela

- Se usar MySQL, crie o banco e execute o conteúdo de `imoveis.sql` (algumas declarações no arquivo foram geradas para SQLite; ajuste `id`/AUTO_INCREMENT conforme necessário). Exemplo:

```sql
CREATE DATABASE imoveis_db;
USE imoveis_db;
-- Ajuste a definição de `id` para MySQL: `INT AUTO_INCREMENT PRIMARY KEY`
-- Em seguida, execute os INSERTs do arquivo `imoveis.sql`.
```


Executando a API

```powershell
# com o virtualenv ativado e variáveis de ambiente configuradas
python app.py
```

A aplicação pode ser encontrada em http://54.147.11.85

Exemplos de uso (curl/PowerShell)

- Listar imóveis:

```powershell
curl http://54.147.11.85/imoveis
```

- Obter um imóvel por id:

```powershell
curl http://54.147.11.85/imoveis/1
```

- Criar um imóvel (exemplo JSON):

```powershell
curl -X POST http://54.147.11.85/imoveis -H "Content-Type: application/json" -d '{"logradouro":"Rua Exemplo","tipo_logradouro":"Rua","bairro":"Centro","cidade":"CidadeX","cep":"12345678","tipo":"casa","valor":123000.0,"data_aquisicao":"2024-01-01"}'
```

- Atualizar um imóvel (parcial):

```powershell
curl -X PUT http://54.147.11.85/imoveis/1 -H "Content-Type: application/json" -d '{"valor":200000.0}'
```

- Deletar um imóvel:

```powershell
curl -X DELETE http://54.147.11.85/imoveis/1
```


Autores
- Enzo S. e Victor D.

