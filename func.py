import sqlite3
import os


def listar_todos_imoveis(db_path="imoveis.db"):
    
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database não encontrada: {db_path}")
    
    try:
        # Conecta à database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Query para buscar todos os imóveis
        cursor.execute("""
            SELECT id, logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao
            FROM imoveis
            ORDER BY id
        """)
        
        # Busca todos os resultados
        rows = cursor.fetchall()
        
        # Converte para lista de dicionários
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
                'valor': row[7],
                'data_aquisicao': row[8]
            }
            imoveis.append(imovel)
        
        conn.close()
        return imoveis
        
    except sqlite3.Error as e:
        if 'conn' in locals():
            conn.close()
        raise Exception(f"Erro ao acessar a database: {e}")


def listar_imovel_por_id(imovel_id, db_path="imoveis.db"):
    """
    Busca um imóvel específico pelo ID
    
    Args:
        imovel_id (int): ID do imóvel a ser buscado
        db_path (str): Caminho para o arquivo da database
        
    Returns:
        dict or None: Dicionário com os dados do imóvel ou None se não encontrado
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database não encontrada: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao
            FROM imoveis
            WHERE id = ?
        """, (imovel_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'logradouro': row[1],
                'tipo_logradouro': row[2],
                'bairro': row[3],
                'cidade': row[4],
                'cep': row[5],
                'tipo': row[6],
                'valor': row[7],
                'data_aquisicao': row[8]
            }
        return None
        
    except sqlite3.Error as e:
        if 'conn' in locals():
            conn.close()
        raise Exception(f"Erro ao acessar a database: {e}")


def inserir_imovel(logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao, db_path="imoveis.db"):
    """
    Insere um novo imóvel na database
    
    Args:
        logradouro (str): Nome da rua/logradouro
        tipo_logradouro (str): Tipo do logradouro (Rua, Avenida, etc.)
        bairro (str): Nome do bairro
        cidade (str): Nome da cidade
        cep (str): CEP do imóvel
        tipo (str): Tipo do imóvel (casa, apartamento, etc.)
        valor (float): Valor do imóvel
        data_aquisicao (str): Data de aquisição no formato YYYY-MM-DD
        db_path (str): Caminho para o arquivo da database
        
    Returns:
        int: ID do imóvel inserido
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database não encontrada: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO imoveis (logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao))
        
        imovel_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return imovel_id
        
    except sqlite3.Error as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        raise Exception(f"Erro ao inserir imóvel: {e}")


def deletar_imovel(imovel_id, db_path="imoveis.db"):
    """
    Remove um imóvel da database pelo ID
    
    Args:
        imovel_id (int): ID do imóvel a ser removido
        db_path (str): Caminho para o arquivo da database
        
    Returns:
        bool: True se o imóvel foi removido, False se não foi encontrado
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database não encontrada: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM imoveis WHERE id = ?", (imovel_id,))
        
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return rows_affected > 0
        
    except sqlite3.Error as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        raise Exception(f"Erro ao deletar imóvel: {e}")


def listar_imoveis_por_tipo(tipo_imovel, db_path="imoveis.db"):
    """
    Lista todos os imóveis de um tipo específico
    
    Args:
        tipo_imovel (str): Tipo do imóvel (casa, apartamento, terreno, casa em condominio)
        db_path (str): Caminho para o arquivo da database
        
    Returns:
        list: Lista de dicionários com os imóveis do tipo especificado
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database não encontrada: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao
            FROM imoveis
            WHERE tipo = ?
            ORDER BY id
        """, (tipo_imovel,))
        
        rows = cursor.fetchall()
        
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
                'valor': row[7],
                'data_aquisicao': row[8]
            }
            imoveis.append(imovel)
        
        conn.close()
        return imoveis
        
    except sqlite3.Error as e:
        if 'conn' in locals():
            conn.close()
        raise Exception(f"Erro ao acessar a database: {e}")


def listar_imoveis_por_cidade(cidade, db_path="imoveis.db"):
    """
    Lista todos os imóveis de uma cidade específica
    
    Args:
        cidade (str): Nome da cidade
        db_path (str): Caminho para o arquivo da database
        
    Returns:
        list: Lista de dicionários com os imóveis da cidade especificada
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database não encontrada: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao
            FROM imoveis
            WHERE cidade = ?
            ORDER BY id
        """, (cidade,))
        
        rows = cursor.fetchall()
        
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
                'valor': row[7],
                'data_aquisicao': row[8]
            }
            imoveis.append(imovel)
        
        conn.close()
        return imoveis
        
    except sqlite3.Error as e:
        if 'conn' in locals():
            conn.close()
        raise Exception(f"Erro ao acessar a database: {e}")


def atualizar_imovel(imovel_id, logradouro=None, tipo_logradouro=None, bairro=None, 
                    cidade=None, cep=None, tipo=None, valor=None, data_aquisicao=None, db_path="imoveis.db"):
    """
    Atualiza os dados de um imóvel existente na database
    
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
        db_path (str): Caminho para o arquivo da database
        
    Returns:
        bool: True se o imóvel foi atualizado, False se não foi encontrado
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database não encontrada: {db_path}")
    
    # Constrói a query dinamicamente baseado nos campos fornecidos
    campos_atualizacao = []
    valores = []
    
    if logradouro is not None:
        campos_atualizacao.append("logradouro = ?")
        valores.append(logradouro)
    if tipo_logradouro is not None:
        campos_atualizacao.append("tipo_logradouro = ?")
        valores.append(tipo_logradouro)
    if bairro is not None:
        campos_atualizacao.append("bairro = ?")
        valores.append(bairro)
    if cidade is not None:
        campos_atualizacao.append("cidade = ?")
        valores.append(cidade)
    if cep is not None:
        campos_atualizacao.append("cep = ?")
        valores.append(cep)
    if tipo is not None:
        campos_atualizacao.append("tipo = ?")
        valores.append(tipo)
    if valor is not None:
        campos_atualizacao.append("valor = ?")
        valores.append(valor)
    if data_aquisicao is not None:
        campos_atualizacao.append("data_aquisicao = ?")
        valores.append(data_aquisicao)
    
    # Se nenhum campo foi fornecido para atualização
    if not campos_atualizacao:
        return False
    
    # Adiciona o ID no final para a cláusula WHERE
    valores.append(imovel_id)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        query = f"UPDATE imoveis SET {', '.join(campos_atualizacao)} WHERE id = ?"
        cursor.execute(query, valores)
        
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return rows_affected > 0
        
    except sqlite3.Error as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        raise Exception(f"Erro ao atualizar imóvel: {e}")