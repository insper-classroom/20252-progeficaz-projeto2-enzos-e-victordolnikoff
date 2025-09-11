#!/usr/bin/env python3
"""
Test script to demonstrate MySQL database connectivity
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test MySQL database connection"""
    
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

if __name__ == "__main__":
    success = test_database_connection()
    
    if not success:
        show_environment_setup()
    
    sys.exit(0 if success else 1)
