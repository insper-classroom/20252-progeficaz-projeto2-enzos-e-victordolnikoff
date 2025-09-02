import pytest
import json
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


def exibir_todos_imoveis(db_path="imoveis.db"):
    """
    Exibe todos os imóveis e seus atributos da database de forma formatada
    
    Args:
        db_path (str): Caminho para o arquivo da database
    """
    try:
        imoveis = listar_todos_imoveis(db_path)
        
        if not imoveis:
            print("Nenhum imóvel encontrado na database.")
            return
        
        print(f"\n📋 LISTA DE TODOS OS IMÓVEIS ({len(imoveis)} encontrados)")
        print("=" * 80)
        
        for imovel in imoveis:
            print(f"\n🏠 ID: {imovel['id']}")
            print(f"   Endereço: {imovel['tipo_logradouro']} {imovel['logradouro']}")
            print(f"   Bairro: {imovel['bairro']}")
            print(f"   Cidade: {imovel['cidade']}")
            print(f"   CEP: {imovel['cep']}")
            print(f"   Tipo: {imovel['tipo']}")
            print(f"   Valor: R$ {imovel['valor']:,.2f}")
            print(f"   Data de Aquisição: {imovel['data_aquisicao']}")
            print("-" * 60)
            
    except Exception as e:
        print(f"Erro ao exibir imóveis: {e}")


def test_listar_imoveis():
    # Testa se a função retorna uma lista
    imoveis = listar_todos_imoveis()
    assert isinstance(imoveis, list)
    
    # Testa se há imóveis na database
    assert len(imoveis) > 0
    
    # Testa se cada imóvel tem os atributos necessários
    imovel = imoveis[0]
    required_keys = ['id', 'logradouro', 'tipo_logradouro', 'bairro', 'cidade', 'cep', 'tipo', 'valor', 'data_aquisicao']
    for key in required_keys:
        assert key in imovel 


def test_listar_imoveis_id():
    return


def test_novo_imovel():
    return


def test_del_imovel():
    return


def test_listar_imoveis_tipo():
    return


def test_listar_imoveis_cidade():
    return

