#!/usr/bin/env python3
"""
Database rebuild script for Hive platform.
Completely rebuilds the database schema from scratch using the unified schema.
"""

import os
import sys
import logging
import psycopg2
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def get_database_config():
    """Get database configuration from environment variables."""
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'hive'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'hive123'),
    }

def execute_sql_file(connection, sql_file_path):
    """Execute an SQL file against the database."""
    try:
        with open(sql_file_path, 'r') as file:
            sql_content = file.read()
        
        with connection.cursor() as cursor:
            cursor.execute(sql_content)
        
        connection.commit()
        logger.info(f"Successfully executed {sql_file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to execute {sql_file_path}: {e}")
        connection.rollback()
        return False

def main():
    """Main function to rebuild the database."""
    logger.info("🔄 Starting Hive database rebuild...")
    
    # Get database configuration
    db_config = get_database_config()
    logger.info(f"Connecting to database: {db_config['host']}:{db_config['port']}/{db_config['database']}")
    
    # Connect to database
    try:
        connection = psycopg2.connect(**db_config)
        logger.info("✅ Connected to database successfully")
    except Exception as e:
        logger.error(f"❌ Failed to connect to database: {e}")
        sys.exit(1)
    
    try:
        # Path to the complete schema file
        schema_file = Path(__file__).parent.parent / "migrations" / "000_complete_schema.sql"
        
        if not schema_file.exists():
            logger.error(f"❌ Schema file not found: {schema_file}")
            sys.exit(1)
        
        logger.info(f"📄 Using schema file: {schema_file}")
        
        # Execute the complete schema
        logger.info("🏗️  Rebuilding database schema...")
        if execute_sql_file(connection, schema_file):
            logger.info("✅ Database schema rebuilt successfully!")
            
            # Verify the rebuild
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM users;")
                user_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public';")
                table_count = cursor.fetchone()[0]
                
                logger.info(f"📊 Database verification:")
                logger.info(f"   - Tables created: {table_count}")
                logger.info(f"   - Initial users: {user_count}")
                
                if user_count >= 2:
                    logger.info("🔐 Default users created successfully")
                    logger.warning("⚠️  SECURITY: Change default passwords in production!")
                else:
                    logger.warning("⚠️  Warning: Expected at least 2 initial users")
                
        else:
            logger.error("❌ Failed to rebuild database schema")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Unexpected error during rebuild: {e}")
        sys.exit(1)
        
    finally:
        connection.close()
        logger.info("🔌 Database connection closed")
    
    logger.info("🎉 Hive database rebuild completed successfully!")
    logger.info("🚀 Ready for authentication and full platform functionality")

if __name__ == "__main__":
    main()