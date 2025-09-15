from flask import Flask, jsonify, request
from func import *
import re
from datetime import datetime

app = Flask(__name__)

# Configurações
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Middleware para tratamento de erros
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Recurso não encontrado',
        'message': 'O recurso solicitado não foi encontrado no servidor',
        'status': 404
    }), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'error': 'Requisição inválida',
        'message': 'Os dados enviados são inválidos ou estão mal formatados',
        'status': 400
    }), 400

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Erro interno do servidor',
        'message': 'Ocorreu um erro inesperado no servidor',
        'status': 500
    }), 500

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'error': 'Método não permitido',
        'message': 'O método HTTP usado não é permitido para este endpoint',
        'status': 405
    }), 405

@app.errorhandler(409)
def conflict(error):
    return jsonify({
        'error': 'Conflito',
        'message': 'A requisição não pôde ser processada devido a conflito com o estado atual do recurso',
        'status': 409
    }), 409

@app.errorhandler(422)
def unprocessable_entity(error):
    return jsonify({
        'error': 'Entidade não processável',
        'message': 'A requisição está bem formada, mas não pôde ser processada devido a erros semânticos',
        'status': 422
    }), 422

@app.errorhandler(503)
def service_unavailable(error):
    return jsonify({
        'error': 'Serviço indisponível',
        'message': 'O servidor não está disponível temporariamente. Tente novamente mais tarde',
        'status': 503
    }), 503

# Função auxiliar para tratamento de erros de banco de dados
def handle_database_error(e):
    """Trata erros de banco de dados e retorna a resposta apropriada"""
    error_message = str(e).lower()
    
    # Erros de conexão com banco de dados
    if any(keyword in error_message for keyword in ['connection', 'timeout', 'refused', 'unreachable']):
        return jsonify({
            'success': False,
            'error': 'Serviço de banco de dados indisponível',
            'message': 'Não foi possível conectar ao banco de dados. Tente novamente mais tarde.',
            'details': str(e)
        }), 503
    
    # Erros de constraint/integridade (duplicatas, violações de chave)
    elif any(keyword in error_message for keyword in ['duplicate', 'constraint', 'integrity', 'unique']):
        return jsonify({
            'success': False,
            'error': 'Conflito de dados',
            'message': 'Os dados fornecidos conflitam com registros existentes',
            'details': str(e)
        }), 409
    
    # Erros gerais do servidor
    else:
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'message': 'Ocorreu um erro inesperado no servidor',
            'details': str(e)
        }), 500

# Função auxiliar para validações
def validate_imovel_data(data, is_update=False):
    """Valida os dados do imóvel e retorna erros se houver"""
    tipos_validos = ['casa', 'apartamento', 'terreno', 'comercial', 'industrial']
    
    # Validar CEP se fornecido
    if 'cep' in data:
        cep = str(data['cep']).strip().replace('-', '').replace('.', '')
        if not re.match(r'^\d{8}$', cep):
            return {
                'success': False,
                'error': 'CEP inválido',
                'message': 'CEP deve conter 8 dígitos numéricos (formato: 12345678 ou 12345-678)'
            }, 422
    
    # Validar tipo se fornecido
    if 'tipo' in data:
        if str(data['tipo']).strip().lower() not in tipos_validos:
            return {
                'success': False,
                'error': 'Tipo de imóvel inválido',
                'message': f'Tipo deve ser um dos seguintes: {", ".join(tipos_validos)}'
            }, 422
    
    # Validar data de aquisição se fornecida
    if 'data_aquisicao' in data:
        try:
            data_aquisicao = str(data['data_aquisicao']).strip()
            datetime.strptime(data_aquisicao, '%Y-%m-%d')
        except ValueError:
            return {
                'success': False,
                'error': 'Data de aquisição inválida',
                'message': 'Data deve estar no formato YYYY-MM-DD (ex: 2024-01-15)'
            }, 422
    
    # Validar valor se fornecido
    if 'valor' in data:
        try:
            valor = float(data['valor'])
            if valor < 0:
                return {
                    'success': False,
                    'error': 'Valor inválido',
                    'message': 'O valor deve ser um número positivo'
                }, 422
        except (ValueError, TypeError):
            return {
                'success': False,
                'error': 'Valor inválido',
                'message': 'O valor deve ser um número válido'
            }, 422
    
    # Validar campos vazios para operações de atualização
    if is_update:
        empty_text_fields = ['logradouro', 'tipo_logradouro', 'bairro', 'cidade']
        for field in empty_text_fields:
            if field in data and not str(data[field]).strip():
                return {
                    'success': False,
                    'error': 'Campo vazio',
                    'message': f'{field.replace("_", " ").title()} não pode estar vazio'
                }, 422
    
    return None, None

# Rota raiz para informações da API
@app.route('/', methods=['GET'])
def api_info():
    """Informações básicas da API"""
    return jsonify({
        'api': 'API RESTful de Imóveis',
        'version': '1.0.0',
        'description': 'API para gerenciamento de imóveis de uma empresa imobiliária',
        'endpoints': {
            'GET /imoveis': 'Listar todos os imóveis',
            'GET /imoveis/<id>': 'Obter imóvel específico por ID',
            'POST /imoveis': 'Criar novo imóvel',
            'PUT /imoveis/<id>': 'Atualizar imóvel existente',
            'DELETE /imoveis/<id>': 'Remover imóvel',
            'GET /imoveis/tipo/<tipo>': 'Listar imóveis por tipo',
            'GET /imoveis/cidade/<cidade>': 'Listar imóveis por cidade'
        },
        'status': 'online'
    })

# 1. Listar todos os imóveis
@app.route('/imoveis', methods=['GET'])
def listar_todos_imoveis_route():
    """Lista todos os imóveis com todos os seus atributos"""
    try:
        imoveis = listar_todos_imoveis()
        
        return jsonify({
            'success': True,
            'message': f'{len(imoveis)} imóveis encontrados',
            'data': imoveis,
            'total': len(imoveis)
        }), 200
        
    except FileNotFoundError as e:
        return jsonify({
            'success': False,
            'error': 'Database não encontrada',
            'message': str(e)
        }), 503
        
    except Exception as e:
        return handle_database_error(e)

# 2. Listar imóvel específico por ID
@app.route('/imoveis/<int:imovel_id>', methods=['GET'])
def obter_imovel_por_id_route(imovel_id):
    """Obtém um imóvel específico pelo seu ID"""
    try:
        imovel = listar_imovel_por_id(imovel_id)
        
        if imovel is None:
            return jsonify({
                'success': False,
                'error': 'Imóvel não encontrado',
                'message': f'Nenhum imóvel encontrado com ID {imovel_id}'
            }), 404
            
        return jsonify({
            'success': True,
            'message': 'Imóvel encontrado com sucesso',
            'data': imovel
        }), 200
        
    except Exception as e:
        return handle_database_error(e)

# 3. Adicionar novo imóvel
@app.route('/imoveis', methods=['POST'])
def criar_imovel_route():
    """Cria um novo imóvel"""
    try:
        # Validar se o request contém JSON
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type deve ser application/json',
                'message': 'A requisição deve conter dados JSON válidos'
            }), 400
            
        data = request.get_json()
        
        # Validar campos obrigatórios
        required_fields = ['logradouro', 'tipo_logradouro', 'bairro', 'cidade', 'cep', 'tipo', 'valor', 'data_aquisicao']
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': 'Campos obrigatórios ausentes',
                'message': f'Os seguintes campos são obrigatórios: {", ".join(missing_fields)}',
                'required_fields': required_fields
            }), 422
        
        # Validar se os campos de texto não estão vazios
        empty_fields = [field for field in required_fields[:-2] if not str(data.get(field, '')).strip()]
        if empty_fields:
            return jsonify({
                'success': False,
                'error': 'Campos vazios detectados',
                'message': f'Os seguintes campos não podem estar vazios: {", ".join(empty_fields)}'
            }), 422
        
        # Usar função de validação centralizada
        error_response, status_code = validate_imovel_data(data)
        if error_response:
            return jsonify(error_response), status_code
        
        # Inserir imóvel
        novo_id = inserir_imovel(
            logradouro=str(data['logradouro']).strip(),
            tipo_logradouro=str(data['tipo_logradouro']).strip(),
            bairro=str(data['bairro']).strip(),
            cidade=str(data['cidade']).strip(),
            cep=str(data['cep']).strip(),
            tipo=str(data['tipo']).strip().lower(),
            valor=float(data['valor']),
            data_aquisicao=str(data['data_aquisicao']).strip()
        )
        
        # Buscar o imóvel criado para retornar
        imovel_criado = listar_imovel_por_id(novo_id)
        
        return jsonify({
            'success': True,
            'message': 'Imóvel criado com sucesso',
            'data': imovel_criado
        }), 201
        
    except Exception as e:
        return handle_database_error(e)

# 4. Atualizar imóvel existente
@app.route('/imoveis/<int:imovel_id>', methods=['PUT'])
def atualizar_imovel_route(imovel_id):
    """Atualiza um imóvel existente"""
    try:
        # Verificar se o imóvel existe
        imovel_existe = listar_imovel_por_id(imovel_id)
        if imovel_existe is None:
            return jsonify({
                'success': False,
                'error': 'Imóvel não encontrado',
                'message': f'Nenhum imóvel encontrado com ID {imovel_id}'
            }), 404
            
        # Validar se o request contém JSON
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type deve ser application/json',
                'message': 'A requisição deve conter dados JSON válidos'
            }), 400
            
        data = request.get_json()
        
        # Usar função de validação centralizada
        error_response, status_code = validate_imovel_data(data, is_update=True)
        if error_response:
            return jsonify(error_response), status_code
        
        # Preparar argumentos para atualização (apenas campos fornecidos)
        update_args = {}
        
        if 'logradouro' in data:
            update_args['logradouro'] = str(data['logradouro']).strip()
        if 'tipo_logradouro' in data:
            update_args['tipo_logradouro'] = str(data['tipo_logradouro']).strip()
        if 'bairro' in data:
            update_args['bairro'] = str(data['bairro']).strip()
        if 'cidade' in data:
            update_args['cidade'] = str(data['cidade']).strip()
        if 'cep' in data:
            update_args['cep'] = str(data['cep']).strip()
        if 'tipo' in data:
            update_args['tipo'] = str(data['tipo']).strip().lower()
        if 'data_aquisicao' in data:
            update_args['data_aquisicao'] = str(data['data_aquisicao']).strip()
        if 'valor' in data:
            update_args['valor'] = float(data['valor'])
        
        # Verificar se há campos para atualizar
        if not update_args:
            return jsonify({
                'success': False,
                'error': 'Nenhum campo para atualizar',
                'message': 'Pelo menos um campo deve ser fornecido para atualização'
            }), 422
        
        # Atualizar imóvel
        sucesso = atualizar_imovel(imovel_id, **update_args)
        
        if not sucesso:
            return jsonify({
                'success': False,
                'error': 'Falha na atualização',
                'message': 'Não foi possível atualizar o imóvel'
            }), 500
        
        # Buscar imóvel atualizado
        imovel_atualizado = listar_imovel_por_id(imovel_id)
        
        return jsonify({
            'success': True,
            'message': 'Imóvel atualizado com sucesso',
            'data': imovel_atualizado
        }), 200
        
    except Exception as e:
        return handle_database_error(e)

# 5. Remover imóvel
@app.route('/imoveis/<int:imovel_id>', methods=['DELETE'])
def deletar_imovel_route(imovel_id):
    """Remove um imóvel existente"""
    try:
        # Verificar se o imóvel existe antes de tentar deletar
        imovel_existe = listar_imovel_por_id(imovel_id)
        if imovel_existe is None:
            return jsonify({
                'success': False,
                'error': 'Imóvel não encontrado',
                'message': f'Nenhum imóvel encontrado com ID {imovel_id}'
            }), 404
        
        # Deletar imóvel
        sucesso = deletar_imovel(imovel_id)
        
        if not sucesso:
            return jsonify({
                'success': False,
                'error': 'Falha na remoção',
                'message': 'Não foi possível remover o imóvel'
            }), 500
        
        return jsonify({
            'success': True,
            'message': f'Imóvel com ID {imovel_id} removido com sucesso',
            'data': imovel_existe  # Retorna os dados do imóvel removido
        }), 200
        
    except Exception as e:
        return handle_database_error(e)

# 6. Listar imóveis por tipo
@app.route('/imoveis/tipo/<tipo>', methods=['GET'])
def listar_imoveis_por_tipo_route(tipo):
    """Lista todos os imóveis de um tipo específico"""
    try:
        imoveis = listar_imoveis_por_tipo(tipo)
        
        return jsonify({
            'success': True,
            'message': f'{len(imoveis)} imóveis do tipo "{tipo}" encontrados',
            'data': imoveis,
            'filtro': {
                'tipo': tipo
            },
            'total': len(imoveis)
        }), 200
        
    except Exception as e:
        return handle_database_error(e)

# 7. Listar imóveis por cidade
@app.route('/imoveis/cidade/<cidade>', methods=['GET'])
def listar_imoveis_por_cidade_route(cidade):
    """Lista todos os imóveis de uma cidade específica"""
    try:
        imoveis = listar_imoveis_por_cidade(cidade)
        
        return jsonify({
            'success': True,
            'message': f'{len(imoveis)} imóveis na cidade "{cidade}" encontrados',
            'data': imoveis,
            'filtro': {
                'cidade': cidade
            },
            'total': len(imoveis)
        }), 200
        
    except Exception as e:
        return handle_database_error(e)

# Rota para verificar health da API
@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se a API está funcionando"""
    try:
        # Tenta fazer uma consulta simples no banco
        imoveis = listar_todos_imoveis()
        return jsonify({
            'status': 'healthy',
            'message': 'API funcionando corretamente',
            'database': 'connected',
            'total_imoveis': len(imoveis)
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'message': 'Problemas na API',
            'error': str(e)
        }), 503

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
