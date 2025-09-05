"""
Application configuration management
"""
from pydantic_settings import BaseSettings
from typing import Optional, List
import os
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "TimelyCabs"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # API
    api_v1_prefix: str = "/api/v1"
    cors_origins: List[str] = ["*"]
    
    # Database
    database_url: str = "mysql+pymysql://sql12796707:AiIT5meJZm@sql12.freesqldatabase.com:3306/sql12796707"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_recycle: int = 300
    database_echo: bool = False
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    otp_expire_minutes: int = 5
    
    # SMS/OTP
    sms_provider: str = "mock"  # mock, twilio, aws_sns
    sms_api_key: Optional[str] = None
    sms_api_secret: Optional[str] = None
    
    # Redis (for caching and sessions)
    redis_url: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Environment-specific settings
class DevelopmentSettings(Settings):
    debug: bool = True
    environment: str = "development"
    database_echo: bool = True


class ProductionSettings(Settings):
    debug: bool = False
    environment: str = "production"
    database_echo: bool = False


class TestingSettings(Settings):
    debug: bool = True
    environment: str = "testing"
    database_url: str = "sqlite:///./test.db"
    database_echo: bool = False


def get_environment_settings() -> Settings:
    """Get settings based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()
