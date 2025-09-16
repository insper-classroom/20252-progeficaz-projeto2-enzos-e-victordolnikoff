from flask import Flask, jsonify, request, url_for
from func import *
import re
from datetime import datetime
from collections import OrderedDict

app = Flask(__name__)

# Configurações
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# HATEOAS Helper Functions
def build_imovel_links(imovel_id, include_collection=True):
    """Build hypermedia links for a single imovel resource"""
    links = {
        'self': {
            'href': url_for('obter_imovel_por_id_route', imovel_id=imovel_id, _external=True),
            'method': 'GET',
            'title': 'Obter detalhes deste imóvel'
        },
        'edit': {
            'href': url_for('atualizar_imovel_route', imovel_id=imovel_id, _external=True),
            'method': 'PUT',
            'title': 'Atualizar este imóvel'
        },
        'delete': {
            'href': url_for('deletar_imovel_route', imovel_id=imovel_id, _external=True),
            'method': 'DELETE',
            'title': 'Remover este imóvel'
        }
    }
    
    if include_collection:
        links['collection'] = {
            'href': url_for('listar_todos_imoveis_route', _external=True),
            'method': 'GET',
            'title': 'Listar todos os imóveis'
        }
    
    return links

def build_collection_links():
    """Build hypermedia links for imoveis collection"""
    return {
        'self': {
            'href': url_for('listar_todos_imoveis_route', _external=True),
            'method': 'GET',
            'title': 'Listar todos os imóveis'
        },
        'create': {
            'href': url_for('criar_imovel_route', _external=True),
            'method': 'POST',
            'title': 'Criar novo imóvel'
        },
        'search_by_type': {
            'href': url_for('listar_imoveis_por_tipo_route', tipo='{tipo}', _external=True).replace('%7Btipo%7D', '{tipo}'),
            'method': 'GET',
            'title': 'Buscar imóveis por tipo',
            'templated': True
        },
        'search_by_city': {
            'href': url_for('listar_imoveis_por_cidade_route', cidade='{cidade}', _external=True).replace('%7Bcidade%7D', '{cidade}'),
            'method': 'GET',
            'title': 'Buscar imóveis por cidade',
            'templated': True
        }
    }

def build_api_root_links():
    """Build hypermedia links for API root"""
    return {
        'self': {
            'href': url_for('api_info', _external=True),
            'method': 'GET',
            'title': 'Informações da API'
        },
        'imoveis': {
            'href': url_for('listar_todos_imoveis_route', _external=True),
            'method': 'GET',
            'title': 'Listar todos os imóveis'
        },
        'create_imovel': {
            'href': url_for('criar_imovel_route', _external=True),
            'method': 'POST',
            'title': 'Criar novo imóvel'
        },
        'health': {
            'href': url_for('health_check', _external=True),
            'method': 'GET',
            'title': 'Verificar status da API'
        }
    }

def enhance_imovel_with_links(imovel):
    """Add HATEOAS links to a single imovel object with data fields first"""
    if imovel and 'id' in imovel:
        # Use OrderedDict to guarantee field order
        enhanced_imovel = OrderedDict()
        
        # Add all original fields first in a specific order
        enhanced_imovel['id'] = imovel.get('id')
        enhanced_imovel['logradouro'] = imovel.get('logradouro')
        enhanced_imovel['tipo_logradouro'] = imovel.get('tipo_logradouro')
        enhanced_imovel['bairro'] = imovel.get('bairro')
        enhanced_imovel['cidade'] = imovel.get('cidade')
        enhanced_imovel['cep'] = imovel.get('cep')
        enhanced_imovel['tipo'] = imovel.get('tipo')
        enhanced_imovel['valor'] = imovel.get('valor')
        enhanced_imovel['data_aquisicao'] = imovel.get('data_aquisicao')
        
        # Add links at the end
        enhanced_imovel['link'] = build_imovel_links(imovel['id'])
        
        return enhanced_imovel
    return imovel

def enhance_imoveis_collection_with_links(imoveis):
    """Add HATEOAS links to each imovel in a collection"""
    enhanced_imoveis = []
    for imovel in imoveis:
        enhanced_imoveis.append(enhance_imovel_with_links(imovel.copy()))
    return enhanced_imoveis

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
    tipos_validos = ['casa', 'apartamento', 'terreno',"casa em condominio"]
    
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
    """Informações básicas da API com hypermedia para descoberta"""
    try:
        # Get basic stats for the API overview
        imoveis = listar_todos_imoveis()
        total_imoveis = len(imoveis)
        
        # Get unique types and cities for search hints
        tipos_unicos = list(set(imovel['tipo'] for imovel in imoveis if imovel.get('tipo')))
        cidades_unicas = list(set(imovel['cidade'] for imovel in imoveis if imovel.get('cidade')))
        
        return jsonify({
            'api': 'API RESTful de Imóveis - Nível 3 (HATEOAS)',
            'version': '2.0.0',
            'description': 'API para gerenciamento de imóveis de uma empresa imobiliária com suporte completo a HATEOAS',
            'richardson_level': 3,
            'features': [
                'CRUD completo de imóveis',
                'Busca por tipo e cidade',
                'Navegação descobrível via links',
                'Validação robusta de dados',
                'Tratamento de erros padronizado'
            ],
            'statistics': {
                'total_imoveis': total_imoveis,
                'tipos_disponiveis': sorted(tipos_unicos),
                'cidades_disponiveis': sorted(cidades_unicas[:10])  # Limit to first 10 for brevity
            },
            'media_types': {
                'accepted': ['application/json'],
                'returned': ['application/json']
            },
            'documentation': {
                'hateoas': 'Esta API implementa HATEOAS - use os links link para navegar entre recursos',
                'templated_urls': 'URLs com {parametro} são templates - substitua pelos valores desejados'
            },
            'link': build_api_root_links()
        }), 200
        
    except Exception as e:
        # Even if there's an error getting stats, provide the basic API info
        return jsonify({
            'api': 'API RESTful de Imóveis - Nível 3 (HATEOAS)',
            'version': '2.0.0',
            'description': 'API para gerenciamento de imóveis de uma empresa imobiliária com suporte completo a HATEOAS',
            'richardson_level': 3,
            'status': 'online_with_warnings',
            'warning': 'Não foi possível carregar estatísticas completas',
            'link': build_api_root_links()
        }), 200

# 1. Listar todos os imóveis
@app.route('/imoveis', methods=['GET'])
def listar_todos_imoveis_route():
    """Lista todos os imóveis com todos os seus atributos"""
    try:
        imoveis = listar_todos_imoveis()
        
        # Add HATEOAS links to each imovel
        enhanced_imoveis = enhance_imoveis_collection_with_links(imoveis)
        
        # Use OrderedDict to control response structure
        response_data = OrderedDict([
            ('success', True),
            ('message', f'{len(enhanced_imoveis)} imóveis encontrados'),
            ('total', len(enhanced_imoveis)),
            ('links', build_collection_links()),
            ('data', enhanced_imoveis),
        ])
        
        return jsonify(response_data), 200
        
    except FileNotFoundError as e:
        return jsonify({
            'success': False,
            'error': 'Database não encontrada',
            'message': str(e),
            'link': build_api_root_links()
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
                'message': f'Nenhum imóvel encontrado com ID {imovel_id}',
                'link': {
                    'collection': {
                        'href': url_for('listar_todos_imoveis_route', _external=True),
                        'method': 'GET',
                        'title': 'Listar todos os imóveis'
                    },
                    'create': {
                        'href': url_for('criar_imovel_route', _external=True),
                        'method': 'POST',
                        'title': 'Criar novo imóvel'
                    }
                }
            }), 404
            
        # Add HATEOAS links to the imovel
        enhanced_imovel = enhance_imovel_with_links(imovel)
        
        # Use OrderedDict to control response structure
        response_data = OrderedDict([
            ('success', True),
            ('message', 'Imóvel encontrado com sucesso'),
            ('link', build_collection_links()),
            ('data', enhanced_imovel),
        ])
        
        return jsonify(response_data), 200
        
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
                'message': 'A requisição deve conter dados JSON válidos',
                'link': build_collection_links()
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
                'required_fields': required_fields,
                'link': build_collection_links()
            }), 422
        
        # Validar se os campos de texto não estão vazios
        empty_fields = [field for field in required_fields[:-2] if not str(data.get(field, '')).strip()]
        if empty_fields:
            return jsonify({
                'success': False,
                'error': 'Campos vazios detectados',
                'message': f'Os seguintes campos não podem estar vazios: {", ".join(empty_fields)}',
                'link': build_collection_links()
            }), 422
        
        # Usar função de validação centralizada
        error_response, status_code = validate_imovel_data(data)
        if error_response:
            error_response['link'] = build_collection_links()
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
        enhanced_imovel = enhance_imovel_with_links(imovel_criado)
        
        # Build links for the created resource
        creation_links = {
            'self': {
                'href': url_for('obter_imovel_por_id_route', imovel_id=novo_id, _external=True),
                'method': 'GET',
                'title': 'Ver imóvel criado'
            },
            'edit': {
                'href': url_for('atualizar_imovel_route', imovel_id=novo_id, _external=True),
                'method': 'PUT',
                'title': 'Editar este imóvel'
            },
            'delete': {
                'href': url_for('deletar_imovel_route', imovel_id=novo_id, _external=True),
                'method': 'DELETE',
                'title': 'Remover este imóvel'
            },
            'collection': {
                'href': url_for('listar_todos_imoveis_route', _external=True),
                'method': 'GET',
                'title': 'Listar todos os imóveis'
            },
            'create_another': {
                'href': url_for('criar_imovel_route', _external=True),
                'method': 'POST',
                'title': 'Criar outro imóvel'
            }
        }
        
        # Use OrderedDict for the response
        response_data = OrderedDict([
            ('success', True),
            ('message', 'Imóvel criado com sucesso'),
            ('data', enhanced_imovel),
            ('link', creation_links)
        ])
        
        return jsonify(response_data), 201
        
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
                'message': f'Nenhum imóvel encontrado com ID {imovel_id}',
                'link': {
                    'collection': {
                        'href': url_for('listar_todos_imoveis_route', _external=True),
                        'method': 'GET',
                        'title': 'Listar todos os imóveis'
                    },
                    'create': {
                        'href': url_for('criar_imovel_route', _external=True),
                        'method': 'POST',
                        'title': 'Criar novo imóvel'
                    }
                }
            }), 404
            
        # Validar se o request contém JSON
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type deve ser application/json',
                'message': 'A requisição deve conter dados JSON válidos',
                'link': build_imovel_links(imovel_id)
            }), 400
            
        data = request.get_json()
        
        # Usar função de validação centralizada
        error_response, status_code = validate_imovel_data(data, is_update=True)
        if error_response:
            error_response['link'] = build_imovel_links(imovel_id)
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
                'message': 'Pelo menos um campo deve ser fornecido para atualização',
                'link': build_imovel_links(imovel_id)
            }), 422
        
        # Atualizar imóvel
        sucesso = atualizar_imovel(imovel_id, **update_args)
        
        if not sucesso:
            return jsonify({
                'success': False,
                'error': 'Falha na atualização',
                'message': 'Não foi possível atualizar o imóvel',
                'link': build_imovel_links(imovel_id)
            }), 500
        
        # Buscar imóvel atualizado
        imovel_atualizado = listar_imovel_por_id(imovel_id)
        enhanced_imovel = enhance_imovel_with_links(imovel_atualizado)
        
        # Build links showing available actions after update
        update_links = {
            'self': {
                'href': url_for('obter_imovel_por_id_route', imovel_id=imovel_id, _external=True),
                'method': 'GET',
                'title': 'Ver imóvel atualizado'
            },
            'edit_again': {
                'href': url_for('atualizar_imovel_route', imovel_id=imovel_id, _external=True),
                'method': 'PUT',
                'title': 'Editar novamente'
            },
            'delete': {
                'href': url_for('deletar_imovel_route', imovel_id=imovel_id, _external=True),
                'method': 'DELETE',
                'title': 'Remover este imóvel'
            },
            'collection': {
                'href': url_for('listar_todos_imoveis_route', _external=True),
                'method': 'GET',
                'title': 'Listar todos os imóveis'
            },
            'create_similar': {
                'href': url_for('criar_imovel_route', _external=True),
                'method': 'POST',
                'title': 'Criar imóvel similar'
            }
        }
        
        # Use OrderedDict for the response
        response_data = OrderedDict([
            ('success', True),
            ('message', 'Imóvel atualizado com sucesso'),
            ('data', enhanced_imovel),
            ('link', update_links)
        ])
        
        return jsonify(response_data), 200
        
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
                'message': f'Nenhum imóvel encontrado com ID {imovel_id}',
                'link': {
                    'collection': {
                        'href': url_for('listar_todos_imoveis_route', _external=True),
                        'method': 'GET',
                        'title': 'Listar todos os imóveis'
                    },
                    'create': {
                        'href': url_for('criar_imovel_route', _external=True),
                        'method': 'POST',
                        'title': 'Criar novo imóvel'
                    }
                }
            }), 404
        
        # Deletar imóvel
        sucesso = deletar_imovel(imovel_id)
        
        if not sucesso:
            return jsonify({
                'success': False,
                'error': 'Falha na remoção',
                'message': 'Não foi possível remover o imóvel',
                'link': build_imovel_links(imovel_id)
            }), 500
        
        # Build links for after deletion
        deletion_links = {
            'collection': {
                'href': url_for('listar_todos_imoveis_route', _external=True),
                'method': 'GET',
                'title': 'Listar todos os imóveis'
            },
            'create': {
                'href': url_for('criar_imovel_route', _external=True),
                'method': 'POST',
                'title': 'Criar novo imóvel'
            },
            'create_similar': {
                'href': url_for('criar_imovel_route', _external=True),
                'method': 'POST',
                'title': 'Criar imóvel similar ao removido'
            }
        }
        
        # Use OrderedDict for the response
        response_data = OrderedDict([
            ('success', True),
            ('message', f'Imóvel com ID {imovel_id} removido com sucesso',
            'data', imovel_existe),
            ('link', deletion_links)
        ])
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return handle_database_error(e)

# 6. Listar imóveis por tipo
@app.route('/imoveis/tipo/<tipo>', methods=['GET'])
def listar_imoveis_por_tipo_route(tipo):
    """Lista todos os imóveis de um tipo específico"""
    try:
        imoveis = listar_imoveis_por_tipo(tipo)
        
        # Add HATEOAS links to each imovel
        enhanced_imoveis = enhance_imoveis_collection_with_links(imoveis)
        
        # Build specific links for this filtered collection
        filter_links = {
            'self': {
                'href': url_for('listar_imoveis_por_tipo_route', tipo=tipo, _external=True),
                'method': 'GET',
                'title': f'Imóveis do tipo "{tipo}"'
            },
            'collection': {
                'href': url_for('listar_todos_imoveis_route', _external=True),
                'method': 'GET',
                'title': 'Todos os imóveis'
            },
            'create': {
                'href': url_for('criar_imovel_route', _external=True),
                'method': 'POST',
                'title': 'Criar novo imóvel'
            },
            'search_by_city': {
                'href': url_for('listar_imoveis_por_cidade_route', cidade='{cidade}', _external=True).replace('%7Bcidade%7D', '{cidade}'),
                'method': 'GET',
                'title': 'Buscar imóveis por cidade',
                'templated': True
            }
        }
        
        # Use OrderedDict to control response structure
        response_data = OrderedDict([
            ('success', True),
            ('message', f'{len(enhanced_imoveis)} imóveis do tipo "{tipo}" encontrados'),
            ('total', len(enhanced_imoveis)),
            ('filtro', {'tipo': tipo}),
            ('link', filter_links),

            ('data', enhanced_imoveis),
        ])
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return handle_database_error(e)

# 7. Listar imóveis por cidade
@app.route('/imoveis/cidade/<cidade>', methods=['GET'])
def listar_imoveis_por_cidade_route(cidade):
    """Lista todos os imóveis de uma cidade específica"""
    try:
        imoveis = listar_imoveis_por_cidade(cidade)
        
        # Add HATEOAS links to each imovel
        enhanced_imoveis = enhance_imoveis_collection_with_links(imoveis)
        
        # Build specific links for this filtered collection
        filter_links = {
            'self': {
                'href': url_for('listar_imoveis_por_cidade_route', cidade=cidade, _external=True),
                'method': 'GET',
                'title': f'Imóveis da cidade "{cidade}"'
            },
            'collection': {
                'href': url_for('listar_todos_imoveis_route', _external=True),
                'method': 'GET',
                'title': 'Todos os imóveis'
            },
            'create': {
                'href': url_for('criar_imovel_route', _external=True),
                'method': 'POST',
                'title': 'Criar novo imóvel'
            },
            'search_by_type': {
                'href': url_for('listar_imoveis_por_tipo_route', tipo='{tipo}', _external=True).replace('%7Btipo%7D', '{tipo}'),
                'method': 'GET',
                'title': 'Buscar imóveis por tipo',
                'templated': True
            }
        }
        
        # Use OrderedDict to control response structure
        response_data = OrderedDict([
            ('success', True),
            ('message', f'{len(enhanced_imoveis)} imóveis na cidade "{cidade}" encontrados'),
            ('total', len(enhanced_imoveis)),
            ('filtro', {'cidade': cidade}),
            ('link', filter_links),
            ('data', enhanced_imoveis),
        ])
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return handle_database_error(e)

# Rota para verificar health da API
@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se a API está funcionando"""
    try:
        # Tenta fazer uma consulta simples no banco
        imoveis = listar_todos_imoveis()
        
        health_links = {
            'self': {
                'href': url_for('health_check', _external=True),
                'method': 'GET',
                'title': 'Status da API'
            },
            'api_root': {
                'href': url_for('api_info', _external=True),
                'method': 'GET',
                'title': 'Informações da API'
            },
            'imoveis': {
                'href': url_for('listar_todos_imoveis_route', _external=True),
                'method': 'GET',
                'title': 'Listar imóveis'
            }
        }
        
        return jsonify({
            'status': 'healthy',
            'message': 'API funcionando corretamente',
            'database': 'connected',
            'total_imoveis': len(imoveis),
            'timestamp': datetime.now().isoformat(),
            'link': health_links
        }), 200
    except Exception as e:
        error_links = {
            'self': {
                'href': url_for('health_check', _external=True),
                'method': 'GET',
                'title': 'Status da API'
            },
            'api_root': {
                'href': url_for('api_info', _external=True),
                'method': 'GET',
                'title': 'Informações da API'
            }
        }
        
        return jsonify({
            'status': 'unhealthy',
            'message': 'Problemas na API',
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'link': error_links
        }), 503

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
