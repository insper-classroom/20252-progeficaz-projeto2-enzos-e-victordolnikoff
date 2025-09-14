#!/usr/bin/env python3
"""
Quick MySQL database health check script
Run this script to quickly verify if your database is working
"""

import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def quick_health_check():
    """Perform a quick health check on the MySQL database"""
    
    print("🔍 MySQL Database Health Check")
    print("=" * 40)
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check environment variables
    print("📋 Environment Variables:")
    env_vars = {
        'DB_HOST': os.getenv('DB_HOST', 'NOT SET'),
        'DB_PORT': os.getenv('DB_PORT', 'NOT SET'),
        'DB_USER': os.getenv('DB_USER', 'NOT SET'),
        'DB_PASSWORD': '***' if os.getenv('DB_PASSWORD') else 'NOT SET',
        'DB_NAME': os.getenv('DB_NAME', 'NOT SET')
    }
    
    for key, value in env_vars.items():
        status = "✅" if value != "NOT SET" else "❌"
        print(f"   {status} {key}: {value}")
    
    # Check for missing variables
    missing = [k for k, v in env_vars.items() if v == "NOT SET" and k != 'DB_PASSWORD']
    if missing:
        print(f"\n❌ Missing required variables: {', '.join(missing)}")
        return False
    
    print()
    
    # Test database connection
    print("🔗 Database Connection:")
    connection = None
    
    try:
        config = {
            'host': os.getenv('DB_HOST'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME'),
            'connect_timeout': 10
        }
        
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            print("   ✅ Connection established successfully")
            
            # Get server info
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            print(f"   📊 MySQL Version: {version}")
            
            # Check database
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()[0]
            print(f"   🗄️  Database: {db_name}")
            
            # Check table existence
            cursor.execute("SHOW TABLES LIKE 'imoveis'")
            table_exists = cursor.fetchone()
            
            if table_exists:
                print("   ✅ Table 'imoveis' exists")
                
                # Count records
                cursor.execute("SELECT COUNT(*) FROM imoveis")
                count = cursor.fetchone()[0]
                print(f"   📈 Records in table: {count}")
                
                # Test a simple query
                if count > 0:
                    cursor.execute("SELECT id, logradouro, cidade FROM imoveis LIMIT 1")
                    sample = cursor.fetchone()
                    print(f"   🏠 Sample record: ID={sample[0]}, {sample[1]}, {sample[2]}")
                
                health_status = "HEALTHY 🟢"
            else:
                print("   ⚠️  Table 'imoveis' does not exist")
                health_status = "NEEDS SETUP 🟡"
            
            cursor.close()
            
        else:
            print("   ❌ Failed to establish connection")
            health_status = "UNHEALTHY 🔴"
            
    except Error as e:
        print(f"   ❌ Database error: {e}")
        health_status = "UNHEALTHY 🔴"
        
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        health_status = "UNHEALTHY 🔴"
        
    finally:
        if connection and connection.is_connected():
            connection.close()
    
    print()
    print("🎯 Overall Status:")
    print(f"   {health_status}")
    print()
    
    return "HEALTHY" in health_status


def show_setup_help():
    """Show setup instructions if health check fails"""
    print("🛠️  Setup Instructions:")
    print("=" * 40)
    print()
    print("1. Create .env file with:")
    print("""
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=imoveis_db
""")
    print("2. Create database and import schema:")
    print("   mysql -u username -p")
    print("   CREATE DATABASE imoveis_db;")
    print("   USE imoveis_db;")
    print("   SOURCE imoveis.sql;")
    print()
    print("3. Run this script again to verify setup")


if __name__ == "__main__":
    success = quick_health_check()
    
    if not success:
        show_setup_help()
    
    exit(0 if success else 1)