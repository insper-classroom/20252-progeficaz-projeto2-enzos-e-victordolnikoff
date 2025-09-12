from flask import Flask, jsonify, request
from func import *
import os

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
        }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

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
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

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
            }), 400
        
        # Validar tipos de dados
        try:
            valor = float(data['valor'])
            if valor < 0:
                return jsonify({
                    'success': False,
                    'error': 'Valor inválido',
                    'message': 'O valor deve ser um número positivo'
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Valor inválido',
                'message': 'O valor deve ser um número válido'
            }), 400
        
        # Inserir imóvel
        novo_id = inserir_imovel(
            logradouro=str(data['logradouro']).strip(),
            tipo_logradouro=str(data['tipo_logradouro']).strip(),
            bairro=str(data['bairro']).strip(),
            cidade=str(data['cidade']).strip(),
            cep=str(data['cep']).strip(),
            tipo=str(data['tipo']).strip(),
            valor=valor,
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
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

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
            update_args['tipo'] = str(data['tipo']).strip()
        if 'data_aquisicao' in data:
            update_args['data_aquisicao'] = str(data['data_aquisicao']).strip()
            
        # Validar valor se fornecido
        if 'valor' in data:
            try:
                valor = float(data['valor'])
                if valor < 0:
                    return jsonify({
                        'success': False,
                        'error': 'Valor inválido',
                        'message': 'O valor deve ser um número positivo'
                    }), 400
                update_args['valor'] = valor
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'error': 'Valor inválido',
                    'message': 'O valor deve ser um número válido'
                }), 400
        
        # Verificar se há campos para atualizar
        if not update_args:
            return jsonify({
                'success': False,
                'error': 'Nenhum campo para atualizar',
                'message': 'Pelo menos um campo deve ser fornecido para atualização'
            }), 400
        
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
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

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
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

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
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

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
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

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
        }), 500

if __name__ == '__main__':


    app.run(debug=True, host='0.0.0.0', port=5000)
