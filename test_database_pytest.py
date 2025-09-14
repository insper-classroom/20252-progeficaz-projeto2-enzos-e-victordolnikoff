"""
Pytest-specific database tests for the Imoveis API
Run with: pytest test_database_pytest.py -v
"""

import pytest
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from database_config import DatabaseConfig

# Load environment variables
load_dotenv()


class TestDatabaseConnection:
    """Test class for database connectivity"""
    
    @pytest.fixture(scope="class")
    def db_config(self):
        """Fixture to provide database configuration"""
        return DatabaseConfig.get_mysql_config()
    
    def test_environment_setup(self):
        """Test that environment is properly configured"""
        required_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
        
        for var in required_vars:
            assert os.getenv(var) is not None, f"Missing environment variable: {var}"
    
    def test_database_connection(self, db_config):
        """Test basic database connection"""
        connection = None
        try:
            connection = mysql.connector.connect(**db_config)
            assert connection.is_connected()
            
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1
            cursor.close()
            
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def test_database_exists(self, db_config):
        """Test that the target database exists"""
        connection = None
        try:
            temp_config = db_config.copy()
            database_name = temp_config.pop('database')
            
            connection = mysql.connector.connect(**temp_config)
            cursor = connection.cursor()
            
            cursor.execute("SHOW DATABASES LIKE %s", (database_name,))
            result = cursor.fetchone()
            assert result is not None, f"Database '{database_name}' does not exist"
            cursor.close()
            
        finally:
            if connection and connection.is_connected():
                connection.close()


class TestDatabaseSchema:
    """Test class for database schema validation"""
    
    @pytest.fixture(scope="class")
    def connection(self):
        """Fixture to provide database connection"""
        config = DatabaseConfig.get_mysql_config()
        conn = mysql.connector.connect(**config)
        yield conn
        conn.close()
    
    def test_imoveis_table_exists(self, connection):
        """Test that imoveis table exists"""
        cursor = connection.cursor()
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE() AND table_name = 'imoveis'
        """)
        result = cursor.fetchone()
        assert result[0] == 1, "Table 'imoveis' does not exist"
        cursor.close()
    
    def test_imoveis_table_structure(self, connection):
        """Test imoveis table has correct structure"""
        cursor = connection.cursor()
        cursor.execute("DESCRIBE imoveis")
        columns = cursor.fetchall()
        
        expected_columns = ['id', 'logradouro', 'tipo_logradouro', 'bairro', 
                          'cidade', 'cep', 'tipo', 'valor', 'data_aquisicao']
        
        actual_columns = [col[0] for col in columns]
        
        for expected_col in expected_columns:
            assert expected_col in actual_columns, f"Missing column: {expected_col}"
        
        cursor.close()
    
    def test_primary_key_exists(self, connection):
        """Test that primary key is properly configured"""
        cursor = connection.cursor()
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'imoveis' 
            AND COLUMN_KEY = 'PRI'
        """)
        result = cursor.fetchone()
        assert result is not None, "No primary key found on imoveis table"
        assert result[0] == 'id', "Primary key should be 'id' column"
        cursor.close()


class TestDatabaseOperations:
    """Test class for database CRUD operations"""
    
    @pytest.fixture(scope="class")
    def connection(self):
        """Fixture to provide database connection"""
        config = DatabaseConfig.get_mysql_config()
        conn = mysql.connector.connect(**config)
        yield conn
        conn.close()
    
    def test_select_operation(self, connection):
        """Test SELECT operation"""
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM imoveis")
        result = cursor.fetchone()
        assert result is not None
        assert isinstance(result[0], int)
        cursor.close()
    
    def test_insert_and_delete_operation(self, connection):
        """Test INSERT and DELETE operations"""
        cursor = connection.cursor()
        
        # Insert test data
        test_data = {
            'logradouro': 'Pytest Test Street',
            'tipo_logradouro': 'Rua',
            'bairro': 'Test Neighborhood',
            'cidade': 'Test City',
            'cep': '12345-678',
            'tipo': 'casa',
            'valor': 500000.00,
            'data_aquisicao': '2024-01-01'
        }
        
        insert_query = """
            INSERT INTO imoveis (logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao)
            VALUES (%(logradouro)s, %(tipo_logradouro)s, %(bairro)s, %(cidade)s, %(cep)s, %(tipo)s, %(valor)s, %(data_aquisicao)s)
        """
        
        cursor.execute(insert_query, test_data)
        test_id = cursor.lastrowid
        assert test_id > 0
        
        # Verify insert
        cursor.execute("SELECT logradouro FROM imoveis WHERE id = %s", (test_id,))
        result = cursor.fetchone()
        assert result[0] == 'Pytest Test Street'
        
        # Clean up
        cursor.execute("DELETE FROM imoveis WHERE id = %s", (test_id,))
        assert cursor.rowcount == 1
        
        connection.commit()
        cursor.close()


class TestApplicationIntegration:
    """Test class for application function integration"""
    
    def test_import_functions(self):
        """Test that application functions can be imported"""
        try:
            from func import (listar_todos_imoveis, listar_imovel_por_id, 
                            inserir_imovel, atualizar_imovel, deletar_imovel)
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import application functions: {e}")
    
    def test_list_all_imoveis(self):
        """Test listar_todos_imoveis function"""
        from func import listar_todos_imoveis
        
        result = listar_todos_imoveis()
        assert isinstance(result, list)
        
        if len(result) > 0:
            # Check first item structure
            item = result[0]
            required_keys = ['id', 'logradouro', 'cidade', 'tipo', 'valor']
            for key in required_keys:
                assert key in item, f"Missing key '{key}' in result"
    
    def test_database_functions_integration(self):
        """Test full CRUD cycle with application functions"""
        from func import inserir_imovel, listar_imovel_por_id, deletar_imovel
        
        # Insert test property
        test_id = inserir_imovel(
            logradouro="Pytest Integration Test",
            tipo_logradouro="Rua",
            bairro="Test Bairro",
            cidade="Test Cidade",
            cep="00000-000",
            tipo="apartamento",
            valor=750000.00,
            data_aquisicao="2024-01-01"
        )
        
        assert test_id is not None
        assert isinstance(test_id, int)
        
        # Retrieve the property
        imovel = listar_imovel_por_id(test_id)
        assert imovel is not None
        assert imovel['id'] == test_id
        assert imovel['logradouro'] == "Pytest Integration Test"
        
        # Clean up
        success = deletar_imovel(test_id)
        assert success is True


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v", "--tb=short"])