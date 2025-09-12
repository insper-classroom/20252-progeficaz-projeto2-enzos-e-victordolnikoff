import mysql.connector
from mysql.connector import Error as MySQLError
from database_config import DatabaseConfig


def get_database_connection():
    """
    Get MySQL database connection.
    Returns connection object.
    """
    DatabaseConfig.validate_mysql_config()
    config = DatabaseConfig.get_mysql_config()
    try:
        conn = mysql.connector.connect(**config)
        return conn
    except MySQLError as e:
        raise Exception(f"Erro ao conectar com MySQL: {e}")


def execute_query(query, params=None, fetch_one=False, fetch_all=False, get_lastrowid=False):
    """
    Execute a MySQL database query with proper connection handling.
    
    Args:
        query (str): SQL query to execute
        params (tuple, optional): Parameters for the query
        fetch_one (bool): Whether to fetch one row
        fetch_all (bool): Whether to fetch all rows
        get_lastrowid (bool): Whether to return the last inserted row ID
        
    Returns:
        Query result based on the fetch parameters
    """
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        result = None
        
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        elif get_lastrowid:
            result = cursor.lastrowid
        else:
            # For UPDATE/DELETE operations, return affected rows
            result = cursor.rowcount
        
        conn.commit()
        return result
        
    except MySQLError as e:
        conn.rollback()
        raise Exception(f"Erro na operação do banco de dados: {e}")
    finally:
        cursor.close()
        conn.close()


def listar_todos_imoveis():
    """
    Lista todos os imóveis da database
    
    Returns:
        list: Lista de dicionários com todos os imóveis
    """
    query = """
        SELECT id, logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao
        FROM imoveis
        ORDER BY id
    """
    
    rows = execute_query(query, fetch_all=True)
    
    imoveis = []
    for row in rows:
        imovel = {
            'id': row[0],
            'logradouro': row[1],
            'tipo_logradouro': row[2],
            'bairro': row[3],
            'cidade': row[4],
            'cep': row[5],
            'tipo': row[6],
            'valor': float(row[7]) if row[7] is not None else None,
            'data_aquisicao': row[8]
        }
        imoveis.append(imovel)
    
    return imoveis


def listar_imovel_por_id(imovel_id):
    """
    Busca um imóvel específico pelo ID no banco MySQL
    
    Args:
        imovel_id (int): ID do imóvel a ser buscado
        
    Returns:
        dict or None: Dicionário com os dados do imóvel ou None se não encontrado
    """
    query = """
        SELECT id, logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao
        FROM imoveis
        WHERE id = %s
    """
    
    row = execute_query(query, params=(imovel_id,), fetch_one=True)
    
    if row:
        return {
            'id': row[0],
            'logradouro': row[1],
            'tipo_logradouro': row[2],
            'bairro': row[3],
            'cidade': row[4],
            'cep': row[5],
            'tipo': row[6],
            'valor': float(row[7]) if row[7] is not None else None,
            'data_aquisicao': row[8]
        }
    return None


def inserir_imovel(logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao):
    """
    Insere um novo imóvel na database MySQL
    
    Args:
        logradouro (str): Nome da rua/logradouro
        tipo_logradouro (str): Tipo do logradouro (Rua, Avenida, etc.)
        bairro (str): Nome do bairro
        cidade (str): Nome da cidade
        cep (str): CEP do imóvel
        tipo (str): Tipo do imóvel (casa, apartamento, etc.)
        valor (float): Valor do imóvel
        data_aquisicao (str): Data de aquisição no formato YYYY-MM-DD
        
    Returns:
        int: ID do imóvel inserido
    """
    query = """
        INSERT INTO imoveis (logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao)
    
    return execute_query(query, params, get_lastrowid=True)


def deletar_imovel(imovel_id):
    """
    Remove um imóvel da database MySQL pelo ID
    
    Args:
        imovel_id (int): ID do imóvel a ser removido
        
    Returns:
        bool: True se o imóvel foi removido, False se não foi encontrado
    """
    query = "DELETE FROM imoveis WHERE id = %s"
    
    rows_affected = execute_query(query, params=(imovel_id,))
    
    return rows_affected > 0


def listar_imoveis_por_tipo(tipo_imovel):
    """
    Lista todos os imóveis de um tipo específico no banco MySQL
    
    Args:
        tipo_imovel (str): Tipo do imóvel (casa, apartamento, terreno, casa em condominio)
        
    Returns:
        list: Lista de dicionários com os imóveis do tipo especificado
    """
    query = """
        SELECT id, logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao
        FROM imoveis
        WHERE tipo = %s
        ORDER BY id
    """
    
    rows = execute_query(query, params=(tipo_imovel,), fetch_all=True)
    
    imoveis = []
    for row in rows:
        imovel = {
            'id': row[0],
            'logradouro': row[1],
            'tipo_logradouro': row[2],
            'bairro': row[3],
            'cidade': row[4],
            'cep': row[5],
            'tipo': row[6],
            'valor': float(row[7]) if row[7] is not None else None,
            'data_aquisicao': row[8]
        }
        imoveis.append(imovel)
    
    return imoveis


def listar_imoveis_por_cidade(cidade):
    """
    Lista todos os imóveis de uma cidade específica no banco MySQL
    
    Args:
        cidade (str): Nome da cidade
        
    Returns:
        list: Lista de dicionários com os imóveis da cidade especificada
    """
    query = """
        SELECT id, logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao
        FROM imoveis
        WHERE cidade = %s
        ORDER BY id
    """
    
    rows = execute_query(query, params=(cidade,), fetch_all=True)
    
    imoveis = []
    for row in rows:
        imovel = {
            'id': row[0],
            'logradouro': row[1],
            'tipo_logradouro': row[2],
            'bairro': row[3],
            'cidade': row[4],
            'cep': row[5],
            'tipo': row[6],
            'valor': float(row[7]) if row[7] is not None else None,
            'data_aquisicao': row[8]
        }
        imoveis.append(imovel)
    
    return imoveis


def atualizar_imovel(imovel_id, logradouro=None, tipo_logradouro=None, bairro=None, 
                    cidade=None, cep=None, tipo=None, valor=None, data_aquisicao=None):
    """
    Atualiza os dados de um imóvel existente na database MySQL
    
    Args:
        imovel_id (int): ID do imóvel a ser atualizado
        logradouro (str, optional): Novo nome da rua/logradouro
        tipo_logradouro (str, optional): Novo tipo do logradouro
        bairro (str, optional): Novo nome do bairro
        cidade (str, optional): Nova nome da cidade
        cep (str, optional): Novo CEP do imóvel
        tipo (str, optional): Novo tipo do imóvel
        valor (float, optional): Novo valor do imóvel
        data_aquisicao (str, optional): Nova data de aquisição
        
    Returns:
        bool: True se o imóvel foi atualizado, False se não foi encontrado
    """
    # Constrói a query dinamicamente baseado nos campos fornecidos
    campos_atualizacao = []
    valores = []
    
    if logradouro is not None:
        campos_atualizacao.append("logradouro = %s")
        valores.append(logradouro)
    if tipo_logradouro is not None:
        campos_atualizacao.append("tipo_logradouro = %s")
        valores.append(tipo_logradouro)
    if bairro is not None:
        campos_atualizacao.append("bairro = %s")
        valores.append(bairro)
    if cidade is not None:
        campos_atualizacao.append("cidade = %s")
        valores.append(cidade)
    if cep is not None:
        campos_atualizacao.append("cep = %s")
        valores.append(cep)
    if tipo is not None:
        campos_atualizacao.append("tipo = %s")
        valores.append(tipo)
    if valor is not None:
        campos_atualizacao.append("valor = %s")
        valores.append(valor)
    if data_aquisicao is not None:
        campos_atualizacao.append("data_aquisicao = %s")
        valores.append(data_aquisicao)
    
    # Se nenhum campo foi fornecido para atualização
    if not campos_atualizacao:
        return False
    
    # Adiciona o ID no final para a cláusula WHERE
    valores.append(imovel_id)
    
    query = f"UPDATE imoveis SET {', '.join(campos_atualizacao)} WHERE id = %s"
    rows_affected = execute_query(query, params=valores)
    
    return rows_affected > 0