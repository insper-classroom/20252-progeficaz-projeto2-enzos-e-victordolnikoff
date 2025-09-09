import pytest
import json
import sqlite3
import os


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
    # Testa buscar um imóvel que existe
    imovel = listar_imovel_por_id(1)
    assert imovel is not None
    assert imovel['id'] == 1
    assert 'logradouro' in imovel
    assert 'cidade' in imovel
    
    # Testa buscar um imóvel que não existe
    imovel_inexistente = listar_imovel_por_id(99999)
    assert imovel_inexistente is None
    
    # Testa se retorna o imóvel correto
    imovel_especifico = listar_imovel_por_id(5)
    assert imovel_especifico is not None
    assert imovel_especifico['id'] == 5


def test_novo_imovel():
    # Conta quantos imóveis existem antes da inserção
    imoveis_antes = listar_todos_imoveis()
    count_antes = len(imoveis_antes)
    
    # Insere um novo imóvel
    novo_id = inserir_imovel(
        logradouro="Rua de Teste",
        tipo_logradouro="Rua",
        bairro="Bairro Teste",
        cidade="Cidade Teste",
        cep="12345-678",
        tipo="casa",
        valor=500000.00,
        data_aquisicao="2024-01-01"
    )
    
    # Verifica se o ID foi retornado
    assert novo_id is not None
    assert isinstance(novo_id, int)
    
    # Verifica se o imóvel foi inserido
    imovel_inserido = listar_imovel_por_id(novo_id)
    assert imovel_inserido is not None
    assert imovel_inserido['logradouro'] == "Rua de Teste"
    assert imovel_inserido['cidade'] == "Cidade Teste"
    assert imovel_inserido['tipo'] == "casa"
    
    # Verifica se o número de imóveis aumentou
    imoveis_depois = listar_todos_imoveis()
    count_depois = len(imoveis_depois)
    assert count_depois == count_antes + 1
    
    # Remove o imóvel teste para não afetar outros testes
    deletar_imovel(novo_id)


def test_atualizar_imovel():
    # Insere um imóvel para testar a atualização
    teste_id = inserir_imovel(
        logradouro="Rua Original",
        tipo_logradouro="Rua",
        bairro="Bairro Original",
        cidade="Cidade Original",
        cep="11111-111",
        tipo="casa",
        valor=400000.00,
        data_aquisicao="2023-01-01"
    )
    
    # Verifica se o imóvel foi inserido
    imovel_original = listar_imovel_por_id(teste_id)
    assert imovel_original is not None
    assert imovel_original['logradouro'] == "Rua Original"
    assert imovel_original['valor'] == 400000.00
    
    # Testa atualização de um campo único (logradouro)
    resultado = atualizar_imovel(teste_id, logradouro="Rua Atualizada")
    assert resultado is True
    
    # Verifica se a atualização foi aplicada
    imovel_atualizado = listar_imovel_por_id(teste_id)
    assert imovel_atualizado['logradouro'] == "Rua Atualizada"
    assert imovel_atualizado['cidade'] == "Cidade Original"  # Outros campos inalterados
    
    # Testa atualização de múltiplos campos
    resultado = atualizar_imovel(
        teste_id, 
        cidade="Cidade Nova",
        valor=550000.00,
        tipo="apartamento"
    )
    assert resultado is True
    
    # Verifica as múltiplas atualizações
    imovel_multi_atualizado = listar_imovel_por_id(teste_id)
    assert imovel_multi_atualizado['cidade'] == "Cidade Nova"
    assert imovel_multi_atualizado['valor'] == 550000.00
    assert imovel_multi_atualizado['tipo'] == "apartamento"
    assert imovel_multi_atualizado['logradouro'] == "Rua Atualizada"  # Mantém atualização anterior
    
    # Testa atualização de imóvel inexistente
    resultado_inexistente = atualizar_imovel(99999, logradouro="Teste Falha")
    assert resultado_inexistente is False
    
    # Testa chamada sem parâmetros de atualização
    resultado_vazio = atualizar_imovel(teste_id)
    assert resultado_vazio is False
    
    # Remove o imóvel teste para não afetar outros testes
    deletar_imovel(teste_id)


def test_del_imovel():
    # Insere um imóvel para testar a deleção
    teste_id = inserir_imovel(
        logradouro="Rua Para Deletar",
        tipo_logradouro="Rua",
        bairro="Bairro Teste",
        cidade="Cidade Teste",
        cep="99999-999",
        tipo="apartamento",
        valor=300000.00,
        data_aquisicao="2024-01-01"
    )
    
    # Verifica se o imóvel foi inserido
    imovel_existe = listar_imovel_por_id(teste_id)
    assert imovel_existe is not None
    
    # Deleta o imóvel
    resultado = deletar_imovel(teste_id)
    assert resultado is True
    
    # Verifica se o imóvel foi deletado
    imovel_deletado = listar_imovel_por_id(teste_id)
    assert imovel_deletado is None
    
    # Tenta deletar um imóvel que não existe
    resultado_inexistente = deletar_imovel(99999)
    assert resultado_inexistente is False


def test_listar_imoveis_tipo():
    # Testa listar imóveis do tipo "casa"
    casas = listar_imoveis_por_tipo("casa")
    assert isinstance(casas, list)
    
    # Se existem casas, verifica se todas são do tipo "casa"
    if len(casas) > 0:
        for casa in casas:
            assert casa['tipo'] == "casa"
            assert 'id' in casa
            assert 'logradouro' in casa
    
    # Testa listar imóveis do tipo "apartamento"
    apartamentos = listar_imoveis_por_tipo("apartamento")
    assert isinstance(apartamentos, list)
    
    if len(apartamentos) > 0:
        for apartamento in apartamentos:
            assert apartamento['tipo'] == "apartamento"
    
    # Testa tipo que não existe
    inexistentes = listar_imoveis_por_tipo("mansao")
    assert isinstance(inexistentes, list)
    assert len(inexistentes) == 0


def test_listar_imoveis_cidade():
    # Primeiro, pega todas as cidades disponíveis
    todos_imoveis = listar_todos_imoveis()
    assert len(todos_imoveis) > 0
    
    # Pega a cidade do primeiro imóvel
    cidade_teste = todos_imoveis[0]['cidade']
    
    # Lista imóveis dessa cidade
    imoveis_cidade = listar_imoveis_por_cidade(cidade_teste)
    assert isinstance(imoveis_cidade, list)
    assert len(imoveis_cidade) > 0
    
    # Verifica se todos os imóveis são da cidade correta
    for imovel in imoveis_cidade:
        assert imovel['cidade'] == cidade_teste
        assert 'id' in imovel
        assert 'logradouro' in imovel
    
    # Testa cidade que não existe
    cidade_inexistente = listar_imoveis_por_cidade("Cidade Inexistente")
    assert isinstance(cidade_inexistente, list)
    assert len(cidade_inexistente) == 0