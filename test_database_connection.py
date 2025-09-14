#!/usr/bin/env python3
"""
Comprehensive MySQL database connectivity and functionality tests
"""

import os
import pytest
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from database_config import DatabaseConfig

# Load environment variables
load_dotenv()

def test_environment_variables():
    """Test that all required environment variables are set"""
    required_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
    
    for var in required_vars:
        value = os.getenv(var)
        assert value is not None, f"Environment variable {var} is not set"
        assert value.strip() != "", f"Environment variable {var} is empty"
    
    print("✅ All required environment variables are set")


def test_database_config():
    """Test that database configuration is valid"""
    config = DatabaseConfig.get_mysql_config()
    
    # Check required fields
    assert config['host'] is not None, "Database host is not configured"
    assert config['user'] is not None, "Database user is not configured"
    assert config['password'] is not None, "Database password is not configured"
    assert config['database'] is not None, "Database name is not configured"
    
    # Check data types
    assert isinstance(config['port'], int), "Database port must be an integer"
    assert 1 <= config['port'] <= 65535, "Database port must be between 1 and 65535"
    
    print("✅ Database configuration is valid")


def test_raw_mysql_connection():
    """Test raw MySQL connection without using application functions"""
    config = DatabaseConfig.get_mysql_config()
    connection = None
    
    try:
        print(f"🔗 Attempting connection to MySQL at {config['host']}:{config['port']}")
        
        connection = mysql.connector.connect(**config)
        
        assert connection.is_connected(), "Failed to establish MySQL connection"
        
        # Test basic query
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        
        assert version is not None, "Failed to fetch MySQL version"
        print(f"✅ Connected to MySQL version: {version[0]}")
        
        cursor.close()
        
    except Error as e:
        pytest.fail(f"MySQL connection failed: {e}")
        
    finally:
        if connection and connection.is_connected():
            connection.close()


def test_database_exists():
    """Test that the target database exists"""
    config = DatabaseConfig.get_mysql_config()
    connection = None
    
    try:
        # Connect without specifying database
        temp_config = config.copy()
        database_name = temp_config.pop('database')
        
        connection = mysql.connector.connect(**temp_config)
        cursor = connection.cursor()
        
        # Check if database exists
        cursor.execute("SHOW DATABASES LIKE %s", (database_name,))
        result = cursor.fetchone()
        
        assert result is not None, f"Database '{database_name}' does not exist"
        print(f"✅ Database '{database_name}' exists")
        
        cursor.close()
        
    except Error as e:
        pytest.fail(f"Failed to check database existence: {e}")
        
    finally:
        if connection and connection.is_connected():
            connection.close()


def test_tables_exist():
    """Test that required tables exist in the database"""
    config = DatabaseConfig.get_mysql_config()
    connection = None
    
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # Check for imoveis table
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = %s AND table_name = 'imoveis'
        """, (config['database'],))
        
        result = cursor.fetchone()
        assert result[0] > 0, "Table 'imoveis' does not exist"
        print("✅ Table 'imoveis' exists")
        
        # Check table structure
        cursor.execute("DESCRIBE imoveis")
        columns = cursor.fetchall()
        
        expected_columns = ['id', 'logradouro', 'tipo_logradouro', 'bairro', 
                          'cidade', 'cep', 'tipo', 'valor', 'data_aquisicao']
        
        actual_columns = [col[0] for col in columns]
        
        for col in expected_columns:
            assert col in actual_columns, f"Column '{col}' is missing from imoveis table"
        
        print(f"✅ Table structure is correct ({len(actual_columns)} columns)")
        
        cursor.close()
        
    except Error as e:
        pytest.fail(f"Failed to check table structure: {e}")
        
    finally:
        if connection and connection.is_connected():
            connection.close()


def test_database_operations():
    """Test basic database operations (CRUD)"""
    config = DatabaseConfig.get_mysql_config()
    connection = None
    
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # Test SELECT
        cursor.execute("SELECT COUNT(*) FROM imoveis")
        count_result = cursor.fetchone()
        assert count_result is not None, "Failed to execute SELECT query"
        print(f"✅ SELECT operation successful - {count_result[0]} records found")
        
        # Test INSERT
        test_data = {
            'logradouro': 'Rua Teste Database',
            'tipo_logradouro': 'Rua',
            'bairro': 'Bairro Teste',
            'cidade': 'Cidade Teste',
            'cep': '00000-000',
            'tipo': 'casa',
            'valor': 999999.99,
            'data_aquisicao': '2024-01-01'
        }
        
        insert_query = """
            INSERT INTO imoveis (logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao)
            VALUES (%(logradouro)s, %(tipo_logradouro)s, %(bairro)s, %(cidade)s, %(cep)s, %(tipo)s, %(valor)s, %(data_aquisicao)s)
        """
        
        cursor.execute(insert_query, test_data)
        test_id = cursor.lastrowid
        assert test_id > 0, "Failed to insert test record"
        print(f"✅ INSERT operation successful - ID: {test_id}")
        
        # Test UPDATE
        cursor.execute(
            "UPDATE imoveis SET valor = %s WHERE id = %s", 
            (888888.88, test_id)
        )
        assert cursor.rowcount == 1, "Failed to update test record"
        print("✅ UPDATE operation successful")
        
        # Test DELETE
        cursor.execute("DELETE FROM imoveis WHERE id = %s", (test_id,))
        assert cursor.rowcount == 1, "Failed to delete test record"
        print("✅ DELETE operation successful")
        
        connection.commit()
        cursor.close()
        
    except Error as e:
        if connection:
            connection.rollback()
        pytest.fail(f"Database operation failed: {e}")
        
    finally:
        if connection and connection.is_connected():
            connection.close()


def test_application_functions():
    """Test that application functions work with the database"""
    try:
        from func import listar_todos_imoveis, listar_imovel_por_id
        
        # Test listing all properties
        imoveis = listar_todos_imoveis()
        assert isinstance(imoveis, list), "listar_todos_imoveis should return a list"
        print(f"✅ Application function test - Found {len(imoveis)} properties")
        
        # Test getting specific property (if any exist)
        if len(imoveis) > 0:
            first_id = imoveis[0]['id']
            imovel = listar_imovel_por_id(first_id)
            assert imovel is not None, "Failed to fetch property by ID"
            assert imovel['id'] == first_id, "Returned property has wrong ID"
            print(f"✅ Application function test - Retrieved property ID {first_id}")
        
    except ImportError as e:
        pytest.fail(f"Failed to import application functions: {e}")
    except Exception as e:
        pytest.fail(f"Application function test failed: {e}")


def test_database_performance():
    """Test basic database performance"""
    import time
    config = DatabaseConfig.get_mysql_config()
    connection = None
    
    try:
        # Test connection time
        start_time = time.time()
        connection = mysql.connector.connect(**config)
        connection_time = time.time() - start_time
        
        assert connection_time < 5.0, f"Connection took too long: {connection_time:.2f}s"
        print(f"✅ Connection established in {connection_time:.3f}s")
        
        # Test query performance
        cursor = connection.cursor()
        start_time = time.time()
        cursor.execute("SELECT COUNT(*) FROM imoveis")
        cursor.fetchone()
        query_time = time.time() - start_time
        
        assert query_time < 2.0, f"Query took too long: {query_time:.2f}s"
        print(f"✅ Query executed in {query_time:.3f}s")
        
        cursor.close()
        
    except Error as e:
        pytest.fail(f"Performance test failed: {e}")
        
    finally:
        if connection and connection.is_connected():
            connection.close()


def test_database_connection():
    """Legacy test function for backward compatibility"""
    
    print("=== MySQL Database Connection Test ===\n")
    
    # Show current configuration
    print("MySQL Configuration:")
    print(f"  Host: {os.getenv('DB_HOST', 'localhost')}")
    print(f"  Port: {os.getenv('DB_PORT', '3306')}")
    print(f"  User: {os.getenv('DB_USER', 'NOT_SET')}")
    print(f"  Password: {'SET' if os.getenv('DB_PASSWORD') else 'NOT_SET'}")
    print(f"  Database: {os.getenv('DB_NAME', 'NOT_SET')}")
    print()
    
    # Check if all required variables are set
    required_vars = ['DB_USER', 'DB_PASSWORD', 'DB_NAME']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"Missing required environment variables: {', '.join(missing)}")
        print("Please set these variables in your .env file")
        return False
    else:
        print(" All MySQL environment variables are set")
    
    # Test the actual connection
    try:
        print("Testing database connection...")
        from func import listar_todos_imoveis
        
        imoveis = listar_todos_imoveis()
        print(f" Connection successful! Found {len(imoveis)} records")
        
        if len(imoveis) > 0:
            print(f"First record: {imoveis[0]['logradouro']} - {imoveis[0]['cidade']}")
        
        return True
        
    except Exception as e:
        print(f"Connection failed: {e}")
        print("\nTroubleshooting tips:")
        print("- Ensure MySQL server is running")
        print("- Check your credentials in .env file")
        print("- Verify the database exists")
        print("- Run the imoveis_mysql.sql script to create tables")
        
        return False

def show_environment_setup():
    """Show how to set up environment for MySQL"""
    
    print("\n=== MySQL Setup Instructions ===\n")
    
    print("1. Create a .env file in the project root:")
    print("""
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_NAME=imoveis_db
""")
    
    print("2. Create the MySQL database and tables:")
    print("   mysql -u your_username -p")
    print("   CREATE DATABASE imoveis_db;")
    print("   USE imoveis_db;")
    print("   SOURCE imoveis_mysql.sql;")
    
    print("\n3. Run this test script again to verify connection")

