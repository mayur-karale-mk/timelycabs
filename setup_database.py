#!/usr/bin/env python3
"""
Database setup script for Timelycabs
"""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_database():
    """Setup database and create tables"""
    print("Setting up Timelycabs database...")
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL", "mysql+pymysql://sql12796707:AiIT5meJZm@sql12.freesqldatabase.com:3306/sql12796707")
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
        
        # Create tables
        print("Creating database tables...")
        
        # Import models to create tables
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from app.models import Base
        from app.database import engine as db_engine
        
        # Create all tables
        Base.metadata.create_all(bind=db_engine)
        print("✅ Database tables created successfully")
        
        # Insert default roles
        print("Inserting default roles...")
        with engine.connect() as conn:
            # Check if roles already exist
            result = conn.execute(text("SELECT COUNT(*) FROM roles"))
            role_count = result.scalar()
            
            if role_count == 0:
                roles_data = [
                    ("rider", "Regular taxi booking rider"),
                    ("driver", "Taxi driver"),
                    ("owner", "Taxi fleet owner"),
                    ("admin", "System administrator"),
                    ("support", "Customer support representative")
                ]
                
                for role_name, description in roles_data:
                    conn.execute(text(
                        "INSERT INTO roles (role_name, description) VALUES (:role_name, :description)"
                    ), {"role_name": role_name, "description": description})
                
                conn.commit()
                print("✅ Default roles inserted successfully")
            else:
                print("✅ Roles already exist, skipping insertion")
        
        print("\n🎉 Database setup completed successfully!")
        print("\nNext steps:")
        print("1. Start the server: python run.py")
        print("2. Test the API: python test_auth.py")
        print("3. View API docs: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"❌ Database setup failed: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure MySQL is running")
        print("2. Check your DATABASE_URL in .env file")
        print("3. Ensure the database 'timelycabs' exists")
        print("4. Verify database credentials")

if __name__ == "__main__":
    setup_database()
