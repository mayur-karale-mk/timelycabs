"""
Health check API endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db, check_db_connection
from app.core.config import get_settings
from app.schemas.common import HealthCheckResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


@router.get("/", response_model=HealthCheckResponse)
async def health_check(db: Session = Depends(get_db)) -> HealthCheckResponse:
    """
    Health check endpoint
    """
    try:
        # Check database connection
        db_status = check_db_connection()
        
        # TODO: Add Redis health check when implemented
        redis_status = None
        
        return HealthCheckResponse(
            status="healthy" if db_status else "unhealthy",
            timestamp=datetime.utcnow(),
            version=settings.app_version,
            environment=settings.environment,
            database=db_status,
            redis=redis_status
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheckResponse(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            version=settings.app_version,
            environment=settings.environment,
            database=False,
            redis=None
        )


