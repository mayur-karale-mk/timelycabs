"""
Database configuration and connection setup
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseSettings(BaseSettings):
    """Database configuration settings"""
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "mysql+pymysql://sql12796707:AiIT5meJZm@sql12.freesqldatabase.com:3306/sql12796707"
    )
    
    class Config:
        env_file = ".env"

# Database settings instance
db_settings = DatabaseSettings()

# Create SQLAlchemy engine
engine = create_engine(
    db_settings.database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False  # Set to True for SQL query logging
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
