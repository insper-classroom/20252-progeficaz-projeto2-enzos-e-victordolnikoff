# 🏠 API RESTful de Imóveis - Projeto Completo

Uma API RESTful completa para gerenciamento de imóveis de uma empresa imobiliária, desenvolvida com Flask e seguindo os princípios de TDD.

## 📋 Funcionalidades

### ✅ **Endpoints Principais**
- **GET /imoveis** - Listar todos os imóveis
- **GET /imoveis/{id}** - Obter imóvel específico por ID
- **POST /imoveis** - Criar novo imóvel
- **PUT /imoveis/{id}** - Atualizar imóvel existente
- **DELETE /imoveis/{id}** - Remover imóvel
- **GET /imoveis/tipo/{tipo}** - Filtrar imóveis por tipo
- **GET /imoveis/cidade/{cidade}** - Filtrar imóveis por cidade

### ✅ **Endpoints Auxiliares**
- **GET /** - Informações da API
- **GET /health** - Health check da API

## 🛠️ Tecnologias Utilizadas

- **Flask** - Framework web Python
- **SQLite** - Banco de dados (compatível com MySQL)
- **pytest** - Framework de testes
- **JSON** - Formato de resposta
- **TDD** - Test-Driven Development

## 🚀 Instalação e Execução

### 1. **Pré-requisitos**
- Python 3.8+
- pip

### 2. **Clone o repositório**
```bash
git clone https://github.com/insper-classroom/20252-progeficaz-projeto2-enzos-e-victordolnikoff.git
cd 20252-progeficaz-projeto2-enzos-e-victordolnikoff
```

### 3. **Criar ambiente virtual**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 4. **Instalar dependências**
```bash
pip install -r requirements.txt
```

### 5. **Executar a API**
```bash
python app.py
```

🌐 **API disponível em:** `http://localhost:5000`

## 🧪 Testes

### Executar todos os testes
```bash
# Testes automatizados da API
python -m pytest test_api.py -v

# Testes das funções originais
python -m pytest test_imoveis.py -v

# Testes manuais simplificados
python test_manual.py

# Demonstração interativa completa
python demo.py
```

## 📡 Exemplos de Uso

### **Criar um novo imóvel**
```bash
curl -X POST http://localhost:5000/imoveis \
  -H "Content-Type: application/json" \
  -d '{
    "logradouro": "Avenida Paulista",
    "tipo_logradouro": "Avenida",
    "bairro": "Bela Vista",
    "cidade": "São Paulo",
    "cep": "01310-000",
    "tipo": "apartamento",
    "valor": 850000.00,
    "data_aquisicao": "2024-01-15"
  }'
```

### **Listar imóveis por tipo**
```bash
curl -X GET http://localhost:5000/imoveis/tipo/casa
```

### **Buscar imóvel por ID**
```bash
curl -X GET http://localhost:5000/imoveis/1
```

## 📁 Estrutura do Projeto

```
📦 projeto-imoveis-api/
├── 📄 app.py               # Aplicação Flask principal
├── 📄 func.py              # Funções de banco de dados
├── 📄 test_api.py          # Testes automatizados da API
├── 📄 test_imoveis.py      # Testes das funções originais
├── 📄 test_manual.py       # Testes manuais
├── 📄 demo.py              # Demonstração interativa
├── 📄 requirements.txt     # Dependências Python
├── 📄 README_API.md        # Documentação completa da API
├── 📄 DEPLOY_AWS.md        # Instruções de deploy na AWS
├── 📄 PROJETO_COMPLETO.md  # Resumo do projeto
├── 🗃️ imoveis.db           # Banco de dados SQLite
├── 📄 imoveis.sql          # Script de criação do banco
└── 📄 README.md            # Este arquivo
```

## 🚀 Deploy na AWS EC2

Para instruções completas de deploy na AWS EC2, consulte: **[DEPLOY_AWS.md](DEPLOY_AWS.md)**

### Resumo do deploy:
1. Criar instância EC2
2. Configurar ambiente Python
3. Configurar Nginx como proxy reverso
4. Configurar SSL com Let's Encrypt
5. Configurar monitoramento e backup

## 📊 Status do Projeto

### ✅ **Implementado e Testado**
- [x] API RESTful completa com Flask
- [x] Todas as 7 rotas obrigatórias
- [x] Testes automatizados (26 testes)
- [x] TDD implementado
- [x] Validação de dados
- [x] Tratamento de erros
- [x] Documentação completa
- [x] Scripts de demonstração
- [x] Instruções de deploy

### 📈 **Resultados dos Testes**
- 🏠 **1000 imóveis** no banco de dados
- ✅ **100%** dos endpoints funcionando
- ✅ **100%** dos testes passando
- ✅ **CRUD completo** operacional

## 📚 Documentação Adicional

- **[README_API.md](README_API.md)** - Documentação completa da API
- **[DEPLOY_AWS.md](DEPLOY_AWS.md)** - Instruções de deploy na AWS
- **[PROJETO_COMPLETO.md](PROJETO_COMPLETO.md)** - Resumo completo do projeto

## 🎯 **Status: API PRONTA PARA PRODUÇÃO!** 🚀

---
*Desenvolvido seguindo as melhores práticas de desenvolvimento de APIs RESTful, TDD e deploy em nuvem.*
