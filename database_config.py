import os
from typing import Dict, Any

class DatabaseConfig:
    """
    MySQL database configuration class
    """
    
    @staticmethod
    def get_mysql_config() -> Dict[str, Any]:
        """
        Get MySQL database configuration from environment variables.
        Set these environment variables before running the application:
        
        DB_HOST: MySQL server host (default: localhost)
        DB_PORT: MySQL server port (default: 3306)
        DB_USER: MySQL username
        DB_PASSWORD: MySQL password
        DB_NAME: MySQL database name
        """
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME'),
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci',
            'autocommit': False,
            'raise_on_warnings': True
        }
    
    @staticmethod
    def validate_mysql_config() -> bool:
        """
        Validate that all required MySQL environment variables are set
        """
        required_vars = ['DB_USER', 'DB_PASSWORD', 'DB_NAME']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True
