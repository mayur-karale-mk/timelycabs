#!/usr/bin/env python3
"""
Test database connection script
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test database connection with provided credentials"""
    print("Testing Database Connection...")
    print("=" * 50)
    
    # Database details
    host = "sql12.freesqldatabase.com"
    database = "sql12796707"
    user = "sql12796707"
    password = "AiIT5meJZm"
    port = "3306"
    
    # Construct database URL
    database_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    
    print(f"Host: {host}")
    print(f"Database: {database}")
    print(f"User: {user}")
    print(f"Port: {port}")
    print(f"URL: {database_url.replace(password, '***')}")
    print()
    
    try:
        # Create engine
        engine = create_engine(database_url, pool_pre_ping=True)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            test_value = result.scalar()
            
            if test_value == 1:
                print("✅ Database connection successful!")
                
                # Test database version
                result = conn.execute(text("SELECT VERSION() as version"))
                version = result.scalar()
                print(f"✅ MySQL Version: {version}")
                
                # Check if tables exist
                result = conn.execute(text("SHOW TABLES"))
                tables = [row[0] for row in result.fetchall()]
                
                if tables:
                    print(f"✅ Existing tables: {', '.join(tables)}")
                else:
                    print("ℹ️  No tables found. Run setup_database.py to create tables.")
                
            else:
                print("❌ Database connection test failed")
                
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check if the database credentials are correct")
        print("2. Verify the database server is accessible")
        print("3. Check if the database exists")
        print("4. Ensure the user has proper permissions")

if __name__ == "__main__":
    test_database_connection()
