# API RESTful de Imóveis

Uma API Flask para gerenciamento de imóveis com suporte tanto para SQLite quanto MySQL.

## Funcionalidades

- Listar todos os imóveis
- Buscar imóvel por ID
- Adicionar novo imóvel
- Atualizar imóvel existente
- Remover imóvel
- Filtrar imóveis por tipo
- Filtrar imóveis por cidade

## Configuração de Banco de Dados

Esta aplicação suporta dois tipos de banco de dados:

### SQLite (Padrão)
Por padrão, a aplicação usa SQLite. Nenhuma configuração adicional é necessária.

### MySQL
Para usar MySQL, você precisa:

1. **Instalar MySQL Server** e criar um banco de dados
2. **Executar o script SQL** para criar as tabelas:
   ```sql
   mysql -u your_username -p your_database < imoveis_mysql.sql
   ```

3. **Configurar variáveis de ambiente**:
   - Copie `.env.example` para `.env`
   - Preencha as credenciais do MySQL:
     ```
     DATABASE_TYPE=mysql
     DB_HOST=localhost
     DB_PORT=3306
     DB_USER=seu_usuario_mysql
     DB_PASSWORD=sua_senha_mysql
     DB_NAME=imoveis_db
     ```

## Instalação

1. **Clone o repositório**:
   ```bash
   git clone <repository-url>
   cd 20252-progeficaz-projeto2-enzos-e-victordolnikoff
   ```

2. **Crie um ambiente virtual**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # ou
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure o banco de dados** (se usar MySQL):
   - Copie `.env.example` para `.env`
   - Configure as variáveis de ambiente conforme necessário
   - Execute o script SQL no MySQL

## Execução

```bash
python app.py
```

A API estará disponível em `http://localhost:5000`

## Endpoints da API

### Informações da API
- `GET /` - Informações básicas da API

### Imóveis
- `GET /imoveis` - Listar todos os imóveis
- `GET /imoveis/<id>` - Obter imóvel por ID
- `POST /imoveis` - Criar novo imóvel
- `PUT /imoveis/<id>` - Atualizar imóvel
- `DELETE /imoveis/<id>` - Remover imóvel

### Filtros
- `GET /imoveis/tipo/<tipo>` - Listar imóveis por tipo
- `GET /imoveis/cidade/<cidade>` - Listar imóveis por cidade

## Exemplo de Uso

### Criar um novo imóvel
```bash
curl -X POST http://localhost:5000/imoveis \
  -H "Content-Type: application/json" \
  -d '{
    "logradouro": "Rua das Flores",
    "tipo_logradouro": "Rua",
    "bairro": "Centro",
    "cidade": "São Paulo",
    "cep": "01234-567",
    "tipo": "apartamento",
    "valor": 450000.00,
    "data_aquisicao": "2024-01-15"
  }'
```

## Testes

Execute os testes com:
```bash
pytest test_imoveis.py -v
```

## Estrutura do Projeto

```
├── app.py                 # Aplicação Flask principal
├── func.py               # Funções de banco de dados
├── database_config.py    # Configuração de banco de dados
├── imoveis.db           # Banco SQLite (gerado automaticamente)
├── imoveis.sql          # Script SQL para SQLite
├── imoveis_mysql.sql    # Script SQL para MySQL
├── requirements.txt     # Dependências Python
├── .env.example        # Exemplo de configuração de ambiente
├── test_imoveis.py     # Testes unitários
└── README.md           # Este arquivo
```

## Migração de SQLite para MySQL

Se você já tem dados no SQLite e quer migrar para MySQL:

1. Configure as variáveis de ambiente para MySQL
2. Execute o script `imoveis_mysql.sql` no MySQL
3. Use ferramentas como `sqlite3` e `mysql` para exportar/importar dados, ou
4. Mantenha ambos os bancos e alterne via variável de ambiente `DATABASE_TYPE`
